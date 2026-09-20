# Graph Report - IpamBox  (2026-09-20)

## Corpus Check
- 254 files · ~217,516 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1922 nodes · 5669 edges · 133 communities (81 shown, 33 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 340 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Entity Client Pages
- App Shell & Root Layout
- Prefix Detail & Subnet Grid
- Circuit Schemas
- Settings Client Pages
- Workbook Normalizer
- Dashboard & Status Badges
- App Entry & Asset Model
- Import Planner
- Redis & Auth Security
- Changelog & Dashboard API
- Search API
- Server Page Wrappers
- Route Error Boundaries
- Import API
- Backup Tests
- Auth API
- VLAN API
- Prefix API
- Import Wizard UI
- Tags API
- Site Planner Tests
- Addresses API
- IPAM Tree Builder
- Entity CRUD Routers
- Maintenance API
- Scan Metrics & Tests
- RBAC Tests
- Site Sheet Parser
- package.json Metadata
- Prefix Tree Page
- Scans API
- Sites API
- Prefix & VRF Models
- Scanner & OUI Lookup
- Frontend Dependencies
- Import Executor
- Entity Parsers & Tests
- Runtime Settings
- tsconfig Options
- VRF API
- README Documentation
- Range CRUD Helpers
- Users API
- Scanner VRF Tests
- Backup API
- Auth Guards & LAN Info
- Python Dependencies
- Settings Tests
- Backup File Management
- Changelog Hooks
- Backup Serialize/Restore
- Sites Master Parser
- Test Fixtures
- Sheet Classifier
- Scan Worker
- Search Tests
- Backup Restore
- IPAM Extras Tests
- Normalizer Tests
- Scanner Service Config
- Discovery Inbox API
- Settings Config
- Prefix API Tests
- SSE Stream & CSV
- Workbook Reader
- Fake ARQ Fixture
- Data Model Invariants
- Frontend Dev Dependencies
- Docker Compose Services
- Column Classifier
- Scan Reconcile
- Test Auth Fixtures
- Entity CRUD Tests
- Next Config
- Project Docs
- Health Probes
- Changelog Tests
- Backup Docs
- npm Scripts
- Data Settings Page
- Chart Theme Hook
- Alembic Env
- Permission Helpers
- Login Page
- Feature List
- Route Page certificates
- Route Page changelog
- Route Page circuits
- Route Page discovery
- Route Page import
- Route Page inventory
- Route Page dashboard
- Route Page prefix detail
- Route Page prefixes
- Route Page scans
- Route Page services
- Route Page backup
- Route Page features
- Route Page settings
- Route Page scanning
- Route Page security
- Route Page setup
- Route Page sites
- Route Page tags
- Route Page vlans
- Next Env Types
- Tailwind Config
- Request Import
- Prefix Import
- Exception Import
- App Icon
- Root Layout Node
- README Doc

## God Nodes (most connected - your core abstractions)
1. `react` - 87 edges
2. `cn()` - 65 edges
3. `User` - 54 edges
4. `get_or_404()` - 51 edges
5. `IPAMError` - 50 edges
6. `lucide-react` - 46 edges
7. `Base` - 43 edges
8. `useAsyncData()` - 43 edges
9. `_matrix()` - 39 edges
10. `Button` - 38 edges

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

## Communities (133 total, 33 thin omitted)

### Community 0 - "Entity Client Pages"
Cohesion: 0.10
Nodes (54): EMPTY, ACTION_STYLES, ChangeSummary(), fmt(), EMPTY, BulkResp, AssetRow, EMPTY (+46 more)

### Community 1 - "App Shell & Root Layout"
Cohesion: 0.05
Nodes (56): metadata, AppearancePage(), TagsPage(), AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS (+48 more)

### Community 2 - "Prefix Detail & Subnet Grid"
Cohesion: 0.07
Nodes (48): IP_ROLES, IP_STATUSES, RANGE_ROLES, SplitPlan, AddressFilterPanel(), STATUSES, AddressList(), AddrMapViewSwitcher() (+40 more)

### Community 3 - "Circuit Schemas"
Cohesion: 0.06
Nodes (35): IPRole, str, IPRangeRole, str, CircuitCreate, CircuitOut, CircuitUpdate, BaseModel (+27 more)

### Community 4 - "Settings Client Pages"
Cohesion: 0.15
Nodes (27): BackupSettingsPage(), downloadUrl(), fmtSize(), FEATURES, Key, Key, SetupPage(), CidrListEditor() (+19 more)

### Community 5 - "Workbook Normalizer"
Cohesion: 0.08
Nodes (41): assemble_ip(), clean(), _clean_octets(), map_status(), mask_to_prefixlen(), network_of(), norm_header(), norm_mac() (+33 more)

### Community 6 - "Dashboard & Status Badges"
Cohesion: 0.06
Nodes (41): ACTION_STYLES, expiryBadge(), IpStatusBadge(), PrefixStatusBadge(), prefixVariant, ScanStatusBadge(), scanVariant, Badge() (+33 more)

### Community 7 - "App Entry & Asset Model"
Cohesion: 0.12
Nodes (21): AppSetting, Runtime-editable setting override. Absent row -> env var -> default., Asset, SW/HW catalog rows (תוכנות וחומרות) and serial-number inventory…, Base, Certificate, Certificate-expiry row from the תוקף תעודות sheet., Circuit (+13 more)

### Community 8 - "Import Planner"
Cohesion: 0.10
Nodes (15): parse_sites_master_records(), _Planner, _preview(), (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Folded sheet title vs site name/code — word-boundary matching so 'int' doesn't…, Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new… (+7 more)

### Community 9 - "Redis & Auth Security"
Cohesion: 0.08
Nodes (41): ArqRedis, get_settings(), get_arq_pool(), get_redis(), redis_settings_from_url(), clear_login_failures(), create_session(), destroy_other_sessions() (+33 more)

### Community 10 - "Changelog & Dashboard API"
Cohesion: 0.09
Nodes (32): list_changelog(), AsyncSession, get, _build_out(), _mask_url(), AsyncSession, get, Hide the password in a scheme://user:pass@host URL. (+24 more)

### Community 11 - "Search API"
Cohesion: 0.12
Nodes (35): _folded(), AsyncSession, get, search(), match(), BaseModel, SearchAddress, SearchAsset (+27 more)

### Community 12 - "Server Page Wrappers"
Cohesion: 0.10
Nodes (35): CertificatesPage(), ChangelogPage(), CircuitsPage(), DashboardPage(), DiscoveryPage(), InventoryPage(), PrefixDetailPage(), toggleIn() (+27 more)

### Community 14 - "Import API"
Cohesion: 0.12
Nodes (32): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+24 more)

### Community 15 - "Backup Tests"
Cohesion: 0.17
Nodes (30): _backup_bytes(), _envelope_bytes(), _mkusers(), Hand-craft a backup envelope (e.g. with a forged users table)., Guard: every ORM table must be backed up (or explicitly excluded). Adding a new…, Fresh-server scenario: the migration-seeded Global VRF is replaced by the…, Fresh-server scenario: the target's admins survive; its non-admin set is fully…, A forged users table without the includes_users flag is treated as unknown and… (+22 more)

### Community 16 - "Auth API"
Cohesion: 0.17
Nodes (28): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+20 more)

