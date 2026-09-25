# Graph Report - IpamBox  (2026-09-25)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 3807 nodes · 12234 edges · 204 communities (114 shown, 59 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 802 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e4848d09`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- prefixes-client.tsx
- devices-client.tsx
- react
- device-detail-client.tsx
- test_cabling.py
- cn
- prefixes.py
- services/backup.py
- test_racks.py
- index.ts
- get_settings
- generate_demo_data.py
- test_lists.py
- v1/devices.py
- app-shell.tsx
- test_scanner.py
- cables.py
- _Planner
- entities.py
- rack_io.py
- ipam.py
- color_rules.py
- maintenance.py
- scans.py
- get_redis
- test_devices.py
- worker.py
- User
- backend/tests/test_rack_io.py
- lists.py
- backend/app/services/device_io.py
- command-palette.tsx
- get_or_404
- IPAMError
- test_device_io.py
- route-error.tsx
- Device
- clean
- device-filter-panel.tsx
- addresses.py
- test_backup.py
- rackula.ts
- runtime_settings.py
- group-client.tsx
- v1/backup.py
- AsyncSession
- v1/search.py
- vlans.py
- redis.py
- UserRole
- IpamBox
- IPAddress
- rack_groups.py
- tags.py
- dependencies
- upload_workbook
- _FakeRedis
- v1/racks.py
- users.py
- package.json
- scanner.py
- _matrix
- build-rack-library.mjs
- tree-client.tsx
- parsers.py
- test_colors.py
- schemas/ip_address.py
- build_backup
- test_ordering.py
- execute.py
- test_workbook_import.py
- rack-editor.tsx
- compilerOptions
- parse_bundle
- test_ipam_extras.py
- test_settings.py
- rack-collision.ts
- parse_site_sheet
- demo_rack_dc.py
- Device (first-class host entity)
- _mklist
- Smart import dialog
- apply_bundle
- parse_sites_master
- test_search.py
- interfaces-panel.tsx
- Racks
- schemas/device.py
- workbook/__init__.py
- test_maintenance.py
- schemas/ip_range.py
- classify_sheet
- test_changelog.py
- Settings
- test_scan_cidr_tcp_fallback_reports_found
- list_racks
- after_flush
- rule_matches
- test_prefix_api.py
- _FakePool
- TestNormalize
- devDependencies
- Inventory (asset register)
- CSV export
- _device_out
- check-rack-library.mjs
- RackFace
- scripts
- Devices
- exclusion_hit
- test_entities.py
- api service (FastAPI/uvicorn backend)
- Rack device image library
- shortcuts.ts
- .test_legacy_bezeq_layout
- use-chart-theme.ts
- Security Policy
- app/page.tsx
- racks/[id]/page.tsx
- _fail_inflight_scans
- arq==0.26.1
- asyncpg==0.30.0
- pydantic==2.10.3
- pytest==8.3.4
- next-env.d.ts
- POST /api/v1/devices/import
- Racks REST API (GET /api/v1/racks)
- xff-shim.js
- README.md
- Rack device image library bundle
- delete
- post
- delete
- DeviceInterface
- get
- LinkedRef
- patch
- post
- ReorderBody
- Base
- str
- field_validator
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
- alembic==1.14.0
- bcrypt==4.3.0
- fastapi==0.115.6
- httpx==0.28.1
- openpyxl==3.1.5
- psutil==6.1.0
- scapy==2.6.1
- uvicorn[standard]==0.32.1
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
4. `IPAddress` - 80 edges
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
- `scanner service (arq worker, host networking)` --shares_data_with--> `ip column type (live IPAM resolution)`  [INFERRED]
  docker-compose.yml → frontend/src/content/docs/lists.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Rack bundle export -> dry-run preview -> import round-trip** — frontend_src_content_docs_racks_export_xlsx, frontend_src_content_docs_racks_rack_export_xlsx, frontend_src_content_docs_racks_group_export_xlsx, frontend_src_content_docs_racks_import_endpoint [EXTRACTED 1.00]
- **V5C racks & groups smart export/import feature** — frontend_src_content_docs_racks_export_xlsx, frontend_src_content_docs_racks_import_endpoint, frontend_src_content_docs_devices_import_endpoint [EXTRACTED 1.00]

## Communities (204 total, 59 thin omitted)

