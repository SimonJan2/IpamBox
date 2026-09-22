"""Execute a stored import plan against the DB.

Structure order: sites -> vrfs -> prefixes (+VLAN get-or-create) -> ranges ->
addresses -> entity families. partial=False runs everything in the request
transaction (any failure rolls back); partial=True wraps each sheet's rows in
a savepoint so one bad sheet can't sink the batch.
"""
import ipaddress
from collections import Counter, defaultdict
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset
from app.models.certificate import Certificate
from app.models.change_log import ChangeLog
from app.models.circuit import Circuit
from app.models.custom_list import CustomList, CustomListRow
from app.models.ip_address import IPAddress, IPStatus
from app.models.ip_range import IPRange
from app.models.prefix import Prefix, PrefixStatus
from app.models.service import Service
from app.models.site import Site
from app.models.vlan import VLAN
from app.models.vrf import VRF
from app.services.ipam import slugify
from app.services.workbook.listparse import key_for


class PlanError(Exception):
    pass


async def _get_or_create_site(session, entry, ids) -> int:
    if entry["action"] == "exists" and entry.get("site_id"):
        site = await session.get(Site, entry["site_id"])
        if site is not None:
            # circuit-sheet enrichment may have filled gaps — never
            # overwrite values the site already has
            if not site.code and entry.get("code"):
                site.code = entry["code"]
            if site.site_number is None and entry.get("site_number") is not None:
                site.site_number = entry["site_number"]
            ids[entry["key"]] = site.id
            return site.id
    slug_base = entry.get("slug") or slugify(entry["name"])
    existing = (
        await session.execute(select(Site).where(Site.name == entry["name"]))
    ).scalar_one_or_none()
    if existing is not None:
        ids[entry["key"]] = existing.id
        return existing.id
    slug = slug_base
    taken = set((await session.execute(select(Site.slug))).scalars())
    n = 2
    while slug in taken:
        slug = f"{slug_base}-{n}"
        n += 1
    site = Site(
        name=entry["name"],
        slug=slug,
        description=entry.get("notes"),
        code=entry.get("code"),
        site_number=entry.get("site_number"),
        size=entry.get("size"),
        is_active=entry.get("is_active", True),
    )
    session.add(site)
    await session.flush()
    ids[entry["key"]] = site.id
    return site.id


async def _get_or_create_vrf(session, entry, site_ids, ids) -> int:
    if entry["action"] == "exists" and entry.get("vrf_id"):
        ids[entry["key"]] = entry["vrf_id"]
        return entry["vrf_id"]
    existing = (
        await session.execute(select(VRF).where(VRF.name == entry["name"]))
    ).scalar_one_or_none()
    if existing is not None:
        ids[entry["key"]] = existing.id
        return existing.id
    vrf = VRF(
        name=entry["name"],
        description="created by workbook import",
        site_id=site_ids.get(entry["site_key"]),
    )
    session.add(vrf)
    await session.flush()
    ids[entry["key"]] = vrf.id
    return vrf.id


async def _get_or_create_vlan(session, vid, name, site_id) -> int | None:
    if vid is None:
        return None
    q = select(VLAN).where(VLAN.vid == vid)
    q = q.where(VLAN.site_id == site_id) if site_id else q.where(VLAN.site_id.is_(None))
    existing = (await session.execute(q)).scalars().first()
    if existing is not None:
        return existing.id
    vlan = VLAN(vid=vid, name=(name or f"VLAN {vid}")[:64], site_id=site_id)
    session.add(vlan)
    await session.flush()
    return vlan.id


