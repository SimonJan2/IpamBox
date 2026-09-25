"""V7 monitoring + notification channel schemas.

http_expect grammar (documented in docs/monitoring.md):
    ``status:NNN``  — match the HTTP status code exactly
    anything else   — case-sensitive substring matched against the body
    empty / None    — any 2xx or 3xx response counts as up
"""
import re
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.monitoring import ChannelKind, MonitorKind, MonitorState

_STATUS_RE = re.compile(r"^status:([1-5]\d{2})$")


def validate_http_expect(v: str | None) -> str | None:
    """http_expect: 'status:<100-599>' or a body substring."""
    if v is None or v == "":
        return None
    v = v.strip()
    if v.startswith("status:") and not _STATUS_RE.match(v):
        raise ValueError(
            "http_expect 'status:' form needs a 3-digit code, e.g. status:200"
        )
    return v


class MonitorTargetCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    device_id: int | None = None
    address_id: int | None = None
    kind: MonitorKind
    port: int | None = Field(default=None, ge=1, le=65535)
    http_path: str = Field(default="/", max_length=255)
    http_expect: str | None = Field(default=None, max_length=255)
    interval_seconds: int = Field(default=60, ge=5, le=86400)
    down_after: int = Field(default=2, ge=1, le=100)
    enabled: bool = True
    notes: str | None = None

    _check_expect = field_validator("http_expect")(validate_http_expect)

    @model_validator(mode="after")
    def _coherent(self):
        if (self.device_id is None) == (self.address_id is None):
            raise ValueError("exactly one of device_id / address_id is required")
        validate_kind_fields(
            self.kind, self.port, self.http_path, self.http_expect
        )
        return self


class MonitorTargetUpdate(BaseModel):
    """PATCH — all fields optional; the route re-validates merged fields."""

    model_config = ConfigDict(extra="forbid")

    device_id: int | None = None
    address_id: int | None = None
    kind: MonitorKind | None = None
    port: int | None = Field(default=None, ge=1, le=65535)
    http_path: str | None = Field(default=None, max_length=255)
    http_expect: str | None = Field(default=None, max_length=255)
    interval_seconds: int | None = Field(default=None, ge=5, le=86400)
    down_after: int | None = Field(default=None, ge=1, le=100)
    enabled: bool | None = None
    notes: str | None = None

    _check_expect = field_validator("http_expect")(validate_http_expect)


def validate_kind_fields(
    kind: MonitorKind,
    port: int | None,
    http_path: str | None,
    http_expect: str | None,
) -> None:
    """Per-kind field rules shared by create (schema) and patch (route)."""
    if kind in (MonitorKind.TCP, MonitorKind.HTTP) and port is None:
        raise ValueError(f"port is required for {kind.value} checks")
    if kind == MonitorKind.PING:
        if port is not None:
            raise ValueError("port does not apply to ping checks")
        if http_expect is not None or (http_path or "/") != "/":
            raise ValueError("http_* fields only apply to http checks")
    if kind == MonitorKind.TCP and (
        http_expect is not None or (http_path or "/") != "/"
    ):
        raise ValueError("http_* fields only apply to http checks")
    if kind == MonitorKind.HTTP and http_path and not http_path.startswith("/"):
        raise ValueError("http_path must start with /")


class MonitorTargetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int | None
    address_id: int | None
    kind: MonitorKind
    port: int | None
    http_path: str
    http_expect: str | None
    interval_seconds: int
    down_after: int
    enabled: bool
    state: MonitorState
    consecutive_failures: int
    last_checked_at: datetime | None
    last_change_at: datetime | None
    last_error: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    # resolved display fields — stamped by the router, not columns
    target_label: str | None = None
    resolved_ip: str | None = None
    device_name: str | None = None


class MonitorSummary(BaseModel):
    up: int = 0
    down: int = 0
    unknown: int = 0
    due: int = 0


# ------------------------------------------------------- notification channels


class ChannelCreate(BaseModel):
    """Create a channel. `secret` is write-only (v6 secrets contract):
    webhook/discord URL, SMTP password or Telegram bot token."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=255)
    kind: ChannelKind
    enabled: bool = True
    secret: str | None = Field(default=None, max_length=2048)
    # non-secret per-kind config
    webhook_method: str = Field(default="POST", max_length=16)
    smtp_host: str | None = Field(default=None, max_length=255)
    smtp_port: int | None = Field(default=None, ge=1, le=65535)
    smtp_from: str | None = Field(default=None, max_length=255)
    smtp_to: list[str] = Field(default_factory=list)
    smtp_starttls: bool = True
    smtp_username: str | None = Field(default=None, max_length=255)
    telegram_chat_id: str | None = Field(default=None, max_length=64)

    @model_validator(mode="after")
    def _coherent(self):
        validate_channel_fields(
            self.kind,
            secret=self.secret,
            has_stored_secret=False,
            smtp_host=self.smtp_host,
            smtp_from=self.smtp_from,
            smtp_to=self.smtp_to,
            telegram_chat_id=self.telegram_chat_id,
        )
        if self.webhook_method.upper() not in ("POST", "PUT"):
            raise ValueError("webhook_method must be POST or PUT")
        return self


class ChannelUpdate(BaseModel):
    """PATCH — omitted fields keep their stored values. `secret` omitted =
    keep, empty string = clear, otherwise re-encrypt the new value."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=255)
    kind: ChannelKind | None = None
    enabled: bool | None = None
    secret: str | None = Field(default=None, max_length=2048)
    webhook_method: str | None = Field(default=None, max_length=16)
    smtp_host: str | None = Field(default=None, max_length=255)
    smtp_port: int | None = Field(default=None, ge=1, le=65535)
    smtp_from: str | None = Field(default=None, max_length=255)
    smtp_to: list[str] | None = None
    smtp_starttls: bool | None = None
    smtp_username: str | None = Field(default=None, max_length=255)
    telegram_chat_id: str | None = Field(default=None, max_length=64)


def validate_channel_fields(
    kind: ChannelKind,
    *,
    secret: str | None,
    has_stored_secret: bool,
    smtp_host: str | None,
    smtp_from: str | None,
    smtp_to: list[str] | None,
    telegram_chat_id: str | None,
) -> None:
    """Per-kind required fields — shared by create (schema) and patch
    (route, against the merged config)."""
    has_secret = bool(secret) or has_stored_secret
    if kind in (ChannelKind.WEBHOOK, ChannelKind.DISCORD):
        if not has_secret:
            raise ValueError(
                f"{kind.value} channels need the webhook URL (secret field)"
            )
    elif kind == ChannelKind.TELEGRAM:
        if not telegram_chat_id:
            raise ValueError("telegram channels need telegram_chat_id")
        if not has_secret:
            raise ValueError("telegram channels need the bot token (secret)")
    elif kind == ChannelKind.SMTP:
        if not smtp_host:
            raise ValueError("smtp channels need smtp_host")
        if not smtp_from:
            raise ValueError("smtp channels need smtp_from")
        if not smtp_to:
            raise ValueError("smtp channels need at least one smtp_to address")


class ChannelOut(BaseModel):
    """Secret material never leaves this shape: `secret_set` is a bool,
    `config` holds only non-secret fields (webhook URL lives in
    `secret_enc`)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    kind: ChannelKind
    enabled: bool
    created_at: datetime
    config: dict[str, Any] = {}
    secret_set: bool = False


class ChannelTestOut(BaseModel):
    ok: bool
    error: str | None = None


class NotificationLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    channel_id: int | None
    event_type: str
    summary: str
    ok: bool
    error: str | None
    created_at: datetime
    channel_name: str | None = None  # stamped, survives channel deletion
