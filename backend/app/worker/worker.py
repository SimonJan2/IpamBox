import asyncio
import ipaddress
import json
import logging
from datetime import datetime, timedelta, timezone

from arq import cron
from sqlalchemy import delete, func, select

from app.core.config import get_settings
from app.core.db import SessionLocal
from app.core.redis import (
    close_arq_pool,
    close_redis,
    get_arq_pool,
    get_redis,
    redis_settings_from_url,
)
from app.core.security import set_actor
from app.models.certificate import Certificate
from app.models.change_log import ChangeLog
from app.models.ip_address import IPAddress, IPStatus
from app.models.monitoring import NotificationLog
from app.models.prefix import Prefix, PrefixStatus
from app.models.scan_job import ScanJob, ScanStatus
from app.models.vrf import VRF
from app.schemas.common import ip_display
from app.services import notify, prefix_math, runtime_settings, scan_policy
from app.worker.monitors import monitor_tick, run_monitor_sweep
from app.worker.reconcile import reconcile
from app.worker.scanner import (
    ScanCancelled,
    detect_interface,
    detect_local_cidr,
    scan_cidr,
)

log = logging.getLogger("ipambox.scanner")
settings = get_settings()

CANCEL_KEY_TTL = 3600  # seconds


def cancel_key(scan_id: int) -> str:
    return f"{settings.scan_progress_channel_prefix}cancel:{scan_id}"


async def _publish(scan_id: int, payload: dict):
    r = get_redis()  # shared client — never close per call
    await r.publish(f"{settings.scan_progress_channel_prefix}{scan_id}", json.dumps(payload))


async def _global_vrf_id(session) -> int:
    row = (await session.execute(select(VRF).where(VRF.name == "Global"))).scalar_one_or_none()
    if row is None:
        row = VRF(name="Global", description="Default global routing table")
        session.add(row)
        await session.flush()
    return row.id


async def _infer_scan_vrf(session, net) -> int:
    """Pick the VRF for a scan that didn't specify one.

    An exact-match prefix living in exactly one VRF wins; then a single
    covering prefix (containers included — scans create ACTIVE children
    inside them, same as _resolve_prefix); otherwise Global.
    """
    rows = (await session.execute(select(Prefix))).scalars().all()
    exact: set[int] = set()
    covering: set[int] = set()
    for p in rows:
        pn = prefix_math.to_network(p.prefix)
        if pn.version != net.version:
            continue
        if pn == net:
            exact.add(p.vrf_id)
        elif net.subnet_of(pn):
            covering.add(p.vrf_id)
    for candidates in (exact, covering):
        if len(candidates) == 1:
            return next(iter(candidates))
    return await _global_vrf_id(session)


async def _scan_vrf(session, job: ScanJob, net, infer: bool = True) -> int:
    if job.vrf_id is not None:
        return job.vrf_id
    if job.prefix_id is not None:
        prefix = await session.get(Prefix, job.prefix_id)
        if prefix is not None:
            return prefix.vrf_id
    # scan_infers_vrf off = never guess from prefixes — always Global
    if not infer:
        return await _global_vrf_id(session)
    return await _infer_scan_vrf(session, net)


async def _resolve_prefix(
    session,
    cidr: str,
    vrf_id: int,
    prefix_id: int | None,
    auto_create: bool = True,
) -> Prefix:
    if prefix_id is not None:
        row = await session.get(Prefix, prefix_id)
        if row:
            return row
    net = ipaddress.ip_network(cidr, strict=False)
    rows = (
        await session.execute(select(Prefix).where(Prefix.vrf_id == vrf_id))
    ).scalars().all()
    containers = []
    for p in rows:
        pn = prefix_math.to_network(p.prefix)
        if pn.version != net.version:
            continue
        if pn == net:
            return p
        if net.subnet_of(pn) and p.status != PrefixStatus.CONTAINER:
            return p  # addresses logically belong to the covering prefix
        if net.subnet_of(pn):
            containers.append(p)
    if not auto_create:
        # scan_auto_create_prefix off = documented-first: the scan must land
        # inside an existing prefix, otherwise it fails loudly.
        raise RuntimeError(
            f"no prefix covers {net} in this VRF — document it first or "
            "re-enable scan_auto_create_prefix"
        )
    # auto-create an ACTIVE prefix for the scanned CIDR (legal inside containers)
    row = Prefix(
        prefix=str(net),
        vrf_id=vrf_id,
        status=PrefixStatus.ACTIVE,
        description="Auto-created by scanner",
    )
    session.add(row)
    await session.flush()
    return row


