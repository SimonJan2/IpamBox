"""Full-database backup & restore.

Data tables are exported into a single gzipped JSON envelope and restored by
wiping them and re-inserting rows with their original primary keys. Preserved
IDs mean polymorphic references (tag_assignments.object_id,
change_log.object_id) and every foreign key stay valid with no remapping.

The `users` table is excluded by default. On request
(`build_backup(include_users=True)`) non-admin accounts are exported and the
envelope is flagged `includes_users`; restore then replaces the non-admin
set. Admin accounts are never exported and never modified by a restore.

Extensibility contract
----------------------
- New table: add ONE `BackupTable(...)` entry in dependency order. The
  truncate list, serialization and wipe order all derive from this registry.
  `test_registry_covers_all_tables` fails if a table is forgotten.
- New column on an existing model: nothing — serialization is driven by
  column reflection, restore maps values by column type.
- Special restore handling: use `deferred_fks` (self/circular FKs) or
  `sanitize` (row transform, e.g. marking in-flight scans failed).
- Format changes: bump FORMAT_VERSION; loaders reject newer files cleanly.
- `alembic_revision` in the envelope prevents restoring backups produced by
  a newer schema into older code.
"""
import enum
import gzip
import ipaddress
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable

from alembic.script import ScriptDirectory
from sqlalchemy import DateTime, Enum, Numeric, inspect, select, text, update
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.app_setting import AppSetting
from app.models.base import Base
from app.models.change_log import ChangeLog
from app.models.ip_address import IPAddress
from app.models.ip_range import IPRange
from app.models.prefix import Prefix
from app.models.scan_job import ScanJob
from app.models.site import Site
from app.models.tag import Tag, TagAssignment
from app.models.user import User, UserRole
from app.models.vlan import VLAN, VLANGroup
from app.models.vrf import VRF

log = logging.getLogger(__name__)
settings = get_settings()

FORMAT = "ipambox-backup"
FORMAT_VERSION = 1

# Tables outside the BACKUP_TABLES registry (auth state survives on the
# target server). `users` is exported only via build_backup(include_users=
# True) — it must never join the registry, whose TRUNCATE would wipe admins.
EXCLUDED_TABLES = {"users"}


class BackupError(Exception):
    """Raised for any malformed/unsupported backup payload. Maps to HTTP 422."""


@dataclass(frozen=True)
class BackupTable:
    """One restorable table. Registry order = insert order (parents first)."""

    name: str
    model: type[Base]
    # Columns that may reference rows of the same (or later) table. They are
    # inserted as NULL in pass 1 and set via UPDATE after every table is
    # loaded — sidesteps non-deferrable FK ordering problems entirely.
    deferred_fks: tuple[str, ...] = ()
    # Optional transform applied to each raw row dict before insert.
    sanitize: Callable[[dict], dict] | None = None


def _fail_inflight_scans(row: dict) -> dict:
    """A queued/running job in a backup can never resume — mark it failed."""
    if row.get("status") in ("queued", "running"):
        row["status"] = "failed"
        row["error"] = "interrupted by restore"
        row["finished_at"] = row.get("finished_at") or datetime.utcnow().isoformat()
    return row


BACKUP_TABLES: tuple[BackupTable, ...] = (
    BackupTable("sites", Site),
    BackupTable("vrfs", VRF),
    BackupTable("vlan_groups", VLANGroup),
    BackupTable("vlans", VLAN),
    BackupTable("prefixes", Prefix),
    BackupTable("ip_ranges", IPRange),
    BackupTable("ip_addresses", IPAddress, deferred_fks=("nat_inside_id",)),
    BackupTable("tags", Tag),
    BackupTable("tag_assignments", TagAssignment),
    BackupTable("scan_jobs", ScanJob, sanitize=_fail_inflight_scans),
    BackupTable("change_log", ChangeLog),
    BackupTable("app_settings", AppSetting),
)


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------


def _to_json(v: Any) -> Any:
    if v is None or isinstance(v, (str, int, float, bool, list, dict)):
        return v
    if isinstance(v, enum.Enum):
        return v.value
    if isinstance(v, datetime):
        return v.isoformat()
    if isinstance(v, Decimal):
        return int(v)
    return str(v)  # INET/CIDR arrive as ipaddress objects


