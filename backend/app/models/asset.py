import enum
from datetime import date, datetime

from sqlalchemy import DateTime, Boolean, Date, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class AssetKind(str, enum.Enum):
    HARDWARE = "hardware"
    SOFTWARE = "software"


class Asset(Base):
    """SW/HW catalog rows (תוכנות וחומרות) and serial-number inventory
    (switches/routers sheets) unified: catalog rows have no serial/site,
    inventory rows carry serial_number + site_id."""

    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[AssetKind] = mapped_column(
        Enum(
            AssetKind,
            name="asset_kind",
            native_enum=True,
            values_callable=lambda e: [m.value for m in e],
        ),
        default=AssetKind.HARDWARE,
        server_default=AssetKind.HARDWARE.value,
        index=True,
    )
    category: Mapped[str | None] = mapped_column(String(64))  # סוג / device class
    vendor: Mapped[str | None] = mapped_column(String(255))  # חברה
    model: Mapped[str | None] = mapped_column(String(255), index=True)  # דגם
    purpose: Mapped[str | None] = mapped_column(String(255))  # ייעוד
    version: Mapped[str | None] = mapped_column(String(128))  # גירסה
    eol_on: Mapped[date | None] = mapped_column(Date)
    support_status: Mapped[str | None] = mapped_column(String(128))
    serial_number: Mapped[str | None] = mapped_column(String(128), index=True)
    site_id: Mapped[int | None] = mapped_column(
        ForeignKey("sites.id", ondelete="SET NULL"), index=True
    )
    notes: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int | None] = mapped_column(index=True)
    pinned: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    # Manual row accent (#rrggbb, Tag.color format); NULL = none.
    row_color: Mapped[str | None] = mapped_column(String(7))
    import_batch_id: Mapped[int | None] = mapped_column(
        ForeignKey("import_batches.id", ondelete="SET NULL"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    site: Mapped["Site | None"] = relationship()  # noqa: F821

    def __changelog_repr__(self) -> str:
        return self.serial_number or self.model or f"asset#{self.id}"
