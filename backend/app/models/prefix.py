import enum
from datetime import datetime

from sqlalchemy import CheckConstraint, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import CIDR
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
    vlan_id: Mapped[int | None] = mapped_column()
    vlan_name: Mapped[str | None] = mapped_column(String(255))
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
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    vrf: Mapped["VRF"] = relationship(back_populates="prefixes")  # noqa: F821
    site: Mapped["Site | None"] = relationship(back_populates="prefixes")  # noqa: F821
    addresses: Mapped[list["IPAddress"]] = relationship(  # noqa: F821
        back_populates="prefix", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("vlan_id IS NULL OR (vlan_id BETWEEN 1 AND 4094)", name="ck_prefixes_vlan_range"),
        # Per-VRF uniqueness + no-overlap is enforced by a GiST exclusion
        # constraint created in the initial migration (requires btree_gist).
    )
