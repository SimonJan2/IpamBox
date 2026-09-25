import ipaddress
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.ip_address import IPStatus
from app.models.prefix import PrefixStatus
from app.schemas.common import ip_display


class PrefixCreate(BaseModel):
    prefix: str
    vrf_id: int
    site_id: int | None = None
    vlan_id: int | None = None
    status: PrefixStatus = PrefixStatus.ACTIVE
    description: str | None = None

    @field_validator("prefix")
    @classmethod
    def _canonical(cls, v: str) -> str:
        try:
            return str(ipaddress.ip_network(v.strip(), strict=False))
        except ValueError as exc:
            raise ValueError(f"invalid CIDR: {v}") from exc


def _valid_ip(v: str) -> str:
    try:
        return str(ipaddress.ip_address(v.strip()))
    except ValueError as exc:
        raise ValueError(f"invalid IP address: {v}") from exc


class PrefixUpdate(BaseModel):
    vrf_id: int | None = None
    site_id: int | None = None
    vlan_id: int | None = None
    status: PrefixStatus | None = None
    description: str | None = None
    # Send null to clear. dns entries may live outside the prefix — resolvers
    # often do — but must be valid IPs, max four.
    gateway: str | None = None
    dns_servers: list[str] | None = Field(default=None, max_length=4)

    @field_validator("gateway")
    @classmethod
    def _gw(cls, v: str | None) -> str | None:
        return _valid_ip(v) if v is not None else None

    @field_validator("dns_servers")
    @classmethod
    def _dns(cls, v: list[str] | None) -> list[str] | None:
        return [_valid_ip(s) for s in v] if v is not None else None


class VlanRefOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vid: int
    name: str


class PrefixOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    prefix: str
    vrf_id: int
    site_id: int | None
    vlan_id: int | None
    vlan: VlanRefOut | None = None
    status: PrefixStatus
    description: str | None
    gateway: str | None
    dns_servers: list[str] | None
    created_at: datetime

    # Calculated attributes (filled by the service layer). Capacity fields
    # are null for IPv6 — a /64's count (~1.8e19) exceeds Number.MAX_SAFE_INTEGER
    # and is meaningless; the UI renders '—' while used_ips stays real.
    total_ips: int | None = 0
    usable_ips: int | None = 0
    used_ips: int = 0
    free_ips: int | None = 0
    utilization_pct: float | None = 0.0
    # Marks the network/broadcast boundaries of IPv4 prefixes (None for /31,/32,v6)
    unusable_first: bool = False
    unusable_last: bool = False

    @field_validator("prefix", "gateway", mode="before")
    @classmethod
    def _ip_str(cls, v):
        return ip_display(v)

    @field_validator("dns_servers", mode="before")
    @classmethod
    def _dns_str(cls, v):
        return [ip_display(s) for s in v] if v is not None else None


class PrefixSplitOut(BaseModel):
    mask: int
    children: list[str]
    existing: list[str]  # children that already exist in this VRF


class AllocateIPRequest(BaseModel):
    hostname: str | None = Field(default=None, max_length=255)
    mac_address: str | None = None
    notes: str | None = None
    status: IPStatus = IPStatus.RESERVED


class AvailableIPOut(BaseModel):
    id: int
    address: str
    status: str
    prefix_id: int
    vrf_id: int