### Community 0 - "prefixes-client.tsx"
Cohesion: 0.03
Nodes (75): nextConfig, CertificatesPage(), metadata, ChangelogPage(), metadata, CircuitsPage(), metadata, DevicesPage() (+67 more)

### Community 1 - "devices-client.tsx"
Cohesion: 0.09
Nodes (74): EMPTY, EMPTY, DEVICE_VIEWS, DeviceRow, EMPTY, IMPORT_FIELDS, IMPORT_OPTIONS, TEXT_CHIP_LABELS (+66 more)

### Community 2 - "react"
Cohesion: 0.08
Nodes (56): ImportListDialog(), IPAM_FAMILIES, Step, LoginPage(), metadata, BackupSettingsPage(), downloadUrl(), fmtSize() (+48 more)

### Community 3 - "device-detail-client.tsx"
Cohesion: 0.05
Nodes (62): ACTION_STYLES, ACTION_STYLES, EMPTY_EDIT, FACE_BADGE, BulkResp, metadata, PrintClient(), LabelClient() (+54 more)

### Community 4 - "test_cabling.py"
Cohesion: 0.06
Nodes (80): may_write(), Field-ownership check for source-stamped rows (ip_addresses et al.). True when…, _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params'). (+72 more)

### Community 5 - "cn"
Cohesion: 0.05
Nodes (68): IpCell(), SortableColRow(), IP_ROLES, IP_STATUSES, RANGE_ROLES, SplitDialog(), SplitPlan, toggleIn() (+60 more)

### Community 6 - "prefixes.py"
Cohesion: 0.05
Nodes (73): allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), _prefix_rows() (+65 more)

### Community 7 - "services/backup.py"
Cohesion: 0.10
Nodes (35): _cascade_site_fields(), Propagate site code/number/name changes to linked entities that were following…, Audit trail via session flush hooks. before_flush collects (object, action,…, AppSetting, Runtime-editable setting override. Absent row -> env var -> default., Asset, SW/HW catalog rows (תוכנות וחומרות) and serial-number inventory…, Base (+27 more)

### Community 8 - "test_racks.py"
Cohesion: 0.09
Nodes (65): _carrier(), _dev(), _group(), _imports(), _mount(), _next_free(), AsyncClient, AsyncSession (+57 more)

### Community 9 - "index.ts"
Cohesion: 0.04
Nodes (61): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, SheetResults() (+53 more)

### Community 10 - "get_settings"
Cohesion: 0.06
Nodes (56): do_run_migrations(), run_migrations_online(), _build_out(), _mask_url(), AsyncSession, get, patch, Hide the password in a scheme://user:pass@host URL. (+48 more)

### Community 11 - "generate_demo_data.py"
Cohesion: 0.07
Nodes (58): assets_rows(), _assign_site_sheets(), _assign_site_sheets_clean(), build_en_workbook(), build_mixed_workbook(), build_sites(), certificates_rows(), circuits_rows() (+50 more)

### Community 12 - "test_lists.py"
Cohesion: 0.06
Nodes (42): CustomList, CustomListRow, User-defined table — preserves a workbook sheet's own shape (e.g. 'שרתים…, One row of a custom list — ``data`` maps column key -> string value., ListTarget, PreviewOptions, Import a sheet as a custom list (user-selected or suggested)., User-confirmed mapping choices applied before building the plan. (+34 more)

### Community 13 - "v1/devices.py"
Cohesion: 0.08
Nodes (57): Asset, _asset_ref(), _check_iface_refs(), _check_refs(), create_device(), create_interface(), delete_device(), delete_interface() (+49 more)

### Community 14 - "app-shell.tsx"
Cohesion: 0.05
Nodes (48): metadata, viewport, AppearancePage(), metadata, AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT (+40 more)

### Community 15 - "test_scanner.py"
Cohesion: 0.07
Nodes (48): Any, _flag(), AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), HostResult, _global_vrf_id(), _infer_scan_vrf() (+40 more)

### Community 16 - "cables.py"
Cohesion: 0.12
Nodes (46): _cable_out(), _check_ends(), create_cable(), delete_cable(), _get_cable(), _get_interface(), interfaces_match_free_text(), list_cables() (+38 more)

