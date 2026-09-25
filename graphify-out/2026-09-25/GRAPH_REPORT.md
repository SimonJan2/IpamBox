# Graph Report - IpamBox  (2026-09-25)

## Corpus Check
- 416 files · ~1,005,874 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 21 file(s) not represented in the graph (top: (none) 7, .csv 6, .ini 2)

## Summary
- 4244 nodes · 14244 edges · 168 communities (118 shown, 17 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 1044 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c6c266b4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.ts
- list-client.tsx
- react
- get_or_404
- services/backup.py
- lucide-react
- rackula.ts
- cn
- ScanJob
- test_cabling.py
- rack-row.tsx
- import-client.tsx
- test_racks.py
- get_redis
- v1/settings.py
- cables.py
- generate_demo_data.py
- v1/devices.py
- lists.py
- color_rules.py
- clean
- _Planner
- schemas/certificate.py
- IPAddress
- rack_io.py
- imports.py
- listparse.py
- test_devices.py
- test_rack_io.py
- worker.py
- test_secrets.py
- v1/racks.py
- test_device_io.py
- route-error.tsx
- Rack
- IPRangeRole
- services/racks.py
- test_monitors.py
- Device
- IPAMError
- hex_color_or_none
- useAsyncData
- channels.py
- v1/search.py
- _split_dsn
- UserRole
- get_settings
- _matrix
- scanner.py
- test_scanner.py
- run_scan
- dependencies
- test_ipam_extras.py
- MonitorTarget
- package.json
- docs.ts
- User
- rack-detail-client.tsx
- backend/requirements.txt
- tree-client.tsx
- parse_site_sheet
- build-rack-library.mjs
- v1/monitors.py
- test_workbook_import.py
- _FakeRedis
- NotificationChannel
- rack-editor.tsx
- Excel workbook import
- maintenance.py
- schemas/color_rule.py
- test_prefix_api.py
- compilerOptions
- RackFace
- test_auth.py
- test_ip_source.py
- test_settings.py
- Racks
- Device (first-class host entity)
- IpamBox
- Smart import dialog
- demo_rack_dc.py
- app-shell.tsx
- Rack device image library
- network.py
- _mklist
- IP Addresses
- schemas/tag.py
- test_search.py
- api service (FastAPI/uvicorn backend)
- rack-elevation.tsx
- IP address
- reader.py
- parse_sites_master
- classify_sheet
- test_changelog.py
- schemas/circuit.py
- docs/[slug]/page.tsx
- check_target
- Settings
- schemas/asset.py
- devDependencies
- CSV export
- check-rack-library.mjs
- test_allocation.py
- scripts
- Devices
- test_entities.py
- shortcuts.ts
- Demo import data — ALL FICTIONAL
- Docs: IP Addresses
- Security Policy
- next-env.d.ts
- POST /api/v1/devices/import
- Racks REST API (GET /api/v1/racks)
- xff-shim.js
- IpamBox README
- Rack device image library bundle
- Inventory (asset register)
- RackFace
- schemas/service.py
- schemas/site.py
- _positional_columns
- .test_legacy_bezeq_layout
- use-chart-theme.ts
- _secrets_not_configured
- field_validator
- IpamBox App Icon (icon.svg)
- Root Layout (layout.tsx, title: IpamBox)
- GET /api/v1/devices/export.csv
- GET /api/v1/devices/export.xlsx
- ip_addresses table
- GET /api/v1/racks/export.csv
- GET /api/v1/racks/export.xlsx
- GET /api/v1/rack-groups/{id}/export.xlsx
- GET /api/v1/racks/{id}/export.xlsx

## God Nodes (most connected - your core abstractions)
1. `cn()` - 167 edges
2. `react` - 138 edges
3. `IPAMError` - 111 edges
4. `IPAddress` - 99 edges
5. `get_or_404()` - 88 edges
6. `Device` - 85 edges
7. `useAsyncData()` - 82 edges
8. `lucide-react` - 79 edges
9. `User` - 78 edges
10. `useAuth()` - 71 edges

## Surprising Connections (you probably didn't know these)
- `CSV export` --semantically_similar_to--> `Address CSV import/export (UTF-8 BOM)`  [INFERRED] [semantically similar]
  frontend/src/content/docs/devices.md → README.md
- `Export dropdown (Devices toolbar)` --semantically_similar_to--> `Device smart file I/O (export dropdown + smart import)`  [INFERRED] [semantically similar]
  frontend/src/content/docs/devices.md → README.md
- `Smart import dialog` --semantically_similar_to--> `Excel workbook import (per-sheet detection, dry-run, all-or-nothing/partial commit)`  [INFERRED] [semantically similar]
  frontend/src/content/docs/devices.md → README.md
- `Live IP column resolution` --semantically_similar_to--> `Discovery Inbox reconciliation`  [INFERRED] [semantically similar]
  frontend/src/content/docs/lists.md → README.md
- `Stats strip & saved views` --semantically_similar_to--> `Monitoring doc (V7)`  [AMBIGUOUS] [semantically similar]
  frontend/src/content/docs/inventory.md → frontend/src/content/docs/monitoring.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **IpamBox docker-compose service stack** — compose_db_service, compose_redis_service, compose_api_service, compose_scanner_service, compose_web_service [EXTRACTED 1.00]
- **Monitor sweep → transition → notify → log flow** — frontend_src_content_docs_monitoring_monitor_target, frontend_src_content_docs_monitoring_sweep_tick, frontend_src_content_docs_monitoring_state_machine, frontend_src_content_docs_monitoring_notification_channel, frontend_src_content_docs_monitoring_notification_log [INFERRED 0.85]
- **L1 cabling model** — frontend_src_content_docs_cabling_interface, frontend_src_content_docs_cabling_cable, frontend_src_content_docs_cabling_patch_panel, frontend_src_content_docs_cabling_l1_trace, frontend_src_content_docs_cabling_connected_interface [EXTRACTED 1.00]
- **Fictional demo import suite** — examples_workbook_demo, examples_workbook_demo_en, examples_demo_csvs, examples_vlan_scheme [EXTRACTED 1.00]
- **Consistency enforced by the database, not convention** — readme_gist_exclusion, readme_atomic_allocation, frontend_src_content_docs_subnets_pool_override, frontend_src_content_docs_subnets_gateway_dns [INFERRED 0.85]
- **Prefix utilization & allocation flow** — frontend_src_content_docs_subnets_prefix, frontend_src_content_docs_subnets_ip_range, frontend_src_content_docs_subnets_ip_address, frontend_src_content_docs_subnets_matrix, readme_atomic_allocation [INFERRED 0.85]

## Communities (168 total, 17 thin omitted)

### Community 0 - "index.ts"
Cohesion: 0.03
Nodes (109): ACTION_STYLES, MonitoringPage(), targetLink(), IP_ROLES, IP_STATUSES, RANGE_ROLES, SplitDialog(), SplitPlan (+101 more)

### Community 1 - "list-client.tsx"
Cohesion: 0.09
Nodes (58): EMPTY, ACTION_STYLES, EMPTY, AssetRow, EMPTY, cellLabel(), CHIP_COLORS, COL_TYPES (+50 more)

### Community 2 - "react"
Cohesion: 0.02
Nodes (42): nextConfig, metadata, metadata, metadata, metadata, metadata, metadata, metadata (+34 more)

### Community 3 - "get_or_404"
Cohesion: 0.04
Nodes (129): list_changelog(), AsyncSession, get, AsyncSession, get, stats(), reorder_devices(), _crud_router() (+121 more)

### Community 4 - "services/backup.py"
Cohesion: 0.07
Nodes (60): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), SyncSession, Audit trail via session flush hooks. before_flush collects (object, action,…, register() (+52 more)

### Community 5 - "lucide-react"
Cohesion: 0.08
Nodes (57): BulkResp, DragSession, DataPage(), download(), FeatureDef, GROUPS, Key, configSummary() (+49 more)

### Community 6 - "rackula.ts"
Cohesion: 0.09
Nodes (34): ABBREV_TO_CATEGORY, canonicalCategory(), CATEGORY_TO_ABBREV, clip(), compareVersions(), decodeShareUrl(), DeviceLike, deviceTypeTables() (+26 more)

### Community 7 - "cn"
Cohesion: 0.05
Nodes (109): DEVICE_VIEWS, DeviceRow, EMPTY, IMPORT_FIELDS, IMPORT_OPTIONS, TEXT_CHIP_LABELS, EMPTY_EDIT, FACE_BADGE (+101 more)

### Community 8 - "ScanJob"
Cohesion: 0.07
Nodes (46): cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession, get (+38 more)

### Community 9 - "test_cabling.py"
Cohesion: 0.13
Nodes (46): _backup_bytes(), _cable(), _device(), _gen(), _iface(), _ip(), _login(), _mkuser() (+38 more)

### Community 10 - "rack-row.tsx"
Cohesion: 0.18
Nodes (18): DashboardPage(), errDetail(), findDevice(), GroupClient(), moveDevice(), RackDetailPage(), RackUGrid(), freeByRack() (+10 more)

### Community 11 - "import-client.tsx"
Cohesion: 0.12
Nodes (17): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, PreviewResp, SheetResults(), Step (+9 more)

### Community 12 - "test_racks.py"
Cohesion: 0.09
Nodes (67): hash_password(), _carrier(), _dev(), _group(), _imports(), _mount(), _next_free(), AsyncClient (+59 more)

### Community 13 - "get_redis"
Cohesion: 0.07
Nodes (65): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+57 more)

