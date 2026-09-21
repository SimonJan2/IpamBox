# Graph Report - IpamBox  (2026-09-21)

## Corpus Check
- 78 files · ~99,999 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2337 nodes · 6498 edges · 165 communities (84 shown, 55 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 472 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Entity CRUD Pages
- Entity CRUD Pages (alt paths)
- Entity CRUD API
- Address List UI
- Auth & Scans UI
- Workbook Import Tests
- Import Wizard UI
- Settings & Redis API
- CRUD Router Factory
- Prefixes API
- Addresses API
- Backup & Restore Service
- Changelog & Dashboard API
- Imports API
- Auth API
- Route Error Pages
- Redis & Security Core
- Maintenance API
- Search API
- Workbook Normalizers
- Color Rules API
- Backup Tests
- Backup API
- Settings Nav & Tree UI
- Scan Worker
- Import Planner
- Scanner Pipeline
- Workbook Parsers
- Scans API
- RBAC Tests
- Color & Service Schemas
- Color Tests
- Redis Test Fakes
- Frontend Config
- Frontend Dependencies
- Tags API
- Scan VRF & Scanner Tests
- Ordering Tests
- Runtime Settings
- TS Config
- App Settings Model
- Sheet Classification
- IPAM Extras Tests
- Compose Deployment
- Alembic Env & App Config
- Prefs & Tags UI
- Planner Site Resolution
- App Shell
- Color Rules UI
- Master Sheet Parsing
- Maintenance Tests
- Prefix Tree UI
- Cert & Dashboard Schemas
- Circuit Schemas
- Allocation Tests
- Changelog Tests
- Tree Page
- Scan Policy Guard
- Scan Found Deltas
- ARQ Test Fakes
- Search Tests
- Normalizer Unit Tests
- IP Range Schemas
- VLAN Schemas
- Prefix API Tests
- Sheet UI Primitive
- Color Rules Engine
- Scan Reconcile
- Root Layout
- Command Palette
- Frontend DevDeps
- Subnet Grid
- Print View
- Tree Client
- Changelog Hooks
- Asset Schemas
- Entity Tests
- Next Config
- Quick Scan Overlay
- Keyboard Shortcuts
- npm Scripts
- Shortcuts Overlay
- Chart Theme
- Status Tokens
- Security Docs
- CSV Export
- OUI Lookup
- Backend Dependencies
- Changelog Page
- Dashboard Page
- Changelog Schemas
- DB Stack Deps
- certificates page
- circuits page
- discovery page
- import page
- inventory page
- login page
- prefixes page
- scans page
- services page
- appearance page
- backup page
- data page
- features page
- settings page
- scanning page
- security page
- users page
- setup page
- sites page
- tags page
- vlans page
- vrfs page
- Settings Nav
- Project Docs
- Queue Deps
- Test Deps
- Next Env Types
- XFF Shim
- AllocateIPRequest
- patch
- patch
- bcrypt 4.3.0
- httpx 0.28.1
- openpyxl 3.1.5
- psutil 6.1.0
- scapy 2.6.1
- BaseModel
- IpamBox App Icon (icon.svg)
- Root Layout (layout.tsx, title: IpamBox)
- IPStatus
- PrefixCreate
- PrefixOut
- PrefixUpdate
- BACKUP_TABLES registry (backend/app/serv
- .env.example
- github.com/SimonJan2/IpamBox repository
- MIT License (LICENSE)

## God Nodes (most connected - your core abstractions)
1. `react` - 97 edges
2. `cn()` - 62 edges
3. `User` - 60 edges
4. `lucide-react` - 56 edges
5. `IPAddress` - 56 edges
6. `IPAMError` - 53 edges
7. `get_or_404()` - 51 edges
8. `Prefix` - 50 edges
9. `api` - 45 edges
10. `UserRole` - 43 edges

## Surprising Connections (you probably didn't know these)
- `SitesPage()` --calls--> `usePrefs()`  [EXTRACTED]
  app/sites/sites-client.tsx → lib/prefs.ts
- `TagsPage()` --calls--> `useRowNav()`  [EXTRACTED]
  app/tags/tags-client.tsx → lib/row-nav.ts
- `SavedViews()` --calls--> `usePrefs()`  [EXTRACTED]
  components/saved-views.tsx → lib/prefs.ts
- `useRowNav()` --calls--> `VrfsPage()`  [EXTRACTED]
  lib/row-nav.ts → app/vrfs/vrfs-client.tsx
- `useRowNav()` --calls--> `AddressList()`  [EXTRACTED]
  lib/row-nav.ts → components/address-list.tsx

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **async FastAPI + SQLAlchemy + Postgres API stack** — backend_requirements_fastapi, backend_requirements_uvicorn, backend_requirements_sqlalchemy, backend_requirements_asyncpg, backend_requirements_pydantic [INFERRED 0.85]

## Communities (165 total, 55 thin omitted)

### Community 0 - "Entity CRUD Pages"
Cohesion: 0.08
Nodes (62): CertificatesPage(), EMPTY, CircuitsPage(), EMPTY, BulkResp, AssetRow, EMPTY, InventoryPage() (+54 more)

### Community 1 - "Entity CRUD Pages (alt paths)"
Cohesion: 0.09
Nodes (58): EMPTY, EMPTY, AssetRow, EMPTY, PrefixesPage(), PrefixRow, utilColor(), EMPTY (+50 more)

### Community 2 - "Entity CRUD API"
Cohesion: 0.07
Nodes (60): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, _cascade_site_fields(), create_site(), delete_site(), get_site(), list_sites(), AsyncSession, delete (+52 more)

### Community 3 - "Address List UI"
Cohesion: 0.05
Nodes (64): AddressList(), buildRows(), IP_STATUSES, Row, sortAddr(), SortKey, InlineSelect(), ROLES (+56 more)

### Community 4 - "Auth & Scans UI"
Cohesion: 0.07
Nodes (46): fmtEta(), ScansPage(), ACTION_STYLES, ACTION_STYLES, BulkResp, FEATURES, FeaturesPage(), Key (+38 more)

### Community 5 - "Workbook Import Tests"
Cohesion: 0.05
Nodes (35): _master_row(), _matrix(), _plan(), _preview_of(), Workbook import: normalizer/parser unit tests (no DB) + API e2e., Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so… (+27 more)

### Community 6 - "Import Wizard UI"
Cohesion: 0.04
Nodes (47): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, Step (+39 more)

### Community 7 - "Settings & Redis API"
Cohesion: 0.05
Nodes (54): ArqRedis, _build_out(), _lan_info(), _mask_url(), AsyncSession, get, Hide the password in a scheme://user:pass@host URL., LAN identity detected by the host-networked worker (written to Redis). Falls… (+46 more)

### Community 8 - "CRUD Router Factory"
Cohesion: 0.08
Nodes (55): update_address(), _crud_router(), create_item(), delete_item(), get_item(), list_items(), update_item(), update_range() (+47 more)

### Community 9 - "Prefixes API"
Cohesion: 0.08
Nodes (51): allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), _prefix_rows() (+43 more)

### Community 10 - "Addresses API"
Cohesion: 0.07
Nodes (46): _address_csv_row(), _addresses_stmt(), bulk_addresses(), BulkBody, create_address(), delete_address(), export_addresses(), get_address() (+38 more)

### Community 11 - "Backup & Restore Service"
Cohesion: 0.08
Nodes (46): Restore a backup file (raw .json.gz body). Wipes every data table (users are…, restore(), _alembic_revisions(), backup_dir(), backup_filename(), BackupError, BackupPreview, BackupTable (+38 more)

### Community 12 - "Changelog & Dashboard API"
Cohesion: 0.09
Nodes (30): list_changelog(), AsyncSession, get, stats(), confirm_discovered(), ConfirmBody, list_discovered(), AsyncSession (+22 more)

### Community 13 - "Imports API"
Cohesion: 0.09
Nodes (36): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+28 more)

### Community 14 - "Auth API"
Cohesion: 0.12
Nodes (34): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+26 more)

