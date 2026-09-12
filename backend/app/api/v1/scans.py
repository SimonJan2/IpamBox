import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import SessionLocal, get_session
from app.core.redis import get_arq_pool, get_redis
from app.models.scan_job import ScanJob, ScanStatus
from app.models.vrf import VRF
from app.schemas.scan import ScanCreate, ScanJobOut
from app.services.ipam import IPAMError, get_or_404

router = APIRouter(prefix="/scans", tags=["scans"])
settings = get_settings()

_TERMINAL = (ScanStatus.COMPLETED, ScanStatus.FAILED)


@router.get("", response_model=list[ScanJobOut])
async def list_scans(
    limit: int = 50, session: AsyncSession = Depends(get_session)
):
    return (
        await session.execute(
            select(ScanJob).order_by(ScanJob.id.desc()).limit(limit)
        )
    ).scalars().all()


@router.post("", response_model=ScanJobOut, status_code=201)
async def create_scan(body: ScanCreate, session: AsyncSession = Depends(get_session)):
    vrf_id = body.vrf_id
    if vrf_id is None:
        vrf_id = (
            await session.execute(select(VRF.id).where(VRF.name == "Global"))
        ).scalar_one_or_none()
    else:
        try:
            await get_or_404(session, VRF, vrf_id)
        except IPAMError as e:
            raise HTTPException(e.status_code, str(e))

    job = ScanJob(cidr=body.cidr or "", vrf_id=vrf_id, prefix_id=body.prefix_id)
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


@router.get("/{scan_id}", response_model=ScanJobOut)
async def get_scan(scan_id: int, session: AsyncSession = Depends(get_session)):
    job = await session.get(ScanJob, scan_id)
    if job is None:
        raise HTTPException(404, "scan not found")
    return job


def _job_payload(job: ScanJob) -> dict:
    return {
        "scan_id": job.id,
        "status": job.status.value,
        "phase": "snapshot",
        "progress": job.progress,
        "cidr": job.cidr,
        "hosts_discovered": job.hosts_discovered,
        "hosts_new": job.hosts_new,
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
                        if json.loads(msg["data"]).get("status") in ("completed", "failed"):
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
