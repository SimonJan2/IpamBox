import enum
from datetime import datetime

from sqlalchemy import Enum, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import ARRAY, INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class IPStatus(str, enum.Enum):
    ACTIVE = "active"
    RESERVED = "reserved"
    DHCP = "dhcp"
    DISCOVERED = "discovered"
    OFFLINE = "offline"


class IPRole(str, enum.Enum):
    VIP = "vip"
    VRRP = "vrrp"
    HSRP = "hsrp"
    GLBP = "glbp"
    CARP = "carp"
    SECONDARY = "secondary"


class IPAddress(Base):
    __tablename__ = "ip_addresses"

    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str] = mapped_column(INET, nullable=False)
    # Integer form of the address for fast range scans/sorting (IPv4 fits
    # BIGINT; Numeric(39) keeps IPv6 representable too).
    address_int: Mapped[int] = mapped_column(Numeric(39, 0), nullable=False)
    prefix_id: Mapped[int] = mapped_column(ForeignKey("prefixes.id", ondelete="CASCADE"), index=True)
    vrf_id: Mapped[int] = mapped_column(ForeignKey("vrfs.id", ondelete="CASCADE"), index=True)
    mac_address: Mapped[str | None] = mapped_column(String(17))
    vendor: Mapped[str | None] = mapped_column(String(255))
    hostname: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[IPStatus] = mapped_column(
        Enum(
            IPStatus,
            name="ip_status",
            native_enum=True,
            values_callable=lambda e: [m.value for m in e],
        ),
        default=IPStatus.DISCOVERED,
        server_default=IPStatus.DISCOVERED.value,
        index=True,
    )
    last_seen: Mapped[datetime | None] = mapped_column()
    role: Mapped[IPRole | None] = mapped_column(
        Enum(
            IPRole,
            name="ip_role",
            native_enum=True,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=True,
    )
    nat_inside_id: Mapped[int | None] = mapped_column(
        ForeignKey("ip_addresses.id", ondelete="SET NULL"), index=True
    )
    # Populated by the scanner: TCP ports that answered, and a best-guess
    # device classification derived from ports + vendor + hostname.
    open_ports: Mapped[list[int] | None] = mapped_column(ARRAY(Integer))
    device_type: Mapped[str | None] = mapped_column(String(32))
    # Imported-inventory fields (Network_Address.xlsx site sheets).
    serial_number: Mapped[str | None] = mapped_column(String(128))
    switch_name: Mapped[str | None] = mapped_column(String(255))
    switch_port: Mapped[str | None] = mapped_column(String(64))
    counter_location: Mapped[str | None] = mapped_column(String(255))
    # Overflow bag for imported values that have no typed column
    # (status_raw, mac_raw, other_ips, unmatched sheet columns, …).
    custom_fields: Mapped[dict | None] = mapped_column(JSONB, server_default="{}")
    import_batch_id: Mapped[int | None] = mapped_column(
        ForeignKey("import_batches.id", ondelete="SET NULL"), index=True
    )
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    prefix: Mapped["Prefix"] = relationship(back_populates="addresses")  # noqa: F821
    vrf: Mapped["VRF"] = relationship()  # noqa: F821

    __table_args__ = (
        UniqueConstraint("vrf_id", "address", name="uq_ip_addresses_vrf_address"),
        Index("ix_ip_addresses_address_int", "address_int"),
        Index("ix_ip_addresses_prefix_int", "prefix_id", "address_int"),
    )
