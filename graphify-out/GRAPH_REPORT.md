# Graph Report - IpamBox  (2026-09-21)

## Corpus Check
- 0 files · ~0 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2079 nodes · 5417 edges · 155 communities (82 shown, 50 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 346 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Changelog UI & Utils
- Entity CRUD Pages
- VLAN API
- Backup Service & Models
- Color Rules API
- Shared Types & Form UI
- Workbook Normalizers
- Import Planner
- Frontend API Client
- App Shell & Frontend Auth
- Prefix Detail & Address UI
- Maintenance API
- Entity CRUD Factory
- Route Error Boundaries
- Search & Prefix Math
- Auth & Sessions
- IPAddress Model
- Addresses API
- Settings Pages UI
- Scanner Pipeline
- Config & Redis Clients
- Workbook Parser Tests
- RBAC & User Tests
- Import API
- Sites API
- Scans API
- Auth & Sessions
- Runtime Settings
- Worker & Scan Orchestration
- Import Executor
- Import Plan Tests
- Settings API
- Site Sheet Parsing Tests
- UI Primitives & Scripts
- Frontend Dependencies
- Command Palette & Prefs
- Auth Deps & Permissions
- Scanner Tests
- Prefs & Row Navigation
- IPAM Service Core
- IPAM Service Core
- RBAC & User Tests
- TypeScript Config
- IP Range Schemas
- Docker Compose Services
- Prefix Tree View
- Prefix Tree View
- Dashboard UI
- Changelog UI & Utils
- Reconcile Tests
- Row-Ordering Tests
- Prefix Detail & Address UI
- Prefix Detail & Address UI
- Tags API
- Master Sites Parser Tests
- Settings Tests
- Sheet Classification
- Dashboard UI
- Backup File IO
- Users API
- Test Fixtures & Allocation
- Scan Delta Tests
- Loading & Separator UI
- Prefix API Tests
- Normalize Tests
- Scanner Tests
- Auth & Search Tests
- Root Layout & Prefs Init
- Entity CRUD Pages
- IPAM Service Core
- Frontend Build Deps
- Positional Column Parsing
- UI Primitives & Scripts
- Tree Page Texts
- Entity CRUD Tests
- Next.js Config
- App Shell & Frontend Auth
- Shortcuts Overlay
- Security Policy Doc
- Backup Restore
- CSV Export
- Scanner Pipeline
- Backend Core Deps
- RBAC & User Tests
- Python Web Deps
- DB Driver Deps
- RBAC & User Tests
- Certificates Page
- Circuits Page
- Discovery Page
- Import Page
- Next.js Config
- Login Page
- Prefixes Page
- Scans Page
- Services Page
- Appearance Page
- Backup Page
- Data Page
- Security Page
- Users Page
- Setup Page
- Sites Page
- Tags Page
- VLANs Page
- VRFs Page
- Settings Navigation
- Seeding Service
- Database Deps
- Queue Deps
- Test Deps
- Next Env Types
- XFF Shim
- Queue & Redis Deps
- Test Framework Deps
- bcrypt Dep
- httpx Dep
- openpyxl Dep
- psutil Dep
- Scapy Dep
- App Icon
- Root Layout
- App Icon
- Backup Tables Registry
- Env Example
- GitHub Repo
- MIT License
- Auth Dep (bcrypt)
- HTTP Client Dep
- Excel Import Dep
- System Info Dep
- Packet Scan Dep

## God Nodes (most connected - your core abstractions)
1. `react` - 84 edges
2. `User` - 54 edges
3. `cn()` - 51 edges
4. `lucide-react` - 43 edges
5. `Base` - 42 edges
6. `get_or_404()` - 39 edges
7. `_matrix()` - 39 edges
8. `IPAMError` - 38 edges
9. `_Planner` - 37 edges
10. `UserRole` - 35 edges

## Surprising Connections (you probably didn't know these)
- `AllocateIPRequest` --uses--> `IPStatus`  [INFERRED]
  backend/app/schemas/prefix.py → backend/app/models/ip_address.py
- `ChangeLog` --uses--> `test_settings_changes_audited()`  [INFERRED]
  backend/app/models/change_log.py → backend/tests/test_settings.py
- `ScanJob` --calls--> `create_scan()`  [EXTRACTED]
  frontend/src/types/index.ts → backend/app/api/v1/scans.py
- `SavedViews()` --calls--> `usePrefs()`  [EXTRACTED]
  components/saved-views.tsx → lib/prefs.ts
- `SitesPage()` --calls--> `usePrefs()`  [EXTRACTED]
  app/sites/sites-client.tsx → lib/prefs.ts

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **async FastAPI + SQLAlchemy + Postgres API stack** — requirements_fastapi, requirements_uvicorn, requirements_sqlalchemy, requirements_asyncpg, requirements_pydantic [INFERRED 0.85]

## Communities (155 total, 50 thin omitted)

### Community 0 - "Changelog UI & Utils"
Cohesion: 0.06
Nodes (67): CertificatesPage(), EMPTY, CircuitsPage(), EMPTY, AssetRow, EMPTY, InventoryPage(), EMPTY (+59 more)

### Community 1 - "Entity CRUD Pages"
Cohesion: 0.10
Nodes (54): CertificatesPage(), EMPTY, CircuitsPage(), EMPTY, BulkResp, AssetRow, EMPTY, InventoryPage() (+46 more)

### Community 2 - "VLAN API"
Cohesion: 0.08
Nodes (56): _crud_router(), create_item(), delete_item(), get_item(), list_items(), reorder_items(), update_item(), get_site() (+48 more)

### Community 3 - "Backup Service & Models"
Cohesion: 0.12
Nodes (29): before_flush(), _columns(), _create_changes(), _delete_changes(), Audit trail via session flush hooks. before_flush collects (object, action,…, _ser(), _update_changes(), metrics() (+21 more)

### Community 4 - "Color Rules API"
Cohesion: 0.08
Nodes (38): create_rule(), delete_rule(), get_rule(), list_rules(), preview_rule(), reorder_rules(), rule_fields(), update_rule() (+30 more)

### Community 5 - "Shared Types & Form UI"
Cohesion: 0.05
Nodes (38): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, Step (+30 more)

### Community 6 - "Workbook Normalizers"
Cohesion: 0.08
Nodes (41): assemble_ip(), clean(), _clean_octets(), map_status(), mask_to_prefixlen(), network_of(), norm_header(), norm_mac() (+33 more)

### Community 7 - "Import Planner"
Cohesion: 0.10
Nodes (14): parse_sites_master_records(), _Planner, _preview(), (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Folded sheet title vs site name/code — word-boundary matching so 'int' doesn't…, Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new… (+6 more)

### Community 8 - "Frontend API Client"
Cohesion: 0.09
Nodes (25): fmtEta(), ScansPage(), DataPage(), download(), ConfirmAction(), ConfirmDialog(), TAG_COLORS, TagDialog() (+17 more)

### Community 9 - "App Shell & Frontend Auth"
Cohesion: 0.08
Nodes (29): fmtAgo(), SecurityPage(), AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS, NavGroup (+21 more)

### Community 10 - "Prefix Detail & Address UI"
Cohesion: 0.07
Nodes (32): AddressList(), buildRows(), IP_STATUSES, Row, sortAddr(), SortKey, InlineSelect(), ROLES (+24 more)

### Community 11 - "Maintenance API"
Cohesion: 0.08
Nodes (34): list_changelog(), stats(), _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans() (+26 more)

### Community 12 - "Entity CRUD Factory"
Cohesion: 0.09
Nodes (17): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, AssetKind, AssetCreate, AssetOut, AssetUpdate, CertificateCreate, CertificateOut, CertificateUpdate (+9 more)

### Community 14 - "Search & Prefix Math"
Cohesion: 0.12
Nodes (31): _folded(), search(), match(), SearchAddress, SearchAsset, SearchCertificate, SearchCircuit, SearchJump (+23 more)

### Community 15 - "Auth & Sessions"
Cohesion: 0.15
Nodes (30): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+22 more)

### Community 16 - "IPAddress Model"
Cohesion: 0.11
Nodes (22): confirm_discovered(), ConfirmBody, list_discovered(), Unconfirmed hosts found by scanners, pending admin review., One-click confirm a discovered host (default -> Active)., IPAddress, IPRole, IPStatus (+14 more)

### Community 17 - "Addresses API"
Cohesion: 0.12
Nodes (31): _address_csv_row(), _addresses_stmt(), bulk_addresses(), BulkBody, create_address(), delete_address(), export_addresses(), get_address() (+23 more)

### Community 18 - "Settings Pages UI"
Cohesion: 0.10
Nodes (20): ACTION_STYLES, metadata, SettingsPage(), expiryBadge(), PrefixStatusBadge(), prefixVariant, ScanStatusBadge(), scanVariant (+12 more)

### Community 19 - "Scanner Pipeline"
Cohesion: 0.09
Nodes (26): _arp_scan(), _host_chunks(), HostResult, _icmp_sweep(), infer_device_type(), _ptr_lookup(), Raised inside the pipeline when the user cancels the scan., Blocking scapy ARP sweep -> {ip: mac}. Runs in a thread. (+18 more)

### Community 20 - "Config & Redis Clients"
Cohesion: 0.12
Nodes (16): do_run_migrations(), run_migrations_online(), get_settings(), get_redis(), create_session(), Readiness probe: verifies DB + Redis connectivity., readyz(), auth_on() (+8 more)

### Community 21 - "Workbook Parser Tests"
Cohesion: 0.10
Nodes (19): Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, excel_date(), datetime/date passthrough; int/float serial (20000-80000) -> date; 'd/m/yy'…, parse_assets(), parse_certificates(), Positional 5-col layout: platform, target/VS, server, cert, expiry., 003 תוכנות וחומרות: סוג,חברה,דגם,שם התוכנה,ייעוד,גירסה,EOL,…, load_workbook_bytes() (+11 more)

### Community 22 - "RBAC & User Tests"
Cohesion: 0.20
Nodes (27): _backup_bytes(), _envelope_bytes(), _mkusers(), Hand-craft a backup envelope (e.g. with a forged users table)., Fresh-server scenario: the migration-seeded Global VRF is replaced by the…, Fresh-server scenario: the target's admins survive; its non-admin set is fully…, A forged users table without the includes_users flag is treated as unknown and…, _restore() (+19 more)

### Community 23 - "Import API"
Cohesion: 0.15
Nodes (24): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), Workbook import endpoints: upload -> detect -> preview -> commit. The uploaded… (+16 more)

### Community 24 - "Sites API"
Cohesion: 0.14
Nodes (20): _cascade_site_fields(), create_site(), delete_site(), Propagate site code/number/name changes to linked entities that were following…, update_site(), create_tag(), update_tag(), Site (+12 more)

### Community 25 - "Scans API"
Cohesion: 0.14
Nodes (22): cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), _job_payload(), list_scans(), SSE stream of scan progress (Redis pub/sub backed)., Effective scanner configuration surfaced to the UI. (+14 more)

