# Graph Report - IpamBox  (2026-09-18)

## Corpus Check
- 191 files · ~200,529 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: (none) 7, .ini 2, .example 1)

## Summary
- 1626 nodes · 4690 edges · 102 communities (71 shown, 14 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 367 edges (avg confidence: 0.94)
- Token cost: 1,600 input · 3,400 output

## Community Hubs (Navigation)
- User Management API
- IPAM Entity Pages
- Ops & Audit Pages
- Import Wizard Frontend
- IP Address API
- Settings & Filter Components
- Auth & Dashboard Pages
- Workbook Import API
- Prefix Management API
- Core Models & App Entry
- Authentication API
- Runtime Settings & Config
- IP Ranges API
- Import Plan Builder
- Scanner & Reconciliation
- Scanner VRF & Tests
- Tags API
- Entity Dialogs & UI
- API Routing & Deps
- Import Commit & Seeding
- Scan Jobs API
- VLAN API
- Config & Auth Setup
- Backup Restore Logic
- Maintenance API
- IP Drawer & Badges
- Entity CRUD & Schemas
- Workbook Sheet Parsers
- Scan Worker & ARQ
- Sites & CRUD Router
- Session Security
- Package Meta & Radix
- Prefs & Admin Pages
- IPAM Tree & Stats
- Settings API
- Prefix Math
- Cell Normalizers
- NPM Dependencies
- App Shell & Auth Context
- ScanJob Model & Metrics
- TypeScript Config
- Backup API
- VRF API
- Sites Master Parsing
- README Documentation
- Plan Site Resolution Tests
- Core Python Stack
- Settings Tests
- Backup File Ops
- Changelog Audit Hooks
- Test Fixtures
- Import E2E Tests
- Site Sheet Parser Tests
- Discovery Inbox
- IPAM Extras Tests
- Normalizer Tests
- Scanner Stack
- Circuit Schemas
- Next.js App Setup
- Sheet Classify Tests
- Prefix API Tests
- Database & Cache Infra
- Dev Dependencies
- Compose Services
- Allocation Tests
- Prefixes Page
- Auth Guards
- Entity CRUD Tests
- VLANs Page
- Security Docs
- Health Probes
- Changelog Tests
- Backup Docs
- NPM Scripts
- Circuits Page
- Inventory Page
- Services Page
- README Feature Sections
- Inflight Scan Failover
- Next Env Types
- Tailwind Config
- Top-Level Docs
- AsyncSession Symbol
- App Icon
- Root Layout

## God Nodes (most connected - your core abstractions)
1. `cn()` - 72 edges
2. `User` - 57 edges
3. `get_or_404()` - 52 edges
4. `IPAMError` - 51 edges
5. `IPAddress` - 49 edges
6. `react` - 45 edges
7. `Base` - 43 edges
8. `_matrix()` - 38 edges
9. `UserRole` - 37 edges
10. `get_settings()` - 34 edges

## Surprising Connections (you probably didn't know these)
- `pydantic-settings==2.6.1` --semantically_similar_to--> `Hybrid settings model (.env defaults + runtime overrides in app_settings)`  [INFERRED] [semantically similar]
  backend/requirements.txt → README.md
- `httpx==0.28.1` --references--> `api service (FastAPI backend, alembic+uvicorn entrypoint)`  [INFERRED]
  backend/requirements.txt → docker-compose.yml
- `pytest-asyncio==0.25.0` --references--> `api service (FastAPI backend, alembic+uvicorn entrypoint)`  [INFERRED]
  backend/requirements.txt → docker-compose.yml
- `api service (FastAPI backend, alembic+uvicorn entrypoint)` --references--> `Excel workbook import wizard (detect, dry-run, commit)`  [INFERRED]
  docker-compose.yml → README.md
- `Hybrid settings model (.env defaults + runtime overrides in app_settings)` --references--> `scanner service (ARQ worker, network_mode: host, NET_ADMIN/NET_RAW)`  [INFERRED]
  README.md → docker-compose.yml

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Shared Backup Subsystem** — ipambox_docker_compose_api_service, ipambox_docker_compose_scanner_service, ipambox_docker_compose_backupdata_volume [EXTRACTED 1.00]
- **Healthcheck-Gated Startup Ordering** — ipambox_docker_compose_db_service, ipambox_docker_compose_redis_service, ipambox_docker_compose_api_service, ipambox_docker_compose_scanner_service, ipambox_docker_compose_web_service [EXTRACTED 1.00]
- **Single Backend Image, Two Runtimes (api + scanner)** — ipambox_docker_compose_api_service, ipambox_docker_compose_scanner_service [EXTRACTED 1.00]

## Communities (102 total, 14 thin omitted)

### Community 0 - "User Management API"
Cohesion: 0.08
Nodes (72): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+64 more)

