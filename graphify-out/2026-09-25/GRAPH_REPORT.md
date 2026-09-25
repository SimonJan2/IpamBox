# Graph Report - IpamBox  (2026-09-25)

## Corpus Check
- Large corpus: 2569 files · ~979,568 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder.

## Summary
- 3891 nodes · 12685 edges · 187 communities (119 shown, 38 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 768 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [Id] Page
- Dialog UI
- Rack I/O Tests
- Prefix Detail Client Page
- Color Rules Client Page
- Schemas
- Scans API
- Prefixes API
- Data Models
- Cabling Tests
- Racks Tests
- Auth API
- Import Client Page
- User Docs
- Schemas (14)
- Prefixes Client Page
- App Shell UI
- Plan Service
- Schemas (18)
- Lists API
- Maintenance API
- Lists Tests
- Racks API
- Devices API
- Normalize Service
- Color Rules API
- Devices Tests
- Maintenance Tests
- Scanner Tests
- Error Page
- Schemas (30)
- Schemas (31)
- Rackula Import UI
- Racks Service
- Device Filter Panel UI
- Imports API
- Backup Tests
- Tags API
- Scanner Tests (38)
- Schemas (39)
- Racks API (40)
- Rack I/O Service
- Vlans API
- React
- Runtime Settings Service
- Device I/O Service
- Rack Row UI
- Smart Import Dialog UI
- Scanner Tests (48)
- React (49)
- Backup API
- Schemas (51)
- Oui Service
- Workbook Import Tests
- Prefix Tree UI
- Redis Tests
- Rack Groups API
- Workbook Import Tests (57)
- Build
- Schemas (59)
- Scans API (60)
- Schemas (61)
- Sites API
- Rbac Tests
- Rack Editor UI
- Device I/O Service (65)
- Listparse Service
- Colors Tests
- DB Migrations
- Racks API (69)
- Ordering Tests
- Rack Elevation UI
- Tsconfig
- Workbook Import Tests (73)
- Ipam Extras Tests
- Settings Tests
- User Docs (76)
- Docs Page
- User Docs (78)
- User Docs (79)
- User Docs (80)
- Data Models (81)
- Schemas (82)
- Yaml
- Settings API
- Users API
- Backup Service
- User Docs (87)
- Device I/O Service (88)
- Auth Tests
- Search Tests
- User Docs (91)
- Interfaces Panel UI
- Device I/O Service (93)
- Reader Service
- Workbook Import Tests (95)
- Racks API (96)
- Workbook Import Tests (97)
- Changelog Tests
- Scanner Tests (99)
- [Slug] Page
- Changes
- Colors Service
- Prefix Api Tests
- Scanner Tests (104)
- User Docs (105)
- Workbook Import Tests (106)
- Types
- User Docs (108)
- Rack I/O Service (109)
- History Panel UI
- Check
- Rbac Tests (112)
- Build (113)
- User Docs (114)
- Entities Tests
- Racks API (116)
- Scan Policy Service
- Workbook Import Tests (118)
- Chart
- User Docs (120)
- Device I/O Service (144)
- Rack I/O Service (145)
- Redis
- Asyncpg
- Pydantic
- Pytest
- Next
- User Docs (152)
- User Docs (153)
- Shim
- User Docs (155)
- User Docs (156)
- Misc
- Deviceinterface
- Misc (160)
- Linkedref
- Patch
- Post
- Reorderbody
- Alembic
- Bcrypt
- Fastapi
- Httpx
- Openpyxl
- Psutil
- Scapy
- Uvicorn
- Icon Page
- App Page
- User Docs (180)
- User Docs (181)
- User Docs (182)
- User Docs (183)
- User Docs (184)
- User Docs (185)
- User Docs (186)

## God Nodes (most connected - your core abstractions)
1. `cn()` - 156 edges
2. `react` - 127 edges
3. `IPAMError` - 92 edges
4. `get_or_404()` - 75 edges
5. `IPAddress` - 74 edges
6. `useAsyncData()` - 72 edges
7. `lucide-react` - 71 edges
8. `User` - 69 edges
9. `useAuth()` - 62 edges
10. `Button` - 59 edges

## Surprising Connections (you probably didn't know these)
- `CSV export` --semantically_similar_to--> `Address CSV import/export (UTF-8 BOM)`  [INFERRED] [semantically similar]
  frontend/src/content/docs/devices.md → README.md
- `Export dropdown (Devices toolbar)` --semantically_similar_to--> `Device smart file I/O (export dropdown + smart import)`  [INFERRED] [semantically similar]
  frontend/src/content/docs/devices.md → README.md
- `Smart import dialog` --semantically_similar_to--> `Excel workbook import (per-sheet detection, dry-run, all-or-nothing/partial commit)`  [INFERRED] [semantically similar]
  frontend/src/content/docs/devices.md → README.md
- `Smart import dialog` --semantically_similar_to--> `Device smart file I/O (export dropdown + smart import)`  [INFERRED] [semantically similar]
  frontend/src/content/docs/devices.md → README.md
- `Certificate expiry tracking` --semantically_similar_to--> `Inventory (asset register)`  [INFERRED] [semantically similar]
  frontend/src/content/docs/certificates.md → frontend/src/content/docs/inventory.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Rack bundle export -> dry-run preview -> import round-trip** — frontend_src_content_docs_racks_export_xlsx, frontend_src_content_docs_racks_rack_export_xlsx, frontend_src_content_docs_racks_group_export_xlsx, frontend_src_content_docs_racks_import_endpoint [EXTRACTED 1.00]
- **V5C racks & groups smart export/import feature** — frontend_src_content_docs_racks_export_xlsx, frontend_src_content_docs_racks_import_endpoint, frontend_src_content_docs_devices_import_endpoint [EXTRACTED 1.00]

## Communities (187 total, 38 thin omitted)

### Community 0 - "[Id] Page"
Cohesion: 0.02
Nodes (48): nextConfig, metadata, metadata, metadata, DashboardPage(), DevicesPage(), metadata, metadata (+40 more)

### Community 1 - "Dialog UI"
Cohesion: 0.08
Nodes (78): EMPTY, EMPTY, DEVICE_VIEWS, DeviceRow, EMPTY, IMPORT_FIELDS, IMPORT_OPTIONS, TEXT_CHIP_LABELS (+70 more)

### Community 2 - "Rack I/O Tests"
Cohesion: 0.06
Nodes (109): AsyncClient, auth_on(), _csv(), _device(), _group(), _import(), _ip(), _login() (+101 more)

### Community 3 - "Prefix Detail Client Page"
Cohesion: 0.04
Nodes (88): ImportListDialog(), IpCell(), SortableColRow(), IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, SplitDialog() (+80 more)

### Community 4 - "Color Rules Client Page"
Cohesion: 0.10
Nodes (62): ACTION_STYLES, ACTION_STYLES, EMPTY_EDIT, FACE_BADGE, BulkResp, FACE_BADGE, FACE_BADGE, Draft (+54 more)

### Community 5 - "Schemas"
Cohesion: 0.05
Nodes (72): _address_csv_row(), _addresses_stmt(), bulk_addresses(), BulkBody, _check_interface_link(), create_address(), delete_address(), export_addresses() (+64 more)

### Community 6 - "Scans API"
Cohesion: 0.05
Nodes (74): _alias_to_field(), apply_device_import(), auto_map_fields(), auto_map_headers(), remap(), _carrier_diff_name(), device_export_rows(), _err() (+66 more)

### Community 7 - "Prefixes API"
Cohesion: 0.07
Nodes (71): allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), _prefix_rows() (+63 more)