### Community 16 - "Redis & Security Core"
Cohesion: 0.10
Nodes (36): get_redis(), Shared process-wide Redis client. Do NOT aclose() it per call — connections…, clear_login_failures(), client_ip(), create_session(), destroy_other_sessions(), destroy_session(), destroy_session_by_suffix() (+28 more)

### Community 17 - "Maintenance API"
Cohesion: 0.11
Nodes (33): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+25 more)

### Community 18 - "Search API"
Cohesion: 0.12
Nodes (31): _folded(), search(), match(), SearchAddress, SearchAsset, SearchCertificate, SearchCircuit, SearchJump (+23 more)

### Community 19 - "Workbook Normalizers"
Cohesion: 0.09
Nodes (32): assemble_ip(), clean(), _clean_octets(), fold_hebrew(), map_status(), mask_to_prefixlen(), network_of(), norm_mac() (+24 more)

### Community 20 - "Color Rules API"
Cohesion: 0.10
Nodes (25): create_rule(), delete_rule(), get_rule(), list_rules(), preview_rule(), reorder_rules(), rule_fields(), update_rule() (+17 more)

### Community 21 - "Backup Tests"
Cohesion: 0.16
Nodes (32): _backup_bytes(), _envelope_bytes(), _mkusers(), Hand-craft a backup envelope (e.g. with a forged users table)., Guard: every ORM table must be backed up (or explicitly excluded). Adding a new…, Fresh-server scenario: the migration-seeded Global VRF is replaced by the…, Fresh-server scenario: the target's admins survive; its non-admin set is fully…, A backup carrying an assignment for a missing object (e.g. taken while orphans… (+24 more)

