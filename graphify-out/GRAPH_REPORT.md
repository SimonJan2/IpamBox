# Graph Report - IpamBox  (2026-09-24)

## Corpus Check
- Large corpus: 2563 files · ~955,674 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder.

## Summary
- 3454 nodes · 11567 edges · 152 communities (93 shown, 29 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 796 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Frontend Pages
- Racks API
- Frontend Page Shells
- Config & Migration Env
- Prefix Detail UI
- Changelog Core & Models
- Discovery & Print UI
- Test Fixtures
- Prefixes API
- Rack Tests
- Import Wizard UI
- List Filtering API
- Docker Stack & Rack Library
- Frontend App Shell
- Addresses API
- Workbook Service
- Demo Data Generator
- Cables API
- VLANs API
- Devices API
- Dashboard & Discovery API
- Page Components
- User Docs
- Backup API
- Workbook Planner
- Changelog & Dashboard UI
- Custom Lists
- Maintenance API
- Entities & Schemas
- Auth API
- Color Rules API
- Cabling Tests
- Scans API
- Error Pages
- Imports API
- Rack Groups API
- Rack Detail & Rackula
- Tags API
- Backup Tests
- Device Filter Panel
- Settings Model
- Worker & Scanner Tests
- Sites API
- Search API
- Models & Maintenance Tests
- Frontend Dependencies
- Reconcile Worker
- Frontend Config
- Rack Group View
- Rack Editor UI
- OUI & Scanner
- Workbook Import Tests
- Tree Page
- Settings API
- Security Core
- Scanner Tests
- RBAC Tests
- Workbook Parsers
- Colors Tests
- List Parsing
- Ordering Tests
- TSConfig
- IPAM Extras Tests
- Settings Tests
- Docs Pages
- Users API
- Site Sheet Parsers
- Sites Master Parsers
- Interfaces Panel
- Changelog Tests
- Search Tests
- Devices Docs
- Workbook Execute
- Workbook Reader
- Allocation Tests
- Scanner Delta Tests
- Docs Content
- Changelog Hooks
- Colors Service
- Prefix API Tests
- Community 80
- Community 81
- Community 82
- Community 83
- Community 84
- Community 85
- Community 86
- Community 87
- Community 88
- Community 89
- Community 90
- Community 91
- Community 92
- Community 93
- Community 94
- Community 95
- Community 119
- Community 120
- Community 121
- Community 122
- Community 123
- Community 125
- Community 126
- Community 127
- Community 132
- Community 133
- Community 134
- Community 135
- Community 136
- Community 137
- Community 138
- Community 139
- Community 142
- Community 143
- Community 144
- Community 145
- Community 146
- Community 147
- Community 148
- Community 149
- Community 150
- Community 151

## God Nodes (most connected - your core abstractions)
1. `cn()` - 156 edges
2. `react` - 126 edges
3. `IPAMError` - 99 edges
4. `get_or_404()` - 80 edges
5. `IPAddress` - 76 edges
6. `useAsyncData()` - 73 edges
7. `lucide-react` - 70 edges
8. `User` - 69 edges
9. `useAuth()` - 63 edges
10. `Button` - 58 edges

## Surprising Connections (you probably didn't know these)
- `scanner service (arq worker, host networking)` --shares_data_with--> `ip column type (live IPAM resolution)`  [INFERRED]
  docker-compose.yml → frontend/src/content/docs/lists.md
- `Four roles (Administrator, Operator, Contributor, Viewer)` --semantically_similar_to--> `4-tier RBAC (Administrator/Operator/Contributor/Viewer)`  [EXTRACTED] [semantically similar]
  frontend/src/content/docs/accounts-and-roles.md → README.md
- `Inventory (asset register)` --semantically_similar_to--> `Certificate expiry tracking`  [INFERRED] [semantically similar]
  frontend/src/content/docs/inventory.md → frontend/src/content/docs/certificates.md
- `Rack Group (bayed row)` --references--> `IpamBox`  [EXTRACTED]
  frontend/src/content/docs/racks.md → README.md
- `HostResult` --calls--> `fake_scan()`  [EXTRACTED]
  backend/app/worker/scanner.py → backend/tests/test_scanner.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Demo rack population pipeline (zip + script + /devices/import + Demo DC)** — examples_readme_demo_rack_dc_py, examples_readme_devices_import_endpoint [INFERRED 0.75]
- **Deterministic demo regeneration (fixed seed/timestamps)** — examples_generate_demo_data, examples_readme_demo_rack_dc_py [INFERRED 0.75]

## Communities (152 total, 29 thin omitted)

### Community 0 - "Frontend Pages"
Cohesion: 0.10
Nodes (84): EMPTY, EMPTY, DEVICE_VIEWS, DeviceRow, EMPTY, TEXT_CHIP_LABELS, EMPTY_EDIT, FACE_BADGE (+76 more)

### Community 1 - "Racks API"
Cohesion: 0.05
Nodes (102): _check_refs(), create_device(), create_rack(), delete_device(), delete_rack(), _device_out(), _devices(), _get_device() (+94 more)

### Community 2 - "Frontend Page Shells"
Cohesion: 0.02
Nodes (42): nextConfig, metadata, metadata, metadata, metadata, metadata, metadata, metadata (+34 more)

### Community 3 - "Config & Migration Env"
Cohesion: 0.04
Nodes (88): ArqRedis, do_run_migrations(), run_migrations_online(), get_settings(), close_arq_pool(), close_redis(), get_arq_pool(), get_redis() (+80 more)

### Community 4 - "Prefix Detail UI"
Cohesion: 0.06
Nodes (61): IpCell(), SortableColRow(), IP_ROLES, IP_STATUSES, RANGE_ROLES, SplitDialog(), SplitPlan, toggleIn() (+53 more)

### Community 5 - "Changelog Core & Models"
Cohesion: 0.11
Nodes (37): Audit trail via session flush hooks. before_flush collects (object, action,…, metrics(), Prometheus-style text exposition of object + scan counters., AppSetting, Runtime-editable setting override. Absent row -> env var -> default., Asset, SW/HW catalog rows (תוכנות וחומרות) and serial-number inventory…, Base (+29 more)

### Community 6 - "Discovery & Print UI"
Cohesion: 0.10
Nodes (44): BulkResp, LabelClient(), metadata, FACE_BADGE, PrintClient(), DataPage(), download(), FeatureDef (+36 more)

### Community 7 - "Test Fixtures"
Cohesion: 0.07
Nodes (59): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., _split_dsn() (+51 more)

### Community 8 - "Prefixes API"
Cohesion: 0.07
Nodes (64): allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), _prefix_rows() (+56 more)

### Community 9 - "Rack Tests"
Cohesion: 0.09
Nodes (65): _carrier(), _dev(), _group(), _imports(), _mount(), _next_free(), AsyncClient, AsyncSession (+57 more)

### Community 10 - "Import Wizard UI"
Cohesion: 0.03
Nodes (64): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, PreviewResp, SheetResults(), Step (+56 more)

### Community 11 - "List Filtering API"
Cohesion: 0.07
Nodes (65): list_devices(), _wiring_class(), _crud_router(), create_item(), get_item(), list_items(), update_item(), parse_enum_set() (+57 more)

### Community 12 - "Docker Stack & Rack Library"
Cohesion: 0.05
Nodes (66): api service (FastAPI/uvicorn backend), db service (PostgreSQL 16), ipam bridge network (192.0.2.0/24), redis service (Redis 7, appendonly), scanner service (arq worker, host networking), web service (Next.js frontend), CC0 1.0 Universal, netbox-community/devicetype-library (+58 more)

### Community 13 - "Frontend App Shell"
Cohesion: 0.05
Nodes (57): AppearancePage(), AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS, NavGroup, NavItem (+49 more)

### Community 14 - "Addresses API"
Cohesion: 0.07
Nodes (52): _address_csv_row(), _addresses_stmt(), bulk_addresses(), BulkBody, _check_interface_link(), create_address(), delete_address(), export_addresses() (+44 more)

### Community 15 - "Workbook Service"
Cohesion: 0.06
Nodes (50): _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., assemble_ip(), clean(), _clean_octets(), map_status(), mask_to_prefixlen() (+42 more)

### Community 16 - "Demo Data Generator"
Cohesion: 0.07
Nodes (58): assets_rows(), _assign_site_sheets(), _assign_site_sheets_clean(), build_en_workbook(), build_mixed_workbook(), build_sites(), certificates_rows(), circuits_rows() (+50 more)

### Community 17 - "Cables API"
Cohesion: 0.10
Nodes (48): _cable_out(), _check_ends(), create_cable(), delete_cable(), _get_cable(), _get_interface(), interfaces_match_free_text(), list_cables() (+40 more)

### Community 18 - "VLANs API"
Cohesion: 0.08
Nodes (50): delete_item(), reorder_items(), _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups() (+42 more)

### Community 19 - "Devices API"
Cohesion: 0.08
Nodes (52): Asset, _asset_ref(), _check_iface_refs(), _check_refs(), create_device(), create_interface(), delete_device(), delete_interface() (+44 more)

### Community 20 - "Dashboard & Discovery API"
Cohesion: 0.06
Nodes (40): list_changelog(), AsyncSession, get, AsyncSession, get, stats(), confirm_discovered(), ConfirmBody (+32 more)

### Community 21 - "Page Components"
Cohesion: 0.13
Nodes (53): CertificatesPage(), ChangelogPage(), CircuitsPage(), DevicesPage(), DeviceDetailClient(), DiscoveryPage(), ImportPage(), InventoryPage() (+45 more)

### Community 22 - "User Docs"
Cohesion: 0.11
Nodes (53): Accounts & Roles, Insecure mode (IPAMBOX_ALLOW_INSECURE), Four roles (Administrator, Operator, Contributor, Viewer), Session-cookie authentication, Address roles (vip/vrrp/hsrp/glbp/carp/secondary), Address CSV import/export, IP Addresses, IP drawer (+45 more)

### Community 23 - "Backup API"
Cohesion: 0.07
Nodes (42): delete_scheduled_backup(), download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, delete, get, post (+34 more)

### Community 24 - "Workbook Planner"
Cohesion: 0.09
Nodes (16): _Planner, (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Folded sheet title vs site name/code — word-boundary matching so 'int' doesn't…, Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new…, Resolve a 10.{second}.x sheet — site_number is only meaningful inside the…, A declared octet block claims the sheet — unless its site is inactive, in which… (+8 more)

### Community 25 - "Changelog & Dashboard UI"
Cohesion: 0.07
Nodes (38): ACTION_STYLES, ACTION_STYLES, metadata, PrintClient(), fmtEta(), ScansPage(), ExpiryBadge(), ChangeDiff() (+30 more)

### Community 26 - "Custom Lists"
Cohesion: 0.07
Nodes (28): CustomList, User-defined table — preserves a workbook sheet's own shape (e.g. 'שרתים…, _get_or_create_list(), CustomList, key_for(), pick_key_column(), Custom-list extraction: turn any sheet into {columns, rows} for a list. Unlike…, Default merge column: first non-date/ip column filled in most rows (the… (+20 more)

### Community 27 - "Maintenance API"
Cohesion: 0.08
Nodes (46): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+38 more)

### Community 28 - "Entities & Schemas"
Cohesion: 0.08
Nodes (30): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, AssetKind, str, AssetCreate, AssetOut, AssetUpdate, BaseModel, field_validator (+22 more)

### Community 29 - "Auth API"
Cohesion: 0.12
Nodes (41): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+33 more)

### Community 30 - "Color Rules API"
Cohesion: 0.09
Nodes (34): create_rule(), delete_rule(), get_rule(), list_rules(), preview_rule(), AsyncSession, delete, get (+26 more)

### Community 31 - "Cabling Tests"
Cohesion: 0.17
Nodes (40): auth_on(), _backup_bytes(), _cable(), _device(), _gen(), _iface(), _ip(), _login() (+32 more)

### Community 32 - "Scans API"
Cohesion: 0.10
Nodes (34): cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession, get (+26 more)

### Community 34 - "Imports API"
Cohesion: 0.11
Nodes (34): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+26 more)

