# Graph Report - IpamBox  (2026-09-13)

## Corpus Check
- 125 files · ~152,496 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: (none) 7, .ini 2, .example 1)

## Summary
- 781 nodes · 2311 edges · 42 communities (23 shown, 4 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 242 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- IP Address API
- Scan API Endpoints
- Auth & DB Migration Env
- Sites Dashboard Changelog API
- Prefix VLAN VRF Pages
- Tree View & IP Drawer
- Frontend Dependencies
- Network Scanner Worker
- Tags API
- VLAN API
- Scans & Discovery Pages
- Login Setup Dashboard Pages
- IP Ranges API
- Docker Deployment Stack
- Subnet Grid Components
- Prefix Detail & Tag Picker
- TypeScript Config
- Test Fixtures & Allocation
- App Shell & Layout
- IPAM Extras Tests
- Prefix API Tests
- Changelog Tests
- Badge Component
- Next.js Config
- App Icon Conventions
- Bcrypt Dependency
- Security Policy Doc

## God Nodes (most connected - your core abstractions)
1. `cn()` - 61 edges
2. `IPAMError` - 43 edges
3. `get_or_404()` - 41 edges
4. `IPAddress` - 39 edges
5. `Prefix` - 33 edges
6. `Base` - 26 edges
7. `VRF` - 24 edges
8. `to_network()` - 22 edges
9. `get_settings()` - 21 edges
10. `IPStatus` - 21 edges

## Surprising Connections (you probably didn't know these)
- `fastapi 0.115.6` --implements--> `api service (FastAPI backend)`  [INFERRED]
  backend/requirements.txt → docker-compose.yml
- `api service (FastAPI backend)` --references--> `uvicorn[standard] 0.32.1`  [INFERRED]
  docker-compose.yml → backend/requirements.txt
- `sqlalchemy[asyncio] 2.0.36` --implements--> `api service (FastAPI backend)`  [INFERRED]
  backend/requirements.txt → docker-compose.yml
- `sqlalchemy[asyncio] 2.0.36` --shares_data_with--> `db service (postgres:16-alpine)`  [INFERRED]
  backend/requirements.txt → docker-compose.yml
- `api service (FastAPI backend)` --references--> `alembic 1.14.0`  [INFERRED]
  docker-compose.yml → backend/requirements.txt

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **LAN scan pipeline (compose worker + Scapy + documented flow + reconciliation)** — compose_scanner, req_scapy [INFERRED 0.85]
- **Authentication & session security flow** — req_bcrypt, compose_api [INFERRED 0.85]
- **PostgreSQL persistence stack (db + SQLAlchemy/asyncpg + Alembic + api)** — compose_db, req_sqlalchemy, req_asyncpg, req_alembic, compose_api [INFERRED 0.85]

## Communities (42 total, 4 thin omitted)

### Community 0 - "IP Address API"
Cohesion: 0.06
Nodes (98): Any, bulk_addresses(), BulkBody, create_address(), delete_address(), export_addresses(), get_address(), import_addresses() (+90 more)

### Community 1 - "Scan API Endpoints"
Cohesion: 0.06
Nodes (68): ArqRedis, cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession (+60 more)

### Community 2 - "Auth & DB Migration Env"
Cohesion: 0.08
Nodes (48): do_run_migrations(), run_migrations_online(), auth_status(), _current_user(), ensure_env_password_user(), login(), logout(), me() (+40 more)

### Community 3 - "Sites Dashboard Changelog API"
Cohesion: 0.07
Nodes (39): list_changelog(), AsyncSession, get, AsyncSession, get, stats(), create_site(), delete_site() (+31 more)

### Community 4 - "Prefix VLAN VRF Pages"
Cohesion: 0.12
Nodes (25): PrefixesPage(), utilColor(), VLAN_STATUSES, QuickScanDialog(), useScanStream(), Dialog, DialogClose, DialogContent (+17 more)

### Community 5 - "Tree View & IP Drawer"
Cohesion: 0.07
Nodes (34): PrefixTreeNode(), ROLES, STATUSES, IpStatusBadge(), ipVariant, PrefixStatusBadge(), prefixVariant, ScanStatusBadge() (+26 more)

### Community 6 - "Frontend Dependencies"
Cohesion: 0.05
Nodes (37): dependencies, class-variance-authority, clsx, lucide-react, next, @radix-ui/react-dialog, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+29 more)

