from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.models.change_log import ChangeLog
from app.schemas.changelog import ChangeLogOut

router = APIRouter(prefix="/changelog", tags=["changelog"])


@router.get("", response_model=list[ChangeLogOut])
async def list_changelog(
    object_type: str | None = None,
    object_id: int | None = None,
    action: str | None = Query(default=None, pattern="^(create|update|delete)$"),
    limit: int = Query(default=200, le=1000),
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(ChangeLog)
        .order_by(ChangeLog.id.desc())
        .limit(limit)
        .offset(offset)
    )
    if object_type is not None:
        stmt = stmt.where(ChangeLog.object_type == object_type)
    if object_id is not None:
        stmt = stmt.where(ChangeLog.object_id == object_id)
    if action is not None:
        stmt = stmt.where(ChangeLog.action == action)
    return (await session.execute(stmt)).scalars().all()
