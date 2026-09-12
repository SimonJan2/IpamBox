"""allow children inside container prefixes

Revision ID: 0002_container_overlap
Revises: 0001_initial
Create Date: 2026-09-12

Exclusion constraint now only applies to non-container rows, matching
NetBox-style semantics: a 'container' prefix may contain other prefixes,
while non-container prefixes may never overlap inside the same VRF.
"""
from alembic import op

revision = "0002_container_overlap"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE prefixes DROP CONSTRAINT IF EXISTS excl_prefixes_no_overlap_same_vrf"
    )
    op.execute(
        "ALTER TABLE prefixes ADD CONSTRAINT excl_prefixes_no_overlap_same_vrf "
        "EXCLUDE USING gist (vrf_id WITH =, prefix inet_ops WITH &&) "
        "WHERE (status <> 'container')"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE prefixes DROP CONSTRAINT IF EXISTS excl_prefixes_no_overlap_same_vrf"
    )
    op.execute(
        "ALTER TABLE prefixes ADD CONSTRAINT excl_prefixes_no_overlap_same_vrf "
        "EXCLUDE USING gist (vrf_id WITH =, prefix inet_ops WITH &&)"
    )
