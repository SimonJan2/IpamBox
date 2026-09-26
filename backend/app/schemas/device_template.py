"""Device template schemas (V10.1).

A template's ``interfaces`` list is the stampable port layout:
``{name, kind, speed_mbps?, position?, pair?}``. ``kind`` must be a real
``interface_kind`` value — pydantic enforces it on every write, so a bad
kind is a 422 before the JSONB blob ever reaches the DB. ``pair`` names a
sibling entry (patch-panel front↔back); pairs must be declared mutually
so the stamped link is honest in both directions. ``power_ports`` entries
(``{name}``) stamp as ``kind=power`` ports.
"""
from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.models.cabling import InterfaceKind
from app.models.rack import RackFace
from app.schemas.cabling import _strip_name
from app.schemas.common import hex_color_or_none
from app.schemas.device import DeviceDetail
from app.schemas.ip_address import _norm_mac
from app.schemas.rack import SlotLayout

TemplateSource = Literal["builtin", "manual", "import"]
TemplateFace = Literal["front", "rear", "both"]


class TemplateInterface(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    kind: InterfaceKind = InterfaceKind.RJ45
    speed_mbps: int | None = Field(default=None, ge=1, le=3200000)
    # Template-relative stamp order — null sorts by array order on apply.
    position: int | None = Field(default=None, ge=0)
    # Name of a sibling entry this port pairs with — must be mutual.
    pair: str | None = Field(default=None, max_length=64)

    @field_validator("name")
    @classmethod
    def _name(cls, v: str) -> str:
        return _strip_name(v)

    @field_validator("pair")
    @classmethod
    def _pair(cls, v: str | None) -> str | None:
        return _strip_name(v) if v is not None else v


class TemplatePowerPort(BaseModel):
    name: str = Field(min_length=1, max_length=64)

    @field_validator("name")
    @classmethod
    def _name(cls, v: str) -> str:
        return _strip_name(v)


def _validate_layout(
    interfaces: list[TemplateInterface],
    power_ports: list[TemplatePowerPort] | None,
) -> None:
    """Cross-field layout rules shared by Create/Update: names unique,
    pair refs resolvable and declared on both ends, power names clear of
    the interface set (they stamp into the same per-device namespace)."""
    names = [i.name for i in interfaces]
    dup = next((n for n in names if names.count(n) > 1), None)
    if dup is not None:
        raise ValueError(f"duplicate interface name '{dup}'")
    known = set(names)
    for i in interfaces:
        if i.pair is None:
            continue
        if i.pair == i.name:
            raise ValueError(f"interface '{i.name}' cannot be its own pair")
        if i.pair not in known:
            raise ValueError(
                f"interface '{i.name}' pairs with unknown port '{i.pair}'"
            )
        other = interfaces[names.index(i.pair)]
        if other.pair != i.name:
            raise ValueError(
                f"pair '{i.name}'↔'{i.pair}' must be declared on both ports"
            )
    if power_ports:
        pnames = [p.name for p in power_ports]
        dup = next((n for n in pnames if pnames.count(n) > 1), None)
        if dup is not None:
            raise ValueError(f"duplicate power port name '{dup}'")
        clash = next((n for n in pnames if n in known), None)
        if clash is not None:
            raise ValueError(
                f"power port '{clash}' collides with an interface name"
            )


class DeviceTemplateCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    manufacturer: str | None = Field(default=None, max_length=255)
    model: str | None = Field(default=None, max_length=255)
    device_type: str | None = Field(default=None, max_length=255)
    u_height: int = Field(default=1, ge=1, le=100)
    face_default: TemplateFace = "front"
    colour: str | None = Field(default=None, max_length=7)
    category: str | None = Field(default=None, max_length=64)
    watts: int | None = Field(default=None, ge=0)
    weight_kg: float | None = Field(default=None, ge=0, le=99999)
    interfaces: list[TemplateInterface] = []
    power_ports: list[TemplatePowerPort] | None = None
    source: TemplateSource = "manual"
    notes: str | None = None

    @field_validator("colour")
    @classmethod
    def _colour(cls, v: str | None) -> str | None:
        return hex_color_or_none(v)

    @model_validator(mode="after")
    def _layout(self):
        _validate_layout(self.interfaces, self.power_ports)
        return self


class DeviceTemplateUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    manufacturer: str | None = Field(default=None, max_length=255)
    model: str | None = Field(default=None, max_length=255)
    device_type: str | None = Field(default=None, max_length=255)
    u_height: int | None = Field(default=None, ge=1, le=100)
    face_default: TemplateFace | None = None
    colour: str | None = Field(default=None, max_length=7)
    category: str | None = Field(default=None, max_length=64)
    watts: int | None = Field(default=None, ge=0)
    weight_kg: float | None = Field(default=None, ge=0, le=99999)
    interfaces: list[TemplateInterface] | None = None
    power_ports: list[TemplatePowerPort] | None = None
    source: TemplateSource | None = None
    notes: str | None = None

    @field_validator("colour")
    @classmethod
    def _colour(cls, v: str | None) -> str | None:
        return hex_color_or_none(v)

    @model_validator(mode="after")
    def _layout(self):
        if self.interfaces is not None:
            _validate_layout(self.interfaces, self.power_ports)
        return self


class DeviceTemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    manufacturer: str | None
    model: str | None
    device_type: str | None
    u_height: int
    face_default: str
    colour: str | None
    category: str | None
    watts: int | None
    weight_kg: float | None
    interfaces: list[TemplateInterface]
    power_ports: list[TemplatePowerPort] | None
    source: str
    notes: str | None
    created_at: datetime
    updated_at: datetime


class TemplateApplyIn(BaseModel):
    template_id: int
    mode: Literal["merge", "replace"] = "merge"


class TemplateApplyOut(BaseModel):
    created: int
    skipped: list[str] = []
    blocked: list[str] = []


class TemplateInstantiateIn(BaseModel):
    """"Create the device too" — template fields prefill, every payload
    field overrides. Placement follows the POST /devices rules: rack_id +
    u_position, carrier_id + slot, or neither (unracked inventory)."""

    name: str = Field(min_length=1, max_length=255)
    site_id: int | None = None
    asset_id: int | None = None
    ip_address_id: int | None = None
    serial_number: str | None = Field(default=None, max_length=128)
    mac_address: str | None = None
    # Placement — rack_id+u_position, carrier_id+slot, or unracked.
    rack_id: int | None = None
    u_position: int | None = Field(default=None, ge=1)
    carrier_id: int | None = None
    slot: int | None = Field(default=None, ge=0)
    slot_layout: SlotLayout | None = None
    # Template-prefilled fields — null/absent inherits the template value.
    device_type: str | None = Field(default=None, max_length=255)
    manufacturer: str | None = Field(default=None, max_length=255)
    model: str | None = Field(default=None, max_length=255)
    u_height: int | None = Field(default=None, ge=1, le=100)
    face: RackFace | None = None
    colour: str | None = Field(default=None, max_length=7)
    category: str | None = Field(default=None, max_length=64)
    watts: int | None = Field(default=None, ge=0)
    weight_kg: float | None = Field(default=None, ge=0, le=99999)
    notes: str | None = None

    @field_validator("colour")
    @classmethod
    def _colour(cls, v: str | None) -> str | None:
        return hex_color_or_none(v)

    @field_validator("mac_address")
    @classmethod
    def _mac(cls, v: str | None) -> str | None:
        return _norm_mac(v)


class TemplateInstantiateOut(BaseModel):
    device: DeviceDetail
    created: int
    skipped: list[str] = []
    blocked: list[str] = []
