import ipaddress
from typing import Any

from pydantic import BaseModel, Field


class ReorderBody(BaseModel):
    """POST /{entity}/reorder payload: row ids in their new display order."""

    ids: list[int] = Field(min_length=1)


def ip_display(v: Any) -> str | None:
    """Normalize asyncpg-returned ipaddress objects / strings to display form.

    INET columns arrive as IPv4Interface/IPv6Interface (e.g. '192.168.1.5/32');
    strip the host-length netmask. CIDR columns arrive as networks; keep as-is.
    """
    if v is None:
        return None
    if isinstance(v, (ipaddress.IPv4Interface, ipaddress.IPv6Interface)):
        if v.network.prefixlen == v.max_prefixlen:
            return str(v.ip)
        return str(v)
    if isinstance(
        v,
        (
            ipaddress.IPv4Address,
            ipaddress.IPv6Address,
            ipaddress.IPv4Network,
            ipaddress.IPv6Network,
        ),
    ):
        return str(v)
    return str(v)


def to_int(v: Any) -> int:
    return int(ipaddress.ip_address(str(v)))
