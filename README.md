# IpamBox

**IP Address Management with a built-in LAN scanner** — a self-hosted,
containerized IPAM that keeps your documented network and your real
network in sync.

FastAPI · async SQLAlchemy 2.0 · PostgreSQL 16 · Redis/ARQ worker ·
Scapy raw-socket scanning · Next.js 15 dark-mode UI

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Version](https://img.shields.io/badge/version-0.3.0-green.svg)

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
- **Subnet semantics**: prefixes carry their `gateway` + `dns_servers`;
  technical addresses get protected `reserved` rows (grid glyphs ⌂/≋,
  changelog-audited), and `dhcp`/`pool` ranges own their members —
  statics inside a pool are rejected unless forced (`force=1`, audited
  as `custom_fields.pool_override`). **Add network** creates
  VLAN + subnet + gateway/DNS + DHCP pool in one transaction.
- **Rich object model**: VLAN groups + VLANs, IP ranges
  (dhcp/pool/reserved), IP roles (vip/vrrp/hsrp/glbp/carp/secondary),
  NAT-inside links, colored tags on sites/VRFs/prefixes/addresses.
- **Bulk operations**: select rows → set status/role, tag, delete.
- **CSV**: import addresses (all-or-nothing with per-row error report)
  and export addresses/prefixes (UTF-8 BOM — opens cleanly in Excel).
- **Excel workbook import**: upload a `Network_Address.xlsx`-style
  workbook under **Import** → per-sheet type detection → dry-run preview
  with a per-row conflict/error report → commit all-or-nothing or
  partial (per-sheet rollback). Handles the messy bits: split-octet IPs,
  multi-IP cells, MACs in four formats, Excel serial dates, repeated
  headers and duplicated column blocks. Hebrew content is normalized and
  every imported row keeps provenance back to its upload batch.
- **Extended entities**: WAN circuits, certificate expiry tracking
  (30-day countdown), SW/HW asset + serial-number inventory, rack
  elevations, and a service catalog — first-class tables with pages,
  search, RBAC, backup and changelog coverage.
- **Devices**: first-class device inventory — a device owns many IPs
  (mgmt + service + iLO), links an asset and a site, and optionally sits
  in a rack. Health is the worst status across its linked IPs; unracked
  devices are valid inventory. Smart file I/O: the **Export** dropdown
  downloads the currently filtered set as CSV (UTF-8 BOM) or XLSX —
  what the page shows is what exports. **Import** auto-maps headers
  (canonical + English + Hebrew + NetBox shape), matches existing devices
  by id → serial → MAC → name+site, previews every row's action with
  honest diffs, validates placement against the batch and the DB,
  two-passes carrier mounts, links existing IPs (never creates them),
  and commits all-or-nothing (or `force` for the valid rows) — export
  output re-imports cleanly, with `source="import"` provenance on new
  rows.
- **Cabling**: devices own **interfaces** (rj45/sfp/qsfp/console/patch/
  power) with one-click port generation — including patch-panel front+back
  pairs in a single call. **Device templates** (Devices → Templates) take
  that further: a reusable typed port layout (e.g. `switch-48` = 48×1G +
  4×SFP28 uplinks, `patch-panel-24` = paired front/rear) that stamps a
  device's whole interface set in one apply — merge reports skipped names
  honestly, replace refuses while any port is cabled, and both create
  dialogs can instantiate the device + its ports in one transaction.
  ~10 builtins seed at startup; user templates edit in a port-grid editor
  with a range expander (`Gi1/0/1..48 sfp28 25000`). **Cables** connect
  ports with one-cable-per-
  interface enforcement, and an **L1 trace** walks the chain end to end —
  `host → panel-front → panel-back → switch` — hopping panel pass-throughs.
  IPs gain a structured `connected_interface` link alongside the legacy
  `switch_name`/`switch_port` free text, with an exact-name matcher
  endpoint to transition old data. Cable labels and port names resolve to
  their devices in global search. On SNMP-managed devices, each poll
  validates documented cabling against observed state — a cabled port
  reporting down, a far end whose MACs never appear on the port, or an
  LLDP neighbor on an uncabled port raises a `cable_mismatch` flag (⚠ on
  the port, count in the device header + dashboard, triage in
  `/review`); flags self-heal on the next contradictory-free poll and are
  never auto-fixed. The SNMP card also offers **Pull inventory**: the
  device teaches IpamBox its VLAN database, SVI/L3 subnets and ARP
  neighbors through a preview → one-transaction apply (a committed
  `kind="snmp"` import batch for provenance), with honest conflict rows
  wherever `manual`/`import` data outranks what the device reports.
- **Topology map**: `/topology` draws the network as a canvas — devices
  are nodes, *documented cables* are edges (parallel runs collapse into
  one edge with a count + kind labels; panel chains stay honest — two
  edges via the panel, never a synthesized hop). Nodes nest inside
  site → rack group → rack containers (unracked devices get a "No rack"
  lane, undiscovered-but-seen IPs an "Unlinked hosts" lane), laid out by
  a bundled elk layerer. A health overlay dots each node with its worst
  linked-IP status, `cable_mismatch` edges draw red with ⚠, and dragging
  rearranges freely — positions persist only via **Save layout**
  (`diagram_layouts`, backed up, deliberately not changelog-audited).
  Read-only by design: it's a lens on L1 truth, not an editor.
- **Rack elevations**: racks with per-U device placement on front/rear
  faces, a read-only SVG elevation view, and collision validation
  (front+rear share a U; same-face overlaps are rejected). Live scan-health
  dots reflect each device's worst linked-IP status, a next-free-U finder,
  a printable report and
  QR labels. **Rack groups** render bayed rows — ordered racks side by side
  with per-rack and per-row U/power/weight rollups, and an edit mode for
  dragging devices across racks. A dashboard card charts fleet capacity.
  Racks and groups round-trip as **smart bundles**: the filtered rack view
  exports a flat CSV or a multi-sheet XLSX (groups → racks → devices →
  interfaces → cables, every reference by name), a group page exports the
  whole row in one file, and the smart importer previews per-sheet actions
  — sites/groups/racks match by name, devices follow the device importer's
  rules, placement conflicts are reported never forced, and a group export
  re-imported into an empty install rebuilds the identical tree. Round-trips
  with a self-hosted
  [Rackula](https://github.com/RackulaLives/Rackula) instance via share URLs
  and `.Rackula.zip` archives for heavy editing.
- **Hebrew data support**: final-letter folding in search (type
  `רשת`, match `רשתו`), `dir="auto"` on free-text cells so RTL text
  renders correctly, LTR-pinned IP/MAC columns, Hebrew-safe site slugs.
- **Subnet matrix**: visual /24-style utilization grid per prefix with
  IP-range bands, plus a sortable list view with aggregated free ranges
  and per-IP actions.
- **Change log**: every create/update/delete is recorded with actor,
  timestamp and field-level before/after diffs — global `/changelog`
  page plus per-object history in the IP drawer.
- **Global row colors**: tint any list row — sites, VRFs, VLANs,
  circuits, certificates, assets, services, tags and the address list —
  with a manual color (per-row "Set color" action), or define
  admin-managed rules under **Settings → Color Rules** that color rows
  by field (`cert expiring within 7 days → red`). Stored in Postgres,
  computed server-side, and covered by backup + changelog.

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
  returning hosts flip back to `active`. When a scanned MAC disagrees
  with a stored (e.g. imported) MAC, the live value wins but the address
  is flagged `mac_mismatch` for review — the dashboard counts them and
  the `/review` queue carries the fix actions.

### Review center

- **One queue for every flag** — `/review` (`g v`) collects ten live,
  computed sections ordered worst-first: MAC mismatches, cable
  mismatches, duplicate-MAC groups, aging discoveries, offline hosts past
  the grace scans, certificates inside `cert_warn_days`, unmatched legacy
  switch refs, unmanaged SNMP senders, uncabled devices and unracked
  devices. Nothing is stored for the finding itself — no worker, no cron.
- **Real actions, honest changelog** — confirm/delete go through the
  entity's own endpoints; MAC-mismatch rows offer **Accept scanned**
  (write the observed MAC) or **Keep stored** (restore the documented
  MAC *and* permanently dismiss that MAC pair — the per-address form of
  `scan_stored_mac_wins`, built for shared dock/NIC MACs).
- **Dismissal is data, not deletion** — `review_dismissals` rows pin the
  finding's fingerprint (the MAC pair, the switch/port text, the dup-MAC
  group), so a dismissal survives re-flagging, carries an actor + note,
  is itself audited, and restores with one click.
- **Resolver surface** — the legacy `switch_name`/`switch_port` matcher
  runs from the unmatched-switch card
  (`POST /api/v1/review/resolve-switch-fields`) and reports
  matched/ambiguous/unmatched inline.
- The dashboard's **Review queue** card shows the open count and the
  current worst section.

### Monitoring

- **Per-target health checks** — `ping` (ICMP), `tcp` (port connect) and
  `http` (GET against an expectation: empty = any 2xx/3xx, `status:NNN` =
  exact code, anything else = body substring). Targets anchor to a device
  or an IP address.
- **Hysteresis**: a target flips `down` only after `down_after`
  consecutive failures and recovers on the first success — no flapping
  alerts. State changes emit events; steady state stays silent and never
  touches the changelog.
- **Second worker lane**: a per-minute cron batches all due targets into
  ONE `run_monitor_sweep` job (semaphore-bounded probes, runtime-tunable)
  so monitoring shares the `max_jobs=4` pool without starving scans.
- **Notification channels** — webhook, SMTP, Discord and Telegram — carry
  monitor transitions plus `cert.expiring`, `scan.failed`,
  `mac_mismatch` and `cable.mismatch` events. Channel secrets (webhook URLs, SMTP passwords,
  bot tokens) are encrypted with `IPAMBOX_SECRET_KEY` and are write-only
  in the API; every delivery attempt is recorded in the notification log.
- Surfaces: the live `/monitoring` board (10s poll), a dashboard card
  with danger styling on down, per-device/IP monitor sections, and
  channel admin + delivery log under **Settings → Monitoring**.

### Reports

- **The estate on one page** — `/reports` assembles every aggregate the
  other pages already compute: per-site fill, address status,
  utilization outliers, rack capacity, certificate expiry, scan history,
  open flags, device health and monitor state. Nothing is persisted; a
  report that disagrees with the dashboard is a bug, not a viewpoint.
- **Site scoping** — the whole report narrows to one site via
  `?site_id=` (the per-site report is the common case).
- **Every way out** — a print view (`/reports/print`, browser print with
  the detail tables expanded), a multi-sheet XLSX workbook
  (`/api/v1/reports/export.xlsx`, one sheet per section), and a CSV per
  section (`/api/v1/reports/{section}.csv`, UTF-8 BOM). Large sections
  are capped at 500 rows and marked `truncated`.
- **Email this report** — sends the text digest through the enabled
  notification channels (no attachments); an optional weekly digest rides
  the same path via *Settings → Monitoring → Weekly report digest*.

### Platform

- **First-run auth**: the UI asks you to create the admin account on
  first launch (or pre-provision with `IPAMBOX_PASSWORD[_FILE]`).
  Session-cookie login with 5-strike (user, IP) lockout plus a per-IP
  credential-stuffing backstop.
- **4-tier RBAC**: every account has a role — Administrator, Operator
  (Tier-1), Contributor (Tier-2) or Viewer (Tier-3) — enforced on every
  API route, not just hidden in the UI. The **Users & Roles** console
  under Settings shows role breakdowns and manages accounts. See
  **Roles & permissions** below.
- **Ops endpoints**: `GET /healthz`, `GET /readyz` (checks DB + Redis),
  `GET /metrics` (Prometheus text format with object counts).
- **Docs workspace**: built-in guides plus user-authored **Pages**
  (markdown runbooks/notes with a side-by-side editor at
  `/docs/pages/new`) and **attachments** on devices, racks, sites, IPs,
  certificates, circuits and assets — files ≤6 MB (images, PDF, text,
  ZIP) stored in Postgres, so backups and the changelog cover them and
  deleting an entity sweeps its files in the same transaction.
- **Backup & restore**: download a full snapshot as a single `.json.gz`
  from **Settings** — user accounts are excluded by default (admins always
  are), with an admin-only opt-in for non-admin accounts — and restore it
  on any IpamBox server, even a fresh install. Restores are atomic,
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
- **Exposure model**: both `web` (`:3010`) and `api` (`:8001`) are
  published on all interfaces by default — direct `/docs`, `/metrics` and
  script access from the LAN is deliberate. The API still requires auth
  (and rate-limits logins), but it is a reachable attack surface: set
  `API_BIND=127.0.0.1` to restrict it to loopback so only the web UI is
  reachable. Postgres and Redis stay bound to `127.0.0.1` — never exposed
  to the LAN.
- `scanner` uses `network_mode: host` with `NET_ADMIN`/`NET_RAW` for real
  L2 ARP access and reaches Postgres/Redis via the loopback-published
  ports. **Linux only** (host networking doesn't exist on Docker
  Desktop).

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
| `API_BIND` | interface the published API port binds to (`127.0.0.1` = loopback-only) | `0.0.0.0` |
| `POSTGRES_*` | database credentials | `ipam` / `ipam` / `ipam` |
| `SCAN_INTERFACE` ✎ | pin the scan interface (empty = default-route iface) | — |
| `SCAN_NETWORKS` ✎ | comma-separated CIDRs to scan (empty = auto-detect) | — |
| `SCAN_EXCLUDE_NETWORKS` ✎ | CIDRs that may never be scanned | — |
| `SCAN_ONLY_CONFIGURED` ✎ | refuse scans outside `SCAN_NETWORKS` | `false` |
| `SCAN_INTERVAL_MINUTES` ✎ | recurring scans; `0` = manual only | `0` |
| `SCAN_MIN_INTERVAL_SECONDS` ✎ | per-CIDR manual-scan rate limit | `15` |
| `SCAN_MAX_HOSTS` ✎ | refuse scan targets above this usable-host count | `4096` |
| `SCAN_TCP_PORTS` ✎ | ports probed per host | `22,80,443,445,8080` |
| `IPAMBOX_PASSWORD[_FILE]` | pre-provision the admin password | — |
| `IPAMBOX_SESSION_HOURS` ✎ | session lifetime | `168` |
| `IPAMBOX_ALLOW_INSECURE` | disable auth — only behind a trusted proxy | `false` |
| `IPAMBOX_COOKIE_SECURE` | `Secure` cookie flag — set when serving HTTPS | `false` |
| `IPAMBOX_TRUSTED_PROXIES` | peers whose `X-Forwarded-For` is honored (login lockout keying) — must include `web`'s pinned bridge IP | `127.0.0.1,::1,192.0.2.10` |
| `BACKUP_DIR` | where scheduled snapshots are written (docker volume) | `/backups` |
| `BACKUP_INTERVAL_MINUTES` ✎ | recurring backup interval; `0` = manual only | `0` |
| `BACKUP_KEEP` ✎ | how many scheduled files to retain | `14` |
| `IMPORT_DIR` | where uploaded workbooks are stored for re-preview/commit | `<BACKUP_DIR>/imports` |
| `IPAMBOX_RACKULA_BASE_URL` ✎ | self-hosted Rackula URL enabling "Open in Rackula" | — |
| `MONITORING_ENABLED` ✎ | master switch for the health-check lane | `true` |
| `MONITOR_CONCURRENCY` ✎ | parallel probes inside one monitor sweep | `64` |
| `MONITOR_HTTP_TIMEOUT` ✎ | per-request timeout for http checks (s) | `5` |
| `NOTIFY_RETENTION_DAYS` ✎ | notification-log retention; `0` = keep | `0` |

> **Secrets**: prefer `IPAMBOX_PASSWORD_FILE` (e.g. a Docker secret) over
> `IPAMBOX_PASSWORD` so the value never sits in your env/compose file.

## Pages

| Route | What |
|---|---|
| `/` | Dashboard — totals, status breakdowns, recent scans, entity counts |
| `/discovery` | Discovery Inbox — confirm/delete scanned hosts |
| `/review` | Review center — every flag on one triage queue |
| `/sites` `/vrfs` `/prefixes` | Core IPAM objects |
| `/prefixes/[id]` | Address map (grid/list views), ranges, bulk ops, CSV |
| `/prefixes` → Add network | One-transaction wizard: VLAN + subnet + gateway/DNS + DHCP pool |
| `/circuits` `/certificates` | WAN circuits, certificate expiry (30d countdown) |
| `/inventory` `/services` | SW/HW + serial inventory, service catalog |
| `/racks` `/racks/[id]` `/racks/groups/[id]` `/racks/[id]/print` | Rack list + groups, live elevation, bayed row view, print report + QR labels, Rackula round-trip |
| `/devices` `/devices/[id]` | First-class device inventory — multi-IP links, worst-of health, optional rack placement, interfaces + cables + L1 trace |
| `/import` | Workbook import wizard — upload, detection, preview, commit |
| `/vlans` `/tags` | VLAN groups + VLANs, tag management |
| `/scans` | Trigger/schedule/cancel scans, live progress |
| `/monitoring` | Live monitor board — up/down states, check kind, last error, check-now |
| `/reports` `/reports/print` | Estate-wide report workspace — all sections on one page, print view, per-section CSV + multi-sheet XLSX, optional email digest |
| `/changelog` | Global audit trail |
| `/docs` `/docs/[slug]` | Built-in guides — every feature documented |
| `/docs/pages` `/docs/pages/new` `/docs/pages/[slug]` `/docs/pages/[slug]/edit` | User-authored markdown pages — runbooks/notes beside the builtin help |
| `/tree` | Site → VRF → prefix hierarchy view |
| `/topology` | Device-adjacency canvas — documented cables as edges, site/rack grouping, health + mismatch overlays, saved layout |
| `/settings` | System overview, runtime config, backups, accounts, preferences, maintenance |

The Settings area has its own sub-navigation:

| Route | What |
|---|---|
| `/settings` | General — version, schema rev, DB/Redis health, detected LAN |
| `/settings/scanning` | Networks, excludes, ports, intervals — runtime-editable |
| `/settings/monitoring` | Notification channels + secrets, check-lane toggles, delivery log — admins only |
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
| `GET /api/v1/backup` | download a full backup (`*.json.gz`); `?include_users=1` also exports non-admin accounts (admin only) |
| `GET /api/v1/backup/files` | list scheduled snapshots in `BACKUP_DIR` |
| `POST /api/v1/backup/restore` | restore an uploaded backup (`?dry_run=1` previews) |
| `GET/PATCH /api/v1/settings` | read/patch runtime settings — patch `{"key": null}` resets a key to its env value (PATCH: admin only) |
| `GET/POST /api/v1/users` | list/create user accounts (admin only) |
| `PATCH/DELETE /api/v1/users/{id}` | update/delete users; sessions die with the user (admin only) |
| `GET /api/v1/reports/summary` | estate report — every section in one bounded payload (`?site_id=` scopes) |
| `GET /api/v1/reports/export.xlsx` | the same report as a multi-sheet workbook |
| `GET /api/v1/reports/{section}.csv` | one section as CSV (UTF-8 BOM) |
| `POST /api/v1/reports/email` | send the digest to enabled notification channels |
| `POST /api/v1/auth/change-password` | change the current account's password |
| `GET/DELETE /api/v1/auth/sessions` | list/revoke your active sessions |
| `POST /api/v1/maintenance/*` | purge scans/changelog/discovery, factory reset (admin only) |
| `GET /docs` | interactive OpenAPI (Swagger) |

**Restoring to a fresh server**: bring the stack up, create the admin
account at `/setup`, log in, then upload the backup under **Settings →
Restore**. All data tables are replaced inside one transaction with their
original IDs; the `users` table is never touched unless the file was
exported with `?include_users=1` — and even then only non-admin accounts
are replaced, so the admin you just created (and your session) always
survives. Backups record the Alembic schema revision — a file from a newer
IpamBox release is refused rather than half-applied. See **Backup &
Restore** below for the full rundown.

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
prefixes, IP ranges, addresses, tags + assignments, circuits,
certificates, assets, services, import batches, runtime settings, the
full changelog and scan history. The `users` table is excluded by
default: accounts usually belong to the server you're restoring *on*.
Admins can opt in to exporting **non-admin** accounts (operators,
contributors, viewers) — admin accounts are never written into a backup,
so a file can never carry an admin's credentials.

### Take a backup

- **UI**: **Settings → Backup → Download backup**. Admins can tick
  **Include user accounts (non-admin)** first — the resulting file
  contains password hashes, so store it like a secret.
- **API**: `curl -b cookies.txt -OJ http://localhost:8001/api/v1/backup`
  (append `?include_users=1` for non-admin accounts; requires the
  Administrator role instead of the usual backup permission).
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
- **Admin-safe** — admin accounts are never exported and never modified by
  a restore. A users-inclusive file replaces only the *non-admin* set:
  admin rows inside it are ignored (with a warning), and payload rows
  colliding with an existing admin id/username are skipped rather than
  overwriting the admin.

Avoid restoring while a scan is running — wait for it to finish or cancel
it first.

### Backup file format

```json
{
  "format": "ipambox-backup",
  "format_version": 1,
  "app_version": "0.3.0",
  "alembic_revision": "0011_import_entities",
  "created_at": "2026-09-13T15:07:11",
  "includes_users": true,
  "tables": { "sites": [ { "id": 1, "name": "HQ", ... } ], "...": [] }
}
```

`includes_users` is present only on `?include_users=1` exports — it marks
`tables.users` (non-admin accounts) as restorable.

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
  `0001` → `0011`.
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
  HttpOnly session cookies, per-(user, IP) login lockout with a per-IP
  credential-stuffing backstop.
- `web` and `api` are LAN-reachable by default (the API requires auth);
  DB/Redis are loopback-only. `API_BIND=127.0.0.1` restricts the API to
  loopback.
- Over plain HTTP the session cookie crosses the LAN in cleartext —
  deploy behind HTTPS or on a trusted network only.
- See [SECURITY.md](SECURITY.md) for the threat model, deployment
  hardening and how to report vulnerabilities.

## License

[MIT](LICENSE) © SimonJan2 — with a nod to NetBox and LAN-Orangutan for
proving what good looks like.