### Community 8 - "Data Models"
Cohesion: 0.08
Nodes (49): Audit trail via session flush hooks. before_flush collects (object, action,…, healthz(), metrics(), get, Readiness probe: verifies DB + Redis connectivity., Prometheus-style text exposition of object + scan counters., readyz(), AppSetting (+41 more)

### Community 9 - "Cabling Tests"
Cohesion: 0.07
Nodes (69): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., session() (+61 more)

### Community 10 - "Racks Tests"
Cohesion: 0.09
Nodes (66): hash_password(), _carrier(), _dev(), _group(), _imports(), _mount(), _next_free(), AsyncClient (+58 more)

### Community 11 - "Auth API"
Cohesion: 0.08
Nodes (63): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+55 more)

### Community 12 - "Import Client Page"
Cohesion: 0.04
Nodes (60): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, PreviewResp, SheetResults(), Step (+52 more)

### Community 13 - "User Docs"
Cohesion: 0.07
Nodes (58): assets_rows(), _assign_site_sheets(), _assign_site_sheets_clean(), build_en_workbook(), build_mixed_workbook(), build_sites(), certificates_rows(), circuits_rows() (+50 more)

### Community 14 - "Schemas (14)"
Cohesion: 0.10
Nodes (48): _cable_out(), _check_ends(), create_cable(), delete_cable(), _get_cable(), _get_interface(), interfaces_match_free_text(), list_cables() (+40 more)

### Community 15 - "Prefixes Client Page"
Cohesion: 0.11
Nodes (53): CertificatesPage(), ChangelogPage(), CircuitsPage(), DeviceDetailClient(), DiscoveryPage(), ImportPage(), InventoryPage(), ListsClient() (+45 more)

### Community 16 - "App Shell UI"
Cohesion: 0.06
Nodes (47): metadata, viewport, AppearancePage(), AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS (+39 more)

