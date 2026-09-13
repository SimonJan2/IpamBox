# Graph Report - IpamBox  (2026-09-13)

## Corpus Check
- 124 files · ~153,764 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: (none) 7, .ini 2, .example 1)

## Summary
- 874 nodes · 2521 edges · 46 communities (30 shown, 2 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 242 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9fb3541e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- prefixes.py
- ipam.py
- v1/auth.py
- IPAMError
- prefixes/page.tsx
- index.ts
- dependencies
- scanner.py
- IPAddress
- vlans.py
- scans/page.tsx
- cn
- scans.py
- api service (FastAPI backend)
- subnet-grid.tsx
- [id]/page.tsx
- compilerOptions
- reserve_next_available
- button.tsx
- test_ipam_extras.py
- test_prefix_api.py
- test_changelog.py
- test_scanner.py
- layout.tsx
- IpamBox App Icon (icon.svg)
- package.json
- bcrypt 4.3.0
- IpamBox
- worker.py
- get_redis
- devDependencies
- scripts

## God Nodes (most connected - your core abstractions)
1. `cn()` - 63 edges
2. `IPAMError` - 43 edges
3. `get_or_404()` - 41 edges
4. `IPAddress` - 39 edges
5. `react` - 35 edges
6. `Prefix` - 33 edges
7. `Base` - 26 edges
8. `VRF` - 24 edges
9. `lucide-react` - 23 edges
10. `to_network()` - 22 edges

## Surprising Connections (you probably didn't know these)
- `api service (FastAPI backend)` --references--> `alembic 1.14.0`  [INFERRED]
  docker-compose.yml → backend/requirements.txt
- `api service (FastAPI backend)` --references--> `uvicorn[standard] 0.32.1`  [INFERRED]
  docker-compose.yml → backend/requirements.txt
- `fastapi 0.115.6` --implements--> `api service (FastAPI backend)`  [INFERRED]
  backend/requirements.txt → docker-compose.yml
- `pydantic 2.10.3` --implements--> `api service (FastAPI backend)`  [INFERRED]
  backend/requirements.txt → docker-compose.yml
- `sqlalchemy[asyncio] 2.0.36` --implements--> `api service (FastAPI backend)`  [INFERRED]
  backend/requirements.txt → docker-compose.yml

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Authentication & session security flow** — req_bcrypt, compose_api [INFERRED 0.85]
- **LAN scan pipeline (compose worker + Scapy + documented flow + reconciliation)** — compose_scanner, req_scapy [INFERRED 0.85]
- **PostgreSQL persistence stack (db + SQLAlchemy/asyncpg + Alembic + api)** — compose_db, req_sqlalchemy, req_asyncpg, req_alembic, compose_api [INFERRED 0.85]

## Communities (46 total, 2 thin omitted)

### Community 0 - "prefixes.py"
Cohesion: 0.07
Nodes (59): allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), prefix_tree() (+51 more)

### Community 1 - "ipam.py"
Cohesion: 0.06
Nodes (62): list_changelog(), AsyncSession, get, AsyncSession, get, stats(), _check_range_overlap(), create_range() (+54 more)

### Community 2 - "v1/auth.py"
Cohesion: 0.07
Nodes (53): do_run_migrations(), run_migrations_online(), auth_status(), _current_user(), ensure_env_password_user(), login(), logout(), me() (+45 more)

### Community 3 - "IPAMError"
Cohesion: 0.07
Nodes (57): create_site(), delete_site(), get_site(), list_sites(), AsyncSession, delete, get, patch (+49 more)

### Community 4 - "prefixes/page.tsx"
Cohesion: 0.11
Nodes (28): PrefixesPage(), utilColor(), VLAN_STATUSES, QuickScanDialog(), useScanStream(), TAG_COLORS, Dialog, DialogClose (+20 more)

### Community 5 - "index.ts"
Cohesion: 0.07
Nodes (34): ROLES, STATUSES, IpStatusBadge(), ipVariant, prefixVariant, ScanStatusBadge(), scanVariant, Badge() (+26 more)

### Community 6 - "dependencies"
Cohesion: 0.10
Nodes (21): dependencies, class-variance-authority, clsx, lucide-react, next, @radix-ui/react-dialog, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+13 more)

### Community 7 - "scanner.py"
Cohesion: 0.12
Nodes (21): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), detect_interface(), detect_local_cidr(), _icmp_sweep(), _ptr_lookup() (+13 more)

### Community 8 - "IPAddress"
Cohesion: 0.09
Nodes (44): Any, bulk_addresses(), BulkBody, create_address(), delete_address(), export_addresses(), get_address(), import_addresses() (+36 more)

### Community 9 - "vlans.py"
Cohesion: 0.18
Nodes (26): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+18 more)

### Community 10 - "scans/page.tsx"
Cohesion: 0.18
Nodes (19): ACTION_STYLES, ChangelogPage(), ChangeSummary(), fmt(), DiscoveryPage(), DashboardPage(), AddressTable(), fmtEta() (+11 more)