### Community 17 - "VLAN API"
Cohesion: 0.18
Nodes (25): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+17 more)

### Community 18 - "Prefix API"
Cohesion: 0.16
Nodes (25): AllocateIPRequest, allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses() (+17 more)

### Community 19 - "Import Wizard UI"
Cohesion: 0.09
Nodes (19): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, Step (+11 more)

### Community 20 - "Tags API"
Cohesion: 0.17
Nodes (20): assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession, delete (+12 more)

### Community 21 - "Site Planner Tests"
Cohesion: 0.18
Nodes (12): _master_row(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind…, Mashapan TA + MATPASH share number 200 — merge + conflict, not a silent… (+4 more)

### Community 22 - "Addresses API"
Cohesion: 0.16
Nodes (22): bulk_addresses(), BulkBody, create_address(), delete_address(), export_addresses(), get_address(), import_addresses(), ImportRow (+14 more)

### Community 23 - "IPAM Tree Builder"
Cohesion: 0.15
Nodes (21): AsyncSession, get, stats(), build_tree(), site_node(), vrf_node(), vrf_prefix_tree(), prefix_node() (+13 more)

### Community 24 - "Entity CRUD Routers"
Cohesion: 0.17
Nodes (18): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, AssetKind, str, AssetCreate, AssetOut, AssetUpdate, BaseModel, CertificateCreate (+10 more)

### Community 25 - "Maintenance API"
Cohesion: 0.17
Nodes (22): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+14 more)