### Community 17 - "Plan Service"
Cohesion: 0.08
Nodes (18): parse_sites_master_records(), _Planner, _preview(), (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Folded sheet title vs site name/code — word-boundary matching so 'int' doesn't…, Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new… (+10 more)

### Community 18 - "Schemas (18)"
Cohesion: 0.07
Nodes (36): list_changelog(), AsyncSession, get, AsyncSession, get, stats(), confirm_discovered(), ConfirmBody (+28 more)

### Community 19 - "Lists API"
Cohesion: 0.09
Nodes (47): bulk_rows(), _check_columns(), create_list(), create_row(), delete_list(), delete_row(), get_list(), list_lists() (+39 more)

### Community 20 - "Maintenance API"
Cohesion: 0.07
Nodes (47): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+39 more)

### Community 21 - "Lists Tests"
Cohesion: 0.07
Nodes (27): CustomList, User-defined table — preserves a workbook sheet's own shape (e.g. 'שרתים…, Site, key_for(), pick_key_column(), Custom-list extraction: turn any sheet into {columns, rows} for a list. Unlike…, Default merge column: first non-date/ip column filled in most rows (the…, Normalized merge key — same Hebrew folding the site matcher uses. (+19 more)

### Community 22 - "Racks API"
Cohesion: 0.10
Nodes (47): _check_refs(), create_device(), create_rack(), delete_rack(), _device_out(), _devices(), _export_name(), export_rack_xlsx() (+39 more)

### Community 23 - "Devices API"
Cohesion: 0.09
Nodes (47): Asset, _asset_ref(), _check_iface_refs(), _check_refs(), create_device(), create_interface(), delete_interface(), _detail() (+39 more)

### Community 24 - "Normalize Service"
Cohesion: 0.08
Nodes (41): assemble_ip(), clean(), _clean_octets(), map_status(), mask_to_prefixlen(), network_of(), norm_header(), norm_mac() (+33 more)

### Community 25 - "Color Rules API"
Cohesion: 0.09
Nodes (36): create_rule(), delete_rule(), get_rule(), list_rules(), preview_rule(), AsyncSession, delete, get (+28 more)

### Community 26 - "Devices Tests"
Cohesion: 0.15
Nodes (37): _cable(), _device(), _group(), _iface(), _ip(), _login(), _mkuser(), _prefix() (+29 more)

### Community 27 - "Maintenance Tests"
Cohesion: 0.09
Nodes (34): _job_payload(), str, ScanJob, ScanStatus, _due(), _eta_seconds(), datetime, Auto-purge rows past their configured retention (0 = keep forever). Mirrors the… (+26 more)

### Community 28 - "Scanner Tests"
Cohesion: 0.08
Nodes (31): Exception, Raised inside the pipeline when the user cancels the scan., ScanCancelled, cancel_key(), _job_status(), _publish(), Re-read the job row's status — the session's `job` instance goes stale the…, ARQ job: execute a scan and reconcile results. (+23 more)

### Community 30 - "Schemas (30)"
Cohesion: 0.12
Nodes (29): Rack elevations: racks + nested devices + Rackula import. Not a `_crud_router`…, str, RackFace, DeviceIpRef, One of the device's IPs: link id/label + scan status for the table., IpRef, LinkedRef, NextFreeUOut (+21 more)

### Community 31 - "Schemas (31)"
Cohesion: 0.08
Nodes (22): AssetKind, str, AssetCreate, AssetOut, AssetUpdate, BaseModel, field_validator, CircuitCreate (+14 more)

### Community 32 - "Rackula Import UI"
Cohesion: 0.09
Nodes (35): RackulaImportDialog(), slotLabel(), ABBREV_TO_CATEGORY, canonicalCategory(), CATEGORY_TO_ABBREV, clip(), compareVersions(), decodeShareUrl() (+27 more)

### Community 33 - "Racks Service"
Cohesion: 0.12
Nodes (33): Device, Base, ConflictError, apply_device_patch(), carrier_children(), CarrierError, _check_carrier_mount(), check_layout_change() (+25 more)

### Community 34 - "Device Filter Panel UI"
Cohesion: 0.09
Nodes (32): containsFold(), DEVICE_FILTER_PARAMS, DEVICE_TEXT_PARAMS, DeviceFilterPanel(), DeviceFilterState, DeviceTextParam, FACES, filterDevices() (+24 more)

### Community 35 - "Imports API"
Cohesion: 0.12
Nodes (32): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+24 more)

### Community 36 - "Backup Tests"
Cohesion: 0.16
Nodes (33): _backup_bytes(), _envelope_bytes(), _mkusers(), User, Hand-craft a backup envelope (e.g. with a forged users table)., Guard: every ORM table must be backed up (or explicitly excluded). Adding a new…, Fresh-server scenario: the migration-seeded Global VRF is replaced by the…, Fresh-server scenario: the target's admins survive; its non-admin set is fully… (+25 more)

