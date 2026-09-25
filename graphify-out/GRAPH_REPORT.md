# Graph Report - IpamBox  (2026-09-25)

## Corpus Check
- Large corpus: 2578 files · ~990,626 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder.

## Summary
- 3894 nodes · 12509 edges · 179 communities (109 shown, 38 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 826 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- cn
- devices-client.tsx
- prefixes-client.tsx
- IPAMError
- services/backup.py
- device-detail-client.tsx
- rackula.ts
- react
- scans.py
- test_cabling.py
- device-detail-client.tsx
- index.ts
- test_racks.py
- User
- get_settings
- cables.py
- generate_demo_data.py
- v1/devices.py
- lists.py
- color_rules.py
- clean
- _Planner
- entities.py
- prefixes.py
- rack_io.py
- upload_workbook
- test_lists.py
- test_devices.py
- backend/tests/test_rack_io.py
- redis.py
- get_settings
- AsyncSession
- test_device_io.py
- route-error.tsx
- rack_groups.py
- schemas/ip_range.py
- Device
- test_backup.py
- backend/app/services/device_io.py
- addresses.py
- v1/racks.py
- device-filter-panel.tsx
- IPAddress
- v1/search.py
- vlans.py
- UserRole
- runtime_settings.py
- _matrix
- scanner.py
- test_scanner.py
- _FakeRedis
- dependencies
- test_ipam_extras.py
- test_scanner.py
- package.json
- command-palette.tsx
- v1/backup.py
- users.py
- arq==0.26.1
- tree-client.tsx
- parse_site_sheet
- build-rack-library.mjs
- test_colors.py
- test_workbook_import.py
- parse_bundle
- ipam.py
- test_ordering.py
- list_racks
- maintenance.py
- prefixes.py
- test_prefix_api.py
- compilerOptions
- schemas/device.py
- schemas/ip_address.py
- test_cabling.py
- test_settings.py
- Racks
- Device (first-class host entity)
- IpamBox
- Smart import dialog
- demo_rack_dc.py
- app-shell.tsx
- test_maintenance.py
- network.py
- _mklist
- IpamBox
- execute.py
- test_search.py
- Inventory (asset register)
- interfaces-panel.tsx
- build_backup
- workbook/__init__.py
- parse_sites_master
- classify_sheet
- test_changelog.py
- test_scan_cidr_tcp_fallback_reports_found
- command-palette.tsx
- _FakePool
- Settings
- apply_bundle
- devDependencies
- CSV export
- check-rack-library.mjs
- prefixes.py
- scripts
- Devices
- test_entities.py
- shortcuts.ts
- rack_io.py
- Docs: IP Addresses
- Security Policy
- next-env.d.ts
- POST /api/v1/devices/import
- Racks REST API (GET /api/v1/racks)
- xff-shim.js
- README.md
- Rack device image library bundle
- delete
- DeviceInterface
- get
- LinkedRef
- patch
- post
- ReorderBody
- Device
- IPAddress
- Rack
- RackGroup
- Site
- Rack
- RackGroup
- Site
- CustomList
- Any
- Cable
- IpamBox App Icon (icon.svg)
- Root Layout (layout.tsx, title: IpamBox)
- GET /api/v1/devices/export.csv
- GET /api/v1/devices/export.xlsx
- ip_addresses table
- GET /api/v1/racks/export.csv
- GET /api/v1/racks/export.xlsx
- GET /api/v1/rack-groups/{id}/export.xlsx
- GET /api/v1/racks/{id}/export.xlsx
- LanInfo
- Rack
- SettingsOut

## God Nodes (most connected - your core abstractions)
1. `cn()` - 157 edges
2. `react` - 127 edges
3. `IPAMError` - 94 edges
4. `IPAddress` - 91 edges
5. `get_or_404()` - 75 edges
6. `useAsyncData()` - 74 edges
7. `lucide-react` - 71 edges
8. `User` - 65 edges
9. `useAuth()` - 63 edges
10. `get_settings()` - 60 edges

## Surprising Connections (you probably didn't know these)
- `CSV export` --semantically_similar_to--> `Address CSV import/export (UTF-8 BOM)`  [INFERRED] [semantically similar]
  frontend/src/content/docs/devices.md → README.md
- `Export dropdown (Devices toolbar)` --semantically_similar_to--> `Device smart file I/O (export dropdown + smart import)`  [INFERRED] [semantically similar]
  frontend/src/content/docs/devices.md → README.md
- `Smart import dialog` --semantically_similar_to--> `Excel workbook import (per-sheet detection, dry-run, all-or-nothing/partial commit)`  [INFERRED] [semantically similar]
  frontend/src/content/docs/devices.md → README.md
- `Smart import dialog` --semantically_similar_to--> `Device smart file I/O (export dropdown + smart import)`  [INFERRED] [semantically similar]
  frontend/src/content/docs/devices.md → README.md
- `LanInfo` --calls--> `_lan_info()`  [EXTRACTED]
  frontend/src/types/index.ts → backend/app/api/v1/settings.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **IpamBox docker-compose service stack** — compose_db_service, compose_redis_service, compose_api_service, compose_scanner_service, compose_web_service [EXTRACTED 1.00]

## Communities (179 total, 38 thin omitted)

### Community 0 - "cn"
Cohesion: 0.04
Nodes (103): metadata, viewport, IpCell(), SortableColRow(), IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES (+95 more)

### Community 1 - "devices-client.tsx"
Cohesion: 0.09
Nodes (88): CertificatesPage(), EMPTY, CircuitsPage(), EMPTY, DEVICE_VIEWS, DeviceRow, DevicesPage(), EMPTY (+80 more)

### Community 2 - "prefixes-client.tsx"
Cohesion: 0.02
Nodes (44): nextConfig, metadata, metadata, metadata, metadata, metadata, metadata, metadata (+36 more)

### Community 3 - "IPAMError"
Cohesion: 0.05
Nodes (92): _crud_router(), create_item(), delete_item(), get_item(), list_items(), reorder_items(), update_item(), delete_prefix() (+84 more)

### Community 4 - "services/backup.py"
Cohesion: 0.06
Nodes (67): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), SyncSession, Audit trail via session flush hooks. before_flush collects (object, action,…, register() (+59 more)

### Community 5 - "device-detail-client.tsx"
Cohesion: 0.08
Nodes (55): ACTION_STYLES, BulkResp, LabelClient(), FACE_BADGE, FACE_BADGE, DataPage(), download(), FeatureDef (+47 more)

### Community 6 - "rackula.ts"
Cohesion: 0.05
Nodes (80): DeviceFormDialog(), DragSession, DropRow(), EditorBlock(), errDetail(), Pending, RackEditor(), CarrierFrameSvg() (+72 more)

### Community 7 - "react"
Cohesion: 0.09
Nodes (53): EMPTY_EDIT, FACE_BADGE, ImportListDialog(), IPAM_FAMILIES, Step, PrefixRow, Draft, ENTITIES (+45 more)

### Community 8 - "scans.py"
Cohesion: 0.06
Nodes (70): cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession, get (+62 more)

### Community 9 - "test_cabling.py"
Cohesion: 0.08
Nodes (63): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., _split_dsn() (+55 more)

### Community 10 - "device-detail-client.tsx"
Cohesion: 0.05
Nodes (58): ACTION_STYLES, ChangelogPage(), metadata, DashboardPage(), DeviceDetailClient(), DiscoveryPage(), ImportPage(), ListsClient() (+50 more)

### Community 11 - "index.ts"
Cohesion: 0.04
Nodes (65): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, PreviewResp, SheetResults(), Step (+57 more)

### Community 12 - "test_racks.py"
Cohesion: 0.10
Nodes (64): _carrier(), _dev(), _group(), _imports(), _mount(), _next_free(), AsyncClient, AsyncSession (+56 more)

### Community 13 - "User"
Cohesion: 0.08
Nodes (64): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+56 more)