### Community 35 - "Rack Groups API"
Cohesion: 0.11
Nodes (31): _check_site(), create_rack_group(), delete_rack_group(), _get_group(), get_rack_group(), list_rack_groups(), _ordered_racks(), AsyncSession (+23 more)

### Community 36 - "Rack Detail & Rackula"
Cohesion: 0.10
Nodes (34): RackDetailPage(), RackulaImportDialog(), ABBREV_TO_CATEGORY, canonicalCategory(), CATEGORY_TO_ABBREV, clip(), compareVersions(), decodeShareUrl() (+26 more)

### Community 37 - "Tags API"
Cohesion: 0.13
Nodes (25): assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession, delete (+17 more)

### Community 38 - "Backup Tests"
Cohesion: 0.16
Nodes (33): _backup_bytes(), _envelope_bytes(), _mkusers(), User, Hand-craft a backup envelope (e.g. with a forged users table)., Guard: every ORM table must be backed up (or explicitly excluded). Adding a new…, Fresh-server scenario: the migration-seeded Global VRF is replaced by the…, Fresh-server scenario: the target's admins survive; its non-admin set is fully… (+25 more)

### Community 39 - "Device Filter Panel"
Cohesion: 0.09
Nodes (31): containsFold(), DEVICE_FILTER_PARAMS, DEVICE_TEXT_PARAMS, DeviceFilterPanel(), DeviceFilterState, DeviceTextParam, FACES, filterDevices() (+23 more)