### Community 37 - "Tags API"
Cohesion: 0.14
Nodes (31): _crud_router(), create_item(), delete_item(), get_item(), list_items(), reorder_items(), update_item(), assign_tag() (+23 more)

### Community 38 - "Scanner Tests (38)"
Cohesion: 0.10
Nodes (30): _flag(), Any, AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), HostResult, _mk_prefix(), A stored (e.g. imported) MAC that differs from the scan is flagged in… (+22 more)

### Community 39 - "Schemas (39)"
Cohesion: 0.17
Nodes (27): _folded(), AsyncSession, get, Cross-object search for the command palette. One GET returns grouped matches…, Column expression with Hebrew final letters folded — pairs with fold_hebrew()…, Short label for a list-row search hit: key-column value, else the first non-…, _row_label(), search() (+19 more)

### Community 40 - "Racks API (40)"
Cohesion: 0.14
Nodes (30): Rack, _rack_detail(), Rack -> RackDetail with its (selectin-loaded) devices serialized, each carrying…, _check_refs(), create_device(), delete_device(), delete_rack(), _device_out() (+22 more)

### Community 41 - "Rack I/O Service"
Cohesion: 0.14
Nodes (25): _name_map(), _parse_id(), #5' or '5' -> 5; None when the cell isn't an id reference., apply_bundle(), bundle_sheets(), BundleSheet, _group_export_rows(), _GroupPlan (+17 more)

### Community 42 - "Vlans API"
Cohesion: 0.17
Nodes (27): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+19 more)

### Community 43 - "React"
Cohesion: 0.07
Nodes (29): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, js-yaml, jszip, lucide-react (+21 more)

### Community 44 - "Runtime Settings Service"
Cohesion: 0.10
Nodes (19): psycopg2-style URL for alembic offline mode / scripts., Settings, Effective, _env_sourced(), get_effective(), Any, AsyncSession, Runtime-editable settings: app_settings rows override env defaults. Each public… (+11 more)

### Community 45 - "Device I/O Service"
Cohesion: 0.15
Nodes (27): _carrier_diff_name(), _err(), _int_field(), _ip_tokens(), _match(), _plan_child(), _plan_rack_level(), IPAddress (+19 more)

### Community 46 - "Rack Row UI"
Cohesion: 0.17
Nodes (23): DragSession, errDetail(), findDevice(), GroupClient(), moveDevice(), metadata, RackDetailPage(), slotRect (+15 more)

### Community 47 - "Smart Import Dialog UI"
Cohesion: 0.09
Nodes (23): fmtEta(), ScansPage(), QuickScanDialog(), useScanStream(), ACTION_STYLE, ColumnMap, DetectResp, FieldOption (+15 more)

### Community 48 - "Scanner Tests (48)"
Cohesion: 0.13
Nodes (22): _global_vrf_id(), _infer_scan_vrf(), Prefix, Pick the VRF for a scan that didn't specify one. An exact-match prefix living…, _resolve_prefix(), _scan_vrf(), WorkerSettings, _extra_vrf() (+14 more)

### Community 49 - "React (49)"
Cohesion: 0.07
Nodes (25): name, private, version, autoprefixer, clsx, postcss, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+17 more)

### Community 50 - "Backup API"
Cohesion: 0.13
Nodes (24): delete_scheduled_backup(), download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, delete, get, post (+16 more)

### Community 51 - "Schemas (51)"
Cohesion: 0.14
Nodes (20): create_vrf(), delete_vrf(), get_vrf(), list_vrfs(), AsyncSession, delete, get, post (+12 more)

### Community 52 - "Oui Service"
Cohesion: 0.12
Nodes (20): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), _host_chunks(), _icmp_sweep(), infer_device_type(), _ptr_lookup() (+12 more)

### Community 53 - "Workbook Import Tests"
Cohesion: 0.21
Nodes (13): _master_row(), _matrix(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind… (+5 more)

### Community 54 - "Prefix Tree UI"
Cohesion: 0.18
Nodes (21): ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), collectExpandableKeys(), flattenTree(), prefixKey() (+13 more)

### Community 55 - "Redis Tests"
Cohesion: 0.13
Nodes (20): ArqRedis, close_arq_pool(), close_redis(), get_arq_pool(), Shut down the shared client — lifespan/worker shutdown only., Shared ARQ pool — callers must not close() it per job., redis_settings_from_url(), lifespan() (+12 more)

### Community 56 - "Rack Groups API"
Cohesion: 0.16
Nodes (23): _check_site(), create_rack_group(), delete_rack_group(), export_rack_group_xlsx(), _get_group(), get_rack_group(), list_rack_groups(), _ordered_racks() (+15 more)

### Community 57 - "Workbook Import Tests (57)"
Cohesion: 0.11
Nodes (12): _blocks(), _col_class(), parse_site_sheet(), _positional_columns(), Split duplicated column groups (031-style runaway): each block starts at an…, Dominant content class of a column sample., Headerless sheet: locate the IP column, then assign the remaining canonical…, MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf. (+4 more)

