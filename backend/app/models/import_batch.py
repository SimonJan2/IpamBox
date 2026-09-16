import enum
from datetime import datetime

from sqlalchemy import Enum, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ImportBatchStatus(str, enum.Enum):
    DRAFT = "draft"  # uploaded, not yet committed
    COMMITTED = "committed"
    FAILED = "failed"


class ImportBatch(Base):
    """One uploaded workbook (or file) import run.

    `stats` holds the preview result: per-sheet family/counts plus the
    normalized row plan, so commit executes what the user reviewed without
    re-parsing the file.
    """

    __tablename__ = "import_batches"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    stored_path: Mapped[str] = mapped_column(String(512))
    sha256: Mapped[str] = mapped_column(String(64))
    status: Mapped[ImportBatchStatus] = mapped_column(
        Enum(
            ImportBatchStatus,
            name="import_batch_status",
            native_enum=True,
            values_callable=lambda e: [m.value for m in e],
        ),
        default=ImportBatchStatus.DRAFT,
        server_default=ImportBatchStatus.DRAFT.value,
        index=True,
    )
    stats: Mapped[dict | None] = mapped_column(JSONB, server_default="{}")
    actor: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    committed_at: Mapped[datetime | None] = mapped_column()

    def __changelog_repr__(self) -> str:
        return f"import#{self.id} ({self.filename})"
