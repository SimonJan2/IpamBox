"""Custom lists: user-defined tables (e.g. a 'שרתים בייצור' server sheet).

Lists carry their own column defs (positional keys, display labels, types);
rows store `data` keyed by those column keys. `GET /rows` resolves every
`ip`-typed cell against ip_addresses in one query so the UI can render live
status without a per-cell lookup.
"""
import ipaddress
import re

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import String, cast, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from pydantic import BaseModel

from app.core.db import get_session
from app.core.deps import DATA_DELETE, DATA_WRITE, has_perm, require_perm
from app.models.custom_list import CustomList, CustomListRow
from app.models.ip_address import IPAddress
from app.models.user import User
from app.schemas.common import Page, ReorderBody, hex_color_or_none
from app.schemas.custom_list import (
    CustomListCreate,
    CustomListOut,
    CustomListRowCreate,
    CustomListRowOut,
    CustomListRowsPage,
    CustomListRowUpdate,
    CustomListUpdate,
    ResolvedIp,
)
from app.services.colors import stamp_colors
from app.services.ipam import IPAMError, get_or_404, slugify
from app.services.ordering import ordered, reorder
from app.services.workbook.normalize import fold_hebrew

router = APIRouter(prefix="/lists", tags=["lists"])

MAX_LIST_ROWS = 20_000
_IP_SPLIT_RE = re.compile(r"[,\s;/]+")


async def _unique_slug(session: AsyncSession, name: str, keep: str | None = None) -> str:
    base = slugify(name)
    taken = set((await session.execute(select(CustomList.slug))).scalars())
    slug, n = base, 2
    while slug in taken and slug != keep:
        slug = f"{base}-{n}"
        n += 1
    return slug


def _check_columns(columns: list | None, key_column: str | None) -> None:
    cols = columns or []
    keys = [c.key if hasattr(c, "key") else c["key"] for c in cols]
    if len(keys) != len(set(keys)):
        raise HTTPException(422, "column keys must be unique")
    if key_column is not None and key_column not in keys:
        raise HTTPException(422, f"key_column {key_column!r} is not a column")


async def _resolve_ips(session, lst: CustomList, rows) -> dict[str, ResolvedIp]:
    """ip-typed cell values -> their ip_addresses row, in one query."""
    ip_cols = [c for c in (lst.columns or []) if c.get("type") == "ip"]
    if not ip_cols:
        return {}
    candidates: set[str] = set()
    for r in rows:
        data = r.data or {}
        for c in ip_cols:
            v = data.get(c["key"])
            if not v:
                continue
            toks = _IP_SPLIT_RE.split(str(v)) if c.get("multi") else [str(v)]
            for t in toks:
                t = t.strip()
                try:
                    candidates.add(str(ipaddress.ip_address(t)))
                except ValueError:
                    continue
    if not candidates:
        return {}
    # address_int is Numeric(39,0) — Decimal binds as NUMERIC. Plain ints
    # would be bound as INTEGER by the expanding IN() param and overflow
    # asyncpg's int4 for IPv4 >= 128.0.0.0 / any IPv6.
    ints = [Decimal(int(ipaddress.ip_address(ip))) for ip in candidates]
    found = (
        await session.execute(
            select(IPAddress).where(IPAddress.address_int.in_(ints))
        )
    ).scalars().all()
    return {
        str(a.address): ResolvedIp(
            id=a.id, prefix_id=a.prefix_id, status=a.status.value,
            hostname=a.hostname, last_seen=a.last_seen,
        )
        for a in found
    }


