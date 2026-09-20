# Graph Report - IpamBox  (2026-09-21)

## Corpus Check
- 263 files · ~228,392 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: (none) 7, .ini 2, .example 1)

## Summary
- 1986 nodes · 5467 edges · 138 communities (75 shown, 43 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 334 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Prefix Detail & Address UI
- Entity CRUD Pages
- Auth & Sessions
- RBAC & User Tests
- Shared Types & Form UI
- Workbook Normalizers
- Backup Service & Models
- Import Planner
- Frontend API Client
- Search & Prefix Math
- IPAM Service Core
- App Shell & Frontend Auth
- Route Error Boundaries
- Auth Deps & Permissions
- Scans API
- Prefs & Row Navigation
- Import API
- Scanner Tests
- Prefix Tree View
- App Bootstrap & DB
- Worker & Scan Orchestration
- UI Primitives & Scripts
- VLAN API
- Dashboard UI
- Settings API
- Tags API
- Runtime Settings
- Changelog UI & Utils
- Import Plan Tests
- Entity CRUD Factory
- Maintenance API
- Scanner Pipeline
- Site Sheet Parsing Tests
- Core IPAM Models
- Config & Redis Clients
- Auth & Search Tests
- Addresses API
- Reconcile Tests
- Frontend Dependencies
- Settings Pages UI
- CRUD Router & Ranges
- Sites API
- Workbook Parser Tests
- Test Fixtures & Allocation
- TypeScript Config
- VRF API
- Import Executor
- IP Range Schemas
- Docker Compose Services
- Command Palette & Prefs
- IPAddress Model
- Backup Restore
- Users API
- Settings Tests
- Changelog Core
- Prefix Schemas
- Master Sites Parser Tests
- Maintenance Tests
- Root Layout & Prefs Init
- Sheet Classification
- Backup File IO
- Normalize Tests
- Prefix API Tests
- Circuit Schemas
- Keyboard Navigation
- Workbook Reader
- Frontend Build Deps
- Positional Column Parsing
- Tree Page Texts
- Entity CRUD Tests
- Next.js Config
- Loading & Separator UI
- Ops Endpoints
- CSV Export
- Changelog Tests
- Security Policy Doc
- Backend Core Deps
- DB Driver Deps
- Certificates Page
- Circuits Page
- Discovery Page
- Import Page
- Login Page
- Prefix Detail Page
- Prefixes Page
- Scans Page
- Services Page
- Appearance Page
- Backup Page
- Data Page
- Features Page
- Security Page
- Users Page
- Setup Page
- Sites Page
- Tags Page
- VLANs Page
- VRFs Page
- Queue Deps
- Test Deps
- Next Env Types
- XFF Shim
- FastAPI Request
- Prefix Model
- Python Exception
- bcrypt Dep
- httpx Dep
- openpyxl Dep
- psutil Dep
- Scapy Dep
- App Icon
- Root Layout
- Backup Tables Registry
- Env Example
- GitHub Repo
- MIT License
- Seeding Service
- Security Deployment Notes

## God Nodes (most connected - your core abstractions)
1. `react` - 88 edges
2. `User` - 54 edges
3. `cn()` - 53 edges
4. `get_or_404()` - 51 edges
5. `IPAMError` - 50 edges
6. `lucide-react` - 46 edges
7. `Base` - 43 edges
8. `_matrix()` - 39 edges
9. `get_settings()` - 38 edges
10. `IPAddress` - 37 edges

## Surprising Connections (you probably didn't know these)
- `create_prefix()` --calls--> `Prefix`  [EXTRACTED]
  backend/app/api/v1/prefixes.py → frontend/src/types/index.ts
- `_resolve_prefix()` --calls--> `Prefix`  [EXTRACTED]
  backend/app/worker/worker.py → frontend/src/types/index.ts
- `run_scheduled_scans()` --calls--> `ScanJob`  [EXTRACTED]
  backend/app/worker/worker.py → frontend/src/types/index.ts
- `PrefixesPage()` --calls--> `useTags()`  [EXTRACTED]
  app/prefixes/prefixes-client.tsx → components/tag-picker.tsx
- `SavedViews()` --calls--> `usePrefs()`  [EXTRACTED]
  components/saved-views.tsx → lib/prefs.ts

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Compose-level XFF trust chain (pinned bridge IP + trusted-proxies env + uvicorn flags)** — docker_compose_trusted_proxies, docker_compose_uvicorn_proxy_flags, docker_compose_web_service, docker_compose_ipam_network [EXTRACTED 1.00]
- **Loopback data plane (DB/Redis published on 127.0.0.1, reachable by host-networked scanner)** — docker_compose_db_service, docker_compose_redis_service, docker_compose_loopback_binding, docker_compose_scanner_service, docker_compose_scanner_host_mode [EXTRACTED 1.00]
- **Scan-size guard shared between API validation and worker** — docker_compose_api_service, docker_compose_scanner_service, docker_compose_scan_max_hosts [EXTRACTED 1.00]

## Communities (138 total, 43 thin omitted)

### Community 0 - "Prefix Detail & Address UI"
Cohesion: 0.04
Nodes (68): IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, SplitPlan, toggleIn(), AddressList(), AddrMapViewSwitcher() (+60 more)

### Community 1 - "Entity CRUD Pages"
Cohesion: 0.10
Nodes (52): EMPTY, ACTION_STYLES, ChangeSummary(), fmt(), EMPTY, BulkResp, AssetRow, EMPTY (+44 more)

### Community 2 - "Auth & Sessions"
Cohesion: 0.09
Nodes (59): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+51 more)

