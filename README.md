# IpamBox

Containerized IP Address Management (IPAM) with an automated LAN scanner.
FastAPI + async SQLAlchemy + PostgreSQL + Redis/ARQ worker (Scapy/raw-socket
scanning) + a dark-mode Next.js UI.

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

- UI: http://localhost:3010
- API docs: http://localhost:8001/docs

Seed sample data (Site "Home" + auto-detected LAN prefix):

```bash
docker compose exec scanner python -m app.services.seeding
```

Trigger a scan from the UI (Quick scan button, empty CIDR = auto-detect LAN)
or the API:

```bash
curl -X POST http://localhost:8001/api/v1/scans -H 'content-type: application/json' -d '{}'
curl -N  http://localhost:8001/api/v1/scans/<id>/stream   # live SSE progress
```

## Features

- Sites → VRFs → Prefixes → IP addresses; overlapping CIDRs allowed across VRFs,
  forbidden within a VRF (DB-level GiST exclusion constraint; `container`
  prefixes exempt so they can hold children).
- Atomic "next available IP" allocation (`POST /prefixes/{id}/available-ips`)
  guarded by `SELECT … FOR UPDATE` + `UNIQUE(vrf_id, address)`.
- Scanner: ARP sweep → ICMP ping-socket sweep → TCP port probe
  (22/80/443/445/8080) → PTR lookups → IEEE OUI vendor resolution
  (bundled `backend/app/data/oui.json`). Reconciles into
  Active/Discovered/Offline; new hosts land in the Discovery Inbox.
- UI: dashboard with utilization chart, prefix table with search/VRF filter,
  256-cell subnet matrix (virtualized up to /16) with hover cards and an edit
  drawer, prefix hierarchy tree, discovery inbox, live scan manager (SSE).

## Tests

```bash
docker compose exec api pytest        # unit + integration (uses ipam_test DB)
```

## Layout

```
backend/app/{api,core,models,schemas,services,worker}   # FastAPI + ARQ worker
backend/alembic                                         # migrations
frontend/src/{app,components,lib,types}                 # Next.js app
```
