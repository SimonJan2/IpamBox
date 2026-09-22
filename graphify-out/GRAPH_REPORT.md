# Graph Report - IpamBox  (2026-09-22)

## Corpus Check
- 330 files · ~280,030 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: (none) 7, .csv 6, .ini 2)

## Summary
- 2935 nodes · 7639 edges · 190 communities (106 shown, 57 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 473 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Custom Lists API
- Frontend Pages & Config
- API Router & Core App
- Addresses API
- Prefixes API & Allocation
- Migrations, Backup & Changelog
- Generic CRUD Router
- Entity Client Components
- Workbook Entities API
- Circuits & Services Pages
- Certificates & Filter UI
- OUI Vendor Lookup
- Maintenance & Admin Tasks
- Address List Component
- Accounts & Roles Docs
- Frontend Type Definitions
- Demo Data Generator
- Root Package Dependencies
- Auth API
- Backup Tests
- Request Deps & Auth Guards
- Route Error Boundaries
- Prefs & Print Views
- Changelog & Discovery UI
- Scans & Data Settings UI
- Frontend Entity Pages
- VLANs API
- Import Planner
- Docs Section UI
- Import Value Normalizers
- Tags API
- Color Rules API
- Dashboard & Settings UI
- Ranges API
- Prefix Tree & Field UI
- Backup Service
- Scan VRF Inference
- Test Fakes & Fixtures
- Users API
- Scan Reconciliation
- Scan Worker Jobs
- Workbook Plan Tests
- Prefix Tree Page
- Sheet Header Parsers
- App Layout & Init
- Imports API
- Import Batch Model
- List Detail UI
- RBAC Tests
- Frontend Package Meta
- Frontend Dependencies
- Login & Settings Pages
- Row Ordering Tests
- Prefix Detail Page
- Color Rules Tests
- App Shell & Nav
- TypeScript Config
- Settings Tests
- List Import Tests
- List CRUD & Bulk Tests
- Docker Compose Stack
- Command Palette
- Site Sheet Parser
- Import Wizard UI
- Import Plan Execution
- Custom List Parser
- List Import Dialog
- Import Client Pages
- Sheet Classification
- Sites Master Parser
- Changelog Tests
- Search API Tests
- Color Rules UI
- Runtime Settings
- Scanner Delta Tests
- Import Plan Builder
- Test Fixtures (conftest)
- Fake ARQ/Redis Fixtures
- Normalizer Tests
- App Shell Nav (alt)
- Backup Restore API
- Prefix API Tests
- Sheet UI Primitive
- Settings Read & URL Mask
- App Settings Config
- Auth Test Fixtures
- Row Nav & Shortcuts
- Prefix Detail Client
- Color Rules UI (alt)
- Allocation Tests
- Frontend Dev Dependencies
- Scheduled Backups API
- Workbook Reader
- Scan Job Watchdog
- Inventory Page UI
- Expiry Badge & Flags
- Prefixes Page UI
- Tree Page Client
- Runtime Setting Spec
- Settings Patch API
- Entity Router Tests
- Tree Client (alt)
- VLANs Page UI
- Circuits Parser Tests
- Shortcuts Overlay
- Frontend npm Scripts
- Shortcuts Overlay (alt)
- Chart Theme Hook
- Status Tokens
- Security Policy Doc
- VRFs Page UI
- Backend Dependencies
- Changelog Page UI
- Inventory UI (alt)
- Backup Settings UI
- Features Settings UI
- DB Driver Deps
- Repo Docs
- Security Settings UI
- Queue Deps
- Test Deps
- Next.js Env Types
- Tailwind Config
- XFF Shim
- Next.js Config
- AllocateIPRequest Schema
- patch Symbol
- Request Symbol
- patch Symbol (2)
- SyncSession Symbol
- Base Symbol
- str Symbol
- field_validator Symbol
- datetime Symbol
- Exception Symbol
- datetime Symbol (2)
- Prefix Symbol
- ScanJob Symbol
- bcrypt Dep
- httpx Dep
- openpyxl Dep
- psutil Dep
- scapy Dep
- AsyncClient Symbol
- BaseModel Symbol
- CommitOptions Schema
- Demo Contacts CSV
- Demo Servers CSV
- Demo Site cp1255 CSV
- Demo Site UTF-8 CSV
- Demo VLANs CSV
- App Icon
- Root Layout Meta
- ip_addresses Table
- ImportBatch Symbol
- IPStatus Type
- PrefixCreate Schema
- PrefixOut Schema
- PrefixUpdate Schema
- BACKUP_TABLES Registry
- .env.example
- GitHub Repo Link
- MIT License

## God Nodes (most connected - your core abstractions)
1. `cn()` - 109 edges
2. `react` - 90 edges
3. `User` - 56 edges
4. `IPAMError` - 55 edges
5. `get_or_404()` - 50 edges
6. `lucide-react` - 49 edges
7. `IPAddress` - 48 edges
8. `api` - 46 edges
9. `get_settings()` - 42 edges
10. `UserRole` - 41 edges

## Surprising Connections (you probably didn't know these)
- `SavedViews()` --calls--> `usePrefs()`  [EXTRACTED]
  components/saved-views.tsx → lib/prefs.ts
- `upload_workbook()` --calls--> `ImportBatch`  [EXTRACTED]
  backend/app/api/v1/imports.py → frontend/src/types/index.ts
- `Site` --uses--> `create_prefix()`  [INFERRED]
  backend/app/models/site.py → backend/app/api/v1/prefixes.py
- `Site` --uses--> `_cascade_site_fields()`  [INFERRED]
  backend/app/models/site.py → backend/app/api/v1/sites.py
- `Site` --uses--> `create_site()`  [INFERRED]
  backend/app/models/site.py → backend/app/api/v1/sites.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Demo dataset suite** — examples_readme_demo_workbook, examples_readme_demo_workbook_en, examples_readme_demo_site_utf8, examples_readme_demo_site_cp1255, examples_readme_demo_addresses, examples_readme_demo_contacts, examples_readme_demo_vlans, examples_readme_demo_servers, examples_generate_demo_data [EXTRACTED 1.00]

## Communities (190 total, 57 thin omitted)

### Community 0 - "Custom Lists API"
Cohesion: 0.05
Nodes (84): bulk_rows(), _check_columns(), create_list(), create_row(), delete_list(), delete_row(), get_list(), list_lists() (+76 more)

### Community 1 - "Frontend Pages & Config"
Cohesion: 0.03
Nodes (33): nextConfig, metadata, ChangelogPage(), metadata, metadata, DashboardPage(), metadata, metadata (+25 more)

### Community 2 - "API Router & Core App"
Cohesion: 0.06
Nodes (54): _job_payload(), tag_assignments garbage collection. TagAssignment references its target…, healthz(), metrics(), get, Readiness probe: verifies DB + Redis connectivity., Prometheus-style text exposition of object + scan counters., readyz() (+46 more)

### Community 3 - "Addresses API"
Cohesion: 0.06
Nodes (62): _address_csv_row(), _addresses_stmt(), bulk_addresses(), BulkBody, create_address(), delete_address(), export_addresses(), get_address() (+54 more)

### Community 4 - "Prefixes API & Allocation"
Cohesion: 0.07
Nodes (67): allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), _prefix_rows() (+59 more)

