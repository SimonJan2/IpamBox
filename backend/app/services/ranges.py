"""Subnet semantics — technical addresses and pool membership (V6.1).

Two jobs:

- ``sync_technical_addresses`` mirrors ``prefix.gateway`` / ``prefix.dns_servers``
  into marker-tagged, reserved ``ip_addresses`` rows so the technical addresses
  are documented, glyph-able on the grid, and unreachable by the allocator.
  Rows we created are managed; a row anyone touched is theirs — never
  clobbered, never deleted.
- ``apply_pool_membership`` stamps ``ip_range_id`` when an address lands
  inside an ``ip_ranges`` row of the same prefix, and rejects active/reserved
  statics inside dhcp/pool ranges unless the caller passes ``force`` (the
  override leaves an auditable ``custom_fields.pool_override`` marker).
"""
import ipaddress
from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ip_address import IPAddress, IPStatus
from app.models.ip_range import IPRange, IPRangeRole
from app.models.prefix import Prefix
from app.services import prefix_math
from app.services.ipam import ConflictError

TECHNICAL_HOSTNAME = {"gateway": "gateway", "dns": "resolver"}
TECHNICAL_NOTES = {
    "gateway": "default gateway (managed)",
    "dns": "DNS resolver (managed)",
}
_STATICS_BLOCKED = (IPStatus.ACTIVE, IPStatus.RESERVED)
_RANGES_BLOCK = (IPRangeRole.DHCP, IPRangeRole.POOL)


def _technical_kind(row: IPAddress) -> str | None:
    kind = (row.custom_fields or {}).get("technical")
    return kind if kind in TECHNICAL_HOSTNAME else None


def _pristine_technical(row: IPAddress) -> bool:
    """True when the row is exactly what sync wrote — marker present and no
    field touched since. Anything else is user data: hands off."""
    kind = _technical_kind(row)
    if kind is None:
        return False
    return (
        row.status == IPStatus.RESERVED
        and row.hostname == TECHNICAL_HOSTNAME[kind]
        and row.notes == TECHNICAL_NOTES[kind]
        and row.mac_address is None
        and row.vendor is None
        and row.device_id is None
        and row.nat_inside_id is None
        and row.connected_interface_id is None
        and row.open_ports is None
        and row.source == "manual"
        and set(row.custom_fields or {}) == {"technical"}
    )


async def sync_technical_addresses(session: AsyncSession, prefix: Prefix) -> None:
    """Mirror prefix.gateway/dns_servers into reserved address rows.

    Only addresses inside the prefix get rows — a resolver living elsewhere
    stays a prefix attribute, not a foreign member of this subnet's address
    space. Runs inside the caller's transaction; ORM add/delete keeps the
    changelog hooks honest.
    """
    net = prefix_math.to_network(prefix.prefix)
    desired: dict[int, str] = {}
    for raw in prefix.dns_servers or []:
        ip = ipaddress.ip_address(str(raw))
        if ip in net:
            desired[int(ip)] = "dns"
    if prefix.gateway is not None:
        gw = ipaddress.ip_address(str(prefix.gateway))
        if gw in net:
            desired[int(gw)] = "gateway"

    rows = (
        await session.execute(
            select(IPAddress).where(IPAddress.prefix_id == prefix.id)
        )
    ).scalars().all()
    by_int = {int(r.address_int): r for r in rows}
    ranges = await ranges_for_prefix(session, prefix.id)

    for addr_int, kind in desired.items():
        existing = by_int.get(addr_int)
        if existing is None:
            session.add(
                IPAddress(
                    address=str(ipaddress.ip_address(addr_int)),
                    address_int=addr_int,
                    prefix_id=prefix.id,
                    vrf_id=prefix.vrf_id,
                    hostname=TECHNICAL_HOSTNAME[kind],
                    notes=TECHNICAL_NOTES[kind],
                    status=IPStatus.RESERVED,
                    custom_fields={"technical": kind},
                    source="manual",
                    # Membership is informational — a managed technical row is
                    # legitimate wherever the operator put the gateway, so the
                    # pool guard is intentionally not consulted here.
                    ip_range_id=(
                        r.id
                        if (r := containing_range(ranges, addr_int))
                        else None
                    ),
                )
            )
        elif _pristine_technical(existing) and _technical_kind(existing) != kind:
            # Same address, new job (dns -> gateway) — refresh the marker.
            existing.hostname = TECHNICAL_HOSTNAME[kind]
            existing.notes = TECHNICAL_NOTES[kind]
            existing.custom_fields = {"technical": kind}
        # Anything else is a row someone owns — never clobber it.

    for row in rows:
        if int(row.address_int) in desired:
            continue
        if _pristine_technical(row):
            await session.delete(row)


async def ranges_for_prefix(session: AsyncSession, prefix_id: int) -> list[IPRange]:
    return (
        (await session.execute(select(IPRange).where(IPRange.prefix_id == prefix_id)))
        .scalars()
        .all()
    )


def containing_range(ranges: Iterable[IPRange], address_int: int) -> IPRange | None:
    """The (at most one — overlap is rejected at write time) range holding
    this address integer."""
    for r in ranges:
        if int(r.start_int) <= address_int <= int(r.end_int):
            return r
    return None


def apply_pool_membership(
    row: IPAddress, ranges: Iterable[IPRange], *, force: bool = False
) -> None:
    """Stamp row.ip_range_id from its address, enforcing the pool guard.

    Static (active/reserved) rows inside a dhcp/pool range conflict — a DHCP
    server may hand the address out. ``force`` allows the write and marks it
    ``custom_fields.pool_override`` so the exception stays auditable; a row
    already carrying the marker is considered acknowledged and stays allowed.
    """
    hit = containing_range(ranges, int(row.address_int))
    row.ip_range_id = hit.id if hit else None
    if hit is None or hit.role not in _RANGES_BLOCK or row.status not in _STATICS_BLOCKED:
        return
    cf = dict(row.custom_fields or {})
    if force:
        cf["pool_override"] = True
        row.custom_fields = cf
        return
    if cf.get("pool_override"):
        return
    name = f"{hit.start_address}–{hit.end_address}"
    if hit.description:
        name += f" ({hit.description})"
    raise ConflictError(
        f"{row.address} falls inside {hit.role.value} range {name} — "
        "static assignments inside a pool need force=1"
    )


async def stamp_range_roles(session: AsyncSession, rows) -> None:
    """Group-stamp `range_role` onto address rows — same unmapped-attribute
    pattern as services.devices.stamp_device_names (no per-row lazy load)."""
    ids = {r.ip_range_id for r in rows if r.ip_range_id is not None}
    roles = (
        dict(
            (
                await session.execute(
                    select(IPRange.id, IPRange.role).where(IPRange.id.in_(ids))
                )
            ).all()
        )
        if ids
        else {}
    )
    for r in rows:
        r.range_role = roles.get(r.ip_range_id) if r.ip_range_id else None
