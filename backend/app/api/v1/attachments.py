"""Entity file attachments (V13).

Upload is a raw body + ``?entity_type=&entity_id=&filename=&label=`` — the
same pattern as the workbook import endpoint. Rows are bytes+metadata: the
list/get surfaces never carry the blob (the Out schema omits it and the
list query defers the column); only ``GET /{id}/download`` streams it,
always as ``Content-Disposition: attachment`` so stored HTML/SVG can never
render inline. Deleting an entity sweeps its attachments in the same
transaction — see core.attachment_refs.
"""
import re
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import defer

from app.core.attachment_refs import ATTACHABLE_MODELS
from app.core.db import get_session
from app.core.deps import DATA_DELETE, DATA_WRITE, require_perm
from app.core.security import get_actor
from app.models.attachment import Attachment
from app.schemas.attachment import AttachmentOut

router = APIRouter(prefix="/attachments", tags=["attachments"])

MAX_ATTACHMENT_BYTES = 6 * 1024 * 1024

# Broad-but-honest allowlist: things we can render (images, text), archives
# and documents we merely store (pdf, zip, json), plus octet-stream for
# binary exports with no useful mime (cert bundles, firmware). Blobs are
# only ever served as downloads — nothing here is rendered inline by
# content-type.
_ALLOWED_PREFIXES = ("image/", "text/")
_ALLOWED_TYPES = {
    "application/pdf",
    "application/zip",
    "application/x-zip-compressed",
    "application/json",
    "application/octet-stream",
}

_FILENAME_SAFE = re.compile(r"[^A-Za-z0-9._-]+")


def _content_type(request: Request) -> str:
    raw = (request.headers.get("content-type") or "").split(";")[0].strip().lower()
    return raw or "application/octet-stream"


def _allowed(content_type: str) -> bool:
    return content_type in _ALLOWED_TYPES or content_type.startswith(
        _ALLOWED_PREFIXES
    )


def _content_disposition(filename: str) -> str:
    # ASCII fallback name + RFC 5987 encoded form for non-ASCII filenames.
    fallback = _FILENAME_SAFE.sub("_", filename).strip("._") or "file"
    return (
        f'attachment; filename="{fallback}"; '
        f"filename*=UTF-8''{quote(filename)}"
    )


@router.post(
    "",
    response_model=AttachmentOut,
    status_code=201,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def upload_attachment(
    request: Request,
    entity_type: str,
    entity_id: int,
    label: str | None = Query(default=None, max_length=255),
    filename: str = Query(default="file"),
    session: AsyncSession = Depends(get_session),
):
    """Attach a file to an entity. Raw request body is the file bytes."""
    model = ATTACHABLE_MODELS.get(entity_type)
    if model is None:
        raise HTTPException(
            422,
            f"entity_type must be one of {sorted(ATTACHABLE_MODELS)}",
        )
    if await session.get(model, entity_id) is None:
        raise HTTPException(404, f"{entity_type} {entity_id} not found")

    payload = await request.body()
    if len(payload) > MAX_ATTACHMENT_BYTES:
        raise HTTPException(
            413, f"file too large — attachments are capped at 6 MB"
        )
    if not payload:
        raise HTTPException(422, "empty file")
    content_type = _content_type(request)
    if not _allowed(content_type):
        raise HTTPException(
            422, f"unsupported content type {content_type!r}"
        )

    att = Attachment(
        entity_type=entity_type,
        entity_id=entity_id,
        label=(label or "").strip() or None,
        filename=(Path(filename).name or "file")[:255],
        content_type=content_type[:128],
        size=len(payload),
        blob=payload,
        uploaded_by=get_actor(),
    )
    session.add(att)
    await session.commit()
    await session.refresh(att)
    return att


@router.get("", response_model=list[AttachmentOut])
async def list_attachments(
    entity_type: str,
    entity_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Metadata list for one entity — never the blob column."""
    if entity_type not in ATTACHABLE_MODELS:
        raise HTTPException(
            422,
            f"entity_type must be one of {sorted(ATTACHABLE_MODELS)}",
        )
    rows = (
        await session.execute(
            select(Attachment)
            .where(
                Attachment.entity_type == entity_type,
                Attachment.entity_id == entity_id,
            )
            .options(defer(Attachment.blob))
            .order_by(Attachment.created_at.desc(), Attachment.id.desc())
        )
    ).scalars().all()
    return rows


@router.get("/{attachment_id}/download")
async def download_attachment(
    attachment_id: int, session: AsyncSession = Depends(get_session)
):
    att = await session.get(Attachment, attachment_id)
    if att is None:
        raise HTTPException(404, "attachment not found")
    return Response(
        content=bytes(att.blob),
        media_type=att.content_type or "application/octet-stream",
        headers={
            "Content-Disposition": _content_disposition(att.filename),
            "Content-Length": str(att.size),
        },
    )


@router.delete(
    "/{attachment_id}",
    status_code=204,
    dependencies=[Depends(require_perm(DATA_DELETE))],
)
async def delete_attachment(
    attachment_id: int, session: AsyncSession = Depends(get_session)
):
    """Delete an attachment. Replace = delete + re-upload — no PATCH, so
    the changelog reads as honest history."""
    att = await session.get(Attachment, attachment_id)
    if att is None:
        raise HTTPException(404, "attachment not found")
    await session.delete(att)
    await session.commit()