### Community 3 - "RBAC & User Tests"
Cohesion: 0.10
Nodes (56): str, UserRole, _backup_bytes(), _envelope_bytes(), _mkusers(), Hand-craft a backup envelope (e.g. with a forged users table)., Guard: every ORM table must be backed up (or explicitly excluded). Adding a new…, Fresh-server scenario: the migration-seeded Global VRF is replaced by the… (+48 more)

### Community 4 - "Shared Types & Form UI"
Cohesion: 0.05
Nodes (41): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, Step (+33 more)

### Community 5 - "Workbook Normalizers"
Cohesion: 0.08
Nodes (41): assemble_ip(), clean(), _clean_octets(), map_status(), mask_to_prefixlen(), network_of(), norm_header(), norm_mac() (+33 more)

### Community 6 - "Backup Service & Models"
Cohesion: 0.12
Nodes (22): AppSetting, Runtime-editable setting override. Absent row -> env var -> default., Asset, SW/HW catalog rows (תוכנות וחומרות) and serial-number inventory…, Base, Certificate, Certificate-expiry row from the תוקף תעודות sheet., Circuit (+14 more)

### Community 7 - "Import Planner"
Cohesion: 0.10
Nodes (15): parse_sites_master_records(), _Planner, _preview(), (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Folded sheet title vs site name/code — word-boundary matching so 'int' doesn't…, Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new… (+7 more)

### Community 8 - "Frontend API Client"
Cohesion: 0.09
Nodes (26): fmtEta(), ScansPage(), DataPage(), download(), ConfirmAction(), ConfirmDialog(), QuickScanDialog(), useScanStream() (+18 more)

### Community 9 - "Search & Prefix Math"
Cohesion: 0.12
Nodes (35): _folded(), AsyncSession, get, search(), match(), BaseModel, SearchAddress, SearchAsset (+27 more)

### Community 10 - "IPAM Service Core"
Cohesion: 0.12
Nodes (36): AllocateIPRequest, allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses() (+28 more)

### Community 11 - "App Shell & Frontend Auth"
Cohesion: 0.08
Nodes (25): fmtAgo(), SecurityPage(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS, NavGroup, NavItem (+17 more)

### Community 13 - "Auth Deps & Permissions"
Cohesion: 0.11
Nodes (33): delete_scheduled_backup(), download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, delete, get, post (+25 more)

### Community 14 - "Scans API"
Cohesion: 0.12
Nodes (29): cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession, get (+21 more)

### Community 15 - "Prefs & Row Navigation"
Cohesion: 0.09
Nodes (29): CertificatesPage(), CircuitsPage(), InventoryPage(), metadata, PrintClient(), PrefixesPage(), utilColor(), ServicesPage() (+21 more)

### Community 16 - "Import API"
Cohesion: 0.13
Nodes (30): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+22 more)

### Community 17 - "Scanner Tests"
Cohesion: 0.10
Nodes (23): infer_device_type(), Best-effort device classification; None when nothing matched., _global_vrf_id(), _infer_scan_vrf(), Pick the VRF for a scan that didn't specify one. An exact-match prefix living…, _scan_vrf(), WorkerSettings, _extra_vrf() (+15 more)

### Community 18 - "Prefix Tree View"
Cohesion: 0.14
Nodes (25): metadata, ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), collectExpandableKeys(), flattenTree() (+17 more)

