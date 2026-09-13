# IpamBox

Containerized IP Address Management (IPAM) with an automated LAN scanner.
FastAPI + async SQLAlchemy + PostgreSQL + Redis/ARQ worker (Scapy/raw-socket
scanning) + a dark-mode Next.js UI. NetBox-inspired IPAM depth,
LAN-Orangutan-inspired discovery.

## Stack

| Service   | Tech                                                | Port |
|-----------|-----------------------------------------------------|------|
| `web`     | Next.js 15, React 19, Tailwind, TanStack, Recharts  | 3010 |
| `api`     | FastAPI (async), SQLAlchemy 2.0, Alembic, Pydantic  | 8001 |
| `scanner` | ARQ worker, Scapy ARP + ICMP ping-socket + TCP/PTR  | —    |
| `db`      | PostgreSQL 16                                       | 5432 |
| `redis`   | Redis 7 (ARQ queue + scan-progress pub/sub)         | 6379 |

> Host ports default to `API_PORT=8001` / `WEB_PORT=3010` (overridable via `.env`).
> Postgres/Redis publish on `127.0.0.1` only — the `scanner` runs with
> `network_mode: host` + `NET_ADMIN`/`NET_RAW` for real L2 ARP access and
> reaches them over loopback. Linux only (host networking).

## Run

```bash
cp .env.example .env   # optional, defaults work
docker compose up --build -d
```

- UI: http://localhost:3010 — on first launch you'll be asked to create the
  admin password (or pre-provision via `IPAMBOX_PASSWORD[_FILE]`).
- API docs: http://localhost:8001/docs

Seed sample data (Site "Home" + auto-detected LAN prefix):

```bash
docker compose exec scanner python -m app.services.seeding
```

Trigger a scan from the UI (per-network buttons when `SCAN_NETWORKS` is set,
otherwise auto-detect) or the API:

```bash
curl -b session_cookie -X POST http://localhost:8001/api/v1/scans \
  -H 'content-type: application/json' -d '{"cidr": "192.168.1.0/24"}'
curl -b session_cookie -N http://localhost:8001/api/v1/scans/<id>/stream  # live SSE
curl -b session_cookie -X POST http://localhost:8001/api/v1/scans/<id>/cancel
```

## Features

**IPAM**
- Sites → VRFs → Prefixes → IP addresses; overlapping CIDRs allowed across
  VRFs, forbidden within a VRF (DB-level GiST exclusion constraint;
  `container` prefixes exempt so they can hold children).
- Atomic "next available IP" allocation guarded by `SELECT … FOR UPDATE` +
  `UNIQUE(vrf_id, address)`; defined IP ranges are excluded automatically.
- NetBox-style modeling: VLAN groups + VLANs, IP ranges (DHCP pools), IP
  roles (vip/vrrp/hsrp/glbp/carp/secondary), NAT-inside links, colored tags
  on sites/VRFs/prefixes/addresses.
- Bulk operations (status/role/tag/delete) with row selection; CSV
  import (all-or-nothing with per-row errors) and export for addresses
  and prefixes.
- Change log: every create/update/delete is recorded with actor, timestamp
  and field-level diffs; `/changelog` page + per-object history in the IP
  drawer.

**Scanner**
- ARP sweep → ICMP ping-socket sweep → TCP port probe → PTR lookups →
  IEEE OUI vendor resolution (bundled `backend/app/data/oui.json`).
- Persists `open_ports` + a best-effort `device_type` per host
  (router/printer/camera/nas/phone/tv/iot/vm/server/workstation).
- Scheduled scans via `SCAN_INTERVAL_MINUTES`; multi-network config via
  `SCAN_NETWORKS` / `SCAN_EXCLUDE_NETWORKS` / `SCAN_ONLY_CONFIGURED`.
- Cancellable jobs, SSE progress with ETA, one-live-job rate limiting.
- Reconciles into Active/Discovered/Offline; new hosts land in the
  Discovery Inbox (bulk confirm/delete).

**Platform**
- First-run password setup, session-cookie auth, `PASSWORD_FILE` support,
  optional `IPAMBOX_ALLOW_INSECURE` for trusted proxies.
- Ops endpoints: `GET /healthz`, `GET /readyz` (DB+Redis), `GET /metrics`
  (Prometheus text format).
- CI (pytest + Next build + image builds) and a release workflow publishing
  GHCR images on `v*` tags.

## Configuration

See `.env.example`. Highlights:

| Var | Purpose |
|-----|---------|
| `SCAN_INTERFACE` | pin the scan interface (default: default-route iface) |
| `SCAN_NETWORKS` | comma-separated CIDRs to scan (empty = auto-detect) |
| `SCAN_EXCLUDE_NETWORKS` | never scan these |
| `SCAN_ONLY_CONFIGURED` | refuse scans outside `SCAN_NETWORKS` |
| `SCAN_INTERVAL_MINUTES` | scheduled scans; 0 = manual only |
| `SCAN_TCP_PORTS` | ports probed per host |
| `IPAMBOX_PASSWORD[_FILE]` | pre-provision admin password |
| `IPAMBOX_ALLOW_INSECURE` | disable auth (trusted proxy only) |
| `IPAMBOX_SESSION_HOURS` | session lifetime (default 168) |

## Tests

```bash
docker compose exec api pytest        # unit + integration (uses ipam_test DB)
```

## Upgrading

Pull the new images / rebuild, then `docker compose up -d`. Alembic
migrations run automatically on api start (`alembic upgrade head`).

## Layout

```
backend/app/{api,core,models,schemas,services,worker}   # FastAPI + ARQ worker
backend/alembic                                         # migrations
frontend/src/{app,components,lib,types}                 # Next.js app
```
