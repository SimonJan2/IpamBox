import asyncio
import ipaddress
import json
import logging
from datetime import datetime

from arq import cron
from sqlalchemy import select

from app.core.config import get_settings
from app.core.db import SessionLocal
from app.core.redis import get_arq_pool, get_redis, redis_settings_from_url
from app.core.security import set_actor
from app.models.ip_address import IPAddress
from app.models.prefix import Prefix, PrefixStatus
from app.models.scan_job import ScanJob, ScanStatus
from app.models.vrf import VRF
from app.services import prefix_math
from app.worker.reconcile import reconcile
from app.worker.scanner import ScanCancelled, detect_local_cidr, scan_cidr

log = logging.getLogger("ipambox.scanner")
settings = get_settings()

CANCEL_KEY_TTL = 3600  # seconds


def cancel_key(scan_id: int) -> str:
    return f"{settings.scan_progress_channel_prefix}cancel:{scan_id}"


async def _publish(scan_id: int, payload: dict):
    r = get_redis()
    try:
        await r.publish(f"{settings.scan_progress_channel_prefix}{scan_id}", json.dumps(payload))
    finally:
        await r.aclose()


async def _global_vrf_id(session) -> int:
    row = (await session.execute(select(VRF).where(VRF.name == "Global"))).scalar_one_or_none()
    if row is None:
        row = VRF(name="Global", description="Default global routing table")
        session.add(row)
        await session.flush()
    return row.id


async def _resolve_prefix(session, cidr: str, vrf_id: int, prefix_id: int | None) -> Prefix:
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


def _eta_seconds(started: datetime, progress_pct: float) -> float | None:
    if progress_pct <= 0:
        return None
    elapsed = (datetime.utcnow() - started).total_seconds()
    return round(elapsed * (100.0 - progress_pct) / progress_pct, 1)


async def run_scan(ctx: dict, scan_id: int) -> dict:
    """ARQ job: execute a scan and reconcile results."""
    set_actor("scanner")
    started = datetime.utcnow()
    progress_lock = asyncio.Lock()

    async def _cancelled() -> bool:
        r = get_redis()
        try:
            return bool(await r.get(cancel_key(scan_id)))
        finally:
            await r.aclose()

    async with SessionLocal() as session:
        job = await session.get(ScanJob, scan_id)
        if job is None:
            return {"error": f"scan {scan_id} not found"}
        if job.status == ScanStatus.CANCELLED:
            return {"cancelled": True}

        async def progress(phase: str, pct: float):
            # serialized: concurrent enrich tasks must not commit at once
            async with progress_lock:
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
                except Exception:
                    log.warning("progress publish failed", exc_info=True)

        try:
            cidr = job.cidr or detect_local_cidr(settings.scan_interface)
            if not cidr:
                raise RuntimeError("could not auto-detect local network CIDR")
            job.cidr = cidr
            vrf_id = job.vrf_id or await _global_vrf_id(session)
            job.vrf_id = vrf_id
            prefix = await _resolve_prefix(session, cidr, vrf_id, job.prefix_id)
            job.prefix_id = prefix.id
            job.status = ScanStatus.RUNNING
            job.started_at = started
            net = ipaddress.ip_network(cidr, strict=False)
            job.total_hosts = prefix_math.usable_count(net)
            await session.commit()
            await _publish(
                scan_id,
                {"scan_id": scan_id, "phase": "start", "progress": 0, "status": "running", "cidr": cidr},
            )

            hosts = await scan_cidr(
                cidr,
                iface=settings.scan_interface,
                tcp_ports=settings.tcp_ping_ports,
                icmp_timeout=settings.scan_icmp_timeout,
                tcp_timeout=settings.scan_tcp_timeout,
                concurrency=settings.scan_concurrency,
                on_progress=progress,
                should_stop=_cancelled,
            )

            discovered, new = await reconcile(session, prefix.id, vrf_id, hosts)
            job.status = ScanStatus.COMPLETED
            job.progress = 100.0
            job.hosts_discovered = discovered
            job.hosts_new = new
            job.finished_at = datetime.utcnow()
            job.duration_seconds = round((job.finished_at - started).total_seconds(), 2)
            await session.commit()
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
            job.status = ScanStatus.CANCELLED
            job.finished_at = datetime.utcnow()
            job.duration_seconds = round((job.finished_at - started).total_seconds(), 2)
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
            if job is not None:
                job.status = ScanStatus.FAILED
                job.error = err
                job.finished_at = datetime.utcnow()
                job.duration_seconds = round(
                    (job.finished_at - started).total_seconds(), 2
                )
                await session.commit()
            await _publish(
                scan_id,
                {"scan_id": scan_id, "phase": "error", "status": "failed", "error": err},
            )
            return {"error": err}


async def run_scheduled_scans(ctx: dict) -> dict:
    """Cron entry point: enqueue a scan for every configured network.

    Networks: SCAN_NETWORKS env (or the auto-detected LAN CIDR when unset and
    SCAN_ONLY_CONFIGURED is off). Skips a CIDR that already has a
    queued/running job, and never scans excluded networks.
    """
    set_actor("scheduler")
    excluded = [
        ipaddress.ip_network(n, strict=False)
        for n in settings.scan_exclude_network_list
    ]
    targets = list(settings.scan_network_list)
    if not targets and not settings.scan_only_configured:
        detected = detect_local_cidr(settings.scan_interface)
        if detected:
            targets = [detected]

    enqueued: list[str] = []
    async with SessionLocal() as session:
        pool = await get_arq_pool()
        try:
            for cidr in targets:
                net = ipaddress.ip_network(cidr, strict=False)
                if any(net.subnet_of(x) or net == x for x in excluded):
                    log.info("scheduled scan skipped (excluded): %s", net)
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
        finally:
            await pool.close()
    if enqueued:
        log.info("scheduled scans enqueued: %s", enqueued)
    return {"enqueued": enqueued}


async def run_scheduled_backup(ctx: dict) -> dict:
    """Cron entry point: write a full snapshot into BACKUP_DIR, prune old ones."""
    from app.services import backup as backup_svc

    async with SessionLocal() as session:
        payload = await backup_svc.build_backup(session)
    path = backup_svc.write_backup_file(payload)
    pruned = backup_svc.prune_backups(settings.backup_keep)
    log.info("scheduled backup written: %s (pruned %d)", path.name, pruned)
    return {"file": path.name, "pruned": pruned}


def _periodic(func, minutes: int):
    """Map 'every N minutes' onto an arq cron spec; None disables the job."""
    if minutes <= 0:
        return None
    if minutes < 60:
        return cron(func, minute=set(range(0, 60, minutes)))
    hours = max(1, minutes // 60)
    if hours < 24:
        return cron(func, hour=set(range(0, 24, hours)), minute=0)
    return cron(func, hour=0, minute=0)  # daily fallback


def _cron_jobs() -> list:
    return [
        job
        for job in (
            _periodic(run_scheduled_scans, settings.scan_interval_minutes),
            _periodic(run_scheduled_backup, settings.backup_interval_minutes),
        )
        if job is not None
    ]


async def startup(ctx: dict):
    log.info("scanner worker starting")
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
            j.finished_at = datetime.utcnow()
        await session.commit()


class WorkerSettings:
    functions = [run_scan, run_scheduled_backup]
    cron_jobs = _cron_jobs()
    on_startup = startup
    redis_settings = redis_settings_from_url(settings.redis_url)
    max_jobs = 4
    job_timeout = 1800
    max_tries = 1
