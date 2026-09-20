# Graph Report - IpamBox  (2026-09-20)

## Corpus Check
- 262 files · ~225,758 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: (none) 7, .ini 2, .example 1)

## Summary
- 1951 nodes · 5321 edges · 122 communities (79 shown, 23 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 333 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Certificates & Changelog UI
- App Routes & Next Config
- Prefix Detail Page
- Backup Tests
- IPAM Schemas & Enums
- Discovery & Scans UI
- Import Wizard UI
- Workbook Normalization
- Import Planner
- CRUD Router Factory
- Global Search API
- Dashboard & Features UI
- App Entry & Settings Model
- IPAM Business Logic
- Prefix Tree Page
- Route Error Boundaries
- DB Config & Migrations
- Import API
- Changelog & Dashboard API
- Auth API
- Changelog Page
- Prefixes API
- Settings Config
- Settings UI Pages
- Tags API
- Maintenance API
- Scanner & OUI
- App Shell & Nav
- VLANs API
- Scans API
- Scanner VRF & Tests
- Import Test Fixtures
- Addresses API
- Sessions & Security Core
- Site Sheet Parsing
- Print Report & Pages
- Backup API
- Settings API
- Worker & Audit Actor
- NPM Dependencies
- Asset & Cert Sheet Parsing
- Backup Service
- TypeScript Config
- IPAddress & Reconcile
- Package Manifest
- Users API
- Entity Schemas
- Settings Tests
- Entities API & Schemas
- Master Sheet Parsing
- Backup File Ops
- Sheet Classification
- Search Tests
- Changelog Engine
- Test Fixtures
- IPAM API Tests
- Normalize Tests
- Allocation Logic & Tests
- Loading & Breadcrumbs
- Discovery API
- Prefix API Tests
- Dashboard Page
- Root Layout & Prefs
- VRF Schemas
- Workbook Reader
- Docker Compose Services
- Dev Dependencies
- Column Classification
- UI Primitives
- Tree Client Internals
- Reconcile & MAC Tests
- Entity CRUD Tests
- Health Probes
- CSV Export
- Changelog Tests
- Shortcuts Overlay
- NPM Scripts
- Security Policy Doc
- Security Settings UI
- Changelog Schemas
- Python Web Deps
- Python DB Deps
- Queue Deps
- Test Deps
- Next Env Types
- Tailwind Config
- Request Type
- Prefix Schema
- Exception Type
- bcrypt Dep
- httpx Dep
- openpyxl Dep
- psutil Dep
- scapy Dep
- App Icon
- Root Layout Meta
- Backup Tables Registry
- Env Example
- Repository Link
- MIT License
- Seeding Service
- Security Doc Meta

## God Nodes (most connected - your core abstractions)
1. `react` - 88 edges
2. `User` - 54 edges
3. `cn()` - 53 edges
4. `get_or_404()` - 51 edges
5. `IPAMError` - 50 edges
6. `lucide-react` - 46 edges
7. `Base` - 43 edges
8. `_matrix()` - 39 edges
9. `_Planner` - 37 edges
10. `IPAddress` - 37 edges

## Surprising Connections (you probably didn't know these)
- `Prefix` --calls--> `create_prefix()`  [EXTRACTED]
  frontend/src/types/index.ts → backend/app/api/v1/prefixes.py
- `PrefixesPage()` --calls--> `useTags()`  [EXTRACTED]
  app/prefixes/prefixes-client.tsx → components/tag-picker.tsx
- `SitesPage()` --calls--> `usePrefs()`  [EXTRACTED]
  app/sites/sites-client.tsx → lib/prefs.ts
- `VrfsPage()` --calls--> `useRowNav()`  [EXTRACTED]
  app/vrfs/vrfs-client.tsx → lib/row-nav.ts
- `PrefixDetailPage()` --calls--> `usePrefs()`  [EXTRACTED]
  app/prefixes/[id]/prefix-detail-client.tsx → lib/prefs.ts

## Import Cycles
- None detected.

## Communities (122 total, 23 thin omitted)

### Community 0 - "Certificates & Changelog UI"
Cohesion: 0.09
Nodes (64): CertificatesPage(), EMPTY, ACTION_STYLES, ChangeSummary(), fmt(), CircuitsPage(), EMPTY, AssetRow (+56 more)

### Community 1 - "App Routes & Next Config"
Cohesion: 0.04
Nodes (23): nextConfig, metadata, metadata, metadata, metadata, metadata, metadata, metadata (+15 more)

### Community 2 - "Prefix Detail Page"
Cohesion: 0.05
Nodes (49): IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, SplitPlan, toggleIn(), AddressList(), AddrMapViewSwitcher() (+41 more)

### Community 3 - "Backup Tests"
Cohesion: 0.10
Nodes (56): str, UserRole, _backup_bytes(), _envelope_bytes(), _mkusers(), Hand-craft a backup envelope (e.g. with a forged users table)., Guard: every ORM table must be backed up (or explicitly excluded). Adding a new…, Fresh-server scenario: the migration-seeded Global VRF is replaced by the… (+48 more)

### Community 4 - "IPAM Schemas & Enums"
Cohesion: 0.06
Nodes (37): IPRole, str, IPRangeRole, str, PrefixStatus, str, CircuitCreate, CircuitOut (+29 more)

### Community 5 - "Discovery & Scans UI"
Cohesion: 0.09
Nodes (31): BulkResp, fmtEta(), ScansPage(), DataPage(), download(), ConfirmAction(), ConfirmDialog(), ROLES (+23 more)

### Community 6 - "Import Wizard UI"
Cohesion: 0.05
Nodes (42): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, Step (+34 more)

### Community 7 - "Workbook Normalization"
Cohesion: 0.08
Nodes (41): assemble_ip(), clean(), _clean_octets(), map_status(), mask_to_prefixlen(), network_of(), norm_header(), norm_mac() (+33 more)

### Community 8 - "Import Planner"
Cohesion: 0.10
Nodes (15): parse_sites_master_records(), _Planner, _preview(), (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Folded sheet title vs site name/code — word-boundary matching so 'int' doesn't…, Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new… (+7 more)

### Community 9 - "CRUD Router Factory"
Cohesion: 0.08
Nodes (40): _crud_router(), delete_item(), get_item(), list_items(), update_item(), _check_range_overlap(), create_range(), delete_range() (+32 more)

### Community 10 - "Global Search API"
Cohesion: 0.12
Nodes (35): _folded(), AsyncSession, get, search(), match(), BaseModel, SearchAddress, SearchAsset (+27 more)

### Community 11 - "Dashboard & Features UI"
Cohesion: 0.10
Nodes (22): ACTION_STYLES, FEATURES, FeaturesPage(), Key, metadata, metadata, metadata, Key (+14 more)

### Community 12 - "App Entry & Settings Model"
Cohesion: 0.15
Nodes (16): AppSetting, Runtime-editable setting override. Absent row -> env var -> default., Asset, SW/HW catalog rows (תוכנות וחומרות) and serial-number inventory…, Base, Certificate, Certificate-expiry row from the תוקף תעודות sheet., Circuit (+8 more)

### Community 13 - "IPAM Business Logic"
Cohesion: 0.10
Nodes (30): _cascade_site_fields(), Propagate site code/number/name changes to linked entities that were following…, metrics(), Prometheus-style text exposition of object + scan counters., IPRange, A named block of addresses inside a prefix (e.g. a DHCP scope). Any defined…, Prefix, Service catalog row from the שירותים sheet. (+22 more)

### Community 14 - "Prefix Tree Page"
Cohesion: 0.10
Nodes (31): metadata, ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), collectExpandableKeys(), flattenTree() (+23 more)

### Community 16 - "DB Config & Migrations"
Cohesion: 0.08
Nodes (30): ArqRedis, do_run_migrations(), run_migrations_online(), get_settings(), AsyncSession, Request, Guard for every API route. Returns the User, or None in allow_insecure mode., require_auth() (+22 more)

### Community 17 - "Import API"
Cohesion: 0.12
Nodes (33): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+25 more)