### Community 14 - "get_settings"
Cohesion: 0.05
Nodes (48): do_run_migrations(), run_migrations_online(), AsyncSession, get, stats(), _build_out(), _lan_info(), _mask_url() (+40 more)

### Community 15 - "cables.py"
Cohesion: 0.10
Nodes (49): _cable_out(), _check_ends(), create_cable(), delete_cable(), _get_cable(), _get_interface(), interfaces_match_free_text(), list_cables() (+41 more)

### Community 16 - "generate_demo_data.py"
Cohesion: 0.07
Nodes (58): assets_rows(), _assign_site_sheets(), _assign_site_sheets_clean(), build_en_workbook(), build_mixed_workbook(), build_sites(), certificates_rows(), circuits_rows() (+50 more)

### Community 17 - "v1/devices.py"
Cohesion: 0.08
Nodes (57): Asset, _asset_ref(), _check_iface_refs(), _check_refs(), create_device(), create_interface(), delete_device(), delete_interface() (+49 more)

### Community 18 - "lists.py"
Cohesion: 0.08
Nodes (52): list_changelog(), AsyncSession, get, bulk_rows(), _check_columns(), create_list(), create_row(), delete_list() (+44 more)

### Community 19 - "color_rules.py"
Cohesion: 0.07
Nodes (47): create_rule(), delete_rule(), get_rule(), list_rules(), preview_rule(), AsyncSession, delete, get (+39 more)

