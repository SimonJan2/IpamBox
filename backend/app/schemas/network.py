"""POST /networks — the "add network" wizard payload (V6.1).

One submit creates (or reuses) the VLAN, the prefix, the protected technical
addresses, and an optional DHCP range in a single transaction — the same
all-or-nothing style the importers use.
"""
import ipaddress

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.prefix import PrefixStatus


def _ip(v: str) -> str:
    try:
        return str(ipaddress.ip_address(v.strip()))
    except ValueError as exc:
        raise ValueError(f"invalid IP address: {v}") from exc


class NetworkVlanNew(BaseModel):
    vid: int = Field(ge=1, le=4094)
    name: str = Field(min_length=1, max_length=64)
    group_id: int | None = None


class NetworkPrefix(BaseModel):
    cidr: str
    vrf_id: int
    status: PrefixStatus = PrefixStatus.ACTIVE
    description: str | None = None

    @field_validator("cidr")
    @classmethod
    def _canonical(cls, v: str) -> str:
        try:
            return str(ipaddress.ip_network(v.strip(), strict=False))
        except ValueError as exc:
            raise ValueError(f"invalid CIDR: {v}") from exc


class NetworkDhcpRange(BaseModel):
    start: str
    end: str
    description: str | None = None

    @field_validator("start", "end")
    @classmethod
    def _addr(cls, v: str) -> str:
        return _ip(v)

    @model_validator(mode="after")
    def _ordered(self):
        if ipaddress.ip_address(self.start) > ipaddress.ip_address(self.end):
            raise ValueError("start must be <= end")
        return self


class NetworkCreate(BaseModel):
    site_id: int | None = None
    # Either an existing VLAN id or a new-VLAN spec — exactly one.
    vlan_id: int | None = None
    vlan: NetworkVlanNew | None = None
    prefix: NetworkPrefix
    gateway: str | None = None
    # Resolvers may live outside the prefix — any valid IP, max four.
    dns_servers: list[str] | None = Field(default=None, max_length=4)
    dhcp_range: NetworkDhcpRange | None = None

    @field_validator("gateway")
    @classmethod
    def _gw(cls, v: str | None) -> str | None:
        return _ip(v) if v is not None else None

    @field_validator("dns_servers")
    @classmethod
    def _dns(cls, v: list[str] | None) -> list[str] | None:
        return [_ip(s) for s in v] if v is not None else None

    @model_validator(mode="after")
    def _one_vlan_form(self):
        if self.vlan_id is None and self.vlan is None:
            raise ValueError("vlan_id or vlan is required")
        if self.vlan_id is not None and self.vlan is not None:
            raise ValueError("pass vlan_id or vlan, not both")
        return self


class NetworkOut(BaseModel):
    vlan_id: int
    prefix_id: int
    ip_range_id: int | None
    # Reserved technical-address rows created for gateway/DNS.
    address_ids: list[int]
