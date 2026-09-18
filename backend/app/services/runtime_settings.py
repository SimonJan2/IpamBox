"""Runtime-editable settings: app_settings rows override env defaults.

Each public key resolves as: DB row -> env var -> code default. Validators
run on PATCH and on read (a bad stored value falls back to env/default).
Keys starting with "_" are internal (scheduler stamps) — never exposed or
settable through the API.
"""
import ipaddress
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.models.app_setting import AppSetting


class SettingsValidationError(Exception):
    """Carries {key: message} so the API can return per-field 422s."""

    def __init__(self, errors: dict[str, str]):
        super().__init__(str(errors))
        self.errors = errors


def _v_cidr_list(v: Any) -> list[str]:
    if not isinstance(v, list):
        raise ValueError("expected a list of CIDRs")
    out: list[str] = []
    for item in v:
        try:
            out.append(str(ipaddress.ip_network(str(item).strip(), strict=False)))
        except ValueError:
            raise ValueError(f"invalid CIDR: {item!r}") from None
    return sorted(set(out))


def _v_port_list(v: Any) -> list[int]:
    if not isinstance(v, list):
        raise ValueError("expected a list of ports")
    out: list[int] = []
    for item in v:
        try:
            port = int(item)
        except (TypeError, ValueError):
            raise ValueError(f"invalid port: {item!r}") from None
        if not 1 <= port <= 65535:
            raise ValueError(f"port out of range 1-65535: {port}")
        out.append(port)
    return sorted(set(out))


def _v_bool(v: Any) -> bool:
    if not isinstance(v, bool):
        raise ValueError("expected true/false")
    return v


def _v_int(lo: int, hi: int) -> Callable[[Any], int]:
    def check(v: Any) -> int:
        if isinstance(v, bool) or not isinstance(v, int):
            raise ValueError("expected an integer")
        if not lo <= v <= hi:
            raise ValueError(f"must be between {lo} and {hi}")
        return v

    return check


def _v_float(lo: float, hi: float) -> Callable[[Any], float]:
    def check(v: Any) -> float:
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise ValueError("expected a number")
        if not lo <= float(v) <= hi:
            raise ValueError(f"must be between {lo} and {hi}")
        return float(v)

    return check


def _v_str(maxlen: int) -> Callable[[Any], str]:
    def check(v: Any) -> str:
        if not isinstance(v, str):
            raise ValueError("expected a string")
        if len(v) > maxlen:
            raise ValueError(f"must be at most {maxlen} characters")
        return v.strip()

    return check


@dataclass(frozen=True)
class SettingSpec:
    """One runtime-editable setting.

    field:    the env-backed attribute on config.Settings (env var = FIELD.upper()).
    validate: normalize/reject a PATCH value; raises ValueError -> 422.
    get:      normalized read from env Settings when it differs from the raw
              field (e.g. comma-string -> list properties).
    """

    field: str
    validate: Callable[[Any], Any]
    get: Callable[[Settings], Any] | None = None


EDITABLE: dict[str, SettingSpec] = {
    "scan_networks": SettingSpec(
        "scan_networks", _v_cidr_list, lambda s: s.scan_network_list
    ),
    "scan_exclude_networks": SettingSpec(
        "scan_exclude_networks", _v_cidr_list, lambda s: s.scan_exclude_network_list
    ),
    "scan_only_configured": SettingSpec("scan_only_configured", _v_bool),
    "scan_interval_minutes": SettingSpec("scan_interval_minutes", _v_int(0, 10080)),
    "scan_min_interval_seconds": SettingSpec(
        "scan_min_interval_seconds", _v_int(0, 3600)
    ),
    "scan_tcp_ports": SettingSpec(
        "scan_tcp_ports", _v_port_list, lambda s: s.tcp_ping_ports
    ),
    "scan_interface": SettingSpec("scan_interface", _v_str(64)),
    "scan_icmp_timeout": SettingSpec("scan_icmp_timeout", _v_float(0.1, 10.0)),
    "scan_tcp_timeout": SettingSpec("scan_tcp_timeout", _v_float(0.1, 10.0)),
    "scan_concurrency": SettingSpec("scan_concurrency", _v_int(1, 1024)),
    "site_code_follow_site": SettingSpec("site_code_follow_site", _v_bool),
    "backup_interval_minutes": SettingSpec(
        "backup_interval_minutes", _v_int(0, 10080)
    ),
    "backup_keep": SettingSpec("backup_keep", _v_int(1, 100)),
    "ipambox_session_hours": SettingSpec("ipambox_session_hours", _v_int(1, 720)),
}


@dataclass
class Effective:
    values: dict[str, Any]
    sources: dict[str, str]  # "db" | "env" | "default" per editable key


def _env_sourced(spec: SettingSpec) -> bool:
    """True when the field's current value differs from its declared default."""
    default = Settings.model_fields[spec.field].default
    return getattr(get_settings(), spec.field) != default


async def get_effective(session: AsyncSession) -> Effective:
    rows = (await session.execute(select(AppSetting))).scalars().all()
    overrides = {r.key: r.value for r in rows if not r.key.startswith("_")}
    env = get_settings()
    values: dict[str, Any] = {}
    sources: dict[str, str] = {}
    for key, spec in EDITABLE.items():
        if key in overrides:
            try:
                values[key] = spec.validate(overrides[key])
                sources[key] = "db"
                continue
            except ValueError:
                pass  # corrupt stored value -> behave as if unset
        values[key] = spec.get(env) if spec.get else getattr(env, spec.field)
        sources[key] = "env" if _env_sourced(spec) else "default"
    return Effective(values, sources)


async def patch(session: AsyncSession, updates: dict[str, Any]) -> None:
    """Apply partial updates; a value of None resets the key to env/default."""
    unknown = sorted(set(updates) - set(EDITABLE))
    if unknown:
        raise SettingsValidationError({k: "unknown setting" for k in unknown})

    cleaned: dict[str, Any] = {}
    errors: dict[str, str] = {}
    for key, raw in updates.items():
        if raw is None:
            continue
        try:
            cleaned[key] = EDITABLE[key].validate(raw)
        except ValueError as e:
            errors[key] = str(e)
    if errors:
        raise SettingsValidationError(errors)

    now = datetime.utcnow()
    for key, raw in updates.items():
        if raw is None:
            await session.execute(delete(AppSetting).where(AppSetting.key == key))
            continue
        row = await session.get(AppSetting, key)
        if row is None:
            session.add(AppSetting(key=key, value=cleaned[key]))
        else:
            row.value = cleaned[key]
            row.updated_at = now
