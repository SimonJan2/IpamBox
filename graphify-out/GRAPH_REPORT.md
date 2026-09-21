# Graph Report - IpamBox  (2026-09-21)

## Corpus Check
- 278 files · ~240,622 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2249 nodes · 6320 edges · 150 communities (76 shown, 52 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 391 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Entity table client pages
- Auth & login flow
- Users, roles & RBAC tests
- Entity CRUD client pages
- API client & frontend deps
- Prefix detail & address UI
- App shell & user prefs
- Core app wiring & changelog
- Types & status badges
- Backup & restore API
- Workbook import execution
- Workbook parsing & normalize
- Workbook planner internals
- Prefix CRUD service
- Color rules engine
- IPAM schemas
- Import batches API
- Route error boundaries
- Maintenance & audit log
- Sites API & deps
- Scanner VRF inference tests
- Address API & schemas
- Scan jobs & scanner API
- Tags API & ordering
- VLAN API & models
- CRUD router & color stamping
- Runtime settings service
- Prefix client dialogs
- Command palette & prefs
- Dashboard client UI
- Auth & search tests
- VRF API & schemas
- Scanner worker & scheduler
- Planner site resolution tests
- Network scanner engine
- Site sheet parser tests
- Color rules tests
- Frontend package deps
- Tree page client
- Build config & tailwind
- IPAM reconcile tests
- Row ordering tests
- Search API
- Prefix math utilities
- Workbook import tests
- TypeScript config
- Asset & service entities
- Docker compose services
- UI table primitives
- Prefix tree component
- Settings API tests
- Site schemas & validators
- Sites master parser tests
- Maintenance tests
- Sheet classification
- Settings client UI
- Test fixtures & conftest
- Certificate & dashboard schemas
- Normalize unit tests
- Changelog ORM hooks
- Prefix API tests
- Discovery confirm endpoints
- Workbook reader
- Address allocation tests
- Frontend dev deps
- Positional column parser
- Tree text helpers
- Entity CRUD smoke tests
- Import page & next config
- Loading & separator UI
- Health endpoints
- CSV export helpers
- Changelog tests
- Shortcuts overlay
- Shortcuts overlay groups
- Security policy doc
- Python backend deps
- Backend pinned deps
- SQLAlchemy & alembic deps
- Certificates route page
- Changelog route page
- Circuits route page
- Discovery route page
- Inventory route page
- Login route page
- Prefix detail route page
- Prefixes route page
- Scans route page
- Services route page
- Appearance settings page
- Backup settings page
- Data settings page
- Security settings page
- Users settings page
- Setup route page
- Sites route page
- Tags route page
- VLANs route page
- VRFs route page
- Settings navigation
- README & docs nodes
- DB driver deps
- Worker deps
- Test framework deps
- Next env types
- XFF shim script
- ARQ & redis deps
- Pytest deps
- Request class
- Prefix class
- Exception class
- Bcrypt dep
- Httpx dep
- Openpyxl dep
- Psutil dep
- Scapy dep
- App icon asset
- Root layout node
- App icon node
- Backup tables registry
- Env example file
- GitHub repo link
- MIT license
- Bcrypt dep (dup)
- Httpx dep (dup)
- Openpyxl dep (dup)
- Psutil dep (dup)
- Scapy dep (dup)

## God Nodes (most connected - your core abstractions)
1. `react` - 88 edges
2. `User` - 54 edges
3. `cn()` - 53 edges
4. `IPAddress` - 52 edges
5. `get_or_404()` - 51 edges
6. `IPAMError` - 50 edges
7. `lucide-react` - 46 edges
8. `Base` - 43 edges
9. `_matrix()` - 39 edges
10. `get_settings()` - 38 edges

## Surprising Connections (you probably didn't know these)
- `ScanJob` --calls--> `run_scheduled_scans()`  [EXTRACTED]
  frontend/src/types/index.ts → backend/app/worker/worker.py
- `create_prefix()` --calls--> `Prefix`  [EXTRACTED]
  backend/app/api/v1/prefixes.py → frontend/src/types/index.ts
- `Prefix` --calls--> `_resolve_prefix()`  [EXTRACTED]
  frontend/src/types/index.ts → backend/app/worker/worker.py
- `PrefixDetailPage()` --calls--> `usePrefs()`  [EXTRACTED]
  app/prefixes/[id]/prefix-detail-client.tsx → lib/prefs.ts
- `AddressList()` --calls--> `useRowNav()`  [EXTRACTED]
  components/address-list.tsx → lib/row-nav.ts

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **async FastAPI + SQLAlchemy + Postgres API stack** — requirements_fastapi, requirements_uvicorn, requirements_sqlalchemy, requirements_asyncpg, requirements_pydantic [INFERRED 0.85]

## Communities (150 total, 52 thin omitted)

### Community 0 - "Entity table client pages"
Cohesion: 0.05
Nodes (74): CertificatesPage(), EMPTY, CircuitsPage(), EMPTY, AssetRow, EMPTY, InventoryPage(), IP_ROLES (+66 more)

### Community 1 - "Auth & login flow"
Cohesion: 0.05
Nodes (88): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+80 more)

