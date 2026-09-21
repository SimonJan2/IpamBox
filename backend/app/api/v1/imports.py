"""Workbook import endpoints: upload -> detect -> preview -> commit.

The uploaded file is stored under import_dir; preview parses it, resolves
sites/VRFs/prefixes and dedupes against the DB, then stores the normalized
plan on the batch row so commit runs exactly what was reviewed.
"""
import hashlib
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_session
from app.core.deps import DATA_WRITE, require_perm
from app.core.security import get_actor
from app.models.import_batch import ImportBatch, ImportBatchStatus
from app.models.user import User
from app.schemas.common import Page
from app.schemas.import_batch import (
    CommitOptions,
    ImportBatchOut,
    PreviewOptions,
)
from app.services.ipam import IPAMError, get_or_404
from app.services.workbook.execute import PlanError, commit_batch
from app.services.workbook.plan import build_import_plan
from app.services.workbook.reader import load_workbook_bytes

router = APIRouter(prefix="/imports", tags=["imports"])
settings = get_settings()

MAX_IMPORT_BYTES = 64 * 1024 * 1024


def _import_dir() -> Path:
    d = settings.import_dir_path
    d.mkdir(parents=True, exist_ok=True)
    return d


def _safe_stored(batch_id: int, filename: str) -> Path:
    name = Path(filename).name or "workbook.xlsx"
    return _import_dir() / f"batch_{batch_id}_{name}"


def _load_sheets(batch: ImportBatch):
    path = Path(batch.stored_path)
    if not path.is_file():
        raise HTTPException(410, "stored workbook file is gone — re-upload")
    try:
        return load_workbook_bytes(path.read_bytes())
    except Exception as e:
        raise HTTPException(422, f"cannot parse workbook: {e}")


@router.post(
    "/workbook",
    status_code=201,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def upload_workbook(
    request: Request,
    session: AsyncSession = Depends(get_session),
    filename: str = "workbook.xlsx",
):
    """Upload an .xlsx as raw body (?filename=…). Stores the file, runs sheet
    detection, returns the batch + per-sheet family summary."""
    payload = await request.body()
    if len(payload) > MAX_IMPORT_BYTES:
        raise HTTPException(413, "workbook too large")
    if not zipfile.is_zipfile(__import__("io").BytesIO(payload)):
        raise HTTPException(422, "not an .xlsx file (expected a ZIP container)")

    try:
        sheets = load_workbook_bytes(payload)
    except Exception as e:
        raise HTTPException(422, f"cannot parse workbook: {e}")

    batch = ImportBatch(
        filename=Path(filename).name,
        stored_path="",
        sha256=hashlib.sha256(payload).hexdigest(),
        status=ImportBatchStatus.DRAFT,
        stats={},
        actor=get_actor(),
    )
    session.add(batch)
    await session.flush()
    batch.stored_path = str(_safe_stored(batch.id, filename))
    Path(batch.stored_path).write_bytes(payload)

    # detection pass (no plan yet — preview does that with user overrides)
    plan = await build_import_plan(session, sheets, PreviewOptions())
    batch.stats = {
        "sheets": plan["sheets"],
        "plan": plan["plan"],
        "counts": plan["counts"],
        "rows": plan["rows"][:5000],
    }
    await session.commit()
    await session.refresh(batch)
    return {
        "batch": ImportBatchOut.model_validate(batch),
        "sheets": plan["sheets"],
        "counts": plan["counts"],
    }


@router.get("", response_model=Page[ImportBatchOut])
async def list_imports(
    limit: int | None = Query(default=None, ge=1, le=20000),
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(ImportBatch).order_by(ImportBatch.id.desc())
    total = await session.scalar(
        select(func.count()).select_from(stmt.order_by(None).subquery())
    )
    rows = (
        await session.execute(stmt.limit(limit).offset(offset))
    ).scalars().all()
    for b in rows:  # don't ship the full plan in list responses
        if b.stats and "plan" in b.stats:
            b.stats = {k: v for k, v in b.stats.items() if k != "plan"}
    return Page(items=rows, total=total or 0, limit=limit, offset=offset)


@router.get("/{batch_id}")
async def get_import(batch_id: int, session: AsyncSession = Depends(get_session)):
    try:
        batch = await get_or_404(session, ImportBatch, batch_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    stats = dict(batch.stats or {})
    stats.pop("plan", None)  # plan is internal; report rows + sheets suffice
    return {"batch": ImportBatchOut.model_validate(batch), "stats": stats}


@router.post(
    "/{batch_id}/preview",
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def preview_import(
    batch_id: int,
    body: PreviewOptions,
    session: AsyncSession = Depends(get_session),
):
    """Re-run detection+planning with user site overrides / sheet skips.
    Replaces the stored plan; commit executes this one."""
    try:
        batch = await get_or_404(session, ImportBatch, batch_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    if batch.status == ImportBatchStatus.COMMITTED:
        raise HTTPException(409, "batch already committed")
    sheets = _load_sheets(batch)
    result = await build_import_plan(session, sheets, body)
    batch.stats = {
        "sheets": result["sheets"],
        "plan": result["plan"],
        "counts": result["counts"],
        "rows": result["rows"][:5000],
        "options": body.model_dump(),
    }
    await session.commit()
    return {
        "sheets": result["sheets"],
        "counts": result["counts"],
        "rows": result["rows"][:2000],
    }


@router.post(
    "/{batch_id}/commit",
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def commit_import(
    batch_id: int,
    body: CommitOptions,
    session: AsyncSession = Depends(get_session),
):
    try:
        batch = await get_or_404(session, ImportBatch, batch_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    if batch.status == ImportBatchStatus.COMMITTED:
        raise HTTPException(409, "batch already committed")
    plan = (batch.stats or {}).get("plan")
    if not plan:
        raise HTTPException(409, "run preview first — no stored plan")
    try:
        result = await commit_batch(
            session, batch, plan, partial=body.partial, actor=batch.actor or "system"
        )
    except PlanError as e:
        await session.rollback()
        # rollback() expired every ORM object — touching batch.stats here would
        # lazy-load on the async session and raise MissingGreenlet. Re-fetch.
        batch = await session.get(ImportBatch, batch_id)
        if batch is not None:
            batch.status = ImportBatchStatus.FAILED
            batch.stats = {**(batch.stats or {}), "commit_error": str(e)}
            await session.commit()
        raise HTTPException(422, str(e))
    batch.status = ImportBatchStatus.COMMITTED
    batch.committed_at = datetime.now(timezone.utc)
    batch.stats = {
        **(batch.stats or {}),
        "commit_counts": result["counts"],
        "commit_rows": result["rows"][:5000],
    }
    batch.stats.pop("plan", None)  # drop the big plan once executed
    await session.commit()
    return {"counts": result["counts"], "rows": result["rows"][:2000]}


@router.delete(
    "/{batch_id}",
    status_code=204,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def delete_import(batch_id: int, session: AsyncSession = Depends(get_session)):
    """Delete a draft/failed batch and its stored file. Committed batches are
    history and stay."""
    try:
        batch = await get_or_404(session, ImportBatch, batch_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    if batch.status == ImportBatchStatus.COMMITTED:
        raise HTTPException(409, "committed batches are kept for provenance")
    Path(batch.stored_path).unlink(missing_ok=True)
    await session.delete(batch)
    await session.commit()