### Community 58 - "Build"
Cohesion: 0.13
Nodes (23): arrLen(), attribution(), CATEGORY_COLOUR, CURATED, fetchBuf(), fetchJson(), FRONTEND, FULL_IMPORT (+15 more)

### Community 59 - "Schemas (59)"
Cohesion: 0.15
Nodes (17): _check_range_overlap(), create_range(), delete_range(), list_ranges(), AsyncSession, delete, get, post (+9 more)

### Community 60 - "Scans API (60)"
Cohesion: 0.16
Nodes (19): cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), list_scans(), AsyncSession, get, post (+11 more)

### Community 61 - "Schemas (61)"
Cohesion: 0.16
Nodes (20): _build_out(), _mask_url(), AsyncSession, get, Hide the password in a scheme://user:pass@host URL., read_settings(), update_settings(), ChangePasswordBody (+12 more)

### Community 62 - "Sites API"
Cohesion: 0.16
Nodes (20): _cascade_site_fields(), create_site(), delete_site(), get_site(), list_sites(), AsyncSession, delete, get (+12 more)

### Community 63 - "Rbac Tests"
Cohesion: 0.34
Nodes (22): str, UserRole, login(), mkuser(), other_client(), AsyncClient, AsyncSession, allow_insecure keeps full access (existing behavior preserved). (+14 more)

### Community 64 - "Rack Editor UI"
Cohesion: 0.17
Nodes (18): DragSession, DropRow(), EditorBlock(), errDetail(), Pending, RackEditor(), CarrierFrameSvg(), DeviceBlockSvg() (+10 more)

### Community 65 - "Device I/O Service (65)"
Cohesion: 0.17
Nodes (14): _find_carrier(), _Occupancy, _placement_candidate(), Planned, Device, Apply an update's placement to the simulated occupancy: merge onto the device,…, carrier cell -> the carrier row. '#id' resolves a stored device; names resolve…, One file row's verdict + everything needed to apply it. (+6 more)

