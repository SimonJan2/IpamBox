from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import DATA_WRITE, require_perm
from app.models.ip_address import IPAddress, IPStatus
from app.schemas.common import Page
from app.schemas.ip_address import IPAddressOut
from app.services.ipam import IPAMError, get_or_404
from app.services.ranges import (
    apply_pool_membership,
    ranges_for_prefix,
    stamp_range_roles,
)

router = APIRouter(prefix="/discovery", tags=["discovery"])


@router.get("", response_model=Page[IPAddressOut])
async def list_discovered(
    limit: int | None = Query(default=None, ge=1, le=20000),
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    """Unconfirmed hosts found by scanners, pending admin review.
    No limit -> the full set inside a {items, total} envelope."""
    stmt = (
        select(IPAddress)
        .where(IPAddress.status == IPStatus.DISCOVERED)
        .order_by(IPAddress.address_int)
    )
    total = await session.scalar(
        select(func.count()).select_from(stmt.order_by(None).subquery())
    )
    items = (
        await session.execute(stmt.limit(limit).offset(offset))
    ).scalars().all()
    return Page(items=items, total=total or 0, limit=limit, offset=offset)


class ConfirmBody(BaseModel):
    hostname: str | None = Field(default=None, max_length=255)
    notes: str | None = None
    status: IPStatus = IPStatus.ACTIVE


@router.post(
    "/{address_id}/confirm",
    response_model=IPAddressOut,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def confirm_discovered(
    address_id: int,
    body: ConfirmBody | None = None,
    force: bool = Query(default=False),
    session: AsyncSession = Depends(get_session),
):
    """One-click confirm a discovered host (default -> Active)."""
    try:
        row = await get_or_404(session, IPAddress, address_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    body = body or ConfirmBody()
    row.status = body.status
    if body.hostname is not None:
        row.hostname = body.hostname
    if body.notes is not None:
        row.notes = body.notes
    try:
        # Confirming to active/reserved inside a dhcp/pool range hits the
        # same pool guard as the address write path.
        apply_pool_membership(
            row, await ranges_for_prefix(session, row.prefix_id), force=force
        )
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    await session.commit()
    await session.refresh(row)
    await stamp_range_roles(session, [row])
    return row
