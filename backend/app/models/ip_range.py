import enum
from datetime import datetime

from sqlalchemy import DateTime, CheckConstraint, Enum, ForeignKey, Numeric, Text, func
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class IPRangeRole(str, enum.Enum):
    DHCP = "dhcp"
    POOL = "pool"
    RESERVED = "reserved"


class IPRange(Base):
    """A named block of addresses inside a prefix (e.g. a DHCP scope).

    Any defined range is excluded from automatic next-IP allocation —
    ranges mark space that is managed outside IpamBox's allocator.
    """

    __tablename__ = "ip_ranges"

    id: Mapped[int] = mapped_column(primary_key=True)
    prefix_id: Mapped[int] = mapped_column(ForeignKey("prefixes.id", ondelete="CASCADE"), index=True)
    vrf_id: Mapped[int] = mapped_column(ForeignKey("vrfs.id", ondelete="CASCADE"), index=True)
    start_address: Mapped[str] = mapped_column(INET, nullable=False)
    start_int: Mapped[int] = mapped_column(Numeric(39, 0), nullable=False)
    end_address: Mapped[str] = mapped_column(INET, nullable=False)
    end_int: Mapped[int] = mapped_column(Numeric(39, 0), nullable=False)
    role: Mapped[IPRangeRole] = mapped_column(
        Enum(
            IPRangeRole,
            name="range_role",
            native_enum=True,
            values_callable=lambda e: [m.value for m in e],
        ),
        default=IPRangeRole.DHCP,
        server_default=IPRangeRole.DHCP.value,
    )
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    prefix: Mapped["Prefix"] = relationship()  # noqa: F821
    vrf: Mapped["VRF"] = relationship()  # noqa: F821

    __table_args__ = (
        CheckConstraint("start_int <= end_int", name="ck_ip_ranges_order"),
    )

    def __changelog_repr__(self) -> str:
        return f"{self.start_address}–{self.end_address}"
