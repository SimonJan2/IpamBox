from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.common import hex_color_or_none


class ServiceCreate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    beneficiary: str | None = Field(default=None, max_length=255)
    site_id: int | None = None
    site_code: str | None = Field(default=None, max_length=16)
    doc_path: str | None = None
    test_info: str | None = None
    notes: str | None = None


class ServiceUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    beneficiary: str | None = Field(default=None, max_length=255)
    site_id: int | None = None
    site_code: str | None = Field(default=None, max_length=16)
    doc_path: str | None = None
    test_info: str | None = None
    notes: str | None = None
    pinned: bool | None = None
    sort_order: int | None = None
    row_color: str | None = None

    @field_validator("row_color")
    @classmethod
    def _row_color(cls, v: str | None) -> str | None:
        return hex_color_or_none(v)


class ServiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str | None
    beneficiary: str | None
    site_id: int | None
    site_code: str | None
    doc_path: str | None
    test_info: str | None
    notes: str | None
    pinned: bool
    sort_order: int | None
    row_color: str | None
    display_color: str | None = None
    import_batch_id: int | None
    created_at: datetime
