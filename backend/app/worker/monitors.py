"""The monitor lane — per-target health checks on the worker's minute cron.

`monitor_tick` batches every due target into ONE `run_monitor_sweep` arq
job (never per-target, never more than one per tick — a fixed `_job_id`
also keeps a second sweep from queueing behind a still-running one), so
the shared `max_jobs=4` pool keeps its budget for scans.

Probes reuse the scanner's primitives: ping rides the same Linux
SOCK_DGRAM/IPPROTO_ICMP ping socket, tcp wraps `_tcp_probe`, http is a
plain httpx GET honoring `monitor_http_timeout` and the `http_expect`
grammar (`status:NNN` or a body substring; empty = any 2xx-3xx).
"""
import asyncio
import logging
from datetime import datetime, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import SessionLocal
from app.core.redis import get_arq_pool
from app.core.security import set_actor
from app.models.monitoring import MonitorKind, MonitorState, MonitorTarget
from app.services import monitors as svc
from app.services import notify, runtime_settings
from app.worker.scanner import _ping_host_blocking, _tcp_probe

log = logging.getLogger("ipambox.monitor")

# Fixed arq job id — enqueue_job returns None while a sweep with this id is
# queued/running, so at most one monitor job can ever be in flight.
SWEEP_JOB_ID = "monitor-sweep"


async def _ping(ip: str, timeout: float) -> tuple[bool, str | None]:
    """Single-host ICMP echo — blocking ping/raw socket in a worker
    thread. uvloop (the API's loop) lacks sock_sendto/sock_recvfrom for
    datagrams and restricted hosts deny SOCK_DGRAM, so the probe can't
    live on the event loop."""
    return await asyncio.to_thread(_ping_host_blocking, ip, timeout)


async def _tcp(
    ip: str, port: int, timeout: float, sem: asyncio.Semaphore
) -> tuple[bool, str | None]:
    hit = await _tcp_probe(ip, [port], timeout, sem)
    return (True, None) if hit else (False, f"tcp {port} unreachable")


async def _http(
    ip: str,
    port: int | None,
    path: str,
    expect: str | None,
    client: httpx.AsyncClient,
) -> tuple[bool, str | None]:
    url = f"http://{ip}:{port or 80}{path or '/'}"
    try:
        r = await client.get(url)
    except httpx.HTTPError as e:
        return False, f"http: {e.__class__.__name__}: {e}"
    try:
        return svc.parse_http_expect(expect, r.status_code, r.text)
    except ValueError:
        return False, f"bad http_expect {expect!r}"


async def check_target(
    target: MonitorTarget,
    ip: str | None,
    *,
    sem: asyncio.Semaphore | None = None,
    icmp_timeout: float = 1.0,
    tcp_timeout: float = 0.6,
    http_timeout: float = 5.0,
    client: httpx.AsyncClient | None = None,
) -> tuple[bool, str | None]:
    """Run one check -> (ok, error). `client` lets the sweep share one
    AsyncClient across targets; tests inject httpx.MockTransport."""
    if not ip:
        ref = (
            f"address#{target.address_id}"
            if target.address_id
            else f"device#{target.device_id}"
        )
        return False, f"no resolvable IP for {ref}"
    sem = sem or asyncio.Semaphore(1)
    try:
        if target.kind == MonitorKind.PING:
            async with sem:
                return await _ping(ip, timeout=icmp_timeout)
        if target.kind == MonitorKind.TCP:
            return await _tcp(ip, target.port or 0, tcp_timeout, sem)
        own = client is None
        c = client or httpx.AsyncClient(timeout=http_timeout)
        try:
            async with sem:
                return await _http(
                    ip, target.port, target.http_path or "/",
                    target.http_expect, c
                )
        finally:
            if own:
                await c.aclose()
    except Exception as e:
        # A probe bug must degrade to a failed check, never a 500 (check-
        # now runs inline in the API) or a dead sweep job (gather
        # propagates).
        log.exception("monitor probe raised for target %s", target.id)
        return False, f"probe error: {e.__class__.__name__}"