### Community 1 - "IPAM Entity Pages"
Cohesion: 0.10
Nodes (39): ChangelogPage(), DiscoveryPage(), ImportPage(), IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, toggleIn() (+31 more)

### Community 2 - "Ops & Audit Pages"
Cohesion: 0.13
Nodes (31): CertificatesPage(), EMPTY, expiryBadge(), ACTION_STYLES, ChangeSummary(), fmt(), fmtEta(), ScansPage() (+23 more)

### Community 3 - "Import Wizard Frontend"
Cohesion: 0.06
Nodes (38): ACTION_STYLE, CommitResp, Counts, FAMILY_LABEL, PreviewResp, UploadResp, Asset, AssetKind (+30 more)

### Community 4 - "IP Address API"
Cohesion: 0.12
Nodes (33): bulk_addresses(), BulkBody, create_address(), delete_address(), export_addresses(), get_address(), import_addresses(), ImportRow (+25 more)

### Community 5 - "Settings & Filter Components"
Cohesion: 0.12
Nodes (27): DataPage(), download(), Key, AddressFilterPanel(), STATUS_DOT, STATUSES, CidrListEditor(), ConfirmAction() (+19 more)

### Community 6 - "Auth & Dashboard Pages"
Cohesion: 0.11
Nodes (24): ACTION_STYLES, DashboardPage(), downloadUrl(), fmtSize(), fmtTs(), SettingsPage(), PrefixTreeNode(), expiryBadge() (+16 more)

### Community 7 - "Workbook Import API"
Cohesion: 0.10
Nodes (32): delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession, delete (+24 more)

### Community 8 - "Prefix Management API"
Cohesion: 0.14
Nodes (35): allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), prefix_tree() (+27 more)

### Community 9 - "Core Models & App Entry"
Cohesion: 0.17
Nodes (15): AppSetting, Runtime-editable setting override. Absent row -> env var -> default., Base, ImportBatch, ImportBatchStatus, str, One uploaded workbook (or file) import run. `stats` holds the preview result:…, IPRange (+7 more)

### Community 10 - "Authentication API"
Cohesion: 0.17
Nodes (31): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+23 more)

### Community 11 - "Runtime Settings & Config"
Cohesion: 0.09
Nodes (24): psycopg2-style URL for alembic offline mode / scripts., Settings, Effective, _env_sourced(), get_effective(), patch(), Any, AsyncSession (+16 more)

### Community 12 - "IP Ranges API"
Cohesion: 0.10
Nodes (22): _check_range_overlap(), create_range(), delete_range(), list_ranges(), AsyncSession, delete, get, post (+14 more)

### Community 13 - "Import Plan Builder"
Cohesion: 0.18
Nodes (4): _Planner, _site_key(), Counter, Site

### Community 14 - "Scanner & Reconciliation"
Cohesion: 0.11
Nodes (25): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), _arp_scan(), HostResult (+17 more)

### Community 15 - "Scanner VRF & Tests"
Cohesion: 0.11
Nodes (23): infer_device_type(), Best-effort device classification; None when nothing matched., _global_vrf_id(), _infer_scan_vrf(), Pick the VRF for a scan that didn't specify one. An exact-match prefix living…, _scan_vrf(), _extra_vrf(), fake_arq() (+15 more)

### Community 16 - "Tags API"
Cohesion: 0.15
Nodes (22): assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession, delete (+14 more)

### Community 17 - "Entity Dialogs & UI"
Cohesion: 0.17
Nodes (18): QuickScanDialog(), useScanStream(), Dialog, DialogClose, DialogContent, DialogDescription, DialogFooter(), DialogHeader() (+10 more)

### Community 18 - "API Routing & Deps"
Cohesion: 0.13
Nodes (16): list_changelog(), AsyncSession, get, get_session(), AsyncSession, Dependency factory: 403 unless the caller's role grants `perm`. Stacks on top…, require_perm(), lifespan() (+8 more)

### Community 19 - "Import Commit & Seeding"
Cohesion: 0.12
Nodes (19): commit_import(), Certificate, Certificate-expiry row from the תוקף תעודות sheet., Circuit, WAN circuit row from the קוי-SDH-IPVPN sheet (Bezeq IPVPN/SDH/Metro…)., VRF, Seed sample data: a Site, the Global VRF, and the auto-detected LAN prefix. Run…, commit_batch() (+11 more)

### Community 20 - "Scan Jobs API"
Cohesion: 0.13
Nodes (23): cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession, get (+15 more)