### Community 17 - "_Planner"
Cohesion: 0.09
Nodes (16): _Planner, (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Folded sheet title vs site name/code — word-boundary matching so 'int' doesn't…, Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new…, Resolve a 10.{second}.x sheet — site_number is only meaningful inside the…, A declared octet block claims the sheet — unless its site is inactive, in which… (+8 more)

### Community 18 - "entities.py"
Cohesion: 0.07
Nodes (31): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, AssetKind, str, AssetCreate, AssetOut, AssetUpdate, BaseModel, field_validator (+23 more)

### Community 19 - "rack_io.py"
Cohesion: 0.09
Nodes (46): ip_display(), Any, Normalize asyncpg-returned ipaddress objects / strings to display form. INET…, to_int(), device_export_rows(), _fold(), _name_map(), bundle_sheets() (+38 more)

### Community 20 - "ipam.py"
Cohesion: 0.09
Nodes (31): list_changelog(), AsyncSession, get, AsyncSession, get, stats(), confirm_discovered(), ConfirmBody (+23 more)

### Community 21 - "color_rules.py"
Cohesion: 0.09
Nodes (36): create_rule(), delete_rule(), get_rule(), list_rules(), preview_rule(), AsyncSession, delete, get (+28 more)

### Community 22 - "maintenance.py"
Cohesion: 0.08
Nodes (42): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+34 more)

### Community 23 - "scans.py"
Cohesion: 0.09
Nodes (37): ArqRedis, cancel_scan(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession, get (+29 more)

### Community 24 - "get_redis"
Cohesion: 0.08
Nodes (41): get_redis(), Shared process-wide Redis client. Do NOT aclose() it per call — connections…, client_ip(), create_session(), destroy_other_sessions(), destroy_session(), destroy_session_by_suffix(), _fails_key() (+33 more)

### Community 25 - "test_devices.py"
Cohesion: 0.14
Nodes (38): _cable(), _device(), _group(), _iface(), _ip(), _login(), _mkuser(), _prefix() (+30 more)

### Community 26 - "worker.py"
Cohesion: 0.09
Nodes (40): _lan_info(), LAN identity detected by the host-networked worker (written to Redis). Falls…, redis_settings_from_url(), set_actor(), detect_interface(), detect_local_cidr(), Exception, CIDR of the default-route interface, e.g. '192.168.1.0/24'. (+32 more)

### Community 27 - "User"
Cohesion: 0.12
Nodes (38): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+30 more)

### Community 28 - "backend/tests/test_rack_io.py"
Cohesion: 0.18
Nodes (39): _bundle(), _by_sheet(), _cable(), _csv(), _device(), _group(), _iface(), _import() (+31 more)

### Community 29 - "lists.py"
Cohesion: 0.11
Nodes (37): bulk_rows(), _check_columns(), create_list(), create_row(), delete_list(), delete_row(), get_list(), list_lists() (+29 more)

### Community 30 - "backend/app/services/device_io.py"
Cohesion: 0.16
Nodes (31): _carrier_diff_name(), _err(), _find_carrier(), _float_field(), _int_field(), _ip_tokens(), _load_refs(), _match() (+23 more)

### Community 31 - "command-palette.tsx"
Cohesion: 0.10
Nodes (28): DocsIndexClient(), metadata, DocPage(), dynamicParams, generateMetadata(), loadMarkdown(), CommandPalette(), Icon (+20 more)

### Community 32 - "get_or_404"
Cohesion: 0.09
Nodes (38): _crud_router(), create_item(), delete_item(), get_item(), list_items(), update_item(), update_row(), _check_site() (+30 more)

### Community 33 - "IPAMError"
Cohesion: 0.10
Nodes (32): reorder_items(), ReorderBody, reorder_racks(), post, reorder_sites(), create_vrf(), delete_vrf(), get_vrf() (+24 more)

### Community 34 - "test_device_io.py"
Cohesion: 0.18
Nodes (36): _csv(), _device(), _group(), _import(), _ip(), _login(), _mkuser(), _prefix() (+28 more)

### Community 36 - "Device"
Cohesion: 0.11
Nodes (35): Device, Base, ConflictError, apply_device_patch(), carrier_children(), CarrierError, _check_carrier_mount(), check_layout_change() (+27 more)

### Community 37 - "clean"
Cohesion: 0.09
Nodes (32): Row 0 of an unrecognized sheet looks like headers when every cell is a short…, _sniff_header_row(), assemble_ip(), clean(), _clean_octets(), excel_date(), map_status(), mask_to_prefixlen() (+24 more)

### Community 38 - "device-filter-panel.tsx"
Cohesion: 0.09
Nodes (33): containsFold(), DEVICE_FILTER_PARAMS, DEVICE_TEXT_PARAMS, DeviceFilterPanel(), DeviceFilterState, DeviceTextParam, FACES, filterDevices() (+25 more)

