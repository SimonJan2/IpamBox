from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.asset import AssetKind


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
    import_batch_id: int | None
    created_at: datetime
