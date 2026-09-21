from datetime import datetime

from sqlalchemy import DateTime, Boolean, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Service(Base):
    """Service catalog row from the שירותים sheet."""

    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column(String(255), index=True)
    beneficiary: Mapped[str | None] = mapped_column(String(255))
    site_id: Mapped[int | None] = mapped_column(
        ForeignKey("sites.id", ondelete="SET NULL"), index=True
    )
    site_code: Mapped[str | None] = mapped_column(String(16))
    doc_path: Mapped[str | None] = mapped_column(Text)  # UNC documentation path
    test_info: Mapped[str | None] = mapped_column(Text)
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
        return self.name or f"service#{self.id}"
