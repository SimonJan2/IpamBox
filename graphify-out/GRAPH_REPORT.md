# Graph Report - IpamBox  (2026-09-13)

## Corpus Check
- 132 files · ~158,183 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: (none) 7, .ini 2, .example 1)

## Summary
- 952 nodes · 2701 edges · 57 communities (38 shown, 5 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 250 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Auth & Sessions API
- Ranges & Changelog API
- IPAM CRUD Pages
- Backup & Restore API
- Tags API
- Prefixes API
- IPAM UI Pages
- Discovery API
- Sites API
- VLANs API
- UI Filters & Badges
- Compose Services & Volumes
- Scanner & OUI Lookup
- Shell & Auth Pages
- Worker & Redis Scheduling
- Addresses API
- Scans API
- Frontend Dependencies
- UI Primitives
- Radix & Style Deps
- Subnet Math Service
- Test Harness
- TS Config
- Table Pages
- README Docs
- Scanner Tests & Typing
- Backup Tests
- API Core & Changelog
- App Layout & Config
- Dashboard & Tree Service
- Dashboard & Scan Schemas
- IPAM Extras Tests
- App Shell & Nav
- Prefix API Tests
- Frontend DevDeps
- Settings & Backup UI
- Changelog Tests
- NPM Scripts
- Prefix Schemas
- App Icon
- Tailwind Config
- Scan Interval Env
- bcrypt Dep

## God Nodes (most connected - your core abstractions)
1. `cn()` - 63 edges
2. `IPAMError` - 43 edges
3. `get_or_404()` - 41 edges
4. `IPAddress` - 39 edges
5. `react` - 35 edges
6. `Prefix` - 33 edges
7. `Base` - 26 edges
8. `VRF` - 24 edges
9. `get_settings()` - 23 edges
10. `lucide-react` - 23 edges

## Surprising Connections (you probably didn't know these)
- `api service (FastAPI backend)` --references--> `alembic 1.14.0`  [INFERRED]
  docker-compose.yml → backend/requirements.txt
- `api service (FastAPI backend)` --implements--> `fastapi 0.115.6`  [INFERRED]
  docker-compose.yml → backend/requirements.txt
- `api service (FastAPI backend)` --implements--> `pydantic 2.10.3`  [INFERRED]
  docker-compose.yml → backend/requirements.txt
- `api service (FastAPI backend)` --implements--> `sqlalchemy[asyncio] 2.0.36`  [INFERRED]
  docker-compose.yml → backend/requirements.txt
- `api service (FastAPI backend)` --references--> `uvicorn[standard] 0.32.1`  [INFERRED]
  docker-compose.yml → backend/requirements.txt

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Scheduled backup pipeline (worker -> backupdata volume -> API -> UI)** — compose_scanner, docker_compose_backupdata, docker_compose_backup_dir, docker_compose_backup_interval, docker_compose_backup_keep, compose_api [INFERRED 0.95]
- **Backup & Restore end-to-end surface (API + Settings UI)** — compose_api, compose_web [INFERRED 0.85]

## Communities (57 total, 5 thin omitted)

### Community 0 - "Auth & Sessions API"
Cohesion: 0.07
Nodes (60): auth_status(), _current_user(), ensure_env_password_user(), login(), logout(), me(), AsyncSession, get (+52 more)

### Community 1 - "Ranges & Changelog API"
Cohesion: 0.07
Nodes (43): do_run_migrations(), run_migrations_online(), list_changelog(), AsyncSession, get, _check_range_overlap(), create_range(), delete_range() (+35 more)

### Community 2 - "IPAM CRUD Pages"
Cohesion: 0.10
Nodes (32): VLAN_STATUSES, ROLES, STATUSES, QuickScanDialog(), useScanStream(), PrefixStatusBadge(), TAG_COLORS, Dialog (+24 more)

### Community 3 - "Backup & Restore API"
Cohesion: 0.09
Nodes (42): Any, download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, restore(), BackupFileInfo, BackupFilesOut (+34 more)

### Community 4 - "Tags API"
Cohesion: 0.09
Nodes (37): assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession, delete (+29 more)

### Community 5 - "Prefixes API"
Cohesion: 0.15
Nodes (36): allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), prefix_tree() (+28 more)

