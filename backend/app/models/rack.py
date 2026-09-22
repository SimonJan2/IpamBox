import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class RackFace(str, enum.Enum):
    FRONT = "front"
    REAR = "rear"
    BOTH = "both"


class Rack(Base):
    """A physical rack/cabinet at a site — owns rack_devices rows."""

    __tablename__ = "racks"

    id: Mapped[int] = mapped_column(primary_key=True)
    site_id: Mapped[int | None] = mapped_column(
        ForeignKey("sites.id", ondelete="SET NULL"), index=True
    )
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

    site: Mapped["Site | None"] = relationship()  # noqa: F821
    # selectin keeps collection access async-safe (RackDetail validates it).
    devices: Mapped[list["RackDevice"]] = relationship(
        back_populates="rack",
        cascade="all, delete-orphan",
        order_by="RackDevice.u_position",
        lazy="selectin",
    )

    def __changelog_repr__(self) -> str:
        return self.name or f"rack#{self.id}"


class RackDevice(Base):
    __tablename__ = "rack_devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    rack_id: Mapped[int] = mapped_column(
        ForeignKey("racks.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(255))
    # Library slug or free text — kept NetBox-aligned for a future importer.
    device_type: Mapped[str | None] = mapped_column(String(255))
    u_position: Mapped[int] = mapped_column()  # 1-based bottom U
    u_height: Mapped[int] = mapped_column(default=1, server_default="1")
    face: Mapped[RackFace] = mapped_column(
        Enum(
            RackFace,
            name="rack_face",
            native_enum=True,
            values_callable=lambda e: [m.value for m in e],
        ),
        default=RackFace.FRONT,
        server_default=RackFace.FRONT.value,
    )
    colour: Mapped[str | None] = mapped_column(String(7))  # #rrggbb
    category: Mapped[str | None] = mapped_column(String(64))
    manufacturer: Mapped[str | None] = mapped_column(String(255))
    model: Mapped[str | None] = mapped_column(String(255))
    asset_id: Mapped[int | None] = mapped_column(
        ForeignKey("assets.id", ondelete="SET NULL"), index=True
    )
    ip_address_id: Mapped[int | None] = mapped_column(
        ForeignKey("ip_addresses.id", ondelete="SET NULL"), index=True
    )
    # Provenance: manual | rackula.
    source: Mapped[str] = mapped_column(
        String(16), default="manual", server_default="manual"
    )
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    rack: Mapped[Rack] = relationship(back_populates="devices")
    # selectin so attribute access stays async-safe without explicit eager loads.
    asset: Mapped["Asset | None"] = relationship(lazy="selectin")  # noqa: F821
    ip_address: Mapped["IPAddress | None"] = relationship(lazy="selectin")  # noqa: F821

    # No unique constraint on (rack_id, u_position) — front/rear pairs legally
    # share U slots; collisions are validated in the service layer.
    __table_args__ = (
        Index("ix_rack_devices_rack_u", "rack_id", "u_position"),
    )

    def __changelog_repr__(self) -> str:
        return f"{self.name}@U{self.u_position}"
