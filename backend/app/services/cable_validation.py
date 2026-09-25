"""Cable validation (V8.2) — the physical-layer twin of mac_mismatch.

v4a documents what *should* be cabled; v8 learns what the switch
*reports*. This module closes the loop at the tail of each device's
``poll_device`` pass: three narrow checks per interface on the polled
device, each writing a ``validation`` JSONB blob —

    {cable_mismatch: {reason, detail, at, ...},   <- the flag itself
     lldp: [{remote_name, remote_port, remote_mac, local_port_id}],
     macs_seen: [<mac>, ...]   (bounded ~32),
     notes: [...],
     checked_at}

The checks, in priority order (one flag slot per interface):

1. ``documented_down`` — a cable is documented on the port and the live
   IF-MIB pass reports ``operStatus=down``. The inverse (up, uncabled)
   is informational only — it lands in ``notes``, never a flag.
2. ``far_end_absent`` — the documented far-end device has known MACs
   (its interfaces' ``mac_address`` ∪ its linked ``ip_addresses``), the
   bridge table learned *other* MACs on this port, and none of the
   expected ones appear. Bridge MACs age out, so a silent port is no
   evidence: only a port that learned MACs we don't recognize flags.
3. ``lldp_neighbor`` — LLDP reports a neighbor on a port with NO
   documented cable. Not a wrong cable — a missing one.

Absent evidence is not a violation: a missing/failed walk skips its
check entirely (no raising AND no clearing — ``bridge=None`` /
``lldp=None`` mean "no data", ``{}`` / ``[]`` mean "walked, empty").

Flags self-heal: each flag clears on the poll where its own condition
is disproved by fresh evidence. Cable/interface mutations also clear
the flag keys on the touched interfaces — the next poll re-derives
everything. Human dismissal (review_dismissals, kind='cable_mismatch')
is the only sticky suppression; fingerprints are reason + link
identity, so a genuinely different finding resurfaces.

Everything here is observed state: bulk ``update()`` writes, no
changelog churn — the same treatment ``oper_status`` already gets.
"""
from datetime import datetime

from sqlalchemy import bindparam, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cabling import DeviceInterface
from app.models.device import Device
from app.models.ip_address import IPAddress
from app.services import notify
from app.services.cabling import peers_for

FLAG = "cable_mismatch"
FLAG_KEYS = (FLAG, "notes")

# Bounds — one port's evidence stays small regardless of table size.
MAX_MACS_SEEN = 32
MAX_LLDP_NEIGHBORS = 16
MAX_NEW_FLAGS = 32  # emit payload cap

# Review surface vocabulary (mirrored by the frontend section).
REASON_LABELS = {
    "documented_down": "cabled but port reports down",
    "far_end_absent": "peer MACs not learned on this port",
    "lldp_neighbor": "LLDP neighbor on uncabled port",
}


def _norm_mac(mac: str | None) -> str | None:
    """Loose EUI-48 normalize for comparison: hex chars, lowercased.
    Anything that isn't 12 hex digits normalizes to its stripped lower
    form — still consistent for set membership."""
    if not mac:
        return None
    hexed = "".join(c for c in mac if c in "0123456789abcdefABCDEF")
    return hexed.lower() or None


def flag_fingerprint(flag: dict) -> str:
    """Stable identity of one finding — the dismissal key. reason +
    the link the flag is about: the cable row for cable checks, the
    remote system identity for undocumented neighbors. A re-patch (new
    cable id) or a different neighbor is a different finding."""
    reason = flag.get("reason") or ""
    cable_id = flag.get("cable_id")
    if cable_id is not None:
        return f"{reason}|c{cable_id}"
    remote = f"{flag.get('remote_name') or ''}|{flag.get('remote_port') or ''}"
    return f"{reason}|{remote}"


