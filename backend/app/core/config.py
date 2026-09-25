from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://ipam:ipam@localhost:5432/ipam"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: str = "http://localhost:3000"

    # Scanner settings
    scan_interface: str = ""  # empty -> auto-detect default-route interface
    scan_tcp_ports: str = "22,80,443,445,8080"
    scan_icmp_timeout: float = 1.0
    scan_tcp_timeout: float = 0.6
    scan_concurrency: int = 256
    scan_progress_channel_prefix: str = "scan:"
    # Multi-network scanning (comma-separated CIDRs)
    scan_networks: str = ""            # extra/explicit networks to scan
    scan_exclude_networks: str = ""    # never scan these (even if asked)
    scan_only_configured: bool = False # refuse scans outside scan_networks
    scan_interval_minutes: int = 0     # >0 -> scheduled recurring scans
    scan_min_interval_seconds: int = 15  # rate-limit manual scans per CIDR
    scan_max_hosts: int = 4096         # refuse scan targets with more usable hosts (~ /20)

    # Backup settings — scheduled snapshots are written by the worker into
    # backup_dir (a mounted volume); keep bounds how many files are retained.
    backup_dir: str = "/backups"
    backup_interval_minutes: int = 0   # >0 -> recurring backups on the worker
    backup_keep: int = 14              # scheduled files retained on disk

    # Import settings — uploaded workbooks persist under import_dir so a
    # wizard can preview/commit without re-uploading.
    import_dir: str = ""             # empty -> <backup_dir>/imports
    import_keep: int = 20            # stored workbooks retained on disk

    # Read-endpoint safety caps
    ipambox_max_split_children: int = 4096  # /prefixes/{id}/split child limit

    # Feature toggles — runtime-editable behavior switches (Settings > Features).
    # Defaults reproduce the original hard-coded behavior; flipping a toggle is
    # the only way behavior changes.
    site_code_follow_site: bool = True   # cascade site code/number/name to followers
    # Scanner reconcile policy
    scan_marks_offline: bool = True        # missing hosts -> OFFLINE
    scan_reactivates_offline: bool = True  # OFFLINE -> ACTIVE when re-seen
    scan_new_hosts_discovered: bool = True # new scan hosts land in the inbox
    scan_stored_mac_wins: bool = False     # keep stored MAC on mismatch (still flags)
    scan_overwrites_hostname: bool = False # PTR overwrites a set hostname
    scan_infers_device_type: bool = True   # scanner guess fills device_type
    scan_auto_create_prefix: bool = True   # create a prefix when none covers a scan
    scan_infers_vrf: bool = True           # pick VRF by prefix match, else Global
    # Lifecycle & retention — 0 = disabled
    scan_offline_grace_scans: int = 0      # consecutive misses before OFFLINE
    discovery_expire_days: int = 0         # auto-purge stale DISCOVERED rows
    changelog_retention_days: int = 0      # auto-purge old changelog entries
    scan_job_retention_days: int = 0       # auto-purge terminal scan jobs
    cert_warn_days: int = 30               # amber "expiring soon" threshold

    # Auth settings (env vars are IPAMBOX_*)
    ipambox_password: str = ""  # pre-provision the admin password
    ipambox_password_file: str = ""  # path to a file holding the password (wins over above)
    ipambox_session_hours: int = 168  # one week
    ipambox_allow_insecure: bool = False  # disable auth entirely (behind a trusted proxy)
    ipambox_cookie_secure: bool = False  # set True when serving over HTTPS
    # Master key for secrets at rest — encrypts the *_enc credential columns
    # (monitoring channels, SNMP communities, controller tokens, OIDC). The
    # file wins over the env var, same as ipambox_password_file. Rotating it
    # invalidates every stored credential — there is no re-wrap tooling.
    ipambox_secret_key: str = ""
    ipambox_secret_key_file: str = ""
    # X-Forwarded-For is only honored when the socket peer is inside one of
    # these networks (comma-separated IPs/CIDRs). Loopback covers dev mode;
    # compose adds the pinned `ipam` bridge subnet (see docker-compose.yml).
    ipambox_trusted_proxies: str = "127.0.0.1,::1"

    # Rackula round-trip: base URL of a self-hosted instance — enables the
    # "Open in Rackula" button on rack pages. Empty = air-gapped.
    rackula_base_url: str = Field(
        default="", validation_alias="IPAMBOX_RACKULA_BASE_URL"
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def tcp_ping_ports(self) -> list[int]:
        return [int(p) for p in self.scan_tcp_ports.split(",") if p.strip()]

    @property
    def scan_network_list(self) -> list[str]:
        return [n.strip() for n in self.scan_networks.split(",") if n.strip()]

    @property
    def scan_exclude_network_list(self) -> list[str]:
        return [n.strip() for n in self.scan_exclude_networks.split(",") if n.strip()]

    @property
    def import_dir_path(self):
        from pathlib import Path

        return Path(self.import_dir) if self.import_dir else Path(self.backup_dir) / "imports"

    @property
    def sync_database_url(self) -> str:
        """psycopg2-style URL for alembic offline mode / scripts."""
        return self.database_url.replace("+asyncpg", "")


@lru_cache
def get_settings() -> Settings:
    return Settings()
