import ipaddress

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import DATA_DELETE, DATA_WRITE, has_perm, require_perm
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
from app.services.csv_export import csv_response, parse_csv
from app.services.ipam import IPAMError, get_or_404

router = APIRouter(prefix="/addresses", tags=["addresses"])


@router.get("/export.csv")
async def export_addresses(
    prefix_id: int | None = None,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(IPAddress).order_by(IPAddress.address_int)
    if prefix_id is not None:
        stmt = stmt.where(IPAddress.prefix_id == prefix_id)
    rows = (await session.execute(stmt)).scalars().all()
    return csv_response(
        "addresses.csv",
        [
            "address", "prefix_id", "vrf_id", "hostname", "mac_address",
            "vendor", "status", "role", "nat_inside_id", "device_type",
            "open_ports", "last_seen", "notes",
        ],
        [
            [
                str(a.address), a.prefix_id, a.vrf_id, a.hostname or "",
                a.mac_address or "", a.vendor or "", a.status.value,
                a.role.value if a.role else "", a.nat_inside_id or "",
                a.device_type or "",
                " ".join(str(p) for p in (a.open_ports or [])),
                a.last_seen.isoformat() if a.last_seen else "", a.notes or "",
            ]
            for a in rows
        ],
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
    existing = {
        (int(r.address_int), r.prefix_id)
        for r in (await session.execute(select(IPAddress))).scalars()
    }

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
        return {"affected": 0}
    # delete hides inside a POST here — enforce the stricter permission inline
    if body.action == "delete" and not has_perm(user, DATA_DELETE):
        raise HTTPException(403, f"requires {DATA_DELETE} permission")
    if body.action == "delete":
        await session.execute(delete(IPAddress).where(IPAddress.id.in_(body.ids)))
    elif body.action == "set_status":
        if body.status is None:
            raise HTTPException(422, "status required for set_status")
        rows = (
            await session.execute(select(IPAddress).where(IPAddress.id.in_(body.ids)))
        ).scalars().all()
        for r in rows:
            r.status = body.status
    elif body.action == "set_role":
        rows = (
            await session.execute(select(IPAddress).where(IPAddress.id.in_(body.ids)))
        ).scalars().all()
        for r in rows:
            r.role = body.role
    elif body.action in ("add_tag", "remove_tag"):
        if body.tag_id is None:
            raise HTTPException(422, "tag_id required")
        for oid in body.ids:
            if body.action == "add_tag":
                exists = (
                    await session.execute(
                        select(TagAssignment).where(
                            TagAssignment.tag_id == body.tag_id,
                            TagAssignment.object_type == "IPAddress",
                            TagAssignment.object_id == oid,
                        )
                    )
                ).scalar_one_or_none()
                if exists is None:
                    session.add(
                        TagAssignment(
                            tag_id=body.tag_id,
                            object_type="IPAddress",
                            object_id=oid,
                        )
                    )
            else:
                await session.execute(
                    delete(TagAssignment).where(
                        TagAssignment.tag_id == body.tag_id,
                        TagAssignment.object_type == "IPAddress",
                        TagAssignment.object_id == oid,
                    )
                )
    else:
        raise HTTPException(422, f"unknown action {body.action!r}")
    await session.commit()
    return {"affected": len(body.ids)}


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
    stmt = select(IPAddress).order_by(IPAddress.address_int).limit(limit).offset(offset)
    if vrf_id is not None:
        stmt = stmt.where(IPAddress.vrf_id == vrf_id)
    if prefix_id is not None:
        stmt = stmt.where(IPAddress.prefix_id == prefix_id)
    if status is not None:
        stmt = stmt.where(IPAddress.status == status)
    if tag_id is not None:
        stmt = stmt.where(
            IPAddress.id.in_(
                select(TagAssignment.object_id).where(
                    TagAssignment.object_type == "IPAddress",
                    TagAssignment.tag_id == tag_id,
                )
            )
        )
    rows = (await session.execute(stmt)).scalars().all()
    if q:
        from app.services.workbook.normalize import fold_hebrew

        ql = fold_hebrew(q.lower())
        rows = [
            r
            for r in rows
            if ql in str(r.address).lower()
            or (r.hostname and ql in fold_hebrew(r.hostname.lower()))
            or (r.mac_address and ql in r.mac_address.lower())
            or (r.vendor and ql in fold_hebrew(r.vendor.lower()))
            or (r.notes and ql in fold_hebrew(r.notes.lower()))
        ]
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
        notes=body.notes,
    )
    session.add(row)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(409, f"{ip} already exists in this VRF")
    await session.refresh(row)
    return row


@router.get("/{address_id}", response_model=IPAddressOut)
async def get_address(address_id: int, session: AsyncSession = Depends(get_session)):
    try:
        return await get_or_404(session, IPAddress, address_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))


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
    for field, value in data.items():
        setattr(row, field, value)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(409, "address already exists in this VRF")
    await session.refresh(row)
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
