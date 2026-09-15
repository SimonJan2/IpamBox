from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import DATA_DELETE, DATA_WRITE, require_perm
from app.models.site import Site
from app.models.vlan import VLAN, VLANGroup
from app.schemas.vlan import (
    VLANCreate,
    VLANGroupCreate,
    VLANGroupOut,
    VLANGroupUpdate,
    VLANOut,
    VLANUpdate,
)
from app.services.ipam import IPAMError, get_or_404

router = APIRouter(tags=["vlans"])


@router.get("/vlan-groups", response_model=list[VLANGroupOut])
async def list_vlan_groups(session: AsyncSession = Depends(get_session)):
    stmt = (
        select(VLANGroup, func.count(VLAN.id).label("vlan_count"))
        .outerjoin(VLAN, VLAN.group_id == VLANGroup.id)
        .group_by(VLANGroup.id)
        .order_by(VLANGroup.name)
    )
    out = []
    for group, count in (await session.execute(stmt)).all():
        group.vlan_count = count
        out.append(group)
    return out


@router.post(
    "/vlan-groups",
    response_model=VLANGroupOut,
    status_code=201,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def create_vlan_group(
    body: VLANGroupCreate, session: AsyncSession = Depends(get_session)
):
    g = VLANGroup(**body.model_dump())
    session.add(g)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(409, "vlan group already exists")
    await session.refresh(g)
    return g


@router.patch(
    "/vlan-groups/{group_id}",
    response_model=VLANGroupOut,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def update_vlan_group(
    group_id: int, body: VLANGroupUpdate, session: AsyncSession = Depends(get_session)
):
    try:
        g = await get_or_404(session, VLANGroup, group_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(g, field, value)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(409, "vlan group already exists")
    await session.refresh(g)
    g.vlan_count = await session.scalar(
        select(func.count(VLAN.id)).where(VLAN.group_id == g.id)
    )
    return g


@router.delete(
    "/vlan-groups/{group_id}",
    status_code=204,
    dependencies=[Depends(require_perm(DATA_DELETE))],
)
async def delete_vlan_group(group_id: int, session: AsyncSession = Depends(get_session)):
    try:
        g = await get_or_404(session, VLANGroup, group_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    await session.delete(g)
    await session.commit()


async def _check_duplicate_vid(
    session: AsyncSession, vid: int, group_id: int | None, exclude_id: int | None = None
) -> None:
    """One VID may exist once per group (NULL group = ungrouped)."""
    stmt = select(VLAN).where(VLAN.vid == vid)
    stmt = stmt.where(
        VLAN.group_id.is_(None) if group_id is None else VLAN.group_id == group_id
    )
    if exclude_id is not None:
        stmt = stmt.where(VLAN.id != exclude_id)
    if (await session.execute(stmt)).scalar_one_or_none() is not None:
        scope = "this group" if group_id else "the ungrouped scope"
        raise HTTPException(409, f"VLAN {vid} already exists in {scope}")


@router.get("/vlans", response_model=list[VLANOut])
async def list_vlans(
    group_id: int | None = None,
    site_id: int | None = None,
    q: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(VLAN).order_by(VLAN.vid)
    if group_id is not None:
        stmt = stmt.where(VLAN.group_id == group_id)
    if site_id is not None:
        stmt = stmt.where(VLAN.site_id == site_id)
    rows = (await session.execute(stmt)).scalars().all()
    if q:
        from app.services.workbook.normalize import fold_hebrew

        ql = fold_hebrew(q.lower())
        rows = [
            v
            for v in rows
            if ql in fold_hebrew(v.name.lower()) or ql in str(v.vid)
        ]
    return rows


@router.post(
    "/vlans",
    response_model=VLANOut,
    status_code=201,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def create_vlan(body: VLANCreate, session: AsyncSession = Depends(get_session)):
    try:
        if body.group_id is not None:
            await get_or_404(session, VLANGroup, body.group_id)
        if body.site_id is not None:
            await get_or_404(session, Site, body.site_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    await _check_duplicate_vid(session, body.vid, body.group_id)
    vlan = VLAN(**body.model_dump())
    session.add(vlan)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(400, "invalid vlan data")
    await session.refresh(vlan)
    return vlan


@router.patch(
    "/vlans/{vlan_id}",
    response_model=VLANOut,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def update_vlan(
    vlan_id: int, body: VLANUpdate, session: AsyncSession = Depends(get_session)
):
    try:
        vlan = await get_or_404(session, VLAN, vlan_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    data = body.model_dump(exclude_unset=True)
    if "vid" in data or "group_id" in data:
        await _check_duplicate_vid(
            session,
            data.get("vid", vlan.vid),
            data.get("group_id", vlan.group_id),
            exclude_id=vlan.id,
        )
    for field, value in data.items():
        setattr(vlan, field, value)
    await session.commit()
    await session.refresh(vlan)
    return vlan


@router.delete(
    "/vlans/{vlan_id}",
    status_code=204,
    dependencies=[Depends(require_perm(DATA_DELETE))],
)
async def delete_vlan(vlan_id: int, session: AsyncSession = Depends(get_session)):
    try:
        vlan = await get_or_404(session, VLAN, vlan_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    await session.delete(vlan)
    await session.commit()