### Community 20 - "clean"
Cohesion: 0.07
Nodes (47): assemble_ip(), clean(), _clean_octets(), excel_date(), map_status(), mask_to_prefixlen(), network_of(), norm_header() (+39 more)

### Community 21 - "_Planner"
Cohesion: 0.09
Nodes (17): parse_sites_master_records(), _Planner, (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Folded sheet title vs site name/code — word-boundary matching so 'int' doesn't…, Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new…, Resolve a 10.{second}.x sheet — site_number is only meaningful inside the… (+9 more)

### Community 22 - "entities.py"
Cohesion: 0.07
Nodes (31): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, AssetKind, str, AssetCreate, AssetOut, AssetUpdate, BaseModel, field_validator (+23 more)

### Community 23 - "prefixes.py"
Cohesion: 0.09
Nodes (39): allocate_next_available(), create_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), _prefix_rows(), prefix_tree() (+31 more)

### Community 24 - "rack_io.py"
Cohesion: 0.10
Nodes (45): _float_field(), _fold(), _name_map(), _parse_id(), _resolve_named(), bundle_sheets(), BundleSheet, _cable_match() (+37 more)

### Community 25 - "upload_workbook"
Cohesion: 0.10
Nodes (40): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+32 more)

### Community 26 - "test_lists.py"
Cohesion: 0.09
Nodes (29): ListTarget, Import a sheet as a custom list (user-selected or suggested)., _cell_text(), extract_list_table(), _infer_type(), _ips(), _is_ip_token(), pick_key_column() (+21 more)

### Community 27 - "test_devices.py"
Cohesion: 0.14
Nodes (38): _cable(), _device(), _group(), _iface(), _ip(), _login(), _mkuser(), _prefix() (+30 more)

### Community 28 - "backend/tests/test_rack_io.py"
Cohesion: 0.18
Nodes (39): _bundle(), _by_sheet(), _cable(), _csv(), _device(), _group(), _iface(), _import() (+31 more)

### Community 29 - "redis.py"
Cohesion: 0.08
Nodes (34): ArqRedis, close_arq_pool(), close_redis(), get_arq_pool(), Shut down the shared client — lifespan/worker shutdown only., Shared ARQ pool — callers must not close() it per job., redis_settings_from_url(), lifespan() (+26 more)

### Community 30 - "get_settings"
Cohesion: 0.10
Nodes (34): _data_key(), decrypt_str(), encrypt_str(), _master_key(), Exception, Secrets at rest — the credential contract v7/v8/v12/v14 build on. A single…, Unseal a "v1:…" blob. Strict prefix check — unknown formats, malformed payloads…, Base for secrets-service failures — never carries secret material. (+26 more)

### Community 31 - "AsyncSession"
Cohesion: 0.11
Nodes (38): _check_refs(), create_device(), create_rack(), delete_device(), delete_rack(), _device_out(), _devices(), export_rack_xlsx() (+30 more)

### Community 32 - "test_device_io.py"
Cohesion: 0.18
Nodes (36): _csv(), _device(), _group(), _import(), _ip(), _login(), _mkuser(), _prefix() (+28 more)

### Community 34 - "rack_groups.py"
Cohesion: 0.11
Nodes (34): _check_site(), create_rack_group(), delete_rack_group(), export_rack_group_xlsx(), _get_group(), get_rack_group(), list_rack_groups(), _ordered_racks() (+26 more)

### Community 35 - "schemas/ip_range.py"
Cohesion: 0.09
Nodes (29): _check_range_overlap(), create_range(), delete_range(), list_ranges(), AsyncSession, delete, get, patch (+21 more)

