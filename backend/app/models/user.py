import enum
from datetime import datetime

from sqlalchemy import Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"          # full access incl. user management
    OPERATOR = "operator"    # tier-1: data CRUD + backups, no user admin
    CONTRIBUTOR = "contributor"  # tier-2: add/edit data, no delete/backup
    VIEWER = "viewer"        # tier-3: read-only


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            name="user_role",
            native_enum=True,
            values_callable=lambda e: [m.value for m in e],
        ),
        default=UserRole.ADMIN,
        server_default=UserRole.ADMIN.value,
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
