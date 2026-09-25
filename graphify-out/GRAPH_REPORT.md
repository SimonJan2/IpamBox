# Graph Report - IpamBox  (2026-09-25)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 4412 nodes · 14251 edges · 192 communities (132 shown, 26 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 1099 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `212b7cf4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- IPAddress
- react
- devices-client.tsx
- IPAMError
- v1/racks.py
- index.ts
- prefixes-client.tsx
- lucide-react
- cn
- v1/devices.py
- cables.py
- rack_io.py
- import-client.tsx
- v1/auth.py
- test_racks.py
- Base
- IpamBox
- generate_demo_data.py
- lists.py
- color_rules.py
- device_io.py
- addresses.py
- get_redis
- imports.py
- test_monitors.py
- worker.py
- test_cabling.py
- hex_color_or_none
- device-filter-panel.tsx
- v1/monitors.py
- test_rack_io.py
- get_settings
- deps.py
- scans.py
- Device
- test_secrets.py
- route-error.tsx
- test_device_io.py
- test_devices.py
- test_review.py
- rackula.ts
- NotificationChannel
- services/review.py
- User
- scanner.py
- test_scanner.py
- _split_dsn
- _matrix
- v1/search.py
- clean
- ChannelKind
- _Planner
- HostResult
- test_ipam_extras.py
- rack-editor.tsx
- v1/review.py
- dependencies
- package.json
- ChangeLog
- v1/settings.py
- backend/requirements.txt
- group-client.tsx
- Smart import dialog
- _FakeRedis
- quick-scan.tsx
- build-rack-library.mjs
- tree-client.tsx
- maintenance.py
- hash_password
- UserRole
- test_colors.py
- demo_rack_dc.py
- v1/backup.py
- parse_site_sheet
- _FakeRedis
- test_ordering.py
- channels.py
- services/backup.py
- test_workbook_import.py
- IpamBox README
- parsers.py
- Excel workbook import
- RackFace
- extract_list_table
- test_prefix_api.py
- Device (first-class host entity)
- Monitoring doc (V7)
- compilerOptions
- docs.ts
- restore_backup
- schemas/import_batch.py
- network.py
- test_ip_source.py
- load_upload
- _mklist
- .resolve_sheet_site
- test_search.py
- smart-import-dialog.tsx
- parse_sites_master
- test_lists.py
- test_maintenance.py
- test_changelog.py
- Racks
- core/changelog.py
- worker/monitors.py
- test_scan_cidr_tcp_fallback_reports_found
- Rack device image library
- docs/[slug]/page.tsx
- _FakePool
- command-palette.tsx
- TestNormalize
- devDependencies
- Cable
- RackFace
- CircuitUpdate
- .add_list_sheet
- rack-collision.ts
- v1/dashboard.py
- readyz
- ReviewDismissal
- common.py
- classify.py
- parse_circuits
- test_allocation.py
- check-rack-library.mjs
- BackupError
- scripts
- Devices
- _mkuser
- test_entities.py
- fake_arq
- Docs: IP Addresses
- use-chart-theme.ts
- Security Policy
- after_flush
- test_health_ranking_unit
- next-env.d.ts
- POST /api/v1/devices/import
- Racks REST API (GET /api/v1/racks)
- xff-shim.js
- Rack device image library bundle
- Request
- SyncSession
- str
- model_validator
- Path
- CustomList
- Prefix
- ScanJob
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
1. `cn()` - 170 edges
2. `react` - 140 edges
3. `IPAMError` - 99 edges
4. `get_or_404()` - 86 edges
5. `useAsyncData()` - 84 edges
6. `lucide-react` - 80 edges
7. `IPAddress` - 75 edges
8. `Device` - 74 edges
9. `useAuth()` - 73 edges
10. `User` - 69 edges

## Surprising Connections (you probably didn't know these)
- `CSV export` --semantically_similar_to--> `Address CSV import/export (UTF-8 BOM)`  [INFERRED] [semantically similar]
  frontend/src/content/docs/devices.md → README.md
- `Smart import dialog` --semantically_similar_to--> `Excel workbook import (per-sheet detection, dry-run, all-or-nothing/partial commit)`  [INFERRED] [semantically similar]
  frontend/src/content/docs/devices.md → README.md
- `Stats strip & saved views` --semantically_similar_to--> `Monitoring doc (V7)`  [AMBIGUOUS] [semantically similar]
  frontend/src/content/docs/inventory.md → frontend/src/content/docs/monitoring.md
- `Live IP column resolution` --semantically_similar_to--> `Discovery Inbox reconciliation`  [INFERRED] [semantically similar]
  frontend/src/content/docs/lists.md → README.md
- `Export dropdown (Devices toolbar)` --semantically_similar_to--> `Device smart file I/O (export dropdown + smart import)`  [INFERRED] [semantically similar]
  frontend/src/content/docs/devices.md → README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Fictional demo import suite** — examples_workbook_demo, examples_workbook_demo_en, examples_demo_csvs, examples_vlan_scheme [EXTRACTED 1.00]
