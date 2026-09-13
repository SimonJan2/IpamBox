import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy import func, select, text

from app.api.v1 import auth
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.db import SessionLocal
from app.core.deps import require_auth
from app.core.redis import get_redis
from app.models.ip_address import IPAddress
from app.models.ip_range import IPRange
from app.models.prefix import Prefix
from app.models.scan_job import ScanJob, ScanStatus
from app.models.site import Site
from app.models.tag import Tag
from app.models.user import User
from app.models.vlan import VLAN
from app.models.vrf import VRF

logger = logging.getLogger(__name__)
settings = get_settings()

APP_VERSION = "0.2.0"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if settings.ipambox_allow_insecure:
        logger.warning(
            "IPAMBOX_ALLOW_INSECURE is on — the API is unauthenticated. "
            "Only use this behind a trusted reverse proxy."
        )
    else:
        async with SessionLocal() as s:
            await auth.ensure_env_password_user(s)
    yield


app = FastAPI(title="IpamBox", version=APP_VERSION, docs_url="/docs", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# /auth/* stays open (it gates itself); everything else requires a session.
app.include_router(auth.router, prefix="/api/v1")
app.include_router(
    api_router, prefix="/api/v1", dependencies=[Depends(require_auth)]
)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok", "version": APP_VERSION}


@app.get("/readyz")
async def readyz() -> JSONResponse:
    """Readiness probe: verifies DB + Redis connectivity."""
    errors: dict[str, str] = {}
    try:
        async with SessionLocal() as s:
            await s.execute(text("SELECT 1"))
    except Exception as e:  # noqa: BLE001 — readiness reports, not raises
        errors["db"] = str(e)[:200]
    try:
        r = get_redis()
        try:
            await r.ping()
        finally:
            await r.aclose()
    except Exception as e:  # noqa: BLE001
        errors["redis"] = str(e)[:200]
    if errors:
        return JSONResponse({"status": "not_ready", **errors}, status_code=503)
    return JSONResponse({"status": "ready", "version": APP_VERSION})


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics() -> str:
    """Prometheus-style text exposition of object + scan counters."""
    async with SessionLocal() as s:
        sites = await s.scalar(select(func.count(Site.id)))
        vrfs = await s.scalar(select(func.count(VRF.id)))
        prefixes = await s.scalar(select(func.count(Prefix.id)))
        vlans = await s.scalar(select(func.count(VLAN.id)))
        tags = await s.scalar(select(func.count(Tag.id)))
        ranges = await s.scalar(select(func.count(IPRange.id)))
        users = await s.scalar(select(func.count(User.id)))
        addr_by_status = (
            await s.execute(
                select(IPAddress.status, func.count()).group_by(IPAddress.status)
            )
        ).all()
        scan_by_status = (
            await s.execute(
                select(ScanJob.status, func.count()).group_by(ScanJob.status)
            )
        ).all()

    lines = [
        "# HELP ipambox_info Build/version info",
        "# TYPE ipambox_info gauge",
        f'ipambox_info{{version="{APP_VERSION}"}} 1',
        f"ipambox_sites_total {sites or 0}",
        f"ipambox_vrfs_total {vrfs or 0}",
        f"ipambox_prefixes_total {prefixes or 0}",
        f"ipambox_vlans_total {vlans or 0}",
        f"ipambox_tags_total {tags or 0}",
        f"ipambox_ip_ranges_total {ranges or 0}",
        f"ipambox_users_total {users or 0}",
        "# TYPE ipambox_addresses_total gauge",
    ]
    for status, n in addr_by_status:
        lines.append(f'ipambox_addresses_total{{status="{status.value}"}} {n}')
    lines.append("# TYPE ipambox_scans_total gauge")
    for status, n in scan_by_status:
        lines.append(f'ipambox_scans_total{{status="{status.value}"}} {n}')
    for st in ScanStatus:  # always emit all scan statuses (prom prefers stable series)
        if all(s != st for s, _ in scan_by_status):
            lines.append(f'ipambox_scans_total{{status="{st.value}"}} 0')
    return "\n".join(lines) + "\n"
