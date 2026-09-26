"""diagram_layouts — saved /topology canvas positions (V10)

The topology map lets users drag devices into a readable arrangement and
persist it. ``positions`` is a JSONB blob keyed by graph node id
("dev-12", "unlinked-55") so unknown/future node kinds round-trip
without a schema change. ``key`` scopes the layout ("main" today;
per-site keys later).

Revision ID: 0032_diagram_layouts
Revises: 0031_snmp_inventory
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0032_diagram_layouts"
down_revision = "0031_snmp_inventory"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "diagram_layouts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(64), nullable=False),
        sa.Column(
            "positions",
            postgresql.JSONB(),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_diagram_layouts_key", "diagram_layouts", ["key"], unique=True
    )


def downgrade() -> None:
    op.drop_index("ix_diagram_layouts_key", table_name="diagram_layouts")
    op.drop_table("diagram_layouts")