### Community 40 - "Settings Model"
Cohesion: 0.09
Nodes (23): psycopg2-style URL for alembic offline mode / scripts., Settings, Effective, _env_sourced(), patch(), Any, AsyncSession, Exception (+15 more)

### Community 41 - "Worker & Scanner Tests"
Cohesion: 0.11
Nodes (28): _global_vrf_id(), _infer_scan_vrf(), Prefix, Pick the VRF for a scan that didn't specify one. An exact-match prefix living…, _resolve_prefix(), _scan_vrf(), WorkerSettings, _extra_vrf() (+20 more)

### Community 42 - "Sites API"
Cohesion: 0.13
Nodes (26): _cascade_site_fields(), create_site(), delete_site(), get_site(), list_sites(), AsyncSession, delete, get (+18 more)

### Community 43 - "Search API"
Cohesion: 0.17
Nodes (27): _folded(), AsyncSession, get, Cross-object search for the command palette. One GET returns grouped matches…, Column expression with Hebrew final letters folded — pairs with fold_hebrew()…, Short label for a list-row search hit: key-column value, else the first non-…, _row_label(), search() (+19 more)

### Community 44 - "Models & Maintenance Tests"
Cohesion: 0.10
Nodes (26): IPAddress, Base, Prefix, fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient (+18 more)