### Community 26 - "Scan Metrics & Tests"
Cohesion: 0.15
Nodes (20): _job_payload(), metrics(), Prometheus-style text exposition of object + scan counters., str, ScanJob, ScanStatus, Site, fake_arq() (+12 more)

### Community 27 - "RBAC Tests"
Cohesion: 0.34
Nodes (22): str, UserRole, login(), mkuser(), other_client(), AsyncClient, AsyncSession, allow_insecure keeps full access (existing behavior preserved). (+14 more)

### Community 28 - "Site Sheet Parser"
Cohesion: 0.15
Nodes (12): _blocks(), parse_site_sheet(), Split duplicated column groups (031-style runaway): each block starts at an…, _matrix(), קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf., Bare 'Name' (Cellular) maps to the hostname field. (+4 more)

### Community 29 - "package.json Metadata"
Cohesion: 0.09
Nodes (22): name, private, version, autoprefixer, clsx, postcss, @radix-ui/react-dialog, @radix-ui/react-dropdown-menu (+14 more)

### Community 30 - "Prefix Tree Page"
Cohesion: 0.20
Nodes (18): metadata, ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), collectExpandableKeys(), flattenTree() (+10 more)

### Community 31 - "Scans API"
Cohesion: 0.16
Nodes (18): cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), list_scans(), AsyncSession, get, post (+10 more)

### Community 32 - "Sites API"
Cohesion: 0.16
Nodes (19): _cascade_site_fields(), create_site(), delete_site(), get_site(), list_sites(), AsyncSession, delete, get (+11 more)

### Community 33 - "Prefix & VRF Models"
Cohesion: 0.16
Nodes (17): IPRange, A named block of addresses inside a prefix (e.g. a DHCP scope). Any defined…, Prefix, PrefixStatus, str, VRF, main(), Seed sample data: a Site, the Global VRF, and the auto-detected LAN prefix. Run… (+9 more)

### Community 34 - "Scanner & OUI Lookup"
Cohesion: 0.14
Nodes (18): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), _icmp_sweep(), infer_device_type(), _ptr_lookup(), Blocking scapy ARP sweep -> {ip: mac}. Runs in a thread. (+10 more)

### Community 35 - "Frontend Dependencies"
Cohesion: 0.10
Nodes (21): dependencies, class-variance-authority, clsx, lucide-react, next, @radix-ui/react-dialog, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+13 more)

### Community 36 - "Import Executor"
Cohesion: 0.19
Nodes (15): IPAddress, IPStatus, commit_batch(), execute_plan(), _get_or_create_prefix(), _get_or_create_site(), _get_or_create_vlan(), _get_or_create_vrf() (+7 more)

### Community 37 - "Entity Parsers & Tests"
Cohesion: 0.13
Nodes (14): excel_date(), datetime/date passthrough; int/float serial (20000-80000) -> date; 'd/m/yy'…, parse_assets(), parse_certificates(), Positional 5-col layout: platform, target/VS, server, cert, expiry., 003 תוכנות וחומרות: סוג,חברה,דגם,שם התוכנה,ייעוד,גירסה,EOL,…, Workbook import: normalizer/parser unit tests (no DB) + API e2e., Small synthetic workbook: sites master + one site sheet + circuits. (+6 more)

