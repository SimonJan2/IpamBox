from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.common import hex_color_or_none

TAGGABLE = {"Site", "VRF", "Prefix", "IPAddress"}


class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    slug: str | None = Field(default=None, max_length=64)
    color: str = Field(default="#10b981")
    description: str | None = None

    @field_validator("color")
    @classmethod
    def _color(cls, v: str) -> str:
        return hex_color_or_none(v) or v


class TagUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=64)
    color: str | None = None
    description: str | None = None
    pinned: bool | None = None
    sort_order: int | None = None
    row_color: str | None = None

    @field_validator("color")
    @classmethod
    def _color(cls, v: str | None) -> str | None:
        return hex_color_or_none(v)

    @field_validator("row_color")
    @classmethod
    def _row_color(cls, v: str | None) -> str | None:
        return hex_color_or_none(v)


class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    color: str
    description: str | None
    pinned: bool
    sort_order: int | None
    row_color: str | None
    display_color: str | None = None
    created_at: datetime


class AssignBody(BaseModel):
    object_type: str
    object_id: int

    @field_validator("object_type")
    @classmethod
    def _type(cls, v: str) -> str:
        if v not in TAGGABLE:
            raise ValueError(f"object_type must be one of {sorted(TAGGABLE)}")
        return v


class TagAssignmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tag_id: int
    object_type: str
    object_id: int