### Community 6 - "IPAM UI Pages"
Cohesion: 0.10
Nodes (30): ChangelogPage(), DiscoveryPage(), DashboardPage(), AddressTable(), IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES (+22 more)

### Community 7 - "Discovery API"
Cohesion: 0.12
Nodes (26): confirm_discovered(), ConfirmBody, list_discovered(), AsyncSession, BaseModel, get, post, Unconfirmed hosts found by scanners, pending admin review. (+18 more)

### Community 8 - "Sites API"
Cohesion: 0.15
Nodes (24): create_site(), delete_site(), get_site(), list_sites(), AsyncSession, delete, get, patch (+16 more)

### Community 9 - "VLANs API"
Cohesion: 0.18
Nodes (26): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+18 more)

### Community 10 - "UI Filters & Badges"
Cohesion: 0.08
Nodes (27): AddressFilterPanel(), STATUS_DOT, STATUSES, IpStatusBadge(), ipVariant, prefixVariant, ScanStatusBadge(), scanVariant (+19 more)

### Community 11 - "Compose Services & Volumes"
Cohesion: 0.11
Nodes (26): api service (FastAPI backend), db service (postgres:16-alpine), redis service (redis:7-alpine), scanner service (ARQ worker), web service (Next.js frontend), alembic upgrade head on api start, BACKUP_DIR env (default /backups), BACKUP_INTERVAL_MINUTES env (default 0) (+18 more)

### Community 12 - "Scanner & OUI Lookup"
Cohesion: 0.13
Nodes (21): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), detect_interface(), HostResult, _icmp_sweep(), _ptr_lookup() (+13 more)

### Community 13 - "Shell & Auth Pages"
Cohesion: 0.22
Nodes (11): Card, CardContent(), CardHeader(), CardTitle(), Checkbox, CheckboxProps, api, AUTH_PAGES (+3 more)

### Community 14 - "Worker & Redis Scheduling"
Cohesion: 0.14
Nodes (21): ArqRedis, get_arq_pool(), redis_settings_from_url(), VRF, detect_local_cidr(), CIDR of the default-route interface, e.g. '192.168.1.0/24'., cancel_key(), _cron_jobs() (+13 more)

### Community 15 - "Addresses API"
Cohesion: 0.16
Nodes (21): bulk_addresses(), BulkBody, create_address(), delete_address(), export_addresses(), get_address(), import_addresses(), ImportRow (+13 more)

### Community 16 - "Scans API"
Cohesion: 0.17
Nodes (21): cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession, get (+13 more)

### Community 17 - "Frontend Dependencies"
Cohesion: 0.09
Nodes (21): name, private, version, autoprefixer, clsx, postcss, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+13 more)

### Community 18 - "UI Primitives"
Cohesion: 0.13
Nodes (19): PrefixTreeNode(), Badge(), BadgeProps, badgeVariants, CardDescription(), CardFooter(), Separator, Skeleton() (+11 more)

### Community 19 - "Radix & Style Deps"
Cohesion: 0.10
Nodes (21): dependencies, class-variance-authority, clsx, lucide-react, next, @radix-ui/react-dialog, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+13 more)

### Community 20 - "Subnet Math Service"
Cohesion: 0.19
Nodes (17): children(), lowest_free(), parent_chain(), Inclusive [first, last] integer range of host-usable addresses., True when network/broadcast addresses are unusable for hosts (IPv4 <= /30)., Lowest usable address integer not in `taken` or any excluded range., Split `net` into children of `new_prefix` length., The smallest candidate network that strictly contains `net`. (+9 more)

### Community 21 - "Test Harness"
Cohesion: 0.19
Nodes (16): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Create the test database (if missing) and run migrations against it., session(), sf() (+8 more)

### Community 22 - "TS Config"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 23 - "Table Pages"
Cohesion: 0.27
Nodes (12): ACTION_STYLES, ChangeSummary(), fmt(), fmtEta(), ScansPage(), Table(), TableBody(), TableCell() (+4 more)

### Community 24 - "README Docs"
Cohesion: 0.12
Nodes (16): Architecture, Configuration, Development, Features, IPAM, IpamBox, License, Operations (+8 more)