### Community 38 - "Runtime Settings"
Cohesion: 0.16
Nodes (16): Effective, _env_sourced(), get_effective(), Any, AsyncSession, Runtime-editable settings: app_settings rows override env defaults. Each public…, True when the field's current value differs from its declared default., One runtime-editable setting. field: the env-backed attribute on… (+8 more)

### Community 39 - "tsconfig Options"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 40 - "VRF API"
Cohesion: 0.20
Nodes (14): create_vrf(), delete_vrf(), get_vrf(), list_vrfs(), AsyncSession, delete, get, post (+6 more)

### Community 41 - "README Documentation"
Cohesion: 0.12
Nodes (18): bcrypt==4.3.0, Architecture, Configuration, Development, Extended entities (WAN circuits, certificates, inventory, service catalog), First-run auth, session cookies, bcrypt hashing, IP lockout, Hebrew data support (final-letter folding, RTL rendering), IpamBox (+10 more)

### Community 42 - "Range CRUD Helpers"
Cohesion: 0.20
Nodes (15): _crud_router(), delete_item(), get_item(), list_items(), update_item(), _check_range_overlap(), create_range(), delete_range() (+7 more)

### Community 43 - "Users API"
Cohesion: 0.24
Nodes (16): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+8 more)

### Community 44 - "Scanner VRF Tests"
Cohesion: 0.24
Nodes (12): _global_vrf_id(), _infer_scan_vrf(), Pick the VRF for a scan that didn't specify one. An exact-match prefix living…, _scan_vrf(), _extra_vrf(), _global_id(), _mk_prefix(), test_infer_scan_vrf_ambiguous_prefix_falls_back_to_global() (+4 more)

### Community 45 - "Backup API"
Cohesion: 0.23
Nodes (14): download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, get, Download a full snapshot (every table except users) as .json.gz.…, Scheduled snapshot files written by the worker into BACKUP_DIR., BackupFileInfo (+6 more)

### Community 46 - "Auth Guards & LAN Info"
Cohesion: 0.16
Nodes (16): _lan_info(), LAN identity detected by the host-networked worker (written to Redis). Falls…, AsyncSession, Request, Guard for every API route. Returns the User, or None in allow_insecure mode., require_auth(), set_actor(), detect_interface() (+8 more)

### Community 47 - "Python Dependencies"
Cohesion: 0.15
Nodes (16): alembic==1.14.0, fastapi==0.115.6, httpx==0.28.1, openpyxl==3.1.5, pydantic==2.10.3, pydantic-settings==2.6.1, pytest==8.3.4, pytest-asyncio==0.25.0 (+8 more)

### Community 48 - "Settings Tests"
Cohesion: 0.19
Nodes (13): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_files_report_effective_schedule(), test_internal_keys_hidden() (+5 more)

### Community 49 - "Backup File Management"
Cohesion: 0.20
Nodes (15): delete_scheduled_backup(), delete, backup_dir(), delete_backup_file(), list_backup_files(), prune_backups(), Path, Fetch a scheduled backup by file name (path-traversal safe). (+7 more)

