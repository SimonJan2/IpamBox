from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class CustomList(Base):
    """User-defined table — preserves a workbook sheet's own shape
    (e.g. 'שרתים בייצור') instead of dissolving it into typed entities.

    ``columns`` is an ordered JSONB list of column defs:
        [{key, label, type, options?, multi?}]
    Keys are positional ("c0", "c1"…) so relabeling a column never touches
    row data. ``key_column`` names the merge-identity column used when a
    later import re-syncs the same sheet.
    """

    __tablename__ = "custom_lists"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    icon: Mapped[str | None] = mapped_column(String(64))
    columns: Mapped[list | None] = mapped_column(JSONB, server_default="[]")
    # Column key ("c0"…) whose value identifies a row on re-import merge.
    key_column: Mapped[str | None] = mapped_column(String(64))
    # Workbook sheet this list was imported from (provenance, display only).
    source_sheet: Mapped[str | None] = mapped_column(String(255))
    import_batch_id: Mapped[int | None] = mapped_column(
        ForeignKey("import_batches.id", ondelete="SET NULL"), index=True
    )
    sort_order: Mapped[int | None] = mapped_column(index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    rows: Mapped[list["CustomListRow"]] = relationship(
        back_populates="list", cascade="all, delete-orphan"
    )

    def __changelog_repr__(self) -> str:
        return self.name or f"list#{self.id}"


class CustomListRow(Base):
    """One row of a custom list — ``data`` maps column key -> string value."""

    __tablename__ = "custom_list_rows"

    id: Mapped[int] = mapped_column(primary_key=True)
    list_id: Mapped[int] = mapped_column(
        ForeignKey("custom_lists.id", ondelete="CASCADE"), index=True
    )
    data: Mapped[dict | None] = mapped_column(JSONB, server_default="{}")
    site_id: Mapped[int | None] = mapped_column(
        ForeignKey("sites.id", ondelete="SET NULL"), index=True
    )
    sort_order: Mapped[int | None] = mapped_column(Integer, index=True)
    pinned: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    # Manual row accent (#rrggbb, Tag.color format); NULL = none.
    row_color: Mapped[str | None] = mapped_column(String(7))
    # Set when a human edits cells via the UI/API — re-import merges never
    # overwrite manually-edited rows (they report a conflict instead).
    manually_edited: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    import_batch_id: Mapped[int | None] = mapped_column(
        ForeignKey("import_batches.id", ondelete="SET NULL"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    list: Mapped[CustomList] = relationship(back_populates="rows")

    def __changelog_repr__(self) -> str:
        # data is built in column order, so the first value is usually the
        # key column (server name etc.) — far more readable than row#N.
        # Can't touch self.list here: repr runs inside flush, where a lazy
        # load would explode under asyncio.
        first = next(iter((self.data or {}).values()), None)
        return str(first) if first else f"row#{self.id}"
