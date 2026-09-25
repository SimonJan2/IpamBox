"""Review queue (V7.1) — one triage surface over every computed finding."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReviewItem(BaseModel):
    """One flagged thing, shaped for the single table component.

    (kind of the parent section) + entity_type + entity_id + fingerprint is
    the dismissal key — POST /review/dismiss takes the same tuple back.
    """

    entity_type: str
    entity_id: int
    label: str
    sub: str | None = None
    detail: dict = Field(default_factory=dict)
    flagged_at: str | None = None
    fingerprint: str = ""
    # Populated only on entries of a section's `dismissed` list.
    dismissed_at: datetime | None = None
    dismissed_by: str | None = None
    dismiss_notes: str | None = None


class ReviewSection(BaseModel):
    key: str
    title: str
    # Honest open-item count — `items`/`dismissed` are each capped.
    count: int
    items: list[ReviewItem] = []
    dismissed: list[ReviewItem] = []
    # Set when a section is inert by configuration (e.g. aging disabled).
    note: str | None = None


class ReviewOut(BaseModel):
    sections: list[ReviewSection]


class DismissBody(BaseModel):
    """POST /review/dismiss + /review/undismiss — the dismissal key tuple."""

    kind: str = Field(min_length=1, max_length=32)
    entity_type: str = Field(min_length=1, max_length=32)
    entity_id: int
    fingerprint: str = Field(default="", max_length=255)
    notes: str | None = None


class ReviewDismissalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    kind: str
    entity_type: str
    entity_id: int
    fingerprint: str
    actor: str
    notes: str | None
    created_at: datetime