### Community 39 - "addresses.py"
Cohesion: 0.11
Nodes (33): _address_csv_row(), bulk_addresses(), BulkBody, _check_interface_link(), create_address(), delete_address(), export_addresses(), get_address() (+25 more)

### Community 40 - "test_backup.py"
Cohesion: 0.16
Nodes (33): _backup_bytes(), _envelope_bytes(), _mkusers(), User, Hand-craft a backup envelope (e.g. with a forged users table)., Guard: every ORM table must be backed up (or explicitly excluded). Adding a new…, Fresh-server scenario: the migration-seeded Global VRF is replaced by the…, Fresh-server scenario: the target's admins survive; its non-admin set is fully… (+25 more)

### Community 41 - "rackula.ts"
Cohesion: 0.09
Nodes (33): RackulaImportDialog(), ABBREV_TO_CATEGORY, canonicalCategory(), CATEGORY_TO_ABBREV, clip(), compareVersions(), decodeShareUrl(), DeviceLike (+25 more)

### Community 42 - "runtime_settings.py"
Cohesion: 0.09
Nodes (22): psycopg2-style URL for alembic offline mode / scripts., Settings, Effective, _env_sourced(), get_effective(), Any, AsyncSession, Exception (+14 more)

### Community 43 - "group-client.tsx"
Cohesion: 0.14
Nodes (26): DashboardPage(), DragSession, errDetail(), findDevice(), GroupClient(), moveDevice(), metadata, RackDetailPage() (+18 more)

### Community 44 - "v1/backup.py"
Cohesion: 0.11
Nodes (29): delete_scheduled_backup(), download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, delete, get, post (+21 more)

### Community 45 - "AsyncSession"
Cohesion: 0.14
Nodes (31): _check_refs(), create_device(), delete_device(), delete_rack(), _devices(), _export_name(), export_rack_xlsx(), export_racks_csv() (+23 more)

### Community 46 - "v1/search.py"
Cohesion: 0.17
Nodes (27): _folded(), AsyncSession, get, Cross-object search for the command palette. One GET returns grouped matches…, Column expression with Hebrew final letters folded — pairs with fold_hebrew()…, Short label for a list-row search hit: key-column value, else the first non-…, _row_label(), search() (+19 more)

### Community 47 - "vlans.py"
Cohesion: 0.16
Nodes (27): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+19 more)

### Community 48 - "redis.py"
Cohesion: 0.11
Nodes (27): close_arq_pool(), close_redis(), Shut down the shared client — lifespan/worker shutdown only., lifespan(), shutdown(), auth_on(), AsyncClient, fixture (+19 more)

### Community 49 - "UserRole"
Cohesion: 0.21
Nodes (26): str, UserRole, auth_on(), fake_arq(), login(), mkuser(), other_client(), AsyncClient (+18 more)

### Community 50 - "IpamBox"
Cohesion: 0.21
Nodes (31): Address roles (vip/vrrp/hsrp/glbp/carp/secondary), Address CSV import/export, IP Addresses, IP drawer, mac_mismatch flag, Changelog, Per-object history, Circuits (WAN circuit register) (+23 more)

### Community 51 - "IPAddress"
Cohesion: 0.11
Nodes (25): _addresses_stmt(), list_discovered(), AsyncSession, get, Unconfirmed hosts found by scanners, pending admin review. No limit -> the full…, IPAddress, IPStatus, device_health() (+17 more)

### Community 52 - "rack_groups.py"
Cohesion: 0.11
Nodes (29): create_rack_group(), delete_rack_group(), export_rack_group_xlsx(), _get_group(), get_rack_group(), list_rack_groups(), _ordered_racks(), AsyncSession (+21 more)

### Community 53 - "tags.py"
Cohesion: 0.15
Nodes (24): assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession, delete (+16 more)

### Community 54 - "dependencies"
Cohesion: 0.07
Nodes (29): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, js-yaml, jszip, lucide-react (+21 more)

### Community 55 - "upload_workbook"
Cohesion: 0.12
Nodes (27): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+19 more)

