"""Entity file attachments (V13).

Blobs live in Postgres (BYTEA) so backup/restore stays atomic and
ID-preserving — no filesystem state to reconcile. The owner is referenced
polymorphically by (entity_type, entity_id) — same shape as
tag_assignments — and ``app.core.attachment_refs`` sweeps a doomed
entity's rows inside the delete transaction (cascade-by-application,
mirroring tag_refs; no upsert — same-name re-uploads are allowed and
distinguished by ``label``).

Blob bytes never leave the DB except through the download endpoint:
``blob`` is in core.changelog.SKIP_FIELDS and absent from the API's Out
schema, and list queries defer the column.
"""
from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, LargeBinary, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True)
    # snake_case entity vocabulary — same convention as review_dismissals
    # (entity_type/entity_id), e.g. "device", "ip_address".
    entity_type: Mapped[str] = mapped_column(String(32), index=True)
    entity_id: Mapped[int] = mapped_column(Integer, index=True)
    label: Mapped[str | None] = mapped_column(String(255))
    filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(128))
    size: Mapped[int] = mapped_column(Integer)
    blob: Mapped[bytes] = mapped_column(LargeBinary)
    # username snapshot — see DocsPage.created_by.
    uploaded_by: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        # the hot lookup: "attachments for this entity"
        Index("ix_attachments_entity", "entity_type", "entity_id"),
    )

    def __changelog_repr__(self) -> str:
        return f"{self.filename} on {self.entity_type}#{self.entity_id}"
