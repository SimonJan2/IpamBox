"""Cross-object search for the command palette.

One GET returns grouped matches across every searchable family, capped per
group. Matching reuses the Hebrew-aware folding from the per-family `q`
params: both sides are translate()d so final letters (םןץףך) equal their base
forms, and ilike handles case.

When `q` parses as an IP address the response additionally carries `jump`:
the deepest prefix containing it — the UI offers "jump to address".
"""

import ipaddress

from fastapi import APIRouter, Depends, Query
from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import DATA_READ, require_perm
from app.models.asset import Asset
from app.models.certificate import Certificate
from app.models.circuit import Circuit
from app.models.custom_list import CustomList, CustomListRow
from app.models.ip_address import IPAddress
from app.models.prefix import Prefix
from app.models.rack import Rack, RackDevice
from app.models.service import Service
from app.models.site import Site
from app.models.vlan import VLAN
from app.models.vrf import VRF
from app.schemas.search import (
    SearchAddress,
    SearchAsset,
    SearchCertificate,
    SearchCircuit,
    SearchJump,
    SearchList,
    SearchListRow,
    SearchOut,
    SearchPrefix,
    SearchRack,
    SearchService,
    SearchSite,
    SearchVlan,
    SearchVrf,
)
from app.services import prefix_math
from app.services.workbook.normalize import fold_hebrew

router = APIRouter(prefix="/search", tags=["search"])

PER_GROUP = 8

_HE_FINALS = "םןץףך"
_HE_BASE = "מנצפכ"


def _folded(col):
    """Column expression with Hebrew final letters folded — pairs with
    fold_hebrew() applied to the query string."""
    return func.translate(cast(col, String), _HE_FINALS, _HE_BASE)


def _row_label(row: CustomListRow, lst: CustomList) -> str:
    """Short label for a list-row search hit: key-column value, else the
    first non-empty cell in column order."""
    data = row.data or {}
    if lst.key_column and data.get(lst.key_column):
        return str(data[lst.key_column])
    for c in lst.columns or []:
        v = data.get(c.get("key"))
        if v not in (None, ""):
            return str(v)
    return f"row {row.id}"


