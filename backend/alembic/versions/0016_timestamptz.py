"""timestamptz for every datetime column

All datetime columns become TIMESTAMP WITH TIME ZONE. Existing naive values
are reinterpreted as UTC (the application always wrote wall-clock UTC via
datetime.utcnow()): `col AT TIME ZONE 'UTC'` attaches the UTC offset without
shifting the instant. Downgrade converts back with the same interpretation.

Revision ID: 0016_timestamptz
Revises: 0015_tag_assignments_gc
Create Date: 2026-09-19
"""
from alembic import op

revision = "0016_timestamptz"
down_revision = "0015_tag_assignments_gc"
branch_labels = None
depends_on = None

# (table, column) — every DateTime column in the schema
_COLS = [
    ("app_settings", "updated_at"),
    ("assets", "created_at"),
    ("certificates", "created_at"),
    ("change_log", "ts"),
    ("circuits", "created_at"),
    ("color_rules", "created_at"),
    ("import_batches", "created_at"),
    ("import_batches", "committed_at"),
    ("ip_addresses", "created_at"),
    ("ip_addresses", "updated_at"),
    ("ip_addresses", "last_seen"),
    ("ip_ranges", "created_at"),
    ("prefixes", "created_at"),
    ("scan_jobs", "created_at"),
    ("scan_jobs", "started_at"),
    ("scan_jobs", "finished_at"),
    ("services", "created_at"),
    ("sites", "created_at"),
    ("tags", "created_at"),
    ("users", "created_at"),
    ("vlans", "created_at"),
    ("vlan_groups", "created_at"),
    ("vrfs", "created_at"),
]


def upgrade() -> None:
    for table, col in _COLS:
        op.execute(
            f"ALTER TABLE {table} ALTER COLUMN {col} TYPE timestamptz "
            f"USING {col} AT TIME ZONE 'UTC'"
        )


def downgrade() -> None:
    for table, col in _COLS:
        op.execute(
            f"ALTER TABLE {table} ALTER COLUMN {col} TYPE timestamp "
            f"USING {col} AT TIME ZONE 'UTC'"
        )