### Community 50 - "Changelog Hooks"
Cohesion: 0.29
Nodes (13): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), Audit trail via session flush hooks. before_flush collects (object, action,…, register(), _repr() (+5 more)

### Community 51 - "Backup Serialize/Restore"
Cohesion: 0.19
Nodes (14): BackupPreview, build_backup(), _from_json(), Any, AsyncSession, Convert a JSON value back to what asyncpg expects for this column., Serialize every registered table into the gzipped JSON envelope. With…, Replace the non-admin user set from a users-inclusive envelope. Admin rows in… (+6 more)

### Community 52 - "Sites Master Parser"
Cohesion: 0.19
Nodes (8): _master_blocks(), parse_sites_master(), (first, second) octet pairs a master row declares — lets sheet->site matching…, Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins., TestSitesMasterParser

### Community 53 - "Test Fixtures"
Cohesion: 0.26
Nodes (12): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., session() (+4 more)

### Community 54 - "Sheet Classifier"
Cohesion: 0.24
Nodes (6): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, TestClassify

### Community 55 - "Scan Worker"
Cohesion: 0.23
Nodes (12): Exception, Raised inside the pipeline when the user cancels the scan., ScanCancelled, _due(), _eta_seconds(), _publish(), datetime, ARQ job: execute a scan and reconcile results. (+4 more)

### Community 56 - "Search Tests"
Cohesion: 0.35
Nodes (11): AsyncClient, auth_on(), _seed(), test_addresses_q_filter_not_broken(), test_search_empty_query(), test_search_grouped_results(), test_search_hebrew_folding(), test_search_ip_jump() (+3 more)

### Community 57 - "Backup Restore"
Cohesion: 0.20
Nodes (12): post, Request, Restore a backup file (raw .json.gz body). Wipes every data table (users are…, restore(), _alembic_revisions(), BackupError, _gunzip(), inspect_backup() (+4 more)

### Community 58 - "IPAM Extras Tests"
Cohesion: 0.36
Nodes (11): _prefix(), test_address_role_nat_and_bulk(), test_bulk_reports_real_counts(), test_container_move_with_children_rejected(), test_csv_export_import(), test_dashboard_attention_fields(), test_ip_ranges_exclude_allocator(), test_prefix_move_vrf() (+3 more)

### Community 60 - "Scanner Service Config"
Cohesion: 0.24
Nodes (10): arq==0.26.1, asyncpg==0.30.0, psutil==6.1.0, redis==5.2.0 (Python client), scapy==2.6.1, sqlalchemy[asyncio]==2.0.36, scanner service (ARQ worker, network_mode: host, NET_ADMIN/NET_RAW), Discovery Inbox and drift reconciliation (+2 more)

### Community 61 - "Discovery Inbox API"
Cohesion: 0.22
Nodes (9): confirm_discovered(), ConfirmBody, list_discovered(), AsyncSession, BaseModel, get, post, Unconfirmed hosts found by scanners, pending admin review. (+1 more)

### Community 62 - "Settings Config"
Cohesion: 0.22
Nodes (3): psycopg2-style URL for alembic offline mode / scripts., Settings, BaseSettings

### Community 63 - "Prefix API Tests"
Cohesion: 0.42
Nodes (8): _global_vrf_id(), test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_prefixes_order_by_utilization_and_limit(), test_same_cidr_allowed_across_vrfs(), test_split_endpoint(), test_tree_endpoint(), test_unknown_vlan_rejected()

### Community 64 - "SSE Stream & CSV"
Cohesion: 0.25
Nodes (7): SSE stream of scan progress (Redis pub/sub backed)., stream_scan(), gen(), csv_response(), parse_csv(), CSV text -> list of row dicts (header-named, stripped)., StreamingResponse

### Community 65 - "Workbook Reader"
Cohesion: 0.36
Nodes (5): Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, load_workbook_bytes(), XLSX -> sheet matrices via openpyxl (read_only streams, values only)., Parse workbook bytes into per-sheet row matrices. read_only + data_only:…, SheetMatrix

### Community 66 - "Fake ARQ Fixture"
Cohesion: 0.25
Nodes (6): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture, Stands in for the arq Redis pool — never actually dispatches work.

### Community 67 - "Data Model Invariants"
Cohesion: 0.32
Nodes (8): db service (postgres:16-alpine), pgdata volume, redis service (redis:7-alpine, appendonly), redisdata volume, Atomic next-available-IP allocation (SELECT FOR UPDATE + UNIQUE), PostgreSQL GiST exclusion constraint for CIDR overlap safety, Site -> VRF -> Prefix -> IP address hierarchy, Loopback-only Postgres/Redis binding (not exposed to LAN)

### Community 68 - "Frontend Dev Dependencies"
Cohesion: 0.25
Nodes (8): devDependencies, autoprefixer, postcss, tailwindcss, @types/node, @types/react, @types/react-dom, typescript

### Community 69 - "Docker Compose Services"
Cohesion: 0.36
Nodes (8): api — FastAPI Backend Service, backupdata Volume, db — PostgreSQL 16 Database Service, pgdata Volume, redis — Redis 7 Queue/Cache Service, redisdata Volume, scanner — Network Scan Worker Service, web — Next.js Frontend Service

### Community 70 - "Column Classifier"
Cohesion: 0.29
Nodes (4): _col_class(), _positional_columns(), Dominant content class of a column sample., Headerless sheet: locate the IP column, then assign the remaining canonical…

### Community 71 - "Scan Reconcile"
Cohesion: 0.38
Nodes (7): AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), HostResult, A stored (e.g. imported) MAC that differs from the scan is flagged in…, test_reconcile_flags_mac_mismatch(), test_reconcile_persists_ports_and_type()

### Community 72 - "Test Auth Fixtures"
Cohesion: 0.29
Nodes (4): auth_on(), fake_arq(), fixture, Turn auth on for a test, restore insecure mode after, and flush session/lockout…

### Community 74 - "Next Config"
Cohesion: 0.33
Nodes (3): nextConfig, metadata, next

### Community 75 - "Project Docs"
Cohesion: 0.33
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 76 - "Health Probes"
Cohesion: 0.40
Nodes (5): healthz(), get, Readiness probe: verifies DB + Redis connectivity., readyz(), JSONResponse

### Community 77 - "Changelog Tests"
Cohesion: 0.60
Nodes (4): AsyncClient, test_changelog_captures_ip_status_change(), test_changelog_records_crud(), test_changelog_scoped_filters()

### Community 78 - "Backup Docs"
Cohesion: 0.40
Nodes (5): backupdata volume (/backups), Backup file format, Backup & Restore, Restore, Take a backup

### Community 79 - "npm Scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 80 - "Data Settings Page"
Cohesion: 0.40
Nodes (3): DataPage(), download(), metadata

### Community 81 - "Chart Theme Hook"
Cohesion: 0.50
Nodes (4): ChartTheme, FALLBACK, readTheme(), useChartTheme()

### Community 83 - "Permission Helpers"
Cohesion: 0.50
Nodes (4): has_perm(), Effective permission set; insecure mode (user=None) gets everything., _dep(), user_permissions()

### Community 85 - "Feature List"
Cohesion: 0.50
Nodes (4): Features, IPAM, Platform, Scanner

## Knowledge Gaps
- **211 isolated node(s):** `Row`, `SortKey`, `CheckboxProps`, `SwitchProps`, `ButtonProps` (+206 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 635 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **33 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `create_prefix()` connect `Prefix API` to `Range CRUD Helpers`, `Dashboard & Status Badges`?**
  _High betweenness centrality (0.372) - this node is a cross-community bridge._
- **Why does `Prefix` connect `Dashboard & Status Badges` to `Entity Client Pages`, `Prefix API`, `Prefix Detail & Subnet Grid`?**
  _High betweenness centrality (0.372) - this node is a cross-community bridge._
- **Why does `IPAMError` connect `Prefix API` to `Sites API`, `VRF API`, `Changelog & Dashboard API`, `Range CRUD Helpers`, `Import API`, `VLAN API`, `Tags API`, `Addresses API`, `IPAM Tree Builder`, `Entity CRUD Routers`, `Discovery Inbox API`, `Scans API`?**
  _High betweenness centrality (0.175) - this node is a cross-community bridge._
- **Are the 29 inferred relationships involving `User` (e.g. with `auth_status()` and `change_password()`) actually correct?**
  _`User` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Are the 35 inferred relationships involving `IPAMError` (e.g. with `create_address()` and `delete_address()`) actually correct?**
  _`IPAMError` has 35 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Row`, `SortKey`, `CheckboxProps` to the rest of the system?**
  _211 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Entity Client Pages` be split into smaller, more focused modules?**
  _Cohesion score 0.10469867211440245 - nodes in this community are weakly interconnected._