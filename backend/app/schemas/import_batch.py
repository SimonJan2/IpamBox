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
    # set when the sheet is targeted as a custom list (list_sheets option)
    list_name: str | None = None
    # inferred column defs for list-targeted sheets — [{key,label,type,…}]
    list_columns: list[dict] | None = None


class ListTarget(BaseModel):
    """Import a sheet as a custom list (user-selected or suggested)."""

    # display name for the list — defaults to the sheet title when empty
    name: str | None = None
    # merge-identity column: a column key ("c0") or header label; None = auto
    key_column: str | None = None
    # also run the sheet's detected family parser (IPs still land in the
    # IPAM) — default on; turn off to keep the sheet only as a list
    also_ipam: bool = True


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
    # sheet name -> custom-list target
    list_sheets: dict[str, ListTarget] = Field(default_factory=dict)


class CommitOptions(BaseModel):
    # commit good rows even when others fail (default keeps all-or-nothing)
    partial: bool = False


class RowResult(BaseModel):
    sheet: str
    row: int
    action: str  # create | update | skip | conflict | error
    detail: str
