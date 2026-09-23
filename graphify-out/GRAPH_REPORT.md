# Graph Report - IpamBox  (2026-09-23)

## Corpus Check
- 353 files · ~298,157 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 20 file(s) not represented in the graph (top: (none) 7, .csv 6, .ini 2)

## Summary
- 3265 nodes · 8338 edges · 231 communities (114 shown, 89 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 532 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Auth & App Pages
- Racks API
- Addresses API
- Address Components & Print
- Frontend Client Pages
- App Core & Settings Model
- Test Infrastructure
- CRUD Router & VLANs
- Prefixes API
- Entity CRUD & Asset Model
- Scanner & OUI
- Sites & Dashboard API
- Normalize + Parsers
- Shared TypeScript Types
- Docs Feature Concepts
- Lists API
- Auth & App Pages
- Test Lists + Listparse
- Demo Data Generator
- Frontend Dependencies
- Auth API
- Sites & Dashboard API
- Rack UI & Rackula Interop
- App Shell & Nav
- Migrations & Config
- Error Boundaries
- Entity CRUD & Asset Model
- Migrations & Config
- Frontend Page Clients
- Workbook Import Planner
- Test Scanner + Worker
- Docs + Page
- Test Backup
- App Shell & Appearance
- Scans API
- Import Client + Import List Dialog
- Frontend Entity Pages
- Tags + Tag
- Backup + Config
- Frontend Entity Pages
- Test Scanner + Reconcile
- Address Components & Print
- Color Rule + Color Rules
- Test Scanner + Worker
- Package
- Ip Range + Ranges
- Migrations & Config
- List Client + Index
- Frontend Entity Pages
- Prefix Tree + Url State
- Imports + Import Batch
- Address Components & Print
- Frontend Entity Pages
- Search
- Test Workbook Import + Parsers
- Test Workbook Import
- Package + Tailwind.Config
- Rack Elevation + Rack Editor
- Frontend Entity Pages
- Test Rbac + User
- Test Workbook Import + Parsers
- Frontend Entity Pages
- Settings
- Sites & Dashboard API
- Prefix Math + Test Prefix Math
- Migrations & Config
- Test Colors
- App Shell + Shortcuts Overlay
- Tsconfig
- Users + Security
- Execute + Listparse
- Docker Compose
- Page + Rack Qr
- Test Lists
- Import Client
- Subnets + Hierarchy
- Test Workbook Import + Classify
- Test Infrastructure
- Test Workbook Import + Parsers
- Inventory Client + Racks Client
- Certificates + Readme
- Test Changelog
- Scans API
- Discovery + Readme
- Test Auth
- Test Scanner
- Color Rules Client + Page
- Scans API
- Test Scanner
- Racks API
- Test Prefix Api
- Sheet + Package
- Package
- Frontend Entity Pages
- Prefix Detail Client
- Color Rules Client
- Addresses + Changelog
- Parsers
- Reader
- Circuits + Racks
- Frontend Client Pages
- Device Form + Rack Library
- Prefixes Client
- Worker + Test Scanner
- Test Entities
- Racks + Inventory
- Tree Client
- Vlans Client
- Shortcuts Overlay
- Package
- Status Tokens
- Security
- Vrfs Client
- Addresses + Readme
- Requirements
- Requirements
- Changelog Client
- Inventory Client
- Backup Client
- Features Client
- Requirements
- Readme + Circuits
- Racks
- Readme + Security
- Requirements
- Security Client
- Addresses + Discovery
- Requirements
- Requirements
- Docker Compose + Readme
- Next Env.D
- Xff Shim
- Next.Config
- Overview + Readme
- Requirements
- Requirements
- Scans + Settings
- Subnets + Vrfs
- Accounts And Roles
- Accounts And Roles
- Accounts And Roles
- Addresses
- AllocateIPRequest
- patch
- Request
- patch
- SyncSession
- Base
- str
- field_validator
- datetime
- datetime
- Prefix
- ScanJob
- Requirements
- Requirements
- Requirements
- Requirements
- Requirements
- AsyncClient
- Certificates
- Changelog
- CommitOptions
- Readme
- Readme
- Readme
- Readme
- Readme
- Readme
- Icon
- Layout
- Import
- Racks
- Racks
- Hierarchy
- Icon
- Import
- ImportBatch
- IPStatus
- Overview
- PrefixCreate
- PrefixOut
- PrefixUpdate
- Readme
- Readme
- Readme
- Readme
- Readme
- Requirements
- Requirements
- Requirements
- Requirements
- Requirements
- Scans
- Scans
- Search And Shortcuts
- Search And Shortcuts
- Settings
- Sites
- Subnets
- Subnets
- Tags
- Vlans

## God Nodes (most connected - your core abstractions)
1. `cn()` - 109 edges
2. `react` - 90 edges
3. `User` - 56 edges
4. `IPAMError` - 55 edges
5. `get_or_404()` - 50 edges
6. `lucide-react` - 49 edges
7. `IPAddress` - 48 edges
8. `api` - 46 edges
9. `get_settings()` - 45 edges
10. `UserRole` - 41 edges

## Surprising Connections (you probably didn't know these)
- `ImportBatch` --calls--> `upload_workbook()`  [EXTRACTED]
  frontend/src/types/index.ts → backend/app/api/v1/imports.py
- `Rack` --calls--> `create_rack()`  [EXTRACTED]
  frontend/src/types/index.ts → backend/app/api/v1/racks.py
- `SitesPage()` --calls--> `usePrefs()`  [EXTRACTED]
  app/sites/sites-client.tsx → lib/prefs.ts
- `TagsPage()` --calls--> `useRowNav()`  [EXTRACTED]
  app/tags/tags-client.tsx → lib/row-nav.ts
- `VrfsPage()` --calls--> `useRowNav()`  [EXTRACTED]
  app/vrfs/vrfs-client.tsx → lib/row-nav.ts

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Core IPAM hierarchy: Site → VRF → Prefix → IP address** — sites_feature, vrfs_feature, subnets_feature, addresses_feature, overview_data_model [EXTRACTED 1.00]
- **Core IPAM hierarchy: Site → VRF → Prefix → IP address** — sites_feature, vrfs_feature, subnets_feature, addresses_feature, overview_data_model [EXTRACTED 1.00]
- **Rackula round-trip workflow (share URLs, .Rackula.zip, merge/replace import)** — racks_rackula, readme_rack_elevations, examples_demo_rack [EXTRACTED 1.00]
- **Scan → reconcile → discovery inbox → address statuses** — scans_feature, scans_pipeline, discovery_feature, addresses_statuses [EXTRACTED 1.00]
- **Scan → reconcile → discovery inbox → address statuses** — scans_feature, scans_pipeline, discovery_feature, addresses_statuses [EXTRACTED 1.00]
- **async FastAPI + SQLAlchemy + Postgres API stack** — requirements_fastapi, requirements_uvicorn, requirements_sqlalchemy, requirements_asyncpg, requirements_pydantic [INFERRED 0.85]

## Communities (231 total, 89 thin omitted)

### Community 0 - "Auth & App Pages"
Cohesion: 0.03
Nodes (43): nextConfig, metadata, ChangelogPage(), metadata, metadata, ACTION_STYLES, DashboardPage(), metadata (+35 more)

### Community 1 - "Racks API"
Cohesion: 0.07
Nodes (74): _check_refs(), create_device(), create_rack(), delete_device(), delete_rack(), _device_fields(), _device_out(), _devices() (+66 more)

### Community 2 - "Addresses API"
Cohesion: 0.05
Nodes (66): _address_csv_row(), _addresses_stmt(), bulk_addresses(), BulkBody, create_address(), delete_address(), export_addresses(), get_address() (+58 more)

### Community 3 - "Address Components & Print"
Cohesion: 0.05
Nodes (63): IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, SplitPlan, toggleIn(), AddressFilterPanel(), AddressList() (+55 more)

### Community 4 - "Frontend Client Pages"
Cohesion: 0.09
Nodes (46): EMPTY, ACTION_STYLES, EMPTY, PrefixesPage(), PrefixRow, utilColor(), EMPTY, ServiceRow (+38 more)

### Community 5 - "App Core & Settings Model"
Cohesion: 0.06
Nodes (42): _job_payload(), SSE stream of scan progress (Redis pub/sub backed)., stream_scan(), gen(), healthz(), metrics(), get, Readiness probe: verifies DB + Redis connectivity. (+34 more)

### Community 6 - "Test Infrastructure"
Cohesion: 0.09
Nodes (53): AsyncClient, AsyncSession, _base_dsn(), client(), engine(), _prepare_test_db(), fixture, session() (+45 more)

### Community 7 - "CRUD Router & VLANs"
Cohesion: 0.08
Nodes (53): delete_rule(), delete, update_rule(), _crud_router(), delete_item(), get_item(), list_items(), reorder_items() (+45 more)

### Community 8 - "Prefixes API"
Cohesion: 0.10
Nodes (46): allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), _prefix_rows() (+38 more)