- **IpamBox docker-compose service stack** — compose_db_service, compose_redis_service, compose_api_service, compose_scanner_service, compose_web_service [EXTRACTED 1.00]
- **L1 cabling model** — frontend_src_content_docs_cabling_interface, frontend_src_content_docs_cabling_cable, frontend_src_content_docs_cabling_patch_panel, frontend_src_content_docs_cabling_l1_trace, frontend_src_content_docs_cabling_connected_interface [EXTRACTED 1.00]
- **Consistency enforced by the database, not convention** — readme_gist_exclusion, readme_atomic_allocation, frontend_src_content_docs_subnets_pool_override, frontend_src_content_docs_subnets_gateway_dns [INFERRED 0.85]
- **Monitor sweep → transition → notify → log flow** — frontend_src_content_docs_monitoring_monitor_target, frontend_src_content_docs_monitoring_sweep_tick, frontend_src_content_docs_monitoring_state_machine, frontend_src_content_docs_monitoring_notification_channel, frontend_src_content_docs_monitoring_notification_log [INFERRED 0.85]
- **Prefix utilization & allocation flow** — frontend_src_content_docs_subnets_prefix, frontend_src_content_docs_subnets_ip_range, frontend_src_content_docs_subnets_ip_address, frontend_src_content_docs_subnets_matrix, readme_atomic_allocation [INFERRED 0.85]

## Communities (192 total, 26 thin omitted)

### Community 0 - "IPAddress"
Cohesion: 0.05
Nodes (109): create_network(), AsyncSession, post, POST /networks — the "add network" wizard endpoint (V6.1). One call creates or…, allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes() (+101 more)

### Community 1 - "react"
Cohesion: 0.02
Nodes (47): nextConfig, metadata, metadata, DashboardPage(), metadata, DiscoveryPage(), metadata, metadata (+39 more)

### Community 2 - "devices-client.tsx"
Cohesion: 0.10
Nodes (85): CertificatesPage(), EMPTY, CircuitsPage(), EMPTY, DEVICE_VIEWS, DeviceRow, DevicesPage(), EMPTY (+77 more)

### Community 3 - "IPAMError"
Cohesion: 0.05
Nodes (94): _crud_router(), create_item(), delete_item(), get_item(), list_items(), reorder_items(), update_item(), _check_site() (+86 more)

### Community 4 - "v1/racks.py"
Cohesion: 0.05
Nodes (95): delete_rack_group(), export_rack_group_xlsx(), _get_group(), get_rack_group(), list_rack_groups(), _ordered_racks(), AsyncSession, delete (+87 more)

### Community 5 - "index.ts"
Cohesion: 0.03
Nodes (95): metadata, viewport, AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS, NavGroup (+87 more)

### Community 6 - "prefixes-client.tsx"
Cohesion: 0.07
Nodes (70): DeviceDetailClient(), EMPTY_EDIT, FACE_BADGE, metadata, UploadResp, ImportListDialog(), IPAM_FAMILIES, PreviewResp (+62 more)

### Community 7 - "lucide-react"
Cohesion: 0.09
Nodes (56): ACTION_STYLES, BulkResp, DELETE_PATH, DeleteTarget, DismissTarget, SECTION_ICONS, BackupSettingsPage(), downloadUrl() (+48 more)

### Community 8 - "cn"
Cohesion: 0.06
Nodes (68): IpCell(), SortableColRow(), IP_ROLES, IP_STATUSES, RANGE_ROLES, SplitDialog(), SplitPlan, entityHref() (+60 more)

### Community 9 - "v1/devices.py"
Cohesion: 0.05
Nodes (76): _asset_ref(), _check_iface_refs(), _check_refs(), create_device(), create_interface(), delete_device(), delete_interface(), _detail() (+68 more)

### Community 10 - "cables.py"
Cohesion: 0.06
Nodes (70): _cable_out(), _check_ends(), create_cable(), delete_cable(), _get_cable(), _get_interface(), interfaces_match_free_text(), list_cables() (+62 more)

### Community 11 - "rack_io.py"
Cohesion: 0.05
Nodes (69): import_racks(), Request, Smart rack/group bundle import — V5B's stateless flow for whole trees. Sheets…, RackGroup, A bayed row: racks ordered left-to-right as they stand in the DC., _alias_to_field(), apply_mapping_overrides(), auto_map_fields() (+61 more)

### Community 12 - "import-client.tsx"
Cohesion: 0.04
Nodes (54): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, SheetResults() (+46 more)

### Community 13 - "v1/auth.py"
Cohesion: 0.07
Nodes (64): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+56 more)

### Community 14 - "test_racks.py"
Cohesion: 0.10
Nodes (60): _carrier(), _dev(), _group(), _imports(), _mount(), _next_free(), AsyncClient, _rack() (+52 more)

### Community 15 - "Base"
Cohesion: 0.08
Nodes (31): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, metrics(), Prometheus-style text exposition of object + scan counters., AssetKind, str, Base, Certificate, Certificate-expiry row from the תוקף תעודות sheet. (+23 more)

### Community 16 - "IpamBox"
Cohesion: 0.09
Nodes (60): api service (FastAPI/uvicorn backend), db service (PostgreSQL 16), ipam bridge network (192.0.2.0/24), redis service (Redis 7, appendonly), scanner service (arq worker, host networking), web service (Next.js frontend), Accounts & Roles, Insecure mode (IPAMBOX_ALLOW_INSECURE) (+52 more)

### Community 17 - "generate_demo_data.py"
Cohesion: 0.07
Nodes (58): assets_rows(), _assign_site_sheets(), _assign_site_sheets_clean(), build_en_workbook(), build_mixed_workbook(), build_sites(), certificates_rows(), circuits_rows() (+50 more)

