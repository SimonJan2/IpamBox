import enum
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class VLANStatus(str, enum.Enum):
    ACTIVE = "active"
    RESERVED = "reserved"
    DEPRECATED = "deprecated"


class VLANGroup(Base):
    __tablename__ = "vlan_groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    vlans: Mapped[list["VLAN"]] = relationship(back_populates="group")


class VLAN(Base):
    __tablename__ = "vlans"

    id: Mapped[int] = mapped_column(primary_key=True)
    vid: Mapped[int] = mapped_column(index=True)
    name: Mapped[str] = mapped_column(String(64))
    group_id: Mapped[int | None] = mapped_column(
        ForeignKey("vlan_groups.id", ondelete="SET NULL"), index=True
    )
    site_id: Mapped[int | None] = mapped_column(
        ForeignKey("sites.id", ondelete="SET NULL"), index=True
    )
    status: Mapped[VLANStatus] = mapped_column(
        Enum(
            VLANStatus,
            name="vlan_status",
            native_enum=True,
            values_callable=lambda e: [m.value for m in e],
        ),
        default=VLANStatus.ACTIVE,
        server_default=VLANStatus.ACTIVE.value,
    )
    description: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int | None] = mapped_column(index=True)
    pinned: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    # Manual row accent (#rrggbb, Tag.color format); NULL = none.
    row_color: Mapped[str | None] = mapped_column(String(7))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    group: Mapped["VLANGroup | None"] = relationship(back_populates="vlans")
    prefixes: Mapped[list["Prefix"]] = relationship(back_populates="vlan")  # noqa: F821

    __table_args__ = (
        CheckConstraint("vid BETWEEN 1 AND 4094", name="ck_vlans_vid_range"),
    )

    def __changelog_repr__(self) -> str:
        return f"VLAN {self.vid} ({self.name})"
