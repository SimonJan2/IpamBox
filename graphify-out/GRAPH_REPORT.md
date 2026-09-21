# Graph Report - IpamBox  (2026-09-22)

## Corpus Check
- 59 files · ~99,999 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2578 nodes · 6825 edges · 194 communities (105 shown, 61 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 473 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Entity CRUD API
- Entity CRUD Pages
- Addresses API
- Entity CRUD Pages (alt paths)
- Auth API
- Prefixes API
- Login & Ops Pages
- Changelog & Discovery UI
- Prefix Detail UI
- Import Planner
- Frontend Dependencies
- Changelog & Dashboard API
- Address List UI
- Root Layout & Tree Page
- Alembic Env & Backup API
- Route Error Pages
- Search API
- Scan VRF & Scanner Tests
- Entity CRUD Pages (src)
- Scan Policy Guard
- Sites API
- Backup Tests
- Docs Pages
- Redis Core
- Imports API
- Dashboard & General Settings UI
- Color Rules API
- Frontend Package Meta
- Scanner Pipeline
- Data & Users Settings UI
- Tags API
- VLANs API
- Import Wizard UI
- Maintenance API
- Redis Test Fakes
- RBAC Tests
- Scans API
- Color & Service Schemas
- Workbook Import Tests
- App Shell
- Color Rules Tests
- Frontend Deps (alt)
- Backup & Restore Service
- Ordering Tests
- Command Palette
- Runtime Settings
- Workbook Normalizers
- App Shell (src)
- Users API
- VRFs API
- Circuit & Range Schemas
- Import Wizard UI (alt)
- Docs Articles
- TS Config
- IPAM Extras Tests
- Compose Deployment
- Workbook Parsers
- Test Fixtures
- IP Ranges API
- Import Wizard UI (src)
- Prefs & Tags UI
- Color Rules UI
- Maintenance Tests
- Sheet Classification Tests
- Scheduled Backups API
- Cert & Dashboard Schemas
- Import Value Parsers
- Changelog Tests
- Settings Tests
- Workbook Import E2E
- Auth Tests
- Scan Found-Delta Tests
- Search Tests
- Normalizer Unit Tests
- VLAN Schemas
- Sheet Classification
- Scan Reconcile Tests
- Prefix API Tests
- Master Sheet Tests
- Color Rules Engine
- Page Stubs & CIDR Editor
- Next Config & Page Stubs
- History Panel UI
- Prefix Detail UI (src)
- Color Rules UI (src)
- Import Schemas
- Workbook Reader
- Allocation Tests
- Site Sheet Parser Tests
- Frontend DevDeps
- Asset Schemas
- Sheet Parsers
- Quick Scan Overlay
- Prefixes List UI (src)
- Tree Page
- Entity API Tests
- Tree Page (src)
- VLANs Page (src)
- Circuit Schemas
- Color Rule Schemas
- Circuits Parser Tests
- npm Scripts
- Breadcrumbs UI
- Shortcuts Overlay
- Chart Theme
- Security Docs
- VRFs Page (src)
- CSV Export
- OUI Lookup
- Inventory Parser
- Master Sheet Parser
- Backend Framework Deps
- Changelog Page
- Dashboard Page
- Settings Page
- Changelog UI (src)
- Inventory Page (src)
- Backup Page (src)
- Features Page (src)
- Changelog Schemas
- DB Stack Deps
- certificates page
- discovery page
- import page
- inventory page
- login page
- prefix detail page
- prefixes page
- scans page
- services page
- appearance page
- backup page
- data page
- security page
- users page
- sites page
- vlans page
- vrfs page
- Settings Nav
- Project Docs
- Security Page (src)
- Queue Deps
- Test Deps
- Next Env Types
- XFF Shim
- Next Config
- AllocateIPRequest
- patch fn
- patch fn (alt)
- bcrypt dep
- httpx dep
- openpyxl dep
- psutil dep
- scapy dep
- BaseModel
- App Icon
- Root Layout Meta
- VLANs Doc
- IPStatus Type
- PrefixCreate Schema
- PrefixOut Schema
- PrefixUpdate Schema
- Backup Tables Registry
- Env Example
- GitHub Repo
- MIT License

## God Nodes (most connected - your core abstractions)
1. `react` - 97 edges
2. `cn()` - 62 edges
3. `User` - 60 edges
4. `IPAddress` - 56 edges
5. `lucide-react` - 56 edges
6. `IPAMError` - 53 edges
7. `get_or_404()` - 51 edges
8. `Prefix` - 50 edges
9. `api` - 45 edges
10. `UserRole` - 43 edges

## Surprising Connections (you probably didn't know these)
- `LanInfo` --calls--> `_lan_info()`  [EXTRACTED]
  frontend/src/types/index.ts → backend/app/api/v1/settings.py
- `ImportBatchStatus` --uses--> `ImportBatchOut`  [INFERRED]
  backend/app/models/import_batch.py → backend/app/schemas/import_batch.py
- `ChangeLog` --uses--> `test_settings_changes_audited()`  [INFERRED]
  backend/app/models/change_log.py → backend/tests/test_settings.py
- `SettingsOut` --calls--> `_build_out()`  [EXTRACTED]
  frontend/src/types/index.ts → backend/app/api/v1/settings.py
- `SitesPage()` --calls--> `usePrefs()`  [EXTRACTED]
  app/sites/sites-client.tsx → lib/prefs.ts

## Import Cycles
- None detected.

## Communities (194 total, 61 thin omitted)

### Community 0 - "Entity CRUD API"
Cohesion: 0.07
Nodes (50): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), Audit trail via session flush hooks. before_flush collects (object, action,…, register() (+42 more)

### Community 1 - "Entity CRUD Pages"
Cohesion: 0.09
Nodes (52): CertificatesPage(), EMPTY, CircuitsPage(), EMPTY, BulkResp, AssetRow, EMPTY, InventoryPage() (+44 more)

### Community 2 - "Addresses API"
Cohesion: 0.05
Nodes (64): _address_csv_row(), _addresses_stmt(), bulk_addresses(), BulkBody, create_address(), delete_address(), export_addresses(), get_address() (+56 more)

### Community 3 - "Entity CRUD Pages (alt paths)"
Cohesion: 0.10
Nodes (42): EMPTY, EMPTY, AssetRow, EMPTY, EMPTY, ServiceRow, TagsPage(), VLAN_STATUSES (+34 more)

### Community 4 - "Auth API"
Cohesion: 0.09
Nodes (54): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+46 more)

