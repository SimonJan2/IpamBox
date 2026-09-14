# Graph Report - IpamBox  (2026-09-15)

## Corpus Check
- 162 files · ~174,808 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: (none) 7, .ini 2, .example 1)

## Summary
- 1232 nodes · 3255 edges · 93 communities (53 shown, 23 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 241 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Auth & Sessions
- IP Address API
- Runtime Settings
- Backup & Restore
- Settings & Users UI
- Prefix API
- Scanning & Address UI
- Entity Dialogs UI
- IP Range API
- VLAN API
- Frontend Types
- Dashboard & Auth UI
- RBAC Tests
- Network Scanner
- Tag API
- Backup Tests
- App Entry & Models
- Frontend Dependencies
- VRF API
- Prefix Detail UI
- UI Primitives
- Prefix Math
- Radix Dependencies
- Site API
- Scan VRF Inference
- Test Fixtures
- TypeScript Config
- Dashboard API
- Scan API
- IP Range Schemas
- Worker Scheduler
- Maintenance Tests
- Changelog & Tag UI
- Maintenance API
- Changelog Hooks
- Subnet Grid UI
- Docker Services
- Status Badges
- Changelog API
- IPAM Extras Tests
- Prefix API Tests
- Frontend Dev Dependencies
- Backup Settings UI
- ARQ Test Fixture
- User Tests
- Next.js Config
- Settings Overview Page
- Health Endpoints
- Prefix Tree
- Changelog Tests
- npm Scripts
- Alembic Env
- Button Component
- Test Dependencies
- Project Docs
- Pydantic Dependencies
- delete
- Request
- Any
- Base
- Exception
- Prefix
- fixture
- Root Layout (layout.tsx, title: IpamBox)
- IpamBox App Icon (icon.svg)
- alembic 1.14.0
- arq 0.26.1
- asyncpg 0.30.0
- bcrypt 4.3.0
- fastapi 0.115.6
- psutil 6.1.0
- redis (python client) 5.2.0
- scapy 2.6.1
- sqlalchemy[asyncio] 2.0.36
- uvicorn[standard] 0.32.1
- ScanJob

## God Nodes (most connected - your core abstractions)
1. `cn()` - 63 edges
2. `IPAMError` - 41 edges
3. `get_or_404()` - 39 edges
4. `IPAddress` - 37 edges
5. `react` - 35 edges
6. `User` - 33 edges
7. `useAuth()` - 33 edges
8. `Prefix` - 31 edges
9. `Base` - 26 edges
10. `lucide-react` - 23 edges

## Surprising Connections (you probably didn't know these)
- `run_scheduled_scans()` --calls--> `ScanJob`  [EXTRACTED]
  backend/app/worker/worker.py → frontend/src/types/index.ts
- `User` --uses--> `bulk_addresses()`  [INFERRED]
  backend/app/models/user.py → backend/app/api/v1/addresses.py
- `User` --uses--> `has_perm()`  [INFERRED]
  backend/app/models/user.py → backend/app/core/deps.py
- `User` --uses--> `factory_reset()`  [INFERRED]
  backend/app/models/user.py → backend/app/api/v1/maintenance.py
- `User` --uses--> `require_perm()`  [INFERRED]
  backend/app/models/user.py → backend/app/core/deps.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **IpamBox Container Service Stack** — docker_compose_service_db, docker_compose_service_redis, docker_compose_service_api, docker_compose_service_scanner, docker_compose_service_web [EXTRACTED 1.00]
- **IpamBox Container Service Stack** — docker_compose_service_db, docker_compose_service_redis, docker_compose_service_api, docker_compose_service_scanner, docker_compose_service_web [EXTRACTED 1.00]
- **Scanner Host-Network Access to Data Services** — docker_compose_service_scanner, docker_compose_service_db, docker_compose_service_redis [EXTRACTED 1.00]
- **Scanner Host-Network Access to Data Services** — docker_compose_service_scanner, docker_compose_service_db, docker_compose_service_redis [EXTRACTED 1.00]
- **Scheduled Backup Storage Sharing** — docker_compose_service_api, docker_compose_service_scanner, docker_compose_volume_backupdata [EXTRACTED 1.00]
- **Scheduled Backup Storage Sharing** — docker_compose_service_api, docker_compose_service_scanner, docker_compose_volume_backupdata [EXTRACTED 1.00]

## Communities (93 total, 23 thin omitted)

### Community 0 - "Auth & Sessions"
Cohesion: 0.05
Nodes (96): ArqRedis, AsyncSession, auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session() (+88 more)

### Community 1 - "IP Address API"
Cohesion: 0.07
Nodes (50): bulk_addresses(), BulkBody, create_address(), export_addresses(), get_address(), import_addresses(), ImportRow, list_addresses() (+42 more)

### Community 2 - "Runtime Settings"
Cohesion: 0.06
Nodes (49): _build_out(), _lan_info(), _mask_url(), AsyncSession, get, patch, read_settings(), update_settings() (+41 more)

### Community 3 - "Backup & Restore"
Cohesion: 0.10
Nodes (45): Any, delete_scheduled_backup(), download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, get, post (+37 more)

### Community 4 - "Settings & Users UI"
Cohesion: 0.08
Nodes (28): DiscoveryPage(), DataPage(), download(), UsersPage(), SitesPage(), TagsPage(), VlansPage(), VrfsPage() (+20 more)

### Community 5 - "Prefix API"
Cohesion: 0.12
Nodes (34): AllocateIPRequest, allocate_next_available(), create_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), prefix_tree() (+26 more)

