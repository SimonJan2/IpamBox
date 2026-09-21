from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.asset import AssetKind
from app.schemas.common import hex_color_or_none


class AssetCreate(BaseModel):
    kind: AssetKind = AssetKind.HARDWARE
    category: str | None = Field(default=None, max_length=64)
    vendor: str | None = Field(default=None, max_length=255)
    model: str | None = Field(default=None, max_length=255)
    purpose: str | None = Field(default=None, max_length=255)
    version: str | None = Field(default=None, max_length=128)
    eol_on: date | None = None
    support_status: str | None = Field(default=None, max_length=128)
    serial_number: str | None = Field(default=None, max_length=128)
    site_id: int | None = None
    notes: str | None = None


class AssetUpdate(BaseModel):
    kind: AssetKind | None = None
    category: str | None = Field(default=None, max_length=64)
    vendor: str | None = Field(default=None, max_length=255)
    model: str | None = Field(default=None, max_length=255)
    purpose: str | None = Field(default=None, max_length=255)
    version: str | None = Field(default=None, max_length=128)
    eol_on: date | None = None
    support_status: str | None = Field(default=None, max_length=128)
    serial_number: str | None = Field(default=None, max_length=128)
    site_id: int | None = None
    notes: str | None = None
    pinned: bool | None = None
    sort_order: int | None = None
    row_color: str | None = None

    @field_validator("row_color")
    @classmethod
    def _row_color(cls, v: str | None) -> str | None:
        return hex_color_or_none(v)


class AssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    kind: AssetKind
    category: str | None
    vendor: str | None
    model: str | None
    purpose: str | None
    version: str | None
    eol_on: date | None
    support_status: str | None
    serial_number: str | None
    site_id: int | None
    notes: str | None
    pinned: bool
    sort_order: int | None
    row_color: str | None
    display_color: str | None = None
    import_batch_id: int | None
    created_at: datetime