### Community 36 - "Device"
Cohesion: 0.11
Nodes (35): Device, Base, ConflictError, apply_device_patch(), carrier_children(), CarrierError, _check_carrier_mount(), check_layout_change() (+27 more)

### Community 37 - "test_backup.py"
Cohesion: 0.17
Nodes (34): User, _backup_bytes(), _envelope_bytes(), _mkusers(), User, Hand-craft a backup envelope (e.g. with a forged users table)., Guard: every ORM table must be backed up (or explicitly excluded). Adding a new…, Fresh-server scenario: the migration-seeded Global VRF is replaced by the… (+26 more)

### Community 38 - "backend/app/services/device_io.py"
Cohesion: 0.17
Nodes (27): _carrier_diff_name(), _err(), _find_carrier(), _int_field(), _ip_tokens(), _load_refs(), _match(), _Occupancy (+19 more)

### Community 39 - "addresses.py"
Cohesion: 0.12
Nodes (33): _address_csv_row(), _addresses_stmt(), bulk_addresses(), BulkBody, _check_interface_link(), create_address(), delete_address(), export_addresses() (+25 more)

### Community 40 - "v1/racks.py"
Cohesion: 0.13
Nodes (26): Rack elevations: racks + nested devices + Rackula import. Not a `_crud_router`…, str, RackFace, IpRef, LinkedRef, NextFreeUOut, BaseModel, field_validator (+18 more)

### Community 41 - "device-filter-panel.tsx"
Cohesion: 0.09
Nodes (29): containsFold(), DEVICE_FILTER_PARAMS, DEVICE_TEXT_PARAMS, DeviceFilterPanel(), DeviceFilterState, DeviceTextParam, FACES, filterDevices() (+21 more)

### Community 42 - "IPAddress"
Cohesion: 0.08
Nodes (27): _parse_statuses(), CSV of status names (e.g. 'active,discovered') -> set; 422 on bad., list_discovered(), AsyncSession, get, Unconfirmed hosts found by scanners, pending admin review. No limit -> the full…, IPStatus, str (+19 more)

### Community 43 - "v1/search.py"
Cohesion: 0.17
Nodes (27): _folded(), AsyncSession, get, Cross-object search for the command palette. One GET returns grouped matches…, Column expression with Hebrew final letters folded — pairs with fold_hebrew()…, Short label for a list-row search hit: key-column value, else the first non-…, _row_label(), search() (+19 more)

### Community 44 - "vlans.py"
Cohesion: 0.16
Nodes (27): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+19 more)

### Community 45 - "UserRole"
Cohesion: 0.21
Nodes (26): str, UserRole, auth_on(), fake_arq(), login(), mkuser(), other_client(), AsyncClient (+18 more)

### Community 46 - "runtime_settings.py"
Cohesion: 0.09
Nodes (20): psycopg2-style URL for alembic offline mode / scripts., Settings, Effective, _env_sourced(), Any, Exception, Runtime-editable settings: app_settings rows override env defaults. Each public…, True when the field's current value differs from its declared default. (+12 more)

### Community 47 - "_matrix"
Cohesion: 0.16
Nodes (16): _master_row(), _matrix(), _plan(), _preview_of(), קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches… (+8 more)

### Community 48 - "scanner.py"
Cohesion: 0.10
Nodes (24): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), detect_interface(), _host_chunks(), _icmp_sweep(), infer_device_type() (+16 more)

### Community 49 - "test_scanner.py"
Cohesion: 0.13
Nodes (24): _global_vrf_id(), _infer_scan_vrf(), Pick the VRF for a scan that didn't specify one. An exact-match prefix living…, _scan_vrf(), WorkerSettings, _extra_vrf(), _global_id(), _mk_prefix() (+16 more)

### Community 50 - "_FakeRedis"
Cohesion: 0.10
Nodes (22): sf(), alloc(), _api_cancel(), _FakeRedis, _mk_job(), In-memory stand-in for the worker's redis client (get/set/publish)., Point the worker at the test DB (sf) and the fake redis client., Simulate the API-side cancel: terminal status on a fresh connection. (+14 more)

### Community 51 - "dependencies"
Cohesion: 0.07
Nodes (29): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, js-yaml, jszip, lucide-react (+21 more)

