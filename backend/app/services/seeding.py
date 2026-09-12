"""Seed sample data: a Site, the Global VRF, and the auto-detected LAN prefix.

Run inside the scanner container (host networking -> can detect the LAN):

    docker compose exec scanner python -m app.services.seeding
"""

import asyncio
import ipaddress
import logging

from sqlalchemy import select

from app.core.config import get_settings
from app.core.db import SessionLocal
from app.models.prefix import Prefix, PrefixStatus
from app.models.site import Site
from app.models.vrf import VRF
from app.services import prefix_math
from app.services.ipam import slugify
from app.worker.scanner import detect_local_cidr

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("seed")


async def main() -> None:
    settings = get_settings()
    async with SessionLocal() as session:
        site = (
            await session.execute(select(Site).where(Site.slug == "home"))
        ).scalar_one_or_none()
        if site is None:
            site = Site(name="Home", slug=slugify("Home"), description="Home LAN")
            session.add(site)
            await session.flush()
            log.info("created site Home")

        vrf = (
            await session.execute(select(VRF).where(VRF.name == "Global"))
        ).scalar_one_or_none()
        if vrf is None:
            vrf = VRF(name="Global", description="Default global routing table")
            session.add(vrf)
            await session.flush()
            log.info("created Global VRF")
        if vrf.site_id is None:
            vrf.site_id = site.id

        cidr = detect_local_cidr(settings.scan_interface)
        if not cidr:
            log.warning("could not detect LAN CIDR — skipping prefix seed")
        else:
            net = ipaddress.ip_network(cidr, strict=False)
            existing = (
                await session.execute(select(Prefix).where(Prefix.vrf_id == vrf.id))
            ).scalars().all()
            match = next(
                (p for p in existing if prefix_math.to_network(p.prefix) == net), None
            )
            if match is None:
                prefix = Prefix(
                    prefix=str(net),
                    vrf_id=vrf.id,
                    site_id=site.id,
                    status=PrefixStatus.ACTIVE,
                    description="Local LAN (auto-detected)",
                )
                session.add(prefix)
                log.info("created prefix %s", net)
            else:
                if match.site_id is None:
                    match.site_id = site.id
                log.info("prefix %s already exists", net)

        await session.commit()
    log.info("seed complete")


if __name__ == "__main__":
    asyncio.run(main())
