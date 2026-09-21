from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.vlan import VLANStatus
from app.schemas.common import hex_color_or_none


class VLANGroupCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class VLANGroupUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None


class VLANGroupOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    vlan_count: int = 0
    created_at: datetime


class VLANCreate(BaseModel):
    vid: int = Field(ge=1, le=4094)
    name: str = Field(min_length=1, max_length=64)
    group_id: int | None = None
    site_id: int | None = None
    status: VLANStatus = VLANStatus.ACTIVE
    description: str | None = None


class VLANUpdate(BaseModel):
    vid: int | None = Field(default=None, ge=1, le=4094)
    name: str | None = Field(default=None, min_length=1, max_length=64)
    group_id: int | None = None
    site_id: int | None = None
    status: VLANStatus | None = None
    description: str | None = None
    pinned: bool | None = None
    sort_order: int | None = None
    row_color: str | None = None

    @field_validator("row_color")
    @classmethod
    def _row_color(cls, v: str | None) -> str | None:
        return hex_color_or_none(v)


class VLANOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vid: int
    name: str
    group_id: int | None
    site_id: int | None
    status: VLANStatus
    description: str | None
    pinned: bool
    sort_order: int | None
    row_color: str | None
    display_color: str | None = None
    created_at: datetime