### Community 52 - "test_ipam_extras.py"
Cohesion: 0.15
Nodes (26): _prefix(), _range(), export.csv takes the same filters as the list endpoint — a filtered view…, Same filtered-export treatment on the prefixes CSV (F8)., A documented v6 /64's 2^64 host count must not reach dashboard sums (~1.8e19 >…, test_address_role_nat_and_bulk(), test_addresses_export_respects_filters(), test_bulk_reports_real_counts() (+18 more)

### Community 53 - "test_scanner.py"
Cohesion: 0.10
Nodes (26): Any, _flag(), AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), HostResult, A stored (e.g. imported) MAC that differs from the scan is flagged in…, Scanning a /24 under a documented /16 must not mark the other 255 subnets'… (+18 more)

### Community 54 - "package.json"
Cohesion: 0.07
Nodes (25): name, private, version, autoprefixer, clsx, postcss, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+17 more)

### Community 55 - "command-palette.tsx"
Cohesion: 0.14
Nodes (19): DocsIndexClient(), metadata, CommandPalette(), Icon, Item, itemsFor(), remember(), SearchOut (+11 more)

### Community 56 - "v1/backup.py"
Cohesion: 0.13
Nodes (24): delete_scheduled_backup(), download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, delete, get, post (+16 more)

### Community 57 - "users.py"
Cohesion: 0.14
Nodes (24): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+16 more)

### Community 58 - "arq==0.26.1"
Cohesion: 0.14
Nodes (23): alembic==1.14.0, arq==0.26.1, asyncpg==0.30.0, bcrypt==4.3.0, cryptography==50.0.1, fastapi==0.115.6, httpx==0.28.1, openpyxl==3.1.5 (+15 more)

### Community 59 - "tree-client.tsx"
Cohesion: 0.18
Nodes (20): metadata, ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), collectExpandableKeys(), flattenTree() (+12 more)

### Community 60 - "parse_site_sheet"
Cohesion: 0.11
Nodes (12): _blocks(), _col_class(), parse_site_sheet(), _positional_columns(), Split duplicated column groups (031-style runaway): each block starts at an…, Dominant content class of a column sample., Headerless sheet: locate the IP column, then assign the remaining canonical…, MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf. (+4 more)

### Community 61 - "build-rack-library.mjs"
Cohesion: 0.13
Nodes (23): arrLen(), attribution(), CATEGORY_COLOUR, CURATED, fetchBuf(), fetchJson(), FRONTEND, FULL_IMPORT (+15 more)

### Community 62 - "test_colors.py"
Cohesion: 0.22
Nodes (22): auth_on(), _login(), _mk_rule(), _mk_site(), _mkuser(), AsyncClient, AsyncSession, fixture (+14 more)

### Community 63 - "test_workbook_import.py"
Cohesion: 0.09
Nodes (9): Workbook import: normalizer/parser unit tests (no DB) + API e2e., Small synthetic workbook: sites master + one site sheet + circuits., test_commit_twice_rejected(), test_import_e2e(), TestAssetsParser, TestCertificatesParser, TestNormalize, TestServersParser (+1 more)

### Community 64 - "parse_bundle"
Cohesion: 0.13
Nodes (20): import_devices(), Smart device import. Stateless — the file is posted twice: dry-run preview…, import_racks(), _alias_to_field(), apply_device_import(), apply_mapping_overrides(), auto_map_fields(), auto_map_headers() (+12 more)

### Community 65 - "ipam.py"
Cohesion: 0.20
Nodes (19): confirm_discovered(), ConfirmBody, BaseModel, post, One-click confirm a discovered host (default -> Active)., create_network(), AsyncSession, post (+11 more)

### Community 66 - "test_ordering.py"
Cohesion: 0.22
Nodes (21): auth_on(), _circuit_order(), _login(), _mk_circuits(), _mkuser(), AsyncClient, AsyncSession, fixture (+13 more)

### Community 67 - "list_racks"
Cohesion: 0.13
Nodes (20): parse_enum_set(), parse_int_set(), parse_token_set(), _export_name(), _export_racks(), export_racks_csv(), export_racks_xlsx(), _filtered_racks() (+12 more)

### Community 68 - "maintenance.py"
Cohesion: 0.21
Nodes (19): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+11 more)

### Community 69 - "prefixes.py"
Cohesion: 0.21
Nodes (18): children(), lowest_free(), parent_chain(), Inclusive [first, last] integer range of host-usable addresses., True when network/broadcast addresses are unusable for hosts (IPv4 <= /30)., Lowest usable address integer not in `taken` or any excluded range., Split `net` into children of `new_prefix` length., The smallest candidate network that strictly contains `net`. (+10 more)