async def _known_peer_macs(
    session: AsyncSession, peer_dev_ids: set[int]
) -> dict[int, set[str]]:
    """peer device_id -> every MAC we can plausibly expect to see behind
    its ports: its interfaces' ``mac_address`` ∪ its owned
    ``ip_addresses.mac_address``. Two grouped queries for any fan-out."""
    out: dict[int, set[str]] = {}
    if not peer_dev_ids:
        return out
    for model, col in (
        (DeviceInterface, DeviceInterface.device_id),
        (IPAddress, IPAddress.device_id),
    ):
        rows = await session.execute(
            select(col, model.mac_address).where(
                col.in_(peer_dev_ids), model.mac_address.is_not(None)
            )
        )
        for dev_id, mac in rows.all():
            m = _norm_mac(mac)
            if m:
                out.setdefault(dev_id, set()).add(m)
    return out


def _map_lldp(
    lldp: list[dict] | None, ifaces: list[DeviceInterface]
) -> dict[int, list[dict]]:
    """lldpRemTable rows -> {our interface_id: [neighbors]}.

    Resolution uses the agent's OWN port identifier — ``local_port_id``
    (lldpLocPortId, walked alongside the rem table): exact name match
    first, case-folded, then a MAC match (macAddress-subtype agents).
    No numeric fallback: ``local_port`` ≈ bridge base port is a guess,
    not evidence — an unattributed neighbor is dropped, not blamed.
    """
    if lldp is None:
        return {}
    by_name = {i.name: i for i in ifaces}
    by_name_cf = {i.name.lower(): i for i in ifaces}
    by_mac = {
        m: i
        for i in ifaces
        if (m := _norm_mac(i.mac_address)) is not None
    }
    out: dict[int, list[dict]] = {}
    for row in lldp:
        pid = (row.get("local_port_id") or "").strip()
        if not pid:
            continue
        target = (
            by_name.get(pid)
            or by_name_cf.get(pid.lower())
            or by_mac.get(_norm_mac(pid) or "")
        )
        if target is None:
            continue
        out.setdefault(target.id, []).append(
            {
                "remote_name": row.get("remote_name"),
                "remote_port": row.get("remote_port"),
                "remote_mac": row.get("remote_mac"),
                "local_port_id": pid,
            }
        )
    return out


def _evaluate(
    iface: DeviceInterface,
    *,
    peer,
    fresh_oper: str | None,
    learned: set[str] | None,
    known_macs: set[str] | None,
    neighbors: list[dict] | None,
    now: datetime,
) -> dict | None:
    """The three checks for one covered port -> a flag dict or None.

    ``learned``/``neighbors`` are None when their walk produced no
    evidence (off/failed) — the check is skipped, not failed."""
    if peer is not None:
        detail = f"{peer.device_name} · {peer.interface_name}"
        # 1. documented-but-down — the live oper says the link is dead.
        if fresh_oper == "down":
            return {
                "reason": "documented_down",
                "detail": detail,
                "at": now.isoformat(),
                "cable_id": peer.cable_id,
            }
        # 2. mac-on-port — the bridge learned others' MACs here but
        #    none of the far end's. Silent port = aged out = no flag.
        if learned and known_macs and learned.isdisjoint(known_macs):
            return {
                "reason": "far_end_absent",
                "detail": detail,
                "at": now.isoformat(),
                "cable_id": peer.cable_id,
                "evidence": {
                    "learned": len(learned),
                    "expected": len(known_macs),
                },
            }
        return None
    # 3. undocumented neighbor — LLDP says something lives here, the
    #    documentation says nothing does. Missing cable, not wrong one.
    if neighbors:
        first = neighbors[0]
        remote = f"{first.get('remote_name') or '?'} · {first.get('remote_port') or '?'}"
        return {
            "reason": "lldp_neighbor",
            "detail": remote,
            "at": now.isoformat(),
            "remote_name": first.get("remote_name"),
            "remote_port": first.get("remote_port"),
        }
    return None


