import ipaddress
import json
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import SessionLocal, get_session
from app.core.deps import DATA_WRITE, require_perm
from app.core.redis import get_arq_pool, get_redis
from app.models.scan_job import ScanJob, ScanStatus
from app.models.vrf import VRF
from app.schemas.scan import ScanConfigOut, ScanCreate, ScanJobOut
from app.services import prefix_math, runtime_settings
from app.services.ipam import IPAMError, get_or_404
from app.worker.scanner import detect_local_cidr
from app.worker.worker import cancel_key

router = APIRouter(prefix="/scans", tags=["scans"])
settings = get_settings()

_TERMINAL = (ScanStatus.COMPLETED, ScanStatus.FAILED, ScanStatus.CANCELLED)
_LIVE = (ScanStatus.QUEUED, ScanStatus.RUNNING)


def _check_cidr_allowed(net, eff: dict) -> None:
    for x in eff["scan_exclude_networks"]:
        xn = ipaddress.ip_network(x, strict=False)
        if net.subnet_of(xn) or net == xn or xn.subnet_of(net):
            raise HTTPException(422, f"{net} overlaps excluded network {xn}")
    if eff["scan_only_configured"]:
        allowed = [
            ipaddress.ip_network(n, strict=False) for n in eff["scan_networks"]
        ]
        if not any(net.subnet_of(a) or net == a for a in allowed):
            raise HTTPException(422, f"{net} is not one of the configured scan networks")


@router.get("", response_model=list[ScanJobOut])
async def list_scans(
    limit: int = 50, session: AsyncSession = Depends(get_session)
):
    return (
        await session.execute(
            select(ScanJob).order_by(ScanJob.id.desc()).limit(limit)
        )
    ).scalars().all()


@router.get("/config", response_model=ScanConfigOut)
async def scan_config(session: AsyncSession = Depends(get_session)):
    """Effective scanner configuration surfaced to the UI."""
    from app.api.v1.settings import _lan_info

    eff = await runtime_settings.get_effective(session)
    lan = await _lan_info()
    return ScanConfigOut(
        networks=eff.values["scan_networks"],
        exclude_networks=eff.values["scan_exclude_networks"],
        only_configured=eff.values["scan_only_configured"],
        interval_minutes=eff.values["scan_interval_minutes"],
        detected_cidr=lan.cidr,
        tcp_ports=eff.values["scan_tcp_ports"],
    )


