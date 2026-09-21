"""Destructive maintenance operations, all behind typed confirmation in the UI."""
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import delete, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import BACKUP_ACCESS, SYSTEM_ADMIN, require_perm
from app.core.redis import get_arq_pool
from app.core.security import get_actor
from app.models.change_log import ChangeLog
from app.models.ip_address import IPAddress, IPStatus
from app.models.scan_job import ScanJob, ScanStatus
from app.models.user import User
from app.services.backup import (
    BACKUP_TABLES,
    _has_serial_id,
    _resync_sequence_sql,
    _truncate_sql,
)

router = APIRouter(prefix="/maintenance", tags=["maintenance"])

_TERMINAL = (ScanStatus.COMPLETED, ScanStatus.FAILED, ScanStatus.CANCELLED)


class PurgeBody(BaseModel):
    older_than_days: int | None = Field(default=None, ge=1, le=3650)


class ResetBody(BaseModel):
    confirm: Literal["RESET"]


async def _audit(session: AsyncSession, actor: str, what: str, detail: dict):
    """Summary changelog row for a bulk maintenance action."""
    await session.execute(
        ChangeLog.__table__.insert(),
        [
            {
                "actor": actor,
                "action": "delete",
                "object_type": "Maintenance",
                "object_id": None,
                "object_repr": what,
                "changes": [{"field": "result", "before": None, "after": detail}],
            }
        ],
    )


@router.post("/purge-scans")
async def purge_scans(
    body: PurgeBody,
    session: AsyncSession = Depends(get_session),
    _user=Depends(require_perm(SYSTEM_ADMIN)),
):
    """Delete terminal scan jobs (all, or older than N days)."""
    stmt = delete(ScanJob).where(ScanJob.status.in_(_TERMINAL))
    if body.older_than_days is not None:
        cutoff = datetime.now(timezone.utc) - timedelta(days=body.older_than_days)
        stmt = stmt.where(ScanJob.created_at < cutoff)
    result = await session.execute(stmt)
    deleted = result.rowcount or 0
    await _audit(session, get_actor(), "purge-scans", {"deleted": deleted})
    await session.commit()
    return {"deleted": deleted}


@router.post("/purge-changelog")
async def purge_changelog(
    body: PurgeBody,
    session: AsyncSession = Depends(get_session),
    _user=Depends(require_perm(SYSTEM_ADMIN)),
):
    """Delete changelog entries (all, or older than N days)."""
    stmt = delete(ChangeLog)
    if body.older_than_days is not None:
        cutoff = datetime.now(timezone.utc) - timedelta(days=body.older_than_days)
        stmt = stmt.where(ChangeLog.ts < cutoff)
    result = await session.execute(stmt)
    deleted = result.rowcount or 0
    await _audit(session, get_actor(), "purge-changelog", {"deleted": deleted})
    await session.commit()
    return {"deleted": deleted}


@router.post("/clear-discovery")
async def clear_discovery(
    session: AsyncSession = Depends(get_session),
    _user=Depends(require_perm(SYSTEM_ADMIN)),
):
    """Delete every host still in the discovery inbox (status=discovered)."""
    result = await session.execute(
        delete(IPAddress).where(IPAddress.status == IPStatus.DISCOVERED)
    )
    deleted = result.rowcount or 0
    await _audit(session, get_actor(), "clear-discovery", {"deleted": deleted})
    await session.commit()
    return {"deleted": deleted}


@router.post("/backup-now", status_code=202)
async def backup_now(_user=Depends(require_perm(BACKUP_ACCESS))):
    """Enqueue an immediate scheduled-style backup on the worker."""
    pool = await get_arq_pool()  # shared pool — never close per call
    job = await pool.enqueue_job("run_scheduled_backup")
    if job is None:
        raise HTTPException(409, "a backup job is already queued")
    return {"queued": True, "job_id": job.job_id}


@router.post("/reset")
async def factory_reset(
    body: ResetBody,
    session: AsyncSession = Depends(get_session),
    _user=Depends(require_perm(SYSTEM_ADMIN)),
):
    """Wipe every backup-covered table (incl. app_settings) inside one
    transaction. Users and live sessions survive — same contract as restore."""
    del body  # confirm token already validated by the schema
    users = await session.scalar(select(func.count(User.id)))
    await session.execute(text(_truncate_sql()))
    for spec in BACKUP_TABLES:
        if _has_serial_id(spec):
            await session.execute(
                text(_resync_sequence_sql(spec.name)), {"t": spec.name}
            )
    await _audit(session, get_actor(), "factory-reset", {"users_kept": users or 0})
    await session.commit()
    return {"ok": True, "users_kept": users or 0}
