"""Monitor targets — CRUD + check-now + the dashboard summary counts.

Hand router (not _crud_router): device/address refs are resolved into a
display label + the concrete IP a check would hit, PATCH re-validates the
merged row against the kind rules, and /check runs a probe inline through
the same code path the sweep uses.
"""
import asyncio
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import DATA_WRITE, require_perm
from app.models.device import Device
from app.models.ip_address import IPAddress
from app.models.monitoring import MonitorState, MonitorTarget
from app.schemas.common import Page, ip_display
from app.schemas.monitor import (
    MonitorSummary,
    MonitorTargetCreate,
    MonitorTargetOut,
    MonitorTargetUpdate,
    validate_kind_fields,
)
from app.services import monitors as svc
from app.services import notify, runtime_settings
from app.services.ipam import IPAMError, get_or_404

router = APIRouter(prefix="/monitor-targets", tags=["monitoring"])


async def _get(session: AsyncSession, target_id: int) -> MonitorTarget:
    try:
        return await get_or_404(session, MonitorTarget, target_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))


async def _check_refs(session: AsyncSession, data: dict) -> None:
    """404 for FK references that don't resolve — before the DB would."""
    try:
        if data.get("device_id") is not None:
            await get_or_404(session, Device, data["device_id"])
        if data.get("address_id") is not None:
            await get_or_404(session, IPAddress, data["address_id"])
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))


async def _stamp(session: AsyncSession, rows: list[MonitorTarget]) -> None:
    """Resolve target_label / resolved_ip / device_name for output rows
    via grouped queries — never per-row."""
    ips = await svc.resolve_ips(session, rows)
    dev_ids = {r.device_id for r in rows if r.device_id is not None}
    names = (
        dict(
            (
                await session.execute(
                    select(Device.id, Device.name).where(Device.id.in_(dev_ids))
                )
            ).all()
        )
        if dev_ids
        else {}
    )
    addr_ids = {r.address_id for r in rows if r.address_id is not None}
    hostnames = (
        dict(
            (
                await session.execute(
                    select(IPAddress.id, IPAddress.hostname).where(
                        IPAddress.id.in_(addr_ids)
                    )
                )
            ).all()
        )
        if addr_ids
        else {}
    )
    for r in rows:
        label = svc.target_label(r, ips[r.id], names)
        if r.address_id and (hn := hostnames.get(r.address_id)):
            label += f" ({hn})"
        r.target_label = label
        r.resolved_ip = ips[r.id]
        r.device_name = (
            names.get(r.device_id) if r.device_id is not None else None
        )


def _filters(
    stmt,
    *,
    device_id: int | None,
    address_id: int | None,
    kind: str | None,
    state: str | None,
    enabled: bool | None,
):
    if device_id is not None:
        stmt = stmt.where(MonitorTarget.device_id == device_id)
    if address_id is not None:
        stmt = stmt.where(MonitorTarget.address_id == address_id)
    if kind is not None:
        stmt = stmt.where(MonitorTarget.kind == kind)
    if state is not None:
        stmt = stmt.where(MonitorTarget.state == state)
    if enabled is not None:
        stmt = stmt.where(MonitorTarget.enabled == enabled)
    return stmt


