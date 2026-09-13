from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_session
from app.core.deps import require_auth
from app.core.security import (
    SESSION_COOKIE,
    clear_login_failures,
    create_session,
    destroy_other_sessions,
    destroy_session,
    destroy_session_by_suffix,
    env_password,
    get_session_user_id,
    hash_password,
    is_locked_out,
    list_sessions,
    record_login_failure,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import AuthStatus, LoginBody, SetupBody
from app.schemas.settings import ChangePasswordBody, SessionOut
from app.services import runtime_settings

router = APIRouter(prefix="/auth", tags=["auth"])


async def _current_user(request: Request, session: AsyncSession) -> User | None:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    user_id = await get_session_user_id(token)
    if user_id is None:
        return None
    return await session.get(User, user_id)


async def ensure_env_password_user(session: AsyncSession) -> None:
    """Create the admin user from IPAMBOX_PASSWORD(_FILE) if none exists yet."""
    pw = env_password()
    if not pw:
        return
    if await session.scalar(select(func.count(User.id))):
        return
    session.add(User(username="admin", password_hash=hash_password(pw)))
    await session.commit()


def _set_session_cookie(response: Response, token: str, hours: int) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=hours * 3600,
        httponly=True,
        samesite="lax",
        secure=get_settings().ipambox_cookie_secure,
        path="/",
    )


async def _login_session(
    session: AsyncSession, request: Request, response: Response, user_id: int
) -> None:
    """Create a Redis session + cookie honoring the effective session TTL."""
    eff = await runtime_settings.get_effective(session)
    token = await create_session(
        user_id,
        ttl_hours=eff.values["ipambox_session_hours"],
        ip=request.client.host if request.client else "",
        ua=request.headers.get("user-agent", ""),
    )
    _set_session_cookie(response, token, eff.values["ipambox_session_hours"])


@router.get("/status", response_model=AuthStatus)
async def auth_status(request: Request, session: AsyncSession = Depends(get_session)):
    settings = get_settings()
    if settings.ipambox_allow_insecure:
        return AuthStatus(initialized=True, authenticated=True, allow_insecure=True)
    await ensure_env_password_user(session)
    initialized = bool(await session.scalar(select(func.count(User.id))))
    user = await _current_user(request, session)
    return AuthStatus(
        initialized=initialized,
        authenticated=user is not None,
        allow_insecure=False,
        username=user.username if user else None,
    )


@router.post("/setup", status_code=201)
async def setup(
    body: SetupBody,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
):
    """First-run password creation. Refused once any user exists."""
    await ensure_env_password_user(session)
    if await session.scalar(select(func.count(User.id))):
        raise HTTPException(409, "already initialized")
    user = User(
        username=body.username.strip(), password_hash=hash_password(body.password)
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    await _login_session(session, request, response, user.id)
    return {"ok": True, "username": user.username}


@router.post("/login")
async def login(
    body: LoginBody,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
):
    if get_settings().ipambox_allow_insecure:
        return {"ok": True, "username": None}
    await ensure_env_password_user(session)
    ip = request.client.host if request.client else "unknown"
    if await is_locked_out(ip):
        raise HTTPException(429, "too many failed attempts — try again later")
    user = (
        await session.execute(select(User).where(User.username == body.username))
    ).scalar_one_or_none()
    if user is None or not verify_password(body.password, user.password_hash):
        if await record_login_failure(ip):
            raise HTTPException(429, "too many failed attempts — try again later")
        raise HTTPException(401, "invalid credentials")
    await clear_login_failures(ip)
    await _login_session(session, request, response, user.id)
    return {"ok": True, "username": user.username}


@router.post("/logout")
async def logout(request: Request, response: Response):
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        await destroy_session(token)
    response.delete_cookie(SESSION_COOKIE, path="/")
    return {"ok": True}


@router.get("/me")
async def me(user: User | None = Depends(require_auth)):
    return {"username": user.username if user else None}


@router.post("/change-password")
async def change_password(
    body: ChangePasswordBody,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(require_auth),
):
    if user is None:
        raise HTTPException(400, "auth is disabled — nothing to change")
    if not verify_password(body.current_password, user.password_hash):
        raise HTTPException(403, "current password is incorrect")
    if not 8 <= len(body.new_password) <= 256:
        raise HTTPException(422, "new password must be 8-256 characters")
    user.password_hash = hash_password(body.new_password)
    await session.commit()
    revoked = 0
    if body.logout_others:
        token = request.cookies.get(SESSION_COOKIE)
        revoked = await destroy_other_sessions(user.id, token)
    return {"ok": True, "revoked_sessions": revoked}


@router.get("/sessions", response_model=list[SessionOut])
async def sessions(
    request: Request, user: User | None = Depends(require_auth)
):
    if user is None:
        return []
    return await list_sessions(user.id, request.cookies.get(SESSION_COOKIE))


@router.delete("/sessions/{session_id}", status_code=204)
async def revoke_session(
    session_id: str,
    request: Request,
    user: User | None = Depends(require_auth),
):
    if user is None:
        raise HTTPException(400, "auth is disabled")
    current = request.cookies.get(SESSION_COOKIE)
    if current and current.endswith(session_id):
        raise HTTPException(409, "cannot revoke the current session — log out instead")
    if not await destroy_session_by_suffix(user.id, session_id):
        raise HTTPException(404, "session not found")


@router.post("/sessions/revoke-others")
async def revoke_other_sessions(
    request: Request, user: User | None = Depends(require_auth)
):
    if user is None:
        raise HTTPException(400, "auth is disabled")
    removed = await destroy_other_sessions(
        user.id, request.cookies.get(SESSION_COOKIE)
    )
    return {"ok": True, "revoked_sessions": removed}