### Community 6 - "Scanning & Address UI"
Cohesion: 0.08
Nodes (30): AppearancePage(), Key, ScanningPage(), fmtAgo(), SecurityPage(), AddressList(), AddrMapViewSwitcher(), buildRows() (+22 more)

### Community 7 - "Entity Dialogs UI"
Cohesion: 0.17
Nodes (18): VLAN_STATUSES, TAG_COLORS, Dialog, DialogClose, DialogContent, DialogDescription, DialogFooter(), DialogHeader() (+10 more)

### Community 8 - "IP Range API"
Cohesion: 0.13
Nodes (29): delete_address(), delete_prefix(), delete, _check_range_overlap(), create_range(), delete_range(), list_ranges(), AsyncSession (+21 more)

### Community 9 - "VLAN API"
Cohesion: 0.14
Nodes (30): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+22 more)

### Community 10 - "Frontend Types"
Cohesion: 0.06
Nodes (33): AddressPage, AuthStatus, BackupFileInfo, ChangeField, ChangeLogEntry, DashboardStats, IpAddress, IpRange (+25 more)

### Community 11 - "Dashboard & Auth UI"
Cohesion: 0.16
Nodes (17): DashboardPage(), fmtEta(), ScansPage(), QuickScanDialog(), useScanStream(), ScanStatusBadge(), Card, CardContent() (+9 more)

### Community 12 - "RBAC Tests"
Cohesion: 0.21
Nodes (24): AsyncClient, auth_on(), fake_arq(), login(), mkuser(), other_client(), AsyncSession, fixture (+16 more)

### Community 13 - "Network Scanner"
Cohesion: 0.11
Nodes (24): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), detect_interface(), detect_local_cidr(), HostResult, _icmp_sweep() (+16 more)

### Community 14 - "Tag API"
Cohesion: 0.14
Nodes (22): AssignBody, assign_tag(), create_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession, delete (+14 more)

### Community 15 - "Backup Tests"
Cohesion: 0.23
Nodes (26): _backup_bytes(), _envelope_bytes(), _mkusers(), User, _registry_names(), _restore(), _seed(), test_backup_include_users_excludes_admins() (+18 more)

### Community 16 - "App Entry & Models"
Cohesion: 0.22
Nodes (13): metrics(), Prometheus-style text exposition of object + scan counters., Base, IPRange, A named block of addresses inside a prefix (e.g. a DHCP scope). Any defined…, str, ScanJob, ScanStatus (+5 more)

### Community 17 - "Frontend Dependencies"
Cohesion: 0.08
Nodes (22): name, private, version, autoprefixer, clsx, postcss, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+14 more)

### Community 18 - "VRF API"
Cohesion: 0.17
Nodes (18): create_vrf(), delete_vrf(), get_vrf(), list_vrfs(), AsyncSession, delete, get, patch (+10 more)

