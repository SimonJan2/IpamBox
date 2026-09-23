import ipaddress

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import DATA_DELETE, DATA_WRITE, has_perm, require_perm
from app.models.device import Device
from app.models.ip_address import IPAddress, IPRole, IPStatus
from app.models.user import User
from app.models.prefix import Prefix
from app.models.tag import TagAssignment
from app.schemas.ip_address import (
    IPAddressCreate,
    IPAddressOut,
    IPAddressUpdate,
    _norm_mac,
)
from app.services import prefix_math
from app.services.colors import stamp_colors
from app.services.csv_export import csv_response, parse_csv
from app.services.devices import stamp_device_names
from app.services.ipam import IPAMError, get_or_404

router = APIRouter(prefix="/addresses", tags=["addresses"])

ADDRESS_CSV_COLUMNS = [
    "address", "prefix_id", "vrf_id", "hostname", "mac_address",
    "vendor", "status", "role", "nat_inside_id", "device_type",
    "open_ports", "last_seen", "notes", "display_color",
]


def _addresses_stmt(
    vrf_id: int | None,
    prefix_id: int | None,
    statuses: set[IPStatus] | None,
    tag_ids: set[int] | None,
    untagged: bool,
    q: str | None,
):
    """Shared list/export filter construction — one predicate, two callers."""
    stmt = select(IPAddress).order_by(IPAddress.address_int)
    if vrf_id is not None:
        stmt = stmt.where(IPAddress.vrf_id == vrf_id)
    if prefix_id is not None:
        stmt = stmt.where(IPAddress.prefix_id == prefix_id)
    if statuses:
        stmt = stmt.where(IPAddress.status.in_(statuses))
    if tag_ids:
        # address carries at least one of the selected tags
        stmt = stmt.where(
            IPAddress.id.in_(
                select(TagAssignment.object_id).where(
                    TagAssignment.object_type == "IPAddress",
                    TagAssignment.tag_id.in_(tag_ids),
                )
            )
        )
    if untagged:
        stmt = stmt.where(
            ~IPAddress.id.in_(
                select(TagAssignment.object_id).where(
                    TagAssignment.object_type == "IPAddress"
                )
            )
        )
    if q:
        # Fold Hebrew final letters on both sides (same idiom as entities.py)
        # and match in SQL — a post-limit Python filter would page wrong.
        from app.services.workbook.normalize import fold_hebrew

        like = f"%{fold_hebrew(q)}%"
        stmt = stmt.where(
            or_(
                func.translate(cast(IPAddress.address, String), "םןץףך", "מנצפכ").ilike(like),
                func.translate(IPAddress.hostname, "םןץףך", "מנצפכ").ilike(like),
                func.translate(IPAddress.mac_address, "םןץףך", "מנצפכ").ilike(like),
                func.translate(IPAddress.vendor, "םןץףך", "מנצפכ").ilike(like),
                func.translate(IPAddress.notes, "םןץףך", "מנצפכ").ilike(like),
            )
        )
    return stmt


def _parse_statuses(raw: str | None) -> set[IPStatus] | None:
    """CSV of status names (e.g. 'active,discovered') -> set; 422 on bad."""
    if raw is None or not raw.strip():
        return None
    try:
        return {IPStatus(p.strip()) for p in raw.split(",") if p.strip()}
    except ValueError as e:
        raise HTTPException(422, f"bad status value: {e}")


def _parse_tag_ids(raw: str | None, tag_id: int | None) -> set[int] | None:
    """CSV of tag ids merged with the singular tag_id param."""
    ids: set[int] = set()
    if raw:
        try:
            ids.update(int(p.strip()) for p in raw.split(",") if p.strip())
        except ValueError:
            raise HTTPException(422, f"bad tags value: {raw!r}")
    if tag_id is not None:
        ids.add(tag_id)
    return ids or None


