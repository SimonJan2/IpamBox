from fastapi import APIRouter

from app.api.v1 import (
    addresses,
    changelog,
    dashboard,
    discovery,
    prefixes,
    scans,
    sites,
    vrfs,
)

api_router = APIRouter()
api_router.include_router(sites.router)
api_router.include_router(vrfs.router)
api_router.include_router(prefixes.router)
api_router.include_router(addresses.router)
api_router.include_router(scans.router)
api_router.include_router(dashboard.router)
api_router.include_router(discovery.router)
api_router.include_router(changelog.router)