### Community 14 - "v1/settings.py"
Cohesion: 0.13
Nodes (24): _build_out(), _lan_info(), _mask_url(), AsyncSession, get, Hide the password in a scheme://user:pass@host URL., LAN identity detected by the host-networked worker (written to Redis). Falls…, read_settings() (+16 more)

### Community 15 - "cables.py"
Cohesion: 0.07
Nodes (63): _cable_out(), _check_ends(), create_cable(), delete_cable(), _get_cable(), _get_interface(), interfaces_match_free_text(), list_cables() (+55 more)

### Community 16 - "generate_demo_data.py"
Cohesion: 0.09
Nodes (49): assets_rows(), _assign_site_sheets(), _assign_site_sheets_clean(), build_en_workbook(), build_mixed_workbook(), build_sites(), certificates_rows(), circuits_rows() (+41 more)

### Community 17 - "v1/devices.py"
Cohesion: 0.06
Nodes (69): _asset_ref(), _check_iface_refs(), _check_refs(), create_device(), create_interface(), delete_device(), delete_interface(), _detail() (+61 more)

### Community 18 - "lists.py"
Cohesion: 0.06
Nodes (57): bulk_rows(), _check_columns(), create_list(), create_row(), delete_list(), delete_row(), get_list(), list_lists() (+49 more)