### Community 5 - "Prefixes API"
Cohesion: 0.10
Nodes (50): allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), _prefix_rows() (+42 more)

### Community 6 - "Login & Ops Pages"
Cohesion: 0.06
Nodes (36): fmtEta(), ScansPage(), BackupSettingsPage(), downloadUrl(), fmtSize(), FEATURES, FeaturesPage(), Key (+28 more)

### Community 7 - "Changelog & Discovery UI"
Cohesion: 0.10
Nodes (30): ACTION_STYLES, BulkResp, PrefixesPage(), PrefixRow, utilColor(), AddressFilterPanel(), STATUSES, Button (+22 more)

### Community 8 - "Prefix Detail UI"
Cohesion: 0.07
Nodes (36): IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, SplitPlan, toggleIn(), AddressList(), AddrMapViewSwitcher() (+28 more)

### Community 9 - "Import Planner"
Cohesion: 0.10
Nodes (14): parse_sites_master_records(), _Planner, _preview(), (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Folded sheet title vs site name/code — word-boundary matching so 'int' doesn't…, Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new… (+6 more)

### Community 10 - "Frontend Dependencies"
Cohesion: 0.05
Nodes (41): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, lucide-react, next, @radix-ui/react-dialog (+33 more)

### Community 11 - "Changelog & Dashboard API"
Cohesion: 0.08
Nodes (34): list_changelog(), AsyncSession, get, stats(), confirm_discovered(), ConfirmBody, list_discovered(), AsyncSession (+26 more)

### Community 12 - "Address List UI"
Cohesion: 0.08
Nodes (30): AddressList(), buildRows(), IP_STATUSES, Row, sortAddr(), SortKey, InlineSelect(), ROLES (+22 more)

### Community 13 - "Root Layout & Tree Page"
Cohesion: 0.11
Nodes (33): metadata, ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), collectExpandableKeys(), flattenTree() (+25 more)

