# Graph Report - IpamBox  (2026-09-24)

## Corpus Check
- 7 files · ~966,820 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3614 nodes · 11831 edges · 161 communities (100 shown, 31 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 760 edges (avg confidence: 0.94)
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
- Community 96
- Community 97
- Community 98
- Community 99
- Community 100
- Community 101
- Community 102
- Community 103
- Community 127
- Community 128
- Community 129
- Community 130
- Community 131
- Community 133
- Community 134
- Community 135
- Community 136
- Community 138
- Community 139
- Community 140
- Community 141
- Community 142
- Community 143
- Community 144
- Community 148
- Community 149
- Community 150
- Community 151
- Community 152
- Community 153
- Community 154
- Community 155
- Community 158
- Community 159
- Community 160

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
- `Device smart file I/O (export dropdown + smart import)` --semantically_similar_to--> `Export dropdown (Devices toolbar)`  [INFERRED] [semantically similar]
  README.md → frontend/src/content/docs/devices.md
- `Excel workbook import (per-sheet detection, dry-run, all-or-nothing/partial commit)` --semantically_similar_to--> `Smart import dialog`  [INFERRED] [semantically similar]
  README.md → frontend/src/content/docs/devices.md
- `Address CSV import/export (UTF-8 BOM)` --semantically_similar_to--> `CSV export`  [INFERRED] [semantically similar]
  README.md → frontend/src/content/docs/devices.md
- `Device smart file I/O (export dropdown + smart import)` --semantically_similar_to--> `Smart import dialog`  [INFERRED] [semantically similar]
  README.md → frontend/src/content/docs/devices.md
- `Inventory (asset register)` --semantically_similar_to--> `Certificate expiry tracking`  [INFERRED] [semantically similar]
  frontend/src/content/docs/inventory.md → frontend/src/content/docs/certificates.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Export → re-import round trip: export output re-imports cleanly via stable column contract and preserved id** — frontend_src_content_docs_devices_exportdropdown, frontend_src_content_docs_devices_csvexport, frontend_src_content_docs_devices_xlsxexport, frontend_src_content_docs_devices_roundtripcontract, frontend_src_content_docs_devices_apiimport [EXTRACTED 1.00]
- **Smart import pipeline: pick file → auto-map headers → dry-run preview → validated commit** — frontend_src_content_docs_devices_smartimportdialog, frontend_src_content_docs_devices_headerautomapping, frontend_src_content_docs_devices_dryrunpreview, frontend_src_content_docs_devices_matchprecedence, frontend_src_content_docs_devices_placementvalidation, frontend_src_content_docs_devices_force [EXTRACTED 1.00]
- **Import behavior modes: on_match, unracked_on_missing and force tune match/salvage/commit semantics** — frontend_src_content_docs_devices_onmatch, frontend_src_content_docs_devices_unrackedonmissing, frontend_src_content_docs_devices_force, frontend_src_content_docs_devices_apiimport [INFERRED 0.75]
- **Deterministic demo regeneration (fixed seed/timestamps)** — examples_generate_demo_data, examples_readme_demo_rack_dc_py [INFERRED 0.75]
- **Demo rack population pipeline (zip + script + /devices/import + Demo DC)** — examples_readme_demo_rack_dc_py, examples_readme_devices_import_endpoint [INFERRED 0.75]

## Communities (161 total, 31 thin omitted)

### Community 0 - "Frontend Pages"
Cohesion: 0.10
Nodes (87): EMPTY, ACTION_STYLES, EMPTY, EMPTY_EDIT, FACE_BADGE, AssetRow, EMPTY, IPAM_FAMILIES (+79 more)

### Community 1 - "Racks API"
Cohesion: 0.03
Nodes (97): metadata, viewport, ImportListDialog(), IpCell(), SortableColRow(), metadata, IP_ROLES, IP_STATUSES (+89 more)

### Community 2 - "Frontend Page Shells"
Cohesion: 0.04
Nodes (96): ArqRedis, cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession (+88 more)

### Community 3 - "Config & Migration Env"
Cohesion: 0.03
Nodes (41): nextConfig, metadata, metadata, metadata, metadata, metadata, metadata, metadata (+33 more)

### Community 4 - "Prefix Detail UI"
Cohesion: 0.07
Nodes (63): Audit trail via session flush hooks. before_flush collects (object, action,…, after_flush(), before_flush(), SyncSession, tag_assignments garbage collection. TagAssignment references its target…, register(), healthz(), metrics() (+55 more)

### Community 5 - "Changelog Core & Models"
Cohesion: 0.04
Nodes (78): _flag(), Any, AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), HostResult, _global_vrf_id(), _infer_scan_vrf() (+70 more)

### Community 6 - "Discovery & Print UI"
Cohesion: 0.03
Nodes (81): DragSession, metadata, AddressFilterPanel(), STATUSES, SETTINGS_SECTIONS, SettingsNav(), PrefixStatusBadge(), prefixVariant (+73 more)

### Community 7 - "Test Fixtures"
Cohesion: 0.05
Nodes (71): _address_csv_row(), _addresses_stmt(), bulk_addresses(), BulkBody, _check_interface_link(), create_address(), delete_address(), export_addresses() (+63 more)

### Community 8 - "Prefixes API"
Cohesion: 0.08
Nodes (67): CertificatesPage(), CircuitsPage(), DeviceDetailClient(), BulkResp, DiscoveryPage(), ImportPage(), InventoryPage(), ListsClient() (+59 more)

### Community 9 - "Rack Tests"
Cohesion: 0.06
Nodes (68): allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), _prefix_rows() (+60 more)