@router.post(
    "",
    response_model=ScanJobOut,
    status_code=201,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def create_scan(body: ScanCreate, session: AsyncSession = Depends(get_session)):
    eff = await runtime_settings.get_effective(session)
    if body.cidr:
        net = ipaddress.ip_network(body.cidr, strict=False)
        _check_cidr_allowed(net, eff.values)
        cap = eff.values["scan_max_hosts"]
        usable = prefix_math.usable_count(net)
        if usable > cap:
            raise HTTPException(
                422,
                f"{net} has {usable} usable hosts — exceeds scan_max_hosts={cap} "
                "(Settings → Scanning or SCAN_MAX_HOSTS)",
            )
    elif eff.values["scan_only_configured"] and eff.values["scan_networks"]:
        raise HTTPException(
            422, "only configured networks may be scanned — pick one of them"
        )

    # single-scanner rate limit: one live job at a time + cooldown per CIDR
    live = (
        await session.execute(
            select(func.count(ScanJob.id)).where(ScanJob.status.in_(_LIVE))
        )
    ).scalar_one()
    if live:
        raise HTTPException(429, "a scan is already queued or running")
    if body.cidr:
        cutoff = datetime.utcnow() - timedelta(
            seconds=eff.values["scan_min_interval_seconds"]
        )
        recent = (
            await session.execute(
                select(func.count(ScanJob.id)).where(
                    ScanJob.cidr == body.cidr, ScanJob.created_at >= cutoff
                )
            )
        ).scalar_one()
        if recent:
            raise HTTPException(
                429,
                f"{body.cidr} was scanned <{eff.values['scan_min_interval_seconds']}s ago — slow down",
            )

    if body.vrf_id is not None:
        try:
            await get_or_404(session, VRF, body.vrf_id)
        except IPAMError as e:
            raise HTTPException(e.status_code, str(e))

    job = ScanJob(cidr=body.cidr or "", vrf_id=body.vrf_id, prefix_id=body.prefix_id)
    session.add(job)
    await session.flush()

    pool = await get_arq_pool()
    try:
        arq_job = await pool.enqueue_job("run_scan", job.id)
        job.arq_job_id = arq_job.job_id if arq_job else None
    finally:
        await pool.close()
    await session.commit()
    await session.refresh(job)
    return job


@router.post(
    "/{scan_id}/cancel",
    response_model=ScanJobOut,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def cancel_scan(scan_id: int, session: AsyncSession = Depends(get_session)):
    job = await session.get(ScanJob, scan_id)
    if job is None:
        raise HTTPException(404, "scan not found")
    if job.status in _TERMINAL:
        raise HTTPException(409, f"scan already {job.status.value}")
    # flag for the worker + mark immediately so queued jobs never start
    r = get_redis()
    try:
        await r.set(cancel_key(scan_id), "1", ex=3600)
    finally:
        await r.aclose()
    job.status = ScanStatus.CANCELLED
    job.finished_at = datetime.utcnow()
    if job.started_at:
        job.duration_seconds = round(
            (job.finished_at - job.started_at).total_seconds(), 2
        )
    await session.commit()
    await session.refresh(job)
    return job


@router.get("/{scan_id}", response_model=ScanJobOut)
async def get_scan(scan_id: int, session: AsyncSession = Depends(get_session)):
    job = await session.get(ScanJob, scan_id)
    if job is None:
        raise HTTPException(404, "scan not found")
    return job


def _job_payload(job: ScanJob) -> dict:
    eta = None
    if job.status == ScanStatus.RUNNING and job.started_at and job.progress > 0:
        elapsed = (datetime.utcnow() - job.started_at).total_seconds()
        eta = round(elapsed * (100 - job.progress) / job.progress, 1)
    return {
        "scan_id": job.id,
        "status": job.status.value,
        "phase": "snapshot",
        "progress": job.progress,
        "cidr": job.cidr,
        "hosts_discovered": job.hosts_discovered,
        "hosts_new": job.hosts_new,
        "eta_seconds": eta,
        "error": job.error,
    }


@router.get("/{scan_id}/stream")
async def stream_scan(scan_id: int):
    """SSE stream of scan progress (Redis pub/sub backed)."""

    async def gen():
        r = get_redis()
        pubsub = r.pubsub()
        try:
            async with SessionLocal() as s:
                job = await s.get(ScanJob, scan_id)
            if job is None:
                yield f"data: {json.dumps({'error': 'scan not found'})}\n\n"
                return
            yield f"data: {json.dumps(_job_payload(job))}\n\n"
            if job.status in _TERMINAL:
                return

            channel = f"{settings.scan_progress_channel_prefix}{scan_id}"
            await pubsub.subscribe(channel)
            while True:
                msg = await pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=15.0
                )
                if msg is not None:
                    yield f"data: {msg['data']}\n\n"
                    try:
                        if json.loads(msg["data"]).get("status") in (
                            "completed", "failed", "cancelled",
                        ):
                            return
                    except (ValueError, AttributeError):
                        pass
                else:
                    # heartbeat keeps proxies alive; also bail if job ended silently
                    yield ": heartbeat\n\n"
                    async with SessionLocal() as s:
                        job = await s.get(ScanJob, scan_id)
                    if job is None or job.status in _TERMINAL:
                        if job is not None:
                            yield f"data: {json.dumps(_job_payload(job))}\n\n"
                        return
        finally:
            await pubsub.unsubscribe()
            await r.aclose()

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
