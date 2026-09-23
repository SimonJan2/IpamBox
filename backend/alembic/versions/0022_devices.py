"""devices: rack_devices grows up into a first-class entity

A device is a host that exists independently of any rack: it *has* a rack
placement (all placement columns nullable — NULL rack_id = unracked
inventory), *has* IPs (ip_addresses.device_id — one device, many IPs), and
keeps its asset link. The migration is a straight data move:

1. CREATE TABLE devices (placement + entity kit: serial/site/mac/custom
   fields/row_color/sort_order/pinned/import_batch_id).
2. INSERT INTO devices SELECT FROM rack_devices — column names already
   align; ids preserved so change_log.object_id stays meaningful.
3. ip_addresses.device_id added and backfilled from the old
   rack_devices.ip_address_id single link.
4. DROP TABLE rack_devices — after the data is safely moved.

History is not rewritten: change_log rows keep object_type='rack_device'.

Revision ID: 0022_devices
Revises: 0021_rack_groups
Create Date: 2026-09-26
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0022_devices"
down_revision = "0021_rack_groups"
branch_labels = None
depends_on = None

rack_face = postgresql.ENUM(
    "front", "rear", "both", name="rack_face", create_type=False
)

# rack_devices columns that map 1:1 onto devices (order matches the INSERTs).
_COPY_COLS = (
    "id, rack_id, name, device_type, u_position, u_height, face, colour, "
    "category, manufacturer, model, asset_id, source, carrier_id, slot, "
    "slot_layout, watts, weight_kg, notes, created_at, updated_at"
)


def upgrade() -> None:
    op.create_table(
        "devices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("device_type", sa.String(255), nullable=True),
        sa.Column("serial_number", sa.String(128), nullable=True),
        sa.Column(
            "site_id",
            sa.Integer(),
            sa.ForeignKey("sites.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "asset_id",
            sa.Integer(),
            sa.ForeignKey("assets.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("mac_address", sa.String(17), nullable=True),
        # Placement — all nullable; NULL rack_id = unracked inventory.
        sa.Column(
            "rack_id",
            sa.Integer(),
            sa.ForeignKey("racks.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("u_position", sa.Integer(), nullable=True),
        sa.Column("u_height", sa.Integer(), server_default="1", nullable=True),
        sa.Column("face", rack_face, server_default="front", nullable=True),
        # Self-FK: children ride in a carrier's slots; deleting the carrier
        # unmounts children (SET NULL) rather than deleting real devices.
        sa.Column(
            "carrier_id",
            sa.Integer(),
            sa.ForeignKey("devices.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("slot", sa.Integer(), nullable=True),
        sa.Column("slot_layout", sa.String(16), nullable=True),
        sa.Column("colour", sa.String(7), nullable=True),
        sa.Column("category", sa.String(64), nullable=True),
        sa.Column("manufacturer", sa.String(255), nullable=True),
        sa.Column("model", sa.String(255), nullable=True),
        sa.Column("watts", sa.Integer(), nullable=True),
        sa.Column("weight_kg", sa.Numeric(7, 2), nullable=True),
        sa.Column(
            "custom_fields",
            postgresql.JSONB(),
            server_default=sa.text("'{}'::jsonb"),
            nullable=True,
        ),
        sa.Column(
            "source", sa.String(16), server_default="manual", nullable=False
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("row_color", sa.String(7), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=True),
        sa.Column(
            "pinned", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column(
            "import_batch_id",
            sa.Integer(),
            sa.ForeignKey("import_batches.id", ondelete="SET NULL"),
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
    )
    op.create_index("ix_devices_serial_number", "devices", ["serial_number"])
    op.create_index("ix_devices_site_id", "devices", ["site_id"])
    op.create_index("ix_devices_asset_id", "devices", ["asset_id"])
    op.create_index("ix_devices_mac_address", "devices", ["mac_address"])
    op.create_index("ix_devices_rack_id", "devices", ["rack_id"])
    op.create_index("ix_devices_rack_u", "devices", ["rack_id", "u_position"])
    op.create_index("ix_devices_carrier_id", "devices", ["carrier_id"])
    op.create_index(
        "ix_devices_carrier_slot",
        "devices",
        ["carrier_id", "slot"],
        unique=True,
        postgresql_where=sa.text("carrier_id IS NOT NULL AND slot IS NOT NULL"),
    )
    op.create_index("ix_devices_sort_order", "devices", ["sort_order"])
    op.create_index("ix_devices_import_batch_id", "devices", ["import_batch_id"])

    # Data move — ids preserved so change_log.object_id keeps pointing at the
    # same physical host.
    op.execute(f"INSERT INTO devices ({_COPY_COLS}) SELECT {_COPY_COLS} FROM rack_devices")
    op.execute(
        "SELECT setval(pg_get_serial_sequence('devices','id'), "
        "COALESCE((SELECT max(id) FROM devices), 1), "
        "(SELECT max(id) FROM devices) IS NOT NULL)"
    )

    # One device, many IPs: backfill the old single link.
    op.add_column(
        "ip_addresses",
        sa.Column(
            "device_id",
            sa.Integer(),
            sa.ForeignKey("devices.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_ip_addresses_device_id", "ip_addresses", ["device_id"]
    )
    op.execute(
        "UPDATE ip_addresses ip SET device_id = rd.id "
        "FROM rack_devices rd WHERE rd.ip_address_id = ip.id"
    )

    op.drop_table("rack_devices")


def downgrade() -> None:
    # Recreate rack_devices. Placement columns are recreated NULLABLE so
    # unracked devices (a concept that didn't exist pre-0022) survive the
    # round trip instead of being dropped.
    op.create_table(
        "rack_devices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "rack_id",
            sa.Integer(),
            sa.ForeignKey("racks.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("device_type", sa.String(255), nullable=True),
        sa.Column("u_position", sa.Integer(), nullable=True),
        sa.Column("u_height", sa.Integer(), server_default="1", nullable=True),
        sa.Column("face", rack_face, server_default="front", nullable=True),
        sa.Column("colour", sa.String(7), nullable=True),
        sa.Column("category", sa.String(64), nullable=True),
        sa.Column("manufacturer", sa.String(255), nullable=True),
        sa.Column("model", sa.String(255), nullable=True),
        sa.Column(
            "asset_id",
            sa.Integer(),
            sa.ForeignKey("assets.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "ip_address_id",
            sa.Integer(),
            sa.ForeignKey("ip_addresses.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "source", sa.String(16), server_default="manual", nullable=False
        ),
        sa.Column(
            "carrier_id",
            sa.Integer(),
            sa.ForeignKey("rack_devices.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("slot", sa.Integer(), nullable=True),
        sa.Column("slot_layout", sa.String(16), nullable=True),
        sa.Column("watts", sa.Integer(), nullable=True),
        sa.Column("weight_kg", sa.Numeric(7, 2), nullable=True),
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
    )
    op.create_index("ix_rack_devices_rack_id", "rack_devices", ["rack_id"])
    op.create_index(
        "ix_rack_devices_rack_u", "rack_devices", ["rack_id", "u_position"]
    )
    op.create_index("ix_rack_devices_asset_id", "rack_devices", ["asset_id"])
    op.create_index(
        "ix_rack_devices_ip_address_id", "rack_devices", ["ip_address_id"]
    )
    op.create_index("ix_rack_devices_carrier_id", "rack_devices", ["carrier_id"])
    op.create_index(
        "ix_rack_devices_carrier_slot",
        "rack_devices",
        ["carrier_id", "slot"],
        unique=True,
        postgresql_where=sa.text("carrier_id IS NOT NULL"),
    )

    # Move device rows back; the single-link column gets the lowest-id IP.
    op.execute(f"INSERT INTO rack_devices ({_COPY_COLS}) SELECT {_COPY_COLS} FROM devices")
    op.execute(
        "UPDATE rack_devices rd SET ip_address_id = s.ip_id FROM "
        "(SELECT device_id, MIN(id) AS ip_id FROM ip_addresses "
        " WHERE device_id IS NOT NULL GROUP BY device_id) s "
        "WHERE s.device_id = rd.id"
    )
    op.execute(
        "SELECT setval(pg_get_serial_sequence('rack_devices','id'), "
        "COALESCE((SELECT max(id) FROM rack_devices), 1), "
        "(SELECT max(id) FROM rack_devices) IS NOT NULL)"
    )

    op.drop_index("ix_ip_addresses_device_id", table_name="ip_addresses")
    op.drop_column("ip_addresses", "device_id")
    op.drop_table("devices")
