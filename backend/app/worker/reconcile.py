import ipaddress
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ip_address import IPAddress, IPStatus
from app.worker.scanner import HostResult

# Reconcile policy keys read from effective settings (Settings > Features).
# Missing keys fall back to the original hard-coded behavior.
_DEF = {
    "scan_marks_offline": True,
    "scan_reactivates_offline": True,
    "scan_new_hosts_discovered": True,
    "scan_stored_mac_wins": False,
    "scan_overwrites_hostname": False,
    "scan_infers_device_type": True,
    "scan_offline_grace_scans": 0,
}


def _flag(flags: dict[str, Any] | None, key: str) -> Any:
    if flags is None:
        return _DEF[key]
    return flags.get(key, _DEF[key])


async def reconcile(
    session: AsyncSession,
    prefix_id: int,
    vrf_id: int,
    hosts: list[HostResult],
    net,
    flags: dict[str, Any] | None = None,
) -> tuple[int, int]:
    """Merge scan results into the address table.

    Existing rows: refresh last_seen/mac/vendor/hostname; DISCOVERED/OFFLINE ->
    ACTIVE. New rows: inserted as DISCOVERED (or ACTIVE when the
    scan_new_hosts_discovered toggle is off).
    Previously-live rows absent from this scan -> OFFLINE — but only inside
    the scanned network's range: `prefix_id` often resolves to a *covering*
    prefix, so sweeping the whole prefix would mark untouched subnets offline.
    The scan_offline_grace_scans setting delays that flip until a host has
    been absent for N consecutive scans (missed_scans counter).
    Returns (hosts_seen, hosts_new).
    """
    marks_offline = bool(_flag(flags, "scan_marks_offline"))
    reactivates = bool(_flag(flags, "scan_reactivates_offline"))
    discovered_status = (
        IPStatus.DISCOVERED
        if _flag(flags, "scan_new_hosts_discovered")
        else IPStatus.ACTIVE
    )
    stored_mac_wins = bool(_flag(flags, "scan_stored_mac_wins"))
    overwrite_hostname = bool(_flag(flags, "scan_overwrites_hostname"))
    infer_type = bool(_flag(flags, "scan_infers_device_type"))
    # 0/1 both mean "offline on the first miss" (the original behavior).
    grace = max(1, int(_flag(flags, "scan_offline_grace_scans") or 0))

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
                    status=discovered_status,
                    last_seen=now,
                )
            )
            new_count += 1
        else:
            row.last_seen = now
            if row.missed_scans:
                row.missed_scans = 0
            if h.mac:
                if row.mac_address and row.mac_address.lower() != h.mac.lower():
                    # Imported inventory said a different MAC — flag the
                    # mismatch for review. Live value wins by default; the
                    # scan_stored_mac_wins toggle keeps the stored MAC instead
                    # (e.g. randomized phone MACs flapping every scan).
                    cf = dict(row.custom_fields or {})
                    cf["mac_mismatch"] = {
                        "was": row.mac_address,
                        "seen": h.mac,
                        "at": now.isoformat(timespec="seconds"),
                    }
                    row.custom_fields = cf
                    if not stored_mac_wins:
                        row.mac_address = h.mac
                elif "mac_mismatch" in (row.custom_fields or {}):
                    # scan now agrees with the stored MAC — clear the flag
                    cf = dict(row.custom_fields)
                    cf.pop("mac_mismatch", None)
                    row.custom_fields = cf
                    row.mac_address = h.mac
                else:
                    row.mac_address = h.mac
            if h.vendor:
                row.vendor = h.vendor
            if h.hostname and (not row.hostname or overwrite_hostname):
                row.hostname = h.hostname
            # latest probe result is authoritative for ports
            row.open_ports = h.open_ports or None
            # ...and for device type, unless the toggle protects a set value
            if h.device_type and (infer_type or not row.device_type):
                row.device_type = h.device_type
            # OFFLINE -> ACTIVE when seen again; DISCOVERED stays pending
            # review; RESERVED/DHCP are intentional and never clobbered.
            if row.status == IPStatus.OFFLINE and reactivates:
                row.status = IPStatus.ACTIVE

    # hosts previously live but absent from this scan -> offline
    # (`existing` is already scoped to the scanned range, so out-of-range
    # addresses on the covering prefix are never touched)
    for key, row in existing.items():
        if key in seen_ints:
            continue
        if row.status not in (IPStatus.ACTIVE, IPStatus.DISCOVERED):
            continue
        row.missed_scans = (row.missed_scans or 0) + 1
        if marks_offline and row.missed_scans >= grace:
            row.status = IPStatus.OFFLINE

    await session.flush()
    return len(hosts), new_count
