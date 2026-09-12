from pydantic import BaseModel

from app.schemas.scan import ScanJobOut


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