def _address_csv_row(a: IPAddress) -> list:
    return [
        str(a.address), a.prefix_id, a.vrf_id, a.hostname or "",
        a.mac_address or "", a.vendor or "", a.status.value,
        a.role.value if a.role else "", a.nat_inside_id or "",
        a.device_type or "",
        " ".join(str(p) for p in (a.open_ports or [])),
        a.last_seen.isoformat() if a.last_seen else "", a.notes or "",
        a.display_color or "",
    ]


@router.get("/export.csv")
async def export_addresses(
    prefix_id: int | None = None,
    vrf_id: int | None = None,
    status: str | None = Query(
        default=None, description="status or comma-separated status list"
    ),
    tag_id: int | None = None,
    tags: str | None = Query(
        default=None,
        description="comma-separated tag ids — address must carry at least one",
    ),
    untagged: bool = False,
    q: str | None = Query(
        default=None, description="match address/hostname/mac/vendor/notes"
    ),
    session: AsyncSession = Depends(get_session),
):
    """Same filters as the list endpoint — what a filtered view shows is what
    downloads. Extras over the list: `status`/`tags` accept CSV sets and
    `untagged` selects addresses with no tag assignments."""
    statuses = _parse_statuses(status)
    tag_ids = _parse_tag_ids(tags, tag_id)
    stmt = _addresses_stmt(vrf_id, prefix_id, statuses, tag_ids, untagged, q)
    rows = (await session.execute(stmt)).scalars().all()
    rows = await stamp_colors(session, "addresses", rows)
    filtered = any(
        x is not None for x in (vrf_id, prefix_id, statuses, tag_ids)
    ) or untagged or bool(q)
    return csv_response(
        "addresses-filtered.csv" if filtered else "addresses.csv",
        ADDRESS_CSV_COLUMNS,
        [_address_csv_row(a) for a in rows],
    )


class ImportRow(BaseModel):
    row: int
    ok: bool
    detail: str