### Community 5 - "Migrations, Backup & Changelog"
Cohesion: 0.06
Nodes (50): do_run_migrations(), run_migrations_online(), list_changelog(), AsyncSession, get, AsyncSession, get, stats() (+42 more)

### Community 6 - "Generic CRUD Router"
Cohesion: 0.07
Nodes (55): _crud_router(), delete_item(), get_item(), list_items(), reorder_items(), update_item(), _cascade_site_fields(), create_site() (+47 more)

### Community 7 - "Entity Client Components"
Cohesion: 0.12
Nodes (36): EMPTY, EMPTY, BulkResp, EMPTY, ServiceRow, VLAN_STATUSES, VlanRow, VrfDialog() (+28 more)

### Community 8 - "Workbook Entities API"
Cohesion: 0.06
Nodes (38): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, AssetKind, str, AssetCreate, AssetOut, AssetUpdate, BaseModel, field_validator (+30 more)

### Community 9 - "Circuits & Services Pages"
Cohesion: 0.11
Nodes (35): EMPTY, EMPTY, ServiceRow, TagsPage(), VLAN_STATUSES, VlanRow, VrfDialog(), vrfNameFor() (+27 more)

### Community 10 - "Certificates & Filter UI"
Cohesion: 0.08
Nodes (38): EMPTY, STATUSES, ACTION_STYLES, ChangeDiff(), ChangeVal(), HistoryEntry(), HistoryPanel(), summary() (+30 more)

