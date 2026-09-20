# Graph Report - IpamBox  (2026-09-20)

## Corpus Check
- 254 files · ~99,999 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1921 nodes · 5058 edges · 137 communities (73 shown, 44 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 336 edges (avg confidence: 0.94)
- Token cost: 5,200 input · 3,400 output

## Community Hubs (Navigation)
- Server Page Wrappers
- Prefix Detail & Subnet Grid
- Circuit Schemas
- Backup Tests
- Workbook Normalizer
- Import Planner
- Settings Client Pages
- App Entry & Asset Model
- Backup Serialize/Restore
- Dashboard & Status Badges
- Dashboard & Status Badges
- Scanner VRF Tests
- Route Error Boundaries
- Prefix Tree Page
- Auth Guards & LAN Info
- Auth API
- README Documentation
- Changelog & Dashboard API
- Runtime Settings
- App Shell & Root Layout
- VLAN API
- Scans API
- App Shell & Root Layout
- Import API
- Changelog & Dashboard API
- Prefix API
- Tags API
- Settings Client Pages
- package.json Metadata
- Entity Client Pages
- IPAM Tree Builder
- Redis & Auth Security
- Site Planner Tests
- Addresses API
- Backup API
- Sites API
- Site Sheet Parser
- Scanner & OUI Lookup
- Range CRUD Helpers
- Import Executor
- Frontend Dependencies
- Maintenance API
- Search API
- Prefix & VRF Models
- Search API
- Entity Parsers & Tests
- Import Wizard UI
- tsconfig Options
- Entity CRUD Routers
- VRF API
- Users API
- Settings Tests
- Changelog Hooks
- Scan Metrics & Tests
- Sites Master Parser
- Sheet Classifier
- Search Tests
- Test Fixtures
- IPAM Extras Tests
- Normalizer Tests
- Entity CRUD Routers
- Prefix API Tests
- App Shell & Root Layout
- Workbook Reader
- Redis & Auth Security
- Docker Compose Stack
- Frontend Dev Dependencies
- Column Classifier
- Entity CRUD Tests
- Next Config
- Prefix Detail & Subnet Grid
- SSE Stream & CSV
- Python Dependencies
- Changelog Tests
- Alembic Env
- Scanner Service Config
- Route Page certificates
- Route Page changelog
- Route Page circuits
- Route Page discovery
- Route Page inventory
- Login Page
- Route Page prefix detail
- Route Page prefixes
- Route Page scans
- Route Page services
- Next Config
- Route Page backup
- Data Settings Page
- Route Page security
- Import Wizard UI
- Route Page setup
- Route Page sites
- Route Page tags
- Route Page vlans
- Server Page Wrappers
- Data Model Invariants
- Scanner Service Config
- Python Dependencies
- Python Dependencies
- Next Env Types
- Scanner Service Config
- Request Import
- Prefix Import
- Exception Import
- Python Dependencies
- Scanner Service Config
- Scanner Service Config
- App Icon
- Root Layout Node
- Python Dependencies
- README Doc
- Scanner Service Config
- Data Model Invariants
- Python Dependencies
- Python Dependencies
- Security Policy

## God Nodes (most connected - your core abstractions)
1. `react` - 88 edges
2. `User` - 54 edges
3. `cn()` - 53 edges
4. `get_or_404()` - 51 edges
5. `IPAMError` - 50 edges
6. `lucide-react` - 46 edges
7. `Base` - 43 edges
8. `_matrix()` - 39 edges
9. `IPAddress` - 37 edges
10. `_Planner` - 37 edges

## Surprising Connections (you probably didn't know these)
- `pydantic-settings 2.6.1` --semantically_similar_to--> `Hybrid settings model (.env defaults + runtime overrides in app_settings)`  [INFERRED] [semantically similar]
  backend/requirements.txt → README.md
- `create_prefix()` --calls--> `Prefix`  [EXTRACTED]
  backend/app/api/v1/prefixes.py → frontend/src/types/index.ts
- `openpyxl 3.1.5` --references--> `Excel workbook import wizard (detect, dry-run, commit)`  [INFERRED]
  backend/requirements.txt → README.md
- `CertificatesPage()` --calls--> `columnAriaSort()`  [EXTRACTED]
  app/certificates/certificates-client.tsx → components/sort-header.tsx
- `CircuitsPage()` --calls--> `columnAriaSort()`  [EXTRACTED]
  app/circuits/circuits-client.tsx → components/sort-header.tsx

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Shared Backup Subsystem** — docker_compose_api_service, docker_compose_scanner_service, docker_compose_backupdata_volume [EXTRACTED 1.00]
- **Healthcheck-Gated Startup Ordering** — docker_compose_db_service, docker_compose_redis_service, docker_compose_api_service, docker_compose_scanner_service, docker_compose_web_service [EXTRACTED 1.00]
- **Single Backend Image, Two Runtimes (api + scanner)** — docker_compose_api_service, docker_compose_scanner_service [EXTRACTED 1.00]
- **async FastAPI + SQLAlchemy + Postgres API stack** — backend_requirements_fastapi, backend_requirements_uvicorn, backend_requirements_sqlalchemy, backend_requirements_asyncpg, backend_requirements_pydantic [INFERRED 0.85]

## Communities (137 total, 44 thin omitted)

### Community 0 - "Server Page Wrappers"
Cohesion: 0.09
Nodes (49): CertificatesPage(), EMPTY, CircuitsPage(), EMPTY, AssetRow, EMPTY, InventoryPage(), PrefixesPage() (+41 more)

### Community 1 - "Prefix Detail & Subnet Grid"
Cohesion: 0.05
Nodes (49): BulkResp, IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, SplitPlan, toggleIn(), AddressList() (+41 more)

### Community 2 - "Circuit Schemas"
Cohesion: 0.05
Nodes (45): confirm_discovered(), ConfirmBody, list_discovered(), AsyncSession, BaseModel, get, post, Unconfirmed hosts found by scanners, pending admin review. (+37 more)

### Community 3 - "Backup Tests"
Cohesion: 0.10
Nodes (56): str, UserRole, _backup_bytes(), _envelope_bytes(), _mkusers(), Hand-craft a backup envelope (e.g. with a forged users table)., Guard: every ORM table must be backed up (or explicitly excluded). Adding a new…, Fresh-server scenario: the migration-seeded Global VRF is replaced by the… (+48 more)

### Community 4 - "Workbook Normalizer"
Cohesion: 0.08
Nodes (41): assemble_ip(), clean(), _clean_octets(), map_status(), mask_to_prefixlen(), network_of(), norm_header(), norm_mac() (+33 more)

### Community 5 - "Import Planner"
Cohesion: 0.10
Nodes (15): parse_sites_master_records(), _Planner, _preview(), (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Folded sheet title vs site name/code — word-boundary matching so 'int' doesn't…, Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new… (+7 more)

### Community 6 - "Settings Client Pages"
Cohesion: 0.10
Nodes (23): DataPage(), download(), fmtAgo(), SecurityPage(), ConfirmAction(), ROLES, STATUSES, SETTINGS_SECTIONS (+15 more)

### Community 7 - "App Entry & Asset Model"
Cohesion: 0.11
Nodes (23): healthz(), lifespan(), metrics(), get, Readiness probe: verifies DB + Redis connectivity., Prometheus-style text exposition of object + scan counters., readyz(), AppSetting (+15 more)

### Community 8 - "Backup Serialize/Restore"
Cohesion: 0.09
Nodes (38): backup_dir(), backup_filename(), BackupError, BackupPreview, BackupTable, delete_backup_file(), _fail_inflight_scans(), _from_json() (+30 more)

### Community 9 - "Dashboard & Status Badges"
Cohesion: 0.08
Nodes (23): ACTION_STYLES, DashboardPage(), metadata, metadata, SettingsPage(), expiryBadge(), Badge(), BadgeProps (+15 more)

### Community 10 - "Dashboard & Status Badges"
Cohesion: 0.07
Nodes (34): fmtEta(), ScansPage(), QuickScanDialog(), useScanStream(), DialogDescription, IpStatusBadge(), PrefixStatusBadge(), prefixVariant (+26 more)

### Community 11 - "Scanner VRF Tests"
Cohesion: 0.09
Nodes (30): AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), HostResult, infer_device_type(), Best-effort device classification; None when nothing matched., _global_vrf_id(), _infer_scan_vrf() (+22 more)

### Community 13 - "Prefix Tree Page"
Cohesion: 0.12
Nodes (28): metadata, ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), collectExpandableKeys(), flattenTree() (+20 more)