### Community 19 - "Prefix Detail UI"
Cohesion: 0.16
Nodes (17): IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, toggleIn(), PrefixesPage(), utilColor(), TagChip() (+9 more)

### Community 20 - "UI Primitives"
Cohesion: 0.14
Nodes (20): PrefixTreeNode(), ROLES, STATUSES, CardDescription(), CardFooter(), DialogOverlay, Textarea, SelectContent (+12 more)

### Community 21 - "Prefix Math"
Cohesion: 0.20
Nodes (19): prefix_stats(), children(), lowest_free(), parent_chain(), Inclusive [first, last] integer range of host-usable addresses., True when network/broadcast addresses are unusable for hosts (IPv4 <= /30)., Lowest usable address integer not in `taken` or any excluded range., Split `net` into children of `new_prefix` length. (+11 more)

### Community 22 - "Radix Dependencies"
Cohesion: 0.10
Nodes (21): dependencies, class-variance-authority, clsx, lucide-react, next, @radix-ui/react-dialog, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+13 more)

### Community 23 - "Site API"
Cohesion: 0.19
Nodes (17): create_site(), delete_site(), get_site(), list_sites(), AsyncSession, delete, get, patch (+9 more)

### Community 24 - "Scan VRF Inference"
Cohesion: 0.19
Nodes (11): _global_vrf_id(), _infer_scan_vrf(), _scan_vrf(), _extra_vrf(), _global_id(), _mk_prefix(), test_infer_scan_vrf_ambiguous_prefix_falls_back_to_global(), test_infer_scan_vrf_covering_prefix() (+3 more)

### Community 25 - "Test Fixtures"
Cohesion: 0.19
Nodes (16): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Create the test database (if missing) and run migrations against it., session(), sf() (+8 more)

### Community 26 - "TypeScript Config"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 27 - "Dashboard API"
Cohesion: 0.15
Nodes (12): AsyncSession, get, stats(), lifespan(), DashboardStats, BaseModel, BaseModel, field_validator (+4 more)

### Community 28 - "Scan API"
Cohesion: 0.22
Nodes (15): cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession, get (+7 more)

### Community 29 - "IP Range Schemas"
Cohesion: 0.20
Nodes (10): IPRangeRole, str, ip_display(), Normalize asyncpg-returned ipaddress objects / strings to display form. INET…, IPRangeCreate, IPRangeOut, IPRangeUpdate, BaseModel (+2 more)

### Community 30 - "Worker Scheduler"
Cohesion: 0.22
Nodes (13): _due(), _eta_seconds(), _publish(), datetime, _resolve_prefix(), run_scan(), _cancelled(), progress() (+5 more)

### Community 31 - "Maintenance Tests"
Cohesion: 0.21
Nodes (11): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_now_enqueues(), test_clear_discovery() (+3 more)

### Community 32 - "Changelog & Tag UI"
Cohesion: 0.35
Nodes (10): ACTION_STYLES, ChangelogPage(), ChangeSummary(), fmt(), Table(), TableBody(), TableCell(), TableHead() (+2 more)

### Community 33 - "Maintenance API"
Cohesion: 0.41
Nodes (12): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+4 more)

