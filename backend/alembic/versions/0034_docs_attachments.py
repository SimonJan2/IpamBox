"""docs_pages + attachments — user-authored docs and entity files (V13)

``docs_pages`` stores operator-written markdown pages rendered under
/docs/pages/ beside the builtin help registry. ``attachments`` stores file
blobs (BYTEA — Postgres keeps backup/restore atomic and ID-preserving)
keyed polymorphically by (entity_type, entity_id); core.attachment_refs
sweeps rows when the owning entity is deleted.

Revision ID: 0034_docs_attachments
Revises: 0033_device_templates
"""
import sqlalchemy as sa
from alembic import op

revision = "0034_docs_attachments"
down_revision = "0033_device_templates"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "docs_pages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False),
        sa.Column(
            "category", sa.String(64), server_default="notes", nullable=False
        ),
        sa.Column("body", sa.Text(), server_default="", nullable=False),
        sa.Column("created_by", sa.String(255)),
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
    op.create_index("ix_docs_pages_slug", "docs_pages", ["slug"], unique=True)

    op.create_table(
        "attachments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entity_type", sa.String(32), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(255)),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("content_type", sa.String(128), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column("blob", sa.LargeBinary(), nullable=False),
        sa.Column("uploaded_by", sa.String(255)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_attachments_entity_type", "attachments", ["entity_type"]
    )
    op.create_index("ix_attachments_entity_id", "attachments", ["entity_id"])
    # The hot lookup — "attachments for this entity" filters on the pair.
    op.create_index(
        "ix_attachments_entity", "attachments", ["entity_type", "entity_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_attachments_entity", table_name="attachments")
    op.drop_index("ix_attachments_entity_id", table_name="attachments")
    op.drop_index("ix_attachments_entity_type", table_name="attachments")
    op.drop_table("attachments")
    op.drop_index("ix_docs_pages_slug", table_name="docs_pages")
    op.drop_table("docs_pages")