### Community 22 - "Backup API"
Cohesion: 0.14
Nodes (26): delete_scheduled_backup(), download_backup(), download_scheduled_backup(), list_scheduled_backups(), Download a full snapshot (every table except users) as .json.gz.…, Scheduled snapshot files written by the worker into BACKUP_DIR., _admin_count(), create_user() (+18 more)

### Community 23 - "Settings Nav & Tree UI"
Cohesion: 0.11
Nodes (19): SETTINGS_SECTIONS, ALL_STATUSES, Crumb, findChain(), PrefixBreadcrumbs(), Separator, Skeleton(), decodeSorting() (+11 more)

### Community 24 - "Scan Worker"
Cohesion: 0.13
Nodes (26): set_actor(), cancel_key(), _due(), _eta_seconds(), _job_status(), _publish(), datetime, ScanJob (+18 more)

### Community 25 - "Import Planner"
Cohesion: 0.18
Nodes (6): _Planner, (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Folded sheet title vs site name/code — word-boundary matching so 'int' doesn't…, Match a site among pre-existing DB rows AND sites already planned in this batch…, The circuits sheet doubles as a site directory (מאתר -> מספר אתר + קידומת…, Honesty checks on an octet/name match — inactive sites and title/site…

### Community 26 - "Scanner Pipeline"
Cohesion: 0.11
Nodes (23): _arp_scan(), detect_interface(), detect_local_cidr(), _host_chunks(), HostResult, _icmp_sweep(), infer_device_type(), _ptr_lookup() (+15 more)

### Community 27 - "Workbook Parsers"
Cohesion: 0.10
Nodes (20): excel_date(), datetime/date passthrough; int/float serial (20000-80000) -> date; 'd/m/yy'…, _blocks(), _col_class(), _is_header_echo(), _leftover_bits(), _map_columns(), parse_assets() (+12 more)

### Community 28 - "Scans API"
Cohesion: 0.13
Nodes (23): cancel_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession, get, SSE stream of scan progress (Redis pub/sub backed)., Effective scanner configuration surfaced to the UI. (+15 more)

### Community 29 - "RBAC Tests"
Cohesion: 0.20
Nodes (20): str, UserRole, fake_arq(), login(), mkuser(), other_client(), allow_insecure keeps full access (existing behavior preserved)., test_admin_can_step_down_once_second_admin_exists() (+12 more)

### Community 30 - "Color & Service Schemas"
Cohesion: 0.10
Nodes (13): hex_color_or_none(), Shared row/tag color validator: #rrggbb, normalized to lowercase., ServiceCreate, ServiceOut, ServiceUpdate, SiteCreate, SiteOut, SiteUpdate (+5 more)

### Community 31 - "Color Tests"
Cohesion: 0.22
Nodes (22): auth_on(), _login(), _mk_rule(), _mk_site(), _mkuser(), AsyncClient, AsyncSession, fixture (+14 more)

### Community 32 - "Redis Test Fakes"
Cohesion: 0.12
Nodes (16): _FakeRedis, In-memory stand-in for the worker's redis client (get/set/publish)., Point the worker at the test DB (sf) and the fake redis client., Cancel flag polled between phases -> ScanCancelled -> CANCELLED, and no…, Audit race: API writes CANCELLED mid-scan while the redis flag is lost…, Cancel landing while reconcile writes rows: the flag + row re-check right…, A job already terminal when the worker picks it up is skipped — no RUNNING…, A job enqueued before an exclusion was added fails in run_scan instead of… (+8 more)

### Community 33 - "Frontend Config"
Cohesion: 0.09
Nodes (21): name, private, version, autoprefixer, clsx, postcss, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+13 more)

