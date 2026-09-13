"""audit trail table

Revision ID: 0004_changelog
Revises: 0003_auth
Create Date: 2026-09-13

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004_changelog"
down_revision = "0003_auth"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "change_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ts", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("actor", sa.String(64), server_default="system", nullable=False),
        sa.Column("action", sa.String(16), nullable=False),
        sa.Column("object_type", sa.String(64), nullable=False),
        sa.Column("object_id", sa.Integer(), nullable=True),
        sa.Column("object_repr", sa.String(255), nullable=False),
        sa.Column("changes", postgresql.JSONB(), server_default="[]", nullable=False),
    )
    op.create_index("ix_change_log_ts", "change_log", ["ts"])
    op.create_index("ix_change_log_action", "change_log", ["action"])
    op.create_index("ix_change_log_object_type", "change_log", ["object_type"])
    op.create_index("ix_change_log_object_id", "change_log", ["object_id"])


def downgrade() -> None:
    op.drop_table("change_log")