### Community 14 - "Alembic Env & Backup API"
Cohesion: 0.08
Nodes (26): do_run_migrations(), run_migrations_online(), download_backup(), list_scheduled_backups(), Restore a backup file (raw .json.gz body). Wipes every data table (users are…, Download a full snapshot (every table except users) as .json.gz.…, Scheduled snapshot files written by the worker into BACKUP_DIR., restore() (+18 more)

### Community 16 - "Search API"
Cohesion: 0.12
Nodes (31): _folded(), search(), match(), SearchAddress, SearchAsset, SearchCertificate, SearchCircuit, SearchJump (+23 more)

### Community 17 - "Scan VRF & Scanner Tests"
Cohesion: 0.09
Nodes (27): _global_vrf_id(), _infer_scan_vrf(), Pick the VRF for a scan that didn't specify one. An exact-match prefix living…, _scan_vrf(), WorkerSettings, _extra_vrf(), fake_arq(), _pool() (+19 more)

### Community 18 - "Entity CRUD Pages (src)"
Cohesion: 0.08
Nodes (12): EMPTY, EMPTY, ACTION_STYLES, BulkResp, fmtEta(), ScansPage(), EMPTY, ServiceRow (+4 more)

### Community 19 - "Scan Policy Guard"
Cohesion: 0.10
Nodes (32): _check_cidr_allowed(), set_actor(), get_effective(), AsyncSession, exclusion_hit(), Scan-target policy shared by the API route, the scheduler, and the worker.…, Return the first excluded CIDR overlapping ``net`` (either direction), or None.…, _due() (+24 more)

### Community 20 - "Sites API"
Cohesion: 0.11
Nodes (30): _cascade_site_fields(), create_site(), delete_site(), get_site(), list_sites(), AsyncSession, delete, get (+22 more)

### Community 21 - "Backup Tests"
Cohesion: 0.15
Nodes (34): Base, User, _backup_bytes(), _envelope_bytes(), _mkusers(), Hand-craft a backup envelope (e.g. with a forged users table)., Guard: every ORM table must be backed up (or explicitly excluded). Adding a new…, Fresh-server scenario: the migration-seeded Global VRF is replaced by the… (+26 more)

### Community 22 - "Docs Pages"
Cohesion: 0.11
Nodes (24): DocsIndexClient(), metadata, DocPage(), dynamicParams, generateMetadata(), loadMarkdown(), CommandPalette(), Icon (+16 more)

### Community 23 - "Redis Core"
Cohesion: 0.10
Nodes (28): ArqRedis, close_arq_pool(), close_redis(), get_arq_pool(), get_redis(), Shared process-wide Redis client. Do NOT aclose() it per call — connections…, Shut down the shared client — lifespan/worker shutdown only., Shared ARQ pool — callers must not close() it per job. (+20 more)

### Community 24 - "Imports API"
Cohesion: 0.12
Nodes (29): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+21 more)

### Community 25 - "Dashboard & General Settings UI"
Cohesion: 0.11
Nodes (19): ACTION_STYLES, expiryBadge(), PrefixStatusBadge(), prefixVariant, ScanStatusBadge(), scanVariant, Badge(), BadgeProps (+11 more)

### Community 26 - "Color Rules API"
Cohesion: 0.12
Nodes (24): create_rule(), delete_rule(), get_rule(), list_rules(), preview_rule(), reorder_rules(), rule_fields(), update_rule() (+16 more)