### Community 9 - "Entity CRUD & Asset Model"
Cohesion: 0.07
Nodes (32): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, AssetKind, str, AssetCreate, AssetOut, AssetUpdate, BaseModel, field_validator (+24 more)

### Community 10 - "Scanner & OUI"
Cohesion: 0.07
Nodes (44): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), detect_interface(), detect_local_cidr(), _host_chunks(), HostResult (+36 more)

### Community 11 - "Sites & Dashboard API"
Cohesion: 0.09
Nodes (41): _cascade_site_fields(), create_site(), delete_site(), get_site(), AsyncSession, delete, get, post (+33 more)

### Community 12 - "Normalize + Parsers"
Cohesion: 0.08
Nodes (41): assemble_ip(), clean(), _clean_octets(), map_status(), mask_to_prefixlen(), network_of(), norm_header(), norm_mac() (+33 more)

### Community 13 - "Shared TypeScript Types"
Cohesion: 0.04
Nodes (46): AddressPage, BackupFileInfo, BackupFilesOut, BackupPreview, Certificate, ChangeField, ChangeLogEntry, Circuit (+38 more)

### Community 14 - "Docs Feature Concepts"
Cohesion: 0.14
Nodes (45): Accounts & Roles, Insecure mode (IPAMBOX_ALLOW_INSECURE), Four roles (Administrator, Operator, Contributor, Viewer), Session-cookie authentication, Address roles (vip/vrrp/hsrp/glbp/carp/secondary), Address CSV import/export, IP Addresses, IP drawer (+37 more)