### Community 26 - "Auth & Sessions"
Cohesion: 0.14
Nodes (24): Guard for every API route. Returns the User, or None in allow_insecure mode., require_auth(), clear_login_failures(), client_ip(), destroy_session(), destroy_session_by_suffix(), _fails_key(), get_session_user_id() (+16 more)

### Community 27 - "Runtime Settings"
Cohesion: 0.10
Nodes (13): psycopg2-style URL for alembic offline mode / scripts., Settings, Effective, _env_sourced(), get_effective(), Runtime-editable settings: app_settings rows override env defaults. Each public…, True when the field's current value differs from its declared default., One runtime-editable setting. field: the env-backed attribute on… (+5 more)

### Community 28 - "Worker & Scan Orchestration"
Cohesion: 0.11
Nodes (23): _due(), _eta_seconds(), _publish(), ARQ job: execute a scan and reconcile results., Enqueue a scan for every configured network (effective settings). Targets:…, Write a full snapshot into BACKUP_DIR, prune old ones., Runs every minute: fires scheduled scans/backups whose configured interval has…, Fail live jobs that outlived the worker's job_timeout. An OOM-killed or… (+15 more)

### Community 29 - "Import Executor"
Cohesion: 0.13
Nodes (19): PrefixStatus, AllocateIPRequest, AvailableIPOut, PrefixCreate, PrefixOut, PrefixSplitOut, PrefixUpdate, VlanRefOut (+11 more)

