"""IP ranges + address roles + NAT inside link

Revision ID: 0007_ranges_roles_nat
Revises: 0006_vlans
Create Date: 2026-09-13

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0007_ranges_roles_nat"
down_revision = "0006_vlans"
branch_labels = None
depends_on = None

range_role = postgresql.ENUM("dhcp", "pool", "reserved", name="range_role", create_type=False)
ip_role = postgresql.ENUM(
    "vip", "vrrp", "hsrp", "glbp", "carp", "secondary", name="ip_role", create_type=False
)


def upgrade() -> None:
    op.execute("CREATE TYPE range_role AS ENUM ('dhcp','pool','reserved')")
    op.execute(
        "CREATE TYPE ip_role AS ENUM ('vip','vrrp','hsrp','glbp','carp','secondary')"
    )

    op.create_table(
        "ip_ranges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "prefix_id",
            sa.Integer(),
            sa.ForeignKey("prefixes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "vrf_id",
            sa.Integer(),
            sa.ForeignKey("vrfs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("start_address", postgresql.INET(), nullable=False),
        sa.Column("start_int", sa.Numeric(39, 0), nullable=False),
        sa.Column("end_address", postgresql.INET(), nullable=False),
        sa.Column("end_int", sa.Numeric(39, 0), nullable=False),
        sa.Column("role", range_role, server_default=sa.text("'dhcp'"), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("start_int <= end_int", name="ck_ip_ranges_order"),
    )
    op.create_index("ix_ip_ranges_prefix_id", "ip_ranges", ["prefix_id"])
    op.create_index("ix_ip_ranges_vrf_id", "ip_ranges", ["vrf_id"])

    op.add_column(
        "ip_addresses",
        sa.Column("role", ip_role, nullable=True),
    )
    op.add_column(
        "ip_addresses",
        sa.Column(
            "nat_inside_id",
            sa.Integer(),
            sa.ForeignKey("ip_addresses.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_ip_addresses_nat_inside_id", "ip_addresses", ["nat_inside_id"]
    )


def downgrade() -> None:
    op.drop_column("ip_addresses", "nat_inside_id")
    op.drop_column("ip_addresses", "role")
    op.drop_table("ip_ranges")
    op.execute("DROP TYPE IF EXISTS ip_role")
    op.execute("DROP TYPE IF EXISTS range_role")