_TERMINAL = (ScanStatus.COMPLETED, ScanStatus.FAILED, ScanStatus.CANCELLED)


def _eta_seconds(started: datetime, progress_pct: float) -> float | None:
    if progress_pct <= 0:
        return None
    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    return round(elapsed * (100.0 - progress_pct) / progress_pct, 1)


async def _job_status(session, scan_id: int) -> ScanStatus | None:
    """Re-read the job row's status — the session's `job` instance goes stale
    the moment the API writes CANCELLED on its own connection."""
    return await session.scalar(
        select(ScanJob.status).where(ScanJob.id == scan_id)
    )


async def run_scan(ctx: dict, scan_id: int) -> dict:
    """ARQ job: execute a scan and reconcile results."""
    set_actor("scanner")
    started = datetime.now(timezone.utc)
    progress_lock = asyncio.Lock()

    async def _cancelled() -> bool:
        return bool(await get_redis().get(cancel_key(scan_id)))

    async with SessionLocal() as session:
        job = await session.get(ScanJob, scan_id)
        if job is None:
            return {"error": f"scan {scan_id} not found"}
        if job.status in _TERMINAL:
            # cancelled before pickup, or a duplicate delivery
            return {"cancelled": job.status == ScanStatus.CANCELLED}

        eff = await runtime_settings.get_effective(session)

        async def progress(phase: str, pct: float):
            # serialized: concurrent enrich tasks must not commit at once
            async with progress_lock:
                if (await _job_status(session, scan_id)) in _TERMINAL:
                    # cancel landed between polls — stop the scan now
                    raise ScanCancelled()
                try:
                    job.progress = round(pct * 100, 1)
                    await session.commit()
                    await _publish(
                        scan_id,
                        {
                            "scan_id": scan_id,
                            "phase": phase,
                            "progress": job.progress,
                            "status": "running",
                            "eta_seconds": _eta_seconds(started, job.progress),
                        },
                    )
                except ScanCancelled:
                    raise
                except Exception:
                    log.warning("progress publish failed", exc_info=True)

        async def hosts_found(ips: list[str], phase: str):
            # Additive delta on the progress channel — SSE consumers that only
            # know {phase, progress, eta_seconds} simply ignore `found`.
            try:
                await _publish(
                    scan_id,
                    {
                        "scan_id": scan_id,
                        "phase": phase,
                        "progress": job.progress,
                        "status": "running",
                        "found": ips,
                    },
                )
            except Exception:
                log.warning("found-hosts publish failed", exc_info=True)

        try:
            cidr = job.cidr or detect_local_cidr(eff.values["scan_interface"])
            if not cidr:
                raise RuntimeError("could not auto-detect local network CIDR")
            job.cidr = cidr
            net = ipaddress.ip_network(cidr, strict=False)
            # Defense in depth: jobs enqueued before the enqueue-time guard
            # (or via a future path) re-checked here so they fail instead of
            # expanding into a multi-GB host list on the worker.
            if net.version != 4:
                raise RuntimeError("IPv6 scanning is not supported yet")
            # Defence in depth: re-check exclusions for jobs enqueued before
            # the route guard tightened (or queued by any future path).
            hit = scan_policy.exclusion_hit(
                net, eff.values["scan_exclude_networks"]
            )
            if hit:
                raise RuntimeError(
                    f"scan target {net} overlaps excluded network {hit}"
                )
            usable = prefix_math.usable_count(net)
            if usable > eff.values["scan_max_hosts"]:
                raise RuntimeError(
                    f"scan target {net} has {usable} usable hosts — exceeds "
                    f"scan_max_hosts={eff.values['scan_max_hosts']}"
                )
            vrf_id = await _scan_vrf(
                session, job, net,
                infer=bool(eff.values.get("scan_infers_vrf", True)),
            )
            job.vrf_id = vrf_id
            prefix = await _resolve_prefix(
                session, cidr, vrf_id, job.prefix_id,
                auto_create=bool(
                    eff.values.get("scan_auto_create_prefix", True)
                ),
            )
            job.prefix_id = prefix.id
            if (await _job_status(session, scan_id)) in _TERMINAL:
                # cancelled while resolving — don't resurrect it as RUNNING
                await session.rollback()
                return {"cancelled": True}
            job.status = ScanStatus.RUNNING
            job.started_at = started
            job.total_hosts = usable
            await session.commit()
            await _publish(
                scan_id,
                {"scan_id": scan_id, "phase": "start", "progress": 0, "status": "running", "cidr": cidr},
            )

            hosts = await scan_cidr(
                cidr,
                iface=eff.values["scan_interface"],
                tcp_ports=eff.values["scan_tcp_ports"],
                icmp_timeout=eff.values["scan_icmp_timeout"],
                tcp_timeout=eff.values["scan_tcp_timeout"],
                concurrency=eff.values["scan_concurrency"],
                on_progress=progress,
                on_hosts=hosts_found,
                should_stop=_cancelled,
            )

            # Snapshot the flagged set so the mac_mismatch event fires only
            # for flags this scan *raised* — a flag that persists across
            # scans isn't re-reported every sweep.
            flagged_before = set(
                (
                    await session.execute(
                        select(IPAddress.id).where(
                            IPAddress.custom_fields.has_key("mac_mismatch")  # noqa: W601
                        )
                    )
                ).scalars().all()
            )
            discovered, new = await reconcile(
                session, prefix.id, vrf_id, hosts, net, eff.values
            )
            # A cancel can land during reconcile — the flag is only polled
            # inside scan_cidr's phases, and the row may have been cancelled
            # behind our stale copy. Re-check both before committing results;
            # rollback discards the reconciled writes.
            if await _cancelled() or (
                await _job_status(session, scan_id)
            ) in _TERMINAL:
                await session.rollback()
                await _publish(
                    scan_id,
                    {
                        "scan_id": scan_id,
                        "phase": "cancelled",
                        "status": "cancelled",
                    },
                )
                return {"cancelled": True}
            job.status = ScanStatus.COMPLETED
            job.progress = 100.0
            job.hosts_discovered = discovered
            job.hosts_new = new
            job.finished_at = datetime.now(timezone.utc)
            job.duration_seconds = round((job.finished_at - started).total_seconds(), 2)
            await session.commit()
            # Mismatch events fire post-commit, only for flags this scan
            # raised (cleared-and-reflagged counts as raised again). The
            # notify payload only samples 20 rows — count the true total
            # separately so a big scan doesn't under-report in the summary.
            _mismatch_where = IPAddress.custom_fields.has_key(  # noqa: W601
                "mac_mismatch"
            ) & IPAddress.id.notin_(flagged_before)
            mismatch_total = await session.scalar(
                select(func.count()).select_from(
                    select(IPAddress.id).where(_mismatch_where).subquery()
                )
            ) or 0
            newly_flagged = (
                await session.execute(
                    select(IPAddress).where(_mismatch_where).limit(20)
                )
            ).scalars().all()
            if newly_flagged:
                _shown = (
                    f" (showing {len(newly_flagged)})"
                    if mismatch_total > len(newly_flagged)
                    else ""
                )
                await notify.emit(
                    "mac_mismatch",
                    f"{mismatch_total} MAC mismatch(es) flagged by "
                    f"scan #{scan_id} on {cidr}{_shown}",
                    {
                        "scan_id": scan_id,
                        "cidr": cidr,
                        "items": [
                            {
                                "address": ip_display(a.address),
                                "mac_was": (a.custom_fields or {})
                                .get("mac_mismatch", {})
                                .get("was"),
                                "mac_seen": (a.custom_fields or {})
                                .get("mac_mismatch", {})
                                .get("seen"),
                            }
                            for a in newly_flagged
                        ],
                    },
                )
            await _publish(
                scan_id,
                {
                    "scan_id": scan_id,
                    "phase": "done",
                    "progress": 100,
                    "status": "completed",
                    "hosts_discovered": discovered,
                    "hosts_new": new,
                },
            )
            return {"hosts": discovered, "new": new}
        except ScanCancelled:
            if (await _job_status(session, scan_id)) not in _TERMINAL:
                job.status = ScanStatus.CANCELLED
                job.finished_at = datetime.now(timezone.utc)
                job.duration_seconds = round(
                    (job.finished_at - started).total_seconds(), 2
                )
                await session.commit()
            await _publish(
                scan_id,
                {"scan_id": scan_id, "phase": "cancelled", "status": "cancelled"},
            )
            return {"cancelled": True}
        except Exception as e:
            log.exception("scan %s failed", scan_id)
            # the session may be inside a failed transaction — reset it before
            # recording the failure
            await session.rollback()
            err = str(e)[:2000]
            job = await session.get(ScanJob, scan_id)
            if job is not None and job.status not in _TERMINAL:
                job.status = ScanStatus.FAILED
                job.error = err
                job.finished_at = datetime.now(timezone.utc)
                job.duration_seconds = round(
                    (job.finished_at - started).total_seconds(), 2
                )
                await session.commit()
                await notify.emit(
                    "scan.failed",
                    f"scan #{scan_id}"
                    f"{f' ({job.cidr})' if job.cidr else ''} failed: "
                    f"{err[:300]}",
                    {
                        "scan_id": scan_id,
                        "cidr": job.cidr,
                        "error": err,
                    },
                )
            await _publish(
                scan_id,
                {"scan_id": scan_id, "phase": "error", "status": "failed", "error": err},
            )
            return {"error": err}