### Community 34 - "Frontend Dependencies"
Cohesion: 0.09
Nodes (23): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, lucide-react, next, @radix-ui/react-dialog (+15 more)

### Community 35 - "Tags API"
Cohesion: 0.19
Nodes (20): AssignBody, assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession (+12 more)

### Community 36 - "Scan VRF & Scanner Tests"
Cohesion: 0.16
Nodes (16): _global_vrf_id(), _infer_scan_vrf(), Pick the VRF for a scan that didn't specify one. An exact-match prefix living…, _scan_vrf(), _extra_vrf(), _global_id(), _mk_prefix(), The cap is a runtime setting: lowering it to 2 rejects a /24. (+8 more)

### Community 37 - "Ordering Tests"
Cohesion: 0.22
Nodes (21): auth_on(), _circuit_order(), _login(), _mk_circuits(), _mkuser(), AsyncClient, AsyncSession, fixture (+13 more)

### Community 38 - "Runtime Settings"
Cohesion: 0.16
Nodes (16): Effective, _env_sourced(), get_effective(), Any, AsyncSession, Runtime-editable settings: app_settings rows override env defaults. Each public…, True when the field's current value differs from its declared default., One runtime-editable setting. field: the env-backed attribute on… (+8 more)

### Community 39 - "TS Config"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 40 - "App Settings Model"
Cohesion: 0.13
Nodes (9): AppSetting, Base, Runtime-editable setting override. Absent row -> env var -> default., fake_arq(), _pool(), _FakeArqJob, _FakePool, test_internal_keys_hidden() (+1 more)

### Community 41 - "Sheet Classification"
Cohesion: 0.16
Nodes (14): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, norm_header(), Header cell -> lowercase, single-spaced, for signature matching. Edge… (+6 more)

### Community 42 - "IPAM Extras Tests"
Cohesion: 0.22
Nodes (17): _prefix(), export.csv takes the same filters as the list endpoint — a filtered view…, Same filtered-export treatment on the prefixes CSV (F8)., A documented v6 /64's 2^64 host count must not reach dashboard sums (~1.8e19 >…, test_address_role_nat_and_bulk(), test_addresses_export_respects_filters(), test_bulk_reports_real_counts(), test_container_move_with_children_rejected() (+9 more)

### Community 43 - "Compose Deployment"
Cohesion: 0.19
Nodes (18): alembic upgrade head on api start, API_BIND publish binding, api service, backupdata volume, backupdata Volume, IPAMBOX_COOKIE_SECURE env, db service (postgres:16-alpine), ipam bridge network 192.0.2.0/24 (+10 more)

### Community 44 - "Alembic Env & App Config"
Cohesion: 0.15
Nodes (7): do_run_migrations(), run_migrations_online(), get_settings(), psycopg2-style URL for alembic offline mode / scripts., Settings, Guard for every API route. Returns the User, or None in allow_insecure mode., require_auth()

### Community 45 - "Prefs & Tags UI"
Cohesion: 0.17
Nodes (15): TagsPage(), AppShell(), AddrMapView, applyPrefs(), DEFAULT_PREFS, DensityChoice, getPrefs(), Prefs (+7 more)

### Community 46 - "Planner Site Resolution"
Cohesion: 0.19
Nodes (7): Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new…, Resolve a 10.{second}.x sheet — site_number is only meaningful inside the…, A declared octet block claims the sheet — unless its site is inactive, in which…, site_key, matched_by for a site_sheet., _site_key()

### Community 47 - "App Shell"
Cohesion: 0.14
Nodes (12): AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS, NavGroup, NavItem, NavLink(), Group (+4 more)

### Community 48 - "Color Rules UI"
Cohesion: 0.15
Nodes (11): ColorRulesPage(), Draft, ENTITIES, OP_LABEL, OPS_BY_TYPE, opsFor(), RuleDialog(), metadata (+3 more)

### Community 49 - "Master Sheet Parsing"
Cohesion: 0.18
Nodes (10): _master_blocks(), parse_sites_master(), (first, second) octet pairs a master row declares — lets sheet->site matching…, build_import_plan(), DbState, load_state(), parse_sites_master_records(), _preview() (+2 more)

### Community 50 - "Maintenance Tests"
Cohesion: 0.21
Nodes (11): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_now_enqueues(), test_clear_discovery() (+3 more)

### Community 51 - "Prefix Tree UI"
Cohesion: 0.22
Nodes (11): PrefixTree(), TreeRow, utilColor(), Tooltip, TooltipContent, TooltipTrigger, PrefixNode, SiteNode (+3 more)

