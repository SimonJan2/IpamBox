from pydantic import BaseModel

from app.schemas.certificate import CertificateOut
from app.schemas.scan import ScanJobOut


class MacMismatchItem(BaseModel):
    id: int
    address: str
    prefix_id: int
    mac_was: str | None
    mac_seen: str | None
    flagged_at: str | None


class DashboardStats(BaseModel):
    sites_total: int
    vrfs_total: int
    prefixes_total: int
    ips_total: int
    ips_used: int
    ips_free: int
    utilization_pct: float
    devices_active: int
    devices_discovered: int
    devices_offline: int
    devices_reserved: int
    scans_total: int
    last_scan: ScanJobOut | None = None
    circuits_total: int = 0
    certificates_total: int = 0
    certs_expiring_30d: int = 0
    assets_total: int = 0
    services_total: int = 0
    mac_mismatches: int = 0
    # Bounded samples for the dashboard attention zone — full lists live on
    # the entity pages; these ride along so the page needs no extra requests.
    certs_expiring: list[CertificateOut] = []
    mac_mismatch_items: list[MacMismatchItem] = []
