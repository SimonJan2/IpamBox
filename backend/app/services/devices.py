"""Device helpers: multi-IP health rollup + grouped lookups.

Device health = worst-of across its linked IPs (one device, many IPs is the
point of the entity). Precedence worst-first:

    offline > discovered > dhcp > reserved > active

A device with no linked IPs is unmonitored (health None). The rack detail
and device list compute this in one grouped query — never per-row.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device
from app.models.ip_address import IPAddress, IPStatus

_HEALTH_RANK = {
    IPStatus.OFFLINE: 0,
    IPStatus.DISCOVERED: 1,
    IPStatus.DHCP: 2,
    IPStatus.RESERVED: 3,
    IPStatus.ACTIVE: 4,
}


def health_ip(ips: list[IPAddress]) -> IPAddress | None:
    """The IP driving a device's health: worst status, lowest id on ties.

    The rack elevation dot, the linked-IP label and ip_last_seen all describe
    this same row — "the box is red because THIS address is offline".
    """
    return min(
        ips, key=lambda i: (_HEALTH_RANK[i.status], i.id), default=None
    )


def device_health(ips: list[IPAddress]) -> IPStatus | None:
    ip = health_ip(ips)
    return ip.status if ip is not None else None


async def ips_by_device(
    session: AsyncSession, device_ids: list[int]
) -> dict[int, list[IPAddress]]:
    """One grouped IP query for a set of devices — the anti-N+1 path."""
    if not device_ids:
        return {}
    rows = (
        (
            await session.execute(
                select(IPAddress)
                .where(IPAddress.device_id.in_(device_ids))
                .order_by(IPAddress.id)
            )
        )
        .scalars()
        .all()
    )
    out: dict[int, list[IPAddress]] = {i: [] for i in device_ids}
    for r in rows:
        out[r.device_id].append(r)
    return out


async def stamp_device_names(session: AsyncSession, rows) -> None:
    """Populate ``device_name`` on IPAddressOut rows in one grouped query."""
    ids = {r.device_id for r in rows if r.device_id}
    if not ids:
        return
    names = dict(
        (
            await session.execute(
                select(Device.id, Device.name).where(Device.id.in_(ids))
            )
        ).all()
    )
    for r in rows:
        if r.device_id:
            r.device_name = names.get(r.device_id)
