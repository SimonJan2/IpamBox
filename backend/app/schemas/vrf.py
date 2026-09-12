from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class VRFCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    rd: str | None = Field(default=None, max_length=64)
    description: str | None = None
    site_id: int | None = None

    @field_validator("rd")
    @classmethod
    def _rd_format(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        parts = v.split(":")
        if len(parts) != 2 or not all(p.isdigit() for p in parts):
            raise ValueError("rd must look like '65000:1'")
        return v


class VRFUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    rd: str | None = Field(default=None, max_length=64)
    description: str | None = None
    site_id: int | None = None

    @field_validator("rd")
    @classmethod
    def _rd_format(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        parts = v.split(":")
        if len(parts) != 2 or not all(p.isdigit() for p in parts):
            raise ValueError("rd must look like '65000:1'")
        return v


class VRFOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    rd: str | None
    description: str | None
    site_id: int | None
    created_at: datetime
