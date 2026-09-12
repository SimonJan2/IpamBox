import ipaddress

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.models.ip_address import IPAddress, IPStatus
from app.models.prefix import Prefix
from app.schemas.ip_address import IPAddressCreate, IPAddressOut, IPAddressUpdate
from app.services.ipam import IPAMError, get_or_404
from app.services import prefix_math

router = APIRouter(prefix="/addresses", tags=["addresses"])


@router.get("", response_model=list[IPAddressOut])
async def list_addresses(
    vrf_id: int | None = None,
    prefix_id: int | None = None,
    status: IPStatus | None = None,
    q: str | None = Query(default=None, description="match address/hostname/mac"),
    limit: int = Query(default=500, le=5000),
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(IPAddress).order_by(IPAddress.address_int).limit(limit).offset(offset)
    if vrf_id is not None:
        stmt = stmt.where(IPAddress.vrf_id == vrf_id)
    if prefix_id is not None:
        stmt = stmt.where(IPAddress.prefix_id == prefix_id)
    if status is not None:
        stmt = stmt.where(IPAddress.status == status)
    rows = (await session.execute(stmt)).scalars().all()
    if q:
        ql = q.lower()
        rows = [
            r
            for r in rows
            if ql in str(r.address)
            or (r.hostname and ql in r.hostname.lower())
            or (r.mac_address and ql in r.mac_address.lower())
        ]
    return rows


@router.post("", response_model=IPAddressOut, status_code=201)
async def create_address(body: IPAddressCreate, session: AsyncSession = Depends(get_session)):
    try:
        prefix = await get_or_404(session, Prefix, body.prefix_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))

    ip = ipaddress.ip_address(body.address)
    net = prefix_math.to_network(prefix.prefix)
    if ip not in net:
        raise HTTPException(422, f"{ip} is not inside prefix {net}")

    row = IPAddress(
        address=str(ip),
        address_int=int(ip),
        prefix_id=prefix.id,
        vrf_id=prefix.vrf_id,
        mac_address=body.mac_address,
        hostname=body.hostname,
        vendor=body.vendor,
        status=body.status,
        notes=body.notes,
    )
    session.add(row)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(409, f"{ip} already exists in this VRF")
    await session.refresh(row)
    return row


@router.get("/{address_id}", response_model=IPAddressOut)
async def get_address(address_id: int, session: AsyncSession = Depends(get_session)):
    try:
        return await get_or_404(session, IPAddress, address_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))


@router.patch("/{address_id}", response_model=IPAddressOut)
async def update_address(
    address_id: int, body: IPAddressUpdate, session: AsyncSession = Depends(get_session)
):
    try:
        row = await get_or_404(session, IPAddress, address_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    data = body.model_dump(exclude_unset=True)
    if "prefix_id" in data and data["prefix_id"] is not None:
        try:
            new_prefix = await get_or_404(session, Prefix, data["prefix_id"])
        except IPAMError as e:
            raise HTTPException(e.status_code, str(e))
        ip = ipaddress.ip_address(str(row.address).split("/")[0])
        if ip not in prefix_math.to_network(new_prefix.prefix):
            raise HTTPException(422, f"{ip} is not inside prefix {new_prefix.prefix}")
        row.vrf_id = new_prefix.vrf_id
    for field, value in data.items():
        setattr(row, field, value)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(409, "address already exists in this VRF")
    await session.refresh(row)
    return row


@router.delete("/{address_id}", status_code=204)
async def delete_address(address_id: int, session: AsyncSession = Depends(get_session)):
    try:
        row = await get_or_404(session, IPAddress, address_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    await session.delete(row)
    await session.commit()
