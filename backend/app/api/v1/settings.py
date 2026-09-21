import json
import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_session
from app.core.deps import SYSTEM_ADMIN, require_perm
from app.core.redis import get_redis
from app.schemas.settings import LanInfo, SettingsOut, SettingsPatch, SystemInfo
from app.services import runtime_settings
from app.services.backup import _alembic_revisions
from app.services.runtime_settings import SettingsValidationError

router = APIRouter(prefix="/settings", tags=["settings"])

_LAN_KEY = "ipam:sys:lan"


def _mask_url(url: str) -> str:
    """Hide the password in a scheme://user:pass@host URL."""
    return re.sub(r"(://[^:]+:)[^@]+(@)", r"\1•••\2", url)


async def _lan_info() -> LanInfo:
    """LAN identity detected by the host-networked worker (written to Redis).

    Falls back to local detection — which inside the bridge-networked api
    container reports the container subnet, so it's flagged as such.
    """
    r = get_redis()  # shared client — never close per call
    raw = await r.get(_LAN_KEY)
    if raw:
        try:
            data = json.loads(raw)
            return LanInfo(iface=data.get("iface"), cidr=data.get("cidr"), source="worker")
        except (ValueError, AttributeError):
            pass
    from app.worker.scanner import detect_interface, detect_local_cidr

    iface = detect_interface(get_settings().scan_interface)
    return LanInfo(iface=iface, cidr=detect_local_cidr(iface or ""), source="local")


async def _build_out(session: AsyncSession) -> SettingsOut:
    from app.main import APP_VERSION

    eff = await runtime_settings.get_effective(session)
    env = get_settings()
    revisions = _alembic_revisions()
    return SettingsOut(
        values=eff.values,
        sources=eff.sources,
        env={
            "database_url": _mask_url(env.database_url),
            "redis_url": _mask_url(env.redis_url),
            "cors_origins": env.cors_origin_list,
            "ipambox_allow_insecure": env.ipambox_allow_insecure,
            "ipambox_cookie_secure": env.ipambox_cookie_secure,
            "ipambox_password_set": bool(env.ipambox_password or env.ipambox_password_file),
            "backup_dir": env.backup_dir,
        },
        system=SystemInfo(
            app_version=APP_VERSION,
            alembic_head=revisions[0] if revisions else None,
            lan=await _lan_info(),
        ),
    )


@router.get("", response_model=SettingsOut)
async def read_settings(session: AsyncSession = Depends(get_session)):
    return await _build_out(session)


@router.patch("", response_model=SettingsOut)
async def update_settings(
    body: SettingsPatch,
    session: AsyncSession = Depends(get_session),
    _user=Depends(require_perm(SYSTEM_ADMIN)),
):
    updates = body.model_dump(exclude_unset=True)
    try:
        await runtime_settings.patch(session, updates)
    except SettingsValidationError as e:
        raise HTTPException(422, detail=e.errors)
    await session.commit()
    return await _build_out(session)
