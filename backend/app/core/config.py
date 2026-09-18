from functools import lru_cache

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

    # Backup settings — scheduled snapshots are written by the worker into
    # backup_dir (a mounted volume); keep bounds how many files are retained.
    backup_dir: str = "/backups"
    backup_interval_minutes: int = 0   # >0 -> recurring backups on the worker
    backup_keep: int = 14              # scheduled files retained on disk

    # Import settings — uploaded workbooks persist under import_dir so a
    # wizard can preview/commit without re-uploading.
    import_dir: str = ""             # empty -> <backup_dir>/imports
    import_keep: int = 20            # stored workbooks retained on disk

    # Feature toggles — runtime-editable behavior switches (Settings > Features)
    site_code_follow_site: bool = False  # treat mismatched stored site codes as stale

    # Auth settings (env vars are IPAMBOX_*)
    ipambox_password: str = ""  # pre-provision the admin password
    ipambox_password_file: str = ""  # path to a file holding the password (wins over above)
    ipambox_session_hours: int = 168  # one week
    ipambox_allow_insecure: bool = False  # disable auth entirely (behind a trusted proxy)
    ipambox_cookie_secure: bool = False  # set True when serving over HTTPS

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
