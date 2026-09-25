"""POST /networks — the "add network" wizard endpoint (V6.1).

One call creates or reuses the VLAN, creates the prefix, mirrors gateway/DNS
into protected technical address rows, and defines the DHCP pool — all in a
single transaction. Any failure rolls back everything: a half-built network
is worse than none.
"""
import ipaddress

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import DATA_WRITE, require_perm
from app.models.ip_address import IPAddress
from app.models.ip_range import IPRange, IPRangeRole
from app.models.prefix import Prefix, PrefixStatus
from app.models.site import Site
from app.models.vlan import VLAN, VLANGroup
from app.models.vrf import VRF
from app.schemas.network import NetworkCreate, NetworkOut
from app.services import prefix_math
from app.services.ipam import ConflictError, IPAMError, check_overlap, get_or_404
from app.services.ranges import sync_technical_addresses

router = APIRouter(prefix="/networks", tags=["networks"])


@router.post(
    "",
    response_model=NetworkOut,
    status_code=201,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def create_network(body: NetworkCreate, session: AsyncSession = Depends(get_session)):
    net = prefix_math.to_network(body.prefix.cidr)
    try:
        # -- VLAN: reuse an existing row or create one ----------------------
        if body.vlan_id is not None:
            vlan = await get_or_404(session, VLAN, body.vlan_id)
        else:
            spec = body.vlan
            if spec.group_id is not None:
                await get_or_404(session, VLANGroup, spec.group_id)
            stmt = select(VLAN).where(VLAN.vid == spec.vid)
            stmt = stmt.where(
                VLAN.group_id.is_(None)
                if spec.group_id is None
                else VLAN.group_id == spec.group_id
            )
            vlan = (await session.execute(stmt)).scalars().first()
            if vlan is None:
                vlan = VLAN(
                    vid=spec.vid,
                    name=spec.name,
                    group_id=spec.group_id,
                    site_id=body.site_id,
                )
                session.add(vlan)
                await session.flush()
        if body.site_id is not None:
            await get_or_404(session, Site, body.site_id)
        await get_or_404(session, VRF, body.prefix.vrf_id)

        # -- prefix ----------------------------------------------------------
        if body.prefix.status != PrefixStatus.CONTAINER:
            conflict = await check_overlap(session, net, body.prefix.vrf_id)
            if conflict is not None:
                raise ConflictError(
                    f"{net} overlaps existing prefix {conflict.prefix} "
                    f"(id={conflict.id}) in this VRF",
                )
        if body.gateway is not None:
            gw = ipaddress.ip_address(body.gateway)
            if gw.version != net.version or gw not in net:
                raise HTTPException(
                    422, f"gateway {gw} is not inside prefix {net}"
                )
        prefix = Prefix(
            prefix=str(net),
            vrf_id=body.prefix.vrf_id,
            site_id=body.site_id,
            vlan_id=vlan.id,
            status=body.prefix.status,
            description=body.prefix.description,
            gateway=body.gateway,
            dns_servers=body.dns_servers,
        )
        session.add(prefix)
        await session.flush()

        # -- protected technical addresses (gateway + resolvers) -------------
        await sync_technical_addresses(session, prefix)
        await session.flush()
        tech_ids = [
            r[0]
            for r in (
                await session.execute(
                    select(IPAddress.id).where(
                        IPAddress.prefix_id == prefix.id,
                        IPAddress.custom_fields.has_key("technical"),  # noqa: W601
                    )
                )
            ).all()
        ]

        # -- DHCP pool --------------------------------------------------------
        range_id = None
        if body.dhcp_range is not None:
            start = ipaddress.ip_address(body.dhcp_range.start)
            end = ipaddress.ip_address(body.dhcp_range.end)
            if start.version != net.version or end.version != net.version:
                raise HTTPException(
                    422, "dhcp_range family does not match prefix"
                )
            if start not in net or end not in net:
                raise HTTPException(422, f"dhcp_range must fit inside {net}")
            rng = IPRange(
                prefix_id=prefix.id,
                vrf_id=prefix.vrf_id,
                start_address=str(start),
                start_int=int(start),
                end_address=str(end),
                end_int=int(end),
                role=IPRangeRole.DHCP,
                description=body.dhcp_range.description,
            )
            session.add(rng)
            await session.flush()
            range_id = rng.id
            # Link the technical rows the range happens to cover — same
            # informational retro-link as POST /ranges.
            for addr in (
                await session.execute(
                    select(IPAddress).where(
                        IPAddress.prefix_id == prefix.id,
                        IPAddress.address_int.between(int(start), int(end)),
                    )
                )
            ).scalars():
                addr.ip_range_id = rng.id

        await session.commit()
    except IPAMError as e:
        await session.rollback()
        raise HTTPException(e.status_code, str(e))
    except IntegrityError as e:
        await session.rollback()
        if "excl_prefixes_no_overlap" in str(e):
            raise HTTPException(409, f"{net} overlaps an existing prefix in this VRF")
        raise HTTPException(400, "invalid network data")
    except Exception:
        await session.rollback()
        raise
    return NetworkOut(
        vlan_id=vlan.id,
        prefix_id=prefix.id,
        ip_range_id=range_id,
        address_ids=tech_ids,
    )