async def run_scheduled_scans(ctx: dict) -> dict:
    """Enqueue a scan for every configured network (effective settings).

    Targets: DB/env scan_networks (or the auto-detected LAN CIDR when unset
    and only_configured is off). Skips a CIDR that already has a
    queued/running job, and never scans excluded networks.
    """
    set_actor("scheduler")
    async with SessionLocal() as session:
        eff = await runtime_settings.get_effective(session)
    targets = list(eff.values["scan_networks"])
    if not targets and not eff.values["scan_only_configured"]:
        detected = detect_local_cidr(eff.values["scan_interface"])
        if detected:
            targets = [detected]

    enqueued: list[str] = []
    async with SessionLocal() as session:
        pool = await get_arq_pool()  # shared pool — never close per call
        for cidr in targets:
            net = ipaddress.ip_network(cidr, strict=False)
            hit = scan_policy.exclusion_hit(
                net, eff.values["scan_exclude_networks"]
            )
            if hit:
                log.info(
                    "scheduled scan skipped (excluded): %s overlaps %s",
                    net, hit,
                )
                continue
            if net.version != 4:
                log.info("scheduled scan skipped (IPv6 unsupported): %s", net)
                continue
            if prefix_math.usable_count(net) > eff.values["scan_max_hosts"]:
                log.info(
                    "scheduled scan skipped (over scan_max_hosts): %s", net
                )
                continue
            live = (
                await session.execute(
                    select(ScanJob.id).where(
                        ScanJob.cidr == str(net),
                        ScanJob.status.in_(
                            [ScanStatus.QUEUED, ScanStatus.RUNNING]
                        ),
                    )
                )
            ).first()
            if live:
                continue
            job = ScanJob(cidr=str(net))
            session.add(job)
            await session.flush()
            await pool.enqueue_job("run_scan", job.id)
            enqueued.append(str(net))
        await session.commit()
    if enqueued:
        log.info("scheduled scans enqueued: %s", enqueued)
    return {"enqueued": enqueued}


