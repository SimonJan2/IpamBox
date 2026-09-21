"""one-time sweep of orphaned tag_assignments

Revision ID: 0015_tag_assignments_gc
Revises: 0014_row_colors
Create Date: 2026-09-21

tag_assignments.object_id has no FK (polymorphic target), so rows whose
Site/VRF/Prefix/IPAddress was deleted before the runtime cascade existed
are dangling — and TRUNCATE RESTART IDENTITY paths can re-attach them to
unrelated rows when ids are reused. Delete them once here; the flush hook
in app.core.tag_refs prevents new ones and restore sweeps on load.
"""
from alembic import op

revision = "0015_tag_assignments_gc"
down_revision = "0014_row_colors"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DELETE FROM tag_assignments WHERE
            (object_type = 'Site'      AND object_id NOT IN (SELECT id FROM sites))
         OR (object_type = 'VRF'       AND object_id NOT IN (SELECT id FROM vrfs))
         OR (object_type = 'Prefix'    AND object_id NOT IN (SELECT id FROM prefixes))
         OR (object_type = 'IPAddress' AND object_id NOT IN (SELECT id FROM ip_addresses))
         OR object_type NOT IN ('Site', 'VRF', 'Prefix', 'IPAddress')
        """
    )


def downgrade() -> None:
    # deleted orphans can't be reconstructed
    pass
