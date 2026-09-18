from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.import_batch import ImportBatchStatus


class ImportBatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    sha256: str
    status: ImportBatchStatus
    stats: dict | None
    actor: str | None
    created_at: datetime
    committed_at: datetime | None


class SheetPreview(BaseModel):
    """Per-sheet detection result shown in the wizard."""

    sheet: str
    family: str  # sites_master | circuits | certificates | assets | services
    # | inventory | site_sheet | empty | unknown
    rows: int
    headers: list[str] = []
    # site_sheet only: site suggested by 2nd-octet/name match
    site_id: int | None = None
    site_name: str | None = None
    # "octet" | "octet-new" | "title" | "name" | "override" | None
    matched_by: str | None = None
    warnings: list[str] = []


class PreviewOptions(BaseModel):
    """User-confirmed mapping choices applied before building the plan."""

    # sheet name -> site_id (overrides auto-matching), or a string to create
    # a new site: "__new__" names it after the sheet, any other string is
    # used as the new site's name
    site_overrides: dict[str, int | str] = Field(default_factory=dict)
    # sheet names to exclude entirely
    skip_sheets: list[str] = Field(default_factory=list)
    # create a 10.{N}.0.0/16 container prefix per numbered site
    create_containers: bool = True


class CommitOptions(BaseModel):
    # commit good rows even when others fail (default keeps all-or-nothing)
    partial: bool = False


class RowResult(BaseModel):
    sheet: str
    row: int
    action: str  # create | update | skip | conflict | error
    detail: str