### Community 11 - "OUI Vendor Lookup"
Cohesion: 0.06
Nodes (47): _lan_info(), LAN identity detected by the host-networked worker (written to Redis). Falls…, Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), detect_interface(), detect_local_cidr() (+39 more)

### Community 12 - "Maintenance & Admin Tasks"
Cohesion: 0.06
Nodes (46): ArqRedis, _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody (+38 more)

### Community 13 - "Address List Component"
Cohesion: 0.09
Nodes (38): AddressList(), AddrMapViewSwitcher(), buildRows(), IP_STATUSES, Row, sortAddr(), SortKey, InlineSelect() (+30 more)

### Community 14 - "Accounts & Roles Docs"
Cohesion: 0.14
Nodes (45): Accounts & Roles, Insecure mode (IPAMBOX_ALLOW_INSECURE), Four roles (Administrator, Operator, Contributor, Viewer), Session-cookie authentication, Address roles (vip/vrrp/hsrp/glbp/carp/secondary), Address CSV import/export, IP Addresses, IP drawer (+37 more)

### Community 15 - "Frontend Type Definitions"
Cohesion: 0.05
Nodes (43): AddressPage, BackupFileInfo, BackupFilesOut, BackupPreview, Certificate, ChangeField, ChangeLogEntry, Circuit (+35 more)

### Community 16 - "Demo Data Generator"
Cohesion: 0.13
Nodes (40): assets_rows(), _assign_site_sheets(), _assign_site_sheets_clean(), build_en_workbook(), build_mixed_workbook(), build_sites(), certificates_rows(), circuits_rows() (+32 more)

### Community 17 - "Root Package Dependencies"
Cohesion: 0.05
Nodes (41): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, lucide-react, next, @radix-ui/react-dialog (+33 more)

### Community 18 - "Auth API"
Cohesion: 0.16
Nodes (36): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+28 more)

### Community 19 - "Backup Tests"
Cohesion: 0.14
Nodes (36): delete_scheduled_backup(), delete, Base, User, _backup_bytes(), _envelope_bytes(), _mkusers(), Hand-craft a backup envelope (e.g. with a forged users table). (+28 more)

### Community 20 - "Request Deps & Auth Guards"
Cohesion: 0.09
Nodes (37): AsyncSession, Request, Guard for every API route. Returns the User, or None in allow_insecure mode., require_auth(), get_redis(), Shared process-wide Redis client. Do NOT aclose() it per call — connections…, clear_login_failures(), client_ip() (+29 more)

### Community 22 - "Prefs & Print Views"
Cohesion: 0.08
Nodes (32): CertificatesPage(), CircuitsPage(), metadata, PrintClient(), ServicesPage(), SitesPage(), TagsPage(), VlansPage() (+24 more)

### Community 23 - "Changelog & Discovery UI"
Cohesion: 0.12
Nodes (23): ACTION_STYLES, BulkResp, metadata, PrintClient(), PrefixesPage(), PrefixRow, utilColor(), IpStatusBadge() (+15 more)

### Community 24 - "Scans & Data Settings UI"
Cohesion: 0.10
Nodes (18): fmtEta(), ScansPage(), DataPage(), download(), ConfirmAction(), SETTINGS_SECTIONS, TagChip(), TagPicker() (+10 more)

