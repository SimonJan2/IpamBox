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
    destroy_session,
    env_password,
    get_session_user_id,
    hash_password,
    is_locked_out,
    record_login_failure,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import AuthStatus, LoginBody, SetupBody

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


def _set_session_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=settings.ipambox_session_hours * 3600,
        httponly=True,
        samesite="lax",
        secure=settings.ipambox_cookie_secure,
        path="/",
    )


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
    body: SetupBody, response: Response, session: AsyncSession = Depends(get_session)
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
    token = await create_session(user.id)
    _set_session_cookie(response, token)
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
    token = await create_session(user.id)
    _set_session_cookie(response, token)
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