### Community 11 - "cn"
Cohesion: 0.11
Nodes (27): PrefixTreeNode(), AddressFilterPanel(), STATUS_DOT, STATUSES, PrefixStatusBadge(), TagDialog(), Card, CardContent() (+19 more)

### Community 12 - "scans.py"
Cohesion: 0.15
Nodes (19): _check_cidr_allowed(), create_scan(), get_scan(), list_scans(), AsyncSession, get, SSE stream of scan progress (Redis pub/sub backed)., Scanner configuration surfaced to the UI. (+11 more)

### Community 13 - "api service (FastAPI backend)"
Cohesion: 0.15
Nodes (19): api service (FastAPI backend), db service (postgres:16-alpine), redis service (redis:7-alpine), scanner service (ARQ worker), web service (Next.js frontend), alembic 1.14.0, arq 0.26.1, asyncpg 0.30.0 (+11 more)

### Community 14 - "subnet-grid.tsx"
Cohesion: 0.18
Nodes (12): CellState, stateClass, SubnetGrid(), Tooltip, TooltipContent, TooltipTrigger, intToIp(), ipToInt() (+4 more)

### Community 15 - "[id]/page.tsx"
Cohesion: 0.20
Nodes (15): IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, toggleIn(), TagChip(), TagPicker(), useTags() (+7 more)

### Community 16 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 17 - "reserve_next_available"
Cohesion: 0.16
Nodes (19): ConflictError, Atomically allocate the lowest free usable IP in a prefix. SERIALIZES on the…, reserve_next_available(), _base_dsn(), client(), engine(), _prepare_test_db(), fixture (+11 more)

### Community 18 - "button.tsx"
Cohesion: 0.32
Nodes (6): AUTH_ROUTES, NAV, Button, ButtonProps, buttonVariants, AuthStatus

### Community 19 - "test_ipam_extras.py"
Cohesion: 0.42
Nodes (9): _prefix(), test_address_role_nat_and_bulk(), test_container_move_with_children_rejected(), test_csv_export_import(), test_ip_ranges_exclude_allocator(), test_prefix_move_vrf(), test_tags_crud_and_assignment(), test_vlan_group_and_prefix_link() (+1 more)

### Community 20 - "test_prefix_api.py"
Cohesion: 0.46
Nodes (7): _global_vrf_id(), test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_same_cidr_allowed_across_vrfs(), test_split_endpoint(), test_tree_endpoint(), test_unknown_vlan_rejected()

### Community 21 - "test_changelog.py"
Cohesion: 0.60
Nodes (4): AsyncClient, test_changelog_captures_ip_status_change(), test_changelog_records_crud(), test_changelog_scoped_filters()

### Community 22 - "test_scanner.py"
Cohesion: 0.13
Nodes (14): AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), HostResult, infer_device_type(), Best-effort device classification; None when nothing matched., fake_arq(), _pool() (+6 more)

### Community 31 - "layout.tsx"
Cohesion: 0.25
Nodes (5): nextConfig, metadata, AppShell(), TooltipProvider, next

### Community 39 - "package.json"
Cohesion: 0.09
Nodes (21): name, private, version, autoprefixer, clsx, postcss, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+13 more)

### Community 41 - "IpamBox"
Cohesion: 0.12
Nodes (16): Architecture, Configuration, Development, Features, IPAM, IpamBox, License, Operations (+8 more)

### Community 42 - "worker.py"
Cohesion: 0.20
Nodes (15): ArqRedis, _job_payload(), get_arq_pool(), redis_settings_from_url(), str, ScanJob, ScanStatus, _cron_jobs() (+7 more)

### Community 43 - "get_redis"
Cohesion: 0.19
Nodes (14): cancel_scan(), post, get_redis(), cancel_key(), _eta_seconds(), _global_vrf_id(), _publish(), Prefix (+6 more)

### Community 44 - "devDependencies"
Cohesion: 0.25
Nodes (8): devDependencies, autoprefixer, postcss, tailwindcss, @types/node, @types/react, @types/react-dom, typescript

### Community 45 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

## Knowledge Gaps
- **119 isolated node(s):** `WorkerSettings`, `nextConfig`, `name`, `version`, `private` (+114 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 270 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `IPAddress` connect `IPAddress` to `prefixes.py`, `ipam.py`, `scanner.py`, `worker.py`, `scans.py`, `reserve_next_available`, `test_scanner.py`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Why does `IPAMError` connect `IPAMError` to `prefixes.py`, `ipam.py`, `IPAddress`, `vlans.py`, `scans.py`, `reserve_next_available`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Why does `get_or_404()` connect `IPAMError` to `prefixes.py`, `ipam.py`, `IPAddress`, `vlans.py`, `scans.py`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `IPAMError` (e.g. with `create_address()` and `delete_address()`) actually correct?**
  _`IPAMError` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `IPAddress` (e.g. with `bulk_addresses()` and `create_address()`) actually correct?**
  _`IPAddress` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `WorkerSettings`, `nextConfig`, `name` to the rest of the system?**
  _119 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `prefixes.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07226107226107226 - nodes in this community are weakly interconnected._