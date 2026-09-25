"""V7 — continuous monitoring targets + outbound notification channels."""
import enum
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (Boolean, CheckConstraint, DateTime, Enum,
                        ForeignKey, Integer, String, Text, func, inspect)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class MonitorKind(str, enum.Enum):
    PING = "ping"
    TCP = "tcp"
    HTTP = "http"


class MonitorState(str, enum.Enum):
    UP = "up"
    DOWN = "down"
    UNKNOWN = "unknown"


class ChannelKind(str, enum.Enum):
    WEBHOOK = "webhook"
    SMTP = "smtp"
    DISCORD = "discord"
    TELEGRAM = "telegram"


class MonitorTarget(Base):
    """One monitored endpoint — resolves to a concrete IP at check time.

    ``state``/``consecutive_failures``/``last_*`` are observed values written
    by the sweep via bulk ``update()``; they are also in the changelog
    SKIP_FIELDS so steady-state churn never hits the audit trail.
    """

    __tablename__ = "monitor_targets"
    __table_args__ = (
        CheckConstraint(
            "(device_id IS NULL) <> (address_id IS NULL)",
            name="ck_monitor_targets_one_ref",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # CASCADE, not SET NULL: a SET-NULL'd row would violate the exactly-one
    # CHECK (both refs NULL) and block the parent delete — a monitor whose
    # target is gone is dead weight anyway.
    device_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("devices.id", ondelete="CASCADE"), index=True
    )
    address_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("ip_addresses.id", ondelete="CASCADE"), index=True
    )
    kind: Mapped[MonitorKind] = mapped_column(
        Enum(
            MonitorKind,
            name="monitor_kind",
            native_enum=True,
            values_callable=lambda e: [m.value for m in e],
        )
    )
    port: Mapped[Optional[int]] = mapped_column(Integer)
    http_path: Mapped[str] = mapped_column(String(255), default="/", server_default="/")
    http_expect: Mapped[Optional[str]] = mapped_column(String(255))
    interval_seconds: Mapped[int] = mapped_column(Integer, default=60, server_default="60")
    down_after: Mapped[int] = mapped_column(Integer, default=2, server_default="2")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    state: Mapped[MonitorState] = mapped_column(
        Enum(
            MonitorState,
            name="monitor_state",
            native_enum=True,
            values_callable=lambda e: [m.value for m in e],
        ),
        default=MonitorState.UNKNOWN,
        server_default="unknown",
    )
    consecutive_failures: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    last_checked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_change_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # passive_deletes lets the DB's ON DELETE CASCADE fire on ORM deletes —
    # otherwise the uow would SET NULL the child rows and hit the
    # exactly-one CHECK constraint, breaking device/address deletion.
    device = relationship(
        "Device", foreign_keys=[device_id], passive_deletes=True
    )
    address = relationship(
        "IPAddress", foreign_keys=[address_id], passive_deletes=True
    )

    def __changelog_repr__(self) -> str:
        insp = inspect(self)
        label = None
        if "address" not in insp.unloaded and self.address:
            label = str(self.address.address)
        elif "device" not in insp.unloaded and self.device:
            label = self.device.name
        if not label:
            label = (
                f"address#{self.address_id}"
                if self.address_id
                else f"device#{self.device_id}"
            )
        return f"{self.kind.value} {label}"


class NotificationChannel(Base):
    """Outbound sink. ``config`` holds non-secret fields per kind;
    ``secret_enc`` is the v6 AES-GCM blob for the webhook URL / SMTP
    password / Telegram bot token. Never serialized raw over the API."""

    __tablename__ = "notification_channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    kind: Mapped[ChannelKind] = mapped_column(
        Enum(
            ChannelKind,
            name="channel_kind",
            native_enum=True,
            values_callable=lambda e: [m.value for m in e],
        )
    )
    config: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, server_default="{}"
    )
    secret_enc: Mapped[Optional[str]] = mapped_column(Text)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __changelog_repr__(self) -> str:
        return f"{self.kind.value}:{self.name}"


class NotificationLog(Base):
    """Append-only delivery attempt log — swept by ``notify_retention_days``."""

    __tablename__ = "notification_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    channel_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("notification_channels.id", ondelete="SET NULL"),
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(64))
    summary: Mapped[str] = mapped_column(Text)
    ok: Mapped[bool] = mapped_column(Boolean)
    error: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