async def run_scheduled_backup(ctx: dict) -> dict:
    """Write a full snapshot into BACKUP_DIR, prune old ones."""
    from app.services import backup as backup_svc

    async with SessionLocal() as session:
        eff = await runtime_settings.get_effective(session)
        payload = await backup_svc.build_backup(session)
    path = backup_svc.write_backup_file(payload)
    pruned = backup_svc.prune_backups(eff.values["backup_keep"])
    log.info("scheduled backup written: %s (pruned %d)", path.name, pruned)
    return {"file": path.name, "pruned": pruned}


async def _retention_sweeps(session, values: dict, now: datetime) -> dict:
    """Auto-purge rows past their configured retention (0 = keep forever).

    Mirrors the manual purges in api/v1/maintenance.py but runs unattended in
    the scheduler tick — each sweep writes one summary changelog row when it
    actually deleted something.
    """
    detail: dict[str, int] = {}

    days = int(values.get("changelog_retention_days") or 0)
    if days > 0:
        res = await session.execute(
            delete(ChangeLog).where(
                ChangeLog.ts < now - timedelta(days=days)
            )
        )
        detail["changelog"] = res.rowcount or 0

    days = int(values.get("scan_job_retention_days") or 0)
    if days > 0:
        res = await session.execute(
            delete(ScanJob).where(
                ScanJob.status.in_(_TERMINAL),
                ScanJob.created_at < now - timedelta(days=days),
            )
        )
        detail["scan_jobs"] = res.rowcount or 0

    days = int(values.get("discovery_expire_days") or 0)
    if days > 0:
        # last_seen wins over created_at: a discovered host that keeps
        # answering scans isn't stale, it's just unreviewed.
        res = await session.execute(
            delete(IPAddress).where(
                IPAddress.status == IPStatus.DISCOVERED,
                func.coalesce(IPAddress.last_seen, IPAddress.created_at)
                < now - timedelta(days=days),
            )
        )
        detail["discovery"] = res.rowcount or 0

    days = int(values.get("notify_retention_days") or 0)
    if days > 0:
        res = await session.execute(
            delete(NotificationLog).where(
                NotificationLog.created_at < now - timedelta(days=days)
            )
        )
        detail["notification_log"] = res.rowcount or 0

    if any(detail.values()):
        await session.execute(
            ChangeLog.__table__.insert(),
            [
                {
                    "actor": "scheduler",
                    "action": "delete",
                    "object_type": "Maintenance",
                    "object_id": None,
                    "object_repr": "retention-sweep",
                    "changes": [
                        {"field": "result", "before": None, "after": detail}
                    ],
                }
            ],
        )
        await session.commit()
        log.info("retention sweeps deleted: %s", detail)
    return detail


