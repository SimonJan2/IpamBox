"""CRUD routers for the workbook-imported entity families.

Circuits, certificates, assets and services share the same surface:
list (+q text search), get, create, patch, delete. A small factory keeps the
four routers consistent with the hand-written ones (sites.py et al.).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import DATA_DELETE, DATA_WRITE, require_perm
from app.models.asset import Asset
from app.models.certificate import Certificate
from app.models.circuit import Circuit
from app.models.service import Service
from app.schemas.asset import AssetCreate, AssetOut, AssetUpdate
from app.schemas.certificate import (
    CertificateCreate,
    CertificateOut,
    CertificateUpdate,
)
from app.schemas.circuit import CircuitCreate, CircuitOut, CircuitUpdate
from app.schemas.common import ReorderBody
from app.schemas.service import ServiceCreate, ServiceOut, ServiceUpdate
from app.services.colors import stamp_colors
from app.services.ipam import IPAMError, get_or_404
from app.services.ordering import ordered, reorder


def _crud_router(prefix, tag, model, out_schema, create_schema, update_schema,
                 search_fields):
    entity_type = prefix.lstrip("/")
    router = APIRouter(prefix=prefix, tags=[tag])

    @router.get("", response_model=list[out_schema])
    async def list_items(
        q: str = "",
        session: AsyncSession = Depends(get_session),
    ):
        stmt = select(model)
        if q:
            from app.services.workbook.normalize import fold_hebrew

            # Fold Hebrew final letters (ם→מ …) on both sides so q= "רשת"
            # also matches stored "רשתו"/final forms.
            like = f"%{fold_hebrew(q)}%"
            stmt = stmt.where(
                or_(
                    *(
                        func.translate(f, "םןץףך", "מנצפכ").ilike(like)
                        for f in search_fields
                        if f is not None
                    )
                )
            )
        stmt = ordered(stmt, model, model.id)
        rows = (await session.execute(stmt)).scalars().all()
        return await stamp_colors(session, entity_type, rows)

    @router.post(
        "",
        response_model=out_schema,
        status_code=201,
        dependencies=[Depends(require_perm(DATA_WRITE))],
    )
    async def create_item(body: create_schema,  # type: ignore[valid-type]
                          session: AsyncSession = Depends(get_session)):
        obj = model(**body.model_dump())
        session.add(obj)
        try:
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(409, "duplicate or invalid value") from e
        await session.refresh(obj)
        await stamp_colors(session, entity_type, [obj])
        return obj

    # Declared before /{item_id} so the literal path can't be shadowed.
    @router.post(
        "/reorder",
        status_code=204,
        dependencies=[Depends(require_perm(DATA_WRITE))],
    )
    async def reorder_items(
        body: ReorderBody, session: AsyncSession = Depends(get_session)
    ):
        try:
            await reorder(session, model, body.ids)
        except IPAMError as e:
            raise HTTPException(e.status_code, str(e))

    @router.get("/{item_id}", response_model=out_schema)
    async def get_item(item_id: int, session: AsyncSession = Depends(get_session)):
        try:
            obj = await get_or_404(session, model, item_id)
        except IPAMError as e:
            raise HTTPException(e.status_code, str(e))
        await stamp_colors(session, entity_type, [obj])
        return obj

    @router.patch(
        "/{item_id}",
        response_model=out_schema,
        dependencies=[Depends(require_perm(DATA_WRITE))],
    )
    async def update_item(item_id: int, body: update_schema,  # type: ignore[valid-type]
                          session: AsyncSession = Depends(get_session)):
        try:
            obj = await get_or_404(session, model, item_id)
        except IPAMError as e:
            raise HTTPException(e.status_code, str(e))
        for field, value in body.model_dump(exclude_unset=True).items():
            setattr(obj, field, value)
        try:
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(409, "duplicate or invalid value") from e
        await session.refresh(obj)
        await stamp_colors(session, entity_type, [obj])
        return obj

    @router.delete(
        "/{item_id}",
        status_code=204,
        dependencies=[Depends(require_perm(DATA_DELETE))],
    )
    async def delete_item(item_id: int, session: AsyncSession = Depends(get_session)):
        try:
            obj = await get_or_404(session, model, item_id)
        except IPAMError as e:
            raise HTTPException(e.status_code, str(e))
        await session.delete(obj)
        await session.commit()

    return router


circuits_router = _crud_router(
    "/circuits", "circuits", Circuit, CircuitOut, CircuitCreate, CircuitUpdate,
    [Circuit.site_name, Circuit.site_code, Circuit.bezeq_circuit_id,
     Circuit.node, Circuit.app_client_name, Circuit.line_type, Circuit.env,
     Circuit.status],
)

certificates_router = _crud_router(
    "/certificates", "certificates", Certificate, CertificateOut,
    CertificateCreate, CertificateUpdate,
    [Certificate.platform, Certificate.target, Certificate.server_name,
     Certificate.cert_name],
)

assets_router = _crud_router(
    "/assets", "assets", Asset, AssetOut, AssetCreate, AssetUpdate,
    [Asset.category, Asset.vendor, Asset.model, Asset.purpose,
     Asset.serial_number],
)

services_router = _crud_router(
    "/services", "services", Service, ServiceOut, ServiceCreate, ServiceUpdate,
    [Service.name, Service.beneficiary, Service.site_code, Service.doc_path],
)
