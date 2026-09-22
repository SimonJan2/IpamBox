"""custom lists: user-defined tables imported from workbook sheets

custom_lists holds the table def (name/slug + ordered JSONB column defs with
positional keys); custom_list_rows holds one JSONB data blob per row plus the
shared list-page columns (sort_order/pinned/row_color) and import provenance.
key_column marks the merge-identity column for re-import sync; manually_edited
protects UI-edited rows from being overwritten by a later import.

Revision ID: 0018_custom_lists
Revises: 0017_missed_scans
Create Date: 2026-09-22
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0018_custom_lists"
down_revision = "0017_missed_scans"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "custom_lists",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon", sa.String(64), nullable=True),
        sa.Column("columns", postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=True),
        sa.Column("key_column", sa.String(64), nullable=True),
        sa.Column("source_sheet", sa.String(255), nullable=True),
        sa.Column("import_batch_id", sa.Integer(), sa.ForeignKey("import_batches.id", ondelete="SET NULL"), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_custom_lists_name", "custom_lists", ["name"])
    op.create_index("ix_custom_lists_slug", "custom_lists", ["slug"], unique=True)
    op.create_index("ix_custom_lists_import_batch_id", "custom_lists", ["import_batch_id"])
    op.create_index("ix_custom_lists_sort_order", "custom_lists", ["sort_order"])

    op.create_table(
        "custom_list_rows",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("list_id", sa.Integer(), sa.ForeignKey("custom_lists.id", ondelete="CASCADE"), nullable=False),
        sa.Column("data", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=True),
        sa.Column("site_id", sa.Integer(), sa.ForeignKey("sites.id", ondelete="SET NULL"), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=True),
        sa.Column("pinned", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("row_color", sa.String(7), nullable=True),
        sa.Column("manually_edited", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("import_batch_id", sa.Integer(), sa.ForeignKey("import_batches.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_custom_list_rows_list_id", "custom_list_rows", ["list_id"])
    op.create_index("ix_custom_list_rows_site_id", "custom_list_rows", ["site_id"])
    op.create_index("ix_custom_list_rows_sort_order", "custom_list_rows", ["sort_order"])
    op.create_index("ix_custom_list_rows_import_batch_id", "custom_list_rows", ["import_batch_id"])


def downgrade() -> None:
    op.drop_table("custom_list_rows")
    op.drop_table("custom_lists")