@router.get("", response_model=SearchOut)
async def search(
    q: str = Query(default="", max_length=200),
    session: AsyncSession = Depends(get_session),
    _user=Depends(require_perm(DATA_READ)),
):
    empty = SearchOut(
        addresses=[], prefixes=[], sites=[], vrfs=[], vlans=[],
        circuits=[], certificates=[], assets=[], services=[],
        lists=[], list_rows=[], racks=[], jump=None,
    )
    q = q.strip()
    if not q:
        return empty

    needle = f"%{fold_hebrew(q)}%"

    def match(*cols):
        return or_(*(_folded(c).ilike(needle) for c in cols))

    async def take(stmt):
        return (await session.execute(stmt.limit(PER_GROUP))).scalars().all()

    async def take_rows(stmt):
        return (await session.execute(stmt.limit(PER_GROUP))).all()

    addresses = await take(
        select(IPAddress).where(
            match(
                IPAddress.address,
                IPAddress.hostname,
                IPAddress.mac_address,
                IPAddress.vendor,
                IPAddress.serial_number,
                IPAddress.switch_name,
            )
        ).order_by(IPAddress.address_int)
    )
    prefixes = await take(
        select(Prefix)
        .where(match(Prefix.prefix, Prefix.description))
        .order_by(Prefix.id)
    )
    sites = await take(
        select(Site)
        .where(match(Site.name, Site.code, Site.site_number, Site.description))
        .order_by(Site.name)
    )
    vrfs = await take(
        select(VRF).where(match(VRF.name, VRF.rd, VRF.description)).order_by(VRF.name)
    )
    vlans = await take(
        select(VLAN).where(match(VLAN.name, VLAN.vid, VLAN.description)).order_by(VLAN.vid)
    )
    circuits = await take(
        select(Circuit)
        .where(
            match(
                Circuit.site_name,
                Circuit.site_code,
                Circuit.bezeq_circuit_id,
                Circuit.node,
                Circuit.app_client_name,
                Circuit.line_type,
                Circuit.wan_ip,
            )
        )
        .order_by(Circuit.id)
    )
    certificates = await take(
        select(Certificate)
        .where(
            match(
                Certificate.platform,
                Certificate.target,
                Certificate.server_name,
                Certificate.cert_name,
                Certificate.serial_raw,
            )
        )
        .order_by(Certificate.id)
    )
    assets = await take(
        select(Asset)
        .where(
            match(
                Asset.category,
                Asset.vendor,
                Asset.model,
                Asset.purpose,
                Asset.serial_number,
            )
        )
        .order_by(Asset.id)
    )
    services = await take(
        select(Service)
        .where(match(Service.name, Service.beneficiary, Service.site_code))
        .order_by(Service.id)
    )
    lists = await take(
        select(CustomList)
        .where(match(CustomList.name, CustomList.description))
        .order_by(CustomList.id)
    )
    # rack names/rooms, plus racks containing a matching device name
    racks = await take(
        select(Rack)
        .where(
            or_(
                match(Rack.name, Rack.room),
                Rack.id.in_(
                    select(RackDevice.rack_id).where(
                        match(RackDevice.name, RackDevice.model)
                    )
                ),
            )
        )
        .order_by(Rack.name)
    )
    # row search: jsonb::text match across all cells, joined to its list
    list_row_hits = await take_rows(
        select(CustomListRow, CustomList)
        .join(CustomList, CustomListRow.list_id == CustomList.id)
        .where(match(CustomListRow.data))
        .order_by(CustomListRow.id)
    )

    # "what is 10.20.3.44?" -> jump straight to the prefix holding it.
    jump = None
    try:
        ip = ipaddress.ip_address(q)
    except ValueError:
        ip = None
    if ip is not None:
        all_prefixes = prefixes
        if len(all_prefixes) < PER_GROUP:
            # the LIKE query may have capped/missed — containment needs them all
            all_prefixes = (await session.execute(select(Prefix))).scalars().all()
        containing = []
        for p in all_prefixes:
            net = prefix_math.to_network(p.prefix)
            if net.version == ip.version and ip in net:
                containing.append((p, net))
        if containing:
            existing = set(
                (
                    await session.execute(
                        select(IPAddress.prefix_id).where(
                            IPAddress.address_int == int(ip)
                        )
                    )
                ).scalars().all()
            )
            # deepest first; prefer the prefix that actually owns the address
            containing.sort(key=lambda t: t[1].prefixlen, reverse=True)
            best = next(
                (p for p, _ in containing if p.id in existing),
                containing[0][0],
            )
            jump = SearchJump(
                address=str(ip),
                prefix_id=best.id,
                prefix=str(prefix_math.to_network(best.prefix)),
                exists=best.id in existing,
            )

    return SearchOut(
        addresses=[
            SearchAddress(
                id=a.id,
                address=str(a.address),
                hostname=a.hostname,
                prefix_id=a.prefix_id,
                status=a.status.value,
            )
            for a in addresses
        ],
        prefixes=[
            SearchPrefix(
                id=p.id,
                prefix=str(prefix_math.to_network(p.prefix)),
                description=p.description,
                vrf_id=p.vrf_id,
                site_id=p.site_id,
            )
            for p in prefixes
        ],
        sites=[
            SearchSite(id=s.id, name=s.name, code=s.code, site_number=s.site_number)
            for s in sites
        ],
        vrfs=[
            SearchVrf(id=v.id, name=v.name, rd=v.rd, site_id=v.site_id)
            for v in vrfs
        ],
        vlans=[SearchVlan(id=v.id, vid=v.vid, name=v.name) for v in vlans],
        circuits=[
            SearchCircuit(
                id=c.id,
                site_name=c.site_name,
                site_code=c.site_code,
                bezeq_circuit_id=c.bezeq_circuit_id,
                line_type=c.line_type,
                app_client_name=c.app_client_name,
            )
            for c in circuits
        ],
        certificates=[
            SearchCertificate(
                id=c.id,
                cert_name=c.cert_name,
                server_name=c.server_name,
                platform=c.platform,
                expires_on=c.expires_on,
            )
            for c in certificates
        ],
        assets=[
            SearchAsset(
                id=a.id,
                kind=a.kind.value,
                vendor=a.vendor,
                model=a.model,
                serial_number=a.serial_number,
                category=a.category,
            )
            for a in assets
        ],
        services=[
            SearchService(
                id=s.id, name=s.name, beneficiary=s.beneficiary, site_code=s.site_code
            )
            for s in services
        ],
        lists=[
            SearchList(id=l.id, name=l.name, slug=l.slug, description=l.description)
            for l in lists
        ],
        list_rows=[
            SearchListRow(
                id=r.id,
                list_id=r.list_id,
                list_slug=l.slug,
                list_name=l.name,
                label=_row_label(r, l),
            )
            for r, l in list_row_hits
        ],
        racks=[
            SearchRack(id=r.id, name=r.name, room=r.room, site_id=r.site_id)
            for r in racks
        ],
        jump=jump,
    )
