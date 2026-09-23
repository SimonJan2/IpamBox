"""rack_groups + racks.group_id/group_position + rack_devices watts/weight_kg

Rack groups model a bayed row: racks stand side by side in a datacenter, so
a group is an ordered set of racks rendered as one horizontal elevation
strip. racks.group_id (SET NULL) + group_position (1-based, left to right)
carry the membership and order; a composite (group_id, group_position) index
keeps row lookups cheap.

rack_devices gains watts (nameplate draw) and weight_kg so racks and groups
can roll up power/load for the capacity dashboard.

Revision ID: 0021_rack_groups
Revises: 0020_rack_carriers
Create Date: 2026-09-24
"""
from alembic import op
import sqlalchemy as sa

revision = "0021_rack_groups"
down_revision = "0020_rack_carriers"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rack_groups",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "site_id",
            sa.Integer(),
            sa.ForeignKey("sites.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=True),
        sa.Column(
            "pinned",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("row_color", sa.String(length=7), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_rack_groups_site_id", "rack_groups", ["site_id"])
    op.create_index("ix_rack_groups_name", "rack_groups", ["name"])
    op.create_index("ix_rack_groups_sort_order", "rack_groups", ["sort_order"])

    op.add_column(
        "racks",
        sa.Column(
            "group_id",
            sa.Integer(),
            sa.ForeignKey("rack_groups.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column(
        "racks",
        sa.Column("group_position", sa.Integer(), nullable=True),
    )
    op.create_index("ix_racks_group_id", "racks", ["group_id"])
    op.create_index(
        "ix_racks_group_pos", "racks", ["group_id", "group_position"]
    )

    op.add_column(
        "rack_devices",
        sa.Column("watts", sa.Integer(), nullable=True),
    )
    op.add_column(
        "rack_devices",
        sa.Column("weight_kg", sa.Numeric(7, 2), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("rack_devices", "weight_kg")
    op.drop_column("rack_devices", "watts")

    op.drop_index("ix_racks_group_pos", table_name="racks")
    op.drop_index("ix_racks_group_id", table_name="racks")
    op.drop_column("racks", "group_position")
    op.drop_column("racks", "group_id")

    op.drop_index("ix_rack_groups_sort_order", table_name="rack_groups")
    op.drop_index("ix_rack_groups_name", table_name="rack_groups")
    op.drop_index("ix_rack_groups_site_id", table_name="rack_groups")
    op.drop_table("rack_groups")
