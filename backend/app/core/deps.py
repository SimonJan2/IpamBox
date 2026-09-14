from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_session
from app.core.security import SESSION_COOKIE, get_session_user_id, set_actor
from app.models.user import User, UserRole

# Capability strings checked by require_perm(). Keep the matrix here so every
# router stays declarative and the frontend can mirror it via /auth/status.
DATA_READ = "data:read"
DATA_WRITE = "data:write"
DATA_DELETE = "data:delete"
BACKUP_ACCESS = "backup:access"
SYSTEM_ADMIN = "system:admin"
USERS_MANAGE = "users:manage"

ROLE_PERMISSIONS: dict[UserRole, frozenset[str]] = {
    UserRole.VIEWER: frozenset({DATA_READ}),
    UserRole.CONTRIBUTOR: frozenset({DATA_READ, DATA_WRITE}),
    UserRole.OPERATOR: frozenset(
        {DATA_READ, DATA_WRITE, DATA_DELETE, BACKUP_ACCESS}
    ),
    UserRole.ADMIN: frozenset(
        {
            DATA_READ,
            DATA_WRITE,
            DATA_DELETE,
            BACKUP_ACCESS,
            SYSTEM_ADMIN,
            USERS_MANAGE,
        }
    ),
}


def user_permissions(user: User | None) -> frozenset[str]:
    """Effective permission set; insecure mode (user=None) gets everything."""
    if user is None:
        return frozenset().union(*ROLE_PERMISSIONS.values())
    return ROLE_PERMISSIONS.get(user.role, frozenset())


def has_perm(user: User | None, perm: str) -> bool:
    return perm in user_permissions(user)


async def require_auth(
    request: Request, session: AsyncSession = Depends(get_session)
) -> User | None:
    """Guard for every API route. Returns the User, or None in allow_insecure mode."""
    settings = get_settings()
    if settings.ipambox_allow_insecure:
        set_actor("system")
        return None
    token = request.cookies.get(SESSION_COOKIE)
    user_id = await get_session_user_id(token) if token else None
    if user_id is None:
        raise HTTPException(401, "not authenticated")
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(401, "session expired")
    set_actor(user.username)
    return user


def require_perm(perm: str):
    """Dependency factory: 403 unless the caller's role grants `perm`.

    Stacks on top of the router-level require_auth (FastAPI dedupes it per
    request) and stays permissive in allow_insecure mode.
    """

    async def _dep(user: User | None = Depends(require_auth)) -> User | None:
        if not has_perm(user, perm):
            raise HTTPException(403, f"requires {perm} permission")
        return user

    return _dep
