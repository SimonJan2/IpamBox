from typing import Any

from pydantic import BaseModel, ConfigDict


class SettingsPatch(BaseModel):
    """Partial settings update. Explicit null resets the key to env/default."""

    model_config = ConfigDict(extra="forbid")

    scan_networks: list[str] | None = None
    scan_exclude_networks: list[str] | None = None
    scan_only_configured: bool | None = None
    scan_interval_minutes: int | None = None
    scan_min_interval_seconds: int | None = None
    scan_max_hosts: int | None = None
    scan_tcp_ports: list[int] | None = None
    scan_interface: str | None = None
    scan_icmp_timeout: float | None = None
    scan_tcp_timeout: float | None = None
    scan_concurrency: int | None = None
    backup_interval_minutes: int | None = None
    backup_keep: int | None = None
    ipambox_session_hours: int | None = None
    site_code_follow_site: bool | None = None
    scan_marks_offline: bool | None = None
    scan_reactivates_offline: bool | None = None
    scan_new_hosts_discovered: bool | None = None
    scan_stored_mac_wins: bool | None = None
    scan_overwrites_hostname: bool | None = None
    scan_infers_device_type: bool | None = None
    scan_auto_create_prefix: bool | None = None
    scan_infers_vrf: bool | None = None
    scan_offline_grace_scans: int | None = None
    discovery_expire_days: int | None = None
    changelog_retention_days: int | None = None
    scan_job_retention_days: int | None = None
    cert_warn_days: int | None = None


class LanInfo(BaseModel):
    iface: str | None = None
    cidr: str | None = None
    source: str | None = None  # "worker" | "local"


class SystemInfo(BaseModel):
    app_version: str
    alembic_head: str | None = None
    lan: LanInfo


class SettingsOut(BaseModel):
    values: dict[str, Any]
    sources: dict[str, str]
    env: dict[str, Any]
    system: SystemInfo


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    created_at: str


class SessionOut(BaseModel):
    id: str
    created_at: str | None
    ip: str | None
    ua: str | None
    expires_in: int | None
    current: bool


class ChangePasswordBody(BaseModel):
    current_password: str
    new_password: str
    logout_others: bool = True