### Community 25 - "Scanner Tests & Typing"
Cohesion: 0.15
Nodes (10): infer_device_type(), Best-effort device classification; None when nothing matched., fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture, Stands in for the arq Redis pool — never actually dispatches work. (+2 more)

### Community 26 - "Backup Tests"
Cohesion: 0.36
Nodes (14): _backup_bytes(), _registry_names(), _restore(), _seed(), test_backup_roundtrip(), test_dry_run_does_not_write(), test_registry_covers_all_tables(), test_restore_preserves_users() (+6 more)

### Community 27 - "API Core & Changelog"
Cohesion: 0.27
Nodes (6): get_session(), AsyncSession, ChangeField, ChangeLogOut, BaseModel, FastAPI

### Community 28 - "App Layout & Config"
Cohesion: 0.18
Nodes (8): nextConfig, metadata, Tooltip, TooltipContent, TooltipProvider, TooltipTrigger, next, @radix-ui/react-tooltip

### Community 29 - "Dashboard & Tree Service"
Cohesion: 0.27
Nodes (10): AsyncSession, get, stats(), build_tree(), prefix_node(), site_node(), vrf_node(), dashboard_stats() (+2 more)

### Community 30 - "Dashboard & Scan Schemas"
Cohesion: 0.29
Nodes (7): DashboardStats, BaseModel, BaseModel, field_validator, ScanConfigOut, ScanCreate, ScanJobOut

### Community 31 - "IPAM Extras Tests"
Cohesion: 0.42
Nodes (9): _prefix(), test_address_role_nat_and_bulk(), test_container_move_with_children_rejected(), test_csv_export_import(), test_ip_ranges_exclude_allocator(), test_prefix_move_vrf(), test_tags_crud_and_assignment(), test_vlan_group_and_prefix_link() (+1 more)

### Community 32 - "App Shell & Nav"
Cohesion: 0.28
Nodes (7): AppShell(), AUTH_ROUTES, NAV, Button, ButtonProps, buttonVariants, AuthStatus

### Community 33 - "Prefix API Tests"
Cohesion: 0.46
Nodes (7): _global_vrf_id(), test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_same_cidr_allowed_across_vrfs(), test_split_endpoint(), test_tree_endpoint(), test_unknown_vlan_rejected()

### Community 34 - "Frontend DevDeps"
Cohesion: 0.25
Nodes (8): devDependencies, autoprefixer, postcss, tailwindcss, @types/node, @types/react, @types/react-dom, typescript

### Community 35 - "Settings & Backup UI"
Cohesion: 0.36
Nodes (7): downloadUrl(), fmtSize(), fmtTs(), SettingsPage(), BackupFilesOut, BackupPreview, RestoreReport

### Community 36 - "Changelog Tests"
Cohesion: 0.60
Nodes (4): AsyncClient, test_changelog_captures_ip_status_change(), test_changelog_records_crud(), test_changelog_scoped_filters()

### Community 37 - "NPM Scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

## Knowledge Gaps
- **125 isolated node(s):** `CheckboxProps`, `CellState`, `ButtonProps`, `WorkerSettings`, `BadgeProps` (+120 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 281 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_resolve_prefix()` connect `Prefixes API` to `Shell & Auth Pages`, `Worker & Redis Scheduling`?**
  _High betweenness centrality (0.340) - this node is a cross-community bridge._
- **Why does `Prefix` connect `Shell & Auth Pages` to `IPAM CRUD Pages`, `UI Filters & Badges`, `Prefixes API`, `IPAM UI Pages`?**
  _High betweenness centrality (0.338) - this node is a cross-community bridge._
- **Why does `Prefix` connect `Prefixes API` to `Auth & Sessions API`, `Ranges & Changelog API`, `Sites API`, `Worker & Redis Scheduling`, `Addresses API`, `Dashboard & Tree Service`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `IPAMError` (e.g. with `create_address()` and `delete_address()`) actually correct?**
  _`IPAMError` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `IPAddress` (e.g. with `bulk_addresses()` and `create_address()`) actually correct?**
  _`IPAddress` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `CheckboxProps`, `CellState`, `ButtonProps` to the rest of the system?**
  _125 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Auth & Sessions API` be split into smaller, more focused modules?**
  _Cohesion score 0.06702702702702702 - nodes in this community are weakly interconnected._