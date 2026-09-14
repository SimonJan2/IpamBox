# IpamBox

**IP Address Management with a built-in LAN scanner** — a self-hosted,
containerized IPAM that keeps your documented network and your real
network in sync.

FastAPI · async SQLAlchemy 2.0 · PostgreSQL 16 · Redis/ARQ worker ·
Scapy raw-socket scanning · Next.js 15 dark-mode UI

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Version](https://img.shields.io/badge/version-0.2.0-green.svg)

---

## What it does

1. **Document** — model sites, VRFs, prefixes, VLANs, IP ranges and
   addresses with consistency rules enforced by the database itself,
   not by convention.
2. **Discover** — a worker ARP/ICMP/TCP-scans your LAN on demand or on
   a schedule, fingerprints hosts (vendor, open ports, device type) and
   reconciles what it finds against your IPAM — so drift between the
   spreadsheet and reality shows up as data, not surprises.

## Features

### IPAM

- **Hierarchy**: `Site → VRF → Prefix → IP address`
- **Overlap safety**: overlapping CIDRs are allowed *across* VRFs but
  rejected *within* a VRF by a PostgreSQL GiST exclusion constraint —
  `container` prefixes are exempt so they can hold child subnets.
- **Atomic allocation**: "next available IP" uses `SELECT … FOR UPDATE`
  + `UNIQUE(vrf_id, address)`; defined IP ranges are excluded
  automatically.
- **Rich object model**: VLAN groups + VLANs, IP ranges
  (dhcp/pool/reserved), IP roles (vip/vrrp/hsrp/glbp/carp/secondary),
  NAT-inside links, colored tags on sites/VRFs/prefixes/addresses.
- **Bulk operations**: select rows → set status/role, tag, delete.
- **CSV**: import addresses (all-or-nothing with per-row error report)
  and export addresses/prefixes.
- **Subnet matrix**: visual /24-style utilization grid per prefix with
  IP-range bands.
- **Change log**: every create/update/delete is recorded with actor,
  timestamp and field-level before/after diffs — global `/changelog`
  page plus per-object history in the IP drawer.

### Scanner

- ARP sweep → ICMP ping-socket sweep → TCP port probe → PTR lookups →
  IEEE OUI vendor resolution (bundled 58k-entry database).
- Persists `open_ports` and a best-effort `device_type` per host
  (router / printer / camera / nas / phone / tv / iot / vm / server /
  workstation).
- **Scheduled scans** via `SCAN_INTERVAL_MINUTES`; multi-network
  targeting via `SCAN_NETWORKS` / `SCAN_EXCLUDE_NETWORKS` /
  `SCAN_ONLY_CONFIGURED`. All scanner settings are also editable at
  runtime from **Settings → Scanning** — changes apply to the worker
  within a minute, no restart needed.
- Cancellable jobs, SSE live progress with ETA, per-CIDR rate limiting.
- **Reconciliation**: new hosts land as `discovered` in the Discovery
  Inbox (bulk confirm/delete), missing `active` hosts go `offline`,
  returning hosts flip back to `active`.

### Platform

- **First-run auth**: the UI asks you to create the admin account on
  first launch (or pre-provision with `IPAMBOX_PASSWORD[_FILE]`).
  Session-cookie login with 5-strike IP lockout.
- **4-tier RBAC**: every account has a role — Administrator, Operator
  (Tier-1), Contributor (Tier-2) or Viewer (Tier-3) — enforced on every
  API route, not just hidden in the UI. The **Users & Roles** console
  under Settings shows role breakdowns and manages accounts. See
  **Roles & permissions** below.
- **Ops endpoints**: `GET /healthz`, `GET /readyz` (checks DB + Redis),
  `GET /metrics` (Prometheus text format with object counts).
- **Backup & restore**: download a full snapshot (every table except the
  login accounts) as a single `.json.gz` from **Settings**, and restore it
  on any IpamBox server — even a fresh install. Restores are atomic,
  preserve IDs, and keep you logged in. Optional scheduled snapshots to a
  docker volume via `BACKUP_INTERVAL_MINUTES`.
- **Settings area**: sidebar-organized sections under `/settings` —
  system overview, runtime scanner config, backup schedule, user/session
  administration, appearance (dark/light theme, density), and
  data-maintenance tools. Runtime-editable options are stored in the
  database and fall back to `.env` values; schedule changes apply without
  a restart.
- **Everything containerized**: one `docker compose up` gives you the
  full stack; Alembic migrations run automatically on API start.

## Architecture

| Service   | Tech                                                   | Host port |
|-----------|--------------------------------------------------------|-----------|
| `web`     | Next.js 15, React 19, Tailwind, TanStack, Recharts     | 3010      |
| `api`     | FastAPI (async), SQLAlchemy 2.0, Alembic, Pydantic 2   | 8001      |
| `scanner` | ARQ worker — Scapy ARP, ICMP ping socket, TCP probes   | —         |
| `db`      | PostgreSQL 16 (`btree_gist` for CIDR overlap rules)    | 127.0.0.1:5432 |
| `redis`   | Redis 7 — ARQ queue, sessions, scan-progress pub/sub   | 127.0.0.1:6379 |

- The browser only ever talks to `web`; API calls go same-origin through
  a Next.js rewrite (`/api/*` → `api:8000`) — no CORS pain.
- `scanner` uses `network_mode: host` with `NET_ADMIN`/`NET_RAW` for real
  L2 ARP access and reaches Postgres/Redis via the loopback-published
  ports. **Linux only** (host networking doesn't exist on Docker
  Desktop).
- Postgres and Redis are bound to `127.0.0.1` — not exposed to the LAN.

## Quick start

```bash
git clone https://github.com/SimonJan2/IpamBox.git
cd IpamBox
cp .env.example .env        # optional — defaults work out of the box
docker compose up --build -d
```

- **UI**: http://localhost:3010 — you'll be redirected to `/setup` to
  create the admin account.
- **API docs**: http://localhost:8001/docs

Seed a sample site + your auto-detected LAN prefix:

```bash
docker compose exec scanner python -m app.services.seeding
```

Trigger a scan from **Scans** in the UI, or via the API:

```bash
curl -b cookies.txt -X POST http://localhost:8001/api/v1/scans \
  -H 'content-type: application/json' -d '{"cidr": "192.168.1.0/24"}'
curl -b cookies.txt -N http://localhost:8001/api/v1/scans/<id>/stream  # live progress
curl -b cookies.txt -X POST http://localhost:8001/api/v1/scans/<id>/cancel
```

## Configuration

Settings follow a **hybrid model**: `.env` provides the defaults (see
[`.env.example`](.env.example) for the annotated list), and the
operational ones marked ✎ below can be overridden at runtime from
**Settings** in the UI — overrides persist in the `app_settings` table,
apply without a restart, and can be reset back to the env value per key.

| Variable | Purpose | Default |
|---|---|---|
| `API_PORT` / `WEB_PORT` | host ports for api/web | `8001` / `3010` |
| `POSTGRES_*` | database credentials | `ipam` / `ipam` / `ipam` |
| `SCAN_INTERFACE` ✎ | pin the scan interface (empty = default-route iface) | — |
| `SCAN_NETWORKS` ✎ | comma-separated CIDRs to scan (empty = auto-detect) | — |
| `SCAN_EXCLUDE_NETWORKS` ✎ | CIDRs that may never be scanned | — |
| `SCAN_ONLY_CONFIGURED` ✎ | refuse scans outside `SCAN_NETWORKS` | `false` |
| `SCAN_INTERVAL_MINUTES` ✎ | recurring scans; `0` = manual only | `0` |
| `SCAN_MIN_INTERVAL_SECONDS` ✎ | per-CIDR manual-scan rate limit | `15` |
| `SCAN_TCP_PORTS` ✎ | ports probed per host | `22,80,443,445,8080` |
| `IPAMBOX_PASSWORD[_FILE]` | pre-provision the admin password | — |
| `IPAMBOX_SESSION_HOURS` ✎ | session lifetime | `168` |
| `IPAMBOX_ALLOW_INSECURE` | disable auth — only behind a trusted proxy | `false` |
| `IPAMBOX_COOKIE_SECURE` | `Secure` cookie flag — set when serving HTTPS | `false` |
| `BACKUP_DIR` | where scheduled snapshots are written (docker volume) | `/backups` |
| `BACKUP_INTERVAL_MINUTES` ✎ | recurring backup interval; `0` = manual only | `0` |
| `BACKUP_KEEP` ✎ | how many scheduled files to retain | `14` |

> **Secrets**: prefer `IPAMBOX_PASSWORD_FILE` (e.g. a Docker secret) over
> `IPAMBOX_PASSWORD` so the value never sits in your env/compose file.

## Pages

| Route | What |
|---|---|
| `/` | Dashboard — totals, status breakdowns, recent scans |
| `/discovery` | Discovery Inbox — confirm/delete scanned hosts |
| `/sites` `/vrfs` `/prefixes` | Core IPAM objects |
| `/prefixes/[id]` | Subnet matrix, IP table, ranges, bulk ops, CSV |
| `/vlans` `/tags` | VLAN groups + VLANs, tag management |
| `/scans` | Trigger/schedule/cancel scans, live progress |
| `/changelog` | Global audit trail |
| `/tree` | Site → VRF → prefix hierarchy view |
| `/settings` | System overview, runtime config, backups, accounts, preferences, maintenance |

The Settings area has its own sub-navigation:

| Route | What |
|---|---|
| `/settings` | General — version, schema rev, DB/Redis health, detected LAN |
| `/settings/scanning` | Networks, excludes, ports, intervals — runtime-editable |
| `/settings/backup` | Snapshots, schedule + retention, restore |
| `/settings/security` | Change password, active sessions |
| `/settings/users` | Users & Roles console — admins only |
| `/settings/appearance` | Theme (dark/light/system), density, page size |
| `/settings/data` | Purge scans/changelog/discovery, CSV exports, factory reset |

## Roles & permissions

Every account carries one role; the API enforces it on each request
(`403` on a denied action) — the UI only hides what you can't use.
Existing accounts migrate to **Administrator** on upgrade, so nothing
locks you out.

| Role | Can | Cannot |
|---|---|---|
| **Administrator** | Everything — data CRUD, backups + restore, runtime settings, user & role management, maintenance/factory reset | — |
| **Tier-1 · Operator** | Add/edit/delete all IPAM data, trigger & download backups | Manage users or roles, change settings, restore, purge, factory reset |
| **Tier-2 · Contributor** | View, add and edit all IPAM data (incl. tag assignments) | Delete anything, trigger/download backups, manage users, change settings |
| **Tier-3 · Viewer** | Read data, reports, changelog, settings overview | Create, edit or delete anything; backups; user admin |

Guardrails: the last administrator can't demote or delete themselves,
and nobody can delete their own account. Changing a user's role or
password revokes all of their sessions immediately.

`IPAMBOX_ALLOW_INSECURE=true` bypasses roles entirely (trusted-proxy
mode) — every request gets full permissions.

## Operations

| Endpoint | Purpose |
|---|---|
| `GET /healthz` | liveness — process up |
| `GET /readyz` | readiness — checks DB + Redis connectivity |
| `GET /metrics` | Prometheus text: object counts, scan status, version info |
| `GET /api/v1/backup` | download a full backup (`*.json.gz`) |
| `GET /api/v1/backup/files` | list scheduled snapshots in `BACKUP_DIR` |
| `POST /api/v1/backup/restore` | restore an uploaded backup (`?dry_run=1` previews) |
| `GET/PATCH /api/v1/settings` | read/patch runtime settings — patch `{"key": null}` resets a key to its env value (PATCH: admin only) |
| `GET/POST /api/v1/users` | list/create user accounts (admin only) |
| `PATCH/DELETE /api/v1/users/{id}` | update/delete users; sessions die with the user (admin only) |
| `POST /api/v1/auth/change-password` | change the current account's password |
| `GET/DELETE /api/v1/auth/sessions` | list/revoke your active sessions |
| `POST /api/v1/maintenance/*` | purge scans/changelog/discovery, factory reset (admin only) |
| `GET /docs` | interactive OpenAPI (Swagger) |

**Restoring to a fresh server**: bring the stack up, create the admin
account at `/setup`, log in, then upload the backup under **Settings →
Restore**. All data tables are replaced inside one transaction with their
original IDs; the `users` table (and your session) are never touched.
Backups record the Alembic schema revision — a file from a newer IpamBox
release is refused rather than half-applied. See **Backup & Restore**
below for the full rundown.

Example Prometheus scrape config:

```yaml
scrape_configs:
  - job_name: ipambox
    metrics_path: /metrics
    static_configs: [{ targets: ["host:8001"] }]
```

## Backup & Restore

A backup is a **single portable file** (`ipambox-backup-<ts>.json.gz`)
containing the whole database state — sites, VRFs, VLAN groups + VLANs,
prefixes, IP ranges, addresses, tags + assignments, runtime settings, the
full changelog and scan history. The `users` table is deliberately
excluded: the admin
account always belongs to the server you're restoring *on*.

### Take a backup

- **UI**: **Settings → Backup → Download backup**.
- **API**: `curl -b cookies.txt -OJ http://localhost:8001/api/v1/backup`
- **Scheduled**: set `BACKUP_INTERVAL_MINUTES` (e.g. `1440` for daily) and
  the worker writes timestamped snapshots into the `backupdata` docker
  volume (`BACKUP_DIR`), keeping the newest `BACKUP_KEEP` files. They show
  up under **Settings → Scheduled backups** for download.
  > The volume lives and dies with the host — copy files off-server
  > (download them, or back up the volume) for real disaster recovery.

### Restore

**Settings → Restore**: pick a `.json.gz` (plain `.json` works too) →
check the preview (created-at, app + schema version, per-table row counts,
warnings) → type `RESTORE` → done. The page reloads into the restored
state; you stay logged in.

```bash
# API equivalent — validate first, then apply
curl -b cookies.txt -X POST "http://localhost:8001/api/v1/backup/restore?dry_run=1" \
  --data-binary @ipambox-backup-20260913-150000.json.gz \
  -H 'content-type: application/gzip'
curl -b cookies.txt -X POST "http://localhost:8001/api/v1/backup/restore" \
  --data-binary @ipambox-backup-20260913-150000.json.gz \
  -H 'content-type: application/gzip'
```

What restore guarantees:

- **Atomic** — everything happens in one transaction; any failure rolls
  back and nothing changes.
- **ID-preserving** — rows come back with their original primary keys, so
  tags, changelog entries, NAT-inside links and every FK stay valid.
- **Schema-checked** — a backup from a *newer* IpamBox (unknown Alembic
  revision) is refused; older-schema files restore fine (new columns get
  their defaults, unknown ones are skipped with a warning).
- **Sane scan state** — jobs that were `queued`/`running` when the backup
  was taken are marked `failed` (they can't resume on the new server).
- **Fresh-install friendly** — the migration-seeded `Global` VRF is
  replaced by the backup's copy, not duplicated.

Avoid restoring while a scan is running — wait for it to finish or cancel
it first.

### Backup file format

```json
{
  "format": "ipambox-backup",
  "format_version": 1,
  "app_version": "0.2.0",
  "alembic_revision": "0009_app_settings",
  "created_at": "2026-09-13T15:07:11",
  "tables": { "sites": [ { "id": 1, "name": "HQ", ... } ], "...": [] }
}
```

**For developers**: which tables are backed up lives in
`BACKUP_TABLES` in `backend/app/services/backup.py` — one registry entry
per table, ordered by FK dependency. New columns are picked up
automatically; a new table needs one line (a test fails if you forget it).

## Development

```bash
docker compose exec api pytest          # test suite (uses a separate ipam_test DB)
docker compose exec api alembic upgrade head   # apply migrations manually
```

- Migrations run automatically when `api` starts; the chain is
  `0001` → `0009`.
- The `scanner` service has its **own image** — after changing backend
  code run `docker compose build api scanner` (or just `build`), not
  `build api` alone.
- Backend layout: `backend/app/{api,core,models,schemas,services,worker}`
- Frontend layout: `frontend/src/{app,components,lib,types}`

## Upgrading

```bash
git pull
docker compose build api scanner web
docker compose up -d        # alembic upgrade head runs on api start
```

## Security

- Auth on by default (first-run setup); bcrypt password hashing,
  HttpOnly session cookies, per-IP login lockout.
- DB/Redis are loopback-only; the web UI is the only public surface.
- See [SECURITY.md](SECURITY.md) for the threat model, deployment
  hardening and how to report vulnerabilities.

## License

[MIT](LICENSE) © SimonJan2 — with a nod to NetBox and LAN-Orangutan for
proving what good looks like.