### Community 30 - "Import Plan Tests"
Cohesion: 0.18
Nodes (12): _master_row(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind…, Mashapan TA + MATPASH share number 200 — merge + conflict, not a silent… (+4 more)

### Community 31 - "Settings API"
Cohesion: 0.16
Nodes (20): _build_out(), _lan_info(), _mask_url(), Hide the password in a scheme://user:pass@host URL., LAN identity detected by the host-networked worker (written to Redis). Falls…, read_settings(), update_settings(), LanInfo (+12 more)

### Community 32 - "Site Sheet Parsing Tests"
Cohesion: 0.15
Nodes (12): _blocks(), parse_site_sheet(), Split duplicated column groups (031-style runaway): each block starts at an…, _matrix(), קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf., Bare 'Name' (Cellular) maps to the hostname field. (+4 more)

### Community 33 - "UI Primitives & Scripts"
Cohesion: 0.09
Nodes (21): name, private, scripts, build, dev, lint, start, version (+13 more)

### Community 34 - "Frontend Dependencies"
Cohesion: 0.09
Nodes (23): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, lucide-react, next, @radix-ui/react-dialog (+15 more)

### Community 35 - "Command Palette & Prefs"
Cohesion: 0.14
Nodes (17): Switch, SwitchProps, CommandPalette(), Icon, Item, itemsFor(), remember(), SearchOut (+9 more)

### Community 36 - "Auth Deps & Permissions"
Cohesion: 0.14
Nodes (20): download_backup(), list_scheduled_backups(), Restore a backup file (raw .json.gz body). Wipes every data table (users are…, Download a full snapshot (every table except users) as .json.gz.…, Scheduled snapshot files written by the worker into BACKUP_DIR., restore(), has_perm(), _dep() (+12 more)

### Community 37 - "Scanner Tests"
Cohesion: 0.16
Nodes (15): _global_vrf_id(), _infer_scan_vrf(), Pick the VRF for a scan that didn't specify one. An exact-match prefix living…, _extra_vrf(), _global_id(), _mk_prefix(), The cap is a runtime setting: lowering it to 2 rejects a /24., Enqueue-time bounds: a /8 (~16.7M usable) blows past scan_max_hosts (default… (+7 more)

### Community 38 - "Prefs & Row Navigation"
Cohesion: 0.13
Nodes (18): metadata, PrintClient(), VrfsPage(), IpDrawer(), AddrMapView, applyPrefs(), DEFAULT_PREFS, DensityChoice (+10 more)

### Community 39 - "IPAM Service Core"
Cohesion: 0.18
Nodes (19): delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), _prefix_rows(), prefix_tree(), AsyncSession (+11 more)

### Community 40 - "IPAM Service Core"
Cohesion: 0.16
Nodes (18): build_tree(), site_node(), vrf_node(), vrf_prefix_tree(), prefix_node(), ConflictError, NotFoundError, prefix_stats() (+10 more)

### Community 41 - "RBAC & User Tests"
Cohesion: 0.29
Nodes (18): UserRole, login(), mkuser(), other_client(), allow_insecure keeps full access (existing behavior preserved)., test_admin_can_step_down_once_second_admin_exists(), test_admin_cannot_delete_last_user(), test_admin_full_access() (+10 more)

### Community 42 - "TypeScript Config"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 43 - "IP Range Schemas"
Cohesion: 0.22
Nodes (11): _check_range_overlap(), create_range(), delete_range(), list_ranges(), update_range(), IPRange, IPRangeRole, A named block of addresses inside a prefix (e.g. a DHCP scope). Any defined… (+3 more)

### Community 44 - "Docker Compose Services"
Cohesion: 0.19
Nodes (18): alembic upgrade head on api start, API_BIND publish binding, api service, backupdata volume, backupdata Volume, IPAMBOX_COOKIE_SECURE env, db service (postgres:16-alpine), ipam bridge network 192.0.2.0/24 (+10 more)

### Community 45 - "Prefix Tree View"
Cohesion: 0.18
Nodes (14): metadata, ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), Select, SelectContent (+6 more)