### Community 10 - "Import Wizard UI"
Cohesion: 0.04
Nodes (66): DEVICE_VIEWS, DeviceRow, DevicesPage(), EMPTY, IMPORT_FIELDS, IMPORT_OPTIONS, TEXT_CHIP_LABELS, metadata (+58 more)

### Community 11 - "List Filtering API"
Cohesion: 0.05
Nodes (51): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, create_vrf(), delete_vrf(), get_vrf(), list_vrfs(), AsyncSession, delete, get (+43 more)

### Community 12 - "Docker Stack & Rack Library"
Cohesion: 0.08
Nodes (57): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., _split_dsn() (+49 more)

### Community 13 - "Frontend App Shell"
Cohesion: 0.10
Nodes (64): _carrier(), _dev(), _group(), _imports(), _mount(), _next_free(), AsyncClient, AsyncSession (+56 more)

### Community 14 - "Addresses API"
Cohesion: 0.08
Nodes (59): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+51 more)

### Community 15 - "Workbook Service"
Cohesion: 0.07
Nodes (58): assets_rows(), _assign_site_sheets(), _assign_site_sheets_clean(), build_en_workbook(), build_mixed_workbook(), build_sites(), certificates_rows(), circuits_rows() (+50 more)

### Community 16 - "Demo Data Generator"
Cohesion: 0.06
Nodes (50): do_run_migrations(), run_migrations_online(), get_settings(), close_arq_pool(), close_redis(), get_redis(), Shared process-wide Redis client. Do NOT aclose() it per call — connections…, Shut down the shared client — lifespan/worker shutdown only. (+42 more)

### Community 17 - "Cables API"
Cohesion: 0.07
Nodes (47): create_rule(), delete_rule(), get_rule(), list_rules(), preview_rule(), AsyncSession, delete, get (+39 more)

### Community 18 - "VLANs API"
Cohesion: 0.07
Nodes (46): assemble_ip(), clean(), _clean_octets(), map_status(), mask_to_prefixlen(), network_of(), norm_header(), norm_mac() (+38 more)

### Community 19 - "Devices API"
Cohesion: 0.08
Nodes (18): parse_sites_master_records(), _Planner, _preview(), (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Folded sheet title vs site name/code — word-boundary matching so 'int' doesn't…, Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new… (+10 more)

### Community 20 - "Dashboard & Discovery API"
Cohesion: 0.08
Nodes (46): delete_scheduled_backup(), download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, delete, get, post (+38 more)

### Community 21 - "Page Components"
Cohesion: 0.12
Nodes (46): _cable_out(), _check_ends(), create_cable(), delete_cable(), _get_cable(), _get_interface(), interfaces_match_free_text(), list_cables() (+38 more)

### Community 22 - "User Docs"
Cohesion: 0.10
Nodes (45): bulk_rows(), _check_columns(), create_list(), create_row(), delete_list(), delete_row(), get_list(), list_lists() (+37 more)

### Community 23 - "Backup API"
Cohesion: 0.08
Nodes (44): _crud_router(), create_item(), delete_item(), get_item(), list_items(), reorder_items(), update_item(), _check_site() (+36 more)

### Community 24 - "Workbook Planner"
Cohesion: 0.10
Nodes (44): _carrier_diff_name(), _err(), _float_field(), _fold(), _int_field(), _ip_tokens(), _load_refs(), _match() (+36 more)

### Community 25 - "Changelog & Dashboard UI"
Cohesion: 0.09
Nodes (41): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+33 more)