### Community 19 - "App Bootstrap & DB"
Cohesion: 0.10
Nodes (23): list_changelog(), AsyncSession, get, AsyncSession, get, stats(), confirm_discovered(), ConfirmBody (+15 more)

### Community 20 - "Worker & Scan Orchestration"
Cohesion: 0.14
Nodes (29): get_redis(), set_actor(), Effective, get_effective(), detect_interface(), detect_local_cidr(), CIDR of the default-route interface, e.g. '192.168.1.0/24'., _due() (+21 more)

### Community 21 - "UI Primitives & Scripts"
Cohesion: 0.07
Nodes (25): name, private, scripts, build, dev, lint, start, version (+17 more)

### Community 22 - "VLAN API"
Cohesion: 0.16
Nodes (27): list_items(), _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans() (+19 more)

### Community 23 - "Dashboard UI"
Cohesion: 0.10
Nodes (18): ChangelogPage(), metadata, ACTION_STYLES, DashboardPage(), metadata, expiryBadge(), Badge(), BadgeProps (+10 more)

### Community 24 - "Settings API"
Cohesion: 0.13
Nodes (25): _build_out(), _lan_info(), _mask_url(), AsyncSession, get, Hide the password in a scheme://user:pass@host URL., LAN identity detected by the host-networked worker (written to Redis). Falls…, read_settings() (+17 more)

### Community 25 - "Tags API"
Cohesion: 0.16
Nodes (21): assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession, delete (+13 more)

### Community 26 - "Runtime Settings"
Cohesion: 0.11
Nodes (16): psycopg2-style URL for alembic offline mode / scripts., Settings, _env_sourced(), Any, Runtime-editable settings: app_settings rows override env defaults. Each public…, True when the field's current value differs from its declared default., One runtime-editable setting. field: the env-backed attribute on…, SettingSpec (+8 more)

### Community 27 - "Changelog UI & Utils"
Cohesion: 0.16
Nodes (20): ACTION_STYLES, ChangeSummary(), fmt(), DropdownMenuCheckboxItem, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator (+12 more)

### Community 28 - "Import Plan Tests"
Cohesion: 0.18
Nodes (12): _master_row(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind…, Mashapan TA + MATPASH share number 200 — merge + conflict, not a silent… (+4 more)

### Community 29 - "Entity CRUD Factory"
Cohesion: 0.17
Nodes (18): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, AssetKind, str, AssetCreate, AssetOut, AssetUpdate, BaseModel, CertificateCreate (+10 more)

### Community 30 - "Maintenance API"
Cohesion: 0.18
Nodes (22): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+14 more)