### Community 25 - "Frontend Entity Pages"
Cohesion: 0.08
Nodes (12): EMPTY, EMPTY, ACTION_STYLES, BulkResp, fmtEta(), ScansPage(), EMPTY, ServiceRow (+4 more)

### Community 26 - "VLANs API"
Cohesion: 0.14
Nodes (31): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+23 more)

### Community 28 - "Docs Section UI"
Cohesion: 0.11
Nodes (24): DocsIndexClient(), metadata, DocPage(), dynamicParams, generateMetadata(), loadMarkdown(), CommandPalette(), Icon (+16 more)

### Community 29 - "Import Value Normalizers"
Cohesion: 0.10
Nodes (30): assemble_ip(), clean(), _clean_octets(), map_status(), mask_to_prefixlen(), network_of(), norm_mac(), parse_range_end() (+22 more)

### Community 30 - "Tags API"
Cohesion: 0.14
Nodes (29): AssignBody, assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession (+21 more)

### Community 31 - "Color Rules API"
Cohesion: 0.13
Nodes (23): create_rule(), delete_rule(), get_rule(), list_rules(), preview_rule(), AsyncSession, delete, get (+15 more)

### Community 32 - "Dashboard & Settings UI"
Cohesion: 0.16
Nodes (16): ACTION_STYLES, FeatureDef, GROUPS, Key, metadata, Key, ScanningPage(), SettingsPage() (+8 more)

### Community 33 - "Ranges API"
Cohesion: 0.12
Nodes (22): _check_range_overlap(), create_range(), delete_range(), list_ranges(), AsyncSession, delete, get, post (+14 more)

### Community 34 - "Prefix Tree & Field UI"
Cohesion: 0.11
Nodes (21): PrefixTree(), TreeRow, utilColor(), SOURCE_STYLE, CELL_SIZE, cellLabel(), CellState, GridLegend() (+13 more)

### Community 35 - "Backup Service"
Cohesion: 0.15
Nodes (27): _alembic_revisions(), backup_dir(), backup_filename(), BackupError, BackupPreview, BackupTable, build_backup(), delete_backup_file() (+19 more)

### Community 36 - "Scan VRF Inference"
Cohesion: 0.13
Nodes (20): _global_vrf_id(), _infer_scan_vrf(), Pick the VRF for a scan that didn't specify one. An exact-match prefix living…, _scan_vrf(), _extra_vrf(), _global_id(), _mk_prefix(), The cap is a runtime setting: lowering it to 2 rejects a /24. (+12 more)

### Community 37 - "Test Fakes & Fixtures"
Cohesion: 0.10
Nodes (21): _api_cancel(), _FakeRedis, _mk_job(), In-memory stand-in for the worker's redis client (get/set/publish)., Point the worker at the test DB (sf) and the fake redis client., Simulate the API-side cancel: terminal status on a fresh connection., Cancel flag polled between phases -> ScanCancelled -> CANCELLED, and no…, Audit race: API writes CANCELLED mid-scan while the redis flag is lost… (+13 more)

### Community 38 - "Users API"
Cohesion: 0.14
Nodes (25): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+17 more)

### Community 39 - "Scan Reconciliation"
Cohesion: 0.11
Nodes (25): _flag(), Any, AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), A stored (e.g. imported) MAC that differs from the scan is flagged in…, Scanning a /24 under a documented /16 must not mark the other 255 subnets'…, reconcile() called with no flags (the pre-toggles signature) must do exactly… (+17 more)

### Community 40 - "Scan Worker Jobs"
Cohesion: 0.11
Nodes (23): cancel_key(), _due(), _eta_seconds(), _job_status(), _publish(), Re-read the job row's status — the session's `job` instance goes stale the…, ARQ job: execute a scan and reconcile results., Enqueue a scan for every configured network (effective settings). Targets:… (+15 more)

