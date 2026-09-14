from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import USERS_MANAGE, require_perm
from app.core.security import destroy_user_sessions, hash_password
from app.models.user import User, UserRole
from app.schemas.settings import UserOut

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(require_perm(USERS_MANAGE))],
)


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=8, max_length=256)
    role: UserRole = UserRole.VIEWER


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=64)
    password: str | None = Field(default=None, min_length=8, max_length=256)
    role: UserRole | None = None


def _out(u: User) -> UserOut:
    return UserOut(
        id=u.id,
        username=u.username,
        role=u.role.value,
        created_at=u.created_at.isoformat(),
    )


async def _admin_count(session: AsyncSession) -> int:
    return (
        await session.scalar(
            select(func.count(User.id)).where(User.role == UserRole.ADMIN)
        )
        or 0
    )


@router.get("", response_model=list[UserOut])
async def list_users(session: AsyncSession = Depends(get_session)):
    rows = (
        (await session.execute(select(User).order_by(User.username)))
        .scalars()
        .all()
    )
    return [_out(u) for u in rows]


@router.post("", response_model=UserOut, status_code=201)
async def create_user(
    body: UserCreate, session: AsyncSession = Depends(get_session)
):
    user = User(
        username=body.username.strip(),
        password_hash=hash_password(body.password),
        role=body.role,
    )
    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(409, "username already exists")
    await session.refresh(user)
    return _out(user)


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    body: UserUpdate,
    session: AsyncSession = Depends(get_session),
):
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(404, "user not found")
    credentials_changed = False
    if body.username is not None:
        user.username = body.username.strip()
    if body.password is not None:
        user.password_hash = hash_password(body.password)
        credentials_changed = True
    if body.role is not None and body.role != user.role:
        if user.role == UserRole.ADMIN and await _admin_count(session) <= 1:
            raise HTTPException(409, "cannot demote the only administrator")
        user.role = body.role
        credentials_changed = True
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(409, "username already exists")
    await session.refresh(user)
    if credentials_changed:
        # role/password changes take effect immediately — force re-login
        await destroy_user_sessions(user.id)
    return _out(user)


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    me: User | None = Depends(require_perm(USERS_MANAGE)),
):
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(404, "user not found")
    if me is not None and me.id == user_id:
        raise HTTPException(409, "cannot delete your own account")
    if user.role == UserRole.ADMIN and await _admin_count(session) <= 1:
        raise HTTPException(409, "cannot delete the only administrator")
    total = await session.scalar(select(func.count(User.id)))
    if (total or 0) <= 1:
        raise HTTPException(409, "cannot delete the last user")
    await session.delete(user)
    await session.commit()
    await destroy_user_sessions(user_id)
