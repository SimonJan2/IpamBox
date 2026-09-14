"""users.role — 4-tier RBAC (admin/operator/contributor/viewer)

Existing accounts become admin (they were all full admins already).

Revision ID: 0010_user_roles
Revises: 0009_app_settings
Create Date: 2026-09-14

"""
from alembic import op
import sqlalchemy as sa

revision = "0010_user_roles"
down_revision = "0009_app_settings"
branch_labels = None
depends_on = None

user_role = sa.Enum("admin", "operator", "contributor", "viewer", name="user_role")


def upgrade() -> None:
    user_role.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "users",
        sa.Column("role", user_role, nullable=False, server_default="admin"),
    )


def downgrade() -> None:
    op.drop_column("users", "role")
    user_role.drop(op.get_bind(), checkfirst=True)