### Community 14 - "Auth Guards & LAN Info"
Cohesion: 0.10
Nodes (31): ArqRedis, AsyncSession, Request, Guard for every API route. Returns the User, or None in allow_insecure mode., require_auth(), get_arq_pool(), redis_settings_from_url(), set_actor() (+23 more)

### Community 15 - "Auth API"
Cohesion: 0.16
Nodes (30): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+22 more)

### Community 16 - "README Documentation"
Cohesion: 0.06
Nodes (30): bcrypt 4.3.0, Architecture, Backup file format, Backup & Restore, Configuration, Development, Extended entities (WAN circuits, certificates, inventory, service catalog), Features (+22 more)

### Community 17 - "Changelog & Dashboard API"
Cohesion: 0.13
Nodes (19): list_changelog(), AsyncSession, get, Workbook import endpoints: upload -> detect -> preview -> commit. The uploaded…, get_settings(), get_session(), AsyncSession, Dependency factory: 403 unless the caller's role grants `perm`. Stacks on top… (+11 more)

### Community 18 - "Runtime Settings"
Cohesion: 0.09
Nodes (20): psycopg2-style URL for alembic offline mode / scripts., Settings, Effective, _env_sourced(), Any, Exception, Runtime-editable settings: app_settings rows override env defaults. Each public…, True when the field's current value differs from its declared default. (+12 more)