### Community 19 - "color_rules.py"
Cohesion: 0.09
Nodes (37): create_rule(), delete_rule(), get_rule(), list_rules(), preview_rule(), AsyncSession, delete, get (+29 more)

### Community 20 - "clean"
Cohesion: 0.08
Nodes (41): assemble_ip(), clean(), _clean_octets(), map_status(), mask_to_prefixlen(), network_of(), norm_header(), parse_range_end() (+33 more)

### Community 21 - "_Planner"
Cohesion: 0.08
Nodes (18): _Planner, _preview(), (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Folded sheet title vs site name/code — word-boundary matching so 'int' doesn't…, Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new…, Resolve a 10.{second}.x sheet — site_number is only meaningful inside the… (+10 more)

### Community 22 - "schemas/certificate.py"
Cohesion: 0.27
Nodes (8): CertificateCreate, CertificateOut, CertificateUpdate, BaseModel, field_validator, DashboardStats, MacMismatchItem, BaseModel

### Community 23 - "IPAddress"
Cohesion: 0.05
Nodes (100): create_network(), AsyncSession, post, POST /networks — the "add network" wizard endpoint (V6.1). One call creates or…, allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes() (+92 more)

### Community 24 - "rack_io.py"
Cohesion: 0.05
Nodes (77): import_racks(), Request, Smart rack/group bundle import — V5B's stateless flow for whole trees. Sheets…, RackGroup, A bayed row: racks ordered left-to-right as they stand in the DC., Site, ip_display(), Any (+69 more)

### Community 25 - "imports.py"
Cohesion: 0.10
Nodes (38): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+30 more)

### Community 26 - "listparse.py"
Cohesion: 0.10
Nodes (23): ListTarget, Import a sheet as a custom list (user-selected or suggested)., _cell_text(), extract_list_table(), _infer_type(), _ips(), _is_ip_token(), pick_key_column() (+15 more)

### Community 27 - "test_devices.py"
Cohesion: 0.13
Nodes (39): _cable(), _device(), _group(), _iface(), _ip(), _login(), _mkuser(), _prefix() (+31 more)

### Community 28 - "test_rack_io.py"
Cohesion: 0.15
Nodes (44): auth_on(), _bundle(), _by_sheet(), _cable(), _csv(), _device(), _group(), _iface() (+36 more)

### Community 29 - "worker.py"
Cohesion: 0.08
Nodes (45): ArqRedis, close_arq_pool(), close_redis(), get_arq_pool(), Shut down the shared client — lifespan/worker shutdown only., Shared ARQ pool — callers must not close() it per job., redis_settings_from_url(), set_actor() (+37 more)

### Community 30 - "test_secrets.py"
Cohesion: 0.10
Nodes (34): _data_key(), decrypt_str(), encrypt_str(), _master_key(), Exception, Secrets at rest — the credential contract v7/v8/v12/v14 build on. A single…, Unseal a "v1:…" blob. Strict prefix check — unknown formats, malformed payloads…, Base for secrets-service failures — never carries secret material. (+26 more)

### Community 31 - "v1/racks.py"
Cohesion: 0.06
Nodes (75): _check_refs(), create_device(), create_rack(), delete_device(), delete_rack(), _device_out(), _devices(), _export_name() (+67 more)

### Community 32 - "test_device_io.py"
Cohesion: 0.18
Nodes (36): auth_on(), _csv(), _device(), _group(), _import(), _ip(), _login(), _mkuser() (+28 more)

### Community 34 - "Rack"
Cohesion: 0.13
Nodes (29): _check_site(), create_rack_group(), delete_rack_group(), export_rack_group_xlsx(), _get_group(), get_rack_group(), list_rack_groups(), _ordered_racks() (+21 more)

### Community 35 - "IPRangeRole"
Cohesion: 0.24
Nodes (8): IPRangeRole, str, IPRangeCreate, IPRangeOut, IPRangeUpdate, BaseModel, field_validator, model_validator