### Community 18 - "Changelog & Dashboard API"
Cohesion: 0.13
Nodes (23): list_changelog(), AsyncSession, get, AsyncSession, get, stats(), create_site(), post (+15 more)

### Community 19 - "Auth API"
Cohesion: 0.16
Nodes (31): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+23 more)

### Community 20 - "Changelog Page"
Cohesion: 0.11
Nodes (25): ACTION_STYLES, ChangelogPage(), ChangeSummary(), fmt(), metadata, DropdownMenuCheckboxItem, DropdownMenuContent, DropdownMenuItem (+17 more)

### Community 21 - "Prefixes API"
Cohesion: 0.13
Nodes (29): AllocateIPRequest, allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses() (+21 more)

### Community 22 - "Settings Config"
Cohesion: 0.09
Nodes (20): psycopg2-style URL for alembic offline mode / scripts., Settings, Effective, _env_sourced(), Any, Exception, Runtime-editable settings: app_settings rows override env defaults. Each public…, True when the field's current value differs from its declared default. (+12 more)

### Community 23 - "Settings UI Pages"
Cohesion: 0.12
Nodes (22): BackupSettingsPage(), downloadUrl(), fmtSize(), SettingField(), SOURCE_STYLE, CommandPalette(), Icon, Item (+14 more)

