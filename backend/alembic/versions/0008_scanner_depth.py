"""Scanner depth: open_ports + device_type on addresses, cancelled scan status

Revision ID: 0008_scanner_depth
Revises: 0007_ranges_roles_nat
Create Date: 2026-09-13

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0008_scanner_depth"
down_revision = "0007_ranges_roles_nat"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE scan_status ADD VALUE IF NOT EXISTS 'cancelled'")
    op.add_column(
        "ip_addresses",
        sa.Column("open_ports", postgresql.ARRAY(sa.Integer()), nullable=True),
    )
    op.add_column(
        "ip_addresses",
        sa.Column("device_type", sa.String(32), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("ip_addresses", "device_type")
    op.drop_column("ip_addresses", "open_ports")
    # note: enum values cannot be removed; 'cancelled' remains in scan_status
