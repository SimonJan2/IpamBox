"""row_color on the entity tables + ip_addresses, and the color_rules table

Revision ID: 0014_row_colors
Revises: 0013_row_order
Create Date: 2026-09-21

row_color is a nullable #rrggbb hex string (same format as Tag.color): a
manual per-row accent, global for all users. NULL = no manual color.

color_rules drives rule-based auto-coloring ("cert expiring <7d -> red"):
the first rule (lowest position) matching a row supplies its computed
display_color when the row has no manual row_color. Rules are global
config, managed by admins and evaluated server-side on list/get.
"""
from alembic import op
import sqlalchemy as sa

revision = "0014_row_colors"
down_revision = "0013_row_order"
branch_labels = None
depends_on = None

# The entity list tables + the address list. Prefixes are deliberately
# absent — the subnet grid's status colors own that surface.
_TABLES = (
    "sites",
    "vrfs",
    "vlans",
    "circuits",
    "certificates",
    "assets",
    "services",
    "tags",
    "ip_addresses",
)


def upgrade() -> None:
    for table in _TABLES:
        op.add_column(table, sa.Column("row_color", sa.String(7)))

    op.create_table(
        "color_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entity_type", sa.String(32), nullable=False),
        sa.Column("field", sa.String(64), nullable=False),
        sa.Column("operator", sa.String(16), nullable=False),
        sa.Column("value", sa.String(255), nullable=False),
        sa.Column("color", sa.String(7), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index(
        "ix_color_rules_scope", "color_rules", ["entity_type", "position"]
    )


def downgrade() -> None:
    op.drop_index("ix_color_rules_scope", table_name="color_rules")
    op.drop_table("color_rules")
    for table in _TABLES:
        op.drop_column(table, "row_color")