### Community 24 - "Tags API"
Cohesion: 0.16
Nodes (22): assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession, delete (+14 more)

### Community 25 - "Maintenance API"
Cohesion: 0.15
Nodes (26): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+18 more)

### Community 26 - "Scanner & OUI"
Cohesion: 0.12
Nodes (23): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), detect_interface(), HostResult, _icmp_sweep(), infer_device_type() (+15 more)

### Community 27 - "App Shell & Nav"
Cohesion: 0.10
Nodes (23): AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS, NavGroup, NavItem, NavLink() (+15 more)

### Community 28 - "VLANs API"
Cohesion: 0.19
Nodes (24): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+16 more)

### Community 29 - "Scans API"
Cohesion: 0.17
Nodes (23): cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession, get (+15 more)

### Community 30 - "Scanner VRF & Tests"
Cohesion: 0.15
Nodes (17): _infer_scan_vrf(), Pick the VRF for a scan that didn't specify one. An exact-match prefix living…, _scan_vrf(), _extra_vrf(), fake_arq(), _pool(), _FakeArqJob, _FakePool (+9 more)

### Community 31 - "Import Test Fixtures"
Cohesion: 0.18
Nodes (12): _master_row(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind…, Mashapan TA + MATPASH share number 200 — merge + conflict, not a silent… (+4 more)

### Community 32 - "Addresses API"
Cohesion: 0.16
Nodes (22): bulk_addresses(), BulkBody, create_address(), delete_address(), export_addresses(), get_address(), import_addresses(), ImportRow (+14 more)

### Community 33 - "Sessions & Security Core"
Cohesion: 0.17
Nodes (22): get_redis(), clear_login_failures(), create_session(), destroy_other_sessions(), destroy_session(), destroy_session_by_suffix(), _fails_key(), get_session_user_id() (+14 more)

### Community 34 - "Site Sheet Parsing"
Cohesion: 0.15
Nodes (12): _blocks(), parse_site_sheet(), Split duplicated column groups (031-style runaway): each block starts at an…, _matrix(), קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf., Bare 'Name' (Cellular) maps to the hostname field. (+4 more)

### Community 35 - "Print Report & Pages"
Cohesion: 0.12
Nodes (19): metadata, PrintClient(), TagsPage(), VrfsPage(), IpDrawer(), AddrMapView, applyPrefs(), DEFAULT_PREFS (+11 more)

### Community 36 - "Backup API"
Cohesion: 0.16
Nodes (20): download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, get, post, Request, Restore a backup file (raw .json.gz body). Wipes every data table (users are… (+12 more)

### Community 37 - "Settings API"
Cohesion: 0.18
Nodes (20): _build_out(), _lan_info(), _mask_url(), AsyncSession, get, Hide the password in a scheme://user:pass@host URL., LAN identity detected by the host-networked worker (written to Redis). Falls…, read_settings() (+12 more)

### Community 38 - "Worker & Audit Actor"
Cohesion: 0.17
Nodes (21): set_actor(), get_effective(), _due(), _eta_seconds(), _global_vrf_id(), _publish(), datetime, Prefix (+13 more)

### Community 39 - "NPM Dependencies"
Cohesion: 0.10
Nodes (21): dependencies, class-variance-authority, clsx, lucide-react, next, @radix-ui/react-dialog, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+13 more)

### Community 40 - "Asset & Cert Sheet Parsing"
Cohesion: 0.13
Nodes (14): excel_date(), datetime/date passthrough; int/float serial (20000-80000) -> date; 'd/m/yy'…, parse_assets(), parse_certificates(), Positional 5-col layout: platform, target/VS, server, cert, expiry., 003 תוכנות וחומרות: סוג,חברה,דגם,שם התוכנה,ייעוד,גירסה,EOL,…, Workbook import: normalizer/parser unit tests (no DB) + API e2e., Small synthetic workbook: sites master + one site sheet + circuits. (+6 more)

### Community 41 - "Backup Service"
Cohesion: 0.13
Nodes (19): _alembic_revisions(), BackupError, BackupPreview, build_backup(), _from_json(), _gunzip(), inspect_backup(), Any (+11 more)

### Community 42 - "TypeScript Config"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 43 - "IPAddress & Reconcile"
Cohesion: 0.19
Nodes (13): IPAddress, IPStatus, _insert_address(), fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient (+5 more)

### Community 44 - "Package Manifest"
Cohesion: 0.12
Nodes (16): name, private, version, autoprefixer, clsx, postcss, @radix-ui/react-dialog, @radix-ui/react-separator (+8 more)

### Community 45 - "Users API"
Cohesion: 0.24
Nodes (15): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+7 more)