### Community 2 - "Users, roles & RBAC tests"
Cohesion: 0.08
Nodes (72): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+64 more)

### Community 3 - "Entity CRUD client pages"
Cohesion: 0.10
Nodes (50): CertificatesPage(), EMPTY, ACTION_STYLES, ChangeSummary(), fmt(), CircuitsPage(), EMPTY, AssetRow (+42 more)

### Community 4 - "API client & frontend deps"
Cohesion: 0.07
Nodes (42): BulkResp, fmtEta(), ScansPage(), BackupSettingsPage(), downloadUrl(), fmtSize(), DataPage(), download() (+34 more)

### Community 5 - "Prefix detail & address UI"
Cohesion: 0.06
Nodes (47): IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, SplitPlan, toggleIn(), AddressList(), AddrMapViewSwitcher() (+39 more)

### Community 6 - "App shell & user prefs"
Cohesion: 0.05
Nodes (47): metadata, PrintClient(), VrfsPage(), AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS (+39 more)

### Community 7 - "Core app wiring & changelog"
Cohesion: 0.13
Nodes (27): Audit trail via session flush hooks. before_flush collects (object, action,…, metrics(), Prometheus-style text exposition of object + scan counters., AppSetting, Runtime-editable setting override. Absent row -> env var -> default., Asset, Base, SW/HW catalog rows (תוכנות וחומרות) and serial-number inventory… (+19 more)

### Community 8 - "Types & status badges"
Cohesion: 0.04
Nodes (44): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, Step (+36 more)

### Community 9 - "Backup & restore API"
Cohesion: 0.07
Nodes (48): delete_scheduled_backup(), download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, delete, get, post (+40 more)

### Community 10 - "Workbook import execution"
Cohesion: 0.08
Nodes (38): _check_range_overlap(), create_range(), delete_range(), list_ranges(), AsyncSession, delete, get, post (+30 more)

### Community 11 - "Workbook parsing & normalize"
Cohesion: 0.08
Nodes (41): assemble_ip(), clean(), _clean_octets(), map_status(), mask_to_prefixlen(), network_of(), norm_header(), norm_mac() (+33 more)

### Community 12 - "Workbook planner internals"
Cohesion: 0.10
Nodes (15): parse_sites_master_records(), _Planner, _preview(), (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Folded sheet title vs site name/code — word-boundary matching so 'int' doesn't…, Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new… (+7 more)

### Community 13 - "Prefix CRUD service"
Cohesion: 0.10
Nodes (40): AllocateIPRequest, AsyncSession, get, stats(), allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes() (+32 more)

### Community 14 - "Color rules engine"
Cohesion: 0.11
Nodes (33): create_rule(), delete_rule(), get_rule(), list_rules(), preview_rule(), AsyncSession, delete, get (+25 more)

### Community 15 - "IPAM schemas"
Cohesion: 0.08
Nodes (26): IPRangeRole, str, CircuitCreate, CircuitOut, CircuitUpdate, BaseModel, field_validator, ip_display() (+18 more)

### Community 16 - "Import batches API"
Cohesion: 0.11
Nodes (35): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+27 more)

### Community 18 - "Maintenance & audit log"
Cohesion: 0.10
Nodes (37): ArqRedis, _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody (+29 more)

### Community 19 - "Sites API & deps"
Cohesion: 0.11
Nodes (23): do_run_migrations(), run_migrations_online(), list_changelog(), AsyncSession, get, get_settings(), get_session(), AsyncSession (+15 more)

### Community 20 - "Scanner VRF inference tests"
Cohesion: 0.10
Nodes (25): infer_device_type(), Best-effort device classification; None when nothing matched., _global_vrf_id(), _infer_scan_vrf(), Pick the VRF for a scan that didn't specify one. An exact-match prefix living…, reap_stale_scan_jobs(), _scan_vrf(), scan_watchdog() (+17 more)

### Community 21 - "Address API & schemas"
Cohesion: 0.14
Nodes (26): bulk_addresses(), BulkBody, create_address(), delete_address(), export_addresses(), import_addresses(), ImportRow, list_addresses() (+18 more)

### Community 22 - "Scan jobs & scanner API"
Cohesion: 0.12
Nodes (29): cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession, get (+21 more)

### Community 23 - "Tags API & ordering"
Cohesion: 0.14
Nodes (28): reorder_items(), assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession (+20 more)

### Community 24 - "VLAN API & models"
Cohesion: 0.17
Nodes (28): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+20 more)