def _due(last_iso: str | None, interval_minutes: int, now: datetime) -> bool:
    if interval_minutes <= 0:
        return False
    if not last_iso:
        return True
    try:
        last = datetime.fromisoformat(last_iso)
    except ValueError:
        return True
    if last.tzinfo is None:
        # stamps written before timestamptz carried no offset (UTC implied)
        last = last.replace(tzinfo=timezone.utc)
    return (now - last).total_seconds() >= interval_minutes * 60


async def _cert_warnings(now: datetime) -> int:
    """Emit cert.expiring once per certificate per day for certs inside the
    warn window. Day-stamps live in Redis (like the sched stamps — never
    app_settings, which would spam the changelog every sweep)."""
    async with SessionLocal() as session:
        eff = await runtime_settings.get_effective(session)
        warn = int(eff.values["cert_warn_days"])
        today = now.date()
        rows = (
            await session.execute(
                select(Certificate).where(
                    Certificate.expires_on.is_not(None),
                    Certificate.expires_on <= today + timedelta(days=warn),
                )
            )
        ).scalars().all()
    if not rows:
        return 0
    r = get_redis()
    sent = 0
    for c in rows:
        key = f"ipam:notify:cert:{c.id}"
        if await r.get(key) == today.isoformat():
            continue  # already reported today — one event per cert per day
        days_left = (c.expires_on - today).days
        label = c.cert_name or c.server_name or f"cert#{c.id}"
        await notify.emit(
            "cert.expiring",
            f"{label} expires {c.expires_on.isoformat()} "
            f"({'expired' if days_left < 0 else f'{days_left}d left'})",
            {
                "certificate_id": c.id,
                "cert_name": c.cert_name,
                "server_name": c.server_name,
                "expires_on": c.expires_on.isoformat(),
                "days_left": days_left,
            },
        )
        await r.set(key, today.isoformat(), ex=172800)  # 2-day TTL self-cleans
        sent += 1
    return sent