### Community 26 - "Custom Lists"
Cohesion: 0.09
Nodes (44): Rack, _rack_detail(), Rack -> RackDetail with its (selectin-loaded) devices serialized, each carrying…, _check_refs(), create_device(), create_rack(), delete_device(), delete_rack() (+36 more)

### Community 27 - "Maintenance API"
Cohesion: 0.08
Nodes (42): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+34 more)

### Community 28 - "Entities & Schemas"
Cohesion: 0.17
Nodes (40): auth_on(), _backup_bytes(), _cable(), _device(), _gen(), _iface(), _ip(), _login() (+32 more)

### Community 29 - "Auth API"
Cohesion: 0.11
Nodes (29): parse_enum_set(), parse_int_set(), parse_token_set(), Rack elevations: racks + nested devices + Rackula import. Not a `_crud_router`…, IpRef, LinkedRef, NextFreeUOut, BaseModel (+21 more)

### Community 31 - "Cabling Tests"
Cohesion: 0.10
Nodes (27): ChangelogPage(), ACTION_STYLES, DashboardPage(), metadata, metadata, fmtEta(), ScansPage(), VrfDialog() (+19 more)

### Community 32 - "Scans API"
Cohesion: 0.09
Nodes (37): RackulaImportDialog(), ABBREV_TO_CATEGORY, canonicalCategory(), CATEGORY_TO_ABBREV, clip(), compareVersions(), decodeShareUrl(), DeviceLike (+29 more)

### Community 33 - "Error Pages"
Cohesion: 0.18
Nodes (35): AsyncClient, auth_on(), _csv(), _device(), _group(), _import(), _ip(), _login() (+27 more)

### Community 34 - "Imports API"
Cohesion: 0.11
Nodes (35): Device, Base, ConflictError, apply_device_patch(), carrier_children(), CarrierError, _check_carrier_mount(), check_layout_change() (+27 more)

### Community 35 - "Rack Groups API"
Cohesion: 0.13
Nodes (18): _master_row(), _matrix(), _plan(), _preview_of(), Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins. (+10 more)

### Community 36 - "Rack Detail & Rackula"
Cohesion: 0.15
Nodes (31): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+23 more)

### Community 37 - "Tags API"
Cohesion: 0.16
Nodes (33): _backup_bytes(), _envelope_bytes(), _mkusers(), User, Hand-craft a backup envelope (e.g. with a forged users table)., Guard: every ORM table must be backed up (or explicitly excluded). Adding a new…, Fresh-server scenario: the migration-seeded Global VRF is replaced by the…, Fresh-server scenario: the target's admins survive; its non-admin set is fully… (+25 more)

### Community 38 - "Backup Tests"
Cohesion: 0.09
Nodes (25): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, PreviewResp, SheetResults(), Step (+17 more)

### Community 39 - "Device Filter Panel"
Cohesion: 0.17
Nodes (27): _folded(), AsyncSession, get, Cross-object search for the command palette. One GET returns grouped matches…, Column expression with Hebrew final letters folded — pairs with fold_hebrew()…, Short label for a list-row search hit: key-column value, else the first non-…, _row_label(), search() (+19 more)

### Community 40 - "Settings Model"
Cohesion: 0.12
Nodes (30): _check_iface_refs(), create_interface(), delete_device(), delete_interface(), generate_interfaces(), _get_device(), _get_iface(), _iface_outs() (+22 more)

### Community 41 - "Worker & Scanner Tests"
Cohesion: 0.22
Nodes (26): str, UserRole, auth_on(), fake_arq(), login(), mkuser(), other_client(), AsyncClient (+18 more)

### Community 42 - "Sites API"
Cohesion: 0.10
Nodes (17): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, parse_certificates(), Positional 5-col layout: platform, target/VS, server, cert, expiry. (+9 more)

### Community 43 - "Search API"
Cohesion: 0.07
Nodes (29): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, js-yaml, jszip, lucide-react (+21 more)

### Community 44 - "Models & Maintenance Tests"
Cohesion: 0.17
Nodes (21): assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession, delete (+13 more)