### Community 56 - "_FakeRedis"
Cohesion: 0.10
Nodes (21): _api_cancel(), _FakeRedis, _mk_job(), In-memory stand-in for the worker's redis client (get/set/publish)., Point the worker at the test DB (sf) and the fake redis client., Simulate the API-side cancel: terminal status on a fresh connection., Cancel flag polled between phases -> ScanCancelled -> CANCELLED, and no…, Audit race: API writes CANCELLED mid-scan while the redis flag is lost… (+13 more)

### Community 57 - "v1/racks.py"
Cohesion: 0.17
Nodes (23): Rack elevations: racks + nested devices + Rackula import. Not a `_crud_router`…, str, RackFace, IpRef, LinkedRef, NextFreeUOut, BaseModel, RackCreate (+15 more)

### Community 58 - "users.py"
Cohesion: 0.14
Nodes (25): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+17 more)

### Community 59 - "package.json"
Cohesion: 0.07
Nodes (25): name, private, version, autoprefixer, clsx, postcss, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+17 more)

### Community 60 - "scanner.py"
Cohesion: 0.12
Nodes (20): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), _host_chunks(), _icmp_sweep(), infer_device_type(), _ptr_lookup() (+12 more)

### Community 61 - "_matrix"
Cohesion: 0.21
Nodes (13): _master_row(), _matrix(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind… (+5 more)

### Community 62 - "build-rack-library.mjs"
Cohesion: 0.13
Nodes (23): arrLen(), attribution(), CATEGORY_COLOUR, CURATED, fetchBuf(), fetchJson(), FRONTEND, FULL_IMPORT (+15 more)

### Community 63 - "tree-client.tsx"
Cohesion: 0.18
Nodes (19): metadata, ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), collectExpandableKeys(), flattenTree() (+11 more)

### Community 64 - "parsers.py"
Cohesion: 0.11
Nodes (17): norm_header(), Header cell -> lowercase, single-spaced, for signature matching. Edge…, _col_class(), _is_header_echo(), _leftover_bits(), _map_columns(), parse_assets(), parse_inventory() (+9 more)

### Community 65 - "test_colors.py"
Cohesion: 0.22
Nodes (22): auth_on(), _login(), _mk_rule(), _mk_site(), _mkuser(), AsyncClient, AsyncSession, fixture (+14 more)

### Community 66 - "schemas/ip_address.py"
Cohesion: 0.14
Nodes (10): field_validator, _strip_name(), ConnectedInterfaceRef, IPAddressOut, IPAddressPage, IPAddressUpdate, _norm_mac(), BaseModel (+2 more)

### Community 67 - "build_backup"
Cohesion: 0.15
Nodes (22): _alembic_revisions(), backup_dir(), build_backup(), delete_backup_file(), list_backup_files(), prune_backups(), Any, Base (+14 more)

### Community 68 - "test_ordering.py"
Cohesion: 0.22
Nodes (21): auth_on(), _circuit_order(), _login(), _mk_circuits(), _mkuser(), AsyncClient, AsyncSession, fixture (+13 more)

### Community 69 - "execute.py"
Cohesion: 0.18
Nodes (17): _apply_list(), commit_batch(), execute_plan(), rep(), _get_or_create_list(), _get_or_create_prefix(), _get_or_create_site(), _get_or_create_vlan() (+9 more)

### Community 70 - "test_workbook_import.py"
Cohesion: 0.13
Nodes (14): parse_certificates(), parse_servers(), Positional 5-col layout: platform, target/VS, server, cert, expiry., 002 שרתים בייצור: Name, Guest OS, IP Address(multi), Cert, License, owner., Workbook import: normalizer/parser unit tests (no DB) + API e2e., Small synthetic workbook: sites master + one site sheet + circuits., Commit-time PlanError must 422 AND record the failure. The route rolls back…, test_commit_plan_error_marks_batch_failed() (+6 more)

### Community 71 - "rack-editor.tsx"
Cohesion: 0.20
Nodes (17): DragSession, DropRow(), EditorBlock(), Pending, CarrierFrameSvg(), DeviceBlockSvg(), deviceImage(), FACE_BADGE (+9 more)

### Community 72 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 73 - "parse_bundle"
Cohesion: 0.16
Nodes (18): import_devices(), Smart device import. Stateless — the file is posted twice: dry-run preview…, import_racks(), _alias_to_field(), apply_mapping_overrides(), auto_map_fields(), auto_map_headers(), remap() (+10 more)

