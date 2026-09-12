from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.models.ip_address import IPAddress, IPStatus
from app.schemas.ip_address import IPAddressOut
from app.services.ipam import IPAMError, get_or_404

router = APIRouter(prefix="/discovery", tags=["discovery"])


@router.get("", response_model=list[IPAddressOut])
async def list_discovered(session: AsyncSession = Depends(get_session)):
    """Unconfirmed hosts found by scanners, pending admin review."""
    return (
        await session.execute(
            select(IPAddress)
            .where(IPAddress.status == IPStatus.DISCOVERED)
            .order_by(IPAddress.address_int)
        )
    ).scalars().all()


class ConfirmBody(BaseModel):
    hostname: str | None = Field(default=None, max_length=255)
    notes: str | None = None
    status: IPStatus = IPStatus.ACTIVE


@router.post("/{address_id}/confirm", response_model=IPAddressOut)
async def confirm_discovered(
    address_id: int, body: ConfirmBody | None = None, session: AsyncSession = Depends(get_session)
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
    await session.commit()
    await session.refresh(row)
    return row