### Community 15 - "Lists API"
Cohesion: 0.12
Nodes (38): bulk_rows(), _check_columns(), create_list(), create_row(), delete_list(), delete_row(), get_list(), list_lists() (+30 more)

### Community 16 - "Auth & App Pages"
Cohesion: 0.12
Nodes (20): BulkResp, FeatureDef, GROUPS, Key, Key, STATUSES, TAG_COLORS, TagDialog() (+12 more)

### Community 17 - "Test Lists + Listparse"
Cohesion: 0.09
Nodes (25): ListTarget, _cell_text(), extract_list_table(), _infer_type(), _ips(), _is_ip_token(), pick_key_column(), _sniff_header_row() (+17 more)

### Community 18 - "Demo Data Generator"
Cohesion: 0.13
Nodes (41): generate_demo_data.py, assets_rows(), _assign_site_sheets(), _assign_site_sheets_clean(), build_en_workbook(), build_mixed_workbook(), build_sites(), certificates_rows() (+33 more)

### Community 19 - "Frontend Dependencies"
Cohesion: 0.05
Nodes (41): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, lucide-react, next, @radix-ui/react-dialog (+33 more)

### Community 20 - "Auth API"
Cohesion: 0.16
Nodes (35): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+27 more)

### Community 21 - "Sites & Dashboard API"
Cohesion: 0.09
Nodes (32): delete_scheduled_backup(), download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, delete, get, post (+24 more)

### Community 22 - "Rack UI & Rackula Interop"
Cohesion: 0.09
Nodes (35): metadata, RackDetailPage(), RackulaImportDialog(), STATUS_BADGE, ABBREV_TO_CATEGORY, canonicalCategory(), CATEGORY_TO_ABBREV, clip() (+27 more)

### Community 23 - "App Shell & Nav"
Cohesion: 0.07
Nodes (31): AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS, NavGroup, NavItem, NavLink() (+23 more)

### Community 24 - "Migrations & Config"
Cohesion: 0.08
Nodes (31): ArqRedis, close_arq_pool(), close_redis(), get_arq_pool(), get_redis(), Shared process-wide Redis client. Do NOT aclose() it per call — connections…, Shut down the shared client — lifespan/worker shutdown only., Shared ARQ pool — callers must not close() it per job. (+23 more)

### Community 26 - "Entity CRUD & Asset Model"
Cohesion: 0.10
Nodes (33): list_changelog(), AsyncSession, get, _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog() (+25 more)

### Community 27 - "Migrations & Config"
Cohesion: 0.09
Nodes (32): do_run_migrations(), run_migrations_online(), get_settings(), clear_login_failures(), client_ip(), create_session(), destroy_session(), destroy_session_by_suffix() (+24 more)

### Community 28 - "Frontend Page Clients"
Cohesion: 0.08
Nodes (12): EMPTY, EMPTY, ACTION_STYLES, BulkResp, fmtEta(), ScansPage(), EMPTY, ServiceRow (+4 more)