### Community 21 - "VLAN API"
Cohesion: 0.19
Nodes (24): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+16 more)

### Community 22 - "Config & Auth Setup"
Cohesion: 0.12
Nodes (19): do_run_migrations(), run_migrations_online(), get_settings(), env_password(), Password provisioned via IPAMBOX_PASSWORD_FILE / IPAMBOX_PASSWORD., Password provisioned via IPAMBOX_PASSWORD_FILE / IPAMBOX_PASSWORD., auth_on(), AsyncClient (+11 more)

### Community 23 - "Backup Restore Logic"
Cohesion: 0.11
Nodes (25): post, Request, Restore a backup file (raw .json.gz body). Wipes every data table (users are…, restore(), _alembic_revisions(), BackupError, BackupPreview, build_backup() (+17 more)

### Community 24 - "Maintenance API"
Cohesion: 0.16
Nodes (24): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+16 more)

### Community 25 - "IP Drawer & Badges"
Cohesion: 0.11
Nodes (21): ROLES, STATUSES, IpStatusBadge(), ipVariant, PrefixStatusBadge(), prefixVariant, ScanStatusBadge(), scanVariant (+13 more)

### Community 26 - "Entity CRUD & Schemas"
Cohesion: 0.17
Nodes (17): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, Asset, AssetKind, str, SW/HW catalog rows (תוכנות וחומרות) and serial-number inventory…, AssetCreate, AssetOut, AssetUpdate (+9 more)

### Community 27 - "Workbook Sheet Parsers"
Cohesion: 0.13
Nodes (13): _has(), _looks_like_header(), norm_header(), _blocks(), _col_class(), _is_header_echo(), _leftover_bits(), _map_columns() (+5 more)

### Community 28 - "Scan Worker & ARQ"
Cohesion: 0.15
Nodes (21): ArqRedis, get_arq_pool(), redis_settings_from_url(), detect_interface(), detect_local_cidr(), CIDR of the default-route interface, e.g. '192.168.1.0/24'., _due(), _eta_seconds() (+13 more)

### Community 29 - "Sites & CRUD Router"
Cohesion: 0.17
Nodes (18): _crud_router(), delete_item(), get_item(), update_item(), create_site(), delete_site(), get_site(), list_sites() (+10 more)

### Community 30 - "Session Security"
Cohesion: 0.17
Nodes (21): get_redis(), clear_login_failures(), destroy_other_sessions(), destroy_session(), destroy_session_by_suffix(), _fails_key(), get_session_user_id(), is_locked_out() (+13 more)

### Community 31 - "Package Meta & Radix"
Cohesion: 0.09
Nodes (21): name, private, version, autoprefixer, clsx, postcss, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+13 more)

### Community 32 - "Prefs & Admin Pages"
Cohesion: 0.15
Nodes (16): AppearancePage(), SitesPage(), TagsPage(), AddrMapView, applyPrefs(), DEFAULT_PREFS, DensityChoice, fmtTs() (+8 more)

### Community 33 - "IPAM Tree & Stats"
Cohesion: 0.16
Nodes (20): AsyncSession, AsyncSession, get, stats(), build_tree(), prefix_node(), site_node(), vrf_node() (+12 more)

### Community 34 - "Settings API"
Cohesion: 0.15
Nodes (20): _build_out(), _lan_info(), _mask_url(), AsyncSession, get, Hide the password in a scheme://user:pass@host URL., LAN identity detected by the host-networked worker (written to Redis). Falls…, read_settings() (+12 more)

### Community 35 - "Prefix Math"
Cohesion: 0.20
Nodes (19): prefix_stats(), children(), lowest_free(), parent_chain(), Inclusive [first, last] integer range of host-usable addresses., True when network/broadcast addresses are unusable for hosts (IPv4 <= /30)., Lowest usable address integer not in `taken` or any excluded range., Split `net` into children of `new_prefix` length. (+11 more)

### Community 36 - "Cell Normalizers"
Cohesion: 0.21
Nodes (18): assemble_ip(), clean(), _clean_octets(), excel_date(), fold_hebrew(), map_status(), mask_to_prefixlen(), network_of() (+10 more)

### Community 37 - "NPM Dependencies"
Cohesion: 0.10
Nodes (21): dependencies, class-variance-authority, clsx, lucide-react, next, @radix-ui/react-dialog, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+13 more)

### Community 38 - "App Shell & Auth Context"
Cohesion: 0.16
Nodes (15): AppShell(), AUTH_ROUTES, NAV, SETTINGS_SECTIONS, SettingsNav(), AuthContext, AuthCtx, authCtxValue() (+7 more)

