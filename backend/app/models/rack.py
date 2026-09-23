import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    func,
    text,
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
    """A physical rack/cabinet at a site — owns rack_devices rows."""

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
    # Carrier mounting: NULL slot_layout = normal device; "halves"/"quarters"/
    # "shelf" = carrier tray whose children ride in slots. Children set
    # carrier_id + slot; their u_position/face mirror the carrier's
    # (display-only). Single level — carriers never carry carrier_id.
    carrier_id: Mapped[int | None] = mapped_column(
        ForeignKey("rack_devices.id", ondelete="CASCADE"), index=True
    )
    slot: Mapped[int | None] = mapped_column()
    slot_layout: Mapped[str | None] = mapped_column(String(16))
    # Nameplate draw / installed weight — feed rack + group capacity rollups.
    watts: Mapped[int | None] = mapped_column()
    weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(7, 2))
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
    # Self-FK: children ride in the carrier's slots. Deleting the carrier
    # cascades at the DB level; the API also deletes children explicitly so
    # each removal is audited.
    carrier: Mapped["RackDevice | None"] = relationship(
        remote_side="RackDevice.id", lazy="selectin"
    )

    # No unique constraint on (rack_id, u_position) — front/rear pairs legally
    # share U slots; collisions are validated in the service layer.
    __table_args__ = (
        Index("ix_rack_devices_rack_u", "rack_id", "u_position"),
        # One child per slot (NULL carrier_id rows don't participate).
        Index(
            "ix_rack_devices_carrier_slot",
            "carrier_id",
            "slot",
            unique=True,
            postgresql_where=text("carrier_id IS NOT NULL"),
        ),
    )

    def __changelog_repr__(self) -> str:
        return f"{self.name}@U{self.u_position}"