@router.post(
    "/import",
    response_model=list[ImportRow],
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def import_addresses(
    request: Request,
    dry_run: bool = Query(default=False),
    session: AsyncSession = Depends(get_session),
):
    """Bulk-create addresses from CSV text. Columns: address, prefix (CIDR),
    hostname, mac_address, status, role, notes. ?dry_run=1 validates only."""
    rows = parse_csv((await request.body()).decode("utf-8", "replace"))
    if not rows:
        raise HTTPException(422, "empty CSV or missing header row")

    prefixes = (await session.execute(select(Prefix))).scalars().all()
    by_cidr = {str(prefix_math.to_network(p.prefix)): p for p in prefixes}

    # Existing-address lookup scoped to the prefixes this file references —
    # a full-table load was an accidental O(addresses) on every import.
    ref_prefix_ids: set[int] = set()
    for r in rows:
        try:
            ref_net = ipaddress.ip_network(r.get("prefix") or "", strict=False)
        except ValueError:
            continue
        ref_prefix = by_cidr.get(str(ref_net))
        if ref_prefix is not None:
            ref_prefix_ids.add(ref_prefix.id)
    existing = (
        {
            (int(r.address_int), r.prefix_id)
            for r in (
                await session.execute(
                    select(IPAddress.address_int, IPAddress.prefix_id).where(
                        IPAddress.prefix_id.in_(ref_prefix_ids)
                    )
                )
            )
        }
        if ref_prefix_ids
        else set()
    )

    results: list[ImportRow] = []
    to_add: list[IPAddress] = []
    for i, r in enumerate(rows, start=2):  # header is row 1
        try:
            if not r.get("address"):
                raise ValueError("missing address")
            ip = ipaddress.ip_address(r["address"])
            cidr = r.get("prefix") or ""
            if not cidr:
                raise ValueError("missing prefix column")
            net = ipaddress.ip_network(cidr, strict=False)
            prefix = by_cidr.get(str(net))
            if prefix is None:
                raise ValueError(f"prefix {net} does not exist")
            if ip not in net:
                raise ValueError(f"{ip} not inside {net}")
            if (int(ip), prefix.id) in existing:
                raise ValueError("address already exists")
            status = r.get("status") or "active"
            if status not in {s.value for s in IPStatus}:
                raise ValueError(f"bad status {status!r}")
            mac = _norm_mac(r.get("mac_address") or None)
            role = r.get("role") or None
            row = IPAddress(
                address=str(ip),
                address_int=int(ip),
                prefix_id=prefix.id,
                vrf_id=prefix.vrf_id,
                hostname=r.get("hostname") or None,
                mac_address=mac,
                status=IPStatus(status),
                role=None if role is None else IPRole(role),
                notes=r.get("notes") or None,
            )
            existing.add((int(ip), prefix.id))
            to_add.append(row)
            results.append(ImportRow(row=i, ok=True, detail=str(ip)))
        except Exception as e:
            results.append(ImportRow(row=i, ok=False, detail=str(e)))

    if dry_run or any(not r.ok for r in results):
        return results

    session.add_all(to_add)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(409, f"import conflict: {e.orig}")
    return results


class BulkBody(BaseModel):
    ids: list[int]
    action: str  # "delete" | "set_status" | "set_role" | "add_tag" | "remove_tag"
    status: IPStatus | None = None
    role: IPRole | None = None
    tag_id: int | None = None


@router.post("/bulk")
async def bulk_addresses(
    body: BulkBody,
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(require_perm(DATA_WRITE)),
):
    if not body.ids:
        return {"affected": 0, "not_found": []}
    # delete hides inside a POST here — enforce the stricter permission inline
    if body.action == "delete" and not has_perm(user, DATA_DELETE):
        raise HTTPException(403, f"requires {DATA_DELETE} permission")
    if body.action == "set_status" and body.status is None:
        raise HTTPException(422, "status required for set_status")
    if body.action in ("add_tag", "remove_tag") and body.tag_id is None:
        raise HTTPException(422, "tag_id required")
    if body.action not in ("delete", "set_status", "set_role", "add_tag", "remove_tag"):
        raise HTTPException(422, f"unknown action {body.action!r}")

    # Resolve which requested ids actually exist — callers get the real
    # affected count plus the stale ids, not len(body.ids) parroted back.
    found = set(
        (
            await session.execute(
                select(IPAddress.id).where(IPAddress.id.in_(body.ids))
            )
        ).scalars()
    )
    missing = sorted(set(body.ids) - found)

    if body.action == "delete":
        # ORM deletes so the changelog hook records one entry per row — a
        # Core-level DELETE would bypass the audit trail entirely.
        rows = (
            await session.execute(select(IPAddress).where(IPAddress.id.in_(found)))
        ).scalars().all()
        for r in rows:
            await session.delete(r)
        affected = len(rows)
    elif body.action == "set_status":
        rows = (
            await session.execute(select(IPAddress).where(IPAddress.id.in_(found)))
        ).scalars().all()
        for r in rows:
            r.status = body.status
        affected = len(rows)
    elif body.action == "set_role":
        rows = (
            await session.execute(select(IPAddress).where(IPAddress.id.in_(found)))
        ).scalars().all()
        for r in rows:
            r.role = body.role
        affected = len(rows)
    elif body.action == "add_tag":
        already = set(
            (
                await session.execute(
                    select(TagAssignment.object_id).where(
                        TagAssignment.tag_id == body.tag_id,
                        TagAssignment.object_type == "IPAddress",
                        TagAssignment.object_id.in_(found),
                    )
                )
            ).scalars()
        )
        todo = found - already
        session.add_all(
            TagAssignment(
                tag_id=body.tag_id, object_type="IPAddress", object_id=oid
            )
            for oid in todo
        )
        affected = len(todo)
    else:  # remove_tag — ORM deletes so each unassign lands in the changelog
        rows = (
            await session.execute(
                select(TagAssignment).where(
                    TagAssignment.tag_id == body.tag_id,
                    TagAssignment.object_type == "IPAddress",
                    TagAssignment.object_id.in_(found),
                )
            )
        ).scalars().all()
        for r in rows:
            await session.delete(r)
        affected = len(rows)
    await session.commit()
    return {"affected": affected, "not_found": missing}


@router.get("", response_model=list[IPAddressOut])
async def list_addresses(
    vrf_id: int | None = None,
    prefix_id: int | None = None,
    status: IPStatus | None = None,
    tag_id: int | None = None,
    q: str | None = Query(default=None, description="match address/hostname/mac"),
    limit: int = Query(default=500, le=5000),
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    stmt = _addresses_stmt(
        vrf_id,
        prefix_id,
        {status} if status is not None else None,
        {tag_id} if tag_id is not None else None,
        untagged=False,
        q=q,
    )
    rows = (
        (await session.execute(stmt.limit(limit).offset(offset))).scalars().all()
    )
    rows = await stamp_colors(session, "addresses", rows)
    await stamp_device_names(session, rows)
    return rows


@router.post(
    "",
    response_model=IPAddressOut,
    status_code=201,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def create_address(body: IPAddressCreate, session: AsyncSession = Depends(get_session)):
    try:
        prefix = await get_or_404(session, Prefix, body.prefix_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))

    ip = ipaddress.ip_address(body.address)
    net = prefix_math.to_network(prefix.prefix)
    if ip not in net:
        raise HTTPException(422, f"{ip} is not inside prefix {net}")

    if body.nat_inside_id is not None:
        try:
            await get_or_404(session, IPAddress, body.nat_inside_id)
        except IPAMError as e:
            raise HTTPException(e.status_code, str(e))
    if body.device_id is not None:
        try:
            await get_or_404(session, Device, body.device_id)
        except IPAMError as e:
            raise HTTPException(e.status_code, str(e))

    row = IPAddress(
        address=str(ip),
        address_int=int(ip),
        prefix_id=prefix.id,
        vrf_id=prefix.vrf_id,
        mac_address=body.mac_address,
        hostname=body.hostname,
        vendor=body.vendor,
        status=body.status,
        role=body.role,
        nat_inside_id=body.nat_inside_id,
        device_id=body.device_id,
        notes=body.notes,
    )
    session.add(row)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(409, f"{ip} already exists in this VRF")
    await session.refresh(row)
    await stamp_colors(session, "addresses", [row])
    await stamp_device_names(session, [row])
    return row


@router.get("/{address_id}", response_model=IPAddressOut)
async def get_address(address_id: int, session: AsyncSession = Depends(get_session)):
    try:
        row = await get_or_404(session, IPAddress, address_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    await stamp_colors(session, "addresses", [row])
    await stamp_device_names(session, [row])
    return row


@router.patch(
    "/{address_id}",
    response_model=IPAddressOut,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def update_address(
    address_id: int, body: IPAddressUpdate, session: AsyncSession = Depends(get_session)
):
    try:
        row = await get_or_404(session, IPAddress, address_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    data = body.model_dump(exclude_unset=True)
    if "prefix_id" in data and data["prefix_id"] is not None:
        try:
            new_prefix = await get_or_404(session, Prefix, data["prefix_id"])
        except IPAMError as e:
            raise HTTPException(e.status_code, str(e))
        ip = ipaddress.ip_address(str(row.address).split("/")[0])
        if ip not in prefix_math.to_network(new_prefix.prefix):
            raise HTTPException(422, f"{ip} is not inside prefix {new_prefix.prefix}")
        row.vrf_id = new_prefix.vrf_id
    if "nat_inside_id" in data and data["nat_inside_id"] == address_id:
        raise HTTPException(422, "address cannot be its own NAT inside peer")
    if data.get("device_id") is not None:
        try:
            await get_or_404(session, Device, data["device_id"])
        except IPAMError as e:
            raise HTTPException(e.status_code, str(e))
    for field, value in data.items():
        setattr(row, field, value)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(409, "address already exists in this VRF")
    await session.refresh(row)
    await stamp_colors(session, "addresses", [row])
    await stamp_device_names(session, [row])
    return row


@router.delete(
    "/{address_id}",
    status_code=204,
    dependencies=[Depends(require_perm(DATA_DELETE))],
)
async def delete_address(address_id: int, session: AsyncSession = Depends(get_session)):
    try:
        row = await get_or_404(session, IPAddress, address_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    await session.delete(row)
    await session.commit()
