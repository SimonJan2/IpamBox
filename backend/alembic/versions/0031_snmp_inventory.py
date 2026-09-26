"""snmp_inventory — import_batches.kind batch-kind vocabulary

V8.3 lets a switch teach IpamBox its VLANs/subnets/ARP neighbors through
the same previewed-commit machinery the workbook importer uses. The apply
still creates an ``import_batches`` row for provenance — but the source
isn't a file, so the batch gains ``kind`` ('workbook' keeps meaning what
it always did; 'snmp' marks a device-inventory sync). ``stored_path``
carries a ``snmp://device/<id>`` sentinel for snmp batches and the raw
walk snapshot lives in ``stats['snapshot']`` — the audit trail matches
the file-import shape without pretending a file exists.

Revision ID: 0031_snmp_inventory
Revises: 0030_cable_validation
"""
import sqlalchemy as sa
from alembic import op

revision = "0031_snmp_inventory"
down_revision = "0030_cable_validation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "import_batches",
        sa.Column(
            "kind",
            sa.String(16),
            server_default="workbook",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("import_batches", "kind")