### Community 74 - "test_ipam_extras.py"
Cohesion: 0.22
Nodes (17): _prefix(), export.csv takes the same filters as the list endpoint — a filtered view…, Same filtered-export treatment on the prefixes CSV (F8)., A documented v6 /64's 2^64 host count must not reach dashboard sums (~1.8e19 >…, test_address_role_nat_and_bulk(), test_addresses_export_respects_filters(), test_bulk_reports_real_counts(), test_container_move_with_children_rejected() (+9 more)

### Community 75 - "test_settings.py"
Cohesion: 0.17
Nodes (15): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, Every new Settings > Features key is runtime-editable; untouched keys keep the…, test_backup_files_report_effective_schedule() (+7 more)

### Community 76 - "rack-collision.ts"
Cohesion: 0.19
Nodes (15): DeviceFormDialog(), errDetail(), RackEditor(), canMount(), canPlace(), conflicts(), facesCollide(), freeSlots() (+7 more)

### Community 77 - "parse_site_sheet"
Cohesion: 0.17
Nodes (8): _blocks(), parse_site_sheet(), Split duplicated column groups (031-style runaway): each block starts at an…, MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf., Bare 'Name' (Cellular) maps to the hostname field., Non-empty unnamed columns pile into cf['extra'] instead of vanishing (Pelephone…, TestSiteSheetExtras, TestSiteSheetParser

### Community 78 - "demo_rack_dc.py"
Cohesion: 0.21
Nodes (10): Api, apply(), _device_payload(), emit_zip(), find_one(), _KeepMethodRedirect, layout_doc(), main() (+2 more)

### Community 79 - "Device (first-class host entity)"
Cohesion: 0.22
Nodes (17): IPAddress, Cable, connected_interface_id (structured far-end port link), connected_ip (host-side NIC binding), DeviceInterface (device-owned port), L1 trace (cable path walk), match-free-text transition endpoint, One-cable-per-interface rule (+9 more)

### Community 80 - "_mklist"
Cohesion: 0.21
Nodes (3): _mklist(), TestListCRUD, TestRows

### Community 81 - "Smart import dialog"
Cohesion: 0.17
Nodes (16): POST /api/v1/devices/import, Carrier two-pass mounting, Changelog / audit history, Dry-run preview with per-row {field:[old,new]} diffs, force commit mode (valid rows only), Header auto-mapping (English/Hebrew/NetBox), Match precedence: id → serial_number → mac_address → name+site, NetBox header aliases (device_role→device type, device_type→model, position→U) (+8 more)

### Community 82 - "apply_bundle"
Cohesion: 0.14
Nodes (8): apply_device_import(), apply_bundle(), BundlePlan, Commit a clean (or forced) plan in one transaction — same apply order as the…, Every sheet's verdicts + the commit payload. Pure plan — dry_run and commit…, Cable, RackGroup, RackGroupDetail

### Community 83 - "parse_sites_master"
Cohesion: 0.17
Nodes (9): _master_blocks(), parse_sites_master(), (first, second) octet pairs a master row declares — lets sheet->site matching…, parse_sites_master_records(), Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins. (+1 more)

### Community 84 - "test_search.py"
Cohesion: 0.25
Nodes (14): auth_on(), AsyncClient, fixture, Global /api/v1/search endpoint (UX-3)., Regression: list_addresses ?q= used to crash on a missing column., Site + VRF + prefix + address + one of each workbook entity., _seed(), test_addresses_q_filter_not_broken() (+6 more)

### Community 85 - "interfaces-panel.tsx"
Cohesion: 0.16
Nodes (11): CABLE_KINDS, CableDialog(), fmtSpeed(), IFACE_KINDS, InterfacesPanel(), useDevicePick(), CableKind, CableTraceHop (+3 more)

### Community 86 - "Racks"
Cohesion: 0.19
Nodes (15): Health rollup: worst status across linked IPs, Carrier (slot-layout device: shelves/trays), Elevation editor, Find free U, Health overlay, Linked asset and IP address, Rack placement rules, Printing and QR labels (+7 more)

### Community 87 - "schemas/device.py"
Cohesion: 0.21
Nodes (9): DeviceCreate, DeviceDetail, DeviceIpRef, DeviceOut, DeviceUpdate, BaseModel, field_validator, Device entity schemas — a host that may be racked and owns IPs. Placement… (+1 more)

### Community 88 - "workbook/__init__.py"
Cohesion: 0.24
Nodes (11): Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, _csv_sheet(), load_upload(), load_workbook_bytes(), XLSX/CSV -> sheet matrices (openpyxl read_only streams / csv module)., Drop fully-empty trailing rows/cols for a stable matrix shape., One CSV file -> one SheetMatrix named after the file stem. utf-8-sig first…, Dispatch on container type: ZIP -> xlsx workbook; otherwise try CSV text… (+3 more)

### Community 89 - "test_maintenance.py"
Cohesion: 0.21
Nodes (11): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_now_enqueues(), test_clear_discovery() (+3 more)

### Community 90 - "schemas/ip_range.py"
Cohesion: 0.24
Nodes (8): IPRangeRole, str, IPRangeCreate, IPRangeOut, IPRangeUpdate, BaseModel, field_validator, model_validator

### Community 91 - "classify_sheet"
Cohesion: 0.24
Nodes (6): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, TestClassify

### Community 92 - "test_changelog.py"
Cohesion: 0.23
Nodes (12): AsyncClient, tag_assignments.object_id has no FK — deleting a tagged object must drop its…, Tag.assignments is already ORM delete-orphan — each removed assignment lands in…, PATCH settings with a null value deletes the app_settings row — that delete…, /addresses/bulk action=delete used to issue one Core DELETE — invisible to the…, test_bulk_delete_writes_changelog_entries(), test_changelog_captures_ip_status_change(), test_changelog_records_crud() (+4 more)

### Community 93 - "Settings"
Cohesion: 0.26
Nodes (13): Accounts & Roles, Insecure mode (IPAMBOX_ALLOW_INSECURE), Four roles (Administrator, Operator, Contributor, Viewer), Session-cookie authentication, Certificates, Color rules, Five-stage scan pipeline, Scans (+5 more)

### Community 94 - "test_scan_cidr_tcp_fallback_reports_found"
Cohesion: 0.21
Nodes (8): on_hosts fires once per detection step with that chunk's new IPs — ARP batch…, When L2+L3 find nothing, the TCP fallback publishes its batch too., test_scan_cidr_emits_found_deltas(), fake_icmp(), fake_probe(), fake_ptr(), on_hosts(), test_scan_cidr_tcp_fallback_reports_found()

### Community 95 - "list_racks"
Cohesion: 0.27
Nodes (10): parse_enum_set(), parse_int_set(), parse_token_set(), _export_racks(), _filtered_racks(), list_racks(), _occupancy_class(), Rack (+2 more)

### Community 96 - "after_flush"
Cohesion: 0.27
Nodes (11): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), SyncSession, register(), _repr() (+3 more)