### Community 46 - "Prefix Tree View"
Cohesion: 0.20
Nodes (15): collectExpandableKeys(), flattenTree(), prefixKey(), PrefixTree(), siteKey(), TreeRow, utilColor(), vrfAgg() (+7 more)

### Community 47 - "Dashboard UI"
Cohesion: 0.15
Nodes (11): ACTION_STYLES, ChangelogPage(), metadata, ACTION_STYLES, ChangeDiff(), ChangeVal(), fmtChangeVal(), HistoryEntry() (+3 more)

### Community 48 - "Changelog UI & Utils"
Cohesion: 0.19
Nodes (13): Input, Textarea, Label, Progress, Table(), TableBody(), TableCell(), TableHead() (+5 more)

### Community 49 - "Reconcile Tests"
Cohesion: 0.25
Nodes (15): _prefix(), export.csv takes the same filters as the list endpoint — a filtered view…, Same filtered-export treatment on the prefixes CSV (F8)., test_address_role_nat_and_bulk(), test_addresses_export_respects_filters(), test_bulk_reports_real_counts(), test_container_move_with_children_rejected(), test_csv_export_import() (+7 more)

### Community 50 - "Row-Ordering Tests"
Cohesion: 0.26
Nodes (12): _circuit_order(), _login(), _mk_circuits(), _mkuser(), test_new_row_appends_after_positioned(), test_pinned_rows_sort_first(), test_reorder_and_pin_require_write_perm(), test_reorder_persists() (+4 more)