### Community 18 - "lists.py"
Cohesion: 0.08
Nodes (52): _devices_stmt(), The V5A filter vocabulary -> a Device select. Shared by the list endpoint and…, bulk_rows(), _check_columns(), create_list(), create_row(), delete_list(), delete_row() (+44 more)

### Community 19 - "color_rules.py"
Cohesion: 0.07
Nodes (46): create_rule(), delete_rule(), get_rule(), list_rules(), preview_rule(), AsyncSession, delete, get (+38 more)

### Community 20 - "device_io.py"
Cohesion: 0.09
Nodes (47): _carrier_diff_name(), _err(), _find_carrier(), _ip_tokens(), _load_refs(), _match(), _Occupancy, _placement_candidate() (+39 more)

### Community 21 - "addresses.py"
Cohesion: 0.07
Nodes (50): _address_csv_row(), _addresses_stmt(), bulk_addresses(), BulkBody, _check_interface_link(), create_address(), delete_address(), export_addresses() (+42 more)

### Community 22 - "get_redis"
Cohesion: 0.06
Nodes (46): close_arq_pool(), close_redis(), get_redis(), Shared process-wide Redis client. Do NOT aclose() it per call — connections…, Shut down the shared client — lifespan/worker shutdown only., lifespan(), shutdown(), auth_on() (+38 more)

### Community 23 - "imports.py"
Cohesion: 0.08
Nodes (44): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+36 more)

### Community 24 - "test_monitors.py"
Cohesion: 0.06
Nodes (32): _FakeArqPool, _FakeSMTP, _login(), _mk_device(), _mk_prefix_and_addr(), _mkuser(), V7 monitoring + notification channels. Covers target CRUD/RBAC, the exactly-…, Viewer reads targets but can't write/check/delete them. (+24 more)

### Community 25 - "worker.py"
Cohesion: 0.07
Nodes (44): ArqRedis, get_arq_pool(), Shared ARQ pool — callers must not close() it per job., redis_settings_from_url(), set_actor(), exclusion_hit(), Scan-target policy shared by the API route, the scheduler, and the worker.…, Return the first excluded CIDR overlapping ``net`` (either direction), or None.… (+36 more)

### Community 26 - "test_cabling.py"
Cohesion: 0.13
Nodes (46): _backup_bytes(), _cable(), _device(), _gen(), _iface(), _ip(), _login(), _mkuser() (+38 more)

### Community 27 - "hex_color_or_none"
Cohesion: 0.07
Nodes (29): IPRole, str, str, VLANStatus, field_validator, hex_color_or_none(), Shared row/tag color validator: #rrggbb, normalized to lowercase., field_validator (+21 more)

### Community 28 - "device-filter-panel.tsx"
Cohesion: 0.08
Nodes (40): PrefixDetailPage(), toggleIn(), DEVICE_FILTER_PARAMS, DEVICE_TEXT_PARAMS, DeviceFilterPanel(), DeviceFilterState, DeviceTextParam, FACES (+32 more)

### Community 29 - "v1/monitors.py"
Cohesion: 0.11
Nodes (40): check_now(), _check_refs(), create_target(), delete_target(), _filters(), _get(), get_target(), list_targets() (+32 more)

### Community 30 - "test_rack_io.py"
Cohesion: 0.16
Nodes (42): _bundle(), _by_sheet(), _cable(), _csv(), _device(), _group(), _iface(), _import() (+34 more)

### Community 31 - "get_settings"
Cohesion: 0.07
Nodes (29): do_run_migrations(), run_migrations_online(), get_settings(), psycopg2-style URL for alembic offline mode / scripts., Settings, Effective, _env_sourced(), get_effective() (+21 more)

### Community 32 - "deps.py"
Cohesion: 0.10
Nodes (27): _check_range_overlap(), create_range(), delete_range(), list_ranges(), AsyncSession, delete, get, post (+19 more)

### Community 33 - "scans.py"
Cohesion: 0.11
Nodes (34): cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession, get (+26 more)

### Community 34 - "Device"
Cohesion: 0.10
Nodes (33): Device, apply_device_import(), Write the ok rows in one transaction. Creates go through the create path's…, apply_device_patch(), carrier_children(), CarrierError, _check_carrier_mount(), check_layout_change() (+25 more)

### Community 35 - "test_secrets.py"
Cohesion: 0.10
Nodes (34): _data_key(), decrypt_str(), encrypt_str(), _master_key(), Exception, Secrets at rest — the credential contract v7/v8/v12/v14 build on. A single…, Unseal a "v1:…" blob. Strict prefix check — unknown formats, malformed payloads…, Base for secrets-service failures — never carries secret material. (+26 more)

### Community 37 - "test_device_io.py"
Cohesion: 0.20
Nodes (34): _csv(), _device(), _group(), _import(), _ip(), _login(), _mkuser(), _prefix() (+26 more)

### Community 38 - "test_devices.py"
Cohesion: 0.17
Nodes (32): _cable(), _device(), _group(), _iface(), _ip(), _prefix(), AsyncClient, _rack() (+24 more)

### Community 39 - "test_review.py"
Cohesion: 0.20
Nodes (35): _device(), _flag_mismatch(), _iface(), _ip(), _login(), _mkuser(), _prefix(), AsyncClient (+27 more)