def _serialize_row(model: type[Base], obj: Any) -> dict:
    return {
        attr.key: _to_json(getattr(obj, attr.key))
        for attr in inspect(model).mapper.column_attrs
    }


def _from_json(col, v: Any) -> Any:
    """Convert a JSON value back to what asyncpg expects for this column."""
    if v is None:
        return None
    t = col.type
    if isinstance(t, postgresql.CIDR):
        return ipaddress.ip_network(str(v), strict=False)
    if isinstance(t, postgresql.INET):
        return ipaddress.ip_interface(str(v))
    try:
        if isinstance(t, DateTime):
            return datetime.fromisoformat(str(v))
        if isinstance(t, Numeric):
            return Decimal(str(v))
        if isinstance(t, Enum) and t.enum_class is not None:
            return t.enum_class(v)
    except (ValueError, KeyError) as e:
        raise BackupError(f"bad value for column {col.key!r}: {e}") from e
    return v  # JSONB, ARRAY, str, int, float, bool — as-is


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------


def backup_filename(now: datetime | None = None) -> str:
    ts = (now or datetime.now()).strftime("%Y%m%d-%H%M%S")
    return f"ipambox-backup-{ts}.json.gz"


def _alembic_revisions() -> list[str]:
    """Known migration revisions, head first (linear chain)."""
    versions = Path(__file__).resolve().parents[2] / "alembic"
    script = ScriptDirectory(str(versions))
    return [rev.revision for rev in script.walk_revisions()]


async def build_backup(session: AsyncSession, include_users: bool = False) -> bytes:
    """Serialize every registered table into the gzipped JSON envelope.

    With include_users=True the envelope also carries every user EXCEPT
    admins (password hashes included — handle the file like a secret) and
    is flagged "includes_users" so restore knows to expect it.
    """
    from app.main import APP_VERSION

    tables: dict[str, list[dict]] = {}
    for spec in BACKUP_TABLES:
        rows = (
            (
                await session.execute(
                    select(spec.model).order_by(
                        *inspect(spec.model).mapper.primary_key
                    )
                )
            )
            .scalars()
            .all()
        )
        tables[spec.name] = [_serialize_row(spec.model, r) for r in rows]

    if include_users:
        users = (
            (
                await session.execute(
                    select(User)
                    .where(User.role != UserRole.ADMIN)
                    .order_by(User.id)
                )
            )
            .scalars()
            .all()
        )
        tables["users"] = [_serialize_row(User, u) for u in users]

    revisions = _alembic_revisions()
    envelope = {
        "format": FORMAT,
        "format_version": FORMAT_VERSION,
        "app_version": APP_VERSION,
        "alembic_revision": revisions[0] if revisions else None,
        "created_at": datetime.utcnow().isoformat(),
        "tables": tables,
    }
    if include_users:
        envelope["includes_users"] = True
    return gzip.compress(json.dumps(envelope).encode("utf-8"))


# ---------------------------------------------------------------------------
# Inspect / validate
# ---------------------------------------------------------------------------


@dataclass
class BackupPreview:
    format: str
    format_version: int
    app_version: str | None
    alembic_revision: str | None
    created_at: str | None
    tables: dict[str, int]
    warnings: list[str] = field(default_factory=list)
    # envelope flag: `users` is a known table only when this is true
    includes_users: bool = False
    # parsed payload, kept for restore so the file isn't decompressed twice
    envelope: dict = field(default_factory=dict)


def _gunzip(payload: bytes) -> bytes:
    if payload[:2] == b"\x1f\x8b":
        try:
            return gzip.decompress(payload)
        except OSError as e:
            raise BackupError(f"corrupt gzip stream: {e}") from e
    return payload


