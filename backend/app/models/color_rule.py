from datetime import datetime

from sqlalchemy import Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ColorRule(Base):
    """One auto-coloring rule: <entity_type>.<field> <operator> <value> -> <color>.

    Global config (admin-managed). Rules are evaluated per entity_type in
    position order; the first match supplies a row's display_color when the
    row carries no manual row_color.
    """

    __tablename__ = "color_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    # API resource name of the list the rule colors: "sites", "addresses", …
    entity_type: Mapped[str] = mapped_column(String(32))
    field: Mapped[str] = mapped_column(String(64))  # column name on the model
    operator: Mapped[str] = mapped_column(String(16))  # eq/neq/contains/lt/gt/within_days
    value: Mapped[str] = mapped_column(String(255))
    color: Mapped[str] = mapped_column(String(7))  # #rrggbb — Tag.color format
    position: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    __table_args__ = (
        Index("ix_color_rules_scope", "entity_type", "position"),
    )

    def __changelog_repr__(self) -> str:
        return (
            f"{self.entity_type}.{self.field} {self.operator} "
            f"{self.value!r} -> {self.color}"
        )