### Community 45 - "Frontend Dependencies"
Cohesion: 0.07
Nodes (29): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, js-yaml, jszip, lucide-react (+21 more)

### Community 46 - "Reconcile Worker"
Cohesion: 0.11
Nodes (26): _flag(), Any, AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), HostResult, A stored (e.g. imported) MAC that differs from the scan is flagged in…, Scanning a /24 under a documented /16 must not mark the other 255 subnets'… (+18 more)

### Community 47 - "Frontend Config"
Cohesion: 0.07
Nodes (26): name, private, version, autoprefixer, clsx, jszip, lz-string, postcss (+18 more)

### Community 48 - "Rack Group View"
Cohesion: 0.17
Nodes (23): DashboardPage(), DragSession, errDetail(), findDevice(), GroupClient(), moveDevice(), metadata, slotRect (+15 more)

### Community 49 - "Rack Editor UI"
Cohesion: 0.16
Nodes (24): DeviceFormDialog(), DragSession, DropRow(), EditorBlock(), errDetail(), Pending, RackEditor(), CarrierFrameSvg() (+16 more)

### Community 50 - "OUI & Scanner"
Cohesion: 0.12
Nodes (20): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), _host_chunks(), _icmp_sweep(), infer_device_type(), _ptr_lookup() (+12 more)

### Community 51 - "Workbook Import Tests"
Cohesion: 0.21
Nodes (13): _master_row(), _matrix(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind… (+5 more)

### Community 52 - "Tree Page"
Cohesion: 0.18
Nodes (20): metadata, ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), collectExpandableKeys(), flattenTree() (+12 more)

### Community 53 - "Settings API"
Cohesion: 0.12
Nodes (23): _build_out(), _lan_info(), _mask_url(), AsyncSession, get, Hide the password in a scheme://user:pass@host URL., LAN identity detected by the host-networked worker (written to Redis). Falls…, read_settings() (+15 more)

### Community 54 - "Security Core"
Cohesion: 0.13
Nodes (23): clear_login_failures(), client_ip(), destroy_session_by_suffix(), _fails_key(), _in_trusted(), _ip_fails_key(), _ip_lock_key(), is_locked_out() (+15 more)

