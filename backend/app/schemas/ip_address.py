import ipaddress
import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.ip_address import IPRole, IPStatus
from app.schemas.common import hex_color_or_none, ip_display

_MAC_RE = re.compile(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$")


def _norm_mac(v: str | None) -> str | None:
    if v is None or v == "":
        return None
    v = v.strip().replace("-", ":").replace(".", ":").upper()
    if not _MAC_RE.match(v):
        raise ValueError("invalid EUI-48 MAC address")
    return v


class IPAddressCreate(BaseModel):
    address: str
    prefix_id: int
    mac_address: str | None = None
    hostname: str | None = Field(default=None, max_length=255)
    vendor: str | None = Field(default=None, max_length=255)
    status: IPStatus = IPStatus.ACTIVE
    role: IPRole | None = None
    nat_inside_id: int | None = None
    device_id: int | None = None
    serial_number: str | None = Field(default=None, max_length=128)
    switch_name: str | None = Field(default=None, max_length=255)
    switch_port: str | None = Field(default=None, max_length=64)
    counter_location: str | None = Field(default=None, max_length=255)
    custom_fields: dict | None = None
    notes: str | None = None

    @field_validator("address")
    @classmethod
    def _addr(cls, v: str) -> str:
        try:
            return str(ipaddress.ip_interface(v.strip()).ip)
        except ValueError as exc:
            raise ValueError(f"invalid IP address: {v}") from exc

    @field_validator("mac_address")
    @classmethod
    def _mac(cls, v: str | None) -> str | None:
        return _norm_mac(v)


class IPAddressUpdate(BaseModel):
    mac_address: str | None = None
    hostname: str | None = Field(default=None, max_length=255)
    vendor: str | None = Field(default=None, max_length=255)
    status: IPStatus | None = None
    role: IPRole | None = None
    nat_inside_id: int | None = None
    device_id: int | None = None
    serial_number: str | None = Field(default=None, max_length=128)
    switch_name: str | None = Field(default=None, max_length=255)
    switch_port: str | None = Field(default=None, max_length=64)
    counter_location: str | None = Field(default=None, max_length=255)
    custom_fields: dict | None = None
    notes: str | None = None
    prefix_id: int | None = None
    row_color: str | None = None

    @field_validator("mac_address")
    @classmethod
    def _mac(cls, v: str | None) -> str | None:
        return _norm_mac(v)

    @field_validator("row_color")
    @classmethod
    def _row_color(cls, v: str | None) -> str | None:
        return hex_color_or_none(v)


class IPAddressOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    address: str
    address_int: int
    prefix_id: int
    vrf_id: int
    mac_address: str | None
    vendor: str | None
    hostname: str | None
    status: IPStatus
    role: IPRole | None
    nat_inside_id: int | None
    device_id: int | None
    open_ports: list[int] | None
    device_type: str | None
    missed_scans: int
    serial_number: str | None
    switch_name: str | None
    switch_port: str | None
    counter_location: str | None
    custom_fields: dict | None
    import_batch_id: int | None
    last_seen: datetime | None
    notes: str | None
    row_color: str | None
    display_color: str | None = None
    # Resolved device name — stamped by the API layer, not a column.
    device_name: str | None = None
    created_at: datetime
    updated_at: datetime

    @field_validator("address", mode="before")
    @classmethod
    def _addr_str(cls, v):
        return ip_display(v)

    @field_validator("address_int", mode="before")
    @classmethod
    def _int(cls, v):
        return int(v)


class IPAddressPage(BaseModel):
    items: list[IPAddressOut]
    total: int
    prefix: str | None = None
    usable_first: str | None = None  # network addr for v4 /32+/30-; marks grid's first cell unusable
    usable_last: str | None = None
