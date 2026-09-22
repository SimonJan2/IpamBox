from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.common import Page, hex_color_or_none

ListColumnType = Literal["text", "ip", "date", "select", "number", "url", "owner"]


class ListColumn(BaseModel):
    """One column of a custom list. ``key`` is positional ("c0"…) and stable
    — label/type edits never touch row data, which is keyed by ``key``."""

    key: str = Field(max_length=64)
    label: str = Field(max_length=128)
    type: ListColumnType = "text"
    options: list[str] | None = None  # select only
    multi: bool | None = None  # ip only: comma-separated multi-value cells


class CustomListCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    icon: str | None = Field(default=None, max_length=64)
    columns: list[ListColumn] = Field(default_factory=list)
    key_column: str | None = Field(default=None, max_length=64)


class CustomListUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    icon: str | None = Field(default=None, max_length=64)
    columns: list[ListColumn] | None = None
    key_column: str | None = Field(default=None, max_length=64)
    sort_order: int | None = None


class CustomListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str | None
    icon: str | None
    columns: list[ListColumn] | None
    key_column: str | None
    source_sheet: str | None
    import_batch_id: int | None
    sort_order: int | None
    created_at: datetime
    row_count: int = 0


class CustomListRowCreate(BaseModel):
    data: dict[str, str | None] = Field(default_factory=dict)
    site_id: int | None = None


class CustomListRowUpdate(BaseModel):
    data: dict[str, str | None] | None = None
    site_id: int | None = None
    pinned: bool | None = None
    sort_order: int | None = None
    row_color: str | None = None

    @field_validator("row_color")
    @classmethod
    def _row_color(cls, v: str | None) -> str | None:
        return hex_color_or_none(v)


class CustomListRowOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    list_id: int
    data: dict | None
    site_id: int | None
    sort_order: int | None
    pinned: bool
    row_color: str | None
    display_color: str | None = None
    manually_edited: bool
    import_batch_id: int | None
    created_at: datetime


class ResolvedIp(BaseModel):
    """Live ip_addresses lookup for an `ip`-typed cell value."""

    id: int
    prefix_id: int
    status: str
    hostname: str | None
    last_seen: datetime | None


class CustomListRowsPage(Page[CustomListRowOut]):
    # ip -> the address-table row it resolves to (empty when none resolve)
    resolved: dict[str, ResolvedIp] = {}