def _disproved(
    flag: dict,
    *,
    peer,
    fresh_oper: str | None,
    learned: set[str] | None,
    known_macs: set[str] | None,
    neighbors: list[dict] | None,
    bridge: dict | None,
    lldp: list | None,
) -> bool:
    """May an existing flag be dropped? Only when ITS OWN check was
    re-evaluated on fresh evidence and came back clean — or the cable
    the flag was about no longer exists."""
    reason = flag.get("reason")
    if reason in ("documented_down", "far_end_absent"):
        if peer is None:
            return True  # cable gone — the documented fact is gone
        if reason == "documented_down":
            return fresh_oper is not None and fresh_oper != "down"
        if bridge is None:
            return False  # no MAC evidence this poll — can't disprove
        learned = learned or set()
        return not (learned and known_macs and learned.isdisjoint(known_macs))
    if reason == "lldp_neighbor":
        if peer is not None:
            return True  # now documented — the missing-cable finding died
        return lldp is not None and not neighbors
    return False


async def validate_device(
    session: AsyncSession,
    dev: Device,
    *,
    polled: list[dict],
    bridge: dict[int, list[str]] | None,
    lldp: list[dict] | None,
    now: datetime,
) -> dict:
    """Run the three checks over a device's ports after a poll.

    Consumes the walks ``poll_device`` already fetched — no re-polling.
    Returns counts + the newly-raised flag rows for the notify emit."""
    ifaces = list(
        (
            await session.execute(
                select(DeviceInterface).where(DeviceInterface.device_id == dev.id)
            )
        ).scalars()
    )
    if not ifaces:
        return {
            "checked": 0,
            "flagged": 0,
            "raised": 0,
            "cleared": 0,
            "new_flags": [],
        }

    peers = await peers_for(session, ifaces)
    known_macs = await _known_peer_macs(
        session, {p.device_id for p in peers.values()}
    )
    lldp_map = _map_lldp(lldp, ifaces)
    oper_by_idx = {
        row["if_index"]: row.get("oper")
        for row in polled
        if row.get("if_index") is not None
    }
    iso = now.isoformat()

    stats = {"checked": 0, "flagged": 0, "raised": 0, "cleared": 0}
    new_flags: list[dict] = []
    bulk: list[dict] = []

    for i in ifaces:
        peer = peers.get(i.id)
        fresh_oper = (
            oper_by_idx.get(i.if_index) if i.if_index is not None else None
        )
        seen_macs = (
            sorted(set(bridge.get(i.if_index, [])))
            if bridge is not None and i.if_index is not None
            else None
        )
        learned = (
            {_norm_mac(m) for m in seen_macs} - {None}
            if seen_macs is not None
            else None
        )
        neighbors = lldp_map.get(i.id, [])

        # Coverage: fresh evidence touched this port this poll. An
        # uncovered port keeps its blob — last-known state, never
        # silently rewritten by a walk that didn't see it.
        covered = (
            fresh_oper is not None
            or i.id in lldp_map
            or bool(learned)
        )
        if not covered:
            stats["flagged"] += int(
                bool(i.validation and i.validation.get(FLAG))
            )
            continue
        stats["checked"] += 1

        new_flag = _evaluate(
            i,
            peer=peer,
            fresh_oper=fresh_oper,
            learned=learned,
            known_macs=known_macs.get(peer.device_id) if peer else None,
            neighbors=neighbors,
            now=now,
        )
        old = dict(i.validation or {})
        old_flag = old.get(FLAG)
        val = dict(old)
        val["checked_at"] = iso
        if seen_macs is not None:
            val["macs_seen"] = seen_macs[:MAX_MACS_SEEN]
        if lldp is not None:
            val["lldp"] = neighbors[:MAX_LLDP_NEIGHBORS]
        # The informational inverse of check 1 — observed, not flagged.
        if peer is None and (fresh_oper or i.oper_status) == "up":
            val["notes"] = ["up_uncabled"]
        else:
            val.pop("notes", None)

        if new_flag is not None:
            if old_flag and flag_fingerprint(old_flag) == flag_fingerprint(
                new_flag
            ):
                val[FLAG] = old_flag  # same finding — keep first-seen `at`
            else:
                val[FLAG] = new_flag
                stats["raised"] += 1
                if len(new_flags) < MAX_NEW_FLAGS:
                    new_flags.append(
                        {
                            "interface_id": i.id,
                            "interface": i.name,
                            "reason": new_flag["reason"],
                            "detail": new_flag["detail"],
                        }
                    )
            stats["flagged"] += 1
        elif old_flag and _disproved(
            old_flag,
            peer=peer,
            fresh_oper=fresh_oper,
            learned=learned,
            known_macs=known_macs.get(peer.device_id) if peer else None,
            neighbors=neighbors,
            bridge=bridge,
            lldp=lldp,
        ):
            val.pop(FLAG, None)
            stats["cleared"] += 1
        else:
            stats["flagged"] += int(bool(val.get(FLAG)))

        if val != old:
            bulk.append({"id": i.id, "validation": val or None})

    if bulk:
        # Observed state via Core update — same as oper_status: no ORM
        # events, no changelog churn. synchronize_session=False + the
        # caller re-selects interfaces on the next poll anyway.
        await session.execute(
            update(DeviceInterface)
            .values(validation=bindparam("validation"))
            .execution_options(synchronize_session=False),
            bulk,
        )
    stats["new_flags"] = new_flags
    return stats


