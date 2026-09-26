"""Device entity schemas — a host that may be racked and owns IPs.

Placement fields (rack_id/u_position/u_height/face/carrier_id/slot/
slot_layout) are all optional: omit them for unracked inventory, or pass
rack_id + u_position (or carrier_id + slot) to place the device directly.
"""
from datetime import datetime
from typing import Literal

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


SnmpVersion = Literal["v1", "v2c", "v3"]


class SnmpCredIn(BaseModel):
    """Write-only SNMP credential for PATCH — encrypted to snmp_cred_enc
    and never returned. v1/v2c need `community`; v3 needs `user` plus
    optional auth/priv keys (proto fields pick the algorithm family).

    Omit the field entirely to keep the stored credential; send null or
    `{}` to clear it."""

    model_config = ConfigDict(extra="forbid")

    community: str | None = Field(default=None, max_length=255)
    user: str | None = Field(default=None, max_length=64)
    auth_key: str | None = Field(default=None, max_length=255)
    priv_key: str | None = Field(default=None, max_length=255)
    auth_proto: (
        Literal["sha", "md5", "sha224", "sha256", "sha384", "sha512"] | None
    ) = None
    priv_proto: (
        Literal["aes128", "aes192", "aes256", "des", "3des"] | None
    ) = None
    # v3 only — agents that scope data behind a contextName (snmpsim does).
    context: str | None = Field(default=None, max_length=255)


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
    # SNMP enrichment (V8) — write-only credential: snmp_cred goes in as
    # plaintext JSON, is encrypted to snmp_cred_enc, and never comes back.
    snmp_enabled: bool | None = None
    snmp_version: SnmpVersion | None = None
    snmp_port: int | None = Field(default=None, ge=1, le=65535)
    snmp_cred: SnmpCredIn | None = None

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
    # SNMP enrichment (V8) — snmp_cred_enc itself never leaves the server;
    # snmp_cred_set only reports that one is stored.
    snmp_enabled: bool
    snmp_version: str | None
    snmp_port: int
    snmp_sys_name: str | None
    snmp_sys_descr: str | None
    snmp_last_ok_at: datetime | None
    snmp_last_trap_at: datetime | None
    snmp_last_error: str | None
    snmp_cred_set: bool = False
    created_at: datetime
    updated_at: datetime
    # Transients stamped by the API layer — not columns.
    display_color: str | None = None
    # Worst-of across linked IPs; None = unmonitored.
    health: IPStatus | None = None
    ip_count: int = 0
    # L1 coverage — how many ports the device has and how many are cabled.
    interface_count: int = 0
    cabled_count: int = 0
    # V8.2 — ports carrying a cable_mismatch flag right now.
    flagged_count: int = 0


class DeviceDetail(DeviceOut):
    ips: list[DeviceIpRef] = []
    asset: LinkedRef | None = None
    site: LinkedRef | None = None
    rack: LinkedRef | None = None
    carrier: LinkedRef | None = None


class SnmpTestOut(BaseModel):
    """POST /devices/{id}/snmp/test — a live sysName/sysDescr probe.
    Unreachable is data, not an error status."""

    up: bool
    sys_name: str | None = None
    sys_descr: str | None = None
    error: str | None = None


class SnmpPollOut(BaseModel):
    """POST /devices/{id}/snmp/poll — one full enrichment pass inline."""

    device_id: int
    up: bool
    sys_name: str | None = None
    sys_descr: str | None = None
    interfaces_seen: int = 0
    interfaces_created: int = 0
    interfaces_updated: int = 0
    macs_learned: int = 0
    links_applied: int = 0
    links_skipped: int = 0
    lldp_neighbors: int = 0
    # Cable validation (V8.2) — ports evaluated, open flags now, and the
    # raise/clear deltas of this pass.
    cable_checked: int = 0
    cable_flags: int = 0
    cable_flags_raised: int = 0
    cable_flags_cleared: int = 0
    cable_flags_new: list[dict] = []
    error: str | None = None
    errors: list[str] = []


class SnmpInventoryRow(BaseModel):
    """One classified observation — the workbook-importer dry-run grammar."""

    section: str  # vlans | subnets | addresses
    key: str      # 'vlan:10' | 'sub:10.0.0.0/24' | 'addr:10.0.0.5'
    action: str   # create | update | exists | conflict | skip | error
    detail: str
    ok: bool = True
    diff: dict | None = None     # field -> [stored, observed]
    ref: dict | None = None      # matched existing {kind,id,label}
    result: dict | None = None   # post-apply: the created/updated row


class SnmpInventoryIn(BaseModel):
    """Preview/apply body — the target VRF the pulled truth lands in."""

    vrf_id: int
    site_id: int | None = None


class SnmpInventoryApplyIn(SnmpInventoryIn):
    # section -> selected row keys; None applies everything applicable.
    # An absent section applies nothing from it (the section was
    # unchecked in the dialog).
    selections: dict[str, list[str]] | None = None


class SnmpInventoryOut(BaseModel):
    """inventory-preview / inventory-apply — unreachable is data."""

    device_id: int
    up: bool
    host: str | None = None
    sys_name: str | None = None
    sys_descr: str | None = None
    vrf_id: int | None = None
    site_id: int | None = None
    counts: dict[str, int] = {}
    rows: list[SnmpInventoryRow] = []
    errors: list[str] = []
    error: str | None = None
    committed: bool = False
    batch_id: int | None = None
