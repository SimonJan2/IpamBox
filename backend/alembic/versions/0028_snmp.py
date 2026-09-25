"""snmp — per-device credentials + IF-MIB observed state (V8)

Column-only migration — no new tables, so backup/restore needs nothing
extra (the *_enc blob rides along as opaque text and stays decryptable
under the same IPAMBOX_SECRET_KEY).

``devices`` gains the SNMP config (version/port/enabled), the encrypted
credential blob ``snmp_cred_enc`` (v6 ``v1:`` AES-GCM contract — never
serialized), and the observed columns the poll lane stamps
(sysName/sysDescr, last_ok_at, last_error — changelog-skipped churn).

``device_interfaces`` gains the poller's view of a port: ``if_index``
(the (device_id, if_index) upsert key, indexed), live oper/admin status,
``snmp_seen_at`` staleness, and ``source`` (manual|snmp — snmp-created
ports are owned by the poller; manual rows are never rewritten).

Revision ID: 0028_snmp
Revises: 0027_review
"""
import sqlalchemy as sa
from alembic import op

revision = "0028_snmp"
down_revision = "0027_review"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "devices",
        sa.Column(
            "snmp_enabled",
            sa.Boolean(),
            server_default="false",
            nullable=False,
        ),
    )
    op.add_column(
        "devices", sa.Column("snmp_version", sa.String(4), nullable=True)
    )
    op.add_column(
        "devices",
        sa.Column(
            "snmp_port", sa.Integer(), server_default="161", nullable=False
        ),
    )
    op.add_column(
        "devices", sa.Column("snmp_cred_enc", sa.Text(), nullable=True)
    )
    op.add_column(
        "devices", sa.Column("snmp_sys_name", sa.Text(), nullable=True)
    )
    op.add_column(
        "devices", sa.Column("snmp_sys_descr", sa.Text(), nullable=True)
    )
    op.add_column(
        "devices",
        sa.Column(
            "snmp_last_ok_at", sa.DateTime(timezone=True), nullable=True
        ),
    )
    op.add_column(
        "devices", sa.Column("snmp_last_error", sa.Text(), nullable=True)
    )

    op.add_column(
        "device_interfaces",
        sa.Column("if_index", sa.Integer(), nullable=True),
    )
    op.add_column(
        "device_interfaces",
        sa.Column("oper_status", sa.String(16), nullable=True),
    )
    op.add_column(
        "device_interfaces",
        sa.Column("admin_status", sa.String(16), nullable=True),
    )
    op.add_column(
        "device_interfaces",
        sa.Column(
            "snmp_seen_at", sa.DateTime(timezone=True), nullable=True
        ),
    )
    op.add_column(
        "device_interfaces",
        sa.Column(
            "source",
            sa.String(16),
            server_default="manual",
            nullable=False,
        ),
    )
    op.create_unique_constraint(
        "uq_device_interfaces_device_ifindex",
        "device_interfaces",
        ["device_id", "if_index"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_device_interfaces_device_ifindex", "device_interfaces"
    )
    op.drop_column("device_interfaces", "source")
    op.drop_column("device_interfaces", "snmp_seen_at")
    op.drop_column("device_interfaces", "admin_status")
    op.drop_column("device_interfaces", "oper_status")
    op.drop_column("device_interfaces", "if_index")
    op.drop_column("devices", "snmp_last_error")
    op.drop_column("devices", "snmp_last_ok_at")
    op.drop_column("devices", "snmp_sys_descr")
    op.drop_column("devices", "snmp_sys_name")
    op.drop_column("devices", "snmp_cred_enc")
    op.drop_column("devices", "snmp_port")
    op.drop_column("devices", "snmp_version")
    op.drop_column("devices", "snmp_enabled")