### Community 45 - "Frontend Dependencies"
Cohesion: 0.14
Nodes (23): _build_out(), _lan_info(), _mask_url(), AsyncSession, get, Hide the password in a scheme://user:pass@host URL., LAN identity detected by the host-networked worker (written to Redis). Falls…, read_settings() (+15 more)

### Community 46 - "Reconcile Worker"
Cohesion: 0.11
Nodes (17): psycopg2-style URL for alembic offline mode / scripts., Settings, Effective, _env_sourced(), Any, Runtime-editable settings: app_settings rows override env defaults. Each public…, True when the field's current value differs from its declared default., One runtime-editable setting. field: the env-backed attribute on… (+9 more)

### Community 47 - "Frontend Config"
Cohesion: 0.08
Nodes (24): name, private, version, autoprefixer, clsx, postcss, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+16 more)

### Community 48 - "Rack Group View"
Cohesion: 0.25
Nodes (26): Address CSV import/export, IP Addresses, Circuits (WAN circuit register), Hierarchy Tree, Roll-up utilization, EOL & support-status tracking, Inventory (asset register), Site → VRF → Prefix → IP address data model (+18 more)

### Community 49 - "Rack Editor UI"
Cohesion: 0.14
Nodes (21): _cascade_site_fields(), create_site(), delete_site(), get_site(), list_sites(), AsyncSession, delete, get (+13 more)

### Community 50 - "OUI & Scanner"
Cohesion: 0.15
Nodes (21): DeviceFormDialog(), DragSession, DropRow(), EditorBlock(), errDetail(), Pending, RackEditor(), CarrierFrameSvg() (+13 more)

### Community 51 - "Workbook Import Tests"
Cohesion: 0.13
Nodes (23): arrLen(), attribution(), CATEGORY_COLOUR, CURATED, fetchBuf(), fetchJson(), FRONTEND, FULL_IMPORT (+15 more)

### Community 52 - "Tree Page"
Cohesion: 0.19
Nodes (19): metadata, ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), collectExpandableKeys(), flattenTree() (+11 more)

### Community 53 - "Settings API"
Cohesion: 0.11
Nodes (18): list_changelog(), AsyncSession, get, AsyncSession, get, stats(), confirm_discovered(), ConfirmBody (+10 more)

### Community 54 - "Security Core"
Cohesion: 0.15
Nodes (17): _check_range_overlap(), create_range(), delete_range(), list_ranges(), AsyncSession, delete, get, post (+9 more)

### Community 55 - "Scanner Tests"
Cohesion: 0.19
Nodes (19): errDetail(), findDevice(), GroupClient(), moveDevice(), RackGeom, slotRect, usedUSlots(), freeByRack() (+11 more)

### Community 56 - "RBAC Tests"
Cohesion: 0.16
Nodes (21): Accounts & Roles, Insecure mode (IPAMBOX_ALLOW_INSECURE), Four roles (Administrator, Operator, Contributor, Viewer), Session-cookie authentication, Address roles (vip/vrrp/hsrp/glbp/carp/secondary), IP drawer, mac_mismatch flag, Certificates (+13 more)

### Community 57 - "Workbook Parsers"
Cohesion: 0.18
Nodes (19): _devices_stmt(), export_devices_csv(), export_devices_xlsx(), _export_name(), _export_rows(), _filtered_devices(), _health_class(), list_devices() (+11 more)

### Community 58 - "Colors Tests"
Cohesion: 0.16
Nodes (20): _alembic_revisions(), backup_dir(), build_backup(), delete_backup_file(), list_backup_files(), prune_backups(), Any, Base (+12 more)