@router.get("", response_model=Page[CustomListOut])
async def list_lists(
    limit: int | None = Query(default=None, ge=1, le=20000),
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(CustomList).order_by(
        CustomList.sort_order.asc().nulls_last(), CustomList.id
    )
    total = await session.scalar(
        select(func.count()).select_from(stmt.order_by(None).subquery())
    )
    rows = (
        await session.execute(stmt.limit(limit).offset(offset))
    ).scalars().all()
    counts = dict(
        (await session.execute(
            select(CustomListRow.list_id, func.count())
            .group_by(CustomListRow.list_id)
        )).all()
    )
    for lst in rows:
        lst.row_count = counts.get(lst.id, 0)
    return Page(items=rows, total=total or 0, limit=limit, offset=offset)


@router.post(
    "",
    response_model=CustomListOut,
    status_code=201,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def create_list(
    body: CustomListCreate, session: AsyncSession = Depends(get_session)
):
    _check_columns(body.columns, body.key_column)
    lst = CustomList(
        name=body.name,
        slug=await _unique_slug(session, body.name),
        description=body.description,
        icon=body.icon,
        columns=[c.model_dump() for c in body.columns],
        key_column=body.key_column,
    )
    session.add(lst)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(409, "duplicate or invalid value") from e
    await session.refresh(lst)
    return lst


@router.post("/reorder", status_code=204, dependencies=[Depends(require_perm(DATA_WRITE))])
async def reorder_lists(
    body: ReorderBody, session: AsyncSession = Depends(get_session)
):
    try:
        await reorder(session, CustomList, body.ids)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))