### Community 97 - "rule_matches"
Cohesion: 0.29
Nodes (11): _as_date(), _as_str(), display_color_for(), _ordered_cmp(), Any, date, -1/0/1 comparing a column value to a rule's value string. Tries date first when…, Does ``rule`` fire on this row? NULL fields never match. (+3 more)

### Community 98 - "test_prefix_api.py"
Cohesion: 0.33
Nodes (10): _global_vrf_id(), Splits are counted arithmetically before materializing: anything over…, test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_prefixes_order_by_utilization_and_limit(), test_same_cidr_allowed_across_vrfs(), test_split_cardinality_cap(), test_split_endpoint() (+2 more)

### Community 99 - "_FakePool"
Cohesion: 0.20
Nodes (8): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture, Stands in for the arq Redis pool — never actually dispatches work., scan_exclude_networks=10.70.0.64/26 inside scan_networks=10.70.0.0/24: the…, test_scheduler_and_route_share_exclusion_guard()

### Community 101 - "devDependencies"
Cohesion: 0.20
Nodes (10): devDependencies, autoprefixer, postcss, sharp, tailwindcss, @types/js-yaml, @types/node, @types/react (+2 more)

### Community 102 - "Inventory (asset register)"
Cohesion: 0.22
Nodes (10): Certificate expiry tracking, EOL & support-status tracking, import_batch_id provenance, Inventory (asset register), Custom Lists (user-defined tables), Hebrew-aware text handling, ip_addresses table (IPAM data store), ip column type (live IPAM resolution) (+2 more)

### Community 103 - "CSV export"
Cohesion: 0.22
Nodes (10): GET /api/v1/devices/export.csv, GET /api/v1/devices/export.xlsx, CSV export, Export dropdown (Devices toolbar), Filtered-set export parity (devices-filtered.*), Filter facets as URL params, Export column round-trip contract, UTF-8 BOM encoding (Excel/Hebrew-safe) (+2 more)