### Community 19 - "App Shell & Root Layout"
Cohesion: 0.11
Nodes (23): BackupSettingsPage(), downloadUrl(), fmtSize(), SettingField(), SOURCE_STYLE, CommandPalette(), Icon, Item (+15 more)

### Community 20 - "VLAN API"
Cohesion: 0.16
Nodes (27): list_items(), _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans() (+19 more)

### Community 21 - "Scans API"
Cohesion: 0.14
Nodes (26): cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession, get (+18 more)

### Community 22 - "App Shell & Root Layout"
Cohesion: 0.10
Nodes (23): AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS, NavGroup, NavItem, NavLink(), Sheet (+15 more)

### Community 23 - "Import API"
Cohesion: 0.13
Nodes (26): commit_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession, get (+18 more)

### Community 24 - "Changelog & Dashboard API"
Cohesion: 0.14
Nodes (25): _build_out(), _lan_info(), _mask_url(), AsyncSession, get, Hide the password in a scheme://user:pass@host URL., LAN identity detected by the host-networked worker (written to Redis). Falls…, read_settings() (+17 more)

### Community 25 - "Prefix API"
Cohesion: 0.16
Nodes (23): AllocateIPRequest, allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses() (+15 more)

### Community 26 - "Tags API"
Cohesion: 0.17
Nodes (20): assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession, delete (+12 more)

### Community 27 - "Settings Client Pages"
Cohesion: 0.13
Nodes (13): FEATURES, FeaturesPage(), Key, metadata, metadata, Key, ScanningPage(), Button (+5 more)

### Community 28 - "package.json Metadata"
Cohesion: 0.08
Nodes (23): name, private, scripts, build, dev, lint, start, version (+15 more)

### Community 29 - "Entity Client Pages"
Cohesion: 0.16
Nodes (20): ACTION_STYLES, ChangeSummary(), fmt(), DropdownMenuCheckboxItem, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator (+12 more)

