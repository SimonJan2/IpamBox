from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import DATA_DELETE, DATA_WRITE, require_perm
from app.models.vrf import VRF
from app.schemas.common import ReorderBody
from app.schemas.vrf import VRFCreate, VRFOut, VRFUpdate
from app.services.colors import stamp_colors
from app.services.ipam import IPAMError, get_or_404
from app.services.ordering import ordered, reorder

router = APIRouter(prefix="/vrfs", tags=["vrfs"])


@router.get("", response_model=list[VRFOut])
async def list_vrfs(session: AsyncSession = Depends(get_session)):
    stmt = ordered(select(VRF), VRF, VRF.name)
    rows = (await session.execute(stmt)).scalars().all()
    return await stamp_colors(session, "vrfs", rows)


@router.post(
    "",
    response_model=VRFOut,
    status_code=201,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def create_vrf(body: VRFCreate, session: AsyncSession = Depends(get_session)):
    vrf = VRF(**body.model_dump())
    session.add(vrf)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(409, "VRF name or RD already exists")
    await session.refresh(vrf)
    await stamp_colors(session, "vrfs", [vrf])
    return vrf


# Declared before /{vrf_id} so the literal path can't be shadowed.
@router.post(
    "/reorder",
    status_code=204,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def reorder_vrfs(
    body: ReorderBody, session: AsyncSession = Depends(get_session)
):
    try:
        await reorder(session, VRF, body.ids)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))


@router.get("/{vrf_id}", response_model=VRFOut)
async def get_vrf(vrf_id: int, session: AsyncSession = Depends(get_session)):
    try:
        vrf = await get_or_404(session, VRF, vrf_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    await stamp_colors(session, "vrfs", [vrf])
    return vrf


@router.patch(
    "/{vrf_id}",
    response_model=VRFOut,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def update_vrf(vrf_id: int, body: VRFUpdate, session: AsyncSession = Depends(get_session)):
    try:
        vrf = await get_or_404(session, VRF, vrf_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(vrf, field, value)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(409, "VRF name or RD already exists")
    await session.refresh(vrf)
    await stamp_colors(session, "vrfs", [vrf])
    return vrf


@router.delete(
    "/{vrf_id}",
    status_code=204,
    dependencies=[Depends(require_perm(DATA_DELETE))],
)
async def delete_vrf(vrf_id: int, session: AsyncSession = Depends(get_session)):
    try:
        vrf = await get_or_404(session, VRF, vrf_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    await session.delete(vrf)
    await session.commit()
