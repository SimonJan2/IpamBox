from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.models.change_log import ChangeLog
from app.schemas.changelog import ChangeLogOut
from app.schemas.common import Page

router = APIRouter(prefix="/changelog", tags=["changelog"])


@router.get("", response_model=Page[ChangeLogOut])
async def list_changelog(
    object_type: str | None = None,
    object_id: int | None = None,
    action: str | None = Query(default=None, pattern="^(create|update|delete)$"),
    # the audit log stays bounded by default — pass ?limit=&offset= to page
    limit: int = Query(default=200, le=1000),
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(ChangeLog).order_by(ChangeLog.id.desc())
    if object_type is not None:
        stmt = stmt.where(ChangeLog.object_type == object_type)
    if object_id is not None:
        stmt = stmt.where(ChangeLog.object_id == object_id)
    if action is not None:
        stmt = stmt.where(ChangeLog.action == action)
    total = await session.scalar(
        select(func.count()).select_from(stmt.order_by(None).subquery())
    )
    rows = (
        await session.execute(stmt.limit(limit).offset(offset))
    ).scalars().all()
    return Page(items=rows, total=total or 0, limit=limit, offset=offset)