### Community 66 - "Listparse Service"
Cohesion: 0.14
Nodes (15): _cell_text(), extract_list_table(), _infer_type(), _ips(), _is_ip_token(), SheetMatrix -> (column defs, row dicts). columns: [{key, label, type, options?,…, Raw cell -> stored string. Dates iso-format; everything else cleans., (type, extra) for one column — extra carries options/multi. (+7 more)

### Community 67 - "Colors Tests"
Cohesion: 0.27
Nodes (19): _login(), _mk_rule(), _mk_site(), _mkuser(), AsyncClient, AsyncSession, Global row colors: manual row_color + rule-computed display_color. Covers the…, test_backup_roundtrips_color_rules() (+11 more)

### Community 68 - "DB Migrations"
Cohesion: 0.12
Nodes (16): do_run_migrations(), run_migrations_online(), get_settings(), auth_on(), fixture, Same pattern as test_ordering: flip auth on, restore + flush keys., auth_on(), fixture (+8 more)

### Community 69 - "Racks API (69)"
Cohesion: 0.16
Nodes (17): parse_enum_set(), parse_int_set(), parse_token_set(), _export_name(), export_rack_xlsx(), _export_racks(), export_racks_csv(), export_racks_xlsx() (+9 more)

### Community 70 - "Ordering Tests"
Cohesion: 0.28
Nodes (18): _circuit_order(), _login(), _mk_circuits(), _mkuser(), AsyncClient, AsyncSession, Global row ordering: POST /{entity}/reorder + pinned rows. Covered on both…, Reordering a subset keeps the slots those rows already had — rows outside the… (+10 more)

### Community 71 - "Rack Elevation UI"
Cohesion: 0.19
Nodes (17): deviceImage(), FACE_BADGE, HEALTH_KEY, RackElevation(), RackGeom, RackUGrid(), useLibraryBySlug(), Placed (+9 more)

### Community 72 - "Tsconfig"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 73 - "Workbook Import Tests (73)"
Cohesion: 0.14
Nodes (12): parse_assets(), parse_certificates(), Positional 5-col layout: platform, target/VS, server, cert, expiry., 003 תוכנות וחומרות: סוג,חברה,דגם,שם התוכנה,ייעוד,גירסה,EOL,…, Workbook import: normalizer/parser unit tests (no DB) + API e2e., Small synthetic workbook: sites master + one site sheet + circuits., test_commit_twice_rejected(), test_import_e2e() (+4 more)

### Community 74 - "Ipam Extras Tests"
Cohesion: 0.22
Nodes (17): _prefix(), export.csv takes the same filters as the list endpoint — a filtered view…, Same filtered-export treatment on the prefixes CSV (F8)., A documented v6 /64's 2^64 host count must not reach dashboard sums (~1.8e19 >…, test_address_role_nat_and_bulk(), test_addresses_export_respects_filters(), test_bulk_reports_real_counts(), test_container_move_with_children_rejected() (+9 more)

### Community 75 - "Settings Tests"
Cohesion: 0.17
Nodes (15): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, Every new Settings > Features key is runtime-editable; untouched keys keep the…, test_backup_files_report_effective_schedule() (+7 more)

### Community 76 - "User Docs (76)"
Cohesion: 0.16
Nodes (17): CC0 1.0 Universal, netbox-community/devicetype-library, Rack device image library, Carrier (slot-layout device: shelves/trays), Device image library, Elevation editor, Find free U, Health overlay (+9 more)

### Community 77 - "Docs Page"
Cohesion: 0.19
Nodes (11): DocsIndexClient(), metadata, DocsNav(), BY_SLUG, DOC_ARTICLES, DOC_CATEGORIES, DocArticle, DocCategory (+3 more)

### Community 78 - "User Docs (78)"
Cohesion: 0.22
Nodes (18): IPAddress, Cable, connected_interface_id (structured far-end port link), connected_ip (host-side NIC binding), DeviceInterface (device-owned port), L1 trace (cable path walk), match-free-text transition endpoint, One-cable-per-interface rule (+10 more)

### Community 79 - "User Docs (79)"
Cohesion: 0.37
Nodes (18): Circuits (WAN circuit register), Hierarchy Tree, Roll-up utilization, Site → VRF → Prefix → IP address data model, IpamBox, Row Colors, Command palette, Services (service catalog) (+10 more)

### Community 80 - "User Docs (80)"
Cohesion: 0.14
Nodes (18): POST /api/v1/devices/import, Carrier two-pass mounting, Changelog / audit history, Dry-run preview with per-row {field:[old,new]} diffs, force commit mode (valid rows only), Header auto-mapping (English/Hebrew/NetBox), IP address, IP linking: existing addresses only, never creates (+10 more)

### Community 81 - "Data Models (81)"
Cohesion: 0.17
Nodes (15): create_rack(), _next_group_position(), patch, post, ReorderBody, Append slot at the row's right end for a rack joining without an explicit…, reorder_racks(), update_rack() (+7 more)

### Community 82 - "Schemas (82)"
Cohesion: 0.21
Nodes (12): CommitOptions, ListTarget, PreviewOptions, BaseModel, Per-sheet detection result shown in the wizard., Import a sheet as a custom list (user-selected or suggested)., User-confirmed mapping choices applied before building the plan., RowResult (+4 more)

### Community 83 - "Yaml"
Cohesion: 0.21
Nodes (10): Api, apply(), _device_payload(), emit_zip(), find_one(), _KeepMethodRedirect, layout_doc(), main() (+2 more)

### Community 84 - "Settings API"
Cohesion: 0.16
Nodes (16): _lan_info(), LAN identity detected by the host-networked worker (written to Redis). Falls…, AsyncSession, Request, Guard for every API route. Returns the User, or None in allow_insecure mode., require_auth(), set_actor(), detect_interface() (+8 more)

### Community 85 - "Users API"
Cohesion: 0.22
Nodes (16): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+8 more)

### Community 86 - "Backup Service"
Cohesion: 0.22
Nodes (16): _alembic_revisions(), backup_dir(), delete_backup_file(), list_backup_files(), prune_backups(), Path, Known migration revisions, head first (linear chain)., Fetch a scheduled backup by file name (path-traversal safe). (+8 more)

### Community 87 - "User Docs (87)"
Cohesion: 0.24
Nodes (16): Address roles (vip/vrrp/hsrp/glbp/carp/secondary), Address CSV import/export, IP Addresses, IP drawer, mac_mismatch flag, Changelog, Per-object history, Discovery Inbox (+8 more)

### Community 88 - "Device I/O Service (88)"
Cohesion: 0.25
Nodes (14): import_racks(), _alias_to_field(), apply_mapping_overrides(), auto_map_fields(), auto_map_headers(), remap(), header -> canonical field (None = skip). Unmapped columns are reported, never…, User {source_header: field} overrides on top of the auto-map. field "" / null… (+6 more)

### Community 89 - "Auth Tests"
Cohesion: 0.21
Nodes (14): auth_on(), AsyncClient, fixture, Turn auth on for a test, restore insecure mode after, and flush session/lockout…, When the socket peer isn't in ipambox_trusted_proxies, a supplied XFF is…, Spreading failures across many usernames from one IP trips the aggregate lock —…, Five bad logins for one (user, ip) pair must not lock out other users on the…, test_endpoints_require_auth() (+6 more)

### Community 90 - "Search Tests"
Cohesion: 0.25
Nodes (14): auth_on(), AsyncClient, fixture, Global /api/v1/search endpoint (UX-3)., Regression: list_addresses ?q= used to crash on a missing column., Site + VRF + prefix + address + one of each workbook entity., _seed(), test_addresses_q_filter_not_broken() (+6 more)

### Community 91 - "User Docs (91)"
Cohesion: 0.19
Nodes (15): api service (FastAPI/uvicorn backend), db service (PostgreSQL 16), ipam bridge network (192.0.2.0/24), redis service (Redis 7, appendonly), scanner service (arq worker, host networking), web service (Next.js frontend), EOL & support-status tracking, import_batch_id provenance (+7 more)

### Community 92 - "Interfaces Panel UI"
Cohesion: 0.16
Nodes (11): CABLE_KINDS, CableDialog(), fmtSpeed(), IFACE_KINDS, InterfacesPanel(), useDevicePick(), Cable, CableKind (+3 more)

### Community 93 - "Device I/O Service (93)"
Cohesion: 0.19
Nodes (12): apply_device_import(), device_export_rows(), _load_refs(), plan_device_import(), AsyncSession, Rack, RackGroup, Site (+4 more)

### Community 94 - "Reader Service"
Cohesion: 0.24
Nodes (11): Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, _csv_sheet(), load_upload(), load_workbook_bytes(), XLSX/CSV -> sheet matrices (openpyxl read_only streams / csv module)., Drop fully-empty trailing rows/cols for a stable matrix shape., One CSV file -> one SheetMatrix named after the file stem. utf-8-sig first…, Dispatch on container type: ZIP -> xlsx workbook; otherwise try CSV text… (+3 more)

### Community 95 - "Workbook Import Tests (95)"
Cohesion: 0.19
Nodes (8): _master_blocks(), parse_sites_master(), (first, second) octet pairs a master row declares — lets sheet->site matching…, Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins., TestSitesMasterParser

### Community 96 - "Racks API (96)"
Cohesion: 0.18
Nodes (13): import_racks(), Smart rack/group bundle import — V5B's stateless flow for whole trees. Sheets…, reorder_racks(), apply_mapping_overrides(), User {source_header: field} overrides on top of the auto-map. field "" / null…, import_devices(), Smart device import. Stateless — the file is posted twice: dry-run preview…, reorder_devices() (+5 more)

### Community 97 - "Workbook Import Tests (97)"
Cohesion: 0.24
Nodes (6): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, TestClassify

### Community 98 - "Changelog Tests"
Cohesion: 0.23
Nodes (12): AsyncClient, tag_assignments.object_id has no FK — deleting a tagged object must drop its…, Tag.assignments is already ORM delete-orphan — each removed assignment lands in…, PATCH settings with a null value deletes the app_settings row — that delete…, /addresses/bulk action=delete used to issue one Core DELETE — invisible to the…, test_bulk_delete_writes_changelog_entries(), test_changelog_captures_ip_status_change(), test_changelog_records_crud() (+4 more)

### Community 99 - "Scanner Tests (99)"
Cohesion: 0.21
Nodes (8): on_hosts fires once per detection step with that chunk's new IPs — ARP batch…, When L2+L3 find nothing, the TCP fallback publishes its batch too., test_scan_cidr_emits_found_deltas(), fake_icmp(), fake_probe(), fake_ptr(), on_hosts(), test_scan_cidr_tcp_fallback_reports_found()

### Community 100 - "[Slug] Page"
Cohesion: 0.24
Nodes (9): DocPage(), dynamicParams, generateMetadata(), loadMarkdown(), DocsContent(), docCategoryLabel(), getDoc(), react-markdown (+1 more)

### Community 101 - "Changes"
Cohesion: 0.27
Nodes (11): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), SyncSession, register(), _repr() (+3 more)

