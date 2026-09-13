import ipaddress
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.ip_range import IPRangeRole
from app.schemas.common import ip_display


class IPRangeCreate(BaseModel):
    prefix_id: int
    start_address: str
    end_address: str
    role: IPRangeRole = IPRangeRole.DHCP
    description: str | None = None

    @field_validator("start_address", "end_address")
    @classmethod
    def _addr(cls, v: str) -> str:
        try:
            return str(ipaddress.ip_address(v.strip()))
        except ValueError as exc:
            raise ValueError(f"invalid IP address: {v}") from exc

    @model_validator(mode="after")
    def _ordered(self):
        if ipaddress.ip_address(self.start_address) > ipaddress.ip_address(
            self.end_address
        ):
            raise ValueError("start_address must be <= end_address")
        return self


class IPRangeUpdate(BaseModel):
    role: IPRangeRole | None = None
    description: str | None = None


class IPRangeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    prefix_id: int
    vrf_id: int
    start_address: str
    start_int: int
    end_address: str
    end_int: int
    role: IPRangeRole
    description: str | None
    created_at: datetime

    @field_validator("start_address", "end_address", mode="before")
    @classmethod
    def _addr_str(cls, v):
        return ip_display(v)

    @field_validator("start_int", "end_int", mode="before")
    @classmethod
    def _int(cls, v):
        return int(v)