### Community 51 - "Prefix Detail & Address UI"
Cohesion: 0.17
Nodes (12): IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, SplitPlan, toggleIn(), QuickScanDialog(), usePrefixScanOverlay() (+4 more)

### Community 52 - "Prefix Detail & Address UI"
Cohesion: 0.13
Nodes (12): CELL_SIZE, cellLabel(), CellState, STATUS_ORDER, SubnetGrid(), AddressPage, IpRange, IpStatus (+4 more)

### Community 53 - "Tags API"
Cohesion: 0.24
Nodes (10): assign_tag(), list_assignments(), unassign_tag(), Polymorphic tag link — attaches a Tag to a Site/VRF/Prefix/IPAddress., TagAssignment, AssignBody, TagAssignmentOut, TagCreate (+2 more)

### Community 54 - "Master Sites Parser Tests"
Cohesion: 0.19
Nodes (8): _master_blocks(), parse_sites_master(), (first, second) octet pairs a master row declares — lets sheet->site matching…, Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins., TestSitesMasterParser

### Community 55 - "Settings Tests"
Cohesion: 0.16
Nodes (6): fake_arq(), _pool(), _FakeArqJob, _FakePool, test_internal_keys_hidden(), test_settings_changes_audited()

### Community 56 - "Sheet Classification"
Cohesion: 0.24
Nodes (6): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, TestClassify

### Community 57 - "Dashboard UI"
Cohesion: 0.17
Nodes (9): DashboardPage(), metadata, ChartTheme, FALLBACK, readTheme(), useChartTheme(), PollingOptions, PollSignature (+1 more)

### Community 58 - "Backup File IO"
Cohesion: 0.21
Nodes (12): delete_scheduled_backup(), download_scheduled_backup(), backup_dir(), delete_backup_file(), list_backup_files(), prune_backups(), Fetch a scheduled backup by file name (path-traversal safe)., Delete a scheduled backup by file name (path-traversal safe). (+4 more)

### Community 59 - "Users API"
Cohesion: 0.41
Nodes (11): _admin_count(), create_user(), delete_user(), list_users(), _out(), update_user(), UserCreate, UserUpdate (+3 more)

### Community 60 - "Test Fixtures & Allocation"
Cohesion: 0.27
Nodes (10): _base_dsn(), client(), engine(), _prepare_test_db(), Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., session(), sf() (+2 more)

### Community 61 - "Scan Delta Tests"
Cohesion: 0.21
Nodes (8): on_hosts fires once per detection step with that chunk's new IPs — ARP batch…, When L2+L3 find nothing, the TCP fallback publishes its batch too., test_scan_cidr_emits_found_deltas(), fake_icmp(), fake_probe(), fake_ptr(), on_hosts(), test_scan_cidr_tcp_fallback_reports_found()

### Community 62 - "Loading & Separator UI"
Cohesion: 0.21
Nodes (7): Crumb, findChain(), PrefixBreadcrumbs(), Separator, Skeleton(), PrefixNode, @radix-ui/react-separator

### Community 63 - "Prefix API Tests"
Cohesion: 0.38
Nodes (9): _global_vrf_id(), test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_prefixes_order_by_utilization_and_limit(), test_same_cidr_allowed_across_vrfs(), test_split_cardinality_cap(), test_split_endpoint(), test_tree_endpoint() (+1 more)

### Community 65 - "Scanner Tests"
Cohesion: 0.22
Nodes (7): fake_arq(), _pool(), _FakeArqJob, _FakePool, Stands in for the arq Redis pool — never actually dispatches work., auth_on(), fixture

### Community 66 - "Auth & Search Tests"
Cohesion: 0.36
Nodes (6): _seed(), test_addresses_q_filter_not_broken(), test_search_grouped_results(), test_search_hebrew_folding(), test_search_ip_jump(), test_search_ip_jump_prefers_owner_then_deepest()

