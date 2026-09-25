import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, CIDR, INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PrefixStatus(str, enum.Enum):
    CONTAINER = "container"
    ACTIVE = "active"
    RESERVED = "reserved"
    DEPRECATED = "deprecated"


class Prefix(Base):
    __tablename__ = "prefixes"

    id: Mapped[int] = mapped_column(primary_key=True)
    prefix: Mapped[str] = mapped_column(CIDR, nullable=False)
    vrf_id: Mapped[int] = mapped_column(ForeignKey("vrfs.id", ondelete="CASCADE"), index=True)
    site_id: Mapped[int | None] = mapped_column(ForeignKey("sites.id", ondelete="SET NULL"), index=True)
    vlan_id: Mapped[int | None] = mapped_column(ForeignKey("vlans.id", ondelete="SET NULL"), index=True)
    status: Mapped[PrefixStatus] = mapped_column(
        Enum(
            PrefixStatus,
            name="prefix_status",
            native_enum=True,
            values_callable=lambda e: [m.value for m in e],
        ),
        default=PrefixStatus.ACTIVE,
        server_default=PrefixStatus.ACTIVE.value,
    )
    description: Mapped[str | None] = mapped_column(Text)
    # Technical addresses of the subnet — the default gateway and resolver
    # IPs it hands out. Each value is mirrored by a reserved, marker-tagged
    # ip_addresses row (services.ranges.sync_technical_addresses) so the
    # allocator never hands them out and the grid can glyph them.
    gateway: Mapped[str | None] = mapped_column(INET)
    dns_servers: Mapped[list[str] | None] = mapped_column(ARRAY(INET))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    vrf: Mapped["VRF"] = relationship(back_populates="prefixes")  # noqa: F821
    site: Mapped["Site | None"] = relationship(back_populates="prefixes")  # noqa: F821
    vlan: Mapped["VLAN | None"] = relationship(back_populates="prefixes")  # noqa: F821
    addresses: Mapped[list["IPAddress"]] = relationship(  # noqa: F821
        back_populates="prefix", cascade="all, delete-orphan"
    )

    __table_args__ = (
        # Per-VRF uniqueness + no-overlap is enforced by a GiST exclusion
        # constraint created in the initial migration (requires btree_gist).
    )
