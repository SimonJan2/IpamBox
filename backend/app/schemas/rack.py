from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.rack import RackFace
from app.schemas.common import hex_color_or_none

_WIDTHS = (10, 19)


def _rail_width(v: int | None) -> int | None:
    if v is not None and v not in _WIDTHS:
        raise ValueError("width must be 10 or 19 (rail width in inches)")
    return v


class RackCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    site_id: int | None = None
    description: str | None = None
    room: str | None = Field(default=None, max_length=255)
    height_u: int = Field(default=42, ge=1, le=100)
    width: int = 19
    notes: str | None = None

    @field_validator("width")
    @classmethod
    def _width(cls, v: int) -> int:
        return _rail_width(v)


class RackUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    site_id: int | None = None
    description: str | None = None
    room: str | None = Field(default=None, max_length=255)
    height_u: int | None = Field(default=None, ge=1, le=100)
    width: int | None = None
    notes: str | None = None
    pinned: bool | None = None
    sort_order: int | None = None
    row_color: str | None = None

    @field_validator("width")
    @classmethod
    def _width(cls, v: int | None) -> int | None:
        return _rail_width(v)

    @field_validator("row_color")
    @classmethod
    def _row_color(cls, v: str | None) -> str | None:
        return hex_color_or_none(v)


class RackOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    site_id: int | None
    name: str
    description: str | None
    room: str | None
    height_u: int
    width: int
    notes: str | None
    pinned: bool
    sort_order: int | None
    row_color: str | None
    display_color: str | None = None
    created_at: datetime
    # Aggregates populated by the API layer — not columns.
    device_count: int = 0
    used_u: int = 0


class RackDeviceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    device_type: str | None = Field(default=None, max_length=255)
    u_position: int = Field(ge=1)
    u_height: int = Field(default=1, ge=1, le=100)
    face: RackFace = RackFace.FRONT
    colour: str | None = Field(default=None, max_length=7)
    category: str | None = Field(default=None, max_length=64)
    manufacturer: str | None = Field(default=None, max_length=255)
    model: str | None = Field(default=None, max_length=255)
    asset_id: int | None = None
    ip_address_id: int | None = None
    source: Literal["manual", "rackula"] = "manual"
    notes: str | None = None

    @field_validator("colour")
    @classmethod
    def _colour(cls, v: str | None) -> str | None:
        return hex_color_or_none(v)


class RackDeviceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    device_type: str | None = Field(default=None, max_length=255)
    u_position: int | None = Field(default=None, ge=1)
    u_height: int | None = Field(default=None, ge=1, le=100)
    face: RackFace | None = None
    colour: str | None = Field(default=None, max_length=7)
    category: str | None = Field(default=None, max_length=64)
    manufacturer: str | None = Field(default=None, max_length=255)
    model: str | None = Field(default=None, max_length=255)
    asset_id: int | None = None
    ip_address_id: int | None = None
    notes: str | None = None

    @field_validator("colour")
    @classmethod
    def _colour(cls, v: str | None) -> str | None:
        return hex_color_or_none(v)


class LinkedRef(BaseModel):
    """Resolved FK summary for the detail UI: id for the link, label to show."""

    id: int
    label: str


class IpRef(LinkedRef):
    prefix_id: int


class RackDeviceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rack_id: int
    name: str
    device_type: str | None
    u_position: int
    u_height: int
    face: RackFace
    colour: str | None
    category: str | None
    manufacturer: str | None
    model: str | None
    asset_id: int | None
    ip_address_id: int | None
    source: str
    notes: str | None
    created_at: datetime
    updated_at: datetime
    asset: LinkedRef | None = None
    ip: IpRef | None = None


class RackDetail(RackOut):
    devices: list[RackDeviceOut] = []


class RackDeviceImport(BaseModel):
    mode: Literal["merge", "replace"] = "merge"
    devices: list[RackDeviceCreate] = Field(default_factory=list, max_length=500)


class SkippedDevice(BaseModel):
    name: str | None
    u_position: int | None
    reason: str


class RackImportResult(BaseModel):
    created: int
    skipped: list[SkippedDevice] = []
