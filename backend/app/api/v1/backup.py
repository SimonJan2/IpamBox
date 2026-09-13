from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_session
from app.core.deps import require_auth
from app.models.user import User
from app.schemas.backup import (
    BackupFileInfo,
    BackupFilesOut,
    BackupPreviewOut,
    RestoreReport,
)
from app.services import backup as svc
from app.services.backup import BackupError, backup_filename

router = APIRouter(prefix="/backup", tags=["backup"])
settings = get_settings()

MAX_BACKUP_BYTES = 256 * 1024 * 1024  # sanity cap on uploads


@router.get("")
async def download_backup(session: AsyncSession = Depends(get_session)):
    """Download a full snapshot (every table except users) as .json.gz."""
    payload = await svc.build_backup(session)
    return Response(
        payload,
        media_type="application/gzip",
        headers={
            "Content-Disposition": f'attachment; filename="{backup_filename()}"'
        },
    )


@router.get("/files", response_model=BackupFilesOut)
async def list_scheduled_backups():
    """Scheduled snapshot files written by the worker into BACKUP_DIR."""
    return BackupFilesOut(
        files=[BackupFileInfo(**f) for f in svc.list_backup_files()],
        interval_minutes=settings.backup_interval_minutes,
        keep=settings.backup_keep,
    )


@router.get("/files/{name}")
async def download_scheduled_backup(name: str):
    payload = svc.read_backup_file(name)
    if payload is None:
        raise HTTPException(404, "backup file not found")
    return Response(
        payload,
        media_type="application/gzip",
        headers={"Content-Disposition": f'attachment; filename="{name}"'},
    )


@router.post("/restore")
async def restore(
    request: Request,
    dry_run: bool = Query(default=False),
    name: str = Query(default="backup.json.gz"),
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(require_auth),
):
    """Restore a backup file (raw .json.gz body). Wipes every data table
    (users are kept) and re-inserts rows with their original IDs — all in
    one transaction. ?dry_run=1 validates and previews without writing."""
    payload = await request.body()
    if len(payload) > MAX_BACKUP_BYTES:
        raise HTTPException(413, "backup file too large")
    try:
        preview = svc.inspect_backup(payload)
    except BackupError as e:
        raise HTTPException(422, str(e))

    if dry_run:
        return BackupPreviewOut(
            format=preview.format,
            format_version=preview.format_version,
            app_version=preview.app_version,
            alembic_revision=preview.alembic_revision,
            created_at=preview.created_at,
            tables=preview.tables,
            warnings=preview.warnings,
        )

    try:
        report = await svc.restore_backup(
            session,
            preview,
            actor=user.username if user else "system",
            filename=name,
        )
    except BackupError as e:
        raise HTTPException(422, str(e))
    except IntegrityError as e:
        raise HTTPException(
            422, f"backup data violates a constraint — nothing was restored: {e.orig}"
        )
    return RestoreReport(**report)
