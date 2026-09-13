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
  `SCAN_ONLY_CONFIGURED`.
- Cancellable jobs, SSE live progress with ETA, per-CIDR rate limiting.
- **Reconciliation**: new hosts land as `discovered` in the Discovery
  Inbox (bulk confirm/delete), missing `active` hosts go `offline`,
  returning hosts flip back to `active`.

### Platform

- **First-run auth**: the UI asks you to create the admin account on
  first launch (or pre-provision with `IPAMBOX_PASSWORD[_FILE]`).
  Session-cookie login with 5-strike IP lockout.
- **Ops endpoints**: `GET /healthz`, `GET /readyz` (checks DB + Redis),
  `GET /metrics` (Prometheus text format with object counts).
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

All settings live in `.env` — see [`.env.example`](.env.example) for the
annotated list. Highlights:

| Variable | Purpose | Default |
|---|---|---|
| `API_PORT` / `WEB_PORT` | host ports for api/web | `8001` / `3010` |
| `POSTGRES_*` | database credentials | `ipam` / `ipam` / `ipam` |
| `SCAN_INTERFACE` | pin the scan interface (empty = default-route iface) | — |
| `SCAN_NETWORKS` | comma-separated CIDRs to scan (empty = auto-detect) | — |
| `SCAN_EXCLUDE_NETWORKS` | CIDRs that may never be scanned | — |
| `SCAN_ONLY_CONFIGURED` | refuse scans outside `SCAN_NETWORKS` | `false` |
| `SCAN_INTERVAL_MINUTES` | recurring scans; `0` = manual only | `0` |
| `SCAN_MIN_INTERVAL_SECONDS` | per-CIDR manual-scan rate limit | `15` |
| `SCAN_TCP_PORTS` | ports probed per host | `22,80,443,445,8080` |
| `IPAMBOX_PASSWORD[_FILE]` | pre-provision the admin password | — |
| `IPAMBOX_SESSION_HOURS` | session lifetime | `168` |
| `IPAMBOX_ALLOW_INSECURE` | disable auth — only behind a trusted proxy | `false` |
| `IPAMBOX_COOKIE_SECURE` | `Secure` cookie flag — set when serving HTTPS | `false` |

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

## Operations

| Endpoint | Purpose |
|---|---|
| `GET /healthz` | liveness — process up |
| `GET /readyz` | readiness — checks DB + Redis connectivity |
| `GET /metrics` | Prometheus text: object counts, scan status, version info |
| `GET /docs` | interactive OpenAPI (Swagger) |

Example Prometheus scrape config:

```yaml
scrape_configs:
  - job_name: ipambox
    metrics_path: /metrics
    static_configs: [{ targets: ["host:8001"] }]
```

## Development

```bash
docker compose exec api pytest          # test suite (uses a separate ipam_test DB)
docker compose exec api alembic upgrade head   # apply migrations manually
```

- Migrations run automatically when `api` starts; the chain is
  `0001` → `0008`.
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