### Community 25 - "CRUD router & color stamping"
Cohesion: 0.11
Nodes (30): get_address(), patch, update_address(), _crud_router(), create_item(), delete_item(), get_item(), list_items() (+22 more)

### Community 26 - "Runtime settings service"
Cohesion: 0.09
Nodes (20): psycopg2-style URL for alembic offline mode / scripts., Settings, Effective, _env_sourced(), Any, Exception, Runtime-editable settings: app_settings rows override env defaults. Each public…, True when the field's current value differs from its declared default. (+12 more)

### Community 27 - "Prefix client dialogs"
Cohesion: 0.13
Nodes (20): PrefixRow, ConfirmAction(), ConfirmDialog(), QuickScanDialog(), useScanStream(), TAG_COLORS, TagDialog(), Dialog (+12 more)

### Community 28 - "Command palette & prefs"
Cohesion: 0.12
Nodes (22): SettingField(), SOURCE_STYLE, CommandPalette(), Icon, Item, itemsFor(), remember(), SearchOut (+14 more)

### Community 29 - "Dashboard client UI"
Cohesion: 0.10
Nodes (19): ACTION_STYLES, DashboardPage(), metadata, expiryBadge(), Badge(), BadgeProps, badgeVariants, Progress (+11 more)

### Community 30 - "Auth & search tests"
Cohesion: 0.16
Nodes (22): AsyncClient, auth_on(), AsyncClient, fixture, Turn auth on for a test, restore insecure mode after, and flush session/lockout…, test_endpoints_require_auth(), test_lockout_keyed_per_user_ip_pair(), test_login_lockout() (+14 more)

### Community 31 - "VRF API & schemas"
Cohesion: 0.15
Nodes (18): create_vrf(), delete_vrf(), get_vrf(), list_vrfs(), AsyncSession, delete, get, patch (+10 more)

### Community 32 - "Scanner worker & scheduler"
Cohesion: 0.17
Nodes (23): set_actor(), get_effective(), AsyncSession, detect_interface(), detect_local_cidr(), CIDR of the default-route interface, e.g. '192.168.1.0/24'., _due(), _eta_seconds() (+15 more)

### Community 33 - "Planner site resolution tests"
Cohesion: 0.18
Nodes (12): _master_row(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind…, Mashapan TA + MATPASH share number 200 — merge + conflict, not a silent… (+4 more)

### Community 34 - "Network scanner engine"
Cohesion: 0.13
Nodes (19): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), _host_chunks(), _icmp_sweep(), _ptr_lookup(), Exception (+11 more)

### Community 35 - "Site sheet parser tests"
Cohesion: 0.15
Nodes (12): _blocks(), parse_site_sheet(), Split duplicated column groups (031-style runaway): each block starts at an…, _matrix(), קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf., Bare 'Name' (Cellular) maps to the hostname field. (+4 more)

### Community 36 - "Color rules tests"
Cohesion: 0.22
Nodes (22): auth_on(), _login(), _mk_rule(), _mk_site(), _mkuser(), AsyncClient, AsyncSession, fixture (+14 more)

### Community 37 - "Frontend package deps"
Cohesion: 0.09
Nodes (23): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, lucide-react, next, @radix-ui/react-dialog (+15 more)

### Community 38 - "Tree page client"
Cohesion: 0.16
Nodes (19): metadata, ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), collectExpandableKeys(), flattenTree() (+11 more)

### Community 39 - "Build config & tailwind"
Cohesion: 0.09
Nodes (20): name, private, scripts, build, dev, lint, start, version (+12 more)

### Community 40 - "IPAM reconcile tests"
Cohesion: 0.20
Nodes (19): AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), HostResult, _prefix(), test_address_role_nat_and_bulk(), test_bulk_reports_real_counts(), test_container_move_with_children_rejected() (+11 more)

### Community 41 - "Row ordering tests"
Cohesion: 0.24
Nodes (20): auth_on(), _circuit_order(), _login(), _mk_circuits(), _mkuser(), AsyncClient, AsyncSession, fixture (+12 more)

