from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChangeField(BaseModel):
    field: str
    before: object = None
    after: object = None


class ChangeLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ts: datetime
    actor: str
    action: str
    object_type: str
    object_id: int | None
    object_repr: str
    changes: list[ChangeField]