### Community 46 - "Entity Schemas"
Cohesion: 0.20
Nodes (12): CertificateCreate, CertificateOut, CertificateUpdate, BaseModel, DashboardStats, MacMismatchItem, BaseModel, BaseModel (+4 more)

### Community 47 - "Settings Tests"
Cohesion: 0.20
Nodes (12): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_files_report_effective_schedule(), test_scan_guards_use_db_settings() (+4 more)

### Community 48 - "Entities API & Schemas"
Cohesion: 0.29
Nodes (11): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, AssetKind, str, AssetCreate, AssetOut, AssetUpdate, BaseModel, BaseModel (+3 more)

### Community 49 - "Master Sheet Parsing"
Cohesion: 0.19
Nodes (8): _master_blocks(), parse_sites_master(), (first, second) octet pairs a master row declares — lets sheet->site matching…, Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins., TestSitesMasterParser

### Community 50 - "Backup File Ops"
Cohesion: 0.23
Nodes (13): delete_scheduled_backup(), delete, backup_dir(), delete_backup_file(), list_backup_files(), prune_backups(), Path, Fetch a scheduled backup by file name (path-traversal safe). (+5 more)

### Community 51 - "Sheet Classification"
Cohesion: 0.24
Nodes (6): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, TestClassify

### Community 52 - "Search Tests"
Cohesion: 0.35
Nodes (11): AsyncClient, auth_on(), _seed(), test_addresses_q_filter_not_broken(), test_search_empty_query(), test_search_grouped_results(), test_search_hebrew_folding(), test_search_ip_jump() (+3 more)

### Community 53 - "Changelog Engine"
Cohesion: 0.35
Nodes (11): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), Audit trail via session flush hooks. before_flush collects (object, action,…, register(), _repr() (+3 more)

### Community 54 - "Test Fixtures"
Cohesion: 0.30
Nodes (10): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., sf() (+2 more)

### Community 55 - "IPAM API Tests"
Cohesion: 0.36
Nodes (11): _prefix(), test_address_role_nat_and_bulk(), test_bulk_reports_real_counts(), test_container_move_with_children_rejected(), test_csv_export_import(), test_dashboard_attention_fields(), test_ip_ranges_exclude_allocator(), test_prefix_move_vrf() (+3 more)

### Community 57 - "Allocation Logic & Tests"
Cohesion: 0.36
Nodes (9): IPStatus, reserve_next_available(), _mk_prefix(), test_address_crud_and_dup_guard(), test_allocation_skips_existing(), test_concurrent_allocation_unique(), alloc(), test_exhausted_prefix_conflicts() (+1 more)

### Community 58 - "Loading & Breadcrumbs"
Cohesion: 0.27
Nodes (5): Crumb, findChain(), PrefixBreadcrumbs(), Separator, Skeleton()

### Community 59 - "Discovery API"
Cohesion: 0.22
Nodes (9): confirm_discovered(), ConfirmBody, list_discovered(), AsyncSession, BaseModel, get, post, Unconfirmed hosts found by scanners, pending admin review. (+1 more)

### Community 60 - "Prefix API Tests"
Cohesion: 0.42
Nodes (8): _global_vrf_id(), test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_prefixes_order_by_utilization_and_limit(), test_same_cidr_allowed_across_vrfs(), test_split_endpoint(), test_tree_endpoint(), test_unknown_vlan_rejected()

### Community 61 - "Dashboard Page"
Cohesion: 0.25
Nodes (6): DashboardPage(), metadata, ChartTheme, FALLBACK, readTheme(), useChartTheme()

### Community 62 - "Root Layout & Prefs"
Cohesion: 0.28
Nodes (6): metadata, PrefsInit(), TooltipProvider, applyPrefs(), resolveTheme(), useApplyPrefs()

### Community 63 - "VRF Schemas"
Cohesion: 0.36
Nodes (5): BaseModel, field_validator, VRFCreate, VRFOut, VRFUpdate

### Community 64 - "Workbook Reader"
Cohesion: 0.36
Nodes (5): Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, load_workbook_bytes(), XLSX -> sheet matrices via openpyxl (read_only streams, values only)., Parse workbook bytes into per-sheet row matrices. read_only + data_only:…, SheetMatrix

### Community 65 - "Docker Compose Services"
Cohesion: 0.36
Nodes (8): api — FastAPI Backend Service, backupdata Volume, db — PostgreSQL 16 Database Service, pgdata Volume, redis — Redis 7 Queue/Cache Service, redisdata Volume, scanner — Network Scan Worker Service, web — Next.js Frontend Service

### Community 66 - "Dev Dependencies"
Cohesion: 0.25
Nodes (8): devDependencies, autoprefixer, postcss, tailwindcss, @types/node, @types/react, @types/react-dom, typescript

### Community 67 - "Column Classification"
Cohesion: 0.29
Nodes (4): _col_class(), _positional_columns(), Dominant content class of a column sample., Headerless sheet: locate the IP column, then assign the remaining canonical…

### Community 68 - "UI Primitives"
Cohesion: 0.38
Nodes (4): Button, ButtonProps, buttonVariants, @radix-ui/react-slot

### Community 69 - "Tree Client Internals"
Cohesion: 0.53
Nodes (5): ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText()

### Community 70 - "Reconcile & MAC Tests"
Cohesion: 0.33
Nodes (6): AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), A stored (e.g. imported) MAC that differs from the scan is flagged in…, test_reconcile_flags_mac_mismatch(), test_reconcile_persists_ports_and_type()

