"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-12

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

prefix_status = postgresql.ENUM(
    "container", "active", "reserved", "deprecated", name="prefix_status", create_type=False
)
ip_status = postgresql.ENUM(
    "active", "reserved", "dhcp", "discovered", "offline", name="ip_status", create_type=False
)
scan_status = postgresql.ENUM(
    "queued", "running", "completed", "failed", name="scan_status", create_type=False
)


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")

    op.execute("CREATE TYPE prefix_status AS ENUM ('container','active','reserved','deprecated')")
    op.execute("CREATE TYPE ip_status AS ENUM ('active','reserved','dhcp','discovered','offline')")
    op.execute("CREATE TYPE scan_status AS ENUM ('queued','running','completed','failed')")

    op.create_table(
        "sites",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_sites_name", "sites", ["name"], unique=True)
    op.create_index("ix_sites_slug", "sites", ["slug"], unique=True)

    op.create_table(
        "vrfs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("rd", sa.String(64), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("site_id", sa.Integer(), sa.ForeignKey("sites.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_vrfs_name", "vrfs", ["name"], unique=True)
    op.create_index("ix_vrfs_rd", "vrfs", ["rd"], unique=True)
    op.create_index("ix_vrfs_site_id", "vrfs", ["site_id"])

    op.create_table(
        "prefixes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("prefix", postgresql.CIDR(), nullable=False),
        sa.Column("vrf_id", sa.Integer(), sa.ForeignKey("vrfs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("site_id", sa.Integer(), sa.ForeignKey("sites.id", ondelete="SET NULL"), nullable=True),
        sa.Column("vlan_id", sa.Integer(), nullable=True),
        sa.Column("vlan_name", sa.String(255), nullable=True),
        sa.Column("status", prefix_status, server_default=sa.text("'active'"), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "vlan_id IS NULL OR (vlan_id BETWEEN 1 AND 4094)", name="ck_prefixes_vlan_range"
        ),
    )
    op.create_index("ix_prefixes_vrf_id", "prefixes", ["vrf_id"])
    op.create_index("ix_prefixes_site_id", "prefixes", ["site_id"])
    op.create_index("ix_prefixes_prefix", "prefixes", ["prefix"])
    op.create_index("ix_prefixes_prefix_gist", "prefixes", ["prefix"], postgresql_using="gist", postgresql_ops={"prefix": "inet_ops"})

    # Hard guarantee: CIDRs may overlap across VRFs but never inside one VRF.
    op.execute(
        "ALTER TABLE prefixes ADD CONSTRAINT excl_prefixes_no_overlap_same_vrf "
        "EXCLUDE USING gist (vrf_id WITH =, prefix inet_ops WITH &&)"
    )

    op.create_table(
        "ip_addresses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("address", postgresql.INET(), nullable=False),
        sa.Column("address_int", sa.Numeric(39, 0), nullable=False),
        sa.Column("prefix_id", sa.Integer(), sa.ForeignKey("prefixes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("vrf_id", sa.Integer(), sa.ForeignKey("vrfs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mac_address", sa.String(17), nullable=True),
        sa.Column("vendor", sa.String(255), nullable=True),
        sa.Column("hostname", sa.String(255), nullable=True),
        sa.Column("status", ip_status, server_default=sa.text("'discovered'"), nullable=False),
        sa.Column("last_seen", sa.DateTime(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("vrf_id", "address", name="uq_ip_addresses_vrf_address"),
    )
    op.create_index("ix_ip_addresses_address_int", "ip_addresses", ["address_int"])
    op.create_index("ix_ip_addresses_prefix_int", "ip_addresses", ["prefix_id", "address_int"])
    op.create_index("ix_ip_addresses_prefix_id", "ip_addresses", ["prefix_id"])
    op.create_index("ix_ip_addresses_vrf_id", "ip_addresses", ["vrf_id"])
    op.create_index("ix_ip_addresses_status", "ip_addresses", ["status"])

    op.create_table(
        "scan_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("arq_job_id", sa.String(64), nullable=True),
        sa.Column("cidr", sa.String(64), nullable=False),
        sa.Column("vrf_id", sa.Integer(), sa.ForeignKey("vrfs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("prefix_id", sa.Integer(), sa.ForeignKey("prefixes.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", scan_status, server_default=sa.text("'queued'"), nullable=False),
        sa.Column("progress", sa.Float(), server_default=sa.text("0"), nullable=False),
        sa.Column("total_hosts", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("hosts_discovered", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("hosts_new", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_scan_jobs_status", "scan_jobs", ["status"])
    op.create_index("ix_scan_jobs_vrf_id", "scan_jobs", ["vrf_id"])
    op.create_index("ix_scan_jobs_prefix_id", "scan_jobs", ["prefix_id"])

    # Seed the default Global VRF (no RD).
    op.execute(
        "INSERT INTO vrfs (name, rd, description) "
        "VALUES ('Global', NULL, 'Default global routing table') ON CONFLICT DO NOTHING"
    )


def downgrade() -> None:
    op.drop_table("scan_jobs")
    op.drop_table("ip_addresses")
    op.execute("ALTER TABLE prefixes DROP CONSTRAINT IF EXISTS excl_prefixes_no_overlap_same_vrf")
    op.drop_table("prefixes")
    op.drop_table("vrfs")
    op.drop_table("sites")
    op.execute("DROP TYPE IF EXISTS scan_status")
    op.execute("DROP TYPE IF EXISTS ip_status")
    op.execute("DROP TYPE IF EXISTS prefix_status")
