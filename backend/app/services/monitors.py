"""Monitor-target resolution + state machine — shared by the API
(check-now) and the worker sweep so both paths behave identically.

The observed columns (state/consecutive_failures/last_*) are written via
Core ``update()`` — never ORM attribute writes — so steady-state churn
can't touch the changelog even before the SKIP_FIELDS guard. last_change_at
only moves when ``state`` actually flips.
"""
from datetime import datetime

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ip_address import IPAddress, IPStatus
from app.models.monitoring import MonitorState, MonitorTarget
from app.schemas.common import ip_display
from app.services.devices import ips_by_device

# Per-tick hard cap — the tick batches all due targets into ONE arq job;
# anything beyond the cap simply stays due and is picked next minute.
TICK_BATCH_LIMIT = 200


def device_check_ip(ips: list[IPAddress]) -> IPAddress | None:
    """The address a device target probes: first ACTIVE ip, else the
    lowest-id row — deterministic, and 'is the box reachable' maps onto
    whichever address the network actually watches."""
    active = [i for i in ips if i.status == IPStatus.ACTIVE]
    pool = active or ips
    return min(pool, key=lambda i: i.id, default=None)


async def resolve_ips(
    session: AsyncSession, targets: list[MonitorTarget]
) -> dict[int, str | None]:
    """target.id -> concrete IP string (or None when unresolvable — the
    check fails with an honest error, e.g. 'device has no addresses')."""
    addr_ids = {t.address_id for t in targets if t.address_id is not None}
    addrs = (
        {
            r.id: ip_display(r.address)
            for r in (
                await session.execute(
                    select(IPAddress).where(IPAddress.id.in_(addr_ids))
                )
            ).scalars()
        }
        if addr_ids
        else {}
    )
    dev_ids = {t.device_id for t in targets if t.device_id is not None}
    dev_ips = await ips_by_device(session, list(dev_ids))
    out: dict[int, str | None] = {}
    for t in targets:
        if t.address_id is not None:
            out[t.id] = addrs.get(t.address_id)
        else:
            ip = device_check_ip(dev_ips.get(t.device_id, []))
            out[t.id] = ip_display(ip.address) if ip else None
    return out


def target_label(
    t: MonitorTarget,
    ip: str | None,
    device_names: dict[int, str] | None = None,
) -> str:
    """Human label for lists/logs/events: 'web-01 · 10.0.0.5' for device
    targets, '10.0.0.5' (+hostname later) for address targets."""
    if t.device_id is not None:
        name = (device_names or {}).get(t.device_id)
        base = name or f"device#{t.device_id}"
        return f"{base} · {ip}" if ip else base
    if ip:
        return ip
    return f"address#{t.address_id}"


def due_where(now: datetime):
    """The 'is due' predicate — never-checked or interval elapsed. Shared
    by the tick's select and the /summary count so they agree."""
    return or_(
        MonitorTarget.last_checked_at.is_(None),
        MonitorTarget.last_checked_at
        + func.make_interval(0, 0, 0, 0, 0, 0, MonitorTarget.interval_seconds)
        <= now,
    )


async def due_target_ids(
    session: AsyncSession, now: datetime, limit: int = TICK_BATCH_LIMIT
) -> list[int]:
    """Enabled targets whose interval has elapsed — id order, capped."""
    stmt = (
        select(MonitorTarget.id)
        .where(MonitorTarget.enabled.is_(True), due_where(now))
        .order_by(MonitorTarget.id)
        .limit(limit)
    )
    return list((await session.execute(stmt)).scalars().all())


def parse_http_expect(
    expect: str | None, status_code: int, body: str
) -> tuple[bool, str | None]:
    """(ok, error) for an HTTP response against the expectation grammar."""
    if not expect:
        ok = 200 <= status_code < 400
        return ok, None if ok else f"http status {status_code}"
    if expect.startswith("status:"):
        want = int(expect.split(":", 1)[1])
        ok = status_code == want
        return ok, None if ok else f"http status {status_code} != {want}"
    ok = expect in body
    return ok, None if ok else "expected substring not in body"


async def apply_result(
    session: AsyncSession,
    target_id: int,
    prev_state: MonitorState,
    prev_failures: int,
    down_after: int,
    ok: bool,
    error: str | None,
    now: datetime,
) -> MonitorState:
    """Write one check's outcome. Returns the NEW state — the caller diffs
    prev_state/new_state to decide whether to emit an event.

    down -> up is recovery (emit); up/unknown -> down at the failure
    threshold is the flap (emit); unknown -> up on first contact stays
    silent. Steady-state writes are Core updates: no ORM churn, no
    changelog noise.
    """
    if ok:
        failures = 0
        new_state = MonitorState.UP
        err = None
    else:
        failures = prev_failures + 1
        err = (error or "check failed")[:2000]
        new_state = (
            MonitorState.DOWN if failures >= down_after else prev_state
        )
    values: dict = {
        "state": new_state,
        "consecutive_failures": failures,
        "last_checked_at": now,
        "last_error": err,
    }
    if new_state != prev_state:
        values["last_change_at"] = now
    await session.execute(
        update(MonitorTarget).where(MonitorTarget.id == target_id).values(**values)
    )
    return new_state
