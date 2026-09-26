"""User-authored docs pages (V13).

Operators write their own markdown pages (runbooks, notes) beside the
builtin help articles. ``category`` is a free-form grouping label that
defaults to ``notes`` — deliberately not the builtin DOC_CATEGORIES list,
so user pages never blur into developer-authored help. ``slug`` is
generated server-side (slugify + ``-2`` collision suffix) and stays
stable across title edits — it is the public URL under /docs/pages/.
"""
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class DocsPage(Base):
    __tablename__ = "docs_pages"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    category: Mapped[str] = mapped_column(
        String(64), default="notes", server_default="notes"
    )
    body: Mapped[str] = mapped_column(Text, default="", server_default="")
    # username snapshot — not a FK, survives user deletion and restore.
    created_by: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __changelog_repr__(self) -> str:
        return self.title or f"docs_page#{self.id}"