### Community 52 - "Cert & Dashboard Schemas"
Cohesion: 0.21
Nodes (8): CertificateCreate, CertificateOut, CertificateUpdate, DashboardStats, MacMismatchItem, ScanConfigOut, ScanCreate, ScanJobOut

### Community 53 - "Circuit Schemas"
Cohesion: 0.18
Nodes (7): CircuitCreate, CircuitOut, CircuitUpdate, ip_display(), Any, Normalize asyncpg-returned ipaddress objects / strings to display form. INET…, to_int()

### Community 54 - "Allocation Tests"
Cohesion: 0.23
Nodes (12): sf(), _mk_prefix(), test_address_crud_and_dup_guard(), test_allocation_skips_existing(), test_concurrent_allocation_unique(), alloc(), test_exhausted_prefix_conflicts(), test_sequential_allocation_skips_boundaries() (+4 more)

### Community 55 - "Changelog Tests"
Cohesion: 0.23
Nodes (12): AsyncClient, tag_assignments.object_id has no FK — deleting a tagged object must drop its…, Tag.assignments is already ORM delete-orphan — each removed assignment lands in…, PATCH settings with a null value deletes the app_settings row — that delete…, /addresses/bulk action=delete used to issue one Core DELETE — invisible to the…, test_bulk_delete_writes_changelog_entries(), test_changelog_captures_ip_status_change(), test_changelog_records_crud() (+4 more)

### Community 56 - "Tree Page"
Cohesion: 0.22
Nodes (11): metadata, prefixText(), siteText(), TreePage(), vrfText(), collectExpandableKeys(), flattenTree(), prefixKey() (+3 more)

### Community 57 - "Scan Policy Guard"
Cohesion: 0.17
Nodes (10): _check_cidr_allowed(), create_scan(), post, ScanJob, exclusion_hit(), Scan-target policy shared by the API route, the scheduler, and the worker.…, Return the first excluded CIDR overlapping ``net`` (either direction), or None.…, test_exclusion_hit_both_directions() (+2 more)

### Community 58 - "Scan Found Deltas"
Cohesion: 0.21
Nodes (8): on_hosts fires once per detection step with that chunk's new IPs — ARP batch…, When L2+L3 find nothing, the TCP fallback publishes its batch too., test_scan_cidr_emits_found_deltas(), fake_icmp(), fake_probe(), fake_ptr(), on_hosts(), test_scan_cidr_tcp_fallback_reports_found()

### Community 59 - "ARQ Test Fakes"
Cohesion: 0.20
Nodes (8): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture, Stands in for the arq Redis pool — never actually dispatches work., scan_exclude_networks=10.70.0.64/26 inside scan_networks=10.70.0.0/24: the…, test_scheduler_and_route_share_exclusion_guard()

### Community 60 - "Search Tests"
Cohesion: 0.27
Nodes (8): auth_on(), _seed(), test_addresses_q_filter_not_broken(), test_search_grouped_results(), test_search_hebrew_folding(), test_search_ip_jump(), test_search_ip_jump_prefers_owner_then_deepest(), fixture

### Community 62 - "IP Range Schemas"
Cohesion: 0.27
Nodes (5): IPRangeRole, str, IPRangeCreate, IPRangeOut, IPRangeUpdate

### Community 63 - "VLAN Schemas"
Cohesion: 0.27
Nodes (8): str, VLANStatus, VLANCreate, VLANGroupCreate, VLANGroupOut, VLANGroupUpdate, VLANOut, VLANUpdate

### Community 64 - "Prefix API Tests"
Cohesion: 0.38
Nodes (9): _global_vrf_id(), test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_prefixes_order_by_utilization_and_limit(), test_same_cidr_allowed_across_vrfs(), test_split_cardinality_cap(), test_split_endpoint(), test_tree_endpoint() (+1 more)

### Community 65 - "Sheet UI Primitive"
Cohesion: 0.20
Nodes (9): Sheet, SheetClose, SheetContent, SheetDescription, SheetHeader(), SheetPortal, SheetTitle, SheetTrigger (+1 more)

### Community 66 - "Color Rules Engine"
Cohesion: 0.39
Nodes (9): _as_date(), _as_str(), display_color_for(), _ordered_cmp(), Any, -1/0/1 comparing a column value to a rule's value string. Tries date first when…, Does ``rule`` fire on this row? NULL fields never match., Effective row color: manual row_color beats every rule. (+1 more)

