from datetime import datetime

from sqlalchemy import Boolean, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Site(Base):
    __tablename__ = "sites"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    # Short code from the sites master list (e.g. "ALNB"); unique when set.
    code: Mapped[str | None] = mapped_column(String(16), unique=True, index=True)
    # The N in 10.{N}.0.0 — links imported site sheets to this site.
    site_number: Mapped[int | None] = mapped_column(index=True)
    # Raw size class from the workbook (קטן/בינוני/גדול …) — kept as text.
    size: Mapped[str | None] = mapped_column(String(32))
    is_active: Mapped[bool] = mapped_column(default=True, server_default="true")
    contact: Mapped[str | None] = mapped_column(Text)
    address: Mapped[str | None] = mapped_column(Text)
    # Manual list order, global for all users. NULL = never positioned:
    # unpositioned rows sort to the end of their pin group (NULLS LAST).
    sort_order: Mapped[int | None] = mapped_column(index=True)
    pinned: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    vrfs: Mapped[list["VRF"]] = relationship(back_populates="site")  # noqa: F821
    prefixes: Mapped[list["Prefix"]] = relationship(back_populates="site")  # noqa: F821
