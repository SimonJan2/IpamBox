"""snmp_traps — last-trap stamp for the V8.1 receiver

One column: ``devices.snmp_last_trap_at`` records when the trap
listener last handled a trap attributable to this device (the SNMP
card's "last trap" line). Observed state — changelog-skipped like the
rest of the snmp_last_* family, so the migration is column-only and
backup/restore needs nothing extra.

Revision ID: 0029_snmp_traps
Revises: 0028_snmp
"""
import sqlalchemy as sa
from alembic import op

revision = "0029_snmp_traps"
down_revision = "0028_snmp"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "devices",
        sa.Column(
            "snmp_last_trap_at", sa.DateTime(timezone=True), nullable=True
        ),
    )


def downgrade() -> None:
    op.drop_column("devices", "snmp_last_trap_at")