### Community 30 - "Test Scanner + Worker"
Cohesion: 0.09
Nodes (28): _job_status(), _publish(), Re-read the job row's status — the session's `job` instance goes stale the…, ARQ job: execute a scan and reconcile results., run_scan(), hosts_found(), progress(), _api_cancel() (+20 more)

### Community 31 - "Docs + Page"
Cohesion: 0.11
Nodes (24): DocsIndexClient(), metadata, DocPage(), dynamicParams, generateMetadata(), loadMarkdown(), CommandPalette(), Icon (+16 more)

### Community 32 - "Test Backup"
Cohesion: 0.15
Nodes (32): _backup_bytes(), _envelope_bytes(), _mkusers(), Hand-craft a backup envelope (e.g. with a forged users table)., Guard: every ORM table must be backed up (or explicitly excluded). Adding a new…, Fresh-server scenario: the migration-seeded Global VRF is replaced by the…, Fresh-server scenario: the target's admins survive; its non-admin set is fully…, A backup carrying an assignment for a missing object (e.g. taken while orphans… (+24 more)

### Community 33 - "App Shell & Appearance"
Cohesion: 0.10
Nodes (27): metadata, viewport, AppearancePage(), InlineSelect(), PrefsInit(), SavedViews(), Select, SelectContent (+19 more)

### Community 34 - "Scans API"
Cohesion: 0.10
Nodes (28): cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), list_scans(), AsyncSession, get, post (+20 more)

### Community 35 - "Import Client + Import List Dialog"
Cohesion: 0.09
Nodes (23): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, Step (+15 more)

### Community 36 - "Frontend Entity Pages"
Cohesion: 0.15
Nodes (21): CertificatesPage(), EMPTY, CircuitsPage(), EMPTY, EMPTY, ServiceRow, ServicesPage(), SitesPage() (+13 more)

### Community 37 - "Tags + Tag"
Cohesion: 0.14
Nodes (29): AssignBody, assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession (+21 more)

### Community 38 - "Backup + Config"
Cohesion: 0.14
Nodes (28): _alembic_revisions(), backup_dir(), backup_filename(), BackupError, BackupPreview, BackupTable, build_backup(), delete_backup_file() (+20 more)

### Community 39 - "Frontend Entity Pages"
Cohesion: 0.11
Nodes (19): BackupSettingsPage(), downloadUrl(), fmtSize(), AddressList(), buildRows(), IP_STATUSES, Row, sortAddr() (+11 more)

### Community 40 - "Test Scanner + Reconcile"
Cohesion: 0.11
Nodes (29): _flag(), Any, AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), _mk_prefix(), A stored (e.g. imported) MAC that differs from the scan is flagged in…, Scanning a /24 under a documented /16 must not mark the other 255 subnets'… (+21 more)

### Community 41 - "Address Components & Print"
Cohesion: 0.11
Nodes (22): fmtEta(), ScansPage(), metadata, PrintClient(), ACTION_STYLES, ChangeDiff(), ChangeVal(), fmtChangeVal() (+14 more)

### Community 42 - "Color Rule + Color Rules"
Cohesion: 0.14
Nodes (20): create_rule(), get_rule(), list_rules(), preview_rule(), AsyncSession, get, post, reorder_rules() (+12 more)

### Community 43 - "Test Scanner + Worker"
Cohesion: 0.11
Nodes (20): _global_vrf_id(), _infer_scan_vrf(), Pick the VRF for a scan that didn't specify one. An exact-match prefix living…, _resolve_prefix(), _scan_vrf(), _extra_vrf(), _global_id(), The cap is a runtime setting: lowering it to 2 rejects a /24. (+12 more)

### Community 44 - "Package"
Cohesion: 0.07
Nodes (29): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, js-yaml, jszip, lucide-react (+21 more)

### Community 45 - "Ip Range + Ranges"
Cohesion: 0.11
Nodes (22): _check_range_overlap(), create_range(), delete_range(), list_ranges(), AsyncSession, delete, get, post (+14 more)

### Community 46 - "Migrations & Config"
Cohesion: 0.10
Nodes (19): psycopg2-style URL for alembic offline mode / scripts., Settings, _env_sourced(), Any, Exception, Runtime-editable settings: app_settings rows override env defaults. Each public…, True when the field's current value differs from its declared default., Carries {key: message} so the API can return per-field 422s. (+11 more)

### Community 47 - "List Client + Index"
Cohesion: 0.09
Nodes (20): cellLabel(), CHIP_COLORS, chipColor(), COL_TYPES, ListClient(), metadata, IpDrawer(), ROLES (+12 more)

