"""Review center (V7.1): operator dismissals for computed findings.

Every review section is a live query — nothing is stored for the finding
itself. A dismissal is the only persisted state: "I've seen this exact
thing, don't queue it again". The (kind, entity_type, entity_id,
fingerprint) tuple identifies WHAT was ignored — for a MAC mismatch that's
the was→seen pair, so a scanner re-flag of the same pair stays suppressed
while a new MAC pair resurfaces as a fresh item.
"""
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ReviewDismissal(Base):
    __tablename__ = "review_dismissals"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Section key producing the item: mac_mismatch, dup_mac,
    # aging_discovery, offline, cert_expiry, unmatched_switch, uncabled,
    # unracked — future writers add kinds without a schema change.
    kind: Mapped[str] = mapped_column(String(32))
    entity_type: Mapped[str] = mapped_column(String(32))
    # 0 for virtual entities (a dup-MAC group has no single row id).
    entity_id: Mapped[int] = mapped_column(Integer)
    # The stable thing being ignored (the MAC pair, the switch/port text…).
    fingerprint: Mapped[str] = mapped_column(String(255), default="", server_default="")
    # Same actor convention as the changelog (app.core.security.get_actor).
    actor: Mapped[str] = mapped_column(String(255), default="system", server_default="system")
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "kind",
            "entity_type",
            "entity_id",
            "fingerprint",
            name="uq_review_dismissals_key",
        ),
    )

    def __changelog_repr__(self) -> str:
        return f"{self.kind} {self.entity_type}#{self.entity_id}"
