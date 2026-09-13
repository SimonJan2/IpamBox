"""first-class VLANs: vlan_groups + vlans, migrate prefix vlan columns

Revision ID: 0006_vlans
Revises: 0005_tags
Create Date: 2026-09-13

Prefixes previously carried loose (vlan_id int, vlan_name text) columns.
This migration creates real VLAN rows for every distinct vid in use and
re-points prefixes.vlan_id at the new vlans table.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0006_vlans"
down_revision = "0005_tags"
branch_labels = None
depends_on = None

vlan_status = postgresql.ENUM(
    "active", "reserved", "deprecated", name="vlan_status", create_type=False
)


def upgrade() -> None:
    op.execute("CREATE TYPE vlan_status AS ENUM ('active','reserved','deprecated')")

    op.create_table(
        "vlan_groups",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_vlan_groups_name", "vlan_groups", ["name"], unique=True)

    op.create_table(
        "vlans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("vid", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column(
            "group_id",
            sa.Integer(),
            sa.ForeignKey("vlan_groups.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "site_id",
            sa.Integer(),
            sa.ForeignKey("sites.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("status", vlan_status, server_default=sa.text("'active'"), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("vid BETWEEN 1 AND 4094", name="ck_vlans_vid_range"),
    )
    op.create_index("ix_vlans_vid", "vlans", ["vid"])
    op.create_index("ix_vlans_group_id", "vlans", ["group_id"])
    op.create_index("ix_vlans_site_id", "vlans", ["site_id"])

    # Move prefix vlan data: old columns -> real VLAN rows -> FK column.
    op.execute("ALTER TABLE prefixes DROP CONSTRAINT IF EXISTS ck_prefixes_vlan_range")
    op.execute("ALTER TABLE prefixes RENAME COLUMN vlan_id TO vlan_vid")
    op.add_column(
        "prefixes",
        sa.Column(
            "vlan_id",
            sa.Integer(),
            sa.ForeignKey("vlans.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.execute(
        "INSERT INTO vlans (vid, name) "
        "SELECT DISTINCT vlan_vid, COALESCE(vlan_name, 'VLAN ' || vlan_vid) "
        "FROM prefixes WHERE vlan_vid IS NOT NULL"
    )
    op.execute(
        "UPDATE prefixes p SET vlan_id = v.id "
        "FROM vlans v WHERE v.vid = p.vlan_vid"
    )
    op.execute("ALTER TABLE prefixes DROP COLUMN vlan_vid")
    op.execute("ALTER TABLE prefixes DROP COLUMN vlan_name")
    op.create_index("ix_prefixes_vlan_id", "prefixes", ["vlan_id"])


def downgrade() -> None:
    op.add_column(
        "prefixes",
        sa.Column("vlan_vid", sa.Integer(), nullable=True),
    )
    op.add_column(
        "prefixes",
        sa.Column("vlan_name", sa.String(255), nullable=True),
    )
    op.execute(
        "UPDATE prefixes p SET vlan_vid = v.vid, vlan_name = v.name "
        "FROM vlans v WHERE v.id = p.vlan_id"
    )
    op.execute("ALTER TABLE prefixes DROP COLUMN vlan_id")
    op.execute("ALTER TABLE prefixes RENAME COLUMN vlan_vid TO vlan_id")
    op.drop_table("vlans")
    op.drop_table("vlan_groups")
    op.execute("DROP TYPE IF EXISTS vlan_status")