### Community 39 - "ScanJob Model & Metrics"
Cohesion: 0.17
Nodes (16): metrics(), Prometheus-style text exposition of object + scan counters., str, ScanJob, ScanStatus, Site, fake_arq(), _pool() (+8 more)

### Community 40 - "TypeScript Config"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 41 - "Backup API"
Cohesion: 0.20
Nodes (16): download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, get, Download a full snapshot (every table except users) as .json.gz.…, Scheduled snapshot files written by the worker into BACKUP_DIR., has_perm() (+8 more)

### Community 42 - "VRF API"
Cohesion: 0.20
Nodes (14): create_vrf(), delete_vrf(), get_vrf(), list_vrfs(), AsyncSession, delete, get, post (+6 more)

### Community 43 - "Sites Master Parsing"
Cohesion: 0.16
Nodes (9): _master_blocks(), parse_sites_master(), build_import_plan(), DbState, load_state(), parse_sites_master_records(), _preview(), _vrf_name_for() (+1 more)

### Community 44 - "README Documentation"
Cohesion: 0.12
Nodes (18): bcrypt==4.3.0, Architecture, Configuration, Development, Extended entities (WAN circuits, certificates, inventory, service catalog), First-run auth, session cookies, bcrypt hashing, IP lockout, Hebrew data support (final-letter folding, RTL rendering), IpamBox (+10 more)

### Community 45 - "Plan Site Resolution Tests"
Cohesion: 0.37
Nodes (6): _master_row(), _matrix(), _plan(), _preview_of(), _site_key_by_name(), TestPlanSiteResolution

### Community 46 - "Core Python Stack"
Cohesion: 0.15
Nodes (16): alembic==1.14.0, fastapi==0.115.6, httpx==0.28.1, openpyxl==3.1.5, pydantic==2.10.3, pydantic-settings==2.6.1, pytest==8.3.4, pytest-asyncio==0.25.0 (+8 more)

### Community 47 - "Settings Tests"
Cohesion: 0.19
Nodes (13): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_files_report_effective_schedule(), test_internal_keys_hidden() (+5 more)

### Community 48 - "Backup File Ops"
Cohesion: 0.20
Nodes (15): delete_scheduled_backup(), delete, backup_dir(), delete_backup_file(), list_backup_files(), prune_backups(), Path, Fetch a scheduled backup by file name (path-traversal safe). (+7 more)