### Community 40 - "rackula.ts"
Cohesion: 0.09
Nodes (35): RackulaImportDialog(), ABBREV_TO_CATEGORY, canonicalCategory(), CATEGORY_TO_ABBREV, clip(), compareVersions(), decodeShareUrl(), DeviceLike (+27 more)

### Community 41 - "NotificationChannel"
Cohesion: 0.10
Nodes (31): NotificationChannel, NotificationLog, Base, Outbound sink. ``config`` holds non-secret fields per kind; ``secret_enc`` is…, Append-only delivery attempt log — swept by ``notify_retention_days``., _deliver(), _DeliveryFailed, emit() (+23 more)

### Community 42 - "services/review.py"
Cohesion: 0.13
Nodes (34): accept_scanned_mac(), _aging_discovery_items(), build_review(), _cert_items(), _clear_flag(), _dismissal_map(), _dup_mac_items(), _emit() (+26 more)

### Community 43 - "User"
Cohesion: 0.16
Nodes (33): User, _backup_bytes(), _envelope_bytes(), _mkusers(), Hand-craft a backup envelope (e.g. with a forged users table)., Guard: every ORM table must be backed up (or explicitly excluded). Adding a new…, Fresh-server scenario: the migration-seeded Global VRF is replaced by the…, Fresh-server scenario: the target's admins survive; its non-admin set is fully… (+25 more)

### Community 44 - "scanner.py"
Cohesion: 0.09
Nodes (29): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), _host_chunks(), _icmp_checksum(), _icmp_echo_packet(), _icmp_socket() (+21 more)

### Community 45 - "test_scanner.py"
Cohesion: 0.11
Nodes (29): infer_device_type(), Best-effort device classification; None when nothing matched., _global_vrf_id(), _infer_scan_vrf(), Pick the VRF for a scan that didn't specify one. An exact-match prefix living…, _resolve_prefix(), _scan_vrf(), WorkerSettings (+21 more)

### Community 46 - "_split_dsn"
Cohesion: 0.12
Nodes (25): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., sf() (+17 more)

### Community 47 - "_matrix"
Cohesion: 0.15
Nodes (14): _master_row(), _matrix(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind… (+6 more)

### Community 48 - "v1/search.py"
Cohesion: 0.17
Nodes (27): _folded(), AsyncSession, get, Cross-object search for the command palette. One GET returns grouped matches…, Column expression with Hebrew final letters folded — pairs with fold_hebrew()…, Short label for a list-row search hit: key-column value, else the first non-…, _row_label(), search() (+19 more)

### Community 49 - "clean"
Cohesion: 0.10
Nodes (28): assemble_ip(), clean(), _clean_octets(), excel_date(), map_status(), mask_to_prefixlen(), network_of(), parse_range_end() (+20 more)

### Community 50 - "ChannelKind"
Cohesion: 0.12
Nodes (26): ChannelKind, MonitorKind, V7 — continuous monitoring targets + outbound notification channels., ChannelCreate, ChannelOut, ChannelTestOut, ChannelUpdate, MonitorSummary (+18 more)

### Community 51 - "_Planner"
Cohesion: 0.15
Nodes (8): parse_sites_master_records(), _Planner, (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Folded sheet title vs site name/code — word-boundary matching so 'int' doesn't…, Match a site among pre-existing DB rows AND sites already planned in this batch…, The circuits sheet doubles as a site directory (מאתר -> מספר אתר + קידומת…, Honesty checks on an octet/name match — inactive sites and title/site…, Counter

### Community 52 - "HostResult"
Cohesion: 0.09
Nodes (28): _flag(), Any, AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), HostResult, reconcile raising a mac_mismatch flag emits once; a follow-up scan that leaves…, test_mac_mismatch_emits_once() (+20 more)

### Community 53 - "test_ipam_extras.py"
Cohesion: 0.13
Nodes (28): _prefix(), _range(), export.csv takes the same filters as the list endpoint — a filtered view…, Same filtered-export treatment on the prefixes CSV (F8)., A documented v6 /64's 2^64 host count must not reach dashboard sums (~1.8e19 >…, A deliberate bulk import documents existing reality — statics inside pools land…, Scratch DB: seed a range + member address at 0024, upgrade to head —…, test_address_role_nat_and_bulk() (+20 more)

### Community 54 - "rack-editor.tsx"
Cohesion: 0.15
Nodes (27): DeviceFormDialog(), DragSession, DropRow(), EditorBlock(), errDetail(), Pending, RackEditor(), CarrierFrameSvg() (+19 more)

### Community 55 - "v1/review.py"
Cohesion: 0.12
Nodes (27): dismiss_item(), _flagged_address(), get_review(), mac_mismatch_accept(), mac_mismatch_keep(), AsyncSession, get, IPAddress (+19 more)

### Community 56 - "dependencies"
Cohesion: 0.07
Nodes (29): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, js-yaml, jszip, lucide-react (+21 more)

### Community 57 - "package.json"
Cohesion: 0.07
Nodes (25): name, private, version, autoprefixer, clsx, postcss, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+17 more)

### Community 58 - "ChangeLog"
Cohesion: 0.11
Nodes (22): list_changelog(), AsyncSession, get, AppSetting, Runtime-editable setting override. Absent row -> env var -> default., ChangeLog, NetBox-style audit trail: who changed what, when, and the field diff., fake_arq() (+14 more)

