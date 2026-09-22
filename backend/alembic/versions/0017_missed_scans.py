"""missed_scans on ip_addresses — offline-grace hysteresis counter

Counts consecutive scans where the host was absent. Drives the
scan_offline_grace_scans feature (Settings > Features): a host only flips to
OFFLINE once its miss count reaches the configured threshold. server_default
keeps existing rows at 0 without a table rewrite; the column is changelog-
skipped (churn-only, like last_seen).

Revision ID: 0017_missed_scans
Revises: 0016_timestamptz
Create Date: 2026-09-22
"""
from alembic import op
import sqlalchemy as sa

revision = "0017_missed_scans"
down_revision = "0016_timestamptz"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ip_addresses",
        sa.Column(
            "missed_scans", sa.Integer(), server_default="0", nullable=False
        ),
    )


def downgrade() -> None:
    op.drop_column("ip_addresses", "missed_scans")
