import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class RackFace(str, enum.Enum):
    FRONT = "front"
    REAR = "rear"
    BOTH = "both"


class RackGroup(Base):
    """A bayed row: racks ordered left-to-right as they stand in the DC."""

    __tablename__ = "rack_groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    site_id: Mapped[int | None] = mapped_column(
        ForeignKey("sites.id", ondelete="SET NULL"), index=True
    )
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int | None] = mapped_column(index=True)
    pinned: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    row_color: Mapped[str | None] = mapped_column(String(7))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    site: Mapped["Site | None"] = relationship()  # noqa: F821
    racks: Mapped[list["Rack"]] = relationship(
        back_populates="group",
        order_by="Rack.group_position",
        lazy="selectin",
    )

    def __changelog_repr__(self) -> str:
        return self.name or f"rack_group#{self.id}"


class Rack(Base):
    """A physical rack/cabinet at a site — devices take placement in it."""

    __tablename__ = "racks"

    id: Mapped[int] = mapped_column(primary_key=True)
    site_id: Mapped[int | None] = mapped_column(
        ForeignKey("sites.id", ondelete="SET NULL"), index=True
    )
    # Bayed-row membership: which group + left-to-right position inside it.
    # NULL group = standalone rack; NULL position sorts to the row's end.
    group_id: Mapped[int | None] = mapped_column(
        ForeignKey("rack_groups.id", ondelete="SET NULL"), index=True
    )
    group_position: Mapped[int | None] = mapped_column()
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    room: Mapped[str | None] = mapped_column(String(255))
    height_u: Mapped[int] = mapped_column(default=42, server_default="42")
    # Rail width in inches: 10 or 19 (Rackula's widths).
    width: Mapped[int] = mapped_column(default=19, server_default="19")
    notes: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int | None] = mapped_column(index=True)
    pinned: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    row_color: Mapped[str | None] = mapped_column(String(7))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("ix_racks_group_pos", "group_id", "group_position"),
    )

    site: Mapped["Site | None"] = relationship()  # noqa: F821
    group: Mapped["RackGroup | None"] = relationship(back_populates="racks")
    # selectin keeps collection access async-safe (RackDetail validates it).
    # No cascade: devices survive the rack — deleting a rack SETs their
    # rack_id NULL (they become unracked inventory, not deleted rows).
    devices: Mapped[list["Device"]] = relationship(  # noqa: F821
        back_populates="rack",
        order_by="Device.u_position",
        lazy="selectin",
    )

    def __changelog_repr__(self) -> str:
        return self.name or f"rack#{self.id}"
