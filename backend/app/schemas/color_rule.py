from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.common import hex_color_or_none
from app.services.colors import COLORABLE, OPERATORS, validate_rule


class ColorRuleCreate(BaseModel):
    entity_type: str
    field: str = Field(min_length=1, max_length=64)
    operator: str
    value: str = Field(min_length=1, max_length=255)
    color: str

    @field_validator("entity_type")
    @classmethod
    def _entity(cls, v: str) -> str:
        if v not in COLORABLE:
            raise ValueError(f"entity_type must be one of {sorted(COLORABLE)}")
        return v

    @field_validator("operator")
    @classmethod
    def _op(cls, v: str) -> str:
        if v not in OPERATORS:
            raise ValueError(f"operator must be one of {list(OPERATORS)}")
        return v

    @field_validator("color")
    @classmethod
    def _color(cls, v: str) -> str:
        return hex_color_or_none(v) or v

    @model_validator(mode="after")
    def _field_ok(self):
        err = validate_rule(self.entity_type, self.field, self.operator, self.value)
        if err:
            raise ValueError(err)
        return self


class ColorRuleUpdate(BaseModel):
    field: str | None = Field(default=None, min_length=1, max_length=64)
    operator: str | None = None
    value: str | None = Field(default=None, min_length=1, max_length=255)
    color: str | None = None

    @field_validator("operator")
    @classmethod
    def _op(cls, v: str | None) -> str | None:
        if v is not None and v not in OPERATORS:
            raise ValueError(f"operator must be one of {list(OPERATORS)}")
        return v

    @field_validator("color")
    @classmethod
    def _color(cls, v: str | None) -> str | None:
        return hex_color_or_none(v)


class ColorRuleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    entity_type: str
    field: str
    operator: str
    value: str
    color: str
    position: int
    created_at: datetime


class RuleReorderBody(BaseModel):
    """POST /color-rules/reorder: rule ids of ONE entity_type in new order."""

    entity_type: str
    ids: list[int] = Field(min_length=1)


class RulePreviewOut(BaseModel):
    count: int