### Community 36 - "services/racks.py"
Cohesion: 0.10
Nodes (32): apply_device_import(), Write the ok rows in one transaction. Creates go through the create path's…, apply_device_patch(), carrier_children(), CarrierError, _check_carrier_mount(), check_layout_change(), check_placement() (+24 more)

### Community 37 - "test_monitors.py"
Cohesion: 0.07
Nodes (31): NotificationLog, Append-only delivery attempt log — swept by ``notify_retention_days``., _FakeArqPool, _Job, _login(), _mk_device(), _mk_prefix_and_addr(), _mkuser() (+23 more)

### Community 38 - "Device"
Cohesion: 0.09
Nodes (51): Device, _carrier_diff_name(), _err(), _find_carrier(), _int_field(), _ip_tokens(), _load_refs(), _match() (+43 more)

### Community 39 - "IPAMError"
Cohesion: 0.07
Nodes (62): _address_csv_row(), _addresses_stmt(), bulk_addresses(), BulkBody, _check_interface_link(), create_address(), delete_address(), export_addresses() (+54 more)

### Community 40 - "hex_color_or_none"
Cohesion: 0.31
Nodes (4): hex_color_or_none(), Shared row/tag color validator: #rrggbb, normalized to lowercase., field_validator, field_validator

### Community 41 - "useAsyncData"
Cohesion: 0.07
Nodes (86): CertificatesPage(), ChangelogPage(), CircuitsPage(), DevicesPage(), DeviceDetailClient(), DiscoveryPage(), ImportPage(), InventoryPage() (+78 more)

### Community 42 - "channels.py"
Cohesion: 0.11
Nodes (37): _config_fields(), create_channel(), delete_channel(), _get(), get_channel(), list_channels(), notification_log(), _out() (+29 more)

### Community 43 - "v1/search.py"
Cohesion: 0.17
Nodes (27): _folded(), AsyncSession, get, Cross-object search for the command palette. One GET returns grouped matches…, Column expression with Hebrew final letters folded — pairs with fold_hebrew()…, Short label for a list-row search hit: key-column value, else the first non-…, _row_label(), search() (+19 more)

### Community 44 - "_split_dsn"
Cohesion: 0.11
Nodes (26): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., _split_dsn() (+18 more)

### Community 45 - "UserRole"
Cohesion: 0.05
Nodes (103): str, UserRole, _backup_bytes(), _envelope_bytes(), _mkusers(), Hand-craft a backup envelope (e.g. with a forged users table)., Guard: every ORM table must be backed up (or explicitly excluded). Adding a new…, Fresh-server scenario: the migration-seeded Global VRF is replaced by the… (+95 more)

### Community 46 - "get_settings"
Cohesion: 0.06
Nodes (36): do_run_migrations(), run_migrations_online(), get_settings(), psycopg2-style URL for alembic offline mode / scripts., Settings, Effective, _env_sourced(), Any (+28 more)

### Community 47 - "_matrix"
Cohesion: 0.21
Nodes (13): _master_row(), _matrix(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind… (+5 more)

### Community 48 - "scanner.py"
Cohesion: 0.08
Nodes (28): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), _host_chunks(), _icmp_sweep(), infer_device_type(), _ptr_lookup() (+20 more)

### Community 49 - "test_scanner.py"
Cohesion: 0.06
Nodes (57): _flag(), Any, AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), HostResult, _global_vrf_id(), _infer_scan_vrf() (+49 more)

### Community 50 - "run_scan"
Cohesion: 0.09
Nodes (28): Exception, Raised inside the pipeline when the user cancels the scan., ScanCancelled, _job_status(), _publish(), Re-read the job row's status — the session's `job` instance goes stale the…, ARQ job: execute a scan and reconcile results., run_scan() (+20 more)

### Community 51 - "dependencies"
Cohesion: 0.07
Nodes (29): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, js-yaml, jszip, lucide-react (+21 more)

### Community 52 - "test_ipam_extras.py"
Cohesion: 0.16
Nodes (26): _prefix(), _range(), export.csv takes the same filters as the list endpoint — a filtered view…, Same filtered-export treatment on the prefixes CSV (F8)., A documented v6 /64's 2^64 host count must not reach dashboard sums (~1.8e19 >…, A deliberate bulk import documents existing reality — statics inside pools land…, test_address_role_nat_and_bulk(), test_addresses_export_respects_filters() (+18 more)

### Community 53 - "MonitorTarget"
Cohesion: 0.11
Nodes (26): MonitorKind, MonitorState, MonitorTarget, str, V7 — continuous monitoring targets + outbound notification channels., One monitored endpoint — resolves to a concrete IP at check time.…, MonitorTargetOut, apply_result() (+18 more)

### Community 54 - "package.json"
Cohesion: 0.07
Nodes (25): name, private, version, autoprefixer, clsx, postcss, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+17 more)