async def scheduler_tick(ctx: dict) -> dict:
    """Runs every minute: fires scheduled scans/backups whose configured
    interval has elapsed. DB-backed intervals apply without a worker restart.

    Also refreshes the worker's view of the LAN (iface + CIDR, host-networked)
    into Redis so the API/UI can display the real detected network. Last-run
    stamps live in Redis (not app_settings — they'd spam the changelog).
    """
    set_actor("scheduler")
    ran: list[str] = []
    now = datetime.now(timezone.utc)

    async with SessionLocal() as session:
        eff = await runtime_settings.get_effective(session)

    r = get_redis()  # shared client — never close per call
    try:
        iface = eff.values["scan_interface"]
        lan = {"iface": detect_interface(iface), "cidr": detect_local_cidr(iface)}
        await r.set("ipam:sys:lan", json.dumps(lan))
    except Exception:
        log.warning("lan detection publish failed", exc_info=True)

    if _due(
        await r.get("ipam:sched:last_scan_at"),
        eff.values["scan_interval_minutes"],
        now,
    ):
        await r.set("ipam:sched:last_scan_at", now.isoformat())
        ran.append("scans")
    if _due(
        await r.get("ipam:sched:last_backup_at"),
        eff.values["backup_interval_minutes"],
        now,
    ):
        await r.set("ipam:sched:last_backup_at", now.isoformat())
        ran.append("backups")

    async with SessionLocal() as session:
        await _retention_sweeps(session, eff.values, now)

    # Channel events — cert warnings ride the minute tick too.
    try:
        notified = await _cert_warnings(now)
        if notified:
            ran.append("cert_warnings")
    except Exception:
        log.warning("cert warning sweep failed", exc_info=True)

    if "scans" in ran:
        await run_scheduled_scans(ctx)
    if "backups" in ran:
        await run_scheduled_backup(ctx)
    return {"ran": ran}


async def reap_stale_scan_jobs(session, now: datetime | None = None) -> int:
    """Fail live jobs that outlived the worker's job_timeout.

    An OOM-killed or otherwise dead worker leaves RUNNING/QUEUED rows behind;
    without this they block the single-live-job rule (429) until a restart.
    started_at marks RUNNING rows, created_at QUEUED ones (never picked up).
    """
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(seconds=WorkerSettings.job_timeout)
    stale = (
        await session.execute(
            select(ScanJob).where(
                ScanJob.status.in_([ScanStatus.QUEUED, ScanStatus.RUNNING])
            )
        )
    ).scalars().all()
    reaped = 0
    reaped_jobs: list[ScanJob] = []
    for j in stale:
        ref = j.started_at if j.status == ScanStatus.RUNNING else j.created_at
        if ref is None or ref > cutoff:
            continue
        j.status = ScanStatus.FAILED
        j.error = f"exceeded job_timeout ({WorkerSettings.job_timeout}s) — worker died?"
        j.finished_at = now
        if j.started_at:
            j.duration_seconds = round((now - j.started_at).total_seconds(), 2)
        reaped += 1
        reaped_jobs.append(j)
    if reaped:
        await session.commit()
        log.warning("watchdog reaped %d stale scan job(s)", reaped)
        for j in reaped_jobs:
            await notify.emit(
                "scan.failed",
                f"scan #{j.id}{f' ({j.cidr})' if j.cidr else ''} "
                "timed out — worker died?",
                {"scan_id": j.id, "cidr": j.cidr, "error": j.error},
            )
    return reaped


async def scan_watchdog(ctx: dict) -> dict:
    """Every-minute cron: reaps live jobs that outlived job_timeout."""
    async with SessionLocal() as session:
        return {"reaped": await reap_stale_scan_jobs(session)}


async def startup(ctx: dict):
    log.info("scanner worker starting")
    get_redis()  # create the shared client on the worker's loop
    # any job left queued/running by a previous worker instance is dead
    async with SessionLocal() as session:
        stale = (
            await session.execute(
                select(ScanJob).where(
                    ScanJob.status.in_([ScanStatus.QUEUED, ScanStatus.RUNNING])
                )
            )
        ).scalars().all()
        for j in stale:
            j.status = ScanStatus.FAILED
            j.error = "worker restarted"
            j.finished_at = datetime.now(timezone.utc)
        await session.commit()
        for j in stale:
            await notify.emit(
                "scan.failed",
                f"scan #{j.id}{f' ({j.cidr})' if j.cidr else ''} "
                "failed — worker restarted",
                {"scan_id": j.id, "cidr": j.cidr, "error": j.error},
            )


async def shutdown(ctx: dict):
    await close_redis()
    await close_arq_pool()


class WorkerSettings:
    functions = [run_scan, run_scheduled_backup, run_monitor_sweep]
    cron_jobs = [
        cron(scheduler_tick, minute=set(range(60))),
        cron(scan_watchdog, minute=set(range(60))),
        # the monitor lane — batches due targets into ONE job per tick so
        # checks never eat the scan budget (max_jobs=4 is shared)
        cron(monitor_tick, minute=set(range(60))),
    ]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = redis_settings_from_url(settings.redis_url)
    max_jobs = 4
    job_timeout = 1800
    max_tries = 1