### Community 48 - "Frontend Entity Pages"
Cohesion: 0.13
Nodes (16): VLAN_STATUSES, VlanRow, ConfirmDialog(), TAG_COLORS, TagDialog(), Dialog, DialogClose, DialogContent (+8 more)

### Community 49 - "Prefix Tree + Url State"
Cohesion: 0.17
Nodes (21): metadata, ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), collectExpandableKeys(), flattenTree() (+13 more)

### Community 50 - "Imports + Import Batch"
Cohesion: 0.17
Nodes (23): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+15 more)

### Community 51 - "Address Components & Print"
Cohesion: 0.15
Nodes (19): QuickScanDialog(), usePrefixScanOverlay(), useScanStream(), v4NetBounds(), Dialog, DialogClose, DialogContent, DialogDescription (+11 more)

### Community 52 - "Frontend Entity Pages"
Cohesion: 0.14
Nodes (15): DataPage(), download(), fmtAgo(), SecurityPage(), ConfirmAction(), SETTINGS_SECTIONS, SETTINGS_SECTIONS, SettingsNav() (+7 more)

### Community 53 - "Search"
Cohesion: 0.22
Nodes (21): _folded(), AsyncSession, get, _row_label(), search(), match(), BaseModel, SearchAddress (+13 more)

### Community 54 - "Test Workbook Import + Parsers"
Cohesion: 0.10
Nodes (19): ImportBatchStatus, str, excel_date(), date, datetime/date passthrough; int/float serial (20000-80000) -> date; 'd/m/yy'…, parse_assets(), parse_certificates(), Positional 5-col layout: platform, target/VS, server, cert, expiry. (+11 more)

### Community 55 - "Test Workbook Import"
Cohesion: 0.17
Nodes (13): _master_row(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind…, Mashapan TA + MATPASH share number 200 — merge + conflict, not a silent… (+5 more)

### Community 56 - "Package + Tailwind.Config"
Cohesion: 0.08
Nodes (23): name, private, version, autoprefixer, clsx, postcss, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+15 more)

### Community 57 - "Rack Elevation + Rack Editor"
Cohesion: 0.18
Nodes (19): FACE_BADGE, DragSession, errDetail(), Pending, RackEditor(), DeviceBlockSvg(), FACE_BADGE, HEALTH_KEY (+11 more)

### Community 58 - "Frontend Entity Pages"
Cohesion: 0.14
Nodes (20): TagsPage(), ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), SavedViews(), AddrMapView (+12 more)

### Community 59 - "Test Rbac + User"
Cohesion: 0.34
Nodes (22): str, UserRole, login(), mkuser(), other_client(), AsyncClient, AsyncSession, allow_insecure keeps full access (existing behavior preserved). (+14 more)

### Community 60 - "Test Workbook Import + Parsers"
Cohesion: 0.15
Nodes (12): _blocks(), parse_site_sheet(), Split duplicated column groups (031-style runaway): each block starts at an…, _matrix(), קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf., Bare 'Name' (Cellular) maps to the hostname field. (+4 more)

### Community 61 - "Frontend Entity Pages"
Cohesion: 0.22
Nodes (13): BulkResp, metadata, PrintClient(), VrfDialog(), vrfNameFor(), VrfsPage(), Table(), TableBody() (+5 more)

### Community 62 - "Settings"
Cohesion: 0.17
Nodes (20): _build_out(), _lan_info(), _mask_url(), AsyncSession, get, Hide the password in a scheme://user:pass@host URL., LAN identity detected by the host-networked worker (written to Redis). Falls…, read_settings() (+12 more)

### Community 63 - "Sites & Dashboard API"
Cohesion: 0.19
Nodes (17): create_vrf(), delete_vrf(), get_vrf(), list_vrfs(), AsyncSession, delete, get, post (+9 more)

### Community 64 - "Prefix Math + Test Prefix Math"
Cohesion: 0.19
Nodes (20): prefix_stats_dict(), Stats payload for one prefix given its address count (no DB access). IPv6…, children(), lowest_free(), parent_chain(), Inclusive [first, last] integer range of host-usable addresses., True when network/broadcast addresses are unusable for hosts (IPv4 <= /30)., Lowest usable address integer not in `taken` or any excluded range. (+12 more)

### Community 65 - "Migrations & Config"
Cohesion: 0.22
Nodes (21): auth_on(), _circuit_order(), _login(), _mk_circuits(), _mkuser(), AsyncClient, AsyncSession, fixture (+13 more)