### Community 30 - "IPAM Tree Builder"
Cohesion: 0.14
Nodes (22): AsyncSession, get, stats(), build_tree(), site_node(), vrf_node(), vrf_prefix_tree(), prefix_node() (+14 more)

### Community 31 - "Redis & Auth Security"
Cohesion: 0.16
Nodes (23): get_redis(), clear_login_failures(), create_session(), destroy_other_sessions(), destroy_session(), destroy_session_by_suffix(), env_password(), _fails_key() (+15 more)

### Community 32 - "Site Planner Tests"
Cohesion: 0.18
Nodes (12): _master_row(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind…, Mashapan TA + MATPASH share number 200 — merge + conflict, not a silent… (+4 more)

### Community 33 - "Addresses API"
Cohesion: 0.16
Nodes (22): bulk_addresses(), BulkBody, create_address(), delete_address(), export_addresses(), get_address(), import_addresses(), ImportRow (+14 more)

### Community 34 - "Backup API"
Cohesion: 0.15
Nodes (20): delete_scheduled_backup(), download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, delete, get, post (+12 more)

### Community 35 - "Sites API"
Cohesion: 0.15
Nodes (20): _cascade_site_fields(), create_site(), delete_site(), get_site(), list_sites(), AsyncSession, delete, get (+12 more)

### Community 36 - "Site Sheet Parser"
Cohesion: 0.15
Nodes (12): _blocks(), parse_site_sheet(), Split duplicated column groups (031-style runaway): each block starts at an…, _matrix(), קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf., Bare 'Name' (Cellular) maps to the hostname field. (+4 more)

### Community 37 - "Scanner & OUI Lookup"
Cohesion: 0.14
Nodes (18): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), _icmp_sweep(), _ptr_lookup(), Exception, Raised inside the pipeline when the user cancels the scan. (+10 more)

### Community 38 - "Range CRUD Helpers"
Cohesion: 0.17
Nodes (19): _crud_router(), delete_item(), get_item(), update_item(), delete_import(), delete, Delete a draft/failed batch and its stored file. Committed batches are history…, _check_range_overlap() (+11 more)

### Community 39 - "Import Executor"
Cohesion: 0.15
Nodes (16): Asset, SW/HW catalog rows (תוכנות וחומרות) and serial-number inventory…, VLAN, commit_batch(), execute_plan(), _get_or_create_prefix(), _get_or_create_site(), _get_or_create_vlan() (+8 more)

### Community 40 - "Frontend Dependencies"
Cohesion: 0.10
Nodes (21): dependencies, class-variance-authority, clsx, lucide-react, next, @radix-ui/react-dialog, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+13 more)

### Community 41 - "Maintenance API"
Cohesion: 0.21
Nodes (19): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+11 more)

### Community 42 - "Search API"
Cohesion: 0.27
Nodes (17): _folded(), AsyncSession, get, search(), match(), BaseModel, SearchAddress, SearchAsset (+9 more)

### Community 43 - "Prefix & VRF Models"
Cohesion: 0.23
Nodes (14): Prefix, PrefixStatus, str, Site, VRF, main(), Seed sample data: a Site, the Global VRF, and the auto-detected LAN prefix. Run…, build_import_plan() (+6 more)

### Community 44 - "Search API"
Cohesion: 0.21
Nodes (18): children(), lowest_free(), parent_chain(), Inclusive [first, last] integer range of host-usable addresses., True when network/broadcast addresses are unusable for hosts (IPv4 <= /30)., Lowest usable address integer not in `taken` or any excluded range., Split `net` into children of `new_prefix` length., The smallest candidate network that strictly contains `net`. (+10 more)

### Community 45 - "Entity Parsers & Tests"
Cohesion: 0.13
Nodes (14): excel_date(), datetime/date passthrough; int/float serial (20000-80000) -> date; 'd/m/yy'…, parse_assets(), parse_certificates(), Positional 5-col layout: platform, target/VS, server, cert, expiry., 003 תוכנות וחומרות: סוג,חברה,דגם,שם התוכנה,ייעוד,גירסה,EOL,…, Workbook import: normalizer/parser unit tests (no DB) + API e2e., Small synthetic workbook: sites master + one site sheet + circuits. (+6 more)

