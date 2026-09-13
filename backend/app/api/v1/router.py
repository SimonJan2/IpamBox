from fastapi import APIRouter

from app.api.v1 import (
    addresses,
    backup,
    changelog,
    dashboard,
    discovery,
    maintenance,
    prefixes,
    ranges,
    scans,
    settings,
    sites,
    tags,
    users,
    vlans,
    vrfs,
)

api_router = APIRouter()
api_router.include_router(settings.router)
api_router.include_router(users.router)
api_router.include_router(maintenance.router)
api_router.include_router(backup.router)
api_router.include_router(sites.router)
api_router.include_router(vrfs.router)
api_router.include_router(prefixes.router)
api_router.include_router(addresses.router)
api_router.include_router(scans.router)
api_router.include_router(dashboard.router)
api_router.include_router(discovery.router)
api_router.include_router(changelog.router)
api_router.include_router(tags.router)
api_router.include_router(vlans.router)
api_router.include_router(ranges.router)