def inspect_backup(payload: bytes) -> BackupPreview:
    """Validate a backup payload without touching the database."""
    try:
        envelope = json.loads(_gunzip(payload))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise BackupError(f"not a valid backup file: {e}") from e
    if not isinstance(envelope, dict) or envelope.get("format") != FORMAT:
        raise BackupError("not an IpamBox backup file")
    version = envelope.get("format_version")
    if not isinstance(version, int) or version > FORMAT_VERSION:
        raise BackupError(
            f"unsupported backup format_version {version!r} "
            f"(this build understands up to {FORMAT_VERSION})"
        )
    revision = envelope.get("alembic_revision")
    known = _alembic_revisions()
    if revision and revision not in known:
        raise BackupError(
            f"backup was made on a newer IpamBox schema ({revision}); "
            "upgrade this installation before restoring"
        )

    warnings: list[str] = []
    tables = envelope.get("tables")
    if not isinstance(tables, dict):
        raise BackupError("backup has no 'tables' object")
    includes_users = bool(envelope.get("includes_users"))
    known_names = {spec.name for spec in BACKUP_TABLES}
    if includes_users:
        known_names |= {"users"}
    counts: dict[str, int] = {}
    for name, rows in tables.items():
        if name not in known_names:
            warnings.append(f"unknown table {name!r} skipped")
            continue
        if not isinstance(rows, list):
            raise BackupError(f"table {name!r} is not a list of rows")
        counts[name] = len(rows)

    return BackupPreview(
        format=envelope["format"],
        format_version=version,
        app_version=envelope.get("app_version"),
        alembic_revision=revision,
        created_at=envelope.get("created_at"),
        tables=counts,
        warnings=warnings,
        includes_users=includes_users,
        envelope=envelope,
    )


# ---------------------------------------------------------------------------
# Restore
# ---------------------------------------------------------------------------


def _truncate_sql() -> str:
    names = ", ".join(spec.name for spec in BACKUP_TABLES)
    return f"TRUNCATE {names} RESTART IDENTITY CASCADE"


def _has_serial_id(spec: BackupTable) -> bool:
    return "id" in spec.model.__table__.columns


def _resync_sequence_sql(table: str) -> str:
    # serial/identity PKs: jump the sequence past the restored max(id) so the
    # next insert can't collide. No-op when the table has no sequence.
    return (
        "SELECT CASE WHEN pg_get_serial_sequence(:t, 'id') IS NOT NULL THEN setval("
        "pg_get_serial_sequence(:t, 'id'), "
        f"COALESCE((SELECT MAX(id) FROM {table}), 1), "
        f"(SELECT MAX(id) FROM {table}) IS NOT NULL) END"
    )


async def _restore_users(
    session: AsyncSession, raw_rows: list[dict], warnings: list[str]
) -> int:
    """Replace the non-admin user set from a users-inclusive envelope.

    Admin rows in the payload are dropped (backups never carry them, but a
    hand-crafted file might) and every admin on the target is preserved —
    rows colliding with an admin id or username are skipped, not failed.
    """
    valid_roles = {r.value for r in UserRole}
    kept: list[dict] = []
    ignored_admins = 0
    for raw in raw_rows:
        if not isinstance(raw, dict):
            warnings.append("users: non-object row skipped")
            continue
        role = raw.get("role")
        if role == UserRole.ADMIN.value:
            ignored_admins += 1
            continue
        if role not in valid_roles:
            warnings.append(
                f"user {raw.get('username')!r} skipped: unknown role {role!r}"
            )
            continue
        kept.append(raw)
    if ignored_admins:
        warnings.append(
            f"{ignored_admins} admin account(s) ignored — admins are never restored"
        )

    # Replace semantics: the non-admin set is fully replaced, admins untouched.
    await session.execute(text("DELETE FROM users WHERE role <> 'admin'"))
    admin_ids = set((await session.execute(select(User.id))).scalars())
    admin_names = set((await session.execute(select(User.username))).scalars())

    columns = {c.key: c for c in User.__table__.columns}
    rows: list[dict] = []
    seen_unknown: set[str] = set()
    for raw in kept:
        if raw.get("id") in admin_ids:
            warnings.append(
                f"user {raw.get('username')!r} skipped: "
                f"id {raw['id']} in use by an admin account"
            )
            continue
        if raw.get("username") in admin_names:
            warnings.append(
                f"user {raw.get('username')!r} skipped: "
                "username in use by an admin account"
            )
            continue
        row: dict = {}
        for key, v in raw.items():
            col = columns.get(key)
            if col is None:
                if key not in seen_unknown:
                    seen_unknown.add(key)
                    warnings.append(f"users: unknown column {key!r} skipped")
                continue
            row[key] = _from_json(col, v)
        rows.append(row)
    if rows:
        await session.execute(User.__table__.insert(), rows)
    return len(rows)


