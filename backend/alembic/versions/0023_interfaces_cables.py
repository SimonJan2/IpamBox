"""device_interfaces + cables: the L1 layer (V4A)

A device_interface is one named port/NIC on a device; a cable links exactly
two interfaces and each interface terminates at most one cable end (both
end columns are UNIQUE and the API additionally checks across both columns,
so "one cable per interface" holds for every kind).

Patch panels need no dedicated entity: a 24-port panel is a device whose
interfaces have kind='patch'. The front/back pair inside one panel position
is linked by `pair_interface_id` (self-FK — NetBox rear_port-style); the
cable trace hops front→back through it, which is why panel daisy chains
work without giving any interface two cables.

`ip_addresses.connected_interface_id` is the structured sibling of the
legacy `switch_name`/`switch_port` free text — the text columns stay
(they're still useful as a fallback) and get a transition path via the
match-free-text endpoint rather than an in-migration guess.

device_interfaces.connected_ip_id is the host-side NIC→IP binding ("this
port serves this IP") — a different link from ip_addresses.device_id
(device *owns* the address) and from the IP's switch-port link above.
The two interface↔ip FKs form a cycle the backup restore resolves via
deferred_fks.

Revision ID: 0023_interfaces_cables
Revises: 0022_devices
Create Date: 2026-10-05
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0023_interfaces_cables"
down_revision = "0022_devices"
branch_labels = None
depends_on = None

interface_kind = postgresql.ENUM(
    "rj45", "sfp", "sfp28", "qsfp", "console", "patch", "power", "other",
    name="interface_kind", create_type=False,
)
cable_kind = postgresql.ENUM(
    "cat5e", "cat6", "cat6a", "dac", "fiber_sm", "fiber_mm", "power",
    "console", "other",
    name="cable_kind", create_type=False,
)


def upgrade() -> None:
    op.execute(
        "CREATE TYPE interface_kind AS ENUM "
        "('rj45','sfp','sfp28','qsfp','console','patch','power','other')"
    )
    op.execute(
        "CREATE TYPE cable_kind AS ENUM "
        "('cat5e','cat6','cat6a','dac','fiber_sm','fiber_mm','power',"
        "'console','other')"
    )

    op.create_table(
        "device_interfaces",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "device_id",
            sa.Integer(),
            sa.ForeignKey("devices.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column(
            "kind", interface_kind, server_default="other", nullable=False
        ),
        sa.Column("speed_mbps", sa.Integer(), nullable=True),
        sa.Column("mac_address", sa.String(17), nullable=True),
        sa.Column("position", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "connected_ip_id",
            sa.Integer(),
            sa.ForeignKey("ip_addresses.id", ondelete="SET NULL"),
            nullable=True,
        ),
        # Patch-panel front↔back pair link (self-FK; SET NULL so deleting one
        # side leaves the other as an unpaired port).
        sa.Column(
            "pair_interface_id",
            sa.Integer(),
            sa.ForeignKey("device_interfaces.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "device_id", "name", name="uq_device_interfaces_device_name"
        ),
    )
    op.create_index(
        "ix_device_interfaces_device_id", "device_interfaces", ["device_id"]
    )
    op.create_index(
        "ix_device_interfaces_connected_ip_id",
        "device_interfaces",
        ["connected_ip_id"],
    )
    op.create_index(
        "ix_device_interfaces_pair_interface_id",
        "device_interfaces",
        ["pair_interface_id"],
    )

    op.create_table(
        "cables",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "a_interface_id",
            sa.Integer(),
            sa.ForeignKey("device_interfaces.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "b_interface_id",
            sa.Integer(),
            sa.ForeignKey("device_interfaces.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", cable_kind, server_default="other", nullable=False),
        sa.Column("color", sa.String(32), nullable=True),
        sa.Column("label", sa.String(255), nullable=True),
        sa.Column("length_m", sa.Numeric(5, 1), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "a_interface_id <> b_interface_id", name="ck_cables_distinct_ends"
        ),
        sa.UniqueConstraint("a_interface_id", name="uq_cables_a_interface"),
        sa.UniqueConstraint("b_interface_id", name="uq_cables_b_interface"),
    )
    op.create_index(
        "ix_cables_a_interface_id", "cables", ["a_interface_id"]
    )
    op.create_index(
        "ix_cables_b_interface_id", "cables", ["b_interface_id"]
    )

    # Structured sibling of switch_name/switch_port (kept — see docstring).
    op.add_column(
        "ip_addresses",
        sa.Column("connected_interface_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_ip_addresses_connected_interface_id",
        "ip_addresses",
        "device_interfaces",
        ["connected_interface_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_ip_addresses_connected_interface_id",
        "ip_addresses",
        ["connected_interface_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_ip_addresses_connected_interface_id", table_name="ip_addresses"
    )
    op.drop_constraint(
        "fk_ip_addresses_connected_interface_id",
        "ip_addresses",
        type_="foreignkey",
    )
    op.drop_column("ip_addresses", "connected_interface_id")
    op.drop_table("cables")
    op.drop_table("device_interfaces")
    op.execute("DROP TYPE IF EXISTS cable_kind")
    op.execute("DROP TYPE IF EXISTS interface_kind")