### Community 42 - "Search API"
Cohesion: 0.27
Nodes (17): _folded(), AsyncSession, get, search(), match(), BaseModel, SearchAddress, SearchAsset (+9 more)

### Community 43 - "Prefix math utilities"
Cohesion: 0.21
Nodes (18): children(), lowest_free(), parent_chain(), Inclusive [first, last] integer range of host-usable addresses., True when network/broadcast addresses are unusable for hosts (IPv4 <= /30)., Lowest usable address integer not in `taken` or any excluded range., Split `net` into children of `new_prefix` length., The smallest candidate network that strictly contains `net`. (+10 more)

### Community 44 - "Workbook import tests"
Cohesion: 0.13
Nodes (14): excel_date(), datetime/date passthrough; int/float serial (20000-80000) -> date; 'd/m/yy'…, parse_assets(), parse_certificates(), Positional 5-col layout: platform, target/VS, server, cert, expiry., 003 תוכנות וחומרות: סוג,חברה,דגם,שם התוכנה,ייעוד,גירסה,EOL,…, Workbook import: normalizer/parser unit tests (no DB) + API e2e., Small synthetic workbook: sites master + one site sheet + circuits. (+6 more)

### Community 45 - "TypeScript config"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 46 - "Asset & service entities"
Cohesion: 0.20
Nodes (13): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, AssetKind, str, AssetCreate, AssetOut, AssetUpdate, BaseModel, field_validator (+5 more)

### Community 47 - "Docker compose services"
Cohesion: 0.19
Nodes (18): alembic upgrade head on api start, API_BIND publish binding, api service, backupdata volume, backupdata Volume, IPAMBOX_COOKIE_SECURE env, db service (postgres:16-alpine), ipam bridge network 192.0.2.0/24 (+10 more)

### Community 48 - "UI table primitives"
Cohesion: 0.23
Nodes (14): ACTION_STYLES, ChangeSummary(), fmt(), Input, Textarea, Label, Table(), TableBody() (+6 more)

### Community 49 - "Prefix tree component"
Cohesion: 0.18
Nodes (12): metadata, PrefixTree(), TreeRow, utilColor(), Tooltip, TooltipContent, TooltipProvider, TooltipTrigger (+4 more)

### Community 50 - "Settings API tests"
Cohesion: 0.19
Nodes (13): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_files_report_effective_schedule(), test_internal_keys_hidden() (+5 more)

### Community 51 - "Site schemas & validators"
Cohesion: 0.18
Nodes (8): hex_color_or_none(), BaseModel, field_validator, SiteCreate, SiteOut, SiteUpdate, field_validator, field_validator

### Community 52 - "Sites master parser tests"
Cohesion: 0.19
Nodes (8): _master_blocks(), parse_sites_master(), (first, second) octet pairs a master row declares — lets sheet->site matching…, Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins., TestSitesMasterParser

### Community 53 - "Maintenance tests"
Cohesion: 0.21
Nodes (11): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_now_enqueues(), test_clear_discovery() (+3 more)

### Community 54 - "Sheet classification"
Cohesion: 0.24
Nodes (6): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, TestClassify

### Community 55 - "Settings client UI"
Cohesion: 0.21
Nodes (6): metadata, SettingsPage(), Card, CardHeader(), CardTitle(), DashboardStats

### Community 56 - "Test fixtures & conftest"
Cohesion: 0.30
Nodes (10): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., sf() (+2 more)

### Community 57 - "Certificate & dashboard schemas"
Cohesion: 0.27
Nodes (8): CertificateCreate, CertificateOut, CertificateUpdate, BaseModel, field_validator, DashboardStats, MacMismatchItem, BaseModel

### Community 59 - "Changelog ORM hooks"
Cohesion: 0.29
Nodes (10): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), register(), _repr(), _ser() (+2 more)

### Community 60 - "Prefix API tests"
Cohesion: 0.38
Nodes (9): _global_vrf_id(), test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_prefixes_order_by_utilization_and_limit(), test_same_cidr_allowed_across_vrfs(), test_split_cardinality_cap(), test_split_endpoint(), test_tree_endpoint() (+1 more)

### Community 61 - "Discovery confirm endpoints"
Cohesion: 0.22
Nodes (9): confirm_discovered(), ConfirmBody, list_discovered(), AsyncSession, BaseModel, get, post, Unconfirmed hosts found by scanners, pending admin review. (+1 more)