### Community 72 - "Health Probes"
Cohesion: 0.40
Nodes (5): healthz(), get, Readiness probe: verifies DB + Redis connectivity., readyz(), JSONResponse

### Community 73 - "CSV Export"
Cohesion: 0.40
Nodes (4): csv_response(), parse_csv(), CSV text -> list of row dicts (header-named, stripped)., StreamingResponse

### Community 74 - "Changelog Tests"
Cohesion: 0.60
Nodes (4): AsyncClient, test_changelog_captures_ip_status_change(), test_changelog_records_crud(), test_changelog_scoped_filters()

### Community 75 - "Shortcuts Overlay"
Cohesion: 0.40
Nodes (3): Group, GROUPS, ShortcutsOverlay()

### Community 76 - "NPM Scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 77 - "Security Policy Doc"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 78 - "Security Settings UI"
Cohesion: 0.67
Nodes (3): fmtAgo(), SecurityPage(), ROLE_META

### Community 79 - "Changelog Schemas"
Cohesion: 0.67
Nodes (3): ChangeField, ChangeLogOut, BaseModel

### Community 80 - "Python Web Deps"
Cohesion: 0.50
Nodes (4): fastapi 0.115.6, pydantic 2.10.3, pydantic-settings 2.6.1, uvicorn[standard] 0.32.1

### Community 93 - "Python DB Deps"
Cohesion: 0.67
Nodes (3): alembic 1.14.0, asyncpg 0.30.0, sqlalchemy[asyncio] 2.0.36

## Knowledge Gaps
- **217 isolated node(s):** `AssetRow`, `PrefixRow`, `ServiceRow`, `VlanRow`, `BulkResp` (+212 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 653 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `create_prefix()` connect `Prefixes API` to `CRUD Router Factory`, `Prefix Detail Page`?**
  _High betweenness centrality (0.409) - this node is a cross-community bridge._
- **Why does `Prefix` connect `Prefix Detail Page` to `Certificates & Changelog UI`, `Discovery & Scans UI`, `Import Wizard UI`, `Dashboard & Features UI`, `Prefixes API`?**
  _High betweenness centrality (0.408) - this node is a cross-community bridge._
- **Why does `get_or_404()` connect `CRUD Router Factory` to `Addresses API`, `Entities API & Schemas`, `Import API`, `Changelog & Dashboard API`, `Prefixes API`, `Tags API`, `Discovery API`, `VLANs API`, `Scans API`?**
  _High betweenness centrality (0.186) - this node is a cross-community bridge._
- **Are the 29 inferred relationships involving `User` (e.g. with `auth_status()` and `change_password()`) actually correct?**
  _`User` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Are the 35 inferred relationships involving `IPAMError` (e.g. with `create_address()` and `delete_address()`) actually correct?**
  _`IPAMError` has 35 INFERRED edges - model-reasoned connections that need verification._
- **What connects `AssetRow`, `PrefixRow`, `ServiceRow` to the rest of the system?**
  _217 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Certificates & Changelog UI` be split into smaller, more focused modules?**
  _Cohesion score 0.08648901355773726 - nodes in this community are weakly interconnected._