async def clear_validation(
    session: AsyncSession, interface_ids
) -> int:
    """Drop flag keys on interfaces whose cabling just changed.

    Called by cable create/patch/delete and interface patch: a stale
    ``cable_mismatch`` (or an ``up_uncabled`` note) must not survive a
    documented truth that changed under it — the next poll re-derives
    everything. Observed-blob evidence (lldp, macs_seen) stays."""
    ids = {int(i) for i in interface_ids if i}
    if not ids:
        return 0
    rows = (
        await session.execute(
            select(DeviceInterface.id, DeviceInterface.validation).where(
                DeviceInterface.id.in_(ids),
                DeviceInterface.validation.is_not(None),
            )
        )
    ).all()
    cleared = 0
    for rid, val in rows:
        if not isinstance(val, dict) or not any(
            k in val for k in FLAG_KEYS
        ):
            continue
        new_val = {k: v for k, v in val.items() if k not in FLAG_KEYS}
        await session.execute(
            update(DeviceInterface)
            .where(DeviceInterface.id == rid)
            .values(validation=new_val or None)
        )
        cleared += 1
    return cleared


async def emit_new_flags(
    device_id: int, device_name: str, new_flags: list[dict]
) -> None:
    """Post-commit notify — one ``cable.mismatch`` event per poll per
    device carrying the newly-raised flags. Cleared/recurrent flags are
    silent (recoveries don't page); ``emit`` is failure-isolated."""
    if not new_flags:
        return
    await notify.emit(
        "cable.mismatch",
        f"{len(new_flags)} cable mismatch(es) flagged on {device_name}",
        {"device_id": device_id, "device": device_name, "items": new_flags},
    )


async def flagged_counts(
    session: AsyncSession, device_ids: list[int]
) -> dict[int, int]:
    """device_id -> count of interfaces carrying the cable_mismatch
    flag. One grouped query — the anti-N+1 path for device list/detail
    headers (mirrors ``interface_stats``)."""
    if not device_ids:
        return {}
    rows = await session.execute(
        select(DeviceInterface.device_id, func.count())
        .where(
            DeviceInterface.device_id.in_(device_ids),
            DeviceInterface.validation.has_key(FLAG),  # noqa: W601
        )
        .group_by(DeviceInterface.device_id)
    )
    return {d: n for d, n in rows.all()}