async def _get_or_create_prefix(session, entry, vrf_ids, site_ids, ids) -> int:
    if entry["action"] == "exists" and entry.get("prefix_id"):
        ids[entry["key"]] = entry["prefix_id"]
        return entry["prefix_id"]
    vrf_id = vrf_ids[entry["vrf_key"]]
    site_id = site_ids.get(entry["site_key"])
    # a matching prefix may have been created by a concurrent or earlier
    # section of this same plan — re-check before inserting
    for p in (await session.execute(select(Prefix).where(Prefix.vrf_id == vrf_id))).scalars():
        if str(ipaddress.ip_network(str(p.prefix), strict=False)) == entry["cidr"]:
            ids[entry["key"]] = p.id
            return p.id
    vlan_id = entry.get("vlan_id")
    if vlan_id is None and entry.get("vlan_vid"):
        vlan_id = await _get_or_create_vlan(
            session, entry["vlan_vid"], entry.get("vlan_name"), site_id
        )
    prefix = Prefix(
        prefix=entry["cidr"],
        vrf_id=vrf_id,
        site_id=site_id,
        vlan_id=vlan_id,
        status=PrefixStatus(entry["status"]),
        description=entry.get("description"),
    )
    session.add(prefix)
    try:
        await session.flush()
    except Exception as e:  # overlap/exclusion -> surface as plan error
        raise PlanError(f"prefix {entry['cidr']}: {e}") from e
    ids[entry["key"]] = prefix.id
    return prefix.id


async def _insert_address(session, row, vrf_ids, prefix_ids, batch_id):
    if row["action"] == "skip":
        return "skip"
    if row["action"] == "update" and row.get("target_id"):
        addr = await session.get(IPAddress, row["target_id"])
        if addr is not None:
            field_map = {
                "hostname": "hostname",
                "mac_address": "mac",
                "serial_number": "serial",
                "switch_name": "switch",
                "switch_port": "port",
                "counter_location": "counter",
                "notes": "notes",
            }
            for f in row.get("fills", []):
                setattr(addr, f, row.get(field_map[f]))
            return "update"
        # target vanished — fall through to create
    addr = IPAddress(
        address=row["address"],
        address_int=int(ipaddress.ip_address(row["address"])),
        prefix_id=prefix_ids[row["prefix_key"]],
        vrf_id=vrf_ids[row["vrf_key"]],
        hostname=row.get("hostname"),
        mac_address=row.get("mac"),
        vendor=row.get("model"),
        status=IPStatus(row["status"]),
        serial_number=row.get("serial"),
        switch_name=row.get("switch"),
        switch_port=row.get("port"),
        counter_location=row.get("counter"),
        custom_fields=row.get("custom_fields"),
        import_batch_id=batch_id,
        notes=row.get("notes"),
    )
    session.add(addr)
    await session.flush()
    return "create"


def _group_by_sheet(rows):
    groups: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        groups[r.get("sheet") or ""].append(r)
    return groups


async def _get_or_create_list(session, entry, batch_id) -> CustomList:
    lst = None
    if entry.get("list_id"):
        lst = await session.get(CustomList, entry["list_id"])
    if lst is None:
        slug_base = slugify(entry["name"])
        lst = (
            await session.execute(
                select(CustomList).where(CustomList.slug == slug_base)
            )
        ).scalar_one_or_none()
    if lst is None:
        slug, n = slug_base, 2
        taken = set((await session.execute(select(CustomList.slug))).scalars())
        while slug in taken:
            slug = f"{slug_base}-{n}"
            n += 1
        lst = CustomList(name=entry["name"], slug=slug)
        session.add(lst)
        await session.flush()
    # the plan already remapped incoming data onto these column keys
    lst.columns = entry.get("columns") or []
    lst.key_column = entry.get("key_column")
    lst.source_sheet = entry.get("sheet")
    lst.import_batch_id = batch_id
    return lst


