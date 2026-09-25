"""Cabling (V4A): device interfaces and the cables between them.

A DeviceInterface is one named port/NIC on a device. A Cable links exactly
two interfaces; each interface terminates at most one cable end (a/b end
columns are each UNIQUE and the API checks across both columns, so an
interface carries at most one cable).

Patch panels need no dedicated entity: a 24-port panel is a device whose
interfaces have kind='patch'. The front/back pair inside one panel position
is linked by `pair_interface_id` (self-FK — NetBox rear_port-style); the
cable trace hops front→back through it. That pair link (not a second
cable) is what lets panel daisy chains work under the one-cable rule.
"""
import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class InterfaceKind(str, enum.Enum):
    RJ45 = "rj45"
    SFP = "sfp"
    SFP28 = "sfp28"
    QSFP = "qsfp"
    CONSOLE = "console"
    PATCH = "patch"
    POWER = "power"
    OTHER = "other"


class CableKind(str, enum.Enum):
    CAT5E = "cat5e"
    CAT6 = "cat6"
    CAT6A = "cat6a"
    DAC = "dac"
    FIBER_SM = "fiber_sm"
    FIBER_MM = "fiber_mm"
    POWER = "power"
    CONSOLE = "console"
    OTHER = "other"


class DeviceInterface(Base):
    __tablename__ = "device_interfaces"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int] = mapped_column(
        ForeignKey("devices.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(64))
    kind: Mapped[InterfaceKind] = mapped_column(
        Enum(
            InterfaceKind,
            name="interface_kind",
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        default=InterfaceKind.OTHER,
        server_default=InterfaceKind.OTHER.value,
    )
    speed_mbps: Mapped[int | None] = mapped_column(Integer)
    mac_address: Mapped[str | None] = mapped_column(String(17))
    # Ordering within the device (port grid position).
    position: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    # Host-side NIC→IP binding — "this port serves this IP". Distinct from
    # ip_addresses.device_id (device *owns* the address) and from
    # ip_addresses.connected_interface_id (the far-end switch port).
    connected_ip_id: Mapped[int | None] = mapped_column(
        ForeignKey("ip_addresses.id", ondelete="SET NULL"), index=True
    )
    # Patch-panel front↔back pair (self-FK, both directions set by the
    # generate endpoint; the trace resolves it either way).
    pair_interface_id: Mapped[int | None] = mapped_column(
        ForeignKey("device_interfaces.id", ondelete="SET NULL"), index=True
    )
    # SNMP-observed state (V8) — written by the poll lane via bulk
    # update(); live in changelog.SKIP_FIELDS. if_index is the device's
    # IF-MIB index (the upsert key); a stale snmp_seen_at marks a port the
    # device no longer reports — never deleted, manual ports included.
    if_index: Mapped[int | None] = mapped_column(Integer)
    oper_status: Mapped[str | None] = mapped_column(String(16))
    admin_status: Mapped[str | None] = mapped_column(String(16))
    snmp_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    # Cable-validation evidence blob (V8.2) — one observed document per
    # port written at the tail of each SNMP poll:
    #   {cable_mismatch: {reason, detail, at, ...},   <- the flag, has_key
    #    lldp: [{remote_name, remote_port, remote_mac, ...}],
    #    macs_seen: [<mac>, ...] (bounded ~32),
    #    notes: [...], checked_at}
    # Flags are findings, never fixes — the human confirms what is true.
    validation: Mapped[dict | None] = mapped_column(JSONB)
    # Provenance — who owns this row: manual (user-created, protected) or
    # snmp (poller-created). Same vocabulary family as ip_addresses.source.
    source: Mapped[str] = mapped_column(
        String(16), default="manual", server_default="manual"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    device: Mapped["Device"] = relationship(back_populates="interfaces")  # noqa: F821
    # connected_ip_id / pair_interface_id stay plain FK columns — resolved
    # via grouped queries (services.cabling), not relationships: the Out
    # schemas stamp `connected_ip`/`peer` fields and an ORM relationship of
    # the same name would collide during model_validate.
    pair: Mapped["DeviceInterface | None"] = relationship(
        remote_side=[id],
        foreign_keys=[pair_interface_id],
        lazy="selectin",
        # Mutually-paired ports (panel front↔back) are a self-referential
        # cycle — post_update lets the UOW sever the link in a second pass
        # instead of failing on circular delete ordering.
        post_update=True,
    )

    __table_args__ = (
        UniqueConstraint("device_id", "name", name="uq_device_interfaces_device_name"),
        # if_index is the poller's upsert key — unique per device so two
        # rows can never claim the same IF-MIB index (NULLs exempt).
        UniqueConstraint(
            "device_id", "if_index", name="uq_device_interfaces_device_ifindex"
        ),
    )

    def __changelog_repr__(self) -> str:
        return f"{self.name} (device {self.device_id})"


class Cable(Base):
    __tablename__ = "cables"

    id: Mapped[int] = mapped_column(primary_key=True)
    a_interface_id: Mapped[int] = mapped_column(
        ForeignKey("device_interfaces.id", ondelete="CASCADE"), index=True
    )
    b_interface_id: Mapped[int] = mapped_column(
        ForeignKey("device_interfaces.id", ondelete="CASCADE"), index=True
    )
    kind: Mapped[CableKind] = mapped_column(
        Enum(
            CableKind,
            name="cable_kind",
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        default=CableKind.OTHER,
        server_default=CableKind.OTHER.value,
    )
    color: Mapped[str | None] = mapped_column(String(32))
    label: Mapped[str | None] = mapped_column(String(255))
    length_m: Mapped[Decimal | None] = mapped_column(Numeric(5, 1))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    a_interface: Mapped["DeviceInterface"] = relationship(
        foreign_keys=[a_interface_id], lazy="selectin"
    )
    b_interface: Mapped["DeviceInterface"] = relationship(
        foreign_keys=[b_interface_id], lazy="selectin"
    )

    __table_args__ = (
        CheckConstraint(
            "a_interface_id <> b_interface_id", name="ck_cables_distinct_ends"
        ),
        UniqueConstraint("a_interface_id", name="uq_cables_a_interface"),
        UniqueConstraint("b_interface_id", name="uq_cables_b_interface"),
    )

    def __changelog_repr__(self) -> str:
        return self.label or f"cable#{self.id}"
