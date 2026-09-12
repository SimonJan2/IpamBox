from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.models.site import Site
from app.schemas.site import SiteCreate, SiteOut, SiteUpdate
from app.services.ipam import IPAMError, get_or_404, slugify

router = APIRouter(prefix="/sites", tags=["sites"])


@router.get("", response_model=list[SiteOut])
async def list_sites(session: AsyncSession = Depends(get_session)):
    return (await session.execute(select(Site).order_by(Site.name))).scalars().all()


@router.post("", response_model=SiteOut, status_code=201)
async def create_site(body: SiteCreate, session: AsyncSession = Depends(get_session)):
    site = Site(name=body.name, slug=body.slug or slugify(body.name), description=body.description)
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


@router.patch("/{site_id}", response_model=SiteOut)
async def update_site(site_id: int, body: SiteUpdate, session: AsyncSession = Depends(get_session)):
    try:
        site = await get_or_404(session, Site, site_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(site, field, value)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(409, "site name or slug already exists")
    await session.refresh(site)
    return site


@router.delete("/{site_id}", status_code=204)
async def delete_site(site_id: int, session: AsyncSession = Depends(get_session)):
    try:
        site = await get_or_404(session, Site, site_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    await session.delete(site)
    await session.commit()