### Community 31 - "Scanner Pipeline"
Cohesion: 0.13
Nodes (19): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), _host_chunks(), _icmp_sweep(), _ptr_lookup(), Exception (+11 more)

### Community 32 - "Site Sheet Parsing Tests"
Cohesion: 0.15
Nodes (12): _blocks(), parse_site_sheet(), Split duplicated column groups (031-style runaway): each block starts at an…, _matrix(), קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf., Bare 'Name' (Cellular) maps to the hostname field. (+4 more)

### Community 33 - "Core IPAM Models"
Cohesion: 0.21
Nodes (16): metrics(), Prometheus-style text exposition of object + scan counters., IPAddress, Prefix, Site, VLAN, VRF, main() (+8 more)

### Community 34 - "Config & Redis Clients"
Cohesion: 0.14
Nodes (16): ArqRedis, do_run_migrations(), run_migrations_online(), get_settings(), get_arq_pool(), redis_settings_from_url(), auth_on(), fixture (+8 more)

### Community 35 - "Auth & Search Tests"
Cohesion: 0.20
Nodes (19): AsyncClient, AsyncClient, test_endpoints_require_auth(), test_lockout_keyed_per_user_ip_pair(), test_login_lockout(), test_per_ip_aggregate_backstop(), test_setup_login_flow(), test_xff_only_honored_from_trusted_peer() (+11 more)

### Community 36 - "Addresses API"
Cohesion: 0.18
Nodes (20): bulk_addresses(), BulkBody, create_address(), delete_address(), export_addresses(), get_address(), import_addresses(), ImportRow (+12 more)

### Community 37 - "Reconcile Tests"
Cohesion: 0.20
Nodes (19): AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), HostResult, _prefix(), test_address_role_nat_and_bulk(), test_bulk_reports_real_counts(), test_container_move_with_children_rejected() (+11 more)

### Community 38 - "Frontend Dependencies"
Cohesion: 0.10
Nodes (21): dependencies, class-variance-authority, clsx, lucide-react, next, @radix-ui/react-dialog, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+13 more)

### Community 39 - "Settings Pages UI"
Cohesion: 0.15
Nodes (11): metadata, metadata, Key, ScanningPage(), SettingsPage(), Card, CardContent(), CardHeader() (+3 more)

### Community 40 - "CRUD Router & Ranges"
Cohesion: 0.16
Nodes (17): _crud_router(), delete_item(), get_item(), update_item(), _check_range_overlap(), create_range(), delete_range(), list_ranges() (+9 more)

### Community 41 - "Sites API"
Cohesion: 0.18
Nodes (17): _cascade_site_fields(), create_site(), delete_site(), get_site(), list_sites(), AsyncSession, delete, get (+9 more)

### Community 42 - "Workbook Parser Tests"
Cohesion: 0.13
Nodes (14): excel_date(), datetime/date passthrough; int/float serial (20000-80000) -> date; 'd/m/yy'…, parse_assets(), parse_certificates(), Positional 5-col layout: platform, target/VS, server, cert, expiry., 003 תוכנות וחומרות: סוג,חברה,דגם,שם התוכנה,ייעוד,גירסה,EOL,…, Workbook import: normalizer/parser unit tests (no DB) + API e2e., Small synthetic workbook: sites master + one site sheet + circuits. (+6 more)

### Community 43 - "Test Fixtures & Allocation"
Cohesion: 0.17
Nodes (17): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., sf() (+9 more)

### Community 44 - "TypeScript Config"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 45 - "VRF API"
Cohesion: 0.20
Nodes (14): create_vrf(), delete_vrf(), get_vrf(), list_vrfs(), AsyncSession, delete, get, post (+6 more)

### Community 46 - "Import Executor"
Cohesion: 0.18
Nodes (14): IPRange, A named block of addresses inside a prefix (e.g. a DHCP scope). Any defined…, commit_batch(), execute_plan(), _get_or_create_prefix(), _get_or_create_vlan(), _get_or_create_vrf(), _group_by_sheet() (+6 more)

