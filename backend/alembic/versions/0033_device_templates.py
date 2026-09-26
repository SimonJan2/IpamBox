"""device_templates — reusable typed port layouts (V10.1)

A template row stores a device profile (manufacturer/model/u_height/…) plus
a JSONB port list stamped onto devices by apply-template / instantiate.
`interfaces` entries are {name, kind, speed_mbps?, position?, pair?};
`power_ports` entries are {name} — both are data, validated at the schema
layer (kind must be an interface_kind value), so the table stays honest
without per-vendor logic.

Revision ID: 0033_device_templates
Revises: 0032_diagram_layouts
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0033_device_templates"
down_revision = "0032_diagram_layouts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "device_templates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("manufacturer", sa.String(255)),
        sa.Column("model", sa.String(255)),
        sa.Column("device_type", sa.String(255)),
        sa.Column("u_height", sa.Integer(), server_default="1", nullable=False),
        sa.Column(
            "face_default",
            sa.String(8),
            server_default="front",
            nullable=False,
        ),
        sa.Column("colour", sa.String(7)),
        sa.Column("category", sa.String(64)),
        sa.Column("watts", sa.Integer()),
        sa.Column("weight_kg", sa.Numeric(7, 2)),
        sa.Column(
            "interfaces",
            postgresql.JSONB(),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("power_ports", postgresql.JSONB()),
        sa.Column(
            "source", sa.String(16), server_default="manual", nullable=False
        ),
        sa.Column("notes", sa.Text()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
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
        "ix_device_templates_name", "device_templates", ["name"]
    )


def downgrade() -> None:
    op.drop_index("ix_device_templates_name", table_name="device_templates")
    op.drop_table("device_templates")
