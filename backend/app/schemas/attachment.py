from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AttachmentOut(BaseModel):
    """Metadata only — blob bytes are never serialized here; the download
    endpoint streams them directly."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    entity_type: str
    entity_id: int
    label: str | None
    filename: str
    content_type: str
    size: int
    uploaded_by: str | None
    created_at: datetime