### Community 34 - "Changelog Hooks"
Cohesion: 0.31
Nodes (11): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), Audit trail via session flush hooks. before_flush collects (object, action,…, register(), _repr() (+3 more)

### Community 35 - "Subnet Grid UI"
Cohesion: 0.22
Nodes (10): CellState, stateClass, SubnetGrid(), Tooltip, TooltipContent, TooltipTrigger, intToIp(), ipToInt() (+2 more)

### Community 36 - "Docker Services"
Cohesion: 0.27
Nodes (12): CORS_ORIGINS env var, DATABASE_URL env var, NEXT_PUBLIC_API_URL env var, REDIS_URL env var, api service (FastAPI backend), db service (postgres:16-alpine), redis service (redis:7-alpine), scanner service (ARQ worker) (+4 more)

### Community 37 - "Status Badges"
Cohesion: 0.22
Nodes (9): IpStatusBadge(), ipVariant, PrefixStatusBadge(), prefixVariant, scanVariant, Badge(), BadgeProps, badgeVariants (+1 more)

### Community 38 - "Changelog API"
Cohesion: 0.27
Nodes (8): list_changelog(), AsyncSession, get, ChangeLog, NetBox-style audit trail: who changed what, when, and the field diff., ChangeField, ChangeLogOut, BaseModel

### Community 39 - "IPAM Extras Tests"
Cohesion: 0.42
Nodes (9): _prefix(), test_address_role_nat_and_bulk(), test_container_move_with_children_rejected(), test_csv_export_import(), test_ip_ranges_exclude_allocator(), test_prefix_move_vrf(), test_tags_crud_and_assignment(), test_vlan_group_and_prefix_link() (+1 more)

### Community 40 - "Prefix API Tests"
Cohesion: 0.46
Nodes (7): _global_vrf_id(), test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_same_cidr_allowed_across_vrfs(), test_split_endpoint(), test_tree_endpoint(), test_unknown_vlan_rejected()

### Community 41 - "Frontend Dev Dependencies"
Cohesion: 0.25
Nodes (8): devDependencies, autoprefixer, postcss, tailwindcss, @types/node, @types/react, @types/react-dom, typescript

### Community 42 - "Backup Settings UI"
Cohesion: 0.32
Nodes (7): BackupSettingsPage(), downloadUrl(), fmtSize(), BackupFilesOut, BackupPreview, RestoreReport, SettingsOut

### Community 43 - "ARQ Test Fixture"
Cohesion: 0.29
Nodes (5): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture

### Community 44 - "User Tests"
Cohesion: 0.38
Nodes (6): auth_on(), AsyncClient, fixture, test_change_password_and_sessions(), test_revoke_session_endpoint(), test_users_crud_and_guards()

### Community 45 - "Next.js Config"
Cohesion: 0.29
Nodes (4): nextConfig, metadata, TooltipProvider, next

### Community 46 - "Settings Overview Page"
Cohesion: 0.53
Nodes (4): downloadUrl(), fmtSize(), fmtTs(), SettingsPage()

### Community 47 - "Health Endpoints"
Cohesion: 0.40
Nodes (5): healthz(), get, Readiness probe: verifies DB + Redis connectivity., readyz(), JSONResponse

### Community 48 - "Prefix Tree"
Cohesion: 0.70
Nodes (5): build_tree(), prefix_node(), site_node(), vrf_node(), Site -> VRF -> nested prefix containment tree.

### Community 49 - "Changelog Tests"
Cohesion: 0.60
Nodes (4): AsyncClient, test_changelog_captures_ip_status_change(), test_changelog_records_crud(), test_changelog_scoped_filters()

### Community 50 - "npm Scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 52 - "Button Component"
Cohesion: 0.67
Nodes (3): Button, ButtonProps, buttonVariants

### Community 63 - "Test Dependencies"
Cohesion: 0.67
Nodes (3): httpx 0.28.1, pytest 8.3.4, pytest-asyncio 0.25.0

## Knowledge Gaps
- **158 isolated node(s):** `AddressPage`, `AuthStatus`, `BackupFileInfo`, `ChangeField`, `ChangeLogEntry` (+153 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 373 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `Auth & Sessions` to `App Entry & Models`, `IP Address API`, `Backup & Restore`, `Maintenance API`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Why does `IPAddress` connect `IP Address API` to `Changelog Hooks`, `Prefix API`, `IP Range API`, `Network Scanner`, `App Entry & Models`, `Prefix Math`, `Dashboard API`, `IP Range Schemas`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Are the 29 inferred relationships involving `IPAMError` (e.g. with `create_address()` and `get_address()`) actually correct?**
  _`IPAMError` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `IPAddress` (e.g. with `bulk_addresses()` and `list_addresses()`) actually correct?**
  _`IPAddress` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `AddressPage`, `AuthStatus`, `BackupFileInfo` to the rest of the system?**
  _158 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Auth & Sessions` be split into smaller, more focused modules?**
  _Cohesion score 0.052743652743652746 - nodes in this community are weakly interconnected._
- **Should `IP Address API` be split into smaller, more focused modules?**
  _Cohesion score 0.07486338797814207 - nodes in this community are weakly interconnected._