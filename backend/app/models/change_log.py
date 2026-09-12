from datetime import datetime

from sqlalchemy import Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ChangeLog(Base):
    """NetBox-style audit trail: who changed what, when, and the field diff."""

    __tablename__ = "change_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    ts: Mapped[datetime] = mapped_column(server_default=func.now(), index=True)
    actor: Mapped[str] = mapped_column(String(64), default="system", server_default="system")
    action: Mapped[str] = mapped_column(String(16), index=True)  # create | update | delete
    object_type: Mapped[str] = mapped_column(String(64), index=True)
    object_id: Mapped[int | None] = mapped_column(Integer, index=True)
    object_repr: Mapped[str] = mapped_column(String(255))
    # [{"field": "status", "before": "discovered", "after": "active"}, ...]
    changes: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