### Community 41 - "Workbook Plan Tests"
Cohesion: 0.20
Nodes (14): _master_row(), _matrix(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind… (+6 more)

### Community 42 - "Prefix Tree Page"
Cohesion: 0.17
Nodes (22): metadata, ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), collectExpandableKeys(), flattenTree() (+14 more)

### Community 43 - "Sheet Header Parsers"
Cohesion: 0.10
Nodes (18): norm_header(), Header cell -> lowercase, single-spaced, for signature matching. Edge…, _col_class(), _is_header_echo(), _leftover_bits(), _map_columns(), parse_assets(), parse_servers() (+10 more)

### Community 44 - "App Layout & Init"
Cohesion: 0.11
Nodes (21): metadata, viewport, fmtChangeVal(), PrefsInit(), TooltipProvider, AddrMapView, applyPrefs(), DEFAULT_PREFS (+13 more)

### Community 45 - "Imports API"
Cohesion: 0.18
Nodes (21): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+13 more)

### Community 46 - "Import Batch Model"
Cohesion: 0.10
Nodes (19): ImportBatch, ImportBatchStatus, Base, str, One uploaded workbook (or file) import run. `stats` holds the preview result:…, excel_date(), date, datetime/date passthrough; int/float serial (20000-80000) -> date; 'd/m/yy'… (+11 more)

### Community 47 - "List Detail UI"
Cohesion: 0.11
Nodes (17): cellLabel(), CHIP_COLORS, chipColor(), COL_TYPES, ListClient(), metadata, IpDrawer(), ROLES (+9 more)

### Community 48 - "RBAC Tests"
Cohesion: 0.34
Nodes (22): str, UserRole, login(), mkuser(), other_client(), AsyncClient, AsyncSession, allow_insecure keeps full access (existing behavior preserved). (+14 more)

### Community 49 - "Frontend Package Meta"
Cohesion: 0.09
Nodes (22): name, private, version, autoprefixer, clsx, postcss, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+14 more)

### Community 50 - "Frontend Dependencies"
Cohesion: 0.09
Nodes (23): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, lucide-react, next, @radix-ui/react-dialog (+15 more)

### Community 51 - "Login & Settings Pages"
Cohesion: 0.14
Nodes (12): BackupSettingsPage(), downloadUrl(), fmtSize(), fmtAgo(), SecurityPage(), SettingField(), SOURCE_STYLE, AccessibleName (+4 more)

### Community 52 - "Row Ordering Tests"
Cohesion: 0.22
Nodes (21): auth_on(), _circuit_order(), _login(), _mk_circuits(), _mkuser(), AsyncClient, AsyncSession, fixture (+13 more)

### Community 53 - "Prefix Detail Page"
Cohesion: 0.13
Nodes (13): IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, SplitPlan, toggleIn(), AddressFilterPanel(), Breadcrumbs() (+5 more)

### Community 54 - "Color Rules Tests"
Cohesion: 0.27
Nodes (19): _login(), _mk_rule(), _mk_site(), _mkuser(), AsyncClient, AsyncSession, Global row colors: manual row_color + rule-computed display_color. Covers the…, test_backup_roundtrips_color_rules() (+11 more)

### Community 55 - "App Shell & Nav"
Cohesion: 0.13
Nodes (15): AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS, NavGroup, NavItem, NavLink() (+7 more)

### Community 56 - "TypeScript Config"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 57 - "Settings Tests"
Cohesion: 0.17
Nodes (15): AsyncClient, fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture, Every new Settings > Features key is runtime-editable; untouched keys keep the…, test_backup_files_report_effective_schedule() (+7 more)

### Community 58 - "List Import Tests"
Cohesion: 0.22
Nodes (11): ListTarget, auth_on(), _preview_of(), fixture, _servers_xlsx(), test_import_as_list_e2e(), test_manually_edited_row_wins_conflict(), test_reimport_merges_by_key() (+3 more)

### Community 59 - "List CRUD & Bulk Tests"
Cohesion: 0.18
Nodes (4): _mklist(), TestBulkRows, TestListCRUD, TestRows