### Community 102 - "Colors Service"
Cohesion: 0.29
Nodes (11): _as_date(), _as_str(), display_color_for(), _ordered_cmp(), Any, date, -1/0/1 comparing a column value to a rule's value string. Tries date first when…, Does ``rule`` fire on this row? NULL fields never match. (+3 more)

### Community 103 - "Prefix Api Tests"
Cohesion: 0.33
Nodes (10): _global_vrf_id(), Splits are counted arithmetically before materializing: anything over…, test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_prefixes_order_by_utilization_and_limit(), test_same_cidr_allowed_across_vrfs(), test_split_cardinality_cap(), test_split_endpoint() (+2 more)

### Community 104 - "Scanner Tests (104)"
Cohesion: 0.20
Nodes (8): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture, Stands in for the arq Redis pool — never actually dispatches work., scan_exclude_networks=10.70.0.64/26 inside scan_networks=10.70.0.0/24: the…, test_scheduler_and_route_share_exclusion_guard()

### Community 105 - "User Docs (105)"
Cohesion: 0.27
Nodes (11): Accounts & Roles, Insecure mode (IPAMBOX_ALLOW_INSECURE), Four roles (Administrator, Operator, Contributor, Viewer), Session-cookie authentication, Certificates, Certificate expiry tracking, Color rules, Scan targeting policy (+3 more)

