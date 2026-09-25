"""ip_addresses.source — provenance column (V6)

Adds the field-ownership column every later writer (snmp/integration)
respects. Vocabulary is by convention, same as devices.source:
manual|import|scan|snmp|integration.

Backfill is honest, not clever: only imported rows are distinguishable
(import_batch_id was stamped by the workbook importer), so they become
'import' and everything else stays the 'manual' server default — rows the
scanner merely touched were indistinguishable from manual entries. The
reconcile writer stamps 'scan' on rows it creates from here on.

Revision ID: 0024_ip_source
Revises: 0023_interfaces_cables
Create Date: 2026-09-25
"""
import sqlalchemy as sa
from alembic import op

revision = "0024_ip_source"
down_revision = "0023_interfaces_cables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ip_addresses",
        sa.Column(
            "source",
            sa.String(16),
            nullable=False,
            server_default="manual",
        ),
    )
    op.create_index("ix_ip_addresses_source", "ip_addresses", ["source"])
    # Idempotent: re-running this UPDATE leaves the same state.
    op.execute(
        "UPDATE ip_addresses SET source = 'import' "
        "WHERE import_batch_id IS NOT NULL AND source <> 'import'"
    )


def downgrade() -> None:
    op.drop_index("ix_ip_addresses_source", table_name="ip_addresses")
    op.drop_column("ip_addresses", "source")