### Community 60 - "Docker Compose Stack"
Cohesion: 0.19
Nodes (18): alembic upgrade head on api start, API_BIND publish binding, api service, backupdata volume, backupdata Volume, IPAMBOX_COOKIE_SECURE env, db service (postgres:16-alpine), ipam bridge network 192.0.2.0/24 (+10 more)

### Community 61 - "Command Palette"
Cohesion: 0.16
Nodes (15): CommandPalette(), Icon, Item, itemsFor(), remember(), SearchOut, BY_SLUG, DOC_ARTICLES (+7 more)

### Community 62 - "Site Sheet Parser"
Cohesion: 0.17
Nodes (8): _blocks(), parse_site_sheet(), Split duplicated column groups (031-style runaway): each block starts at an…, MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf., Bare 'Name' (Cellular) maps to the hostname field., Non-empty unnamed columns pile into cf['extra'] instead of vanishing (Pelephone…, TestSiteSheetExtras, TestSiteSheetParser

### Community 63 - "Import Wizard UI"
Cohesion: 0.14
Nodes (11): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, Step (+3 more)

### Community 64 - "Import Plan Execution"
Cohesion: 0.22
Nodes (14): _apply_list(), execute_plan(), rep(), _get_or_create_list(), _get_or_create_prefix(), _get_or_create_site(), _get_or_create_vlan(), _get_or_create_vrf() (+6 more)

### Community 65 - "Custom List Parser"
Cohesion: 0.23
Nodes (9): _cell_text(), extract_list_table(), _infer_type(), _ips(), _is_ip_token(), pick_key_column(), _sniff_header_row(), _matrix() (+1 more)

### Community 66 - "List Import Dialog"
Cohesion: 0.19
Nodes (12): UploadResp, ImportListDialog(), IPAM_FAMILIES, PreviewResp, Step, UploadResp, ListsClient(), metadata (+4 more)

### Community 67 - "Import Client Pages"
Cohesion: 0.13
Nodes (10): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, Step (+2 more)

### Community 68 - "Sheet Classification"
Cohesion: 0.21
Nodes (7): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, TestClassify

### Community 69 - "Sites Master Parser"
Cohesion: 0.19
Nodes (8): _master_blocks(), parse_sites_master(), (first, second) octet pairs a master row declares — lets sheet->site matching…, Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins., TestSitesMasterParser

### Community 70 - "Changelog Tests"
Cohesion: 0.23
Nodes (12): AsyncClient, tag_assignments.object_id has no FK — deleting a tagged object must drop its…, Tag.assignments is already ORM delete-orphan — each removed assignment lands in…, PATCH settings with a null value deletes the app_settings row — that delete…, /addresses/bulk action=delete used to issue one Core DELETE — invisible to the…, test_bulk_delete_writes_changelog_entries(), test_changelog_captures_ip_status_change(), test_changelog_records_crud() (+4 more)

### Community 71 - "Search API Tests"
Cohesion: 0.31
Nodes (12): auth_on(), AsyncClient, fixture, _seed(), test_addresses_q_filter_not_broken(), test_search_empty_query(), test_search_grouped_results(), test_search_hebrew_folding() (+4 more)

### Community 72 - "Color Rules UI"
Cohesion: 0.18
Nodes (9): ColorRulesPage(), Draft, ENTITIES, OP_LABEL, OPS_BY_TYPE, opsFor(), RuleDialog(), metadata (+1 more)

### Community 73 - "Runtime Settings"
Cohesion: 0.27
Nodes (9): Any, Runtime-editable settings: app_settings rows override env defaults. Each public…, _v_bool(), _v_cidr_list(), _v_float(), _v_int(), check(), _v_port_list() (+1 more)

### Community 74 - "Scanner Delta Tests"
Cohesion: 0.21
Nodes (8): on_hosts fires once per detection step with that chunk's new IPs — ARP batch…, When L2+L3 find nothing, the TCP fallback publishes its batch too., test_scan_cidr_emits_found_deltas(), fake_icmp(), fake_probe(), fake_ptr(), on_hosts(), test_scan_cidr_tcp_fallback_reports_found()

### Community 75 - "Import Plan Builder"
Cohesion: 0.25
Nodes (8): key_for(), build_import_plan(), DbState, load_state(), parse_sites_master_records(), _preview(), AsyncSession, _site_key()

### Community 76 - "Test Fixtures (conftest)"
Cohesion: 0.38
Nodes (9): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, session(), sf(), _split_dsn() (+1 more)

### Community 77 - "Fake ARQ/Redis Fixtures"
Cohesion: 0.20
Nodes (8): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture, Stands in for the arq Redis pool — never actually dispatches work., scan_exclude_networks=10.70.0.64/26 inside scan_networks=10.70.0.0/24: the…, test_scheduler_and_route_share_exclusion_guard()

### Community 79 - "App Shell Nav (alt)"
Cohesion: 0.20
Nodes (8): AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS, NavGroup, NavItem, NavLink(), AuthStatus

### Community 80 - "Backup Restore API"
Cohesion: 0.29
Nodes (9): post, Request, Restore a backup file (raw .json.gz body). Wipes every data table (users are…, restore(), BackupFileInfo, BackupFilesOut, BackupPreviewOut, BaseModel (+1 more)

### Community 81 - "Prefix API Tests"
Cohesion: 0.38
Nodes (9): _global_vrf_id(), test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_prefixes_order_by_utilization_and_limit(), test_same_cidr_allowed_across_vrfs(), test_split_cardinality_cap(), test_split_endpoint(), test_tree_endpoint() (+1 more)

### Community 82 - "Sheet UI Primitive"
Cohesion: 0.20
Nodes (8): Sheet, SheetClose, SheetContent, SheetDescription, SheetPortal, SheetTitle, SheetTrigger, @radix-ui/react-dialog

### Community 83 - "Settings Read & URL Mask"
Cohesion: 0.28
Nodes (9): _build_out(), _mask_url(), AsyncSession, get, Hide the password in a scheme://user:pass@host URL., read_settings(), update_settings(), SettingsOut (+1 more)

### Community 84 - "App Settings Config"
Cohesion: 0.22
Nodes (3): psycopg2-style URL for alembic offline mode / scripts., Settings, BaseSettings

### Community 85 - "Auth Test Fixtures"
Cohesion: 0.22
Nodes (6): auth_on(), fixture, auth_on(), fake_arq(), fixture, Turn auth on for a test, restore insecure mode after, and flush session/lockout…

### Community 86 - "Row Nav & Shortcuts"
Cohesion: 0.33
Nodes (6): moveRowNav(), RowNavApi, G_CHORDS, isEditableTarget(), modalOpen(), useGlobalShortcuts()

### Community 87 - "Prefix Detail Client"
Cohesion: 0.25
Nodes (6): IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, SplitPlan, toggleIn()

### Community 88 - "Color Rules UI (alt)"
Cohesion: 0.25
Nodes (6): Draft, ENTITIES, OP_LABEL, OPS_BY_TYPE, opsFor(), RuleDialog()

### Community 89 - "Allocation Tests"
Cohesion: 0.43
Nodes (7): _mk_prefix(), test_address_crud_and_dup_guard(), test_allocation_skips_existing(), test_concurrent_allocation_unique(), alloc(), test_exhausted_prefix_conflicts(), test_sequential_allocation_skips_boundaries()

### Community 90 - "Frontend Dev Dependencies"
Cohesion: 0.25
Nodes (8): devDependencies, autoprefixer, postcss, tailwindcss, @types/node, @types/react, @types/react-dom, typescript

### Community 91 - "Scheduled Backups API"
Cohesion: 0.33
Nodes (7): download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, get, Download a full snapshot (every table except users) as .json.gz.…, Scheduled snapshot files written by the worker into BACKUP_DIR.

### Community 92 - "Workbook Reader"
Cohesion: 0.62
Nodes (5): _csv_sheet(), load_upload(), load_workbook_bytes(), SheetMatrix, _trim()

### Community 93 - "Scan Job Watchdog"
Cohesion: 0.29
Nodes (7): Fail live jobs that outlived the worker's job_timeout. An OOM-killed or…, Every-minute cron: reaps live jobs that outlived job_timeout., reap_stale_scan_jobs(), scan_watchdog(), WorkerSettings, A worker killed mid-scan leaves RUNNING rows that would wedge the single-live-…, test_watchdog_reaps_stale_jobs()

### Community 94 - "Inventory Page UI"
Cohesion: 0.29
Nodes (5): AssetRow, EMPTY, Asset, AssetKind, Site

### Community 95 - "Expiry Badge & Flags"
Cohesion: 0.48
Nodes (5): ExpiryBadge(), listeners, load(), useFeatureFlag(), useSetting()

### Community 96 - "Prefixes Page UI"
Cohesion: 0.33
Nodes (3): PrefixesPage(), PrefixRow, utilColor()

### Community 97 - "Tree Page Client"
Cohesion: 0.53
Nodes (5): ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText()

### Community 98 - "Runtime Setting Spec"
Cohesion: 0.33
Nodes (6): Effective, _env_sourced(), get_effective(), True when the field's current value differs from its declared default., One runtime-editable setting. field: the env-backed attribute on…, SettingSpec

### Community 99 - "Settings Patch API"
Cohesion: 0.40
Nodes (5): patch(), AsyncSession, Apply partial updates; a value of None resets the key to env/default., Carries {key: message} so the API can return per-field 422s., SettingsValidationError

### Community 101 - "Tree Client (alt)"
Cohesion: 0.53
Nodes (5): ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText()

### Community 103 - "Circuits Parser Tests"
Cohesion: 0.40
Nodes (3): קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., TestCircuitsParser

### Community 105 - "Frontend npm Scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 107 - "Chart Theme Hook"
Cohesion: 0.50
Nodes (4): ChartTheme, FALLBACK, readTheme(), useChartTheme()

### Community 108 - "Status Tokens"
Cohesion: 0.40
Nodes (4): GRID_CELL_TOKENS, STATUS_TOKENS, StatusBadgeVariant, StatusTokenSet

### Community 109 - "Security Policy Doc"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 112 - "Backend Dependencies"
Cohesion: 0.50
Nodes (4): fastapi 0.115.6, pydantic 2.10.3, pydantic-settings 2.6.1, uvicorn[standard] 0.32.1

### Community 115 - "Backup Settings UI"
Cohesion: 0.83
Nodes (3): BackupSettingsPage(), downloadUrl(), fmtSize()

### Community 136 - "DB Driver Deps"
Cohesion: 0.67
Nodes (3): alembic 1.14.0, asyncpg 0.30.0, sqlalchemy[asyncio] 2.0.36

## Knowledge Gaps
- **417 isolated node(s):** `Row`, `SortKey`, `ButtonProps`, `AccessibleName`, `CheckboxBaseProps` (+412 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1078 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **57 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `upload_workbook()` connect `Imports API` to `Auth API`, `List Import Dialog`, `Import Plan Builder`, `Workbook Reader`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Why does `ImportBatch` connect `List Import Dialog` to `Frontend Type Definitions`, `Imports API`, `Import Wizard UI`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `IPAddress` connect `Addresses API` to `Ranges API`, `API Router & Core App`, `Prefixes API & Allocation`, `Migrations, Backup & Changelog`, `Scan VRF Inference`, `Scan Reconciliation`, `Scan Worker Jobs`, `Maintenance & Admin Tasks`, `Import Value Normalizers`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `User` (e.g. with `bulk_addresses()` and `auth_status()`) actually correct?**
  _`User` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 38 inferred relationships involving `IPAMError` (e.g. with `create_address()` and `delete_address()`) actually correct?**
  _`IPAMError` has 38 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Row`, `SortKey`, `ButtonProps` to the rest of the system?**
  _417 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Custom Lists API` be split into smaller, more focused modules?**
  _Cohesion score 0.05277262420119563 - nodes in this community are weakly interconnected._