async def run_monitor_sweep(ctx: dict, target_ids: list[int]) -> dict:
    """ARQ job: check a batch of targets, write states, emit on flips."""
    set_actor("monitor")
    async with SessionLocal() as session:
        eff = await runtime_settings.get_effective(session)
        targets = list(
            (
                await session.execute(
                    select(MonitorTarget).where(
                        MonitorTarget.id.in_(target_ids),
                        MonitorTarget.enabled.is_(True),
                    )
                )
            )
            .scalars()
            .all()
        )
        if not targets:
            return {"checked": 0}
        ips = await svc.resolve_ips(session, targets)
        sem = asyncio.Semaphore(int(eff.values["monitor_concurrency"]))
        http_timeout = float(eff.values["monitor_http_timeout"])
        icmp_timeout = float(eff.values["scan_icmp_timeout"])
        tcp_timeout = float(eff.values["scan_tcp_timeout"])
        # One shared client for the whole sweep — connection reuse across
        # targets, no per-probe setup cost.
        async with httpx.AsyncClient(timeout=http_timeout) as client:
            results = await asyncio.gather(
                *(
                    check_target(
                        t,
                        ips[t.id],
                        sem=sem,
                        icmp_timeout=icmp_timeout,
                        tcp_timeout=tcp_timeout,
                        http_timeout=http_timeout,
                        client=client,
                    )
                    for t in targets
                )
            )
        now = datetime.now(timezone.utc)
        events: list[tuple[str, MonitorTarget, str | None, str | None]] = []
        for t, (ok, err) in zip(targets, results):
            prev = t.state
            new = await svc.apply_result(
                session, t.id, prev, t.consecutive_failures, t.down_after,
                ok, err, now,
            )
            if new == prev:
                continue
            if new == MonitorState.DOWN:
                events.append(("monitor.down", t, ips[t.id], err))
            elif new == MonitorState.UP and prev == MonitorState.DOWN:
                events.append(("monitor.up", t, ips[t.id], err))
        await session.commit()
        # labels for event payloads — grouped name lookups, not per-row
        from app.models.device import Device

        dev_ids = {
            t.device_id for _e, t, _i, _er in events if t.device_id is not None
        }
        names = (
            dict(
                (
                    await session.execute(
                        select(Device.id, Device.name).where(Device.id.in_(dev_ids))
                    )
                ).all()
            )
            if dev_ids
            else {}
        )
    for ev, t, ip, err in events:
        label = svc.target_label(t, ip, names)
        await notify.emit(
            ev,
            f"{label} is {'DOWN' if ev == 'monitor.down' else 'UP'}"
            f" ({t.kind.value}"
            + (f" :{t.port}" if t.port else "")
            + ")",
            {
                "monitor_target_id": t.id,
                "kind": t.kind.value,
                "ip": ip,
                "device_id": t.device_id,
                "address_id": t.address_id,
                "error": err,
            },
        )
    log.info(
        "monitor sweep: %d checked, %d events", len(targets), len(events)
    )
    return {"checked": len(targets), "events": len(events)}


async def monitor_tick(ctx: dict) -> dict:
    """Every-minute cron beside scheduler_tick: batch due targets into a
    single sweep job. `monitoring_enabled` off -> the whole lane idles."""
    set_actor("scheduler")
    async with SessionLocal() as session:
        eff = await runtime_settings.get_effective(session)
        if not eff.values.get("monitoring_enabled", True):
            return {"skipped": "monitoring disabled"}
        ids = await svc.due_target_ids(session, datetime.now(timezone.utc))
    if not ids:
        return {"due": 0}
    pool = await get_arq_pool()
    job = await pool.enqueue_job("run_monitor_sweep", ids, _job_id=SWEEP_JOB_ID)
    return {"due": len(ids), "enqueued": job is not None}