async def restore_backup(
    session: AsyncSession, preview: BackupPreview, actor: str, filename: str
) -> dict:
    """Wipe all registered tables and re-load them from the backup envelope.

    Runs inside the session's implicit transaction — any failure rolls back
    completely. `users` is never truncated: a users-inclusive envelope
    replaces only non-admin accounts, so admins (and the current login)
    always survive.
    """
    tables: dict[str, list[dict]] = preview.envelope["tables"]
    warnings = list(preview.warnings)
    counts: dict[str, int] = {}
    deferred: list[tuple[BackupTable, str, Any, Any]] = []  # (spec, col, pk, val)

    try:
        await session.execute(text(_truncate_sql()))

        for spec in BACKUP_TABLES:
            raw_rows = tables.get(spec.name) or []
            columns = {c.key: c for c in spec.model.__table__.columns}
            rows: list[dict] = []
            seen_unknown: set[str] = set()
            for raw in raw_rows:
                if spec.sanitize is not None:
                    raw = spec.sanitize(dict(raw))
                row: dict = {}
                for key, v in raw.items():
                    col = columns.get(key)
                    if col is None:
                        if key not in seen_unknown:
                            seen_unknown.add(key)
                            warnings.append(f"{spec.name}: unknown column {key!r} skipped")
                        continue
                    row[key] = _from_json(col, v)
                for fk in spec.deferred_fks:
                    if row.get(fk) is not None:
                        deferred.append((spec, fk, row["id"], row[fk]))
                        row[fk] = None
                rows.append(row)
            if rows:
                await session.execute(spec.model.__table__.insert(), rows)
            counts[spec.name] = len(rows)

        # Pass 2: wire up deferred (self/circular) foreign keys.
        for spec, col, pk, val in deferred:
            await session.execute(
                update(spec.model)
                .where(spec.model.id == pk)
                .values({col: val})
            )

        if preview.includes_users:
            counts["users"] = await _restore_users(
                session, tables.get("users") or [], warnings
            )

        for spec in BACKUP_TABLES:
            if _has_serial_id(spec):
                await session.execute(
                    text(_resync_sequence_sql(spec.name)), {"t": spec.name}
                )
        if preview.includes_users:
            await session.execute(
                text(_resync_sequence_sql("users")), {"t": "users"}
            )

        await session.execute(
            ChangeLog.__table__.insert(),
            [
                {
                    "actor": actor,
                    "action": "create",
                    "object_type": "Backup",
                    "object_id": None,
                    "object_repr": filename,
                    "changes": [
                        {"field": "restored", "before": None, "after": counts}
                    ],
                }
            ],
        )
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    log.info("restored backup %s: %s", filename, counts)
    return {
        "restored": counts,
        "warnings": warnings,
        "backup_created_at": preview.created_at,
    }


# ---------------------------------------------------------------------------
# Scheduled-backup file store (BACKUP_DIR volume)
# ---------------------------------------------------------------------------


def backup_dir() -> Path:
    return Path(settings.backup_dir)


def write_backup_file(payload: bytes, name: str | None = None) -> Path:
    d = backup_dir()
    d.mkdir(parents=True, exist_ok=True)
    path = d / (name or backup_filename())
    path.write_bytes(payload)
    return path


def list_backup_files() -> list[dict]:
    d = backup_dir()
    if not d.is_dir():
        return []
    files = []
    for p in sorted(d.glob("ipambox-backup-*.json.gz"), reverse=True):
        st = p.stat()
        files.append(
            {
                "name": p.name,
                "size": st.st_size,
                "created_at": datetime.fromtimestamp(st.st_mtime).isoformat(),
            }
        )
    return files


def read_backup_file(name: str) -> bytes | None:
    """Fetch a scheduled backup by file name (path-traversal safe)."""
    if Path(name).name != name or not name.endswith(".json.gz"):
        return None
    path = backup_dir() / name
    return path.read_bytes() if path.is_file() else None


def delete_backup_file(name: str) -> bool:
    """Delete a scheduled backup by file name (path-traversal safe)."""
    if Path(name).name != name or not name.endswith(".json.gz"):
        return False
    path = backup_dir() / name
    if not path.is_file():
        return False
    path.unlink()
    return True


def prune_backups(keep: int) -> int:
    """Delete oldest scheduled backups beyond the retention count."""
    d = backup_dir()
    files = sorted(d.glob("ipambox-backup-*.json.gz"), reverse=True)
    removed = 0
    for p in files[max(keep, 0):]:
        p.unlink(missing_ok=True)
        removed += 1
    return removed
