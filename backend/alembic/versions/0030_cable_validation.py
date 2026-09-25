"""cable_validation — observed L1 evidence blob on device_interfaces

One column: ``device_interfaces.validation`` (JSONB, nullable). The
cable-validation pass at the tail of each SNMP poll keeps the interface's
observed L1 evidence together here:

    {cable_mismatch: {reason, detail, at, ...},
     lldp: [{remote_name, remote_port, remote_mac, ...}],
     macs_seen: [<mac>, ...] (bounded ~32),
     notes: [...],
     checked_at}

The flag itself is ``validation["cable_mismatch"]`` — queryable via
``has_key`` exactly like ``mac_mismatch`` on ip_addresses.custom_fields.
Observed state — changelog-skipped like the rest of the snmp_* family,
so the migration is column-only and backup/restore needs nothing extra.

Revision ID: 0030_cable_validation
Revises: 0029_snmp_traps
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0030_cable_validation"
down_revision = "0029_snmp_traps"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "device_interfaces",
        sa.Column("validation", postgresql.JSONB(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("device_interfaces", "validation")