### Community 62 - "Workbook reader"
Cohesion: 0.36
Nodes (5): Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, load_workbook_bytes(), XLSX -> sheet matrices via openpyxl (read_only streams, values only)., Parse workbook bytes into per-sheet row matrices. read_only + data_only:…, SheetMatrix

### Community 63 - "Address allocation tests"
Cohesion: 0.43
Nodes (7): _mk_prefix(), test_address_crud_and_dup_guard(), test_allocation_skips_existing(), test_concurrent_allocation_unique(), alloc(), test_exhausted_prefix_conflicts(), test_sequential_allocation_skips_boundaries()

### Community 64 - "Frontend dev deps"
Cohesion: 0.25
Nodes (8): devDependencies, autoprefixer, postcss, tailwindcss, @types/node, @types/react, @types/react-dom, typescript

### Community 65 - "Positional column parser"
Cohesion: 0.29
Nodes (4): _col_class(), _positional_columns(), Dominant content class of a column sample., Headerless sheet: locate the IP column, then assign the remaining canonical…

### Community 66 - "Tree text helpers"
Cohesion: 0.53
Nodes (5): ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText()

### Community 68 - "Import page & next config"
Cohesion: 0.33
Nodes (3): nextConfig, metadata, next

### Community 69 - "Loading & separator UI"
Cohesion: 0.40
Nodes (3): Separator, Skeleton(), @radix-ui/react-separator

### Community 70 - "Health endpoints"
Cohesion: 0.40
Nodes (5): healthz(), get, Readiness probe: verifies DB + Redis connectivity., readyz(), JSONResponse

### Community 71 - "CSV export helpers"
Cohesion: 0.40
Nodes (4): csv_response(), parse_csv(), CSV text -> list of row dicts (header-named, stripped)., StreamingResponse

### Community 72 - "Changelog tests"
Cohesion: 0.60
Nodes (4): AsyncClient, test_changelog_captures_ip_status_change(), test_changelog_records_crud(), test_changelog_scoped_filters()

### Community 73 - "Shortcuts overlay"
Cohesion: 0.40
Nodes (3): Group, GROUPS, ShortcutsOverlay()

### Community 75 - "Security policy doc"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 76 - "Python backend deps"
Cohesion: 0.50
Nodes (4): fastapi 0.115.6, pydantic 2.10.3, pydantic-settings 2.6.1, uvicorn[standard] 0.32.1

### Community 77 - "Backend pinned deps"
Cohesion: 0.50
Nodes (4): fastapi 0.115.6, pydantic 2.10.3, pydantic-settings 2.6.1, uvicorn[standard] 0.32.1

### Community 92 - "SQLAlchemy & alembic deps"
Cohesion: 0.67
Nodes (3): alembic 1.14.0, asyncpg 0.30.0, sqlalchemy[asyncio] 2.0.36

### Community 115 - "DB driver deps"
Cohesion: 0.67
Nodes (3): alembic 1.14.0, asyncpg 0.30.0, sqlalchemy[asyncio] 2.0.36

## Knowledge Gaps
- **265 isolated node(s):** `AssetRow`, `SplitPlan`, `ServiceRow`, `Draft`, `VlanRow` (+260 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 749 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **52 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Prefix` connect `Prefix client dialogs` to `Scanner worker & scheduler`, `Entity table client pages`, `API client & frontend deps`, `Prefix detail & address UI`, `Types & status badges`, `Prefix CRUD service`, `Dashboard client UI`?**
  _High betweenness centrality (0.252) - this node is a cross-community bridge._
- **Why does `create_prefix()` connect `Prefix CRUD service` to `Core app wiring & changelog`, `Workbook import execution`, `VLAN API & models`, `CRUD router & color stamping`, `Prefix client dialogs`?**
  _High betweenness centrality (0.168) - this node is a cross-community bridge._
- **Why does `ScanJob` connect `Scan jobs & scanner API` to `Scanner worker & scheduler`, `API client & frontend deps`, `Types & status badges`, `Prefix client dialogs`, `Dashboard client UI`?**
  _High betweenness centrality (0.145) - this node is a cross-community bridge._
- **Are the 29 inferred relationships involving `User` (e.g. with `me()` and `change_password()`) actually correct?**
  _`User` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `IPAddress` (e.g. with `bulk_addresses()` and `create_address()`) actually correct?**
  _`IPAddress` has 17 INFERRED edges - model-reasoned connections that need verification._
- **What connects `AssetRow`, `SplitPlan`, `ServiceRow` to the rest of the system?**
  _265 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Entity table client pages` be split into smaller, more focused modules?**
  _Cohesion score 0.0543956043956044 - nodes in this community are weakly interconnected._