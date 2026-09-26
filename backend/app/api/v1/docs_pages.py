"""User-authored docs pages (V13).

Same CRUD surface as the entity routers (sites.py et al.) but hand-written:
slugs are generated server-side (slugify + ``-2`` collision suffix) which the
_crud_router factory can't carry. User pages render under /docs/pages/<slug>;
builtin help keeps /docs/<slug> — the two never share a namespace.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import DATA_DELETE, DATA_WRITE, require_perm
from app.core.security import get_actor
from app.models.docs_page import DocsPage
from app.schemas.common import Page
from app.schemas.docs_page import DocsPageCreate, DocsPageOut, DocsPageUpdate
from app.services.ipam import IPAMError, get_or_404, slugify

router = APIRouter(prefix="/docs-pages", tags=["docs"])

# /docs/pages/new is the frontend's editor route — a page slugged "new"
# would be unreachable, so the word stays reserved on the backend too.
RESERVED_SLUGS = {"new"}


async def _unique_slug(session: AsyncSession, raw: str) -> str:
    """slugify + dedup against existing page slugs (x, x-2, x-3…)."""
    base = slugify(raw, "page")
    existing = set((await session.execute(select(DocsPage.slug))).scalars())
    slug = base
    n = 2
    while slug in existing or slug in RESERVED_SLUGS:
        slug = f"{base}-{n}"
        n += 1
    return slug


@router.get("", response_model=Page[DocsPageOut])
async def list_pages(
    q: str = "",
    category: str | None = None,
    limit: int | None = Query(default=None, ge=1, le=20000),
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(DocsPage)
    if q:
        from app.services.workbook.normalize import fold_hebrew

        # Fold Hebrew final letters (ם→מ …) on both sides so q= "רשת"
        # also matches stored "רשתו"/final forms — same trick as the
        # entity routers.
        like = f"%{fold_hebrew(q)}%"
        stmt = stmt.where(
            or_(
                func.translate(DocsPage.title, "םןץףך", "מנצפכ").ilike(like),
                func.translate(DocsPage.category, "םןץףך", "מנצפכ").ilike(like),
            )
        )
    if category is not None:
        stmt = stmt.where(DocsPage.category == category)
    stmt = stmt.order_by(DocsPage.title, DocsPage.id)
    total = await session.scalar(
        select(func.count()).select_from(stmt.order_by(None).subquery())
    )
    rows = (
        await session.execute(stmt.limit(limit).offset(offset))
    ).scalars().all()
    return Page(items=rows, total=total or 0, limit=limit, offset=offset)


# Declared before /{page_id} so the literal path can't be shadowed.
@router.get("/slug/{slug}", response_model=DocsPageOut)
async def get_page_by_slug(
    slug: str, session: AsyncSession = Depends(get_session)
):
    page = (
        await session.execute(
            select(DocsPage).where(DocsPage.slug == slug)
        )
    ).scalar_one_or_none()
    if page is None:
        raise HTTPException(404, "page not found")
    return page


@router.get("/{page_id}", response_model=DocsPageOut)
async def get_page(page_id: int, session: AsyncSession = Depends(get_session)):
    try:
        return await get_or_404(session, DocsPage, page_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))


@router.post(
    "",
    response_model=DocsPageOut,
    status_code=201,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def create_page(
    body: DocsPageCreate, session: AsyncSession = Depends(get_session)
):
    page = DocsPage(
        title=body.title,
        slug=await _unique_slug(session, body.slug or body.title),
        category=body.category or "notes",
        body=body.body,
        created_by=get_actor(),
    )
    session.add(page)
    await session.commit()
    await session.refresh(page)
    return page


@router.patch(
    "/{page_id}",
    response_model=DocsPageOut,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def update_page(
    page_id: int,
    body: DocsPageUpdate,
    session: AsyncSession = Depends(get_session),
):
    try:
        page = await get_or_404(session, DocsPage, page_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    fields = body.model_dump(exclude_unset=True)
    if "slug" in fields:
        slug = slugify(fields.pop("slug") or page.title, "page")
        if slug != page.slug:
            taken = await session.scalar(
                select(func.count(DocsPage.id)).where(
                    DocsPage.slug == slug, DocsPage.id != page.id
                )
            )
            if taken or slug in RESERVED_SLUGS:
                raise HTTPException(409, "slug already in use")
            page.slug = slug
    for field, value in fields.items():
        setattr(page, field, value)
    await session.commit()
    await session.refresh(page)
    return page


@router.delete(
    "/{page_id}",
    status_code=204,
    dependencies=[Depends(require_perm(DATA_DELETE))],
)
async def delete_page(page_id: int, session: AsyncSession = Depends(get_session)):
    try:
        page = await get_or_404(session, DocsPage, page_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    await session.delete(page)
    await session.commit()