async def _apply_list(session, entry, batch_id, rep) -> None:
    """Merge-by-key sync of one custom list. Manual edits, pins, colors and
    row order survive; vanished source rows are kept and reported."""
    lst = await _get_or_create_list(session, entry, batch_id)
    key_col = entry.get("key_column")
    live: dict[str, CustomListRow] = {}
    if key_col:
        for row in (
            await session.execute(
                select(CustomListRow).where(CustomListRow.list_id == lst.id)
            )
        ).scalars():
            k = key_for(row.data or {}, key_col)
            if k:
                live.setdefault(k, row)

    name = lst.name
    seen_keys: set[str] = set()
    for i, r in enumerate(entry.get("rows", [])):
        k = r.get("key") or key_for(r.get("data") or {}, key_col)
        if k:
            seen_keys.add(k)
        action = r.get("action")
        label = str((r.get("data") or {}).get(key_col) or f"row {r['row']}")
        if action in ("skip", "conflict"):
            rep(entry["sheet"], r["row"], action, f"list '{name}': {label}")
            continue
        row = None
        if action == "update" and r.get("target_id"):
            row = await session.get(CustomListRow, r["target_id"])
            if row is not None and row.list_id != lst.id:
                row = None
        if row is None and k:
            row = live.get(k)
        if row is not None:
            # re-check at commit time: a UI edit between preview and commit
            # still wins over the sheet
            if row.manually_edited and (row.data or {}) != r["data"]:
                rep(
                    entry["sheet"], r["row"], "conflict",
                    f"list '{name}': '{label}' was edited in-app — kept",
                )
                continue
            if (row.data or {}) != r["data"]:
                row.data = r["data"]
            row.import_batch_id = batch_id
            rep(
                entry["sheet"], r["row"], "update",
                f"list '{name}': '{label}'",
            )
            continue
        session.add(
            CustomListRow(
                list_id=lst.id, data=r.get("data") or {},
                sort_order=i, import_batch_id=batch_id,
            )
        )
        rep(entry["sheet"], r["row"], "create", f"list '{name}': {label}")
    await session.flush()

    if key_col:
        for k, row in live.items():
            if k not in seen_keys:
                label = str((row.data or {}).get(key_col) or row.id)
                rep(
                    entry["sheet"], 0, "skip",
                    f"list '{name}': '{label}' missing from source — kept",
                )


