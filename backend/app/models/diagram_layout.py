"""Saved canvas positions for /topology (V10).

One row per named diagram — `"main"` today, per-site keys later. The
positions blob is keyed by the same string node ids the graph endpoint
emits ("dev-12", "unlinked-55", "rack-7", …): `{node_id: {x, y}}`.

Deliberately not in AUDITED_MODELS: layout churn (every drag-save) would
spam the changelog without telling an auditor anything — it's UI state
that happens to live server-side, like prefs with a sync story. It IS in
BACKUP_TABLES: positions are user work and must survive a restore.
"""
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, String, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class DiagramLayout(Base):
    __tablename__ = "diagram_layouts"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    positions: Mapped[dict[str, Any]] = mapped_column(
        JSONB, server_default=text("'{}'::jsonb")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __changelog_repr__(self) -> str:
        return self.key
