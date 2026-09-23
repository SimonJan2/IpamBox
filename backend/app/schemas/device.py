"""Device entity schemas — a host that may be racked and owns IPs.

Placement fields (rack_id/u_position/u_height/face/carrier_id/slot/
slot_layout) are all optional: omit them for unracked inventory, or pass
rack_id + u_position (or carrier_id + slot) to place the device directly.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.ip_address import IPStatus
from app.models.rack import RackFace
from app.schemas.common import hex_color_or_none
from app.schemas.ip_address import _norm_mac
from app.schemas.rack import LinkedRef, SlotLayout


class DeviceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    device_type: str | None = Field(default=None, max_length=255)
    serial_number: str | None = Field(default=None, max_length=128)
    site_id: int | None = None
    asset_id: int | None = None
    mac_address: str | None = None
    colour: str | None = Field(default=None, max_length=7)
    category: str | None = Field(default=None, max_length=64)
    manufacturer: str | None = Field(default=None, max_length=255)
    model: str | None = Field(default=None, max_length=255)
    watts: int | None = Field(default=None, ge=0)
    weight_kg: float | None = Field(default=None, ge=0, le=99999)
    custom_fields: dict | None = None
    notes: str | None = None
    # Placement — NULL = unracked inventory device.
    rack_id: int | None = None
    u_position: int | None = Field(default=None, ge=1)
    u_height: int | None = Field(default=None, ge=1, le=100)
    face: RackFace | None = None
    carrier_id: int | None = None
    slot: int | None = Field(default=None, ge=0)
    slot_layout: SlotLayout | None = None

    @field_validator("colour")
    @classmethod
    def _colour(cls, v: str | None) -> str | None:
        return hex_color_or_none(v)

    @field_validator("mac_address")
    @classmethod
    def _mac(cls, v: str | None) -> str | None:
        return _norm_mac(v)


class DeviceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    device_type: str | None = Field(default=None, max_length=255)
    serial_number: str | None = Field(default=None, max_length=128)
    site_id: int | None = None
    asset_id: int | None = None
    mac_address: str | None = None
    colour: str | None = Field(default=None, max_length=7)
    category: str | None = Field(default=None, max_length=64)
    manufacturer: str | None = Field(default=None, max_length=255)
    model: str | None = Field(default=None, max_length=255)
    watts: int | None = Field(default=None, ge=0)
    weight_kg: float | None = Field(default=None, ge=0, le=99999)
    custom_fields: dict | None = None
    notes: str | None = None
    # rack_id=null unracks the device; rack_id=X re-homes it (validated
    # against the target rack's occupancy like the rack route).
    rack_id: int | None = None
    u_position: int | None = Field(default=None, ge=1)
    u_height: int | None = Field(default=None, ge=1, le=100)
    face: RackFace | None = None
    carrier_id: int | None = None
    slot: int | None = Field(default=None, ge=0)
    slot_layout: SlotLayout | None = None
    pinned: bool | None = None
    sort_order: int | None = None
    row_color: str | None = None

    @field_validator("colour", "row_color")
    @classmethod
    def _colour(cls, v: str | None) -> str | None:
        return hex_color_or_none(v)

    @field_validator("mac_address")
    @classmethod
    def _mac(cls, v: str | None) -> str | None:
        return _norm_mac(v)


class DeviceIpRef(LinkedRef):
    """One of the device's IPs: link id/label + scan status for the table."""

    address: str
    hostname: str | None
    status: IPStatus
    last_seen: datetime | None
    prefix_id: int


class DeviceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    device_type: str | None
    serial_number: str | None
    site_id: int | None
    asset_id: int | None
    mac_address: str | None
    # Placement — NULLs mean unracked.
    rack_id: int | None
    u_position: int | None
    u_height: int | None
    face: RackFace | None
    carrier_id: int | None
    slot: int | None
    slot_layout: str | None
    colour: str | None
    category: str | None
    manufacturer: str | None
    model: str | None
    watts: int | None
    weight_kg: float | None
    custom_fields: dict | None
    source: str
    notes: str | None
    row_color: str | None
    sort_order: int | None
    pinned: bool
    import_batch_id: int | None
    created_at: datetime
    updated_at: datetime
    # Transients stamped by the API layer — not columns.
    display_color: str | None = None
    # Worst-of across linked IPs; None = unmonitored.
    health: IPStatus | None = None
    ip_count: int = 0


class DeviceDetail(DeviceOut):
    ips: list[DeviceIpRef] = []
    asset: LinkedRef | None = None
    site: LinkedRef | None = None
    rack: LinkedRef | None = None
    carrier: LinkedRef | None = None