### Community 59 - "v1/settings.py"
Cohesion: 0.14
Nodes (23): _build_out(), _lan_info(), _mask_url(), AsyncSession, get, Hide the password in a scheme://user:pass@host URL., LAN identity detected by the host-networked worker (written to Redis). Falls…, read_settings() (+15 more)

### Community 60 - "backend/requirements.txt"
Cohesion: 0.14
Nodes (23): alembic==1.14.0, arq==0.26.1, asyncpg==0.30.0, bcrypt==4.3.0, cryptography==50.0.1, fastapi==0.115.6, httpx==0.28.1, openpyxl==3.1.5 (+15 more)

### Community 61 - "group-client.tsx"
Cohesion: 0.18
Nodes (21): DragSession, errDetail(), findDevice(), GroupClient(), moveDevice(), metadata, slotRect, freeByRack() (+13 more)

### Community 62 - "Smart import dialog"
Cohesion: 0.10
Nodes (26): GET /api/v1/devices/export.csv, GET /api/v1/devices/export.xlsx, POST /api/v1/devices/import, Carrier two-pass mounting, Changelog / audit history, CSV export, Dry-run preview with per-row {field:[old,new]} diffs, Export dropdown (Devices toolbar) (+18 more)

### Community 63 - "_FakeRedis"
Cohesion: 0.10
Nodes (18): _api_cancel(), _FakeRedis, In-memory stand-in for the worker's redis client (get/set/publish)., Point the worker at the test DB (sf) and the fake redis client., Simulate the API-side cancel: terminal status on a fresh connection., Audit race: API writes CANCELLED mid-scan while the redis flag is lost…, Cancel landing while reconcile writes rows: the flag + row re-check right…, A job already terminal when the worker picks it up is skipped — no RUNNING… (+10 more)

### Community 64 - "quick-scan.tsx"
Cohesion: 0.11
Nodes (19): ACTION_STYLES, ChangelogPage(), metadata, MonitoringPage(), targetLink(), fmtEta(), ScansPage(), ChangeDiff() (+11 more)

### Community 65 - "build-rack-library.mjs"
Cohesion: 0.13
Nodes (23): arrLen(), attribution(), CATEGORY_COLOUR, CURATED, fetchBuf(), fetchJson(), FRONTEND, FULL_IMPORT (+15 more)

### Community 66 - "tree-client.tsx"
Cohesion: 0.18
Nodes (19): metadata, ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), collectExpandableKeys(), flattenTree() (+11 more)

### Community 67 - "maintenance.py"
Cohesion: 0.17
Nodes (22): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+14 more)

### Community 68 - "hash_password"
Cohesion: 0.16
Nodes (22): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+14 more)

### Community 69 - "UserRole"
Cohesion: 0.34
Nodes (22): str, UserRole, login(), mkuser(), other_client(), AsyncClient, AsyncSession, allow_insecure keeps full access (existing behavior preserved). (+14 more)

### Community 70 - "test_colors.py"
Cohesion: 0.22
Nodes (22): auth_on(), _login(), _mk_rule(), _mk_site(), _mkuser(), AsyncClient, AsyncSession, fixture (+14 more)

### Community 71 - "demo_rack_dc.py"
Cohesion: 0.13
Nodes (16): Api, apply(), _device_payload(), emit_zip(), find_one(), _KeepMethodRedirect, layout_doc(), main() (+8 more)

### Community 72 - "v1/backup.py"
Cohesion: 0.16
Nodes (20): delete_scheduled_backup(), download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, delete, get, post (+12 more)