### Community 55 - "docs.ts"
Cohesion: 0.19
Nodes (11): DocsIndexClient(), metadata, DocsNav(), BY_SLUG, DOC_ARTICLES, DOC_CATEGORIES, DocArticle, DocCategory (+3 more)

### Community 56 - "User"
Cohesion: 0.05
Nodes (65): delete_scheduled_backup(), download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, delete, get, post (+57 more)

### Community 57 - "rack-detail-client.tsx"
Cohesion: 0.12
Nodes (19): LabelClient(), metadata, metadata, FACE_BADGE, PrintClient(), FACE_BADGE, ExpiryBadge(), RackQrCode() (+11 more)

### Community 58 - "backend/requirements.txt"
Cohesion: 0.14
Nodes (23): alembic==1.14.0, arq==0.26.1, asyncpg==0.30.0, bcrypt==4.3.0, cryptography==50.0.1, fastapi==0.115.6, httpx==0.28.1, openpyxl==3.1.5 (+15 more)

### Community 59 - "tree-client.tsx"
Cohesion: 0.12
Nodes (25): metadata, ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), Breadcrumbs(), Crumb (+17 more)

### Community 60 - "parse_site_sheet"
Cohesion: 0.17
Nodes (8): _blocks(), parse_site_sheet(), Split duplicated column groups (031-style runaway): each block starts at an…, MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf., Bare 'Name' (Cellular) maps to the hostname field., Non-empty unnamed columns pile into cf['extra'] instead of vanishing (Pelephone…, TestSiteSheetExtras, TestSiteSheetParser

### Community 61 - "build-rack-library.mjs"
Cohesion: 0.13
Nodes (23): arrLen(), attribution(), CATEGORY_COLOUR, CURATED, fetchBuf(), fetchJson(), FRONTEND, FULL_IMPORT (+15 more)

### Community 62 - "v1/monitors.py"
Cohesion: 0.16
Nodes (24): check_now(), _check_refs(), create_target(), delete_target(), _filters(), _get(), get_target(), list_targets() (+16 more)

### Community 63 - "test_workbook_import.py"
Cohesion: 0.08
Nodes (15): parse_certificates(), Positional 5-col layout: platform, target/VS, server, cert, expiry., Workbook import: normalizer/parser unit tests (no DB) + API e2e., Small synthetic workbook: sites master + one site sheet + circuits., Site sheet documenting a DHCP span AND static stations inside it — the real…, Pool-guard regression: committing a plan whose dhcp range covers documented…, test_commit_twice_rejected(), test_import_e2e() (+7 more)

### Community 64 - "_FakeRedis"
Cohesion: 0.09
Nodes (15): _FakeRedis, check-now drives the same state machine the sweep does; failures accrue until…, Observed churn (state/failures/last_*) must not touch the audit log., _cert_warnings emits cert.expiring once per cert per day — the Redis day-stamp…, A scan that raises mid-job flips to FAILED and emits scan.failed., reconcile raising a mac_mismatch flag emits once; a follow-up scan that leaves…, In-memory get/set/publish stand-in for the worker's redis client., test_cert_warning_emits_once_per_day() (+7 more)

### Community 65 - "NotificationChannel"
Cohesion: 0.14
Nodes (22): NotificationChannel, Outbound sink. ``config`` holds non-secret fields per kind; ``secret_enc`` is…, _deliver(), _DeliveryFailed, emit(), _log(), _post_json(), Any (+14 more)

### Community 66 - "rack-editor.tsx"
Cohesion: 0.17
Nodes (20): DeviceFormDialog(), DragSession, DropRow(), EditorBlock(), errDetail(), Pending, RackEditor(), CarrierFrameSvg() (+12 more)

### Community 67 - "Excel workbook import"
Cohesion: 0.17
Nodes (19): Demo CSV files, Fictional demo dataset, Demo import data README, Demo VLAN scheme, Network_Address_DEMO.xlsx, Network_Address_DEMO_EN.xlsx, backend/app/services/workbook parser, Asset (SW/HW inventory) (+11 more)

### Community 68 - "maintenance.py"
Cohesion: 0.11
Nodes (33): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+25 more)

### Community 69 - "schemas/color_rule.py"
Cohesion: 0.19
Nodes (9): ColorRuleCreate, ColorRuleOut, ColorRuleUpdate, BaseModel, field_validator, model_validator, POST /color-rules/reorder: rule ids of ONE entity_type in new order., RulePreviewOut (+1 more)

### Community 70 - "test_prefix_api.py"
Cohesion: 0.22
Nodes (18): _addrs(), _global_vrf_id(), _mkprefix(), Splits are counted arithmetically before materializing: anything over…, test_gateway_clear_removes_only_pristine_row(), test_gateway_never_clobbers_manual_row(), test_gateway_validation(), test_next_ip_never_hands_out_gateway() (+10 more)