### Community 107 - "Types"
Cohesion: 0.20
Nodes (10): devDependencies, autoprefixer, postcss, sharp, tailwindcss, @types/js-yaml, @types/node, @types/react (+2 more)

### Community 108 - "User Docs (108)"
Cohesion: 0.22
Nodes (10): GET /api/v1/devices/export.csv, GET /api/v1/devices/export.xlsx, CSV export, Export dropdown (Devices toolbar), Filtered-set export parity (devices-filtered.*), Filter facets as URL params, Export column round-trip contract, UTF-8 BOM encoding (Excel/Hebrew-safe) (+2 more)

### Community 109 - "Rack I/O Service (109)"
Cohesion: 0.33
Nodes (9): _float_field(), _fold(), _cable_match(), _CablePlan, _IfacePlan, _plan_cables(), _dev(), _iface() (+1 more)

### Community 110 - "History Panel UI"
Cohesion: 0.28
Nodes (8): ACTION_STYLES, ChangeDiff(), ChangeVal(), fmtChangeVal(), HistoryEntry(), HistoryPanel(), summary(), ChangeField

### Community 111 - "Check"
Cohesion: 0.25
Nodes (6): DIR, FACES, LAYOUTS, problems, referenced, slugs

### Community 112 - "Rbac Tests (112)"
Cohesion: 0.29
Nodes (4): auth_on(), fake_arq(), fixture, Turn auth on for a test, restore insecure mode after, and flush session/lockout…

### Community 113 - "Build (113)"
Cohesion: 0.29
Nodes (7): scripts, build, build:rack-library, check:rack-library, dev, lint, start

### Community 114 - "User Docs (114)"
Cohesion: 0.29
Nodes (7): API sketch, Device detail, Devices, Devices vs racks, From the IP drawer, Health rollup, The list

### Community 116 - "Racks API (116)"
Cohesion: 0.40
Nodes (5): delete_device(), Unrack, not delete: placement NULLs, the device row lives on. Real deletion is…, delete_device(), The real delete: IPs unlink (SET NULL), carrier children unmount., delete

### Community 117 - "Scan Policy Service"
Cohesion: 0.40
Nodes (4): exclusion_hit(), Scan-target policy shared by the API route, the scheduler, and the worker.…, Return the first excluded CIDR overlapping ``net`` (either direction), or None.…, test_exclusion_hit_both_directions()

### Community 118 - "Workbook Import Tests (118)"
Cohesion: 0.40
Nodes (3): קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., TestCircuitsParser

### Community 119 - "Chart"
Cohesion: 0.50
Nodes (4): ChartTheme, FALLBACK, readTheme(), useChartTheme()

### Community 120 - "User Docs (120)"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 144 - "Device I/O Service (144)"
Cohesion: 0.67
Nodes (3): StreamingResponse, Single-sheet plain-value workbook — the xlsx twin of csv_response., xlsx_response()

## Ambiguous Edges - Review These
- `Cable` → `Rack`  [AMBIGUOUS]
  frontend/src/content/docs/cabling.md · relation: conceptually_related_to

## Knowledge Gaps
- **355 isolated node(s):** `DeviceRow`, `AssetRow`, `RackRow`, `HandleState`, `SortableRowProps` (+350 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1230 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **38 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Cable` and `Rack`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `IPAddress` connect `Schemas` to `Scanner Tests (38)`, `Prefixes API`, `Data Models`, `Schemas (39)`, `Racks Tests`, `Racks API (40)`, `Schemas (14)`, `Scanner Tests (48)`, `Schemas (18)`, `Lists API`, `Maintenance API`, `Lists Tests`, `Devices Tests`, `Maintenance Tests`, `Schemas (30)`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `react` connect `[Id] Page` to `Rack Editor UI`, `Dialog UI`, `Prefix Detail Client Page`, `Color Rules Client Page`, `Rack Elevation UI`, `Import Client Page`, `Docs Page`, `History Panel UI`, `Prefixes Client Page`, `App Shell UI`, `Smart Import Dialog UI`, `React (49)`, `Rack Row UI`, `Prefix Tree UI`, `Chart`, `Error Page`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Why does `_split_dsn()` connect `Cabling Tests` to `Devices Tests`, `Racks Tests`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Are the 67 inferred relationships involving `IPAMError` (e.g. with `create_address()` and `_check_interface_link()`) actually correct?**
  _`IPAMError` has 67 INFERRED edges - model-reasoned connections that need verification._
- **What connects `DeviceRow`, `AssetRow`, `RackRow` to the rest of the system?**
  _355 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `[Id] Page` be split into smaller, more focused modules?**
  _Cohesion score 0.021135347513887008 - nodes in this community are weakly interconnected._