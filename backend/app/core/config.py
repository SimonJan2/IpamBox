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

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def tcp_ping_ports(self) -> list[int]:
        return [int(p) for p in self.scan_tcp_ports.split(",") if p.strip()]

    @property
    def sync_database_url(self) -> str:
        """psycopg2-style URL for alembic offline mode / scripts."""
        return self.database_url.replace("+asyncpg", "")


@lru_cache
def get_settings() -> Settings:
    return Settings()