async def execute_plan(
    session: AsyncSession,
    batch,
    plan: dict,
    *,
    partial: bool,
    actor: str,
) -> dict:
    """Returns {'counts': {...}, 'rows': [...]}. Raises on total failure."""
    site_ids: dict[str, int] = {}
    vrf_ids: dict[str, int] = {}
    prefix_ids: dict[str, int] = {}
    results: list[dict] = []

    def rep(sheet, row, action, detail):
        results.append(
            {"sheet": sheet, "row": row, "action": action, "detail": detail}
        )

    # -- scaffold (sites -> vrfs -> prefixes) -----------------------------
    try:
        for entry in plan.get("sites", []):
            await _get_or_create_site(session, entry, site_ids)
        for entry in plan.get("vrfs", []):
            await _get_or_create_vrf(session, entry, site_ids, vrf_ids)
        for entry in plan.get("prefixes", []):
            await _get_or_create_prefix(session, entry, vrf_ids, site_ids, prefix_ids)
    except Exception as e:
        raise PlanError(f"scaffold failed — nothing imported: {e}") from e

    # -- ranges ------------------------------------------------------------
    for r in plan.get("ranges", []):
        try:
            prefix_id = prefix_ids[r["prefix_key"]]
            lo = ipaddress.ip_address(r["lo"])
            hi = ipaddress.ip_address(r["hi"])
            if partial:
                async with session.begin_nested():
                    session.add(
                        IPRange(
                            prefix_id=prefix_id, vrf_id=vrf_ids[r["vrf_key"]],
                            start_address=str(lo), start_int=int(lo),
                            end_address=str(hi), end_int=int(hi),
                            role=r["role"], description=r.get("description"),
                        )
                    )
                    await session.flush()
            else:
                session.add(
                    IPRange(
                        prefix_id=prefix_id, vrf_id=vrf_ids[r["vrf_key"]],
                        start_address=str(lo), start_int=int(lo),
                        end_address=str(hi), end_int=int(hi),
                        role=r["role"], description=r.get("description"),
                    )
                )
                await session.flush()
            rep(r["sheet"], r["row"], "create", f"range {r['lo']}-{r['hi']}")
        except Exception as e:
            if not partial:
                raise
            rep(r["sheet"], r["row"], "error", str(e)[:200])

    # -- addresses, grouped per sheet for partial-mode savepoints -----------
    addr_groups = _group_by_sheet(plan.get("addresses", []))
    for sheet, rows in addr_groups.items():
        for row in rows:
            try:
                if partial:
                    async with session.begin_nested():
                        outcome = await _insert_address(
                            session, row, vrf_ids, prefix_ids, batch.id
                        )
                else:
                    outcome = await _insert_address(
                        session, row, vrf_ids, prefix_ids, batch.id
                    )
                rep(sheet, row["row"], outcome, row["address"])
            except Exception as e:
                if not partial:
                    raise
                rep(sheet, row["row"], "error", f"{row['address']}: {str(e)[:200]}")

    # -- entity families -----------------------------------------------------
    def _site_id(key):
        return site_ids.get(key) if key else None

    entity_specs = (
        ("circuits", Circuit, lambda r: {
            "env": r.get("env"), "site_id": _site_id(r.get("site_key")),
            "site_number": r.get("site_number"), "site_code": r.get("site_code"),
            "site_name": r.get("site_name"), "line_type": r.get("line_type"),
            "bezeq_circuit_id": r.get("bezeq_circuit_id"), "node": r.get("node"),
            "bw_down": r.get("bw_down"), "bw_up": r.get("bw_up"),
            "wan_ip": r.get("wan_ip"), "app_client_num": r.get("app_client_num"),
            "app_client_name": r.get("app_client_name"),
            "app_service_type": r.get("app_service_type"),
            "contact": r.get("contact"), "status": r.get("status"),
            "notes": r.get("notes"), "is_retired": r.get("is_retired", False),
        }),
        ("certificates", Certificate, lambda r: {
            "platform": r.get("platform"), "target": r.get("target"),
            "server_name": r.get("server_name"), "cert_name": r.get("cert_name"),
            "expires_on": r.get("expires_on"), "serial_raw": r.get("serial_raw"),
            "notes": r.get("notes"),
        }),
        ("assets", Asset, lambda r: {
            "kind": r.get("kind"), "category": r.get("category"),
            "vendor": r.get("vendor"), "model": r.get("model"),
            "purpose": r.get("purpose"), "version": r.get("version"),
            "eol_on": r.get("eol_on"), "support_status": r.get("support_status"),
            "serial_number": r.get("serial_number"),
            "site_id": _site_id(r.get("site_key")), "notes": r.get("notes"),
        }),
        ("services", Service, lambda r: {
            "name": r.get("name"), "beneficiary": r.get("beneficiary"),
            "site_id": _site_id(r.get("site_key")), "site_code": r.get("site_code"),
            "doc_path": r.get("doc_path"), "test_info": r.get("test_info"),
            "notes": r.get("notes"),
        }),
    )
    for section, model, to_kwargs in entity_specs:
        for r in plan.get(section, []):
            try:
                kw = to_kwargs(r)
                if kw.get("expires_on") and isinstance(kw["expires_on"], str):
                    kw["expires_on"] = datetime.fromisoformat(kw["expires_on"]).date()
                if kw.get("eol_on") and isinstance(kw["eol_on"], str):
                    kw["eol_on"] = datetime.fromisoformat(kw["eol_on"]).date()
                if partial:
                    async with session.begin_nested():
                        session.add(model(**kw, import_batch_id=batch.id))
                        await session.flush()
                else:
                    session.add(model(**kw, import_batch_id=batch.id))
                    await session.flush()
                rep(r["sheet"], r["row"], "create", model.__name__)
            except Exception as e:
                if not partial:
                    raise
                rep(r["sheet"], r["row"], "error", str(e)[:200])

    # -- custom lists (merge-by-key per list) ------------------------------
    for entry in plan.get("custom_lists", []):
        try:
            if partial:
                async with session.begin_nested():
                    await _apply_list(session, entry, batch.id, rep)
            else:
                await _apply_list(session, entry, batch.id, rep)
        except Exception as e:
            if not partial:
                raise
            rep(
                entry["sheet"], 0, "error",
                f"list '{entry.get('name')}': {str(e)[:200]}",
            )

    counts = Counter(r["action"] for r in results)
    return {"counts": dict(counts), "rows": results}


async def commit_batch(session, batch, plan: dict, *, partial: bool, actor: str) -> dict:
    result = await execute_plan(session, batch, plan, partial=partial, actor=actor)
    has_errors = result["counts"].get("error", 0) > 0
    if has_errors and not partial:
        raise PlanError("plan has errors — nothing committed")
    await session.execute(
        ChangeLog.__table__.insert(),
        [
            {
                "actor": actor,
                "action": "create",
                "object_type": "Import",
                "object_id": batch.id,
                "object_repr": batch.filename,
                "changes": [
                    {"field": "committed", "before": None, "after": result["counts"]}
                ],
            }
        ],
    )
    return result
