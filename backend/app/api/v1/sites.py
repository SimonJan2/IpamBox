from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import DATA_DELETE, DATA_WRITE, require_perm
from app.models.circuit import Circuit
from app.models.service import Service
from app.models.site import Site
from app.models.vrf import VRF
from app.schemas.site import SiteCreate, SiteOut, SiteUpdate
from app.services import runtime_settings
from app.services.ipam import IPAMError, get_or_404, slugify, vrf_name_for

router = APIRouter(prefix="/sites", tags=["sites"])


@router.get("", response_model=list[SiteOut])
async def list_sites(session: AsyncSession = Depends(get_session)):
    return (await session.execute(select(Site).order_by(Site.name))).scalars().all()


@router.post(
    "",
    response_model=SiteOut,
    status_code=201,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def create_site(body: SiteCreate, session: AsyncSession = Depends(get_session)):
    site = Site(
        **body.model_dump(exclude={"slug"}),
        slug=body.slug or slugify(body.name),
    )
    session.add(site)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(409, "site name or slug already exists")
    await session.refresh(site)
    return site


@router.get("/{site_id}", response_model=SiteOut)
async def get_site(site_id: int, session: AsyncSession = Depends(get_session)):
    try:
        return await get_or_404(session, Site, site_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))


async def _cascade_site_fields(
    session: AsyncSession,
    site: Site,
    old: dict,
) -> None:
    """Propagate site code/number/name changes to linked entities that were
    following the site's previous values (site_code_follow_site feature).

    A row "follows" a field when its stored value equals the site's previous
    value — or is NULL when the site's value was NULL. Anything else is a
    manual override and is left alone.
    """
    eff = await runtime_settings.get_effective(session)
    if not eff.values.get("site_code_follow_site"):
        return

    old_vrf = vrf_name_for(old["name"], old["code"], old["number"])
    new_vrf = vrf_name_for(site.name, site.code, site.site_number)
    if new_vrf != old_vrf:
        vrfs = (
            await session.execute(
                select(VRF).where(VRF.site_id == site.id, VRF.name == old_vrf)
            )
        ).scalars()
        for v in vrfs:
            v.name = new_vrf

    async def follow(model, col, old_v, new_v):
        if old_v == new_v:
            return
        cond = col == old_v if old_v is not None else col.is_(None)
        rows = (
            await session.execute(
                select(model).where(model.site_id == site.id, cond)
            )
        ).scalars()
        for row in rows:
            setattr(row, col.key, new_v)

    for model in (Circuit, Service):
        await follow(model, model.site_code, old["code"], site.code)
    await follow(Circuit, Circuit.site_number, old["number"], site.site_number)
    await follow(Circuit, Circuit.site_name, old["name"], site.name)


@router.patch(
    "/{site_id}",
    response_model=SiteOut,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def update_site(site_id: int, body: SiteUpdate, session: AsyncSession = Depends(get_session)):
    try:
        site = await get_or_404(session, Site, site_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    old = {"code": site.code, "number": site.site_number, "name": site.name}
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(site, field, value)
    await _cascade_site_fields(session, site, old)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(409, "site name or slug already exists")
    await session.refresh(site)
    return site


@router.delete(
    "/{site_id}",
    status_code=204,
    dependencies=[Depends(require_perm(DATA_DELETE))],
)
async def delete_site(site_id: int, session: AsyncSession = Depends(get_session)):
    try:
        site = await get_or_404(session, Site, site_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    await session.delete(site)
    await session.commit()