### Community 66 - "Test Colors"
Cohesion: 0.27
Nodes (19): _login(), _mk_rule(), _mk_site(), _mkuser(), AsyncClient, AsyncSession, Global row colors: manual row_color + rule-computed display_color. Covers the…, test_backup_roundtrips_color_rules() (+11 more)

### Community 67 - "App Shell + Shortcuts Overlay"
Cohesion: 0.13
Nodes (15): AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS, NavGroup, NavItem, NavLink() (+7 more)

### Community 68 - "Tsconfig"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 69 - "Users + Security"
Cohesion: 0.22
Nodes (17): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+9 more)

### Community 70 - "Execute + Listparse"
Cohesion: 0.20
Nodes (16): _apply_list(), commit_batch(), execute_plan(), rep(), _get_or_create_list(), _get_or_create_prefix(), _get_or_create_site(), _get_or_create_vlan() (+8 more)

### Community 71 - "Docker Compose"
Cohesion: 0.19
Nodes (18): alembic upgrade head on api start, API_BIND publish binding, api service, backupdata volume, backupdata Volume, IPAMBOX_COOKIE_SECURE env, db service (postgres:16-alpine), ipam bridge network 192.0.2.0/24 (+10 more)

### Community 72 - "Page + Rack Qr"
Cohesion: 0.20
Nodes (10): LabelClient(), metadata, metadata, FACE_BADGE, PrintClient(), RackQrCode(), RackQrDialog(), rackUrl() (+2 more)

### Community 73 - "Test Lists"
Cohesion: 0.21
Nodes (3): _mklist(), TestListCRUD, TestRows

### Community 74 - "Import Client"
Cohesion: 0.13
Nodes (10): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, Step (+2 more)

### Community 75 - "Subnets + Hierarchy"
Cohesion: 0.19
Nodes (15): IP Addresses — documented intent + observed reality, Hierarchy tree (/tree) — Site→VRF→Prefix, Tree navigation (click-to-prefix, session expand state), Data model — Site→VRF→Prefix→IP address, Next-free-U finder (lowest/highest contiguous span, face-aware), Placement & collision rules (u_position bottom-up), Manual row colors (per-row Set color), Command palette (⌘K/Ctrl+K) (+7 more)

### Community 76 - "Test Workbook Import + Classify"
Cohesion: 0.21
Nodes (7): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, TestClassify

### Community 77 - "Test Infrastructure"
Cohesion: 0.25
Nodes (14): auth_on(), fixture, auth_on(), AsyncClient, fixture, _seed(), test_addresses_q_filter_not_broken(), test_search_empty_query() (+6 more)

### Community 78 - "Test Workbook Import + Parsers"
Cohesion: 0.19
Nodes (8): _master_blocks(), parse_sites_master(), (first, second) octet pairs a master row declares — lets sheet->site matching…, Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins., TestSitesMasterParser

### Community 79 - "Inventory Client + Racks Client"
Cohesion: 0.15
Nodes (9): AssetRow, EMPTY, metadata, EMPTY, RackRow, RacksPage(), Asset, AssetKind (+1 more)

### Community 80 - "Certificates + Readme"
Cohesion: 0.17
Nodes (13): The four roles (Administrator/Operator/Contributor/Viewer), Expiry tracking (badge, certs_expiring_30d dashboard count), Certificates — expiry tracking register, Circuits — WAN circuit register, demo-rack.Rackula.zip — 42U/18-device demo rack, Rackula round-trip (share URL, .Rackula.zip, merge/replace import), 4-tier RBAC (Administrator/Operator/Contributor/Viewer), Color rules — admin-managed conditional row coloring (+5 more)

### Community 81 - "Test Changelog"
Cohesion: 0.23
Nodes (12): AsyncClient, tag_assignments.object_id has no FK — deleting a tagged object must drop its…, Tag.assignments is already ORM delete-orphan — each removed assignment lands in…, PATCH settings with a null value deletes the app_settings row — that delete…, /addresses/bulk action=delete used to issue one Core DELETE — invisible to the…, test_bulk_delete_writes_changelog_entries(), test_changelog_captures_ip_status_change(), test_changelog_records_crud() (+4 more)

### Community 82 - "Scans API"
Cohesion: 0.22
Nodes (10): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_now_enqueues(), test_clear_discovery() (+2 more)

### Community 83 - "Discovery + Readme"
Cohesion: 0.20
Nodes (12): Accounts & role-based access control, Address statuses (active/reserved/dhcp/discovered/offline), Changelog coverage & retention, Confirm/delete workflow, Discovery Inbox — reconciliation queue, Going quiet — active↔offline flips, Overview — what IpamBox is, Health overlay — scan-status dots on device blocks (+4 more)

