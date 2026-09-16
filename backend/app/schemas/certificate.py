from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class CertificateCreate(BaseModel):
    platform: str | None = Field(default=None, max_length=64)
    target: str | None = Field(default=None, max_length=255)
    server_name: str | None = Field(default=None, max_length=255)
    cert_name: str | None = Field(default=None, max_length=255)
    expires_on: date | None = None
    serial_raw: str | None = Field(default=None, max_length=64)
    notes: str | None = None


class CertificateUpdate(BaseModel):
    platform: str | None = Field(default=None, max_length=64)
    target: str | None = Field(default=None, max_length=255)
    server_name: str | None = Field(default=None, max_length=255)
    cert_name: str | None = Field(default=None, max_length=255)
    expires_on: date | None = None
    serial_raw: str | None = Field(default=None, max_length=64)
    notes: str | None = None


class CertificateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    platform: str | None
    target: str | None
    server_name: str | None
    cert_name: str | None
    expires_on: date | None
    serial_raw: str | None
    notes: str | None
    import_batch_id: int | None
    created_at: datetime