### Community 49 - "Changelog Audit Hooks"
Cohesion: 0.27
Nodes (13): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), Audit trail via session flush hooks. before_flush collects (object, action,…, register(), _repr() (+5 more)

### Community 50 - "Test Fixtures"
Cohesion: 0.26
Nodes (12): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., session() (+4 more)

### Community 51 - "Import E2E Tests"
Cohesion: 0.21
Nodes (7): parse_servers(), test_commit_twice_rejected(), test_import_e2e(), TestAssetsParser, TestCertificatesParser, TestServersParser, _xlsx_bytes()

### Community 52 - "Site Sheet Parser Tests"
Cohesion: 0.27
Nodes (3): parse_site_sheet(), TestSiteSheetExtras, TestSiteSheetParser

### Community 53 - "Discovery Inbox"
Cohesion: 0.18
Nodes (11): confirm_discovered(), ConfirmBody, list_discovered(), AsyncSession, BaseModel, get, post, Unconfirmed hosts found by scanners, pending admin review. (+3 more)

### Community 54 - "IPAM Extras Tests"
Cohesion: 0.40
Nodes (10): _prefix(), test_address_role_nat_and_bulk(), test_container_move_with_children_rejected(), test_csv_export_import(), test_dashboard_attention_fields(), test_ip_ranges_exclude_allocator(), test_prefix_move_vrf(), test_tags_crud_and_assignment() (+2 more)

### Community 56 - "Scanner Stack"
Cohesion: 0.24
Nodes (10): arq==0.26.1, asyncpg==0.30.0, psutil==6.1.0, redis==5.2.0 (Python client), scapy==2.6.1, sqlalchemy[asyncio]==2.0.36, scanner service (ARQ worker, network_mode: host, NET_ADMIN/NET_RAW), Discovery Inbox and drift reconciliation (+2 more)

### Community 57 - "Circuit Schemas"
Cohesion: 0.36
Nodes (5): CircuitCreate, CircuitOut, CircuitUpdate, BaseModel, field_validator

### Community 58 - "Next.js App Setup"
Cohesion: 0.25
Nodes (5): nextConfig, metadata, PrefsInit(), TooltipProvider, next

### Community 60 - "Prefix API Tests"
Cohesion: 0.46
Nodes (7): _global_vrf_id(), test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_same_cidr_allowed_across_vrfs(), test_split_endpoint(), test_tree_endpoint(), test_unknown_vlan_rejected()

### Community 61 - "Database & Cache Infra"
Cohesion: 0.32
Nodes (8): db service (postgres:16-alpine), pgdata volume, redis service (redis:7-alpine, appendonly), redisdata volume, Atomic next-available-IP allocation (SELECT FOR UPDATE + UNIQUE), PostgreSQL GiST exclusion constraint for CIDR overlap safety, Site -> VRF -> Prefix -> IP address hierarchy, Loopback-only Postgres/Redis binding (not exposed to LAN)

### Community 62 - "Dev Dependencies"
Cohesion: 0.25
Nodes (8): devDependencies, autoprefixer, postcss, tailwindcss, @types/node, @types/react, @types/react-dom, typescript

### Community 63 - "Compose Services"
Cohesion: 0.36
Nodes (8): api — FastAPI Backend Service, backupdata Volume, db — PostgreSQL 16 Database Service, pgdata Volume, redis — Redis 7 Queue/Cache Service, redisdata Volume, scanner — Network Scan Worker Service, web — Next.js Frontend Service

### Community 64 - "Allocation Tests"
Cohesion: 0.52
Nodes (6): _mk_prefix(), test_address_crud_and_dup_guard(), test_allocation_skips_existing(), test_concurrent_allocation_unique(), test_exhausted_prefix_conflicts(), test_sequential_allocation_skips_boundaries()

### Community 65 - "Prefixes Page"
Cohesion: 0.33
Nodes (3): PrefixesPage(), PrefixRow, utilColor()

### Community 66 - "Auth Guards"
Cohesion: 0.33
Nodes (6): AsyncSession, Request, Guard for every API route. Returns the User, or None in allow_insecure mode., Guard for every API route. Returns the User, or None in allow_insecure mode., require_auth(), set_actor()

### Community 69 - "Security Docs"
Cohesion: 0.33
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 70 - "Health Probes"
Cohesion: 0.40
Nodes (5): healthz(), get, Readiness probe: verifies DB + Redis connectivity., readyz(), JSONResponse

### Community 71 - "Changelog Tests"
Cohesion: 0.60
Nodes (4): AsyncClient, test_changelog_captures_ip_status_change(), test_changelog_records_crud(), test_changelog_scoped_filters()

### Community 72 - "Backup Docs"
Cohesion: 0.40
Nodes (5): backupdata volume (/backups), Backup file format, Backup & Restore, Restore, Take a backup

### Community 73 - "NPM Scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 77 - "README Feature Sections"
Cohesion: 0.50
Nodes (4): Features, IPAM, Platform, Scanner

## Knowledge Gaps
- **176 isolated node(s):** `Row`, `SortKey`, `CellState`, `BadgeProps`, `CheckboxProps` (+171 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 485 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ScanJob` connect `Auth & Dashboard Pages` to `Ops & Audit Pages`, `Import Wizard Frontend`, `Entity Dialogs & UI`, `Scan Jobs API`, `Scan Worker & ARQ`?**
  _High betweenness centrality (0.223) - this node is a cross-community bridge._
- **Why does `create_scan()` connect `Scan Jobs API` to `IPAM Tree & Stats`, `Auth & Dashboard Pages`, `ScanJob Model & Metrics`, `Runtime Settings & Config`, `Import Commit & Seeding`, `Scan Worker & ARQ`, `Sites & CRUD Router`?**
  _High betweenness centrality (0.163) - this node is a cross-community bridge._
- **Why does `get_or_404()` connect `Sites & CRUD Router` to `IPAM Tree & Stats`, `IP Address API`, `Workbook Import API`, `Prefix Management API`, `VRF API`, `IP Ranges API`, `Tags API`, `API Routing & Deps`, `Import Commit & Seeding`, `Scan Jobs API`, `Discovery Inbox`, `VLAN API`, `Entity CRUD & Schemas`?**
  _High betweenness centrality (0.122) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `User` (e.g. with `bulk_addresses()` and `me()`) actually correct?**
  _`User` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 35 inferred relationships involving `IPAMError` (e.g. with `confirm_discovered()` and `create_prefix()`) actually correct?**
  _`IPAMError` has 35 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `IPAddress` (e.g. with `list_discovered()` and `confirm_discovered()`) actually correct?**
  _`IPAddress` has 16 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Row`, `SortKey`, `CellState` to the rest of the system?**
  _176 weakly-connected nodes found - possible documentation gaps or missing edges._