### Community 27 - "Frontend Package Meta"
Cohesion: 0.07
Nodes (23): name, private, version, Separator, Skeleton(), autoprefixer, clsx, postcss (+15 more)

### Community 28 - "Scanner Pipeline"
Cohesion: 0.11
Nodes (23): _arp_scan(), detect_interface(), detect_local_cidr(), _host_chunks(), HostResult, _icmp_sweep(), infer_device_type(), _ptr_lookup() (+15 more)

### Community 29 - "Data & Users Settings UI"
Cohesion: 0.13
Nodes (16): DataPage(), download(), ConfirmAction(), SETTINGS_SECTIONS, AuthContext, AuthCtx, authCtxValue(), AuthProvider (+8 more)

### Community 30 - "Tags API"
Cohesion: 0.15
Nodes (24): AssignBody, assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession (+16 more)

### Community 31 - "VLANs API"
Cohesion: 0.17
Nodes (24): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+16 more)

### Community 32 - "Import Wizard UI"
Cohesion: 0.09
Nodes (17): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, Step (+9 more)

### Community 33 - "Maintenance API"
Cohesion: 0.16
Nodes (24): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+16 more)

### Community 34 - "Redis Test Fakes"
Cohesion: 0.13
Nodes (18): str, ScanStatus, _FakeRedis, _mk_job(), In-memory stand-in for the worker's redis client (get/set/publish)., Point the worker at the test DB (sf) and the fake redis client., Cancel flag polled between phases -> ScanCancelled -> CANCELLED, and no…, Audit race: API writes CANCELLED mid-scan while the redis flag is lost… (+10 more)

### Community 35 - "RBAC Tests"
Cohesion: 0.20
Nodes (20): str, UserRole, fake_arq(), login(), mkuser(), other_client(), allow_insecure keeps full access (existing behavior preserved)., test_admin_can_step_down_once_second_admin_exists() (+12 more)

