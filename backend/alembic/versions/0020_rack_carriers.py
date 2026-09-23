"""rack_devices carriers: carrier_id self-FK + slot + slot_layout

A carrier is an ordinary rack-level rack_devices row flagged by a non-NULL
slot_layout ("halves" = 2 side-by-side slots, "quarters" = 4, "shelf" = 1
full-width tray). Children carry carrier_id -> the carrier row plus a `slot`
index into that layout; their u_position/face stay synced to the carrier's
(display-only). Single level: carriers can't themselves have carrier_id —
enforced in the service layer. A partial unique index on (carrier_id, slot)
enforces one child per slot; deleting a carrier cascades to its children.

Revision ID: 0020_rack_carriers
Revises: 0019_racks
Create Date: 2026-09-23
"""
from alembic import op
import sqlalchemy as sa

revision = "0020_rack_carriers"
down_revision = "0019_racks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "rack_devices",
        sa.Column(
            "carrier_id",
            sa.Integer(),
            sa.ForeignKey("rack_devices.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    op.add_column("rack_devices", sa.Column("slot", sa.Integer(), nullable=True))
    op.add_column(
        "rack_devices", sa.Column("slot_layout", sa.String(16), nullable=True)
    )
    op.create_index("ix_rack_devices_carrier_id", "rack_devices", ["carrier_id"])
    op.create_index(
        "ix_rack_devices_carrier_slot",
        "rack_devices",
        ["carrier_id", "slot"],
        unique=True,
        postgresql_where=sa.text("carrier_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("ix_rack_devices_carrier_slot", table_name="rack_devices")
    op.drop_index("ix_rack_devices_carrier_id", table_name="rack_devices")
    op.drop_column("rack_devices", "slot_layout")
    op.drop_column("rack_devices", "slot")
    op.drop_column("rack_devices", "carrier_id")
