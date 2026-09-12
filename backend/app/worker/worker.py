import asyncio
import ipaddress
import json
import logging
from datetime import datetime

from sqlalchemy import select

from app.core.config import get_settings
from app.core.db import SessionLocal
from app.core.redis import get_redis, redis_settings_from_url
from app.core.security import set_actor
from app.models.ip_address import IPAddress
from app.models.prefix import Prefix, PrefixStatus
from app.models.scan_job import ScanJob, ScanStatus
from app.models.vrf import VRF
from app.services import prefix_math
from app.worker.reconcile import reconcile
from app.worker.scanner import detect_local_cidr, scan_cidr

log = logging.getLogger("ipambox.scanner")
settings = get_settings()


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


async def run_scan(ctx: dict, scan_id: int) -> dict:
    """ARQ job: execute a scan and reconcile results."""
    set_actor("scanner")
    started = datetime.utcnow()
    progress_lock = asyncio.Lock()

    async with SessionLocal() as session:
        job = await session.get(ScanJob, scan_id)
        if job is None:
            return {"error": f"scan {scan_id} not found"}

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
        except Exception as e:
            log.exception("scan %s failed", scan_id)
            job.status = ScanStatus.FAILED
            job.error = str(e)[:2000]
            job.finished_at = datetime.utcnow()
            job.duration_seconds = round((job.finished_at - started).total_seconds(), 2)
            await session.commit()
            await _publish(
                scan_id,
                {"scan_id": scan_id, "phase": "error", "status": "failed", "error": job.error},
            )
            return {"error": job.error}


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
    functions = [run_scan]
    on_startup = startup
    redis_settings = redis_settings_from_url(settings.redis_url)
    max_jobs = 4
    job_timeout = 1800
    max_tries = 1