### Community 59 - "List Parsing"
Cohesion: 0.14
Nodes (15): _cell_text(), extract_list_table(), _infer_type(), _ips(), _is_ip_token(), SheetMatrix -> (column defs, row dicts). columns: [{key, label, type, options?,…, Raw cell -> stored string. Dates iso-format; everything else cleans., (type, extra) for one column — extra carries options/multi. (+7 more)

### Community 60 - "Ordering Tests"
Cohesion: 0.27
Nodes (19): _login(), _mk_rule(), _mk_site(), _mkuser(), AsyncClient, AsyncSession, Global row colors: manual row_color + rule-computed display_color. Covers the…, test_backup_roundtrips_color_rules() (+11 more)

### Community 61 - "TSConfig"
Cohesion: 0.28
Nodes (18): _circuit_order(), _login(), _mk_circuits(), _mkuser(), AsyncClient, AsyncSession, Global row ordering: POST /{entity}/reorder + pinned rows. Covered on both…, Reordering a subset keeps the slots those rows already had — rows outside the… (+10 more)

### Community 62 - "IPAM Extras Tests"
Cohesion: 0.20
Nodes (19): IPAddress, Cable, connected_interface_id (structured far-end port link), connected_ip (host-side NIC binding), DeviceInterface (device-owned port), L1 trace (cable path walk), match-free-text transition endpoint, One-cable-per-interface rule (+11 more)

### Community 63 - "Settings Tests"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 64 - "Docs Pages"
Cohesion: 0.20
Nodes (13): CommitOptions, ImportBatchOut, ListTarget, PreviewOptions, BaseModel, Per-sheet detection result shown in the wizard., Import a sheet as a custom list (user-selected or suggested)., User-confirmed mapping choices applied before building the plan. (+5 more)

### Community 65 - "Users API"
Cohesion: 0.22
Nodes (17): _prefix(), export.csv takes the same filters as the list endpoint — a filtered view…, Same filtered-export treatment on the prefixes CSV (F8)., A documented v6 /64's 2^64 host count must not reach dashboard sums (~1.8e19 >…, test_address_role_nat_and_bulk(), test_addresses_export_respects_filters(), test_bulk_reports_real_counts(), test_container_move_with_children_rejected() (+9 more)

### Community 66 - "Site Sheet Parsers"
Cohesion: 0.18
Nodes (4): _mklist(), TestBulkRows, TestListCRUD, TestRows

### Community 67 - "Sites Master Parsers"
Cohesion: 0.17
Nodes (15): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, Every new Settings > Features key is runtime-editable; untouched keys keep the…, test_backup_files_report_effective_schedule() (+7 more)

### Community 68 - "Interfaces Panel"
Cohesion: 0.14
Nodes (18): POST /api/v1/devices/import, Carrier two-pass mounting, Changelog / audit history, Dry-run preview with per-row {field:[old,new]} diffs, force commit mode (valid rows only), Header auto-mapping (English/Hebrew/NetBox), IP address, IP linking: existing addresses only, never creates (+10 more)

### Community 69 - "Changelog Tests"
Cohesion: 0.17
Nodes (8): _blocks(), parse_site_sheet(), Split duplicated column groups (031-style runaway): each block starts at an…, MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf., Bare 'Name' (Cellular) maps to the hostname field., Non-empty unnamed columns pile into cf['extra'] instead of vanishing (Pelephone…, TestSiteSheetExtras, TestSiteSheetParser

### Community 70 - "Search Tests"
Cohesion: 0.21
Nodes (10): Api, apply(), _device_payload(), emit_zip(), find_one(), _KeepMethodRedirect, layout_doc(), main() (+2 more)

### Community 71 - "Devices Docs"
Cohesion: 0.17
Nodes (16): CC0 1.0 Universal, netbox-community/devicetype-library, Rack device image library, Carrier (slot-layout device: shelves/trays), Device image library, Elevation editor, Find free U, Health overlay (+8 more)

### Community 72 - "Workbook Execute"
Cohesion: 0.19
Nodes (10): DocsIndexClient(), metadata, DocsNav(), BY_SLUG, DOC_ARTICLES, DOC_CATEGORIES, DocArticle, DocCategory (+2 more)

### Community 73 - "Workbook Reader"
Cohesion: 0.20
Nodes (11): str, RackFace, DeviceCreate, DeviceDetail, DeviceIpRef, DeviceOut, DeviceUpdate, BaseModel (+3 more)

### Community 74 - "Allocation Tests"
Cohesion: 0.22
Nodes (11): pick_key_column(), Custom-list extraction: turn any sheet into {columns, rows} for a list. Unlike…, Default merge column: first non-date/ip column filled in most rows (the…, Custom lists: CRUD + rows + IP resolution + workbook list-target import., v2 workbook: SRV2 edited, SRV3 added, SRV1 missing -> merge keeps SRV1, updates…, _servers_xlsx(), test_import_as_list_e2e(), test_manually_edited_row_wins_conflict() (+3 more)

### Community 75 - "Scanner Delta Tests"
Cohesion: 0.16
Nodes (11): CABLE_KINDS, CableDialog(), fmtSpeed(), IFACE_KINDS, InterfacesPanel(), useDevicePick(), Cable, CableKind (+3 more)

### Community 76 - "Docs Content"
Cohesion: 0.21
Nodes (11): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_now_enqueues(), test_clear_discovery() (+3 more)

### Community 77 - "Changelog Hooks"
Cohesion: 0.29
Nodes (12): deviceImage(), FACE_BADGE, RackElevation(), useLibraryBySlug(), Placed, libraryBySlug(), LibraryDevice, libraryImage() (+4 more)

### Community 78 - "Colors Service"
Cohesion: 0.15
Nodes (12): import_devices(), Smart device import. Stateless — the file is posted twice: dry-run preview…, _alias_to_field(), apply_device_import(), apply_mapping_overrides(), auto_map_headers(), parse_device_sheet(), Write the ok rows in one transaction. Creates go through the create path's… (+4 more)

### Community 79 - "Prefix API Tests"
Cohesion: 0.26
Nodes (7): _find_carrier(), _Occupancy, _placement_candidate(), Device, carrier cell -> the carrier row. '#id' resolves a stored device; names resolve…, Simulated rack occupancy: DB occupants plus earlier batch rows, kept current…, Merged post-patch Device for the occupancy simulation — the same blend…

### Community 80 - "Community 80"
Cohesion: 0.23
Nodes (12): AsyncClient, tag_assignments.object_id has no FK — deleting a tagged object must drop its…, Tag.assignments is already ORM delete-orphan — each removed assignment lands in…, PATCH settings with a null value deletes the app_settings row — that delete…, /addresses/bulk action=delete used to issue one Core DELETE — invisible to the…, test_bulk_delete_writes_changelog_entries(), test_changelog_captures_ip_status_change(), test_changelog_records_crud() (+4 more)

### Community 81 - "Community 81"
Cohesion: 0.31
Nodes (12): AsyncClient, Global /api/v1/search endpoint (UX-3)., Regression: list_addresses ?q= used to crash on a missing column., Site + VRF + prefix + address + one of each workbook entity., _seed(), test_addresses_q_filter_not_broken(), test_search_empty_query(), test_search_grouped_results() (+4 more)

### Community 82 - "Community 82"
Cohesion: 0.22
Nodes (13): api service (FastAPI/uvicorn backend), db service (PostgreSQL 16), ipam bridge network (192.0.2.0/24), redis service (Redis 7, appendonly), scanner service (arq worker, host networking), web service (Next.js frontend), import_batch_id provenance, Custom Lists (user-defined tables) (+5 more)

### Community 83 - "Community 83"
Cohesion: 0.21
Nodes (8): on_hosts fires once per detection step with that chunk's new IPs — ARP batch…, When L2+L3 find nothing, the TCP fallback publishes its batch too., test_scan_cidr_emits_found_deltas(), fake_icmp(), fake_probe(), fake_ptr(), on_hosts(), test_scan_cidr_tcp_fallback_reports_found()

### Community 84 - "Community 84"
Cohesion: 0.24
Nodes (9): DocPage(), dynamicParams, generateMetadata(), loadMarkdown(), DocsContent(), docCategoryLabel(), getDoc(), react-markdown (+1 more)

### Community 85 - "Community 85"
Cohesion: 0.20
Nodes (11): Asset, _asset_ref(), _check_refs(), create_device(), _detail(), Device -> DeviceDetail: IPs, asset, site/rack/carrier context, health rollup —…, Create a device — unracked inventory by default, or placed directly when…, Existence checks for the linkable FKs on create/patch payloads. (+3 more)

### Community 86 - "Community 86"
Cohesion: 0.27
Nodes (11): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), SyncSession, register(), _repr() (+3 more)

### Community 87 - "Community 87"
Cohesion: 0.33
Nodes (10): _global_vrf_id(), Splits are counted arithmetically before materializing: anything over…, test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_prefixes_order_by_utilization_and_limit(), test_same_cidr_allowed_across_vrfs(), test_split_cardinality_cap(), test_split_endpoint() (+2 more)

### Community 89 - "Community 89"
Cohesion: 0.20
Nodes (10): devDependencies, autoprefixer, postcss, sharp, tailwindcss, @types/js-yaml, @types/node, @types/react (+2 more)

### Community 90 - "Community 90"
Cohesion: 0.36
Nodes (9): CommandPalette(), Icon, Item, itemsFor(), remember(), SearchOut, searchDocs(), getPrefs() (+1 more)

### Community 91 - "Community 91"
Cohesion: 0.22
Nodes (10): GET /api/v1/devices/export.csv, GET /api/v1/devices/export.xlsx, CSV export, Export dropdown (Devices toolbar), Filtered-set export parity (devices-filtered.*), Filter facets as URL params, Export column round-trip contract, UTF-8 BOM encoding (Excel/Hebrew-safe) (+2 more)

### Community 92 - "Community 92"
Cohesion: 0.43
Nodes (7): _mk_prefix(), test_address_crud_and_dup_guard(), test_allocation_skips_existing(), test_concurrent_allocation_unique(), alloc(), test_exhausted_prefix_conflicts(), test_sequential_allocation_skips_boundaries()

### Community 93 - "Community 93"
Cohesion: 0.25
Nodes (6): DIR, FACES, LAYOUTS, problems, referenced, slugs

### Community 95 - "Community 95"
Cohesion: 0.29
Nodes (4): _col_class(), _positional_columns(), Dominant content class of a column sample., Headerless sheet: locate the IP column, then assign the remaining canonical…

### Community 96 - "Community 96"
Cohesion: 0.29
Nodes (7): scripts, build, build:rack-library, check:rack-library, dev, lint, start

### Community 97 - "Community 97"
Cohesion: 0.29
Nodes (7): API sketch, Device detail, Devices, Devices vs racks, From the IP drawer, Health rollup, The list

### Community 99 - "Community 99"
Cohesion: 0.53
Nodes (5): moveRowNav(), G_CHORDS, isEditableTarget(), modalOpen(), useGlobalShortcuts()

### Community 100 - "Community 100"
Cohesion: 0.40
Nodes (3): קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., TestCircuitsParser

### Community 101 - "Community 101"
Cohesion: 0.50
Nodes (4): ChartTheme, FALLBACK, readTheme(), useChartTheme()

### Community 102 - "Community 102"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 103 - "Community 103"
Cohesion: 0.67
Nodes (3): ChangeField, ChangeLogOut, BaseModel

## Ambiguous Edges - Review These
- `Cable` → `Rack`  [AMBIGUOUS]
  frontend/src/content/docs/cabling.md · relation: conceptually_related_to

## Knowledge Gaps
- **347 isolated node(s):** `AssetRow`, `Step`, `PrefixRow`, `RackRow`, `ServiceRow` (+342 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1169 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **31 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Cable` and `Rack`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `IPAddress` connect `Test Fixtures` to `Frontend Page Shells`, `Site Sheet Parsers`, `Prefix Detail UI`, `Changelog Core & Models`, `Device Filter Panel`, `Rack Tests`, `Allocation Tests`, `Docker Stack & Rack Library`, `Docs Content`, `Frontend App Shell`, `Settings API`, `User Docs`, `Page Components`, `Custom Lists`, `Maintenance API`, `Auth API`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Why does `react` connect `Config & Migration Env` to `Frontend Pages`, `Racks API`, `Community 99`, `Community 101`, `Backup Tests`, `Discovery & Print UI`, `Prefixes API`, `Workbook Execute`, `Import Wizard UI`, `Changelog Hooks`, `Frontend Config`, `OUI & Scanner`, `Tree Page`, `Community 90`, `Color Rules API`, `Cabling Tests`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `Demo Data Generator` to `Frontend Page Shells`, `Prefix Detail UI`, `Rack Tests`, `Allocation Tests`, `Worker & Scanner Tests`, `Docker Stack & Rack Library`, `Frontend Dependencies`, `Addresses API`, `Reconcile Worker`, `Frontend App Shell`, `Community 81`, `Dashboard & Discovery API`, `Changelog & Dashboard UI`, `Ordering Tests`, `TSConfig`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Are the 67 inferred relationships involving `IPAMError` (e.g. with `_check_interface_link()` and `create_address()`) actually correct?**
  _`IPAMError` has 67 INFERRED edges - model-reasoned connections that need verification._
- **Are the 32 inferred relationships involving `IPAddress` (e.g. with `_address_csv_row()` and `_addresses_stmt()`) actually correct?**
  _`IPAddress` has 32 INFERRED edges - model-reasoned connections that need verification._
- **What connects `AssetRow`, `Step`, `PrefixRow` to the rest of the system?**
  _347 weakly-connected nodes found - possible documentation gaps or missing edges._