### Community 73 - "parse_site_sheet"
Cohesion: 0.12
Nodes (10): _col_class(), parse_site_sheet(), _positional_columns(), Dominant content class of a column sample., Headerless sheet: locate the IP column, then assign the remaining canonical…, MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf., Bare 'Name' (Cellular) maps to the hostname field., Non-empty unnamed columns pile into cf['extra'] instead of vanishing (Pelephone… (+2 more)

### Community 74 - "_FakeRedis"
Cohesion: 0.10
Nodes (12): _FakeRedis, check-now drives the same state machine the sweep does; failures accrue until…, Observed churn (state/failures/last_*) must not touch the audit log., In-memory get/set/publish stand-in for the worker's redis client., _cert_warnings emits cert.expiring once per cert per day — the Redis day-stamp…, A scan that raises mid-job flips to FAILED and emits scan.failed., test_cert_warning_emits_once_per_day(), test_check_now_transitions_and_emits() (+4 more)

### Community 75 - "test_ordering.py"
Cohesion: 0.22
Nodes (21): auth_on(), _circuit_order(), _login(), _mk_circuits(), _mkuser(), AsyncClient, AsyncSession, fixture (+13 more)

### Community 76 - "channels.py"
Cohesion: 0.20
Nodes (20): _config_fields(), create_channel(), delete_channel(), _get(), get_channel(), list_channels(), notification_log(), _out() (+12 more)

### Community 77 - "services/backup.py"
Cohesion: 0.17
Nodes (20): _alembic_revisions(), backup_dir(), backup_filename(), delete_backup_file(), _fail_inflight_scans(), list_backup_files(), prune_backups(), datetime (+12 more)

### Community 78 - "test_workbook_import.py"
Cohesion: 0.11
Nodes (16): parse_certificates(), Positional 5-col layout: platform, target/VS, server, cert, expiry., Workbook import: normalizer/parser unit tests (no DB) + API e2e., Small synthetic workbook: sites master + one site sheet + circuits., Site sheet documenting a DHCP span AND static stations inside it — the real…, Pool-guard regression: committing a plan whose dhcp range covers documented…, Commit-time PlanError must 422 AND record the failure. The route rolls back…, test_commit_plan_error_marks_batch_failed() (+8 more)

### Community 79 - "IpamBox README"
Cohesion: 0.18
Nodes (21): Changelog bypass for state writes, Add network wizard, Subnets doc, Gateway/DNS technical addresses, IP address, IP range (dhcp/pool/reserved), Subnet matrix, Pool override (force=1) (+13 more)

### Community 80 - "parsers.py"
Cohesion: 0.14
Nodes (17): norm_header(), Header cell -> lowercase, single-spaced, for signature matching. Edge…, _blocks(), _is_header_echo(), _leftover_bits(), _map_columns(), parse_assets(), parse_inventory() (+9 more)

### Community 81 - "Excel workbook import"
Cohesion: 0.16
Nodes (20): Demo CSV files, Fictional demo dataset, Demo import data README, Demo VLAN scheme, Network_Address_DEMO.xlsx, Network_Address_DEMO_EN.xlsx, backend/app/services/workbook parser, Asset (SW/HW inventory) (+12 more)

### Community 82 - "RackFace"
Cohesion: 0.18
Nodes (11): First-class device: a host that exists independently of any rack. A Device owns…, str, RackFace, DeviceCreate, DeviceDetail, DeviceOut, DeviceUpdate, BaseModel (+3 more)

### Community 83 - "extract_list_table"
Cohesion: 0.17
Nodes (13): _cell_text(), extract_list_table(), _infer_type(), _ips(), _is_ip_token(), Custom-list extraction: turn any sheet into {columns, rows} for a list. Unlike…, SheetMatrix -> (column defs, row dicts). columns: [{key, label, type, options?,…, Raw cell -> stored string. Dates iso-format; everything else cleans. (+5 more)

### Community 84 - "test_prefix_api.py"
Cohesion: 0.22
Nodes (18): _addrs(), _global_vrf_id(), _mkprefix(), Splits are counted arithmetically before materializing: anything over…, test_gateway_clear_removes_only_pristine_row(), test_gateway_never_clobbers_manual_row(), test_gateway_validation(), test_next_ip_never_hands_out_gateway() (+10 more)

### Community 85 - "Device (first-class host entity)"
Cohesion: 0.18
Nodes (19): IPAddress, connected_interface_id (structured far-end port link), connected_ip (host-side NIC binding), DeviceInterface (device-owned port), L1 trace (cable path walk), match-free-text transition endpoint, One-cable-per-interface rule, Front/back port pairing (pair partner / pair_interface_id) (+11 more)

### Community 86 - "Monitoring doc (V7)"
Cohesion: 0.23
Nodes (19): Check kinds (ping/tcp/http), Monitoring doc (V7), Event sources, Deliberate limits, Monitor target, Notification channel, Notification log, Secrets contract (+11 more)

### Community 87 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 88 - "docs.ts"
Cohesion: 0.19
Nodes (11): DocsIndexClient(), metadata, DocsNav(), BY_SLUG, DOC_ARTICLES, DOC_CATEGORIES, DocArticle, DocCategory (+3 more)

### Community 89 - "restore_backup"
Cohesion: 0.15
Nodes (17): Delete assignments whose target no longer exists. For non-ORM write paths…, sweep_orphans(), build_backup(), _from_json(), Any, AsyncSession, Base, Convert a JSON value back to what asyncpg expects for this column. (+9 more)

### Community 90 - "schemas/import_batch.py"
Cohesion: 0.21
Nodes (12): CommitOptions, ImportBatchOut, ListTarget, PreviewOptions, BaseModel, Per-sheet detection result shown in the wizard., Import a sheet as a custom list (user-selected or suggested)., User-confirmed mapping choices applied before building the plan. (+4 more)

### Community 91 - "network.py"
Cohesion: 0.20
Nodes (10): _ip(), NetworkCreate, NetworkDhcpRange, NetworkOut, NetworkPrefix, NetworkVlanNew, BaseModel, field_validator (+2 more)

### Community 92 - "test_ip_source.py"
Cohesion: 0.24
Nodes (16): may_write(), Field-ownership check for source-stamped rows (ip_addresses et al.). True when…, _mk_prefix(), V6 provenance — ip_addresses.source: stamping, ownership, filtering. Every…, Manual and imported rows keep their provenance when a scan sees them — observed…, Response bodies carry `source` but never any *_enc-style field., test_csv_import_stamps_import(), test_export_filters_and_carries_source() (+8 more)

### Community 93 - "load_upload"
Cohesion: 0.18
Nodes (14): parse_device_sheet(), One SheetMatrix -> (headers, [(row_no, {header: str})]). Row numbers are the…, First sheet of an xlsx/CSV -> (headers, [(row_no, {header: str})]). xlsx is…, sheet_rows(), _csv_sheet(), load_upload(), load_workbook_bytes(), XLSX/CSV -> sheet matrices (openpyxl read_only streams / csv module). (+6 more)

### Community 94 - "_mklist"
Cohesion: 0.21
Nodes (3): _mklist(), TestListCRUD, TestRows

### Community 95 - ".resolve_sheet_site"
Cohesion: 0.21
Nodes (6): Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new…, Resolve a 10.{second}.x sheet — site_number is only meaningful inside the…, A declared octet block claims the sheet — unless its site is inactive, in which…, site_key, matched_by for a site_sheet.

### Community 96 - "test_search.py"
Cohesion: 0.25
Nodes (14): auth_on(), AsyncClient, fixture, Global /api/v1/search endpoint (UX-3)., Regression: list_addresses ?q= used to crash on a missing column., Site + VRF + prefix + address + one of each workbook entity., _seed(), test_addresses_q_filter_not_broken() (+6 more)

### Community 97 - "smart-import-dialog.tsx"
Cohesion: 0.16
Nodes (12): ACTION_STYLE, ColumnMap, DetectResp, FieldOption, fmt(), ImportOption, ImportResp, ResultRows() (+4 more)

### Community 98 - "parse_sites_master"
Cohesion: 0.19
Nodes (8): _master_blocks(), parse_sites_master(), (first, second) octet pairs a master row declares — lets sheet->site matching…, Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins., TestSitesMasterParser

### Community 99 - "test_lists.py"
Cohesion: 0.23
Nodes (10): _preview_of(), Custom lists: CRUD + rows + IP resolution + workbook list-target import., v2 workbook: SRV2 edited, SRV3 added, SRV1 missing -> merge keeps SRV1, updates…, _servers_xlsx(), test_import_as_list_e2e(), test_manually_edited_row_wins_conflict(), test_reimport_merges_by_key(), TestBulkRows (+2 more)

### Community 100 - "test_maintenance.py"
Cohesion: 0.21
Nodes (11): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_now_enqueues(), test_clear_discovery() (+3 more)

### Community 101 - "test_changelog.py"
Cohesion: 0.23
Nodes (12): AsyncClient, tag_assignments.object_id has no FK — deleting a tagged object must drop its…, Tag.assignments is already ORM delete-orphan — each removed assignment lands in…, PATCH settings with a null value deletes the app_settings row — that delete…, /addresses/bulk action=delete used to issue one Core DELETE — invisible to the…, test_bulk_delete_writes_changelog_entries(), test_changelog_captures_ip_status_change(), test_changelog_records_crud() (+4 more)

### Community 102 - "Racks"
Cohesion: 0.23
Nodes (13): Carrier (slot-layout device: shelves/trays), Device image library, Elevation editor, Find free U, Health overlay, Linked asset and IP address, Rack placement rules, Printing and QR labels (+5 more)

### Community 103 - "core/changelog.py"
Cohesion: 0.35
Nodes (11): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), Audit trail via session flush hooks. before_flush collects (object, action,…, register(), _repr() (+3 more)

### Community 104 - "worker/monitors.py"
Cohesion: 0.24
Nodes (11): parse_http_expect(), (ok, error) for an HTTP response against the expectation grammar., check_target(), _http(), _ping(), AsyncClient, Semaphore, The monitor lane — per-target health checks on the worker's minute cron.… (+3 more)

### Community 105 - "test_scan_cidr_tcp_fallback_reports_found"
Cohesion: 0.21
Nodes (8): on_hosts fires once per detection step with that chunk's new IPs — ARP batch…, When L2+L3 find nothing, the TCP fallback publishes its batch too., test_scan_cidr_emits_found_deltas(), fake_icmp(), fake_probe(), fake_ptr(), on_hosts(), test_scan_cidr_tcp_fallback_reports_found()

### Community 106 - "Rack device image library"
Cohesion: 0.24
Nodes (11): Demo .Rackula.zip racks, Air-gap safe bundling, CC0 1.0 Universal license, CC0 1.0 Universal, netbox-community/devicetype-library, Rack library ATTRIBUTION, netbox-community/devicetype-library, Rack device image library (+3 more)

### Community 107 - "docs/[slug]/page.tsx"
Cohesion: 0.24
Nodes (9): DocPage(), dynamicParams, generateMetadata(), loadMarkdown(), DocsContent(), docCategoryLabel(), getDoc(), react-markdown (+1 more)

### Community 108 - "_FakePool"
Cohesion: 0.20
Nodes (8): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture, Stands in for the arq Redis pool — never actually dispatches work., scan_exclude_networks=10.70.0.64/26 inside scan_networks=10.70.0.0/24: the…, test_scheduler_and_route_share_exclusion_guard()

### Community 109 - "command-palette.tsx"
Cohesion: 0.31
Nodes (10): CommandPalette(), Icon, Item, itemsFor(), PAGES, pagesFor(), remember(), SearchOut (+2 more)

### Community 111 - "devDependencies"
Cohesion: 0.20
Nodes (10): devDependencies, autoprefixer, postcss, sharp, tailwindcss, @types/js-yaml, @types/node, @types/react (+2 more)

### Community 112 - "Cable"
Cohesion: 0.42
Nodes (10): Cable, connected_interface structured link, Cabling doc, Interface, L1 trace, POST /api/v1/interfaces/match-free-text, Patch panel as kind=patch device, Bulk port generation (+2 more)

### Community 113 - "RackFace"
Cohesion: 0.29
Nodes (9): Placed, libraryBySlug(), LibraryDevice, libraryImage(), RACK_LIBRARY, ImportDevice, PreviewRow, RackFace (+1 more)

### Community 114 - "CircuitUpdate"
Cohesion: 0.33
Nodes (5): CircuitCreate, CircuitOut, CircuitUpdate, BaseModel, field_validator

### Community 115 - ".add_list_sheet"
Cohesion: 0.22
Nodes (5): pick_key_column(), Default merge column: first non-date/ip column filled in most rows (the…, Map incoming column keys onto an existing list's defs by folded label — a re-…, User-picked key column may arrive as a key ('c0') or a header label ('Name');…, Extract a sheet as custom-list rows and diff it against the existing list…

### Community 116 - "rack-collision.ts"
Cohesion: 0.33
Nodes (6): canPlace(), conflicts(), facesCollide(), freeSlots(), rangesOverlap(), SLOT_LAYOUTS

### Community 117 - "v1/dashboard.py"
Cohesion: 0.32
Nodes (6): AsyncSession, get, stats(), DashboardStats, MacMismatchItem, BaseModel

### Community 118 - "readyz"
Cohesion: 0.25
Nodes (8): healthz(), get, Request, Readiness probe: verifies DB + Redis connectivity., readyz(), _secrets_not_configured(), exception_handler, JSONResponse

### Community 119 - "ReviewDismissal"
Cohesion: 0.25
Nodes (6): Base, Review center (V7.1): operator dismissals for computed findings. Every review…, ReviewDismissal, dismiss(), Record a dismissal; re-dismissing the same tuple returns the row., test_review_dismissals_backed_up_and_audited()

### Community 120 - "common.py"
Cohesion: 0.32
Nodes (4): ip_display(), Any, Normalize asyncpg-returned ipaddress objects / strings to display form. INET…, to_int()

### Community 121 - "classify.py"
Cohesion: 0.36
Nodes (6): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…

### Community 122 - "parse_circuits"
Cohesion: 0.29
Nodes (5): parse_site_number(), parse_circuits(), קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., TestCircuitsParser

### Community 123 - "test_allocation.py"
Cohesion: 0.43
Nodes (7): _mk_prefix(), test_address_crud_and_dup_guard(), test_allocation_skips_existing(), test_concurrent_allocation_unique(), alloc(), test_exhausted_prefix_conflicts(), test_sequential_allocation_skips_boundaries()

### Community 124 - "check-rack-library.mjs"
Cohesion: 0.25
Nodes (6): DIR, FACES, LAYOUTS, problems, referenced, slugs

### Community 125 - "BackupError"
Cohesion: 0.33
Nodes (7): BackupError, BackupPreview, _gunzip(), inspect_backup(), Exception, Validate a backup payload without touching the database., Raised for any malformed/unsupported backup payload. Maps to HTTP 422.

### Community 126 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, build:rack-library, check:rack-library, dev, lint, start

### Community 127 - "Devices"
Cohesion: 0.29
Nodes (7): API sketch, Device detail, Devices, Devices vs racks, From the IP drawer, Health rollup, The list

### Community 128 - "_mkuser"
Cohesion: 0.53
Nodes (6): _login(), _mkuser(), AsyncSession, RBAC unchanged: the facet vocabulary stays DATA_READ., test_devices_list_filters_viewer(), test_devices_rbac()

### Community 130 - "fake_arq"
Cohesion: 0.33
Nodes (3): _Job, fake_arq(), enqueue_job()

### Community 131 - "Docs: IP Addresses"
Cohesion: 0.40
Nodes (5): Docs: IP Addresses, Docs: Devices, Docs: Racks, Docs: Settings, Docs: Subnets

### Community 132 - "use-chart-theme.ts"
Cohesion: 0.50
Nodes (4): ChartTheme, FALLBACK, readTheme(), useChartTheme()

### Community 133 - "Security Policy"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 134 - "after_flush"
Cohesion: 0.67
Nodes (4): after_flush(), before_flush(), SyncSession, register()

## Ambiguous Edges - Review These
- `Cable` → `Rack`  [AMBIGUOUS]
  frontend/src/content/docs/cabling.md · relation: conceptually_related_to
- `Stats strip & saved views` → `Monitoring doc (V7)`  [AMBIGUOUS]
  frontend/src/content/docs/inventory.md · relation: semantically_similar_to

## Knowledge Gaps
- **367 isolated node(s):** `Icon`, `Item`, `SearchOut`, `DensityChoice`, `FxLevel` (+362 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1456 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Cable` and `Rack`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Stats strip & saved views` and `Monitoring doc (V7)`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._
- **Why does `_resolve_prefix()` connect `test_scanner.py` to `IPAddress`, `worker.py`, `lucide-react`?**
  _High betweenness centrality (0.174) - this node is a cross-community bridge._
- **Why does `Prefix` connect `lucide-react` to `index.ts`, `prefixes-client.tsx`, `cn`, `import-client.tsx`, `test_scanner.py`?**
  _High betweenness centrality (0.173) - this node is a cross-community bridge._
- **Why does `run_scheduled_scans()` connect `worker.py` to `IPAddress`, `_FakePool`, `lucide-react`, `get_settings`?**
  _High betweenness centrality (0.122) - this node is a cross-community bridge._
- **Are the 72 inferred relationships involving `IPAMError` (e.g. with `_get_cable()` and `_get_interface()`) actually correct?**
  _`IPAMError` has 72 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `get_or_404()` (e.g. with `_check_interface_link()` and `create_address()`) actually correct?**
  _`get_or_404()` has 9 INFERRED edges - model-reasoned connections that need verification._