### Community 55 - "Scanner Tests"
Cohesion: 0.12
Nodes (17): _FakeRedis, _mk_job(), In-memory stand-in for the worker's redis client (get/set/publish)., Point the worker at the test DB (sf) and the fake redis client., Cancel flag polled between phases -> ScanCancelled -> CANCELLED, and no…, Audit race: API writes CANCELLED mid-scan while the redis flag is lost…, Cancel landing while reconcile writes rows: the flag + row re-check right…, A job already terminal when the worker picks it up is skipped — no RUNNING… (+9 more)

### Community 56 - "RBAC Tests"
Cohesion: 0.34
Nodes (22): str, UserRole, login(), mkuser(), other_client(), AsyncClient, AsyncSession, allow_insecure keeps full access (existing behavior preserved). (+14 more)

### Community 57 - "Workbook Parsers"
Cohesion: 0.11
Nodes (16): parse_certificates(), parse_servers(), Positional 5-col layout: platform, target/VS, server, cert, expiry., 002 שרתים בייצור: Name, Guest OS, IP Address(multi), Cert, License, owner., Workbook import: normalizer/parser unit tests (no DB) + API e2e., קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., Small synthetic workbook: sites master + one site sheet + circuits. (+8 more)

### Community 58 - "Colors Tests"
Cohesion: 0.27
Nodes (19): _login(), _mk_rule(), _mk_site(), _mkuser(), AsyncClient, AsyncSession, Global row colors: manual row_color + rule-computed display_color. Covers the…, test_backup_roundtrips_color_rules() (+11 more)