### Community 47 - "IP Range Schemas"
Cohesion: 0.18
Nodes (12): IPRangeRole, str, ip_display(), Any, Normalize asyncpg-returned ipaddress objects / strings to display form. INET…, to_int(), IPRangeCreate, IPRangeOut (+4 more)

### Community 48 - "Docker Compose Services"
Cohesion: 0.19
Nodes (18): alembic upgrade head on api start, API_BIND publish binding, api service, backupdata volume, backupdata Volume, IPAMBOX_COOKIE_SECURE env, db service (postgres:16-alpine), ipam bridge network 192.0.2.0/24 (+10 more)

### Community 49 - "Command Palette & Prefs"
Cohesion: 0.18
Nodes (16): CommandPalette(), Icon, Item, itemsFor(), remember(), SearchOut, AddrMapView, DEFAULT_PREFS (+8 more)

### Community 50 - "IPAddress Model"
Cohesion: 0.25
Nodes (10): IPRole, IPStatus, str, IPAddressCreate, IPAddressOut, IPAddressPage, IPAddressUpdate, _norm_mac() (+2 more)

### Community 51 - "Backup Restore"
Cohesion: 0.15
Nodes (17): BackupError, BackupPreview, _from_json(), _gunzip(), inspect_backup(), Any, AsyncSession, Exception (+9 more)

### Community 52 - "Users API"
Cohesion: 0.24
Nodes (15): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+7 more)

### Community 53 - "Settings Tests"
Cohesion: 0.19
Nodes (13): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_files_report_effective_schedule(), test_internal_keys_hidden() (+5 more)

