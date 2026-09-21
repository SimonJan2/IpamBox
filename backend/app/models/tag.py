from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    color: Mapped[str] = mapped_column(String(7), default="#10b981", server_default="#10b981")
    description: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int | None] = mapped_column(index=True)
    pinned: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    assignments: Mapped[list["TagAssignment"]] = relationship(
        back_populates="tag", cascade="all, delete-orphan"
    )


class TagAssignment(Base):
    """Polymorphic tag link — attaches a Tag to a Site/VRF/Prefix/IPAddress."""

    __tablename__ = "tag_assignments"

    id: Mapped[int] = mapped_column(primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), index=True)
    object_type: Mapped[str] = mapped_column(String(32))  # model class name
    object_id: Mapped[int] = mapped_column(Integer)

    tag: Mapped[Tag] = relationship(back_populates="assignments")

    __table_args__ = (
        UniqueConstraint("tag_id", "object_type", "object_id", name="uq_tag_assignment"),
        Index("ix_tag_assignments_object", "object_type", "object_id"),
    )

    def __changelog_repr__(self) -> str:
        return f"tag#{self.tag_id} on {self.object_type}#{self.object_id}"
