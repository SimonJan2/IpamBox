from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_session
from app.core.security import SESSION_COOKIE, get_session_user_id, set_actor
from app.models.user import User


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
