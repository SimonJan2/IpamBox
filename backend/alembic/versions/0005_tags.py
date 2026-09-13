"""tags + polymorphic tag assignments

Revision ID: 0005_tags
Revises: 0004_changelog
Create Date: 2026-09-13

"""
from alembic import op
import sqlalchemy as sa

revision = "0005_tags"
down_revision = "0004_changelog"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("slug", sa.String(64), nullable=False),
        sa.Column("color", sa.String(7), server_default="#10b981", nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_tags_name", "tags", ["name"], unique=True)
    op.create_index("ix_tags_slug", "tags", ["slug"], unique=True)

    op.create_table(
        "tag_assignments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "tag_id",
            sa.Integer(),
            sa.ForeignKey("tags.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("object_type", sa.String(32), nullable=False),
        sa.Column("object_id", sa.Integer(), nullable=False),
        sa.UniqueConstraint("tag_id", "object_type", "object_id", name="uq_tag_assignment"),
    )
    op.create_index("ix_tag_assignments_tag_id", "tag_assignments", ["tag_id"])
    op.create_index(
        "ix_tag_assignments_object", "tag_assignments", ["object_type", "object_id"]
    )


def downgrade() -> None:
    op.drop_table("tag_assignments")
    op.drop_table("tags")