### Community 70 - "test_prefix_api.py"
Cohesion: 0.22
Nodes (18): _addrs(), _global_vrf_id(), _mkprefix(), Splits are counted arithmetically before materializing: anything over…, test_gateway_clear_removes_only_pristine_row(), test_gateway_never_clobbers_manual_row(), test_gateway_validation(), test_next_ip_never_hands_out_gateway() (+10 more)

### Community 71 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 72 - "schemas/device.py"
Cohesion: 0.16
Nodes (11): DeviceCreate, DeviceDetail, DeviceIpRef, DeviceOut, DeviceUpdate, BaseModel, field_validator, Device entity schemas — a host that may be racked and owns IPs. Placement… (+3 more)

### Community 73 - "schemas/ip_address.py"
Cohesion: 0.24
Nodes (11): IPRole, ConnectedInterfaceRef, IPAddressCreate, IPAddressOut, IPAddressPage, IPAddressUpdate, _norm_mac(), BaseModel (+3 more)

### Community 74 - "test_cabling.py"
Cohesion: 0.23
Nodes (17): may_write(), Field-ownership check for source-stamped rows (ip_addresses et al.). True when…, _mk_prefix(), V6 provenance — ip_addresses.source: stamping, ownership, filtering. Every…, Manual and imported rows keep their provenance when a scan sees them — observed…, Response bodies carry `source` but never any *_enc-style field., test_csv_import_stamps_import(), test_export_filters_and_carries_source() (+9 more)

### Community 75 - "test_settings.py"
Cohesion: 0.17
Nodes (15): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, Every new Settings > Features key is runtime-editable; untouched keys keep the…, test_backup_files_report_effective_schedule() (+7 more)

### Community 76 - "Racks"
Cohesion: 0.16
Nodes (17): CC0 1.0 Universal, netbox-community/devicetype-library, Rack device image library, Carrier (slot-layout device: shelves/trays), Device image library, Elevation editor, Find free U, Health overlay (+9 more)

### Community 77 - "Device (first-class host entity)"
Cohesion: 0.22
Nodes (18): IPAddress, Cable, connected_interface_id (structured far-end port link), connected_ip (host-side NIC binding), DeviceInterface (device-owned port), L1 trace (cable path walk), match-free-text transition endpoint, One-cable-per-interface rule (+10 more)

### Community 78 - "IpamBox"
Cohesion: 0.37
Nodes (18): Circuits (WAN circuit register), Hierarchy Tree, Roll-up utilization, Site → VRF → Prefix → IP address data model, IpamBox, Row Colors, Command palette, Services (service catalog) (+10 more)

### Community 79 - "Smart import dialog"
Cohesion: 0.14
Nodes (18): POST /api/v1/devices/import, Carrier two-pass mounting, Changelog / audit history, Dry-run preview with per-row {field:[old,new]} diffs, force commit mode (valid rows only), Header auto-mapping (English/Hebrew/NetBox), IP address, IP linking: existing addresses only, never creates (+10 more)

### Community 80 - "demo_rack_dc.py"
Cohesion: 0.21
Nodes (10): Api, apply(), _device_payload(), emit_zip(), find_one(), _KeepMethodRedirect, layout_doc(), main() (+2 more)

### Community 81 - "app-shell.tsx"
Cohesion: 0.15
Nodes (15): AppearancePage(), PrefsInit(), AddrMapView, applyPrefs(), DEFAULT_PREFS, DensityChoice, FxLevel, Prefs (+7 more)

### Community 82 - "test_maintenance.py"
Cohesion: 0.18
Nodes (13): Site, _get_or_create_site(), _site_key(), fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient (+5 more)

### Community 83 - "network.py"
Cohesion: 0.22
Nodes (9): _ip(), NetworkCreate, NetworkDhcpRange, NetworkOut, NetworkPrefix, NetworkVlanNew, BaseModel, field_validator (+1 more)

### Community 84 - "_mklist"
Cohesion: 0.21
Nodes (3): _mklist(), TestListCRUD, TestRows

### Community 85 - "IpamBox"
Cohesion: 0.24
Nodes (16): Address roles (vip/vrrp/hsrp/glbp/carp/secondary), Address CSV import/export, IP Addresses, IP drawer, mac_mismatch flag, Changelog, Per-object history, Discovery Inbox (+8 more)

