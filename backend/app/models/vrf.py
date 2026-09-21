from datetime import datetime

from sqlalchemy import DateTime, Boolean, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class VRF(Base):
    __tablename__ = "vrfs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    # Route Distinguisher e.g. "65000:1"; NULL for the default/Global VRF
    rd: Mapped[str | None] = mapped_column(String(64), unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    site_id: Mapped[int | None] = mapped_column(ForeignKey("sites.id", ondelete="SET NULL"), index=True)
    sort_order: Mapped[int | None] = mapped_column(index=True)
    pinned: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    # Manual row accent (#rrggbb, Tag.color format); NULL = none.
    row_color: Mapped[str | None] = mapped_column(String(7))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    site: Mapped["Site | None"] = relationship(back_populates="vrfs")  # noqa: F821
    # ORM cascade (mirrors Prefix.addresses): deleting a VRF must run its
    # prefixes — and their addresses — through session.deleted so the
    # changelog records each row and tag_refs sweeps their assignments. The
    # DB-level ondelete="CASCADE" alone would do all of that invisibly.
    prefixes: Mapped[list["Prefix"]] = relationship(  # noqa: F821
        back_populates="vrf", cascade="all, delete-orphan"
    )
