"""Review sections — every flag the system raises, on one queue.

Sections are read-only queries computed on demand (no worker, no cron).
An item's dismissal key is (section kind, entity_type, entity_id,
fingerprint) — the same tuple POST /review/dismiss stores; `_emit` splits
each section's live findings into open `items` and recallable `dismissed`.

Fingerprints pin the STABLE identity of a finding so the dismissal
survives re-flags: a MAC mismatch keys on the was→seen pair, a duplicate
group on the MAC itself, an unmatched switch ref on the switch/port text.
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_actor
from app.models.cabling import DeviceInterface
from app.models.certificate import Certificate
from app.models.device import Device
from app.models.ip_address import IPAddress, IPStatus
from app.models.review import ReviewDismissal
from app.schemas.common import ip_display
from app.services.cabling import interface_stats
from app.services.ipam import NotFoundError
from app.services.runtime_settings import get_effective

# Bounded payload per section; `count` stays the honest total.
SECTION_CAP = 50


def _item(
    entity_type: str,
    entity_id: int,
    label: str,
    sub: str | None = None,
    detail: dict | None = None,
    flagged_at=None,
    fingerprint: str = "",
) -> dict:
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "label": label,
        "sub": sub,
        "detail": detail or {},
        "flagged_at": flagged_at,
        "fingerprint": fingerprint,
    }


def _iso(v) -> str | None:
    return v.isoformat() if v is not None else None


def mac_fingerprint(was: str | None, seen: str | None) -> str:
    """The stable identity of a MAC mismatch: the documented→observed pair."""
    return f"{(was or '').lower()}->{(seen or '').lower()}"


async def _dismissal_map(
    session: AsyncSession,
) -> dict[tuple[str, str, int, str], ReviewDismissal]:
    rows = (await session.execute(select(ReviewDismissal))).scalars().all()
    return {
        (d.kind, d.entity_type, d.entity_id, d.fingerprint): d for d in rows
    }


def _emit(
    key: str,
    title: str,
    items: list[dict],
    dismissed_map: dict,
    note: str | None = None,
) -> dict:
    open_items, dismissed = [], []
    for it in items:
        hit = dismissed_map.get(
            (key, it["entity_type"], it["entity_id"], it["fingerprint"])
        )
        if hit is None:
            open_items.append(it)
        else:
            dismissed.append(
                {
                    **it,
                    "dismissed_at": hit.created_at,
                    "dismissed_by": hit.actor,
                    "dismiss_notes": hit.notes,
                }
            )
    return {
        "key": key,
        "title": title,
        "count": len(open_items),
        "items": open_items[:SECTION_CAP],
        "dismissed": dismissed[:SECTION_CAP],
        "note": note,
    }


# ---------------------------------------------------------------------------
# Section queries — one function each, in display order.
# ---------------------------------------------------------------------------


async def _mac_mismatch_items(session: AsyncSession) -> list[dict]:
    """Scanner observed a different MAC than inventory documented."""
    rows = (
        (
            await session.execute(
                select(IPAddress)
                .where(IPAddress.custom_fields.has_key("mac_mismatch"))  # noqa: W601
                .order_by(IPAddress.updated_at.desc())
            )
        )
        .scalars()
        .all()
    )
    items = []
    for r in rows:
        flag = (r.custom_fields or {}).get("mac_mismatch") or {}
        was, seen = flag.get("was"), flag.get("seen")
        items.append(
            _item(
                "ip_address",
                r.id,
                ip_display(r.address) or str(r.address),
                sub=r.hostname,
                detail={
                    "mac_was": was,
                    "mac_seen": seen,
                    # live column value — equals `seen` unless the
                    # scan_stored_mac_wins policy kept the stored MAC.
                    "mac_live": r.mac_address,
                    "prefix_id": r.prefix_id,
                },
                flagged_at=flag.get("at") or _iso(r.updated_at),
                fingerprint=mac_fingerprint(was, seen),
            )
        )
    return items


async def _dup_mac_items(session: AsyncSession) -> list[dict]:
    """ip_addresses rows sharing one MAC — real multi-NIC host or bad data."""
    groups = (
        await session.execute(
            select(func.lower(IPAddress.mac_address), func.count())
            .where(IPAddress.mac_address.is_not(None))
            .group_by(func.lower(IPAddress.mac_address))
            .having(func.count() > 1)
            .order_by(func.count().desc(), func.lower(IPAddress.mac_address))
        )
    ).all()
    if not groups:
        return []
    members = (
        (
            await session.execute(
                select(IPAddress)
                .where(
                    func.lower(IPAddress.mac_address).in_([m for m, _ in groups])
                )
                .order_by(IPAddress.id)
            )
        )
        .scalars()
        .all()
    )
    by_mac: dict[str, list[IPAddress]] = {}
    for r in members:
        by_mac.setdefault((r.mac_address or "").lower(), []).append(r)
    items = []
    for mac, n in groups:
        ms = by_mac.get(mac, [])
        items.append(
            _item(
                # A group has no single row — entity_id 0 keeps the
                # dismissal keyed on the MAC fingerprint alone.
                "mac_group",
                0,
                mac,
                sub=f"{n} addresses",
                detail={
                    "members": [
                        {
                            "id": r.id,
                            "address": ip_display(r.address),
                            "hostname": r.hostname,
                            "prefix_id": r.prefix_id,
                            "status": r.status.value,
                        }
                        for r in ms
                    ]
                },
                flagged_at=_iso(
                    min((r.updated_at for r in ms), default=None)
                ),
                fingerprint=f"mac:{mac}",
            )
        )
    return items


async def _aging_discovery_items(
    session: AsyncSession, values: dict
) -> tuple[list[dict], str | None]:
    """DISCOVERED rows older than discovery_expire_days (0 = feature off)."""
    days = int(values.get("discovery_expire_days") or 0)
    if days <= 0:
        return [], "disabled — discovery_expire_days is 0"
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    rows = (
        (
            await session.execute(
                select(IPAddress)
                .where(
                    IPAddress.status == IPStatus.DISCOVERED,
                    # never-seen discovered rows age hardest — NULL sorts first
                    or_(
                        IPAddress.last_seen.is_(None),
                        IPAddress.last_seen < cutoff,
                    ),
                )
                .order_by(IPAddress.last_seen.asc().nulls_first(), IPAddress.id)
            )
        )
        .scalars()
        .all()
    )
    return [
        _item(
            "ip_address",
            r.id,
            ip_display(r.address) or str(r.address),
            sub=r.hostname,
            detail={"prefix_id": r.prefix_id, "expire_days": days},
            flagged_at=_iso(r.last_seen),
            fingerprint=ip_display(r.address) or str(r.address),
        )
        for r in rows
    ], None


async def _offline_items(
    session: AsyncSession, values: dict
) -> list[dict]:
    """OFFLINE hosts past the scan_offline_grace_scans hysteresis."""
    grace = max(1, int(values.get("scan_offline_grace_scans") or 0))
    rows = (
        (
            await session.execute(
                select(IPAddress)
                .where(
                    IPAddress.status == IPStatus.OFFLINE,
                    IPAddress.missed_scans >= grace,
                )
                .order_by(
                    IPAddress.last_seen.asc().nulls_first(), IPAddress.id
                )
            )
        )
        .scalars()
        .all()
    )
    return [
        _item(
            "ip_address",
            r.id,
            ip_display(r.address) or str(r.address),
            sub=r.hostname,
            detail={
                "prefix_id": r.prefix_id,
                "missed_scans": r.missed_scans,
                "grace": grace,
            },
            flagged_at=_iso(r.last_seen),
            fingerprint=ip_display(r.address) or str(r.address),
        )
        for r in rows
    ]


async def _cert_items(
    session: AsyncSession, values: dict
) -> list[dict]:
    """Certificates expiring within cert_warn_days (incl. already expired)."""
    warn = int(values.get("cert_warn_days") or 30)
    today = datetime.now(timezone.utc).date()
    rows = (
        (
            await session.execute(
                select(Certificate)
                .where(
                    Certificate.expires_on.is_not(None),
                    Certificate.expires_on <= today + timedelta(days=warn),
                )
                .order_by(Certificate.expires_on.asc(), Certificate.id)
            )
        )
        .scalars()
        .all()
    )
    items = []
    for r in rows:
        days = (r.expires_on - today).days
        items.append(
            _item(
                "certificate",
                r.id,
                r.cert_name or r.server_name or f"certificate#{r.id}",
                sub=" · ".join(p for p in (r.platform, r.target) if p) or None,
                detail={
                    "expires_on": str(r.expires_on),
                    "days": days,
                    "warn_days": warn,
                },
                flagged_at=str(r.expires_on),
                # renewals change the date -> a dismissed expiry resurfaces
                fingerprint=f"expires:{r.expires_on}",
            )
        )
    return items


async def _unmatched_switch_items(session: AsyncSession) -> list[dict]:
    """Legacy switch_name/switch_port text never resolved to an interface."""
    rows = (
        (
            await session.execute(
                select(IPAddress)
                .where(
                    IPAddress.switch_name.is_not(None),
                    IPAddress.connected_interface_id.is_(None),
                )
                .order_by(IPAddress.switch_name, IPAddress.address_int)
            )
        )
        .scalars()
        .all()
    )
    return [
        _item(
            "ip_address",
            r.id,
            ip_display(r.address) or str(r.address),
            sub=" · ".join(
                p for p in (r.switch_name, r.switch_port) if p
            ),
            detail={
                "switch_name": r.switch_name,
                "switch_port": r.switch_port,
                "prefix_id": r.prefix_id,
            },
            flagged_at=_iso(r.updated_at),
            fingerprint=f"{r.switch_name}|{r.switch_port or ''}",
        )
        for r in rows
    ]


async def _snmp_unmanaged_items(session: AsyncSession) -> list[dict]:
    """Trap senders with an ip_addresses row but no credentialed device.

    The trap receiver stamps ``custom_fields.snmp_unmanaged`` when a trap
    arrives from a documented address that doesn't resolve to an
    SNMP-enabled device — the auto-learn announcement pointed at review
    instead of silent row creation. Rows whose linked device later gains
    credentials (or the flag) drop out of the section automatically."""
    rows = (
        (
            await session.execute(
                select(IPAddress, Device)
                .outerjoin(Device, IPAddress.device_id == Device.id)
                .where(
                    IPAddress.custom_fields.has_key("snmp_unmanaged")  # noqa: W601
                )
                .order_by(IPAddress.address_int)
            )
        )
        .all()
    )
    items = []
    for r, dev in rows:
        if dev is not None and dev.snmp_enabled and dev.snmp_cred_enc:
            continue  # credentialed now — the flag self-clears on traps
        flag = (r.custom_fields or {}).get("snmp_unmanaged") or {}
        items.append(
            _item(
                "ip_address",
                r.id,
                ip_display(r.address) or str(r.address),
                sub=dev.name if dev is not None else r.hostname,
                detail={
                    "trap": flag.get("trap"),
                    "device_id": r.device_id,
                    "prefix_id": r.prefix_id,
                },
                flagged_at=flag.get("at") or _iso(r.updated_at),
                # identity = the sender address — a dismissal survives
                # re-flags from the same source
                fingerprint=ip_display(r.address) or str(r.address),
            )
        )
    return items


async def _uncabled_items(session: AsyncSession) -> list[dict]:
    """Devices that have interfaces but zero cables (wiring='uncabled')."""
    with_ifaces = [
        d
        for d, n in (
            await session.execute(
                select(DeviceInterface.device_id, func.count()).group_by(
                    DeviceInterface.device_id
                )
            )
        ).all()
        if n > 0
    ]
    if not with_ifaces:
        return []
    istats = await interface_stats(session, with_ifaces)
    uncabled = [d for d, (total, cabled) in istats.items() if cabled == 0]
    if not uncabled:
        return []
    devices = (
        (
            await session.execute(
                select(Device)
                .where(Device.id.in_(uncabled))
                .order_by(Device.name, Device.id)
            )
        )
        .scalars()
        .all()
    )
    return [
        _item(
            "device",
            d.id,
            d.name,
            sub=d.device_type,
            detail={"interface_count": istats[d.id][0]},
            flagged_at=_iso(d.updated_at),
        )
        for d in devices
    ]


async def _unracked_items(session: AsyncSession) -> list[dict]:
    """Devices with no rack placement — inventory hygiene, lowest priority."""
    rows = (
        (
            await session.execute(
                select(Device)
                .where(Device.rack_id.is_(None))
                .order_by(Device.name, Device.id)
            )
        )
        .scalars()
        .all()
    )
    return [
        _item(
            "device",
            d.id,
            d.name,
            sub=d.device_type,
            detail={"source": d.source},
            flagged_at=_iso(d.created_at),
        )
        for d in rows
    ]


async def build_review(session: AsyncSession) -> dict:
    """GET /review payload — all sections, dismissed split applied."""
    dismissed = await _dismissal_map(session)
    values = (await get_effective(session)).values

    aging_items, aging_note = await _aging_discovery_items(session, values)
    return {
        "sections": [
            _emit(
                "mac_mismatch",
                "MAC mismatches",
                await _mac_mismatch_items(session),
                dismissed,
            ),
            _emit(
                "dup_mac",
                "Duplicate MACs",
                await _dup_mac_items(session),
                dismissed,
            ),
            _emit(
                "aging_discovery",
                "Aging discoveries",
                aging_items,
                dismissed,
                note=aging_note,
            ),
            _emit(
                "offline",
                "Offline hosts",
                await _offline_items(session, values),
                dismissed,
            ),
            _emit(
                "cert_expiry",
                "Certificates expiring",
                await _cert_items(session, values),
                dismissed,
            ),
            _emit(
                "unmatched_switch",
                "Unmatched switch refs",
                await _unmatched_switch_items(session),
                dismissed,
            ),
            _emit(
                "snmp_unmanaged",
                "Unmanaged SNMP senders",
                await _snmp_unmanaged_items(session),
                dismissed,
            ),
            _emit(
                "uncabled",
                "Uncabled devices",
                await _uncabled_items(session),
                dismissed,
            ),
            _emit(
                "unracked",
                "Unracked devices",
                await _unracked_items(session),
                dismissed,
            ),
        ]
    }


# ---------------------------------------------------------------------------
# Actions — dismissal bookkeeping + the mac_mismatch write paths.
# ---------------------------------------------------------------------------


async def dismiss(
    session: AsyncSession,
    *,
    kind: str,
    entity_type: str,
    entity_id: int,
    fingerprint: str,
    notes: str | None,
) -> ReviewDismissal:
    """Record a dismissal; re-dismissing the same tuple returns the row."""
    row = await session.scalar(
        select(ReviewDismissal).where(
            ReviewDismissal.kind == kind,
            ReviewDismissal.entity_type == entity_type,
            ReviewDismissal.entity_id == entity_id,
            ReviewDismissal.fingerprint == fingerprint,
        )
    )
    if row is not None:
        return row
    row = ReviewDismissal(
        kind=kind,
        entity_type=entity_type,
        entity_id=entity_id,
        fingerprint=fingerprint,
        actor=get_actor(),
        notes=notes,
    )
    session.add(row)
    await session.flush()
    return row


async def undismiss(
    session: AsyncSession,
    *,
    kind: str,
    entity_type: str,
    entity_id: int,
    fingerprint: str,
) -> bool:
    row = await session.scalar(
        select(ReviewDismissal).where(
            ReviewDismissal.kind == kind,
            ReviewDismissal.entity_type == entity_type,
            ReviewDismissal.entity_id == entity_id,
            ReviewDismissal.fingerprint == fingerprint,
        )
    )
    if row is None:
        return False
    await session.delete(row)
    return True


def _mismatch_flag(row: IPAddress) -> dict:
    flag = (row.custom_fields or {}).get("mac_mismatch")
    if not isinstance(flag, dict):
        raise NotFoundError(f"address {row.id} has no mac_mismatch flag")
    return flag


def _clear_flag(row: IPAddress) -> None:
    # Reassign the dict — in-place mutation never registers on JSONB.
    cf = dict(row.custom_fields or {})
    cf.pop("mac_mismatch", None)
    row.custom_fields = cf


async def accept_scanned_mac(
    session: AsyncSession, row: IPAddress
) -> IPAddress:
    """Trust the scanner: scanned MAC becomes the stored mac_address."""
    flag = _mismatch_flag(row)
    if flag.get("seen"):
        row.mac_address = flag["seen"]
    _clear_flag(row)
    await session.flush()
    return row


async def keep_stored_mac(
    session: AsyncSession, row: IPAddress
) -> IPAddress:
    """Trust inventory: restore the documented MAC and dismiss the pair so
    the scanner's next re-flag stays out of the queue (the
    scan_stored_mac_wins policy made persistent, per-address)."""
    flag = _mismatch_flag(row)
    if flag.get("was"):
        row.mac_address = flag["was"]
    _clear_flag(row)
    await dismiss(
        session,
        kind="mac_mismatch",
        entity_type="ip_address",
        entity_id=row.id,
        fingerprint=mac_fingerprint(flag.get("was"), flag.get("seen")),
        notes="kept stored MAC",
    )
    await session.flush()
    return row