### Community 36 - "Scans API"
Cohesion: 0.15
Nodes (22): cancel_scan(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession, get, post (+14 more)

### Community 37 - "Color & Service Schemas"
Cohesion: 0.10
Nodes (13): hex_color_or_none(), Shared row/tag color validator: #rrggbb, normalized to lowercase., ServiceCreate, ServiceOut, ServiceUpdate, SiteCreate, SiteOut, SiteUpdate (+5 more)

### Community 38 - "Workbook Import Tests"
Cohesion: 0.18
Nodes (12): _master_row(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind…, Mashapan TA + MATPASH share number 200 — merge + conflict, not a silent… (+4 more)

### Community 39 - "App Shell"
Cohesion: 0.11
Nodes (17): AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS, NavGroup, NavItem, NavLink() (+9 more)

### Community 40 - "Color Rules Tests"
Cohesion: 0.22
Nodes (22): auth_on(), _login(), _mk_rule(), _mk_site(), _mkuser(), AsyncClient, AsyncSession, fixture (+14 more)

### Community 41 - "Frontend Deps (alt)"
Cohesion: 0.09
Nodes (23): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, lucide-react, next, @radix-ui/react-dialog (+15 more)

### Community 42 - "Backup & Restore Service"
Cohesion: 0.12
Nodes (22): Delete assignments whose target no longer exists. For non-ORM write paths…, sweep_orphans(), BackupError, BackupPreview, build_backup(), _from_json(), _gunzip(), inspect_backup() (+14 more)

### Community 43 - "Ordering Tests"
Cohesion: 0.22
Nodes (21): auth_on(), _circuit_order(), _login(), _mk_circuits(), _mkuser(), AsyncClient, AsyncSession, fixture (+13 more)

### Community 44 - "Command Palette"
Cohesion: 0.16
Nodes (19): CommandPalette(), Icon, Item, itemsFor(), remember(), SearchOut, PrefsInit(), AddrMapView (+11 more)

### Community 45 - "Runtime Settings"
Cohesion: 0.13
Nodes (17): Effective, _env_sourced(), Any, Exception, Runtime-editable settings: app_settings rows override env defaults. Each public…, True when the field's current value differs from its declared default., Carries {key: message} so the API can return per-field 422s., One runtime-editable setting. field: the env-backed attribute on… (+9 more)

### Community 46 - "Workbook Normalizers"
Cohesion: 0.11
Nodes (19): _clean_octets(), fold_hebrew(), map_status(), mask_to_prefixlen(), network_of(), norm_mac(), parse_vlan(), Cell-level normalizers for the Network_Address workbook. Pure functions — unit-… (+11 more)

### Community 47 - "App Shell (src)"
Cohesion: 0.13
Nodes (15): AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS, NavGroup, NavItem, NavLink() (+7 more)

### Community 48 - "Users API"
Cohesion: 0.18
Nodes (17): _admin_count(), create_user(), delete_user(), list_users(), _out(), update_user(), UserCreate, UserUpdate (+9 more)

### Community 49 - "VRFs API"
Cohesion: 0.19
Nodes (14): create_vrf(), delete_vrf(), list_vrfs(), reorder_vrfs(), update_vrf(), Base, VRF, POST /{entity}/reorder payload: row ids in their new display order. (+6 more)

### Community 50 - "Circuit & Range Schemas"
Cohesion: 0.15
Nodes (10): IPRangeRole, str, CircuitOut, ip_display(), Any, Normalize asyncpg-returned ipaddress objects / strings to display form. INET…, to_int(), IPRangeCreate (+2 more)

### Community 51 - "Import Wizard UI (alt)"
Cohesion: 0.14
Nodes (13): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, Step (+5 more)

### Community 52 - "Docs Articles"
Cohesion: 0.18
Nodes (19): Accounts & Roles, IP Addresses, Certificates, Changelog, Circuits, Discovery Inbox, Hierarchy Tree, Import (+11 more)

### Community 53 - "TS Config"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 54 - "IPAM Extras Tests"
Cohesion: 0.22
Nodes (17): _prefix(), export.csv takes the same filters as the list endpoint — a filtered view…, Same filtered-export treatment on the prefixes CSV (F8)., A documented v6 /64's 2^64 host count must not reach dashboard sums (~1.8e19 >…, test_address_role_nat_and_bulk(), test_addresses_export_respects_filters(), test_bulk_reports_real_counts(), test_container_move_with_children_rejected() (+9 more)

### Community 55 - "Compose Deployment"
Cohesion: 0.19
Nodes (18): alembic upgrade head on api start, API_BIND publish binding, api service, backupdata volume, backupdata Volume, IPAMBOX_COOKIE_SECURE env, db service (postgres:16-alpine), ipam bridge network 192.0.2.0/24 (+10 more)

### Community 56 - "Workbook Parsers"
Cohesion: 0.16
Nodes (12): _blocks(), _col_class(), _is_header_echo(), _map_columns(), parse_site_sheet(), _positional_columns(), Per-family sheet parsers -> normalized record dicts. Every parser takes…, Split duplicated column groups (031-style runaway): each block starts at an… (+4 more)

### Community 57 - "Test Fixtures"
Cohesion: 0.21
Nodes (15): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., session() (+7 more)

### Community 58 - "IP Ranges API"
Cohesion: 0.21
Nodes (14): _check_range_overlap(), create_range(), delete_range(), list_ranges(), AsyncSession, delete, get, post (+6 more)

### Community 59 - "Import Wizard UI (src)"
Cohesion: 0.13
Nodes (10): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, Step (+2 more)

### Community 60 - "Prefs & Tags UI"
Cohesion: 0.19
Nodes (14): TagsPage(), AddrMapView, applyPrefs(), DEFAULT_PREFS, DensityChoice, getPrefs(), Prefs, resolveTheme() (+6 more)

### Community 61 - "Color Rules UI"
Cohesion: 0.15
Nodes (11): ColorRulesPage(), Draft, ENTITIES, OP_LABEL, OPS_BY_TYPE, opsFor(), RuleDialog(), metadata (+3 more)

### Community 62 - "Maintenance Tests"
Cohesion: 0.21
Nodes (11): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_now_enqueues(), test_clear_discovery() (+3 more)

### Community 63 - "Sheet Classification Tests"
Cohesion: 0.24
Nodes (3): _matrix(), TestClassify, TestSiteSheetParser

### Community 64 - "Scheduled Backups API"
Cohesion: 0.23
Nodes (13): delete_scheduled_backup(), download_scheduled_backup(), backup_dir(), delete_backup_file(), list_backup_files(), prune_backups(), Path, Fetch a scheduled backup by file name (path-traversal safe). (+5 more)

### Community 65 - "Cert & Dashboard Schemas"
Cohesion: 0.21
Nodes (8): CertificateCreate, CertificateOut, CertificateUpdate, DashboardStats, MacMismatchItem, ScanConfigOut, ScanCreate, ScanJobOut

### Community 66 - "Import Value Parsers"
Cohesion: 0.22
Nodes (11): assemble_ip(), clean(), parse_range_end(), parse_site_number(), 10.79.1.' + '101-200' -> ('10.79.1.101', '10.79.1.200')., Cell -> stripped single-line string; gershayim and star-runs fixed., Combine a base column ('10.2.1.' / '10.192.10' / '10.0.0') with the 'end ip'…, _leftover_bits() (+3 more)

### Community 67 - "Changelog Tests"
Cohesion: 0.23
Nodes (12): AsyncClient, tag_assignments.object_id has no FK — deleting a tagged object must drop its…, Tag.assignments is already ORM delete-orphan — each removed assignment lands in…, PATCH settings with a null value deletes the app_settings row — that delete…, /addresses/bulk action=delete used to issue one Core DELETE — invisible to the…, test_bulk_delete_writes_changelog_entries(), test_changelog_captures_ip_status_change(), test_changelog_records_crud() (+4 more)

### Community 68 - "Settings Tests"
Cohesion: 0.18
Nodes (5): fake_arq(), _pool(), _FakeArqJob, _FakePool, test_settings_changes_audited()

### Community 69 - "Workbook Import E2E"
Cohesion: 0.18
Nodes (8): Workbook import: normalizer/parser unit tests (no DB) + API e2e., Small synthetic workbook: sites master + one site sheet + circuits., test_commit_twice_rejected(), test_import_e2e(), TestAssetsParser, TestCertificatesParser, TestServersParser, _xlsx_bytes()

### Community 70 - "Auth Tests"
Cohesion: 0.29
Nodes (11): AsyncClient, When the socket peer isn't in ipambox_trusted_proxies, a supplied XFF is…, Spreading failures across many usernames from one IP trips the aggregate lock —…, Five bad logins for one (user, ip) pair must not lock out other users on the…, test_endpoints_require_auth(), test_lockout_keyed_per_user_ip_pair(), test_login_lockout(), test_per_ip_aggregate_backstop() (+3 more)

### Community 71 - "Scan Found-Delta Tests"
Cohesion: 0.21
Nodes (8): on_hosts fires once per detection step with that chunk's new IPs — ARP batch…, When L2+L3 find nothing, the TCP fallback publishes its batch too., test_scan_cidr_emits_found_deltas(), fake_icmp(), fake_probe(), fake_ptr(), on_hosts(), test_scan_cidr_tcp_fallback_reports_found()

### Community 72 - "Search Tests"
Cohesion: 0.27
Nodes (8): auth_on(), _seed(), test_addresses_q_filter_not_broken(), test_search_grouped_results(), test_search_hebrew_folding(), test_search_ip_jump(), test_search_ip_jump_prefers_owner_then_deepest(), fixture

### Community 74 - "VLAN Schemas"
Cohesion: 0.27
Nodes (8): str, VLANStatus, VLANCreate, VLANGroupCreate, VLANGroupOut, VLANGroupUpdate, VLANOut, VLANUpdate

### Community 75 - "Sheet Classification"
Cohesion: 0.27
Nodes (9): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, norm_header(), Header cell -> lowercase, single-spaced, for signature matching. Edge…, parse_servers() (+1 more)

### Community 76 - "Scan Reconcile Tests"
Cohesion: 0.27
Nodes (10): AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), A stored (e.g. imported) MAC that differs from the scan is flagged in…, Scanning a /24 under a documented /16 must not mark the other 255 subnets'…, test_reconcile_flags_mac_mismatch(), test_reconcile_offline_sweep_scoped_to_scanned_net(), test_reconcile_persists_ports_and_type() (+2 more)

### Community 77 - "Prefix API Tests"
Cohesion: 0.38
Nodes (9): _global_vrf_id(), test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_prefixes_order_by_utilization_and_limit(), test_same_cidr_allowed_across_vrfs(), test_split_cardinality_cap(), test_split_endpoint(), test_tree_endpoint() (+1 more)

### Community 78 - "Master Sheet Tests"
Cohesion: 0.20
Nodes (5): Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins., TestSitesMasterParser

### Community 79 - "Color Rules Engine"
Cohesion: 0.39
Nodes (9): _as_date(), _as_str(), display_color_for(), _ordered_cmp(), Any, -1/0/1 comparing a column value to a rule's value string. Tries date first when…, Does ``rule`` fire on this row? NULL fields never match., Effective row color: manual row_color beats every rule. (+1 more)

### Community 80 - "Page Stubs & CIDR Editor"
Cohesion: 0.22
Nodes (3): metadata, metadata, react

### Community 81 - "Next Config & Page Stubs"
Cohesion: 0.22
Nodes (4): nextConfig, metadata, metadata, next

### Community 82 - "History Panel UI"
Cohesion: 0.28
Nodes (7): ACTION_STYLES, ChangeDiff(), ChangeVal(), fmtChangeVal(), HistoryEntry(), summary(), ChangeLogEntry

### Community 83 - "Prefix Detail UI (src)"
Cohesion: 0.25
Nodes (6): IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, SplitPlan, toggleIn()

### Community 84 - "Color Rules UI (src)"
Cohesion: 0.25
Nodes (6): Draft, ENTITIES, OP_LABEL, OPS_BY_TYPE, opsFor(), RuleDialog()

### Community 85 - "Import Schemas"
Cohesion: 0.25
Nodes (7): CommitOptions, ImportBatchOut, PreviewOptions, Per-sheet detection result shown in the wizard., User-confirmed mapping choices applied before building the plan., RowResult, SheetPreview

### Community 86 - "Workbook Reader"
Cohesion: 0.36
Nodes (5): Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, load_workbook_bytes(), XLSX -> sheet matrices via openpyxl (read_only streams, values only)., Parse workbook bytes into per-sheet row matrices. read_only + data_only:…, SheetMatrix

### Community 87 - "Allocation Tests"
Cohesion: 0.43
Nodes (7): _mk_prefix(), test_address_crud_and_dup_guard(), test_allocation_skips_existing(), test_concurrent_allocation_unique(), alloc(), test_exhausted_prefix_conflicts(), test_sequential_allocation_skips_boundaries()

### Community 88 - "Site Sheet Parser Tests"
Cohesion: 0.25
Nodes (4): MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf., Bare 'Name' (Cellular) maps to the hostname field., Non-empty unnamed columns pile into cf['extra'] instead of vanishing (Pelephone…, TestSiteSheetExtras

### Community 89 - "Frontend DevDeps"
Cohesion: 0.25
Nodes (8): devDependencies, autoprefixer, postcss, tailwindcss, @types/node, @types/react, @types/react-dom, typescript

### Community 90 - "Asset Schemas"
Cohesion: 0.43
Nodes (5): AssetKind, str, AssetCreate, AssetOut, AssetUpdate

### Community 91 - "Sheet Parsers"
Cohesion: 0.29
Nodes (6): excel_date(), datetime/date passthrough; int/float serial (20000-80000) -> date; 'd/m/yy'…, parse_assets(), parse_certificates(), Positional 5-col layout: platform, target/VS, server, cert, expiry., 003 תוכנות וחומרות: סוג,חברה,דגם,שם התוכנה,ייעוד,גירסה,EOL,…

### Community 92 - "Quick Scan Overlay"
Cohesion: 0.38
Nodes (6): QuickScanDialog(), usePrefixScanOverlay(), useScanStream(), v4NetBounds(), ScanEvent, ScanJob

### Community 93 - "Prefixes List UI (src)"
Cohesion: 0.33
Nodes (3): PrefixesPage(), PrefixRow, utilColor()

### Community 94 - "Tree Page"
Cohesion: 0.53
Nodes (5): ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText()

### Community 96 - "Tree Page (src)"
Cohesion: 0.53
Nodes (5): ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText()

### Community 100 - "Circuits Parser Tests"
Cohesion: 0.40
Nodes (3): קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., TestCircuitsParser

### Community 101 - "npm Scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 102 - "Breadcrumbs UI"
Cohesion: 0.50
Nodes (3): Crumb, findChain(), PrefixBreadcrumbs()

### Community 104 - "Chart Theme"
Cohesion: 0.50
Nodes (4): ChartTheme, FALLBACK, readTheme(), useChartTheme()

### Community 105 - "Security Docs"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 109 - "OUI Lookup"
Cohesion: 0.67
Nodes (3): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for()

### Community 110 - "Inventory Parser"
Cohesion: 0.50
Nodes (4): PCB Serial Number : 31231187' -> ['31231187']; multi-line cells -> one serial…, split_serial_blob(), parse_inventory(), 105/106 serial-number lists -> hardware assets.

### Community 111 - "Master Sheet Parser"
Cohesion: 0.50
Nodes (3): _master_blocks(), parse_sites_master(), (first, second) octet pairs a master row declares — lets sheet->site matching…

### Community 112 - "Backend Framework Deps"
Cohesion: 0.50
Nodes (4): fastapi 0.115.6, pydantic 2.10.3, pydantic-settings 2.6.1, uvicorn[standard] 0.32.1

### Community 118 - "Backup Page (src)"
Cohesion: 0.83
Nodes (3): BackupSettingsPage(), downloadUrl(), fmtSize()

### Community 138 - "DB Stack Deps"
Cohesion: 0.67
Nodes (3): alembic 1.14.0, asyncpg 0.30.0, sqlalchemy[asyncio] 2.0.36

## Knowledge Gaps
- **364 isolated node(s):** `BulkResp`, `AssetRow`, `ServiceRow`, `VlanRow`, `SwitchProps` (+359 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1012 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **61 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_lan_info()` connect `Scans API` to `Changelog & Dashboard API`, `Login & Ops Pages`, `Redis Core`?**
  _High betweenness centrality (0.198) - this node is a cross-community bridge._
- **Why does `LanInfo` connect `Login & Ops Pages` to `Scans API`?**
  _High betweenness centrality (0.193) - this node is a cross-community bridge._
- **Why does `_build_out()` connect `Changelog & Dashboard API` to `Scan Policy Guard`, `Scans API`, `Login & Ops Pages`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `User` (e.g. with `bulk_addresses()` and `auth_status()`) actually correct?**
  _`User` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `IPAddress` (e.g. with `_address_csv_row()` and `_addresses_stmt()`) actually correct?**
  _`IPAddress` has 18 INFERRED edges - model-reasoned connections that need verification._
- **What connects `BulkResp`, `AssetRow`, `ServiceRow` to the rest of the system?**
  _364 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Entity CRUD API` be split into smaller, more focused modules?**
  _Cohesion score 0.06925624811803674 - nodes in this community are weakly interconnected._