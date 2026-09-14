from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import DATA_DELETE, DATA_WRITE, require_perm
from app.models.tag import Tag, TagAssignment
from app.schemas.tag import (
    TAGGABLE,
    AssignBody,
    TagAssignmentOut,
    TagCreate,
    TagOut,
    TagUpdate,
)
from app.services.ipam import IPAMError, get_or_404, slugify

router = APIRouter(prefix="/tags", tags=["tags"])

# declared before /{tag_id} so "assignments" isn't parsed as an id
@router.get("/assignments", response_model=list[TagAssignmentOut])
async def list_assignments(
    object_type: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(TagAssignment)
    if object_type is not None:
        stmt = stmt.where(TagAssignment.object_type == object_type)
    return (await session.execute(stmt)).scalars().all()


@router.get("", response_model=list[TagOut])
async def list_tags(session: AsyncSession = Depends(get_session)):
    return (
        (await session.execute(select(Tag).order_by(Tag.name))).scalars().all()
    )


@router.post(
    "",
    response_model=TagOut,
    status_code=201,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def create_tag(body: TagCreate, session: AsyncSession = Depends(get_session)):
    tag = Tag(
        name=body.name,
        slug=body.slug or slugify(body.name),
        color=body.color,
        description=body.description,
    )
    session.add(tag)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(409, "tag name or slug already exists")
    await session.refresh(tag)
    return tag


@router.get("/{tag_id}", response_model=TagOut)
async def get_tag(tag_id: int, session: AsyncSession = Depends(get_session)):
    try:
        return await get_or_404(session, Tag, tag_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))


@router.patch(
    "/{tag_id}",
    response_model=TagOut,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def update_tag(
    tag_id: int, body: TagUpdate, session: AsyncSession = Depends(get_session)
):
    try:
        tag = await get_or_404(session, Tag, tag_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    data = body.model_dump(exclude_unset=True)
    if "name" in data and data["name"]:
        data["slug"] = slugify(data["name"])
    for field, value in data.items():
        setattr(tag, field, value)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(409, "tag name or slug already exists")
    await session.refresh(tag)
    return tag


@router.delete(
    "/{tag_id}",
    status_code=204,
    dependencies=[Depends(require_perm(DATA_DELETE))],
)
async def delete_tag(tag_id: int, session: AsyncSession = Depends(get_session)):
    try:
        tag = await get_or_404(session, Tag, tag_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    await session.delete(tag)
    await session.commit()


@router.post(
    "/{tag_id}/assignments",
    response_model=TagAssignmentOut,
    status_code=201,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def assign_tag(
    tag_id: int, body: AssignBody, session: AsyncSession = Depends(get_session)
):
    try:
        await get_or_404(session, Tag, tag_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    row = TagAssignment(
        tag_id=tag_id, object_type=body.object_type, object_id=body.object_id
    )
    session.add(row)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(409, "already assigned")
    await session.refresh(row)
    return row


@router.delete(
    "/{tag_id}/assignments/{object_type}/{object_id}",
    status_code=204,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def unassign_tag(
    tag_id: int,
    object_type: str,
    object_id: int,
    session: AsyncSession = Depends(get_session),
):
    if object_type not in TAGGABLE:
        raise HTTPException(422, f"object_type must be one of {sorted(TAGGABLE)}")
    await session.execute(
        delete(TagAssignment).where(
            TagAssignment.tag_id == tag_id,
            TagAssignment.object_type == object_type,
            TagAssignment.object_id == object_id,
        )
    )
    await session.commit()