@router.get("/{list_id}", response_model=CustomListOut)
async def get_list(list_id: int, session: AsyncSession = Depends(get_session)):
    try:
        lst = await get_or_404(session, CustomList, list_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    lst.row_count = await session.scalar(
        select(func.count()).where(CustomListRow.list_id == lst.id)
    ) or 0
    return lst


@router.patch(
    "/{list_id}",
    response_model=CustomListOut,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def update_list(
    list_id: int,
    body: CustomListUpdate,
    session: AsyncSession = Depends(get_session),
):
    try:
        lst = await get_or_404(session, CustomList, list_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    patch = body.model_dump(exclude_unset=True)
    _check_columns(
        patch.get("columns", lst.columns),
        patch.get("key_column", lst.key_column),
    )
    if "name" in patch and patch["name"] != lst.name:
        patch["slug"] = await _unique_slug(session, patch["name"], keep=lst.slug)
    if "columns" in patch and patch["columns"] is not None:
        patch["columns"] = [c.model_dump() for c in body.columns]
    for field, value in patch.items():
        setattr(lst, field, value)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(409, "duplicate or invalid value") from e
    await session.refresh(lst)
    return lst


@router.delete(
    "/{list_id}",
    status_code=204,
    dependencies=[Depends(require_perm(DATA_DELETE))],
)
async def delete_list(list_id: int, session: AsyncSession = Depends(get_session)):
    try:
        lst = await get_or_404(session, CustomList, list_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    await session.delete(lst)
    await session.commit()


# --- rows -----------------------------------------------------------------


@router.get("/{list_id}/rows", response_model=CustomListRowsPage)
async def list_rows(
    list_id: int,
    q: str = "",
    limit: int | None = Query(default=None, ge=1, le=20000),
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    try:
        lst = await get_or_404(session, CustomList, list_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    stmt = select(CustomListRow).where(CustomListRow.list_id == list_id)
    if q:
        # jsonb::text match — Hebrew-folded on both sides like the entity
        # routers; searches every cell value at once.
        like = f"%{fold_hebrew(q)}%"
        stmt = stmt.where(
            func.translate(
                cast(CustomListRow.data, String), "םןץףך", "מנצפכ"
            ).ilike(like)
        )
    stmt = ordered(stmt, CustomListRow, CustomListRow.id)
    total = await session.scalar(
        select(func.count()).select_from(stmt.order_by(None).subquery())
    )
    rows = (
        await session.execute(stmt.limit(limit).offset(offset))
    ).scalars().all()
    resolved = await _resolve_ips(session, lst, rows)
    await stamp_colors(session, "custom_list_rows", rows)
    return CustomListRowsPage(
        items=rows, total=total or 0, limit=limit, offset=offset,
        resolved=resolved,
    )


@router.post(
    "/{list_id}/rows/reorder",
    status_code=204,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def reorder_rows(
    list_id: int,
    body: ReorderBody,
    session: AsyncSession = Depends(get_session),
):
    # keep the reorder scoped to this list's rows
    ids = set(
        (await session.execute(
            select(CustomListRow.id).where(CustomListRow.list_id == list_id)
        )).scalars().all()
    )
    foreign = [i for i in body.ids if i not in ids]
    if foreign:
        raise HTTPException(422, f"row ids not in list {list_id}: {foreign[:5]}")
    try:
        await reorder(session, CustomListRow, body.ids)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))


@router.post(
    "/{list_id}/rows",
    response_model=CustomListRowOut,
    status_code=201,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def create_row(
    list_id: int,
    body: CustomListRowCreate,
    session: AsyncSession = Depends(get_session),
):
    try:
        await get_or_404(session, CustomList, list_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    total = await session.scalar(
        select(func.count()).where(CustomListRow.list_id == list_id)
    )
    if (total or 0) >= MAX_LIST_ROWS:
        raise HTTPException(422, f"list is capped at {MAX_LIST_ROWS} rows")
    row = CustomListRow(
        list_id=list_id,
        data={k: v for k, v in body.data.items() if v is not None},
        site_id=body.site_id,
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    await stamp_colors(session, "custom_list_rows", [row])
    return row


@router.patch(
    "/{list_id}/rows/{row_id}",
    response_model=CustomListRowOut,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def update_row(
    list_id: int,
    row_id: int,
    body: CustomListRowUpdate,
    session: AsyncSession = Depends(get_session),
):
    try:
        row = await get_or_404(session, CustomListRow, row_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    if row.list_id != list_id:
        raise HTTPException(404, "row not in this list")
    patch = body.model_dump(exclude_unset=True)
    if "data" in patch and patch["data"] is not None:
        # null cell values delete the key; the rest merge in
        cur = dict(row.data or {})
        for k, v in patch["data"].items():
            if v is None:
                cur.pop(k, None)
            else:
                cur[k] = v
        row.data = cur
        row.manually_edited = True
    for f in ("site_id", "pinned", "sort_order", "row_color"):
        if f in patch:
            setattr(row, f, patch[f])
    await session.commit()
    await session.refresh(row)
    await stamp_colors(session, "custom_list_rows", [row])
    return row


class RowBulkBody(BaseModel):
    ids: list[int]
    action: str  # "delete" | "pin" | "unpin" | "set_color" | "clear_color"
    row_color: str | None = None


@router.post(
    "/{list_id}/rows/bulk",
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def bulk_rows(
    list_id: int,
    body: RowBulkBody,
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(require_perm(DATA_WRITE)),
):
    """Bulk row ops, same shape as the addresses /bulk endpoint — ORM-level
    writes so the changelog hook records one entry per row."""
    if body.action not in ("delete", "pin", "unpin", "set_color", "clear_color"):
        raise HTTPException(422, f"unknown action {body.action!r}")
    if body.action == "delete" and not has_perm(user, DATA_DELETE):
        raise HTTPException(403, f"requires {DATA_DELETE} permission")
    if body.action == "set_color":
        v = hex_color_or_none(body.row_color)
        if body.row_color and v is None:
            raise HTTPException(422, "row_color must be #rrggbb")
        body.row_color = v
    rows = (
        await session.execute(
            select(CustomListRow).where(
                CustomListRow.list_id == list_id,
                CustomListRow.id.in_(body.ids),
            )
        )
    ).scalars().all()
    found = {r.id for r in rows}
    missing = sorted(set(body.ids) - found)
    for r in rows:
        if body.action == "delete":
            await session.delete(r)
        elif body.action == "pin":
            r.pinned = True
        elif body.action == "unpin":
            r.pinned = False
        elif body.action == "set_color":
            r.row_color = body.row_color
        elif body.action == "clear_color":
            r.row_color = None
    await session.commit()
    return {"affected": len(rows), "not_found": missing}


@router.delete(
    "/{list_id}/rows/{row_id}",
    status_code=204,
    dependencies=[Depends(require_perm(DATA_DELETE))],
)
async def delete_row(
    list_id: int,
    row_id: int,
    session: AsyncSession = Depends(get_session),
):
    try:
        row = await get_or_404(session, CustomListRow, row_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    if row.list_id != list_id:
        raise HTTPException(404, "row not in this list")
    await session.delete(row)
    await session.commit()