### Community 59 - "List Parsing"
Cohesion: 0.19
Nodes (11): ListTarget, Import a sheet as a custom list (user-selected or suggested)., _cell_text(), extract_list_table(), SheetMatrix -> (column defs, row dicts). columns: [{key, label, type, options?,…, Raw cell -> stored string. Dates iso-format; everything else cleans., _matrix(), _preview_of() (+3 more)

### Community 60 - "Ordering Tests"
Cohesion: 0.28
Nodes (18): _circuit_order(), _login(), _mk_circuits(), _mkuser(), AsyncClient, AsyncSession, Global row ordering: POST /{entity}/reorder + pinned rows. Covered on both…, Reordering a subset keeps the slots those rows already had — rows outside the… (+10 more)

### Community 61 - "TSConfig"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 62 - "IPAM Extras Tests"
Cohesion: 0.22
Nodes (17): _prefix(), export.csv takes the same filters as the list endpoint — a filtered view…, Same filtered-export treatment on the prefixes CSV (F8)., A documented v6 /64's 2^64 host count must not reach dashboard sums (~1.8e19 >…, test_address_role_nat_and_bulk(), test_addresses_export_respects_filters(), test_bulk_reports_real_counts(), test_container_move_with_children_rejected() (+9 more)

### Community 63 - "Settings Tests"
Cohesion: 0.17
Nodes (15): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, Every new Settings > Features key is runtime-editable; untouched keys keep the…, test_backup_files_report_effective_schedule() (+7 more)

### Community 64 - "Docs Pages"
Cohesion: 0.19
Nodes (11): DocsIndexClient(), metadata, DocsNav(), BY_SLUG, DOC_ARTICLES, DOC_CATEGORIES, DocArticle, DocCategory (+3 more)

### Community 65 - "Users API"
Cohesion: 0.24
Nodes (16): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+8 more)

### Community 66 - "Site Sheet Parsers"
Cohesion: 0.17
Nodes (8): _blocks(), parse_site_sheet(), Split duplicated column groups (031-style runaway): each block starts at an…, MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf., Bare 'Name' (Cellular) maps to the hostname field., Non-empty unnamed columns pile into cf['extra'] instead of vanishing (Pelephone…, TestSiteSheetExtras, TestSiteSheetParser

### Community 67 - "Sites Master Parsers"
Cohesion: 0.17
Nodes (9): _master_blocks(), parse_sites_master(), (first, second) octet pairs a master row declares — lets sheet->site matching…, parse_sites_master_records(), Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins. (+1 more)

### Community 68 - "Interfaces Panel"
Cohesion: 0.16
Nodes (11): CABLE_KINDS, CableDialog(), fmtSpeed(), IFACE_KINDS, InterfacesPanel(), useDevicePick(), Cable, CableKind (+3 more)

### Community 69 - "Changelog Tests"
Cohesion: 0.23
Nodes (12): AsyncClient, tag_assignments.object_id has no FK — deleting a tagged object must drop its…, Tag.assignments is already ORM delete-orphan — each removed assignment lands in…, PATCH settings with a null value deletes the app_settings row — that delete…, /addresses/bulk action=delete used to issue one Core DELETE — invisible to the…, test_bulk_delete_writes_changelog_entries(), test_changelog_captures_ip_status_change(), test_changelog_records_crud() (+4 more)

### Community 70 - "Search Tests"
Cohesion: 0.31
Nodes (12): AsyncClient, Global /api/v1/search endpoint (UX-3)., Regression: list_addresses ?q= used to crash on a missing column., Site + VRF + prefix + address + one of each workbook entity., _seed(), test_addresses_q_filter_not_broken(), test_search_empty_query(), test_search_grouped_results() (+4 more)

### Community 71 - "Devices Docs"
Cohesion: 0.17
Nodes (13): PATCH /api/v1/addresses/{id} (device_id link/unlink), Device detail API (/api/v1/devices/{id}), Devices REST API (/api/v1/devices, /reorder), API sketch, Device detail, Devices, Devices vs racks, Devices documentation (+5 more)

### Community 72 - "Workbook Execute"
Cohesion: 0.21
Nodes (11): _apply_list(), commit_batch(), execute_plan(), rep(), _get_or_create_prefix(), _group_by_sheet(), PlanError, AsyncSession (+3 more)

### Community 73 - "Workbook Reader"
Cohesion: 0.26
Nodes (9): Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, _csv_sheet(), load_workbook_bytes(), XLSX/CSV -> sheet matrices (openpyxl read_only streams / csv module)., Drop fully-empty trailing rows/cols for a stable matrix shape., One CSV file -> one SheetMatrix named after the file stem. utf-8-sig first…, Parse workbook bytes into per-sheet row matrices. read_only + data_only:…, SheetMatrix (+1 more)

### Community 74 - "Allocation Tests"
Cohesion: 0.24
Nodes (11): sf(), _mk_prefix(), test_address_crud_and_dup_guard(), test_allocation_skips_existing(), test_concurrent_allocation_unique(), alloc(), test_exhausted_prefix_conflicts(), test_sequential_allocation_skips_boundaries() (+3 more)

### Community 75 - "Scanner Delta Tests"
Cohesion: 0.21
Nodes (8): on_hosts fires once per detection step with that chunk's new IPs — ARP batch…, When L2+L3 find nothing, the TCP fallback publishes its batch too., test_scan_cidr_emits_found_deltas(), fake_icmp(), fake_probe(), fake_ptr(), on_hosts(), test_scan_cidr_tcp_fallback_reports_found()

### Community 76 - "Docs Content"
Cohesion: 0.24
Nodes (9): DocPage(), dynamicParams, generateMetadata(), loadMarkdown(), DocsContent(), docCategoryLabel(), getDoc(), react-markdown (+1 more)

### Community 77 - "Changelog Hooks"
Cohesion: 0.27
Nodes (11): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), SyncSession, register(), _repr() (+3 more)

### Community 78 - "Colors Service"
Cohesion: 0.29
Nodes (11): _as_date(), _as_str(), display_color_for(), _ordered_cmp(), Any, date, -1/0/1 comparing a column value to a rule's value string. Tries date first when…, Does ``rule`` fire on this row? NULL fields never match. (+3 more)

### Community 79 - "Prefix API Tests"
Cohesion: 0.33
Nodes (10): _global_vrf_id(), Splits are counted arithmetically before materializing: anything over…, test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_prefixes_order_by_utilization_and_limit(), test_same_cidr_allowed_across_vrfs(), test_split_cardinality_cap(), test_split_endpoint() (+2 more)

### Community 80 - "Community 80"
Cohesion: 0.20
Nodes (8): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture, Stands in for the arq Redis pool — never actually dispatches work., scan_exclude_networks=10.70.0.64/26 inside scan_networks=10.70.0.0/24: the…, test_scheduler_and_route_share_exclusion_guard()

### Community 81 - "Community 81"
Cohesion: 0.27
Nodes (8): canMount(), canPlace(), conflicts(), facesCollide(), freeSlots(), rangesOverlap(), SLOT_LAYOUTS, slotCount()

### Community 82 - "Community 82"
Cohesion: 0.33
Nodes (9): ChangePasswordBody, LanInfo, BaseModel, Partial settings update. Explicit null resets the key to env/default., SessionOut, SettingsOut, SettingsPatch, SystemInfo (+1 more)

### Community 83 - "Community 83"
Cohesion: 0.22
Nodes (9): _infer_type(), _ips(), _is_ip_token(), (type, extra) for one column — extra carries options/multi., Row 0 of an unrecognized sheet looks like headers when every cell is a short…, _sniff_header_row(), excel_date(), date (+1 more)

### Community 85 - "Community 85"
Cohesion: 0.20
Nodes (10): devDependencies, autoprefixer, postcss, sharp, tailwindcss, @types/js-yaml, @types/node, @types/react (+2 more)

### Community 86 - "Community 86"
Cohesion: 0.29
Nodes (9): Placed, libraryBySlug(), LibraryDevice, libraryImage(), RACK_LIBRARY, ImportDevice, PreviewRow, RackFace (+1 more)

### Community 87 - "Community 87"
Cohesion: 0.36
Nodes (3): classify_sheet(), (family, header_row_index, warnings). header_row_index = index of the row…, TestClassify

### Community 88 - "Community 88"
Cohesion: 0.25
Nodes (6): DIR, FACES, LAYOUTS, problems, referenced, slugs

### Community 89 - "Community 89"
Cohesion: 0.29
Nodes (4): auth_on(), fake_arq(), fixture, Turn auth on for a test, restore insecure mode after, and flush session/lockout…

### Community 90 - "Community 90"
Cohesion: 0.29
Nodes (7): scripts, build, build:rack-library, check:rack-library, dev, lint, start

### Community 92 - "Community 92"
Cohesion: 0.53
Nodes (5): moveRowNav(), G_CHORDS, isEditableTarget(), modalOpen(), useGlobalShortcuts()

### Community 93 - "Community 93"
Cohesion: 0.40
Nodes (5): healthz(), get, Readiness probe: verifies DB + Redis connectivity., readyz(), JSONResponse

### Community 94 - "Community 94"
Cohesion: 0.50
Nodes (4): ChartTheme, FALLBACK, readTheme(), useChartTheme()

### Community 95 - "Community 95"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

## Ambiguous Edges - Review These
- `Cable` → `Rack`  [AMBIGUOUS]
  frontend/src/content/docs/cabling.md · relation: conceptually_related_to

## Knowledge Gaps
- **344 isolated node(s):** `SplitPlan`, `Row`, `SortKey`, `NavGroup`, `NavItem` (+339 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1114 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Cable` and `Rack`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `IPAddress` connect `Models & Maintenance Tests` to `Scans API`, `Racks API`, `Config & Migration Env`, `Changelog Core & Models`, `Test Fixtures`, `Prefixes API`, `Workbook Execute`, `Rack Tests`, `List Filtering API`, `Search API`, `Worker & Scanner Tests`, `Addresses API`, `Reconcile Worker`, `Cables API`, `Devices API`, `Dashboard & Discovery API`, `Custom Lists`, `Maintenance API`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Why does `react` connect `Frontend Page Shells` to `Frontend Pages`, `Docs Pages`, `Error Pages`, `Prefix Detail UI`, `Discovery & Print UI`, `Import Wizard UI`, `Frontend App Shell`, `Frontend Config`, `Rack Group View`, `Rack Editor UI`, `Tree Page`, `Page Components`, `Changelog & Dashboard UI`, `Community 92`, `Community 94`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Why does `User` connect `Auth API` to `Users API`, `Imports API`, `Changelog Core & Models`, `Backup Tests`, `Test Fixtures`, `Rack Tests`, `List Filtering API`, `Addresses API`, `Dashboard & Discovery API`, `Backup API`, `RBAC Tests`, `Colors Tests`, `Maintenance API`, `Ordering Tests`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Are the 73 inferred relationships involving `IPAMError` (e.g. with `_check_interface_link()` and `create_address()`) actually correct?**
  _`IPAMError` has 73 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `IPAddress` (e.g. with `_address_csv_row()` and `_addresses_stmt()`) actually correct?**
  _`IPAddress` has 33 INFERRED edges - model-reasoned connections that need verification._
- **What connects `SplitPlan`, `Row`, `SortKey` to the rest of the system?**
  _344 weakly-connected nodes found - possible documentation gaps or missing edges._