from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator
import ipaddress

from app.models.scan_job import ScanStatus


class ScanCreate(BaseModel):
    # All fields optional: empty body -> auto-detect LAN subnet, Global VRF.
    cidr: str | None = None
    vrf_id: int | None = None
    prefix_id: int | None = None

    @field_validator("cidr")
    @classmethod
    def _cidr(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            return str(ipaddress.ip_network(v.strip(), strict=False))
        except ValueError as exc:
            raise ValueError(f"invalid CIDR: {v}") from exc


class ScanJobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cidr: str
    vrf_id: int | None
    prefix_id: int | None
    status: ScanStatus
    progress: float
    total_hosts: int
    hosts_discovered: int
    hosts_new: int
    error: str | None
    started_at: datetime | None
    finished_at: datetime | None
    duration_seconds: float | None
    created_at: datetime


class ScanConfigOut(BaseModel):
    networks: list[str]
    exclude_networks: list[str]
    only_configured: bool
    interval_minutes: int
    detected_cidr: str | None
    tcp_ports: list[int]
