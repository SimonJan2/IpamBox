import ipaddress
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ip_address import IPAddress, IPStatus
from app.worker.scanner import HostResult


async def reconcile(
    session: AsyncSession,
    prefix_id: int,
    vrf_id: int,
    hosts: list[HostResult],
    net,
) -> tuple[int, int]:
    """Merge scan results into the address table.

    Existing rows: refresh last_seen/mac/vendor/hostname; DISCOVERED/OFFLINE -> ACTIVE.
    New rows: inserted as DISCOVERED.
    Previously-live rows absent from this scan -> OFFLINE — but only inside
    the scanned network's range: `prefix_id` often resolves to a *covering*
    prefix, so sweeping the whole prefix would mark untouched subnets offline.
    Returns (hosts_seen, hosts_new).
    """
    now = datetime.now(timezone.utc)
    first = int(net.network_address)
    last = first + net.num_addresses - 1
    rows = (
        await session.execute(
            select(IPAddress).where(
                IPAddress.prefix_id == prefix_id,
                IPAddress.address_int.between(first, last),
            )
        )
    ).scalars().all()
    existing = {int(r.address_int): r for r in rows}
    seen_ints: set[int] = set()
    new_count = 0

    for h in hosts:
        ip = ipaddress.ip_address(h.ip)
        key = int(ip)
        seen_ints.add(key)
        row = existing.get(key)
        if row is None:
            session.add(
                IPAddress(
                    address=h.ip,
                    address_int=key,
                    prefix_id=prefix_id,
                    vrf_id=vrf_id,
                    mac_address=h.mac,
                    vendor=h.vendor,
                    hostname=h.hostname,
                    open_ports=h.open_ports or None,
                    device_type=h.device_type,
                    status=IPStatus.DISCOVERED,
                    last_seen=now,
                )
            )
            new_count += 1
        else:
            row.last_seen = now
            if h.mac:
                if row.mac_address and row.mac_address.lower() != h.mac.lower():
                    # Imported inventory said a different MAC — keep the live
                    # value but flag the mismatch for review.
                    cf = dict(row.custom_fields or {})
                    cf["mac_mismatch"] = {
                        "was": row.mac_address,
                        "seen": h.mac,
                        "at": now.isoformat(timespec="seconds"),
                    }
                    row.custom_fields = cf
                elif "mac_mismatch" in (row.custom_fields or {}):
                    # scan now agrees with the stored MAC — clear the flag
                    cf = dict(row.custom_fields)
                    cf.pop("mac_mismatch", None)
                    row.custom_fields = cf
                row.mac_address = h.mac
            if h.vendor:
                row.vendor = h.vendor
            if h.hostname and not row.hostname:
                row.hostname = h.hostname
            # latest probe result is authoritative for ports/type
            row.open_ports = h.open_ports or None
            if h.device_type:
                row.device_type = h.device_type
            # OFFLINE -> ACTIVE when seen again; DISCOVERED stays pending
            # review; RESERVED/DHCP are intentional and never clobbered.
            if row.status == IPStatus.OFFLINE:
                row.status = IPStatus.ACTIVE

    # hosts previously live but absent from this scan -> offline
    # (`existing` is already scoped to the scanned range, so out-of-range
    # addresses on the covering prefix are never touched)
    for key, row in existing.items():
        if key not in seen_ints and row.status in (IPStatus.ACTIVE, IPStatus.DISCOVERED):
            row.status = IPStatus.OFFLINE

    await session.flush()
    return len(hosts), new_count