### Community 71 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 72 - "RackFace"
Cohesion: 0.11
Nodes (12): First-class device: a host that exists independently of any rack. A Device owns…, str, RackFace, DeviceCreate, DeviceDetail, DeviceOut, DeviceUpdate, BaseModel (+4 more)

### Community 73 - "test_auth.py"
Cohesion: 0.21
Nodes (14): auth_on(), AsyncClient, fixture, Turn auth on for a test, restore insecure mode after, and flush session/lockout…, When the socket peer isn't in ipambox_trusted_proxies, a supplied XFF is…, Spreading failures across many usernames from one IP trips the aggregate lock —…, Five bad logins for one (user, ip) pair must not lock out other users on the…, test_endpoints_require_auth() (+6 more)

### Community 74 - "test_ip_source.py"
Cohesion: 0.24
Nodes (16): may_write(), Field-ownership check for source-stamped rows (ip_addresses et al.). True when…, _mk_prefix(), V6 provenance — ip_addresses.source: stamping, ownership, filtering. Every…, Manual and imported rows keep their provenance when a scan sees them — observed…, Response bodies carry `source` but never any *_enc-style field., test_csv_import_stamps_import(), test_export_filters_and_carries_source() (+8 more)

### Community 75 - "test_settings.py"
Cohesion: 0.17
Nodes (15): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, Every new Settings > Features key is runtime-editable; untouched keys keep the…, test_backup_files_report_effective_schedule() (+7 more)

### Community 76 - "Racks"
Cohesion: 0.21
Nodes (12): netbox-community/devicetype-library, Device image library, Elevation editor, Find free U, Health overlay, Linked asset and IP address, NetBox devicetype-library, Rack placement rules (+4 more)

### Community 77 - "Device (first-class host entity)"
Cohesion: 0.16
Nodes (23): IPAddress, Cable, connected_interface_id (structured far-end port link), connected_ip (host-side NIC binding), DeviceInterface (device-owned port), L1 trace (cable path walk), match-free-text transition endpoint, One-cable-per-interface rule (+15 more)

### Community 78 - "IpamBox"
Cohesion: 0.32
Nodes (20): Circuits (WAN circuit register), Hierarchy Tree, Roll-up utilization, Site → VRF → Prefix → IP address data model, IpamBox, Row Colors, Command palette, Services (service catalog) (+12 more)

### Community 79 - "Smart import dialog"
Cohesion: 0.17
Nodes (16): POST /api/v1/devices/import, Carrier two-pass mounting, Changelog / audit history, Dry-run preview with per-row {field:[old,new]} diffs, force commit mode (valid rows only), Header auto-mapping (English/Hebrew/NetBox), Match precedence: id → serial_number → mac_address → name+site, NetBox header aliases (device_role→device type, device_type→model, position→U) (+8 more)

### Community 80 - "demo_rack_dc.py"
Cohesion: 0.11
Nodes (25): Api, apply(), _device_payload(), emit_zip(), find_one(), _KeepMethodRedirect, layout_doc(), main() (+17 more)

### Community 81 - "app-shell.tsx"
Cohesion: 0.06
Nodes (40): metadata, viewport, AppearancePage(), AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS (+32 more)

### Community 82 - "Rack device image library"
Cohesion: 0.22
Nodes (12): Demo .Rackula.zip racks, Air-gap safe bundling, CC0 1.0 Universal license, CC0 1.0 Universal, netbox-community/devicetype-library, Rack library ATTRIBUTION, Rack device image library, IpamBox (+4 more)

### Community 83 - "network.py"
Cohesion: 0.20
Nodes (10): _ip(), NetworkCreate, NetworkDhcpRange, NetworkOut, NetworkPrefix, NetworkVlanNew, BaseModel, field_validator (+2 more)

### Community 84 - "_mklist"
Cohesion: 0.18
Nodes (4): _mklist(), TestBulkRows, TestListCRUD, TestRows

### Community 85 - "IP Addresses"
Cohesion: 0.29
Nodes (14): Address roles (vip/vrrp/hsrp/glbp/carp/secondary), Address CSV import/export, IP Addresses, IP drawer, mac_mismatch flag, Changelog, Per-object history, Discovery Inbox (+6 more)

### Community 86 - "schemas/tag.py"
Cohesion: 0.27
Nodes (7): AssignBody, BaseModel, field_validator, TagAssignmentOut, TagCreate, TagOut, TagUpdate

### Community 87 - "test_search.py"
Cohesion: 0.25
Nodes (14): auth_on(), AsyncClient, fixture, Global /api/v1/search endpoint (UX-3)., Regression: list_addresses ?q= used to crash on a missing column., Site + VRF + prefix + address + one of each workbook entity., _seed(), test_addresses_q_filter_not_broken() (+6 more)

### Community 88 - "api service (FastAPI/uvicorn backend)"
Cohesion: 0.43
Nodes (8): api service (FastAPI/uvicorn backend), db service (PostgreSQL 16), ipam bridge network (192.0.2.0/24), redis service (Redis 7, appendonly), scanner service (arq worker, host networking), web service (Next.js frontend), ip_addresses table (IPAM data store), ip column type (live IPAM resolution)