### Community 84 - "Test Auth"
Cohesion: 0.29
Nodes (11): AsyncClient, When the socket peer isn't in ipambox_trusted_proxies, a supplied XFF is…, Spreading failures across many usernames from one IP trips the aggregate lock —…, Five bad logins for one (user, ip) pair must not lock out other users on the…, test_endpoints_require_auth(), test_lockout_keyed_per_user_ip_pair(), test_login_lockout(), test_per_ip_aggregate_backstop() (+3 more)

### Community 85 - "Test Scanner"
Cohesion: 0.21
Nodes (8): on_hosts fires once per detection step with that chunk's new IPs — ARP batch…, When L2+L3 find nothing, the TCP fallback publishes its batch too., test_scan_cidr_emits_found_deltas(), fake_icmp(), fake_probe(), fake_ptr(), on_hosts(), test_scan_cidr_tcp_fallback_reports_found()

### Community 86 - "Color Rules Client + Page"
Cohesion: 0.20
Nodes (8): ColorRulesPage(), Draft, ENTITIES, OP_LABEL, OPS_BY_TYPE, opsFor(), RuleDialog(), metadata

### Community 87 - "Scans API"
Cohesion: 0.27
Nodes (8): DashboardStats, MacMismatchItem, BaseModel, BaseModel, field_validator, ScanConfigOut, ScanCreate, ScanJobOut

### Community 88 - "Test Scanner"
Cohesion: 0.20
Nodes (8): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture, Stands in for the arq Redis pool — never actually dispatches work., scan_exclude_networks=10.70.0.64/26 inside scan_networks=10.70.0.0/24: the…, test_scheduler_and_route_share_exclusion_guard()

### Community 90 - "Test Prefix Api"
Cohesion: 0.38
Nodes (9): _global_vrf_id(), test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_prefixes_order_by_utilization_and_limit(), test_same_cidr_allowed_across_vrfs(), test_split_cardinality_cap(), test_split_endpoint(), test_tree_endpoint() (+1 more)

### Community 91 - "Sheet + Package"
Cohesion: 0.20
Nodes (8): Sheet, SheetClose, SheetContent, SheetDescription, SheetPortal, SheetTitle, SheetTrigger, @radix-ui/react-dialog

### Community 92 - "Package"
Cohesion: 0.22
Nodes (9): devDependencies, autoprefixer, postcss, tailwindcss, @types/js-yaml, @types/node, @types/react, @types/react-dom (+1 more)

### Community 93 - "Frontend Entity Pages"
Cohesion: 0.33
Nodes (6): moveRowNav(), RowNavApi, G_CHORDS, isEditableTarget(), modalOpen(), useGlobalShortcuts()

### Community 94 - "Prefix Detail Client"
Cohesion: 0.25
Nodes (6): IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, SplitPlan, toggleIn()

### Community 95 - "Color Rules Client"
Cohesion: 0.25
Nodes (6): Draft, ENTITIES, OP_LABEL, OPS_BY_TYPE, opsFor(), RuleDialog()

### Community 96 - "Addresses + Changelog"
Cohesion: 0.29
Nodes (7): IP drawer — per-address detail panel, Changelog — global /changelog audit log, Backup & restore (.json.gz snapshots), Row color storage & coverage, Backup & restore settings, Site list affordances (reorder, pin, inline edit, tags, row color), Tag list management & deletion semantics

### Community 97 - "Parsers"
Cohesion: 0.29
Nodes (4): _col_class(), _positional_columns(), Dominant content class of a column sample., Headerless sheet: locate the IP column, then assign the remaining canonical…

### Community 98 - "Reader"
Cohesion: 0.62
Nodes (5): _csv_sheet(), load_upload(), load_workbook_bytes(), SheetMatrix, _trim()

### Community 99 - "Circuits + Racks"
Cohesion: 0.29
Nodes (7): Circuit fields (line type, Bezeq circuit ID, WAN IP, is_retired), Racks — physical rack elevations (/racks), Rack elevations feature (front/rear U placement, Rackula round-trip), Service fields (beneficiary, site, doc path, test info), Sites — top of the IpamBox hierarchy, VLAN fields (VID 1–4094, name, group, site, status), VRF fields (name, RD, site) + seeded Global VRF

### Community 100 - "Frontend Client Pages"
Cohesion: 0.48
Nodes (5): ExpiryBadge(), listeners, load(), useFeatureFlag(), useSetting()