### Community 104 - "_device_out"
Cohesion: 0.25
Nodes (9): Rack, _rack_detail(), Rack -> RackDetail with its (selectin-loaded) devices serialized, each carrying…, _device_out(), IPAddress, Device -> the v1 rack-device payload. The single-IP fields now describe the…, interface_stats(), RackDetail (+1 more)

### Community 105 - "check-rack-library.mjs"
Cohesion: 0.25
Nodes (6): DIR, FACES, LAYOUTS, problems, referenced, slugs

### Community 106 - "RackFace"
Cohesion: 0.39
Nodes (7): Placed, LibraryDevice, RACK_LIBRARY, ImportDevice, PreviewRow, RackFace, SlotLayout

### Community 107 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, build:rack-library, check:rack-library, dev, lint, start

### Community 108 - "Devices"
Cohesion: 0.29
Nodes (7): API sketch, Device detail, Devices, Devices vs racks, From the IP drawer, Health rollup, The list

### Community 109 - "exclusion_hit"
Cohesion: 0.33
Nodes (5): _check_cidr_allowed(), exclusion_hit(), Scan-target policy shared by the API route, the scheduler, and the worker.…, Return the first excluded CIDR overlapping ``net`` (either direction), or None.…, test_exclusion_hit_both_directions()

### Community 111 - "api service (FastAPI/uvicorn backend)"
Cohesion: 0.67
Nodes (6): api service (FastAPI/uvicorn backend), db service (PostgreSQL 16), ipam bridge network (192.0.2.0/24), redis service (Redis 7, appendonly), scanner service (arq worker, host networking), web service (Next.js frontend)

### Community 112 - "Rack device image library"
Cohesion: 0.40
Nodes (5): CC0 1.0 Universal, netbox-community/devicetype-library, Rack device image library, Device image library, NetBox devicetype-library

### Community 113 - "shortcuts.ts"
Cohesion: 0.53
Nodes (5): moveRowNav(), G_CHORDS, isEditableTarget(), modalOpen(), useGlobalShortcuts()

### Community 114 - ".test_legacy_bezeq_layout"
Cohesion: 0.40
Nodes (3): קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., TestCircuitsParser

### Community 115 - "use-chart-theme.ts"
Cohesion: 0.50
Nodes (4): ChartTheme, FALLBACK, readTheme(), useChartTheme()

### Community 116 - "Security Policy"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

## Ambiguous Edges - Review These
- `Cable` → `Rack`  [AMBIGUOUS]
  frontend/src/content/docs/cabling.md · relation: conceptually_related_to

## Knowledge Gaps
- **354 isolated node(s):** `PrefixRow`, `Draft`, `AssetRow`, `RackRow`, `ServiceRow` (+349 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1232 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **59 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Cable` and `Rack`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `apply_bundle()` connect `apply_bundle` to `devices-client.tsx`, `device-detail-client.tsx`, `Device`, `parse_bundle`, `cables.py`, `rack_io.py`, `tags.py`, `v1/racks.py`, `backend/app/services/device_io.py`?**
  _High betweenness centrality (0.162) - this node is a cross-community bridge._
- **Why does `Site` connect `devices-client.tsx` to `prefixes-client.tsx`, `device-detail-client.tsx`, `index.ts`, `group-client.tsx`, `apply_bundle`, `rack_io.py`?**
  _High betweenness centrality (0.121) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `get_settings` to `prefixes.py`, `services/backup.py`, `test_racks.py`, `test_lists.py`, `ipam.py`, `scans.py`, `get_redis`, `test_devices.py`, `worker.py`, `User`, `backend/tests/test_rack_io.py`, `test_device_io.py`, `runtime_settings.py`, `v1/backup.py`, `redis.py`, `UserRole`, `test_colors.py`, `test_ordering.py`, `test_search.py`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **Are the 68 inferred relationships involving `IPAMError` (e.g. with `_check_interface_link()` and `create_address()`) actually correct?**
  _`IPAMError` has 68 INFERRED edges - model-reasoned connections that need verification._
- **Are the 37 inferred relationships involving `IPAddress` (e.g. with `_address_csv_row()` and `_addresses_stmt()`) actually correct?**
  _`IPAddress` has 37 INFERRED edges - model-reasoned connections that need verification._
- **What connects `PrefixRow`, `Draft`, `AssetRow` to the rest of the system?**
  _354 weakly-connected nodes found - possible documentation gaps or missing edges._