### Community 89 - "rack-elevation.tsx"
Cohesion: 0.32
Nodes (11): deviceImage(), FACE_BADGE, HEALTH_KEY, RackElevation(), RackGeom, usedUSlots(), useLibraryBySlug(), RackRowColumn() (+3 more)

### Community 90 - "IP address"
Cohesion: 0.42
Nodes (11): Add network wizard, Subnets doc, Gateway/DNS technical addresses, IP address, IP range (dhcp/pool/reserved), Subnet matrix, Pool override (force=1), Prefix (subnet) (+3 more)

### Community 91 - "reader.py"
Cohesion: 0.26
Nodes (9): Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, _csv_sheet(), load_workbook_bytes(), XLSX/CSV -> sheet matrices (openpyxl read_only streams / csv module)., Drop fully-empty trailing rows/cols for a stable matrix shape., One CSV file -> one SheetMatrix named after the file stem. utf-8-sig first…, Parse workbook bytes into per-sheet row matrices. read_only + data_only:…, SheetMatrix (+1 more)

### Community 92 - "parse_sites_master"
Cohesion: 0.17
Nodes (9): _master_blocks(), parse_sites_master(), (first, second) octet pairs a master row declares — lets sheet->site matching…, parse_sites_master_records(), Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins. (+1 more)

### Community 93 - "classify_sheet"
Cohesion: 0.24
Nodes (6): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, TestClassify

### Community 94 - "test_changelog.py"
Cohesion: 0.23
Nodes (12): AsyncClient, tag_assignments.object_id has no FK — deleting a tagged object must drop its…, Tag.assignments is already ORM delete-orphan — each removed assignment lands in…, PATCH settings with a null value deletes the app_settings row — that delete…, /addresses/bulk action=delete used to issue one Core DELETE — invisible to the…, test_bulk_delete_writes_changelog_entries(), test_changelog_captures_ip_status_change(), test_changelog_records_crud() (+4 more)

### Community 95 - "schemas/circuit.py"
Cohesion: 0.33
Nodes (5): CircuitCreate, CircuitOut, CircuitUpdate, BaseModel, field_validator

### Community 96 - "docs/[slug]/page.tsx"
Cohesion: 0.20
Nodes (11): DocPage(), dynamicParams, generateMetadata(), loadMarkdown(), CommandPalette(), itemsFor(), DocsContent(), docCategoryLabel() (+3 more)

### Community 97 - "check_target"
Cohesion: 0.24
Nodes (10): parse_http_expect(), (ok, error) for an HTTP response against the expectation grammar., check_target(), _http(), _ping(), AsyncClient, Semaphore, Run one check -> (ok, error). `client` lets the sweep share one AsyncClient… (+2 more)

### Community 98 - "Settings"
Cohesion: 0.31
Nodes (10): Accounts & Roles, Insecure mode (IPAMBOX_ALLOW_INSECURE), Four roles (Administrator, Operator, Contributor, Viewer), Session-cookie authentication, Certificates, Color rules, Scan targeting policy, Backup & Restore (+2 more)

### Community 99 - "schemas/asset.py"
Cohesion: 0.36
Nodes (7): AssetKind, str, AssetCreate, AssetOut, AssetUpdate, BaseModel, field_validator

### Community 100 - "devDependencies"
Cohesion: 0.20
Nodes (10): devDependencies, autoprefixer, postcss, sharp, tailwindcss, @types/js-yaml, @types/node, @types/react (+2 more)

### Community 101 - "CSV export"
Cohesion: 0.22
Nodes (10): GET /api/v1/devices/export.csv, GET /api/v1/devices/export.xlsx, CSV export, Export dropdown (Devices toolbar), Filtered-set export parity (devices-filtered.*), Filter facets as URL params, Export column round-trip contract, UTF-8 BOM encoding (Excel/Hebrew-safe) (+2 more)

### Community 102 - "check-rack-library.mjs"
Cohesion: 0.25
Nodes (6): DIR, FACES, LAYOUTS, problems, referenced, slugs

### Community 103 - "test_allocation.py"
Cohesion: 0.23
Nodes (12): sf(), _mk_prefix(), test_address_crud_and_dup_guard(), test_allocation_skips_existing(), test_concurrent_allocation_unique(), alloc(), test_exhausted_prefix_conflicts(), test_sequential_allocation_skips_boundaries() (+4 more)

### Community 104 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, build:rack-library, check:rack-library, dev, lint, start

### Community 105 - "Devices"
Cohesion: 0.29
Nodes (7): API sketch, Device detail, Devices, Devices vs racks, From the IP drawer, Health rollup, The list

### Community 107 - "shortcuts.ts"
Cohesion: 0.53
Nodes (5): moveRowNav(), G_CHORDS, isEditableTarget(), modalOpen(), useGlobalShortcuts()