### Community 86 - "execute.py"
Cohesion: 0.21
Nodes (13): _apply_list(), execute_plan(), rep(), _get_or_create_list(), _get_or_create_prefix(), _get_or_create_vlan(), _get_or_create_vrf(), _group_by_sheet() (+5 more)

### Community 87 - "test_search.py"
Cohesion: 0.25
Nodes (14): auth_on(), AsyncClient, fixture, Global /api/v1/search endpoint (UX-3)., Regression: list_addresses ?q= used to crash on a missing column., Site + VRF + prefix + address + one of each workbook entity., _seed(), test_addresses_q_filter_not_broken() (+6 more)

### Community 88 - "Inventory (asset register)"
Cohesion: 0.19
Nodes (15): api service (FastAPI/uvicorn backend), db service (PostgreSQL 16), ipam bridge network (192.0.2.0/24), redis service (Redis 7, appendonly), scanner service (arq worker, host networking), web service (Next.js frontend), EOL & support-status tracking, import_batch_id provenance (+7 more)

### Community 89 - "interfaces-panel.tsx"
Cohesion: 0.16
Nodes (11): CABLE_KINDS, CableDialog(), fmtSpeed(), IFACE_KINDS, InterfacesPanel(), useDevicePick(), CableKind, CableTraceHop (+3 more)

### Community 90 - "build_backup"
Cohesion: 0.25
Nodes (14): _alembic_revisions(), backup_dir(), delete_backup_file(), list_backup_files(), prune_backups(), Path, Known migration revisions, head first (linear chain)., Fetch a scheduled backup by file name (path-traversal safe). (+6 more)

### Community 91 - "workbook/__init__.py"
Cohesion: 0.24
Nodes (11): Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, _csv_sheet(), load_upload(), load_workbook_bytes(), XLSX/CSV -> sheet matrices (openpyxl read_only streams / csv module)., Drop fully-empty trailing rows/cols for a stable matrix shape., One CSV file -> one SheetMatrix named after the file stem. utf-8-sig first…, Dispatch on container type: ZIP -> xlsx workbook; otherwise try CSV text… (+3 more)

### Community 92 - "parse_sites_master"
Cohesion: 0.19
Nodes (8): _master_blocks(), parse_sites_master(), (first, second) octet pairs a master row declares — lets sheet->site matching…, Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins., TestSitesMasterParser

### Community 93 - "classify_sheet"
Cohesion: 0.24
Nodes (6): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, TestClassify

### Community 94 - "test_changelog.py"
Cohesion: 0.23
Nodes (12): AsyncClient, tag_assignments.object_id has no FK — deleting a tagged object must drop its…, Tag.assignments is already ORM delete-orphan — each removed assignment lands in…, PATCH settings with a null value deletes the app_settings row — that delete…, /addresses/bulk action=delete used to issue one Core DELETE — invisible to the…, test_bulk_delete_writes_changelog_entries(), test_changelog_captures_ip_status_change(), test_changelog_records_crud() (+4 more)

### Community 95 - "test_scan_cidr_tcp_fallback_reports_found"
Cohesion: 0.21
Nodes (8): on_hosts fires once per detection step with that chunk's new IPs — ARP batch…, When L2+L3 find nothing, the TCP fallback publishes its batch too., test_scan_cidr_emits_found_deltas(), fake_icmp(), fake_probe(), fake_ptr(), on_hosts(), test_scan_cidr_tcp_fallback_reports_found()

### Community 96 - "command-palette.tsx"
Cohesion: 0.24
Nodes (9): DocPage(), dynamicParams, generateMetadata(), loadMarkdown(), DocsContent(), docCategoryLabel(), getDoc(), react-markdown (+1 more)

### Community 97 - "_FakePool"
Cohesion: 0.20
Nodes (8): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture, Stands in for the arq Redis pool — never actually dispatches work., scan_exclude_networks=10.70.0.64/26 inside scan_networks=10.70.0.0/24: the…, test_scheduler_and_route_share_exclusion_guard()

### Community 98 - "Settings"
Cohesion: 0.27
Nodes (11): Accounts & Roles, Insecure mode (IPAMBOX_ALLOW_INSECURE), Four roles (Administrator, Operator, Contributor, Viewer), Session-cookie authentication, Certificates, Certificate expiry tracking, Color rules, Scan targeting policy (+3 more)

