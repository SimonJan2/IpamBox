import ipaddress

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import DATA_DELETE, DATA_WRITE, require_perm
from app.models.ip_range import IPRange
from app.models.prefix import Prefix
from app.schemas.common import Page
from app.schemas.ip_range import IPRangeCreate, IPRangeOut, IPRangeUpdate
from app.services import prefix_math
from app.services.ipam import IPAMError, get_or_404

router = APIRouter(prefix="/ranges", tags=["ranges"])


@router.get("", response_model=Page[IPRangeOut])
async def list_ranges(
    prefix_id: int | None = None,
    vrf_id: int | None = None,
    limit: int | None = Query(default=None, ge=1, le=20000),
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(IPRange).order_by(IPRange.start_int)
    if prefix_id is not None:
        stmt = stmt.where(IPRange.prefix_id == prefix_id)
    if vrf_id is not None:
        stmt = stmt.where(IPRange.vrf_id == vrf_id)
    total = await session.scalar(
        select(func.count()).select_from(stmt.order_by(None).subquery())
    )
    rows = (
        await session.execute(stmt.limit(limit).offset(offset))
    ).scalars().all()
    return Page(items=rows, total=total or 0, limit=limit, offset=offset)


async def _check_range_overlap(
    session: AsyncSession, prefix: Prefix, start: int, end: int, exclude_id: int | None = None
) -> None:
    stmt = select(IPRange).where(IPRange.prefix_id == prefix.id)
    if exclude_id is not None:
        stmt = stmt.where(IPRange.id != exclude_id)
    for r in (await session.execute(stmt)).scalars():
        if start <= int(r.end_int) and end >= int(r.start_int):
            raise HTTPException(
                409,
                f"range overlaps existing {r.start_address}–{r.end_address} (id={r.id})",
            )


@router.post(
    "",
    response_model=IPRangeOut,
    status_code=201,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def create_range(body: IPRangeCreate, session: AsyncSession = Depends(get_session)):
    try:
        prefix = await get_or_404(session, Prefix, body.prefix_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    net = prefix_math.to_network(prefix.prefix)
    start = ipaddress.ip_address(body.start_address)
    end = ipaddress.ip_address(body.end_address)
    if start.version != net.version or end.version != net.version:
        raise HTTPException(422, "range family does not match prefix")
    if start not in net or end not in net:
        raise HTTPException(422, f"range must fit inside {net}")
    await _check_range_overlap(session, prefix, int(start), int(end))
    row = IPRange(
        prefix_id=prefix.id,
        vrf_id=prefix.vrf_id,
        start_address=str(start),
        start_int=int(start),
        end_address=str(end),
        end_int=int(end),
        role=body.role,
        description=body.description,
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row


@router.patch(
    "/{range_id}",
    response_model=IPRangeOut,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def update_range(
    range_id: int, body: IPRangeUpdate, session: AsyncSession = Depends(get_session)
):
    try:
        row = await get_or_404(session, IPRange, range_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(row, field, value)
    await session.commit()
    await session.refresh(row)
    return row


@router.delete(
    "/{range_id}",
    status_code=204,
    dependencies=[Depends(require_perm(DATA_DELETE))],
)
async def delete_range(range_id: int, session: AsyncSession = Depends(get_session)):
    try:
        row = await get_or_404(session, IPRange, range_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    await session.delete(row)
    await session.commit()