@router.get("", response_model=Page[MonitorTargetOut])
async def list_targets(
    device_id: int | None = None,
    address_id: int | None = None,
    kind: str | None = Query(default=None, pattern="^(ping|tcp|http)$"),
    state: str | None = Query(default=None, pattern="^(up|down|unknown)$"),
    enabled: bool | None = None,
    limit: int | None = Query(default=None, ge=1, le=20000),
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    stmt = _filters(
        select(MonitorTarget),
        device_id=device_id, address_id=address_id, kind=kind,
        state=state, enabled=enabled,
    )
    total = await session.scalar(
        select(func.count()).select_from(stmt.subquery())
    )
    rows = list(
        (
            await session.execute(
                stmt.order_by(MonitorTarget.id).limit(limit).offset(offset)
            )
        )
        .scalars()
        .all()
    )
    await _stamp(session, rows)
    return Page(items=rows, total=total or 0, limit=limit, offset=offset)


# Declared before /{target_id} so the literal path can't be shadowed.
@router.get("/summary", response_model=MonitorSummary)
async def summary(session: AsyncSession = Depends(get_session)):
    counts = dict(
        (
            await session.execute(
                select(MonitorTarget.state, func.count()).group_by(
                    MonitorTarget.state
                )
            )
        ).all()
    )
    now = datetime.now(timezone.utc)
    due = await session.scalar(
        select(func.count(MonitorTarget.id)).where(
            MonitorTarget.enabled.is_(True), svc.due_where(now)
        )
    )
    return MonitorSummary(
        up=int(counts.get(MonitorState.UP, 0)),
        down=int(counts.get(MonitorState.DOWN, 0)),
        unknown=int(counts.get(MonitorState.UNKNOWN, 0)),
        due=int(due or 0),
    )


@router.post(
    "",
    response_model=MonitorTargetOut,
    status_code=201,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def create_target(
    body: MonitorTargetCreate, session: AsyncSession = Depends(get_session)
):
    data = body.model_dump()
    await _check_refs(session, data)
    t = MonitorTarget(**data)
    session.add(t)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(409, "duplicate or invalid value") from e
    await session.refresh(t)
    await _stamp(session, [t])
    return t


@router.get("/{target_id}", response_model=MonitorTargetOut)
async def get_target(
    target_id: int, session: AsyncSession = Depends(get_session)
):
    t = await _get(session, target_id)
    await _stamp(session, [t])
    return t


@router.patch(
    "/{target_id}",
    response_model=MonitorTargetOut,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def update_target(
    target_id: int,
    body: MonitorTargetUpdate,
    session: AsyncSession = Depends(get_session),
):
    t = await _get(session, target_id)
    data = body.model_dump(exclude_unset=True)
    # Re-pointing the anchor: setting one ref clears the other unless the
    # caller pinned both (both-set or both-null then fails validation).
    if (
        data.get("address_id") is not None
        and "device_id" not in data
    ):
        data["device_id"] = None
    if (
        data.get("device_id") is not None
        and "address_id" not in data
    ):
        data["address_id"] = None
    await _check_refs(session, data)
    for k, v in data.items():
        setattr(t, k, v)
    if (t.device_id is None) == (t.address_id is None):
        raise HTTPException(
            422, "exactly one of device_id / address_id is required"
        )
    try:
        validate_kind_fields(t.kind, t.port, t.http_path, t.http_expect)
    except ValueError as e:
        raise HTTPException(422, str(e))
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(409, "duplicate or invalid value") from e
    await session.refresh(t)
    await _stamp(session, [t])
    return t


@router.delete(
    "/{target_id}",
    status_code=204,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def delete_target(
    target_id: int, session: AsyncSession = Depends(get_session)
):
    t = await _get(session, target_id)
    await session.delete(t)
    await session.commit()


@router.post(
    "/{target_id}/check",
    response_model=MonitorTargetOut,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def check_now(
    target_id: int, session: AsyncSession = Depends(get_session)
):
    """Run one check inline (same path the sweep takes) and persist the
    result — transitions emit through notify just like the cron lane."""
    from app.worker import monitors as wmon

    t = await _get(session, target_id)
    ips = await svc.resolve_ips(session, [t])
    eff = await runtime_settings.get_effective(session)
    ok, err = await wmon.check_target(
        t,
        ips[t.id],
        sem=asyncio.Semaphore(1),
        icmp_timeout=float(eff.values["scan_icmp_timeout"]),
        tcp_timeout=float(eff.values["scan_tcp_timeout"]),
        http_timeout=float(eff.values["monitor_http_timeout"]),
    )
    prev = t.state
    now = datetime.now(timezone.utc)
    new = await svc.apply_result(
        session, t.id, prev, t.consecutive_failures, t.down_after,
        ok, err, now,
    )
    await session.commit()
    await session.refresh(t)
    await _stamp(session, [t])
    # Same emit rules as the sweep: down on crossing, up on recovery only.
    if new == MonitorState.DOWN and prev != MonitorState.DOWN:
        await notify.emit(
            "monitor.down",
            f"{t.target_label} is DOWN ({t.kind.value})",
            {"monitor_target_id": t.id, "kind": t.kind.value,
             "ip": ips[t.id], "device_id": t.device_id,
             "address_id": t.address_id, "error": err},
        )
    elif new == MonitorState.UP and prev == MonitorState.DOWN:
        await notify.emit(
            "monitor.up",
            f"{t.target_label} is UP ({t.kind.value})",
            {"monitor_target_id": t.id, "kind": t.kind.value,
             "ip": ips[t.id], "device_id": t.device_id,
             "address_id": t.address_id},
        )
    return t
