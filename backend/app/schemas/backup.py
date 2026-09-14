from pydantic import BaseModel


class BackupPreviewOut(BaseModel):
    format: str
    format_version: int
    app_version: str | None
    alembic_revision: str | None
    created_at: str | None
    tables: dict[str, int]
    warnings: list[str]
    includes_users: bool


class RestoreReport(BaseModel):
    restored: dict[str, int]
    warnings: list[str]
    backup_created_at: str | None


class BackupFileInfo(BaseModel):
    name: str
    size: int
    created_at: str


class BackupFilesOut(BaseModel):
    files: list[BackupFileInfo]
    interval_minutes: int
    keep: int
