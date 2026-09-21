from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.common import hex_color_or_none


class SiteCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str | None = Field(default=None, max_length=255)
    description: str | None = None
    code: str | None = Field(default=None, max_length=16)
    site_number: int | None = None
    size: str | None = Field(default=None, max_length=32)
    is_active: bool = True
    contact: str | None = None
    address: str | None = None


class SiteUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    slug: str | None = Field(default=None, max_length=255)
    description: str | None = None
    code: str | None = Field(default=None, max_length=16)
    site_number: int | None = None
    size: str | None = Field(default=None, max_length=32)
    is_active: bool | None = None
    contact: str | None = None
    address: str | None = None
    pinned: bool | None = None
    sort_order: int | None = None
    row_color: str | None = None

    @field_validator("row_color")
    @classmethod
    def _row_color(cls, v: str | None) -> str | None:
        return hex_color_or_none(v)


class SiteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str | None
    code: str | None
    site_number: int | None
    size: str | None
    is_active: bool
    contact: str | None
    address: str | None
    pinned: bool
    sort_order: int | None
    row_color: str | None
    display_color: str | None = None
    created_at: datetime