### Community 101 - "Device Form + Rack Library"
Cohesion: 0.48
Nodes (5): DeviceFormDialog(), EMPTY, LibraryDevice, RACK_LIBRARY, RackFace

### Community 102 - "Prefixes Client"
Cohesion: 0.33
Nodes (3): PrefixesPage(), PrefixRow, utilColor()

### Community 103 - "Worker + Test Scanner"
Cohesion: 0.33
Nodes (6): Fail live jobs that outlived the worker's job_timeout. An OOM-killed or…, Every-minute cron: reaps live jobs that outlived job_timeout., reap_stale_scan_jobs(), scan_watchdog(), A worker killed mid-scan leaves RUNNING rows that would wedge the single-live-…, test_watchdog_reaps_stale_jobs()

### Community 105 - "Racks + Inventory"
Cohesion: 0.33
Nodes (6): Inventory doc article, Custom Lists doc article, Rack Placement Rules, Rack Elevation Feature, Rackula Round-trip Workflow, Rack Elevations (README feature bullet)

### Community 106 - "Tree Client"
Cohesion: 0.53
Nodes (5): ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText()

### Community 109 - "Package"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 110 - "Status Tokens"
Cohesion: 0.40
Nodes (4): GRID_CELL_TOKENS, STATUS_TOKENS, StatusBadgeVariant, StatusTokenSet

### Community 111 - "Security"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 114 - "Addresses + Readme"
Cohesion: 0.50
Nodes (4): Bulk operations & CSV import/export, Demo CSV files (addresses, VLANs, servers, contacts, site encodings), Table & subnet-grid keyboard navigation, Prefix detail views — subnet matrix + list view + utilization

### Community 115 - "Requirements"
Cohesion: 0.50
Nodes (4): fastapi 0.115.6, pydantic 2.10.3, pydantic-settings 2.6.1, uvicorn[standard] 0.32.1

### Community 116 - "Requirements"
Cohesion: 0.50
Nodes (4): fastapi 0.115.6, pydantic 2.10.3, pydantic-settings 2.6.1, uvicorn[standard] 0.32.1

### Community 119 - "Backup Client"
Cohesion: 0.83
Nodes (3): BackupSettingsPage(), downloadUrl(), fmtSize()

### Community 141 - "Requirements"
Cohesion: 0.67
Nodes (3): alembic 1.14.0, asyncpg 0.30.0, sqlalchemy[asyncio] 2.0.36

### Community 142 - "Readme + Circuits"
Cohesion: 0.67
Nodes (3): Circuit import provenance (import_batch_id), Network_Address_DEMO.xlsx — clean flagship demo workbook, IPAM feature set (hierarchy, overlap safety, allocation, CSV, workbook import)

### Community 143 - "Racks"
Cohesion: 0.67
Nodes (3): SVG rack elevation with Front/Rear toggle, Print report — /racks/[id]/print, QR dialog & /racks/[id]/label sticker

### Community 145 - "Requirements"
Cohesion: 0.67
Nodes (3): alembic 1.14.0, asyncpg 0.30.0, sqlalchemy[asyncio] 2.0.36

## Knowledge Gaps
- **531 isolated node(s):** `ChartTheme`, `PrefixRow`, `VlanRow`, `Group`, `StatusBadgeVariant` (+526 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1200 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **89 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RackDevice` connect `Racks API` to `Rack Elevation + Rack Editor`, `Shared TypeScript Types`, `Device Form + Rack Library`, `Rack UI & Rackula Interop`?**
  _High betweenness centrality (0.184) - this node is a cross-community bridge._
- **Why does `update_device()` connect `Racks API` to `CRUD Router & VLANs`?**
  _High betweenness centrality (0.154) - this node is a cross-community bridge._
- **Why does `ImportBatch` connect `Import Client + Import List Dialog` to `Imports + Import Batch`, `Shared TypeScript Types`?**
  _High betweenness centrality (0.139) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `User` (e.g. with `bulk_addresses()` and `me()`) actually correct?**
  _`User` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 38 inferred relationships involving `IPAMError` (e.g. with `create_address()` and `get_address()`) actually correct?**
  _`IPAMError` has 38 INFERRED edges - model-reasoned connections that need verification._
- **What connects `ChartTheme`, `PrefixRow`, `VlanRow` to the rest of the system?**
  _531 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Auth & App Pages` be split into smaller, more focused modules?**
  _Cohesion score 0.026732673267326732 - nodes in this community are weakly interconnected._