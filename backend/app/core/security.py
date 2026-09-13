import secrets
from contextvars import ContextVar
from pathlib import Path

import bcrypt

from app.core.config import get_settings
from app.core.redis import get_redis

SESSION_COOKIE = "ipambox_session"
_LOCKOUT_AFTER = 5
_LOCKOUT_SECONDS = 900  # 15 minutes

# Who is making changes — set per-request by require_auth, "scanner" in the
# worker. The changelog hook (app.core.changelog) reads it.
_current_actor: ContextVar[str] = ContextVar("ipambox_actor", default="system")


def set_actor(name: str) -> None:
    _current_actor.set(name)


def get_actor() -> str:
    return _current_actor.get()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except ValueError:
        return False


def env_password() -> str | None:
    """Password provisioned via IPAMBOX_PASSWORD_FILE / IPAMBOX_PASSWORD."""
    settings = get_settings()
    if settings.ipambox_password_file:
        try:
            pw = Path(settings.ipambox_password_file).read_text().strip()
            if pw:
                return pw
        except OSError:
            pass
    return settings.ipambox_password or None


def _session_key(token: str) -> str:
    return f"ipam:session:{token}"


def _fails_key(ip: str) -> str:
    return f"ipam:loginfails:{ip}"


def _lock_key(ip: str) -> str:
    return f"ipam:lockout:{ip}"


async def create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    r = get_redis()
    try:
        ttl = get_settings().ipambox_session_hours * 3600
        await r.set(_session_key(token), str(user_id), ex=ttl)
    finally:
        await r.aclose()
    return token


async def get_session_user_id(token: str) -> int | None:
    r = get_redis()
    try:
        value = await r.get(_session_key(token))
        return int(value) if value else None
    finally:
        await r.aclose()


async def destroy_session(token: str) -> None:
    r = get_redis()
    try:
        await r.delete(_session_key(token))
    finally:
        await r.aclose()


async def is_locked_out(ip: str) -> bool:
    r = get_redis()
    try:
        return await r.get(_lock_key(ip)) is not None
    finally:
        await r.aclose()


async def record_login_failure(ip: str) -> bool:
    """Bump the failure counter; returns True once the IP is locked out."""
    r = get_redis()
    try:
        n = await r.incr(_fails_key(ip))
        await r.expire(_fails_key(ip), _LOCKOUT_SECONDS)
        if n >= _LOCKOUT_AFTER:
            await r.set(_lock_key(ip), "1", ex=_LOCKOUT_SECONDS)
            return True
        return False
    finally:
        await r.aclose()


async def clear_login_failures(ip: str) -> None:
    r = get_redis()
    try:
        await r.delete(_fails_key(ip), _lock_key(ip))
    finally:
        await r.aclose()
