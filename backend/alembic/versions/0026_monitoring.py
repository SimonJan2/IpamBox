"""monitoring — per-target health checks + notification channels (V7)

Three tables on top of the scanner's world:

- ``monitor_targets`` — one row per thing we ping/probe/fetch on an
  interval. Exactly one of ``device_id`` / ``address_id`` is set (CHECK):
  the row's concrete IP is resolved at check time from the linked
  address, or the device's first active address for device targets.
  The FKs CASCADE rather than SET NULL — SET NULL would null out the
  last remaining ref and violate the exactly-one CHECK, breaking the
  parent delete outright; a monitor without its target is dead weight.
  ``state``/``consecutive_failures``/``last_*`` are observed columns —
  written by the monitor sweep via bulk UPDATE so they don't spam the
  changelog.
- ``notification_channels`` — outbound webhook/SMTP/Discord/Telegram
  sinks. Non-secret settings live in ``config`` JSONB; secret material
  (webhook URL, SMTP password, Telegram bot token) goes in ``secret_enc``
  under the v6 ``v1:`` AES-GCM blob contract.
- ``notification_log`` — append-only delivery attempts, swept by
  ``notify_retention_days``.

Revision ID: 0026_monitoring
Revises: 0025_subnet_semantics
Create Date: 2026-09-28
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0026_monitoring"
down_revision = "0025_subnet_semantics"
branch_labels = None
depends_on = None

monitor_kind = postgresql.ENUM(
    "ping", "tcp", "http", name="monitor_kind", create_type=False
)
monitor_state = postgresql.ENUM(
    "up", "down", "unknown", name="monitor_state", create_type=False
)
channel_kind = postgresql.ENUM(
    "webhook", "smtp", "discord", "telegram", name="channel_kind", create_type=False
)


def upgrade() -> None:
    op.execute("CREATE TYPE monitor_kind AS ENUM ('ping','tcp','http')")
    op.execute("CREATE TYPE monitor_state AS ENUM ('up','down','unknown')")
    op.execute(
        "CREATE TYPE channel_kind AS ENUM ('webhook','smtp','discord','telegram')"
    )

    op.create_table(
        "monitor_targets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "device_id",
            sa.Integer(),
            sa.ForeignKey("devices.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "address_id",
            sa.Integer(),
            sa.ForeignKey("ip_addresses.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("kind", monitor_kind, nullable=False),
        sa.Column("port", sa.Integer(), nullable=True),
        sa.Column("http_path", sa.String(255), server_default="/", nullable=False),
        sa.Column("http_expect", sa.String(255), nullable=True),
        sa.Column("interval_seconds", sa.Integer(), server_default="60", nullable=False),
        sa.Column("down_after", sa.Integer(), server_default="2", nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "state", monitor_state, server_default="unknown", nullable=False
        ),
        sa.Column("consecutive_failures", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_checked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_change_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
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
            "(device_id IS NULL) <> (address_id IS NULL)",
            name="ck_monitor_targets_one_ref",
        ),
    )
    op.create_index(
        "ix_monitor_targets_device_id", "monitor_targets", ["device_id"]
    )
    op.create_index(
        "ix_monitor_targets_address_id", "monitor_targets", ["address_id"]
    )
    op.create_index(
        "ix_monitor_targets_due",
        "monitor_targets",
        ["enabled", "last_checked_at"],
    )

    op.create_table(
        "notification_channels",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("kind", channel_kind, nullable=False),
        sa.Column(
            "config",
            postgresql.JSONB(),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("secret_enc", sa.Text(), nullable=True),
        sa.Column("enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "notification_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "channel_id",
            sa.Integer(),
            sa.ForeignKey("notification_channels.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("ok", sa.Boolean(), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_notification_log_channel", "notification_log", ["channel_id"]
    )
    op.create_index(
        "ix_notification_log_created", "notification_log", ["created_at"]
    )


def downgrade() -> None:
    op.drop_table("notification_log")
    op.drop_table("notification_channels")
    op.drop_table("monitor_targets")
    op.execute("DROP TYPE channel_kind")
    op.execute("DROP TYPE monitor_state")
    op.execute("DROP TYPE monitor_kind")