### Community 67 - "Scan Reconcile"
Cohesion: 0.31
Nodes (9): AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), A stored (e.g. imported) MAC that differs from the scan is flagged in…, Scanning a /24 under a documented /16 must not mark the other 255 subnets'…, test_reconcile_flags_mac_mismatch(), test_reconcile_offline_sweep_scoped_to_scanned_net(), test_reconcile_persists_ports_and_type() (+1 more)

### Community 68 - "Root Layout"
Cohesion: 0.28
Nodes (6): metadata, PrefsInit(), TooltipProvider, applyPrefs(), resolveTheme(), useApplyPrefs()

### Community 69 - "Command Palette"
Cohesion: 0.39
Nodes (8): CommandPalette(), Icon, Item, itemsFor(), remember(), SearchOut, getPrefs(), savePrefs()

### Community 70 - "Frontend DevDeps"
Cohesion: 0.25
Nodes (8): devDependencies, autoprefixer, postcss, tailwindcss, @types/node, @types/react, @types/react-dom, typescript

### Community 71 - "Subnet Grid"
Cohesion: 0.29
Nodes (5): CELL_SIZE, cellLabel(), CellState, STATUS_ORDER, SubnetGrid()

### Community 72 - "Print View"
Cohesion: 0.29
Nodes (5): metadata, PrintClient(), VrfsPage(), IpDrawer(), fmtTs()

### Community 73 - "Tree Client"
Cohesion: 0.53
Nodes (5): ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText()

### Community 74 - "Changelog Hooks"
Cohesion: 0.53
Nodes (6): before_flush(), _columns(), _create_changes(), _delete_changes(), _ser(), _update_changes()

### Community 75 - "Asset Schemas"
Cohesion: 0.53
Nodes (5): AssetKind, str, AssetCreate, AssetOut, AssetUpdate

### Community 77 - "Next Config"
Cohesion: 0.33
Nodes (3): nextConfig, metadata, next

### Community 78 - "Quick Scan Overlay"
Cohesion: 0.47
Nodes (5): QuickScanDialog(), usePrefixScanOverlay(), useScanStream(), v4NetBounds(), ScanEvent

### Community 79 - "Keyboard Shortcuts"
Cohesion: 0.53
Nodes (5): moveRowNav(), G_CHORDS, isEditableTarget(), modalOpen(), useGlobalShortcuts()

### Community 80 - "npm Scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 82 - "Chart Theme"
Cohesion: 0.50
Nodes (4): ChartTheme, FALLBACK, readTheme(), useChartTheme()

### Community 83 - "Status Tokens"
Cohesion: 0.40
Nodes (4): GRID_CELL_TOKENS, STATUS_TOKENS, StatusBadgeVariant, StatusTokenSet

### Community 84 - "Security Docs"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 86 - "OUI Lookup"
Cohesion: 0.67
Nodes (3): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for()

### Community 87 - "Backend Dependencies"
Cohesion: 0.50
Nodes (4): fastapi 0.115.6, pydantic 2.10.3, pydantic-settings 2.6.1, uvicorn[standard] 0.32.1

### Community 107 - "DB Stack Deps"
Cohesion: 0.67
Nodes (3): alembic 1.14.0, asyncpg 0.30.0, sqlalchemy[asyncio] 2.0.36

## Knowledge Gaps
- **273 isolated node(s):** `Draft`, `Row`, `SortKey`, `HandleState`, `SortableRowProps` (+268 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 875 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **55 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_lan_info()` connect `Settings & Redis API` to `Redis & Security Core`, `Changelog & Dashboard API`, `Scans API`?**
  _High betweenness centrality (0.248) - this node is a cross-community bridge._
- **Why does `LanInfo` connect `Settings & Redis API` to `Address List UI`?**
  _High betweenness centrality (0.241) - this node is a cross-community bridge._
- **Why does `_build_out()` connect `Settings & Redis API` to `Backup & Restore Service`, `Auth & Scans UI`, `Runtime Settings`?**
  _High betweenness centrality (0.162) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `User` (e.g. with `auth_status()` and `change_password()`) actually correct?**
  _`User` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `IPAddress` (e.g. with `DbState` and `load_state()`) actually correct?**
  _`IPAddress` has 18 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Draft`, `Row`, `SortKey` to the rest of the system?**
  _273 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Entity CRUD Pages` be split into smaller, more focused modules?**
  _Cohesion score 0.08289501367557332 - nodes in this community are weakly interconnected._