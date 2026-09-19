# Graph Report - IpamBox  (2026-09-19)

## Corpus Check
- 195 files · ~205,757 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: (none) 7, .ini 2, .example 1)

## Summary
- 1703 nodes · 5255 edges · 95 communities (72 shown, 5 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 398 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- IPAM Frontend Pages
- Backup API
- Import Page
- Addresses API
- Auth API
- Entity Models & IPAM
- Workbook Import Planner
- Changelog & Dashboard API
- Scans API
- Entities API
- Settings & Scans Pages
- CRUD Router & VRFs
- Dashboard & Settings Pages
- Ranges API
- VLANs API
- Redis & Runtime Settings
- Scanner & OUI Lookup
- Tags API
- Scan VRF Inference
- Settings API
- Ranges API
- Workbook Parsing
- Circuits & Inventory Pages
- IP & Site Models
- Site Plan Parsing
- Workbook Import Tests
- Sites API
- Backup API
- Settings Tests
- Appearance & Prefs
- Workbook Import API
- Prefix Hierarchy Tree
- Sites API
- Normalize Tests
- Site Sheet Parser Tests
- Sheet Classification
- Login & Settings Pages
- IPAM Extras Tests
- Discovery API
- Backup API
- IPAM Service Layer
- Changelog & Data Models
- Workbook Import API
- Workbook Parsing
- Prefixes API
- Session Security
- Prefix Math
- Test Fixtures
- Workbook Normalization
- Changelog Flush Hooks
- App Layout & Config
- Auth Tests
- Prefix API Tests
- Backup File Management
- Health & Metrics
- RBAC Test Fixtures
- Entity CRUD Tests
- Auth Dependency Guard
- Changelog Tests
- Workbook Parsing
- Doc File Nodes
- Frontend Package Config
- NPM Dependencies
- TypeScript Config
- Project Documentation
- Dev Dependencies
- Docs & Security Policy
- Backup Docs
- NPM Scripts
- README Features
- Next Env Types
- Python Dependencies
- Infrastructure Docs
- Docker Services
- Compose Services
- App Icon
- Root Layout

## God Nodes (most connected - your core abstractions)
1. `cn()` - 76 edges
2. `User` - 56 edges
3. `react` - 56 edges
4. `IPAddress` - 54 edges
5. `get_or_404()` - 51 edges
6. `IPAMError` - 50 edges
7. `useAuth()` - 47 edges
8. `Base` - 43 edges
9. `lucide-react` - 42 edges
10. `Prefix` - 41 edges

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

## Communities (95 total, 5 thin omitted)

### Community 0 - "IPAM Frontend Pages"
Cohesion: 0.07
Nodes (58): Row, SortKey, CellState, AddressPage, IpAddress, IpRange, IpRole, IpStatus (+50 more)

### Community 1 - "Backup API"
Cohesion: 0.09
Nodes (28): BackupError, BackupPreview, BackupTable, restore(), build_backup(), _from_json(), _gunzip(), _has_serial_id() (+20 more)

### Community 10 - "Import Page"
Cohesion: 0.13
Nodes (24): CommitResp, Counts, PreviewResp, UploadResp, CheckboxProps, ImportBatch, RowResult, SheetPreview (+16 more)

### Community 11 - "Addresses API"
Cohesion: 0.13
Nodes (31): BulkBody, ImportRow, IPAddress, IPRole, IPStatus, IPAddressCreate, IPAddressOut, IPAddressPage (+23 more)

### Community 12 - "Auth API"
Cohesion: 0.06
Nodes (98): UserCreate, UserUpdate, User, UserRole, AuthStatus, LoginBody, SetupBody, auth_status() (+90 more)

### Community 13 - "Entity Models & IPAM"
Cohesion: 0.11
Nodes (21): Certificate, Circuit, IPRange, Service, PlanError, metrics(), execute_plan(), _get_or_create_prefix() (+13 more)

### Community 14 - "Workbook Import Planner"
Cohesion: 0.11
Nodes (14): _Planner, _preview(), Counter, (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Folded sheet title vs site name/code — word-boundary matching so 'int' doesn't…, Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new… (+6 more)

### Community 15 - "Changelog & Dashboard API"
Cohesion: 0.13
Nodes (15): ChangeField, ChangeLogOut, list_changelog(), stats(), get_session(), require_perm(), lifespan(), AsyncSession (+7 more)

### Community 16 - "Scans API"
Cohesion: 0.14
Nodes (27): ScanJob, ScanStatus, ScanConfigOut, ScanCreate, ScanJobOut, cancel_scan(), _check_cidr_allowed(), create_scan() (+19 more)

### Community 17 - "Entities API"
Cohesion: 0.14
Nodes (20): Asset, AssetKind, AssetCreate, AssetOut, AssetUpdate, CertificateCreate, CertificateOut, CertificateUpdate (+12 more)

### Community 18 - "Settings & Scans Pages"
Cohesion: 0.14
Nodes (15): AuthCtx, AuthStatus, RoleName, AppShell(), SettingsNav(), authCtxValue(), AUTH_ROUTES, NAV (+7 more)

### Community 19 - "CRUD Router & VRFs"
Cohesion: 0.20
Nodes (14): VRFCreate, VRFOut, VRFUpdate, create_vrf(), delete_vrf(), get_vrf(), list_vrfs(), update_vrf() (+6 more)

### Community 2 - "Dashboard & Settings Pages"
Cohesion: 0.06
Nodes (41): BadgeProps, Asset, AssetKind, BackupFileInfo, Certificate, ChangeField, ChangeLogEntry, Circuit (+33 more)

### Community 20 - "Ranges API"
Cohesion: 0.12
Nodes (17): IPRangeRole, CircuitCreate, CircuitOut, CircuitUpdate, IPRangeCreate, IPRangeOut, IPRangeUpdate, ip_display() (+9 more)

### Community 21 - "VLANs API"
Cohesion: 0.18
Nodes (25): VLAN, VLANGroup, VLANStatus, VLANCreate, VLANGroupCreate, VLANGroupOut, VLANGroupUpdate, VLANOut (+17 more)

### Community 22 - "Redis & Runtime Settings"
Cohesion: 0.11
Nodes (31): WorkerSettings, _lan_info(), get_arq_pool(), redis_settings_from_url(), set_actor(), get_effective(), detect_interface(), detect_local_cidr() (+23 more)

### Community 23 - "Scanner & OUI Lookup"
Cohesion: 0.12
Nodes (21): ScanCancelled, _table(), vendor_for(), _arp_scan(), _icmp_sweep(), infer_device_type(), _ptr_lookup(), scan_cidr() (+13 more)

### Community 24 - "Tags API"
Cohesion: 0.18
Nodes (17): AssignBody, TagAssignmentOut, TagCreate, TagOut, TagUpdate, assign_tag(), create_tag(), get_tag() (+9 more)

### Community 25 - "Scan VRF Inference"
Cohesion: 0.14
Nodes (18): _FakeArqJob, _FakePool, _global_vrf_id(), _infer_scan_vrf(), _scan_vrf(), _extra_vrf(), fake_arq(), _pool() (+10 more)

### Community 26 - "Settings API"
Cohesion: 0.15
Nodes (22): ChangePasswordBody, LanInfo, SessionOut, SettingsOut, SettingsPatch, SystemInfo, UserOut, SettingsValidationError (+14 more)

### Community 28 - "Ranges API"
Cohesion: 0.14
Nodes (23): IPAMError, _crud_router(), delete_item(), get_item(), list_items(), update_item(), _check_range_overlap(), create_range() (+15 more)

### Community 29 - "Workbook Parsing"
Cohesion: 0.11
Nodes (19): TestServersParser, _has(), _looks_like_header(), norm_header(), _blocks(), _is_header_echo(), _leftover_bits(), _map_columns() (+11 more)

### Community 3 - "Circuits & Inventory Pages"
Cohesion: 0.12
Nodes (38): AssetRow, PrefixRow, ServiceRow, VlanRow, SwitchProps, Site, Vlan, Vrf (+30 more)

### Community 35 - "IP & Site Models"
Cohesion: 0.21
Nodes (11): _FakeArqJob, _FakePool, fake_arq(), _pool(), test_backup_now_enqueues(), test_clear_discovery(), test_factory_reset(), test_purge_changelog() (+3 more)

### Community 37 - "Site Plan Parsing"
Cohesion: 0.17
Nodes (9): TestSitesMasterParser, _master_blocks(), parse_sites_master(), parse_sites_master_records(), (first, second) octet pairs a master row declares — lets sheet->site matching…, Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so… (+1 more)

### Community 39 - "Workbook Import Tests"
Cohesion: 0.21
Nodes (13): TestPlanSiteResolution, _master_row(), _matrix(), _plan(), _preview_of(), _site_key_by_name(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches… (+5 more)

### Community 4 - "Sites API"
Cohesion: 0.11
Nodes (17): Settings, Effective, SettingSpec, _env_sourced(), _v_bool(), _v_cidr_list(), _v_float(), _v_int() (+9 more)

### Community 40 - "Backup API"
Cohesion: 0.21
Nodes (19): PurgeBody, ResetBody, _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans() (+11 more)

### Community 42 - "Settings Tests"
Cohesion: 0.19
Nodes (13): _FakeArqJob, _FakePool, fake_arq(), _pool(), test_backup_files_report_effective_schedule(), test_internal_keys_hidden(), test_scan_guards_use_db_settings(), test_settings_changes_audited() (+5 more)

### Community 43 - "Appearance & Prefs"
Cohesion: 0.11
Nodes (27): AddrMapView, DensityChoice, Prefs, ThemeChoice, TsFormat, CircuitsPage(), InventoryPage(), PrefixesPage() (+19 more)

### Community 44 - "Workbook Import API"
Cohesion: 0.17
Nodes (11): SheetMatrix, TestAssetsParser, load_workbook_bytes(), test_commit_twice_rejected(), test_import_e2e(), _xlsx_bytes(), Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, XLSX -> sheet matrices via openpyxl (read_only streams, values only). (+3 more)

### Community 45 - "Prefix Hierarchy Tree"
Cohesion: 0.24
Nodes (17): TreeRow, PrefixNode, SiteNode, VrfNode, prefixText(), siteText(), TreePage(), vrfText() (+9 more)

### Community 46 - "Sites API"
Cohesion: 0.12
Nodes (29): Site, VRF, SiteCreate, SiteOut, SiteUpdate, DbState, _cascade_site_fields(), create_site() (+21 more)

### Community 47 - "Normalize Tests"
Cohesion: 0.12
Nodes (7): TestCertificatesParser, TestNormalize, excel_date(), parse_certificates(), date, datetime/date passthrough; int/float serial (20000-80000) -> date; 'd/m/yy'…, Positional 5-col layout: platform, target/VS, server, cert, expiry.

### Community 48 - "Site Sheet Parser Tests"
Cohesion: 0.20
Nodes (6): TestSiteSheetExtras, TestSiteSheetParser, parse_site_sheet(), MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf., Bare 'Name' (Cellular) maps to the hostname field., Non-empty unnamed columns pile into cf['extra'] instead of vanishing (Pelephone…

### Community 49 - "Sheet Classification"
Cohesion: 0.36
Nodes (3): TestClassify, classify_sheet(), (family, header_row_index, warnings). header_row_index = index of the row…

### Community 5 - "Login & Settings Pages"
Cohesion: 0.11
Nodes (35): Key, Key, ButtonProps, BackupFilesOut, BackupPreview, RestoreReport, SettingsOut, SettingsValues (+27 more)

### Community 50 - "IPAM Extras Tests"
Cohesion: 0.22
Nodes (17): HostResult, reconcile(), _prefix(), test_address_role_nat_and_bulk(), test_container_move_with_children_rejected(), test_csv_export_import(), test_dashboard_attention_fields(), test_ip_ranges_exclude_allocator() (+9 more)

### Community 53 - "Discovery API"
Cohesion: 0.22
Nodes (9): ConfirmBody, confirm_discovered(), list_discovered(), AsyncSession, BaseModel, get, post, Unconfirmed hosts found by scanners, pending admin review. (+1 more)

### Community 62 - "Backup API"
Cohesion: 0.23
Nodes (14): BackupFileInfo, BackupFilesOut, BackupPreviewOut, RestoreReport, download_backup(), download_scheduled_backup(), list_scheduled_backups(), has_perm() (+6 more)

### Community 63 - "IPAM Service Layer"
Cohesion: 0.20
Nodes (15): ConflictError, NotFoundError, build_tree(), site_node(), vrf_node(), vrf_prefix_tree(), prefix_node(), dashboard_stats() (+7 more)

### Community 7 - "Changelog & Data Models"
Cohesion: 0.18
Nodes (14): AppSetting, Base, ChangeLog, ImportBatch, Tag, TagAssignment, _fail_inflight_scans(), DeclarativeBase (+6 more)

### Community 8 - "Workbook Import API"
Cohesion: 0.12
Nodes (33): ImportBatchStatus, CommitOptions, ImportBatchOut, PreviewOptions, RowResult, SheetPreview, commit_import(), delete_import() (+25 more)

### Community 83 - "Workbook Parsing"
Cohesion: 0.29
Nodes (5): TestCircuitsParser, parse_site_number(), parse_circuits(), קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias.

### Community 9 - "Prefixes API"
Cohesion: 0.14
Nodes (34): Prefix, PrefixStatus, AllocateIPRequest, AvailableIPOut, PrefixCreate, PrefixOut, PrefixSplitOut, PrefixUpdate (+26 more)

### Community 27 - "Session Security"
Cohesion: 0.18
Nodes (21): get_redis(), clear_login_failures(), create_session(), destroy_other_sessions(), destroy_session(), destroy_session_by_suffix(), _fails_key(), get_session_user_id() (+13 more)

### Community 32 - "Prefix Math"
Cohesion: 0.21
Nodes (18): children(), lowest_free(), parent_chain(), reserves_boundaries(), to_network(), usable_bounds(), usable_count(), test_children_split() (+10 more)

### Community 33 - "Test Fixtures"
Cohesion: 0.17
Nodes (17): _base_dsn(), client(), engine(), _prepare_test_db(), sf(), _split_dsn(), test_url(), _mk_prefix() (+9 more)

### Community 36 - "Workbook Normalization"
Cohesion: 0.11
Nodes (28): assemble_ip(), clean(), _clean_octets(), map_status(), mask_to_prefixlen(), network_of(), norm_mac(), parse_range_end() (+20 more)

### Community 51 - "Changelog Flush Hooks"
Cohesion: 0.35
Nodes (11): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), register(), _repr(), _ser() (+3 more)

### Community 54 - "App Layout & Config"
Cohesion: 0.20
Nodes (8): PrefsInit(), applyPrefs(), resolveTheme(), useApplyPrefs(), nextConfig, metadata, TooltipProvider, next

### Community 55 - "Auth Tests"
Cohesion: 0.13
Nodes (18): do_run_migrations(), run_migrations_online(), get_settings(), env_password(), auth_on(), test_endpoints_require_auth(), test_login_lockout(), test_setup_login_flow() (+10 more)

### Community 56 - "Prefix API Tests"
Cohesion: 0.46
Nodes (7): _global_vrf_id(), test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_same_cidr_allowed_across_vrfs(), test_split_endpoint(), test_tree_endpoint(), test_unknown_vlan_rejected()

### Community 6 - "Backup File Management"
Cohesion: 0.19
Nodes (15): delete_scheduled_backup(), backup_dir(), backup_filename(), delete_backup_file(), list_backup_files(), prune_backups(), read_backup_file(), write_backup_file() (+7 more)

### Community 60 - "Health & Metrics"
Cohesion: 0.40
Nodes (5): healthz(), readyz(), get, JSONResponse, Readiness probe: verifies DB + Redis connectivity.

### Community 61 - "RBAC Test Fixtures"
Cohesion: 0.29
Nodes (4): auth_on(), fake_arq(), fixture, Turn auth on for a test, restore insecure mode after, and flush session/lockout…

### Community 66 - "Auth Dependency Guard"
Cohesion: 0.50
Nodes (4): require_auth(), AsyncSession, Request, Guard for every API route. Returns the User, or None in allow_insecure mode.

### Community 67 - "Changelog Tests"
Cohesion: 0.60
Nodes (4): test_changelog_captures_ip_status_change(), test_changelog_records_crud(), test_changelog_scoped_filters(), AsyncClient

### Community 84 - "Workbook Parsing"
Cohesion: 0.29
Nodes (4): _col_class(), _positional_columns(), Dominant content class of a column sample., Headerless sheet: locate the IP column, then assign the remaining canonical…

### Community 30 - "Frontend Package Config"
Cohesion: 0.08
Nodes (22): name, private, version, autoprefixer, clsx, postcss, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+14 more)

### Community 31 - "NPM Dependencies"
Cohesion: 0.10
Nodes (21): dependencies, class-variance-authority, clsx, lucide-react, next, @radix-ui/react-dialog, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+13 more)

### Community 34 - "TypeScript Config"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 38 - "Project Documentation"
Cohesion: 0.12
Nodes (18): Architecture, Configuration, Development, IpamBox, License, Operations, Pages, Quick start (+10 more)

### Community 58 - "Dev Dependencies"
Cohesion: 0.25
Nodes (8): devDependencies, autoprefixer, postcss, tailwindcss, @types/node, @types/react, @types/react-dom, typescript

### Community 65 - "Docs & Security Policy"
Cohesion: 0.33
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 68 - "Backup Docs"
Cohesion: 0.40
Nodes (5): Backup file format, Backup & Restore, Restore, Take a backup, backupdata volume (/backups)

### Community 69 - "NPM Scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 70 - "README Features"
Cohesion: 0.50
Nodes (4): Features, IPAM, Platform, Scanner

### Community 41 - "Python Dependencies"
Cohesion: 0.15
Nodes (16): alembic==1.14.0, fastapi==0.115.6, httpx==0.28.1, openpyxl==3.1.5, pydantic==2.10.3, pydantic-settings==2.6.1, pytest==8.3.4, pytest-asyncio==0.25.0 (+8 more)

### Community 52 - "Infrastructure Docs"
Cohesion: 0.24
Nodes (10): arq==0.26.1, asyncpg==0.30.0, psutil==6.1.0, redis==5.2.0 (Python client), scapy==2.6.1, sqlalchemy[asyncio]==2.0.36, scanner service (ARQ worker, network_mode: host, NET_ADMIN/NET_RAW), Discovery Inbox and drift reconciliation (+2 more)

### Community 57 - "Docker Services"
Cohesion: 0.32
Nodes (8): db service (postgres:16-alpine), pgdata volume, redis service (redis:7-alpine, appendonly), redisdata volume, Site -> VRF -> Prefix -> IP address hierarchy, Atomic next-available-IP allocation (SELECT FOR UPDATE + UNIQUE), PostgreSQL GiST exclusion constraint for CIDR overlap safety, Loopback-only Postgres/Redis binding (not exposed to LAN)

### Community 59 - "Compose Services"
Cohesion: 0.36
Nodes (8): scanner — Network Scan Worker Service, api — FastAPI Backend Service, web — Next.js Frontend Service, db — PostgreSQL 16 Database Service, redis — Redis 7 Queue/Cache Service, backupdata Volume, redisdata Volume, pgdata Volume

## Knowledge Gaps
- **169 isolated node(s):** `Row`, `SortKey`, `CellState`, `Counts`, `CheckboxProps` (+164 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 530 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `IPAddress` connect `Addresses API` to `Sites API`, `Changelog & Data Models`, `Prefixes API`, `Entity Models & IPAM`, `Changelog & Dashboard API`, `Scans API`, `Ranges API`, `Redis & Runtime Settings`, `Scanner & OUI Lookup`, `Scan VRF Inference`, `Ranges API`, `Prefix Math`, `IP & Site Models`, `Workbook Normalization`, `Backup API`, `Sites API`, `IPAM Extras Tests`, `Changelog Flush Hooks`, `Discovery API`, `IPAM Service Layer`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Why does `User` connect `Auth API` to `Backup API`, `Auth Dependency Guard`, `Backup File Management`, `Changelog & Data Models`, `Workbook Import API`, `Backup API`, `Addresses API`, `Entity Models & IPAM`, `Changelog & Dashboard API`, `Changelog Flush Hooks`, `Backup API`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Why does `Site` connect `Sites API` to `IP & Site Models`, `Changelog & Data Models`, `Prefixes API`, `Entity Models & IPAM`, `Workbook Import Planner`, `Changelog Flush Hooks`, `VLANs API`, `IPAM Service Layer`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `User` (e.g. with `bulk_addresses()` and `change_password()`) actually correct?**
  _`User` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `IPAddress` (e.g. with `bulk_addresses()` and `create_address()`) actually correct?**
  _`IPAddress` has 19 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Row`, `SortKey`, `CellState` to the rest of the system?**
  _169 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `IPAM Frontend Pages` be split into smaller, more focused modules?**
  _Cohesion score 0.0654490106544901 - nodes in this community are weakly interconnected._