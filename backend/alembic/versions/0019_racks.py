"""racks + rack_devices: native rack elevations with Rackula round-trip

racks is a site-scoped entity with the shared list-page columns
(sort_order/pinned/row_color). rack_devices holds one row per mounted
device: 1-based bottom U position, U height, and a face (front/rear/both)
from the rack_face PG enum. No unique constraint on (rack_id, u_position) —
front/rear pairs legally share a U slot; collisions are enforced in the
service layer. device links to assets/ip_addresses are SET NULL.

Revision ID: 0019_racks
Revises: 0018_custom_lists
Create Date: 2026-09-23
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0019_racks"
down_revision = "0018_custom_lists"
branch_labels = None
depends_on = None

rack_face = postgresql.ENUM(
    "front", "rear", "both", name="rack_face", create_type=False
)


def upgrade() -> None:
    op.execute("CREATE TYPE rack_face AS ENUM ('front','rear','both')")

    op.create_table(
        "racks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("site_id", sa.Integer(), sa.ForeignKey("sites.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("room", sa.String(255), nullable=True),
        sa.Column("height_u", sa.Integer(), server_default="42", nullable=False),
        sa.Column("width", sa.Integer(), server_default="19", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=True),
        sa.Column("pinned", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("row_color", sa.String(7), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_racks_site_id", "racks", ["site_id"])
    op.create_index("ix_racks_name", "racks", ["name"])
    op.create_index("ix_racks_sort_order", "racks", ["sort_order"])

    op.create_table(
        "rack_devices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("rack_id", sa.Integer(), sa.ForeignKey("racks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("device_type", sa.String(255), nullable=True),
        sa.Column("u_position", sa.Integer(), nullable=False),
        sa.Column("u_height", sa.Integer(), server_default="1", nullable=False),
        sa.Column("face", rack_face, server_default="front", nullable=False),
        sa.Column("colour", sa.String(7), nullable=True),
        sa.Column("category", sa.String(64), nullable=True),
        sa.Column("manufacturer", sa.String(255), nullable=True),
        sa.Column("model", sa.String(255), nullable=True),
        sa.Column("asset_id", sa.Integer(), sa.ForeignKey("assets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("ip_address_id", sa.Integer(), sa.ForeignKey("ip_addresses.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source", sa.String(16), server_default="manual", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_rack_devices_rack_id", "rack_devices", ["rack_id"])
    op.create_index("ix_rack_devices_rack_u", "rack_devices", ["rack_id", "u_position"])
    op.create_index("ix_rack_devices_asset_id", "rack_devices", ["asset_id"])
    op.create_index("ix_rack_devices_ip_address_id", "rack_devices", ["ip_address_id"])


def downgrade() -> None:
    op.drop_table("rack_devices")
    op.drop_table("racks")
    op.execute("DROP TYPE IF EXISTS rack_face")