### Community 108 - "Demo import data — ALL FICTIONAL"
Cohesion: 0.22
Nodes (9): Demo import data — ALL FICTIONAL, demo_rack_dc.py (emit | apply), /devices/import endpoint, Examples README (demo import data), Files, `Network_Address_DEMO_EN.xlsx` — the edge-case workbook, `Network_Address_DEMO.xlsx` — the clean flagship, Regenerating (+1 more)

### Community 109 - "Docs: IP Addresses"
Cohesion: 0.40
Nodes (5): Docs: IP Addresses, Docs: Devices, Docs: Racks, Docs: Settings, Docs: Subnets

### Community 110 - "Security Policy"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 141 - "IpamBox README"
Cohesion: 0.15
Nodes (27): Changelog bypass for state writes, Check kinds (ping/tcp/http), Monitoring doc (V7), Event sources, Deliberate limits, Monitor target, Notification channel, Notification log (+19 more)

### Community 144 - "Inventory (asset register)"
Cohesion: 0.29
Nodes (8): Certificate expiry tracking, EOL & support-status tracking, import_batch_id provenance, Inventory (asset register), Custom Lists (user-defined tables), Hebrew-aware text handling, Key-column merge identity on re-import, Positional column keys (c0, c1, …)

### Community 145 - "RackFace"
Cohesion: 0.39
Nodes (7): Placed, LibraryDevice, RACK_LIBRARY, ImportDevice, PreviewRow, RackFace, SlotLayout

### Community 146 - "schemas/service.py"
Cohesion: 0.38
Nodes (5): BaseModel, field_validator, ServiceCreate, ServiceOut, ServiceUpdate

### Community 147 - "schemas/site.py"
Cohesion: 0.38
Nodes (5): BaseModel, field_validator, SiteCreate, SiteOut, SiteUpdate

### Community 148 - "_positional_columns"
Cohesion: 0.29
Nodes (4): _col_class(), _positional_columns(), Dominant content class of a column sample., Headerless sheet: locate the IP column, then assign the remaining canonical…

### Community 149 - ".test_legacy_bezeq_layout"
Cohesion: 0.40
Nodes (3): קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., TestCircuitsParser

### Community 150 - "use-chart-theme.ts"
Cohesion: 0.50
Nodes (4): ChartTheme, FALLBACK, readTheme(), useChartTheme()

### Community 153 - "_secrets_not_configured"
Cohesion: 0.50
Nodes (4): Request, _secrets_not_configured(), exception_handler, JSONResponse

## Ambiguous Edges - Review These
- `Cable` → `Rack`  [AMBIGUOUS]
  frontend/src/content/docs/cabling.md · relation: conceptually_related_to
- `Stats strip & saved views` → `Monitoring doc (V7)`  [AMBIGUOUS]
  frontend/src/content/docs/inventory.md · relation: semantically_similar_to

## Knowledge Gaps
- **364 isolated node(s):** `nextConfig`, `name`, `version`, `private`, `dev` (+359 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1387 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Cable` and `Rack`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Stats strip & saved views` and `Monitoring doc (V7)`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._
- **Why does `IPAddress` connect `IPAddress` to `get_or_404`, `services/backup.py`, `ScanJob`, `test_racks.py`, `cables.py`, `v1/devices.py`, `lists.py`, `rack_io.py`, `test_devices.py`, `worker.py`, `v1/racks.py`, `Device`, `IPAMError`, `v1/search.py`, `test_scanner.py`, `run_scan`, `MonitorTarget`, `v1/monitors.py`, `maintenance.py`, `_mklist`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Why does `hex_color_or_none()` connect `hex_color_or_none` to `schemas/asset.py`, `get_or_404`, `schemas/color_rule.py`, `IPAMError`, `RackFace`, `lists.py`, `schemas/service.py`, `schemas/site.py`, `schemas/certificate.py`, `schemas/tag.py`, `field_validator`, `v1/racks.py`, `schemas/circuit.py`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `get_settings` to `get_or_404`, `services/backup.py`, `ScanJob`, `test_cabling.py`, `test_racks.py`, `get_redis`, `v1/settings.py`, `lists.py`, `IPAddress`, `imports.py`, `test_devices.py`, `test_rack_io.py`, `worker.py`, `test_secrets.py`, `test_device_io.py`, `test_monitors.py`, `UserRole`, `User`, `test_auth.py`, `test_search.py`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Are the 81 inferred relationships involving `IPAMError` (e.g. with `bulk_addresses()` and `_check_interface_link()`) actually correct?**
  _`IPAMError` has 81 INFERRED edges - model-reasoned connections that need verification._
- **Are the 48 inferred relationships involving `IPAddress` (e.g. with `_address_csv_row()` and `_addresses_stmt()`) actually correct?**
  _`IPAddress` has 48 INFERRED edges - model-reasoned connections that need verification._