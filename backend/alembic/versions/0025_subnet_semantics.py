"""subnet semantics — prefix gateway/DNS + address->range link (V6.1)

`prefixes` learns its technical addresses: a nullable `gateway` INET and a
nullable `dns_servers` ARRAY(INET) — Postgres-native, same ARRAY style as
ip_addresses.open_ports but of INET. `ip_addresses` learns `ip_range_id` —
"this address lives inside this pool" — FK to ip_ranges with SET NULL so
deleting a range frees its members without deleting them.

Backfill is idempotent: rows inside an existing range get linked by a
bounded UPDATE keyed on the int columns; re-running it is a no-op (only
NULL links are written).

Revision ID: 0025_subnet_semantics
Revises: 0024_ip_source
Create Date: 2026-09-27
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0025_subnet_semantics"
down_revision = "0024_ip_source"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("prefixes", sa.Column("gateway", postgresql.INET(), nullable=True))
    op.add_column(
        "prefixes",
        sa.Column("dns_servers", postgresql.ARRAY(postgresql.INET()), nullable=True),
    )
    op.add_column(
        "ip_addresses",
        sa.Column(
            "ip_range_id",
            sa.Integer(),
            sa.ForeignKey("ip_ranges.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index("ix_ip_addresses_ip_range_id", "ip_addresses", ["ip_range_id"])
    # Idempotent: only fills NULL links; re-run leaves the same state.
    op.execute(
        """
        UPDATE ip_addresses a
        SET ip_range_id = r.id
        FROM ip_ranges r
        WHERE a.ip_range_id IS NULL
          AND r.prefix_id = a.prefix_id
          AND a.address_int BETWEEN r.start_int AND r.end_int
        """
    )


def downgrade() -> None:
    op.drop_index("ix_ip_addresses_ip_range_id", table_name="ip_addresses")
    op.drop_column("ip_addresses", "ip_range_id")
    op.drop_column("prefixes", "dns_servers")
    op.drop_column("prefixes", "gateway")
