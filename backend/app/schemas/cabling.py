"""Cabling schemas — interfaces, cables, trace, generate, match report.

`pair_interface_id` links a patch position's front and back ports (same
device). `connected_ip_id` is the host-side NIC→IP binding; the IP→switch
link lives on ip_addresses.connected_interface_id instead.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.cabling import CableKind, InterfaceKind
from app.schemas.ip_address import _norm_mac


def _strip_name(v: str) -> str:
    v = v.strip()
    if not v:
        raise ValueError("name must not be empty")
    return v


class DeviceInterfaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    kind: InterfaceKind = InterfaceKind.RJ45
    speed_mbps: int | None = Field(default=None, ge=1, le=3200000)
    mac_address: str | None = None
    position: int | None = Field(default=None, ge=0)
    connected_ip_id: int | None = None
    pair_interface_id: int | None = None

    @field_validator("name")
    @classmethod
    def _name(cls, v: str) -> str:
        return _strip_name(v)

    @field_validator("mac_address")
    @classmethod
    def _mac(cls, v: str | None) -> str | None:
        return _norm_mac(v)


class DeviceInterfaceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=64)
    kind: InterfaceKind | None = None
    speed_mbps: int | None = Field(default=None, ge=1, le=3200000)
    mac_address: str | None = None
    position: int | None = Field(default=None, ge=0)
    connected_ip_id: int | None = None
    pair_interface_id: int | None = None

    @field_validator("name")
    @classmethod
    def _name(cls, v: str | None) -> str | None:
        return _strip_name(v) if v is not None else v

    @field_validator("mac_address")
    @classmethod
    def _mac(cls, v: str | None) -> str | None:
        return _norm_mac(v)


class InterfaceGenerateBody(BaseModel):
    """Bulk port factory: prefix+index names (Gi1/0/1..48) in one call.

    `pair_prefix` additionally creates a same-indexed second row per port,
    paired 1:1 via pair_interface_id — a patch panel's front+back in one
    click (e.g. prefix="p", pair_prefix="b" → p1..24 + b1..24, p_i↔b_i).
    """

    kind: InterfaceKind = InterfaceKind.RJ45
    prefix: str = Field(min_length=1, max_length=48)
    count: int = Field(ge=1, le=256)
    start_index: int = Field(default=1, ge=0)
    speed_mbps: int | None = Field(default=None, ge=1, le=3200000)
    pair_prefix: str | None = Field(default=None, max_length=48)

    @field_validator("prefix", "pair_prefix")
    @classmethod
    def _prefix(cls, v: str | None) -> str | None:
        return _strip_name(v) if v is not None else v


class CableCreate(BaseModel):
    a_interface_id: int
    b_interface_id: int
    kind: CableKind = CableKind.OTHER
    color: str | None = Field(default=None, max_length=32)
    label: str | None = Field(default=None, max_length=255)
    length_m: float | None = Field(default=None, ge=0, le=9999.9)
    notes: str | None = None


class CableUpdate(BaseModel):
    a_interface_id: int | None = None
    b_interface_id: int | None = None
    kind: CableKind | None = None
    color: str | None = Field(default=None, max_length=32)
    label: str | None = Field(default=None, max_length=255)
    length_m: float | None = Field(default=None, ge=0, le=9999.9)
    notes: str | None = None


class InterfacePeerOut(BaseModel):
    """The far end of an interface's cable — enough to label and link it."""

    cable_id: int
    cable_kind: CableKind
    cable_label: str | None
    interface_id: int
    interface_name: str
    device_id: int
    device_name: str


class ConnectedIpRef(BaseModel):
    """Resolved connected_ip_id — the IP this port serves."""

    id: int
    label: str
    prefix_id: int


class DeviceInterfaceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    name: str
    kind: InterfaceKind
    speed_mbps: int | None
    mac_address: str | None
    position: int
    connected_ip_id: int | None
    pair_interface_id: int | None
    # SNMP-observed state (V8) — null on ports the poller never reported.
    if_index: int | None
    oper_status: str | None
    admin_status: str | None
    snmp_seen_at: datetime | None
    source: str
    created_at: datetime
    updated_at: datetime
    # Resolved by the API layer — not columns.
    peer: InterfacePeerOut | None = None
    connected_ip: ConnectedIpRef | None = None


class CableEndOut(BaseModel):
    """One cable termination resolved for display."""

    interface_id: int
    interface_name: str
    device_id: int
    device_name: str


class CableOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    a_interface_id: int
    b_interface_id: int
    kind: CableKind
    color: str | None
    label: str | None
    length_m: float | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    a: CableEndOut | None = None
    b: CableEndOut | None = None


class CableTraceHop(BaseModel):
    """One step of an L1 path. cable_id/kind are null on the start hop and
    on patch-panel pair hops (the front↔back pass-through isn't a cable)."""

    device_id: int
    device_name: str
    interface_id: int
    interface_name: str
    cable_id: int | None = None
    cable_kind: CableKind | None = None
    cable_label: str | None = None


class MatchFreeTextOut(BaseModel):
    """Report of the legacy switch_name/switch_port → connected_interface_id
    matcher. `*_ids` carry the address ids behind each count for review."""

    matched: int
    ambiguous: int
    unmatched: int
    matched_ids: list[int] = []
    ambiguous_ids: list[int] = []
    unmatched_ids: list[int] = []