### Community 67 - "Root Layout & Prefs Init"
Cohesion: 0.28
Nodes (6): metadata, PrefsInit(), TooltipProvider, applyPrefs(), resolveTheme(), useApplyPrefs()

### Community 68 - "Entity CRUD Pages"
Cohesion: 0.25
Nodes (5): PrefixesPage(), PrefixRow, utilColor(), HistoryDialog(), Vlan

### Community 69 - "IPAM Service Core"
Cohesion: 0.25
Nodes (8): AllocateIPRequest, allocate_next_available(), create_prefix(), post, Atomically reserve the lowest free IP in the prefix., _resolve_prefix(), Prefix, PrefixCreate

### Community 70 - "Frontend Build Deps"
Cohesion: 0.25
Nodes (8): devDependencies, autoprefixer, postcss, tailwindcss, @types/node, @types/react, @types/react-dom, typescript

### Community 71 - "Positional Column Parsing"
Cohesion: 0.29
Nodes (4): _col_class(), _positional_columns(), Dominant content class of a column sample., Headerless sheet: locate the IP column, then assign the remaining canonical…

### Community 72 - "UI Primitives & Scripts"
Cohesion: 0.38
Nodes (4): Button, ButtonProps, buttonVariants, @radix-ui/react-slot

### Community 73 - "Tree Page Texts"
Cohesion: 0.53
Nodes (5): ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText()

### Community 75 - "Next.js Config"
Cohesion: 0.33
Nodes (3): nextConfig, metadata, next

### Community 76 - "App Shell & Frontend Auth"
Cohesion: 0.40
Nodes (3): Group, GROUPS, ShortcutsOverlay()

### Community 78 - "Security Policy Doc"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 79 - "Backup Restore"
Cohesion: 0.50
Nodes (4): _from_json(), Convert a JSON value back to what asyncpg expects for this column., Replace the non-admin user set from a users-inclusive envelope. Admin rows in…, _restore_users()

### Community 81 - "Scanner Pipeline"
Cohesion: 0.67
Nodes (3): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for()

### Community 82 - "Backend Core Deps"
Cohesion: 0.50
Nodes (4): fastapi 0.115.6, pydantic 2.10.3, pydantic-settings 2.6.1, uvicorn[standard] 0.32.1

### Community 85 - "Python Web Deps"
Cohesion: 0.50
Nodes (4): fastapi 0.115.6, pydantic 2.10.3, pydantic-settings 2.6.1, uvicorn[standard] 0.32.1

### Community 100 - "DB Driver Deps"
Cohesion: 0.67
Nodes (3): alembic 1.14.0, asyncpg 0.30.0, sqlalchemy[asyncio] 2.0.36

### Community 101 - "RBAC & User Tests"
Cohesion: 0.67
Nodes (3): Guard: every ORM table must be backed up (or explicitly excluded). Adding a new…, _registry_names(), test_registry_covers_all_tables()

### Community 123 - "Database Deps"
Cohesion: 0.67
Nodes (3): alembic 1.14.0, asyncpg 0.30.0, sqlalchemy[asyncio] 2.0.36

## Knowledge Gaps
- **269 isolated node(s):** `AssetRow`, `SplitPlan`, `ServiceRow`, `Draft`, `VlanRow` (+264 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 731 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **50 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ScanJob` connect `Worker & Scan Orchestration` to `Shared Types & Form UI`, `Frontend API Client`, `Settings Pages UI`, `Prefix Detail & Address UI`, `Scans API`?**
  _High betweenness centrality (0.321) - this node is a cross-community bridge._
- **Why does `create_scan()` connect `Scans API` to `VLAN API`, `Runtime Settings`, `Worker & Scan Orchestration`?**
  _High betweenness centrality (0.283) - this node is a cross-community bridge._
- **Why does `VRF` connect `VLAN API` to `Backup Service & Models`, `Import Planner`, `Sites API`, `Scans API`, `Import Executor`?**
  _High betweenness centrality (0.108) - this node is a cross-community bridge._
- **Are the 29 inferred relationships involving `User` (e.g. with `auth_status()` and `change_password()`) actually correct?**
  _`User` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `Base` (e.g. with `_serialize_row()` and `test_registry_covers_all_tables()`) actually correct?**
  _`Base` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `AssetRow`, `SplitPlan`, `ServiceRow` to the rest of the system?**
  _269 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Changelog UI & Utils` be split into smaller, more focused modules?**
  _Cohesion score 0.06140350877192982 - nodes in this community are weakly interconnected._