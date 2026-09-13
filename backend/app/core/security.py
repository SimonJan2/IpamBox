import json
import secrets
from contextvars import ContextVar
from datetime import datetime
from pathlib import Path
from typing import Any

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


_SESSION_PREFIX = "ipam:session:"


def _session_key(token: str) -> str:
    return f"{_SESSION_PREFIX}{token}"


def _fails_key(ip: str) -> str:
    return f"ipam:loginfails:{ip}"


def _lock_key(ip: str) -> str:
    return f"ipam:lockout:{ip}"


def _session_meta(raw: str | None) -> dict[str, Any] | None:
    """Parse a session value: JSON metadata, or legacy bare user_id."""
    if raw is None:
        return None
    if raw.isdigit():
        return {"user_id": int(raw)}
    try:
        meta = json.loads(raw)
        return meta if isinstance(meta, dict) and "user_id" in meta else None
    except (ValueError, AttributeError):
        return None


async def create_session(
    user_id: int, ttl_hours: int | None = None, ip: str = "", ua: str = ""
) -> str:
    token = secrets.token_urlsafe(32)
    hours = ttl_hours if ttl_hours is not None else get_settings().ipambox_session_hours
    meta = {
        "user_id": user_id,
        "created_at": datetime.utcnow().isoformat(timespec="seconds"),
        "ip": ip,
        "ua": ua[:200],
    }
    r = get_redis()
    try:
        await r.set(_session_key(token), json.dumps(meta), ex=hours * 3600)
    finally:
        await r.aclose()
    return token


async def get_session_user_id(token: str) -> int | None:
    r = get_redis()
    try:
        meta = _session_meta(await r.get(_session_key(token)))
        return int(meta["user_id"]) if meta else None
    finally:
        await r.aclose()


async def destroy_session(token: str) -> None:
    r = get_redis()
    try:
        await r.delete(_session_key(token))
    finally:
        await r.aclose()


async def list_sessions(user_id: int, current_token: str | None) -> list[dict]:
    """All live sessions for a user; tokens surface only as an 8-char suffix."""
    r = get_redis()
    out: list[dict] = []
    try:
        async for key in r.scan_iter(f"{_SESSION_PREFIX}*"):
            token = key[len(_SESSION_PREFIX) :]
            meta = _session_meta(await r.get(key))
            if not meta or int(meta["user_id"]) != user_id:
                continue
            out.append(
                {
                    "id": token[-8:],
                    "created_at": meta.get("created_at"),
                    "ip": meta.get("ip") or None,
                    "ua": meta.get("ua") or None,
                    "expires_in": await r.ttl(key),
                    "current": token == current_token,
                }
            )
    finally:
        await r.aclose()
    out.sort(key=lambda s: (not s["current"], s["created_at"] or ""))
    return out


async def destroy_session_by_suffix(user_id: int, suffix: str) -> bool:
    """Revoke one of the user's sessions identified by its token suffix."""
    r = get_redis()
    try:
        async for key in r.scan_iter(f"{_SESSION_PREFIX}*"):
            token = key[len(_SESSION_PREFIX) :]
            if not token.endswith(suffix):
                continue
            meta = _session_meta(await r.get(key))
            if meta and int(meta["user_id"]) == user_id:
                await r.delete(key)
                return True
        return False
    finally:
        await r.aclose()


async def destroy_user_sessions(user_id: int) -> int:
    return await destroy_other_sessions(user_id, keep_token=None)


async def destroy_other_sessions(user_id: int, keep_token: str | None) -> int:
    """Revoke every session of the user except keep_token. Returns count."""
    r = get_redis()
    removed = 0
    try:
        async for key in r.scan_iter(f"{_SESSION_PREFIX}*"):
            token = key[len(_SESSION_PREFIX) :]
            if token == keep_token:
                continue
            meta = _session_meta(await r.get(key))
            if meta and int(meta["user_id"]) == user_id:
                removed += await r.delete(key)
    finally:
        await r.aclose()
    return removed


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