### Community 46 - "Import Wizard UI"
Cohesion: 0.11
Nodes (13): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, Step (+5 more)

### Community 47 - "tsconfig Options"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 48 - "Entity CRUD Routers"
Cohesion: 0.21
Nodes (13): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, AssetKind, str, Service catalog row from the שירותים sheet., Service, AssetCreate, AssetOut, AssetUpdate (+5 more)

### Community 49 - "VRF API"
Cohesion: 0.20
Nodes (14): create_vrf(), delete_vrf(), get_vrf(), list_vrfs(), AsyncSession, delete, get, post (+6 more)

### Community 50 - "Users API"
Cohesion: 0.24
Nodes (16): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+8 more)

### Community 51 - "Settings Tests"
Cohesion: 0.19
Nodes (13): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_files_report_effective_schedule(), test_internal_keys_hidden() (+5 more)

### Community 52 - "Changelog Hooks"
Cohesion: 0.27
Nodes (13): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), Audit trail via session flush hooks. before_flush collects (object, action,…, register(), _repr() (+5 more)

### Community 53 - "Scan Metrics & Tests"
Cohesion: 0.20
Nodes (11): IPAddress, fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_now_enqueues() (+3 more)

### Community 54 - "Sites Master Parser"
Cohesion: 0.19
Nodes (8): _master_blocks(), parse_sites_master(), (first, second) octet pairs a master row declares — lets sheet->site matching…, Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins., TestSitesMasterParser

### Community 55 - "Sheet Classifier"
Cohesion: 0.24
Nodes (6): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, TestClassify

### Community 56 - "Search Tests"
Cohesion: 0.35
Nodes (11): AsyncClient, auth_on(), _seed(), test_addresses_q_filter_not_broken(), test_search_empty_query(), test_search_grouped_results(), test_search_hebrew_folding(), test_search_ip_jump() (+3 more)

### Community 57 - "Test Fixtures"
Cohesion: 0.30
Nodes (10): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., sf() (+2 more)

### Community 58 - "IPAM Extras Tests"
Cohesion: 0.36
Nodes (11): _prefix(), test_address_role_nat_and_bulk(), test_bulk_reports_real_counts(), test_container_move_with_children_rejected(), test_csv_export_import(), test_dashboard_attention_fields(), test_ip_ranges_exclude_allocator(), test_prefix_move_vrf() (+3 more)

### Community 60 - "Entity CRUD Routers"
Cohesion: 0.36
Nodes (7): CertificateCreate, CertificateOut, CertificateUpdate, BaseModel, DashboardStats, MacMismatchItem, BaseModel

### Community 61 - "Prefix API Tests"
Cohesion: 0.42
Nodes (8): _global_vrf_id(), test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_prefixes_order_by_utilization_and_limit(), test_same_cidr_allowed_across_vrfs(), test_split_endpoint(), test_tree_endpoint(), test_unknown_vlan_rejected()

### Community 62 - "App Shell & Root Layout"
Cohesion: 0.28
Nodes (6): metadata, PrefsInit(), TooltipProvider, applyPrefs(), resolveTheme(), useApplyPrefs()

### Community 63 - "Workbook Reader"
Cohesion: 0.36
Nodes (5): Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, load_workbook_bytes(), XLSX -> sheet matrices via openpyxl (read_only streams, values only)., Parse workbook bytes into per-sheet row matrices. read_only + data_only:…, SheetMatrix

### Community 64 - "Redis & Auth Security"
Cohesion: 0.32
Nodes (7): auth_on(), AsyncClient, fixture, Turn auth on for a test, restore insecure mode after, and flush session/lockout…, test_endpoints_require_auth(), test_login_lockout(), test_setup_login_flow()

### Community 65 - "Docker Compose Stack"
Cohesion: 0.36
Nodes (8): api — FastAPI Backend Service, backupdata Volume, db — PostgreSQL 16 Database Service, pgdata Volume, redis — Redis 7 Queue/Cache Service, redisdata Volume, scanner — Network Scan Worker Service, web — Next.js Frontend Service

### Community 66 - "Frontend Dev Dependencies"
Cohesion: 0.25
Nodes (8): devDependencies, autoprefixer, postcss, tailwindcss, @types/node, @types/react, @types/react-dom, typescript

### Community 67 - "Column Classifier"
Cohesion: 0.29
Nodes (4): _col_class(), _positional_columns(), Dominant content class of a column sample., Headerless sheet: locate the IP column, then assign the remaining canonical…

### Community 69 - "Next Config"
Cohesion: 0.33
Nodes (3): nextConfig, metadata, next

### Community 70 - "Prefix Detail & Subnet Grid"
Cohesion: 0.40
Nodes (3): Separator, Skeleton(), @radix-ui/react-separator

### Community 71 - "SSE Stream & CSV"
Cohesion: 0.40
Nodes (4): csv_response(), parse_csv(), CSV text -> list of row dicts (header-named, stripped)., StreamingResponse

### Community 72 - "Python Dependencies"
Cohesion: 0.40
Nodes (5): fastapi 0.115.6, pydantic 2.10.3, pydantic-settings 2.6.1, uvicorn[standard] 0.32.1, Hybrid settings model (.env defaults + runtime overrides in app_settings)

### Community 73 - "Changelog Tests"
Cohesion: 0.60
Nodes (4): AsyncClient, test_changelog_captures_ip_status_change(), test_changelog_records_crud(), test_changelog_scoped_filters()

### Community 87 - "Scanner Service Config"
Cohesion: 0.67
Nodes (3): alembic 1.14.0, asyncpg 0.30.0, sqlalchemy[asyncio] 2.0.36

### Community 108 - "Data Model Invariants"
Cohesion: 1.00
Nodes (3): Atomic next-available-IP allocation (SELECT FOR UPDATE + UNIQUE), PostgreSQL GiST exclusion constraint for CIDR overlap safety, Site -> VRF -> Prefix -> IP address hierarchy

## Knowledge Gaps
- **223 isolated node(s):** `AssetRow`, `PrefixRow`, `ServiceRow`, `VlanRow`, `Crumb` (+218 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 662 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **44 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `create_prefix()` connect `Prefix API` to `Prefix Detail & Subnet Grid`, `Range CRUD Helpers`?**
  _High betweenness centrality (0.363) - this node is a cross-community bridge._
- **Why does `Prefix` connect `Prefix Detail & Subnet Grid` to `Server Page Wrappers`, `Prefix API`, `Dashboard & Status Badges`, `Dashboard & Status Badges`?**
  _High betweenness centrality (0.362) - this node is a cross-community bridge._
- **Why does `get_or_404()` connect `Range CRUD Helpers` to `Addresses API`, `Circuit Schemas`, `Sites API`, `Entity CRUD Routers`, `VRF API`, `Changelog & Dashboard API`, `VLAN API`, `Scans API`, `Import API`, `Prefix API`, `Tags API`, `IPAM Tree Builder`?**
  _High betweenness centrality (0.165) - this node is a cross-community bridge._
- **Are the 29 inferred relationships involving `User` (e.g. with `me()` and `change_password()`) actually correct?**
  _`User` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Are the 35 inferred relationships involving `IPAMError` (e.g. with `create_address()` and `delete_address()`) actually correct?**
  _`IPAMError` has 35 INFERRED edges - model-reasoned connections that need verification._
- **What connects `AssetRow`, `PrefixRow`, `ServiceRow` to the rest of the system?**
  _223 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Server Page Wrappers` be split into smaller, more focused modules?**
  _Cohesion score 0.09170471841704718 - nodes in this community are weakly interconnected._