### Community 54 - "Changelog Core"
Cohesion: 0.29
Nodes (13): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), Audit trail via session flush hooks. before_flush collects (object, action,…, register(), _repr() (+5 more)

### Community 55 - "Prefix Schemas"
Cohesion: 0.25
Nodes (11): PrefixStatus, str, AllocateIPRequest, AvailableIPOut, PrefixCreate, PrefixOut, PrefixSplitOut, PrefixUpdate (+3 more)

### Community 56 - "Master Sites Parser Tests"
Cohesion: 0.19
Nodes (8): _master_blocks(), parse_sites_master(), (first, second) octet pairs a master row declares — lets sheet->site matching…, Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins., TestSitesMasterParser

### Community 57 - "Maintenance Tests"
Cohesion: 0.21
Nodes (11): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_now_enqueues(), test_clear_discovery() (+3 more)

### Community 58 - "Root Layout & Prefs Init"
Cohesion: 0.18
Nodes (10): metadata, PrefsInit(), Tooltip, TooltipContent, TooltipProvider, TooltipTrigger, applyPrefs(), resolveTheme() (+2 more)

### Community 59 - "Sheet Classification"
Cohesion: 0.24
Nodes (6): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, TestClassify

### Community 60 - "Backup File IO"
Cohesion: 0.29
Nodes (11): backup_dir(), delete_backup_file(), list_backup_files(), prune_backups(), Path, Fetch a scheduled backup by file name (path-traversal safe)., Delete a scheduled backup by file name (path-traversal safe)., Delete oldest scheduled backups beyond the retention count. (+3 more)

### Community 62 - "Prefix API Tests"
Cohesion: 0.38
Nodes (9): _global_vrf_id(), test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_prefixes_order_by_utilization_and_limit(), test_same_cidr_allowed_across_vrfs(), test_split_cardinality_cap(), test_split_endpoint(), test_tree_endpoint() (+1 more)

### Community 63 - "Circuit Schemas"
Cohesion: 0.36
Nodes (5): CircuitCreate, CircuitOut, CircuitUpdate, BaseModel, field_validator

### Community 64 - "Keyboard Navigation"
Cohesion: 0.33
Nodes (7): AppShell(), moveRowNav(), RowNavApi, G_CHORDS, isEditableTarget(), modalOpen(), useGlobalShortcuts()

### Community 65 - "Workbook Reader"
Cohesion: 0.36
Nodes (5): Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, load_workbook_bytes(), XLSX -> sheet matrices via openpyxl (read_only streams, values only)., Parse workbook bytes into per-sheet row matrices. read_only + data_only:…, SheetMatrix

### Community 66 - "Frontend Build Deps"
Cohesion: 0.25
Nodes (8): devDependencies, autoprefixer, postcss, tailwindcss, @types/node, @types/react, @types/react-dom, typescript

### Community 67 - "Positional Column Parsing"
Cohesion: 0.29
Nodes (4): _col_class(), _positional_columns(), Dominant content class of a column sample., Headerless sheet: locate the IP column, then assign the remaining canonical…

### Community 68 - "Tree Page Texts"
Cohesion: 0.53
Nodes (5): ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText()

### Community 70 - "Next.js Config"
Cohesion: 0.33
Nodes (3): nextConfig, metadata, next

### Community 71 - "Loading & Separator UI"
Cohesion: 0.40
Nodes (3): Separator, Skeleton(), @radix-ui/react-separator

### Community 72 - "Ops Endpoints"
Cohesion: 0.40
Nodes (5): healthz(), get, Readiness probe: verifies DB + Redis connectivity., readyz(), JSONResponse

### Community 73 - "CSV Export"
Cohesion: 0.40
Nodes (4): csv_response(), parse_csv(), CSV text -> list of row dicts (header-named, stripped)., StreamingResponse

### Community 74 - "Changelog Tests"
Cohesion: 0.60
Nodes (4): AsyncClient, test_changelog_captures_ip_status_change(), test_changelog_records_crud(), test_changelog_scoped_filters()

### Community 75 - "Security Policy Doc"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 76 - "Backend Core Deps"
Cohesion: 0.50
Nodes (4): fastapi 0.115.6, pydantic 2.10.3, pydantic-settings 2.6.1, uvicorn[standard] 0.32.1

### Community 89 - "DB Driver Deps"
Cohesion: 0.67
Nodes (3): alembic 1.14.0, asyncpg 0.30.0, sqlalchemy[asyncio] 2.0.36

## Knowledge Gaps
- **219 isolated node(s):** `AssetRow`, `PrefixRow`, `ServiceRow`, `VlanRow`, `RowNavApi` (+214 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 659 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **43 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ScanJob` connect `Scans API` to `Frontend API Client`, `Shared Types & Form UI`, `Worker & Scan Orchestration`, `Dashboard UI`?**
  _High betweenness centrality (0.205) - this node is a cross-community bridge._
- **Why does `Prefix` connect `Shared Types & Form UI` to `Prefix Detail & Address UI`, `Entity CRUD Pages`, `IPAM Service Core`, `Worker & Scan Orchestration`, `Dashboard UI`?**
  _High betweenness centrality (0.200) - this node is a cross-community bridge._
- **Why does `create_scan()` connect `Scans API` to `Core IPAM Models`, `Config & Redis Clients`, `CRUD Router & Ranges`, `IPAM Service Core`, `Worker & Scan Orchestration`?**
  _High betweenness centrality (0.137) - this node is a cross-community bridge._
- **Are the 29 inferred relationships involving `User` (e.g. with `me()` and `change_password()`) actually correct?**
  _`User` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Are the 35 inferred relationships involving `IPAMError` (e.g. with `create_address()` and `get_address()`) actually correct?**
  _`IPAMError` has 35 INFERRED edges - model-reasoned connections that need verification._
- **What connects `AssetRow`, `PrefixRow`, `ServiceRow` to the rest of the system?**
  _219 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Prefix Detail & Address UI` be split into smaller, more focused modules?**
  _Cohesion score 0.04360298336201951 - nodes in this community are weakly interconnected._