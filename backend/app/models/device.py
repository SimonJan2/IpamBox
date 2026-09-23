"""First-class device: a host that exists independently of any rack.

A Device owns its rack *placement* (all placement columns nullable — NULL
means unracked inventory), links to any number of IP addresses
(`ip_addresses.device_id` — mgmt + service + iLO on one box), optionally
links an Asset record for lifecycle/catalog data, and can be a carrier
(`slot_layout` set) that holds other devices on shelf slots.
"""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.asset import Asset  # noqa: F401 — relationship target
from app.models.base import Base
from app.models.rack import Rack, RackFace  # noqa: F401 — relationship target
from app.models.site import Site  # noqa: F401 — relationship target


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    device_type: Mapped[str | None] = mapped_column(String(255))
    serial_number: Mapped[str | None] = mapped_column(String(128), index=True)
    site_id: Mapped[int | None] = mapped_column(
        ForeignKey("sites.id", ondelete="SET NULL"), index=True
    )
    asset_id: Mapped[int | None] = mapped_column(
        ForeignKey("assets.id", ondelete="SET NULL"), index=True
    )
    mac_address: Mapped[str | None] = mapped_column(String(17), index=True)

    # Placement — every column NULL = unracked device. rack_id is the marker.
    rack_id: Mapped[int | None] = mapped_column(
        ForeignKey("racks.id", ondelete="SET NULL"), index=True
    )
    u_position: Mapped[int | None] = mapped_column(Integer)
    u_height: Mapped[int | None] = mapped_column(Integer, default=1)
    face: Mapped[RackFace | None] = mapped_column(
        Enum(
            RackFace,
            name="rack_face",
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        default=RackFace.FRONT,
    )
    # Carrier mounting: self-FK (carriers are devices with slot_layout set)
    carrier_id: Mapped[int | None] = mapped_column(
        ForeignKey("devices.id", ondelete="SET NULL"), index=True
    )
    slot: Mapped[int | None] = mapped_column(Integer)
    slot_layout: Mapped[str | None] = mapped_column(String(16))

    colour: Mapped[str | None] = mapped_column(String(7))
    category: Mapped[str | None] = mapped_column(String(64))
    manufacturer: Mapped[str | None] = mapped_column(String(255))
    model: Mapped[str | None] = mapped_column(String(255))
    watts: Mapped[int | None] = mapped_column(Integer)
    weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(7, 2))
    custom_fields: Mapped[dict | None] = mapped_column(
        JSONB, server_default=text("'{}'::jsonb")
    )
    source: Mapped[str] = mapped_column(String(16), default="manual")
    notes: Mapped[str | None] = mapped_column(Text)
    row_color: Mapped[str | None] = mapped_column(String(7))
    sort_order: Mapped[int | None] = mapped_column(Integer, index=True)
    pinned: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    import_batch_id: Mapped[int | None] = mapped_column(
        ForeignKey("import_batches.id", ondelete="SET NULL"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    rack: Mapped["Rack | None"] = relationship(back_populates="devices")
    site: Mapped["Site | None"] = relationship()
    asset: Mapped["Asset | None"] = relationship(lazy="selectin")
    carrier: Mapped["Device | None"] = relationship(
        remote_side="Device.id", lazy="selectin"
    )
    # carrier children are queried explicitly (carrier_id == id) — no
    # `children` relationship so the self-FK stays a single clean mapping.
    ips: Mapped[list["IPAddress"]] = relationship(
        back_populates="device", lazy="selectin", order_by="IPAddress.id"
    )

    __table_args__ = (
        Index("ix_devices_rack_u", "rack_id", "u_position"),
        Index(
            "ix_devices_carrier_slot",
            "carrier_id",
            "slot",
            unique=True,
            postgresql_where=text("carrier_id IS NOT NULL AND slot IS NOT NULL"),
        ),
    )

    def __changelog_repr__(self) -> str:
        return self.name or f"device#{self.id}"