### Community 7 - "Network Scanner Worker"
Cohesion: 0.10
Nodes (25): _table(), vendor_for(), AsyncSession, reconcile(), _arp_scan(), detect_interface(), HostResult, _icmp_sweep() (+17 more)

### Community 8 - "Tags API"
Cohesion: 0.16
Nodes (23): assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession, delete (+15 more)

### Community 9 - "VLAN API"
Cohesion: 0.19
Nodes (25): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+17 more)

### Community 10 - "Scans & Discovery Pages"
Cohesion: 0.19
Nodes (15): ACTION_STYLES, ChangeSummary(), fmt(), fmtEta(), ScansPage(), COLORS, Table(), TableBody() (+7 more)

### Community 11 - "Login Setup Dashboard Pages"
Cohesion: 0.17
Nodes (16): Card, CardContent(), CardDescription(), CardFooter(), CardHeader(), CardTitle(), DialogOverlay, Input (+8 more)

### Community 12 - "IP Ranges API"
Cohesion: 0.14
Nodes (18): _check_range_overlap(), create_range(), delete_range(), list_ranges(), AsyncSession, delete, get, patch (+10 more)

### Community 13 - "Docker Deployment Stack"
Cohesion: 0.15
Nodes (19): api service (FastAPI backend), db service (postgres:16-alpine), redis service (redis:7-alpine), scanner service (ARQ worker), web service (Next.js frontend), alembic 1.14.0, arq 0.26.1, asyncpg 0.30.0 (+11 more)

### Community 14 - "Subnet Grid Components"
Cohesion: 0.16
Nodes (15): ChangelogPage(), DiscoveryPage(), DashboardPage(), AddressTable(), IpDrawer(), CellState, stateClass, SubnetGrid() (+7 more)

### Community 15 - "Prefix Detail & Tag Picker"
Cohesion: 0.19
Nodes (14): IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, TagChip(), TagPicker(), useTags(), Checkbox (+6 more)

### Community 16 - "TypeScript Config"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 17 - "Test Fixtures & Allocation"
Cohesion: 0.20
Nodes (15): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, session(), sf(), test_url() (+7 more)

### Community 18 - "App Shell & Layout"
Cohesion: 0.19
Nodes (9): metadata, AppShell(), AUTH_ROUTES, NAV, Button, ButtonProps, buttonVariants, TooltipProvider (+1 more)

### Community 19 - "IPAM Extras Tests"
Cohesion: 0.42
Nodes (9): _prefix(), test_address_role_nat_and_bulk(), test_container_move_with_children_rejected(), test_csv_export_import(), test_ip_ranges_exclude_allocator(), test_prefix_move_vrf(), test_tags_crud_and_assignment(), test_vlan_group_and_prefix_link() (+1 more)

### Community 20 - "Prefix API Tests"
Cohesion: 0.46
Nodes (7): _global_vrf_id(), test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_same_cidr_allowed_across_vrfs(), test_split_endpoint(), test_tree_endpoint(), test_unknown_vlan_rejected()

### Community 21 - "Changelog Tests"
Cohesion: 0.60
Nodes (4): AsyncClient, test_changelog_captures_ip_status_change(), test_changelog_records_crud(), test_changelog_scoped_filters()

### Community 22 - "Badge Component"
Cohesion: 0.67
Nodes (3): Badge(), BadgeProps, badgeVariants

## Knowledge Gaps
- **96 isolated node(s):** `WorkerSettings`, `nextConfig`, `name`, `version`, `private` (+91 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 206 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `IPAddress` connect `IP Address API` to `Scan API Endpoints`, `IP Ranges API`, `Network Scanner Worker`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Why does `IPAMError` connect `IP Address API` to `Scan API Endpoints`, `Sites Dashboard Changelog API`, `Tags API`, `VLAN API`, `IP Ranges API`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Why does `get_or_404()` connect `IP Address API` to `Scan API Endpoints`, `Sites Dashboard Changelog API`, `Tags API`, `VLAN API`, `IP Ranges API`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `IPAMError` (e.g. with `create_address()` and `delete_address()`) actually correct?**
  _`IPAMError` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `IPAddress` (e.g. with `bulk_addresses()` and `create_address()`) actually correct?**
  _`IPAddress` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `Prefix` (e.g. with `create_address()` and `import_addresses()`) actually correct?**
  _`Prefix` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `WorkerSettings`, `nextConfig`, `name` to the rest of the system?**
  _96 weakly-connected nodes found - possible documentation gaps or missing edges._