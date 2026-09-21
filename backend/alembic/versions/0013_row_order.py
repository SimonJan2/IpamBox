"""sort_order + pinned on the entity list tables — global manual row order

Revision ID: 0013_row_order
Revises: 0012_circuit_retired
Create Date: 2026-09-21

Each table gets:
- sort_order  Integer, indexed, NULL = "never positioned". NULLs sink to the
  end of their pin group (NULLS LAST), so fresh/imported rows append in id
  order without needing a position assigned at insert time.
- pinned      Boolean NOT NULL DEFAULT false — pinned rows float to the top.

Existing rows are backfilled with row_number() over the order their list page
showed before this feature, so the initial manual order matches what users
already saw (sites/vrfs/tags by name, vlans by vid, certificates by expiry —
their client-side default sort — the rest by insertion id).
"""
from alembic import op
import sqlalchemy as sa

revision = "0013_row_order"
down_revision = "0012_circuit_retired"
branch_labels = None
depends_on = None

# table -> ORDER BY used for the row_number() backfill
_TABLES: dict[str, str] = {
    "sites": "name ASC, id ASC",
    "vrfs": "name ASC, id ASC",
    "vlans": "vid ASC, id ASC",
    "circuits": "id ASC",
    "certificates": "expires_on ASC NULLS LAST, id ASC",
    "assets": "id ASC",
    "services": "id ASC",
    "tags": "name ASC, id ASC",
}


def upgrade() -> None:
    for table, order in _TABLES.items():
        op.add_column(table, sa.Column("sort_order", sa.Integer()))
        op.add_column(
            table,
            sa.Column(
                "pinned", sa.Boolean(), server_default=sa.false(), nullable=False
            ),
        )
        op.create_index(f"ix_{table}_sort_order", table, ["sort_order"])
        op.execute(
            f"UPDATE {table} SET sort_order = sub.rn FROM ("
            f"  SELECT id, row_number() OVER (ORDER BY {order}) AS rn"
            f"  FROM {table}"
            f") sub WHERE {table}.id = sub.id"
        )


def downgrade() -> None:
    for table in _TABLES:
        op.drop_index(f"ix_{table}_sort_order", table_name=table)
        op.drop_column(table, "pinned")
        op.drop_column(table, "sort_order")
