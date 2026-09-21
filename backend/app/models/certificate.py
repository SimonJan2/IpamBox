from datetime import date, datetime

from sqlalchemy import Boolean, Date, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Certificate(Base):
    """Certificate-expiry row from the תוקף תעודות sheet."""

    __tablename__ = "certificates"

    id: Mapped[int] = mapped_column(primary_key=True)
    platform: Mapped[str | None] = mapped_column(String(64), index=True)  # F5, …
    target: Mapped[str | None] = mapped_column(String(255))  # VS / virtual server
    server_name: Mapped[str | None] = mapped_column(String(255), index=True)
    cert_name: Mapped[str | None] = mapped_column(String(255))
    expires_on: Mapped[date | None] = mapped_column(Date, index=True)
    # Original cell value (Excel serial or text date) kept for audit.
    serial_raw: Mapped[str | None] = mapped_column(String(64))
    notes: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int | None] = mapped_column(index=True)
    pinned: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    import_batch_id: Mapped[int | None] = mapped_column(
        ForeignKey("import_batches.id", ondelete="SET NULL"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    def __changelog_repr__(self) -> str:
        return self.cert_name or self.server_name or f"certificate#{self.id}"
