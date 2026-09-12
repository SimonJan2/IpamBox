"""users table for dashboard auth

Revision ID: 0003_auth
Revises: 0002_container_overlap
Create Date: 2026-09-13

"""
from alembic import op
import sqlalchemy as sa

revision = "0003_auth"
down_revision = "0002_container_overlap"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(64), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)


def downgrade() -> None:
    op.drop_table("users")