### Community 99 - "apply_bundle"
Cohesion: 0.22
Nodes (5): apply_bundle(), BundlePlan, Commit a clean (or forced) plan in one transaction — same apply order as the…, Every sheet's verdicts + the commit payload. Pure plan — dry_run and commit…, Cable

### Community 100 - "devDependencies"
Cohesion: 0.20
Nodes (10): devDependencies, autoprefixer, postcss, sharp, tailwindcss, @types/js-yaml, @types/node, @types/react (+2 more)

### Community 101 - "CSV export"
Cohesion: 0.22
Nodes (10): GET /api/v1/devices/export.csv, GET /api/v1/devices/export.xlsx, CSV export, Export dropdown (Devices toolbar), Filtered-set export parity (devices-filtered.*), Filter facets as URL params, Export column round-trip contract, UTF-8 BOM encoding (Excel/Hebrew-safe) (+2 more)

### Community 102 - "check-rack-library.mjs"
Cohesion: 0.25
Nodes (6): DIR, FACES, LAYOUTS, problems, referenced, slugs

### Community 103 - "prefixes.py"
Cohesion: 0.52
Nodes (6): _mk_prefix(), test_address_crud_and_dup_guard(), test_allocation_skips_existing(), test_concurrent_allocation_unique(), test_exhausted_prefix_conflicts(), test_sequential_allocation_skips_boundaries()

### Community 104 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, build:rack-library, check:rack-library, dev, lint, start

### Community 105 - "Devices"
Cohesion: 0.29
Nodes (7): API sketch, Device detail, Devices, Devices vs racks, From the IP drawer, Health rollup, The list

### Community 107 - "shortcuts.ts"
Cohesion: 0.53
Nodes (5): moveRowNav(), G_CHORDS, isEditableTarget(), modalOpen(), useGlobalShortcuts()

### Community 108 - "rack_io.py"
Cohesion: 0.40
Nodes (5): ip_display(), Any, Normalize asyncpg-returned ipaddress objects / strings to display form. INET…, to_int(), device_export_rows()

### Community 109 - "Docs: IP Addresses"
Cohesion: 0.40
Nodes (5): Docs: IP Addresses, Docs: Devices, Docs: Racks, Docs: Settings, Docs: Subnets

### Community 110 - "Security Policy"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

## Ambiguous Edges - Review These
- `Cable` → `Rack`  [AMBIGUOUS]
  frontend/src/content/docs/cabling.md · relation: conceptually_related_to

## Knowledge Gaps
- **350 isolated node(s):** `NavGroup`, `NavItem`, `SplitPlan`, `Row`, `SortKey` (+345 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1236 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **38 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Cable` and `Rack`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `apply_bundle()` connect `apply_bundle` to `parse_bundle`, `devices-client.tsx`, `IPAMError`, `Device`, `device-detail-client.tsx`, `backend/app/services/device_io.py`, `v1/racks.py`, `cables.py`, `rack_io.py`?**
  _High betweenness centrality (0.156) - this node is a cross-community bridge._
- **Why does `Site` connect `devices-client.tsx` to `apply_bundle`, `device-detail-client.tsx`, `react`, `device-detail-client.tsx`, `index.ts`, `rack_io.py`?**
  _High betweenness centrality (0.112) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `get_settings` to `IPAMError`, `services/backup.py`, `scans.py`, `test_racks.py`, `User`, `prefixes.py`, `upload_workbook`, `test_lists.py`, `test_devices.py`, `backend/tests/test_rack_io.py`, `redis.py`, `get_settings`, `test_device_io.py`, `UserRole`, `runtime_settings.py`, `v1/backup.py`, `test_colors.py`, `test_ordering.py`, `test_search.py`?**
  _High betweenness centrality (0.100) - this node is a cross-community bridge._
- **Are the 68 inferred relationships involving `IPAMError` (e.g. with `create_address()` and `_check_interface_link()`) actually correct?**
  _`IPAMError` has 68 INFERRED edges - model-reasoned connections that need verification._
- **Are the 42 inferred relationships involving `IPAddress` (e.g. with `_device_out()` and `_resolve_ips()`) actually correct?**
  _`IPAddress` has 42 INFERRED edges - model-reasoned connections that need verification._
- **What connects `NavGroup`, `NavItem`, `SplitPlan` to the rest of the system?**
  _350 weakly-connected nodes found - possible documentation gaps or missing edges._