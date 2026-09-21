import ipaddress
import json
import secrets
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import bcrypt

from app.core.config import get_settings
from app.core.redis import get_redis

SESSION_COOKIE = "ipambox_session"
_LOCKOUT_AFTER = 5      # per (username, ip) pair
_LOCKOUT_IP_AFTER = 20  # per-IP aggregate — credential-stuffing backstop
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


def _uname(username: str) -> str:
    """Normalize a username for counter keys (case-folded, key-safe)."""
    return username.strip().lower().replace(":", "_")[:64]


def _fails_key(username: str, ip: str) -> str:
    return f"ipam:loginfails:{_uname(username)}:{ip}"


def _ip_fails_key(ip: str) -> str:
    return f"ipam:loginfails_ip:{ip}"


def _lock_key(username: str, ip: str) -> str:
    return f"ipam:lockout:{_uname(username)}:{ip}"


def _ip_lock_key(ip: str) -> str:
    return f"ipam:lockout_ip:{ip}"


def _trusted_nets() -> list:
    nets = []
    for part in get_settings().ipambox_trusted_proxies.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            nets.append(ipaddress.ip_network(part, strict=False))
        except ValueError:
            continue
    return nets


def _in_trusted(host: str, nets) -> bool:
    try:
        addr = ipaddress.ip_address(host.split("%")[0])
    except ValueError:
        return False
    return any(addr in n for n in nets)


def client_ip(request) -> str:
    """Resolve the real client IP for lockout keying/session metadata.

    X-Forwarded-For is honored only when the socket peer itself sits inside
    ipambox_trusted_proxies — otherwise the header is client-controlled and
    would let an attacker rotate IPs to dodge (or trigger) lockouts. The
    chain is walked right-to-left, skipping trusted hops, matching how
    uvicorn's --proxy-headers resolves it.
    """
    peer = request.client.host if request.client else "unknown"
    nets = _trusted_nets()
    if not nets or not _in_trusted(peer, nets):
        return peer
    hops = [
        h.strip()
        for h in request.headers.get("x-forwarded-for", "").split(",")
        if h.strip()
    ]
    for hop in reversed(hops):
        if not _in_trusted(hop, nets):
            return hop
    return peer


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
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "ip": ip,
        "ua": ua[:200],
    }
    r = get_redis()
    await r.set(_session_key(token), json.dumps(meta), ex=hours * 3600)
    return token


async def get_session_user_id(token: str) -> int | None:
    r = get_redis()
    meta = _session_meta(await r.get(_session_key(token)))
    return int(meta["user_id"]) if meta else None


async def destroy_session(token: str) -> None:
    await get_redis().delete(_session_key(token))


async def list_sessions(user_id: int, current_token: str | None) -> list[dict]:
    """All live sessions for a user; tokens surface only as an 8-char suffix."""
    r = get_redis()
    out: list[dict] = []
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
    out.sort(key=lambda s: (not s["current"], s["created_at"] or ""))
    return out


async def destroy_session_by_suffix(user_id: int, suffix: str) -> bool:
    """Revoke one of the user's sessions identified by its token suffix."""
    r = get_redis()
    async for key in r.scan_iter(f"{_SESSION_PREFIX}*"):
        token = key[len(_SESSION_PREFIX) :]
        if not token.endswith(suffix):
            continue
        meta = _session_meta(await r.get(key))
        if meta and int(meta["user_id"]) == user_id:
            await r.delete(key)
            return True
    return False


async def destroy_user_sessions(user_id: int) -> int:
    return await destroy_other_sessions(user_id, keep_token=None)


async def destroy_other_sessions(user_id: int, keep_token: str | None) -> int:
    """Revoke every session of the user except keep_token. Returns count."""
    r = get_redis()
    removed = 0
    async for key in r.scan_iter(f"{_SESSION_PREFIX}*"):
        token = key[len(_SESSION_PREFIX) :]
        if token == keep_token:
            continue
        meta = _session_meta(await r.get(key))
        if meta and int(meta["user_id"]) == user_id:
            removed += await r.delete(key)
    return removed


async def is_locked_out(username: str, ip: str) -> bool:
    """True when either the (username, ip) pair or the whole IP is locked.

    The per-IP aggregate is a credential-stuffing backstop: rotating through
    usernames still trips it, while one locked pair never silences others.
    """
    r = get_redis()
    hits = await r.mget(_lock_key(username, ip), _ip_lock_key(ip))
    return any(h is not None for h in hits)


async def record_login_failure(username: str, ip: str) -> bool:
    """Bump (username, ip) + per-IP counters; True once either locks out."""
    r = get_redis()
    n = await r.incr(_fails_key(username, ip))
    await r.expire(_fails_key(username, ip), _LOCKOUT_SECONDS)
    m = await r.incr(_ip_fails_key(ip))
    await r.expire(_ip_fails_key(ip), _LOCKOUT_SECONDS)
    locked = False
    if n >= _LOCKOUT_AFTER:
        await r.set(_lock_key(username, ip), "1", ex=_LOCKOUT_SECONDS)
        locked = True
    if m >= _LOCKOUT_IP_AFTER:
        await r.set(_ip_lock_key(ip), "1", ex=_LOCKOUT_SECONDS)
        locked = True
    return locked


async def clear_login_failures(username: str, ip: str) -> None:
    """Successful login clears the (username, ip) pair only — the per-IP
    aggregate keeps its TTL so valid logins can't reset a stuffing attack."""
    await get_redis().delete(_fails_key(username, ip), _lock_key(username, ip))
