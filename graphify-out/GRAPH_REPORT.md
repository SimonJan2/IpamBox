# Graph Report - IpamBox  (2026-09-25)

## Corpus Check
- 2 files · ~0 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 4732 nodes · 15241 edges · 196 communities (133 shown, 27 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 1174 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- index.ts
- test_snmp.py
- devices-client.tsx
- react
- devices.py
- useAsyncData()
- lucide-react
- get_settings()
- IPAMError
- v1/racks.py
- cn()
- rack_io.py
- DeviceInterface
- ip_display()
- prefixes.py
- test_racks.py
- Device
- IpamBox
- generate_demo_data.py
- color_rules.py
- test_review.py
- test_scanner.py
- Base
- test_monitors.py
- IPAddress
- channels.py
- _Planner
- clean()
- utils.ts
- User
- IPStatus
- v1/monitors.py
- Site
- test_devices.py
- app-shell.tsx
- test_cabling.py
- test_rack_io.py
- addresses.py
- test_snmp.py
- entities.py
- imports.py
- run_scan()
- deps.py
- NotificationChannel
- test_secrets.py
- worker.py
- route-error.tsx
- scanner.py
- _split_dsn()
- test_device_io.py
- badge.tsx
- scans.py
- rackula.ts
- test_backup.py
- tags.py
- test_lists.py
- _matrix()
- v1/search.py
- services/racks.py
- Rack
- vlans.py
- UserRole
- dependencies
- services/backup.py
- group-client.tsx
- Smart import dialog
- runtime_settings.py
- traps.py
- test_ipam_extras.py
- package.json
- backend/requirements.txt
- v1/backup.py
- SNMP Enrichment Documentation
- build-rack-library.mjs
- tree-client.tsx
- v1/settings.py
- ChangeLog
- demo_rack_dc.py
- _wire_traps()
- maintenance.py
- IpamBox README
- execute_plan()
- test_colors.py
- Excel workbook import
- rack-editor.tsx
- test_ordering.py
- test_prefix_api.py
- Monitoring doc (V7)
- compilerOptions
- listparse.py
- _mklist()
- docs.ts
- Device (first-class host entity)
- users.py
- network.py
- test_ip_source.py
- parse_site_sheet()
- test_workbook_import.py
- parse_sites_master()
- rack-collision.ts
- _FakeRedis
- test_allocation.py
- test_changelog.py
- test_search.py
- Rack device image library
- test_auth.py
- test_scan_cidr_tcp_fallback_reports_found()
- docs/[slug]/page.tsx
- Racks
- backup_dir()
- _FakePool
- command-palette.tsx
- Device
- reader.py
- worker/monitors.py
- TestNormalize
- devDependencies
- Cabling doc
- classify.py
- check-rack-library.mjs
- RackFace
- _positional_columns()
- _mkuser()
- scripts
- Devices
- test_tick_batches_due_devices_into_one_job()
- test_entities.py
- shortcuts.ts
- key()
- .test_legacy_bezeq_layout()
- Docs: IP Addresses
- use-chart-theme.ts
- Security Policy
- _serialize_row()
- test_rbac_cabling()
- test_snmp_test_endpoint()
- next-env.d.ts
- POST /api/v1/devices/import
- Racks REST API (GET /api/v1/racks)
- xff-shim.js
- test_trap_listener_binds_releases_and_eats_garbage()
- test_trap_bind_failure_logs_once_and_stays_off()
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
3. `Device` - 107 edges
4. `IPAMError` - 99 edges
5. `get_or_404()` - 86 edges
6. `useAsyncData()` - 84 edges
7. `lucide-react` - 80 edges
8. `IPAddress` - 75 edges
9. `useAuth()` - 73 edges
10. `get_settings()` - 71 edges

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
- **SNMP Poll Flow** — frontend_src_content_docs_snmp_md_poll_pipeline, frontend_src_content_docs_snmp_md_if_mib_upsert, frontend_src_content_docs_snmp_md_bridge_mac_resolution, frontend_src_content_docs_snmp_md_lldp_collection [EXTRACTED 1.00]
- **Backend Dependencies Enabling SNMP Enrichment** — backend_requirements_txt_pysnmp, backend_requirements_txt_cryptography, backend_requirements_txt_arq [INFERRED 0.65]
- **Non-Destructive Enrichment Contract** — frontend_src_content_docs_snmp_md_read_only_polling, frontend_src_content_docs_snmp_md_may_write_provenance, frontend_src_content_docs_snmp_md_stale_dimming [INFERRED 0.85]

## Communities (196 total, 27 thin omitted)

### Community 0 - "index.ts"
Cohesion: 0.03
Nodes (119): EMPTY_EDIT, FACE_BADGE, ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, PreviewResp (+111 more)

### Community 1 - "test_snmp.py"
Cohesion: 0.05
Nodes (108): _apply_bridge_links(), _auth(), _context(), _cred(), due_device_ids(), _get(), _idx_int(), _idx_tail_ints() (+100 more)

### Community 2 - "devices-client.tsx"
Cohesion: 0.08
Nodes (85): EMPTY, ACTION_STYLES, EMPTY, DEVICE_VIEWS, DeviceRow, EMPTY, IMPORT_FIELDS, IMPORT_OPTIONS (+77 more)

### Community 3 - "react"
Cohesion: 0.02
Nodes (39): nextConfig, metadata, metadata, metadata, metadata, metadata, metadata, metadata (+31 more)

### Community 4 - "devices.py"
Cohesion: 0.05
Nodes (95): _asset_ref(), _check_iface_refs(), _check_refs(), create_device(), create_interface(), delete_device(), delete_interface(), _detail() (+87 more)

### Community 5 - "useAsyncData()"
Cohesion: 0.06
Nodes (92): CertificatesPage(), CircuitsPage(), DevicesPage(), DeviceDetailClient(), DiscoveryPage(), ImportPage(), InventoryPage(), ListsClient() (+84 more)

### Community 6 - "lucide-react"
Cohesion: 0.07
Nodes (61): BulkResp, DELETE_PATH, DeleteTarget, DismissTarget, SECTION_ICONS, Draft, ENTITIES, OP_LABEL (+53 more)

### Community 7 - "get_settings()"
Cohesion: 0.04
Nodes (85): ArqRedis, do_run_migrations(), run_migrations_online(), cancel_scan(), post, get_settings(), close_arq_pool(), close_redis() (+77 more)

### Community 8 - "IPAMError"
Cohesion: 0.06
Nodes (83): _crud_router(), create_item(), delete_item(), get_item(), list_items(), reorder_items(), update_item(), bulk_rows() (+75 more)

### Community 9 - "v1/racks.py"
Cohesion: 0.06
Nodes (74): _check_refs(), create_device(), create_rack(), delete_device(), delete_rack(), _device_out(), _devices(), _export_name() (+66 more)

### Community 10 - "cn()"
Cohesion: 0.05
Nodes (67): ImportListDialog(), IpCell(), SortableColRow(), metadata, IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES (+59 more)

### Community 11 - "rack_io.py"
Cohesion: 0.05
Nodes (74): import_racks(), Request, Smart rack/group bundle import — V5B's stateless flow for whole trees. Sheets…, RackGroup, A bayed row: racks ordered left-to-right as they stand in the DC., _alias_to_field(), auto_map_fields(), auto_map_headers() (+66 more)

### Community 12 - "DeviceInterface"
Cohesion: 0.06
Nodes (69): _cable_out(), _check_ends(), create_cable(), delete_cable(), _get_cable(), _get_interface(), interfaces_match_free_text(), list_cables() (+61 more)

### Community 13 - "ip_display()"
Cohesion: 0.05
Nodes (74): AsyncSession, get, stats(), dismiss_item(), _flagged_address(), get_review(), mac_mismatch_accept(), mac_mismatch_keep() (+66 more)

### Community 14 - "prefixes.py"
Cohesion: 0.07
Nodes (63): allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), _prefix_rows() (+55 more)

### Community 15 - "test_racks.py"
Cohesion: 0.10
Nodes (60): _carrier(), _dev(), _group(), _imports(), _mount(), _next_free(), AsyncClient, _rack() (+52 more)

### Community 16 - "Device"
Cohesion: 0.08
Nodes (53): Device, Base, str, RackFace, apply_device_import(), _carrier_diff_name(), _err(), _find_carrier() (+45 more)

### Community 17 - "IpamBox"
Cohesion: 0.09
Nodes (60): api service (FastAPI/uvicorn backend), db service (PostgreSQL 16), ipam bridge network (192.0.2.0/24), redis service (Redis 7, appendonly), scanner service (arq worker, host networking), web service (Next.js frontend), Accounts & Roles, Insecure mode (IPAMBOX_ALLOW_INSECURE) (+52 more)

### Community 18 - "generate_demo_data.py"
Cohesion: 0.07
Nodes (58): assets_rows(), _assign_site_sheets(), _assign_site_sheets_clean(), build_en_workbook(), build_mixed_workbook(), build_sites(), certificates_rows(), circuits_rows() (+50 more)

### Community 19 - "color_rules.py"
Cohesion: 0.07
Nodes (46): create_rule(), delete_rule(), get_rule(), list_rules(), preview_rule(), AsyncSession, delete, get (+38 more)

### Community 20 - "test_review.py"
Cohesion: 0.11
Nodes (50): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), Audit trail via session flush hooks. before_flush collects (object, action,…, register(), _repr() (+42 more)

### Community 21 - "test_scanner.py"
Cohesion: 0.07
Nodes (49): _flag(), Any, AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), HostResult, _global_vrf_id(), _infer_scan_vrf() (+41 more)

### Community 22 - "Base"
Cohesion: 0.10
Nodes (28): after_flush(), before_flush(), SyncSession, tag_assignments garbage collection. TagAssignment references its target…, register(), healthz(), metrics(), get (+20 more)

### Community 23 - "test_monitors.py"
Cohesion: 0.05
Nodes (35): _FakeArqPool, _FakeSMTP, _Job, _login(), _mk_device(), _mk_prefix_and_addr(), _mkuser(), V7 monitoring + notification channels. Covers target CRUD/RBAC, the exactly-… (+27 more)

### Community 24 - "IPAddress"
Cohesion: 0.08
Nodes (42): create_network(), AsyncSession, post, _check_range_overlap(), create_range(), delete_range(), list_ranges(), AsyncSession (+34 more)

### Community 25 - "channels.py"
Cohesion: 0.09
Nodes (46): _config_fields(), create_channel(), delete_channel(), _get(), get_channel(), list_channels(), notification_log(), _out() (+38 more)

### Community 26 - "_Planner"
Cohesion: 0.09
Nodes (16): _Planner, _preview(), (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Folded sheet title vs site name/code — word-boundary matching so 'int' doesn't…, Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new…, Resolve a 10.{second}.x sheet — site_number is only meaningful inside the… (+8 more)

### Community 27 - "clean()"
Cohesion: 0.08
Nodes (41): assemble_ip(), clean(), _clean_octets(), map_status(), mask_to_prefixlen(), network_of(), norm_header(), parse_range_end() (+33 more)

### Community 28 - "utils.ts"
Cohesion: 0.08
Nodes (34): ChangelogPage(), ACTION_STYLES, DashboardPage(), MonitoringPage(), targetLink(), metadata, metadata, WhyCell() (+26 more)

### Community 29 - "User"
Cohesion: 0.11
Nodes (44): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+36 more)

### Community 30 - "IPStatus"
Cohesion: 0.07
Nodes (33): IPRole, IPStatus, str, ConnectedInterfaceRef, IPAddressCreate, IPAddressOut, IPAddressPage, IPAddressUpdate (+25 more)

### Community 31 - "v1/monitors.py"
Cohesion: 0.10
Nodes (42): check_now(), _check_refs(), create_target(), delete_target(), _filters(), _get(), get_target(), list_targets() (+34 more)

### Community 32 - "Site"
Cohesion: 0.10
Nodes (34): _cascade_site_fields(), create_site(), delete_site(), get_site(), list_sites(), AsyncSession, delete, get (+26 more)

### Community 33 - "test_devices.py"
Cohesion: 0.13
Nodes (39): _cable(), _device(), _group(), _iface(), _ip(), _login(), _mkuser(), _prefix() (+31 more)

### Community 34 - "app-shell.tsx"
Cohesion: 0.07
Nodes (35): metadata, viewport, AppearancePage(), AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS (+27 more)

### Community 35 - "test_cabling.py"
Cohesion: 0.15
Nodes (42): _backup_bytes(), _cable(), _device(), _gen(), _iface(), _ip(), _panel_path(), _prefix() (+34 more)

### Community 36 - "test_rack_io.py"
Cohesion: 0.16
Nodes (42): _bundle(), _by_sheet(), _cable(), _csv(), _device(), _group(), _iface(), _import() (+34 more)

### Community 37 - "addresses.py"
Cohesion: 0.09
Nodes (41): _address_csv_row(), _addresses_stmt(), bulk_addresses(), BulkBody, _check_interface_link(), create_address(), delete_address(), export_addresses() (+33 more)

### Community 38 - "test_snmp.py"
Cohesion: 0.18
Nodes (36): AsyncClient, _device(), _down(), _enable(), _ifrow(), _ip(), _mock_poll(), _orm_device() (+28 more)

### Community 39 - "entities.py"
Cohesion: 0.10
Nodes (26): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, AssetKind, str, AssetCreate, AssetOut, AssetUpdate, BaseModel, field_validator (+18 more)

### Community 40 - "imports.py"
Cohesion: 0.11
Nodes (36): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+28 more)

### Community 41 - "run_scan()"
Cohesion: 0.08
Nodes (32): Exception, Raised inside the pipeline when the user cancels the scan., ScanCancelled, cancel_key(), _job_status(), _publish(), Re-read the job row's status — the session's `job` instance goes stale the…, ARQ job: execute a scan and reconcile results. (+24 more)

### Community 42 - "deps.py"
Cohesion: 0.09
Nodes (26): list_changelog(), AsyncSession, get, confirm_discovered(), ConfirmBody, list_discovered(), AsyncSession, BaseModel (+18 more)

### Community 43 - "NotificationChannel"
Cohesion: 0.09
Nodes (35): NotificationChannel, NotificationLog, Base, Outbound sink. ``config`` holds non-secret fields per kind; ``secret_enc`` is…, Append-only delivery attempt log — swept by ``notify_retention_days``., _deliver(), _DeliveryFailed, emit() (+27 more)

### Community 44 - "test_secrets.py"
Cohesion: 0.10
Nodes (34): _data_key(), decrypt_str(), encrypt_str(), _master_key(), Exception, Secrets at rest — the credential contract v7/v8/v12/v14 build on. A single…, Unseal a "v1:…" blob. Strict prefix check — unknown formats, malformed payloads…, Base for secrets-service failures — never carries secret material. (+26 more)

### Community 45 - "worker.py"
Cohesion: 0.10
Nodes (35): _lan_info(), LAN identity detected by the host-networked worker (written to Redis). Falls…, set_actor(), get_effective(), AsyncSession, monitor_tick(), Every-minute cron beside scheduler_tick: batch due targets into a single sweep…, detect_interface() (+27 more)

### Community 47 - "scanner.py"
Cohesion: 0.08
Nodes (32): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), _host_chunks(), _icmp_checksum(), _icmp_echo_packet(), _icmp_socket() (+24 more)

### Community 48 - "_split_dsn()"
Cohesion: 0.11
Nodes (26): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., _split_dsn() (+18 more)

### Community 49 - "test_device_io.py"
Cohesion: 0.20
Nodes (34): _csv(), _device(), _group(), _import(), _ip(), _login(), _mkuser(), _prefix() (+26 more)

### Community 50 - "badge.tsx"
Cohesion: 0.09
Nodes (24): LabelClient(), metadata, metadata, FACE_BADGE, PrintClient(), ExpiryBadge(), RackQrCode(), RackQrDialog() (+16 more)

### Community 51 - "scans.py"
Cohesion: 0.11
Nodes (30): _check_cidr_allowed(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession, get, ScanJob (+22 more)

### Community 52 - "rackula.ts"
Cohesion: 0.10
Nodes (33): RackulaImportDialog(), ABBREV_TO_CATEGORY, canonicalCategory(), CATEGORY_TO_ABBREV, clip(), compareVersions(), decodeShareUrl(), DeviceLike (+25 more)

### Community 53 - "test_backup.py"
Cohesion: 0.16
Nodes (32): _backup_bytes(), _envelope_bytes(), _mkusers(), Hand-craft a backup envelope (e.g. with a forged users table)., Guard: every ORM table must be backed up (or explicitly excluded). Adding a new…, Fresh-server scenario: the migration-seeded Global VRF is replaced by the…, Fresh-server scenario: the target's admins survive; its non-admin set is fully…, A backup carrying an assignment for a missing object (e.g. taken while orphans… (+24 more)

### Community 54 - "tags.py"
Cohesion: 0.14
Nodes (25): assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession, delete (+17 more)

### Community 55 - "test_lists.py"
Cohesion: 0.12
Nodes (20): ListTarget, Import a sheet as a custom list (user-selected or suggested)., extract_list_table(), pick_key_column(), SheetMatrix -> (column defs, row dicts). columns: [{key, label, type, options?,…, Default merge column: first non-date/ip column filled in most rows (the…, User-picked key column may arrive as a key ('c0') or a header label ('Name');…, _matrix() (+12 more)

### Community 56 - "_matrix()"
Cohesion: 0.15
Nodes (14): _master_row(), _matrix(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind… (+6 more)

### Community 57 - "v1/search.py"
Cohesion: 0.17
Nodes (27): _folded(), AsyncSession, get, Cross-object search for the command palette. One GET returns grouped matches…, Column expression with Hebrew final letters folded — pairs with fold_hebrew()…, Short label for a list-row search hit: key-column value, else the first non-…, _row_label(), search() (+19 more)

### Community 58 - "services/racks.py"
Cohesion: 0.11
Nodes (30): apply_device_patch(), carrier_children(), CarrierError, _check_carrier_mount(), check_layout_change(), check_placement(), device_fields(), _faces_collide() (+22 more)

### Community 59 - "Rack"
Cohesion: 0.14
Nodes (28): _check_site(), create_rack_group(), delete_rack_group(), export_rack_group_xlsx(), _get_group(), get_rack_group(), list_rack_groups(), _ordered_racks() (+20 more)

### Community 60 - "vlans.py"
Cohesion: 0.16
Nodes (26): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+18 more)

### Community 61 - "UserRole"
Cohesion: 0.22
Nodes (26): str, UserRole, auth_on(), fake_arq(), login(), mkuser(), other_client(), AsyncClient (+18 more)

### Community 62 - "dependencies"
Cohesion: 0.07
Nodes (29): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, js-yaml, jszip, lucide-react (+21 more)

### Community 63 - "services/backup.py"
Cohesion: 0.12
Nodes (27): _alembic_revisions(), backup_filename(), BackupError, BackupPreview, BackupTable, build_backup(), _fail_inflight_scans(), _from_json() (+19 more)

### Community 64 - "group-client.tsx"
Cohesion: 0.16
Nodes (23): DragSession, errDetail(), findDevice(), GroupClient(), moveDevice(), metadata, slotRect, usedUSlots() (+15 more)

### Community 65 - "Smart import dialog"
Cohesion: 0.09
Nodes (28): GET /api/v1/devices/export.csv, GET /api/v1/devices/export.xlsx, POST /api/v1/devices/import, Carrier two-pass mounting, Changelog / audit history, CSV export, Dry-run preview with per-row {field:[old,new]} diffs, Export dropdown (Devices toolbar) (+20 more)

### Community 66 - "runtime_settings.py"
Cohesion: 0.12
Nodes (18): Any, psycopg2-style URL for alembic offline mode / scripts., Settings, Effective, _env_sourced(), Any, Runtime-editable settings: app_settings rows override env defaults. Each public…, True when the field's current value differs from its declared default. (+10 more)

### Community 67 - "traps.py"
Cohesion: 0.11
Nodes (22): _apply_link_state(), _clear_unmanaged_flag(), _decode(), ensure(), _flag_unmanaged(), handle_trap(), SNMP trap receiver (V8.1) — near-realtime link state. The poll lane…, (transportDomain, transportAddress) -> the sender's IP string. asyncio's UDP… (+14 more)

### Community 68 - "test_ipam_extras.py"
Cohesion: 0.16
Nodes (26): _prefix(), _range(), export.csv takes the same filters as the list endpoint — a filtered view…, Same filtered-export treatment on the prefixes CSV (F8)., A documented v6 /64's 2^64 host count must not reach dashboard sums (~1.8e19 >…, A deliberate bulk import documents existing reality — statics inside pools land…, test_address_role_nat_and_bulk(), test_addresses_export_respects_filters() (+18 more)

### Community 69 - "package.json"
Cohesion: 0.07
Nodes (25): name, private, version, autoprefixer, clsx, lz-string, postcss, @radix-ui/react-dropdown-menu (+17 more)

### Community 70 - "backend/requirements.txt"
Cohesion: 0.14
Nodes (23): alembic==1.14.0, arq==0.26.1, asyncpg==0.30.0, bcrypt==4.3.0, cryptography==50.0.1, fastapi==0.115.6, httpx==0.28.1, openpyxl==3.1.5 (+15 more)

### Community 71 - "v1/backup.py"
Cohesion: 0.14
Nodes (22): delete_scheduled_backup(), download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, delete, get, post (+14 more)

### Community 72 - "SNMP Enrichment Documentation"
Cohesion: 0.15
Nodes (23): arq==0.26.1, bcrypt==4.3.0, cryptography==50.0.1, fastapi==0.115.6, pysnmp==7.1.29, redis==5.2.0, scapy==2.6.1, sqlalchemy[asyncio]==2.0.36 (+15 more)

### Community 73 - "build-rack-library.mjs"
Cohesion: 0.13
Nodes (23): arrLen(), attribution(), CATEGORY_COLOUR, CURATED, fetchBuf(), fetchJson(), FRONTEND, FULL_IMPORT (+15 more)

### Community 74 - "tree-client.tsx"
Cohesion: 0.19
Nodes (19): metadata, ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), collectExpandableKeys(), flattenTree() (+11 more)

### Community 75 - "v1/settings.py"
Cohesion: 0.16
Nodes (20): _build_out(), _mask_url(), AsyncSession, get, Hide the password in a scheme://user:pass@host URL., read_settings(), update_settings(), ChangePasswordBody (+12 more)

### Community 76 - "ChangeLog"
Cohesion: 0.13
Nodes (19): AppSetting, Runtime-editable setting override. Absent row -> env var -> default., ChangeLog, NetBox-style audit trail: who changed what, when, and the field diff., fake_arq(), _pool(), _FakeArqJob, _FakePool (+11 more)

### Community 77 - "demo_rack_dc.py"
Cohesion: 0.13
Nodes (16): Api, apply(), _device_payload(), emit_zip(), find_one(), _KeepMethodRedirect, layout_doc(), main() (+8 more)

### Community 78 - "_wire_traps()"
Cohesion: 0.13
Nodes (20): _iface(), _link_binds(), An interface already learned by a poll — traps never create rows., Two devices, distinct communities — the community alone resolves., Same community on two devices — source IP decides., Credentialed device sending a wrong community is a config problem on the sender…, A real v2c datagram through the live listener: pysnmp decode -> sentinel…, Point the trap handler at the test DB and capture side effects. (+12 more)

### Community 79 - "maintenance.py"
Cohesion: 0.20
Nodes (20): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+12 more)

### Community 80 - "IpamBox README"
Cohesion: 0.18
Nodes (21): Changelog bypass for state writes, Add network wizard, Subnets doc, Gateway/DNS technical addresses, IP address, IP range (dhcp/pool/reserved), Subnet matrix, Pool override (force=1) (+13 more)

### Community 81 - "execute_plan()"
Cohesion: 0.17
Nodes (18): _apply_list(), commit_batch(), execute_plan(), rep(), _get_or_create_list(), _get_or_create_prefix(), _get_or_create_site(), _get_or_create_vlan() (+10 more)

### Community 82 - "test_colors.py"
Cohesion: 0.27
Nodes (19): _login(), _mk_rule(), _mk_site(), _mkuser(), AsyncClient, AsyncSession, Global row colors: manual row_color + rule-computed display_color. Covers the…, test_backup_roundtrips_color_rules() (+11 more)

### Community 83 - "Excel workbook import"
Cohesion: 0.16
Nodes (20): Demo CSV files, Fictional demo dataset, Demo import data README, Demo VLAN scheme, Network_Address_DEMO.xlsx, Network_Address_DEMO_EN.xlsx, backend/app/services/workbook parser, Asset (SW/HW inventory) (+12 more)

### Community 84 - "rack-editor.tsx"
Cohesion: 0.19
Nodes (18): DragSession, DropRow(), EditorBlock(), errDetail(), Pending, CarrierFrameSvg(), DeviceBlockSvg(), deviceImage() (+10 more)

### Community 85 - "test_ordering.py"
Cohesion: 0.28
Nodes (18): _circuit_order(), _login(), _mk_circuits(), _mkuser(), AsyncClient, AsyncSession, Global row ordering: POST /{entity}/reorder + pinned rows. Covered on both…, Reordering a subset keeps the slots those rows already had — rows outside the… (+10 more)

### Community 86 - "test_prefix_api.py"
Cohesion: 0.22
Nodes (18): _addrs(), _global_vrf_id(), _mkprefix(), Splits are counted arithmetically before materializing: anything over…, test_gateway_clear_removes_only_pristine_row(), test_gateway_never_clobbers_manual_row(), test_gateway_validation(), test_next_ip_never_hands_out_gateway() (+10 more)

### Community 87 - "Monitoring doc (V7)"
Cohesion: 0.23
Nodes (19): Check kinds (ping/tcp/http), Monitoring doc (V7), Event sources, Deliberate limits, Monitor target, Notification channel, Notification log, Secrets contract (+11 more)

### Community 88 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 89 - "listparse.py"
Cohesion: 0.13
Nodes (15): _cell_text(), _infer_type(), _ips(), _is_ip_token(), Custom-list extraction: turn any sheet into {columns, rows} for a list. Unlike…, Raw cell -> stored string. Dates iso-format; everything else cleans., (type, extra) for one column — extra carries options/multi., Row 0 of an unrecognized sheet looks like headers when every cell is a short… (+7 more)

### Community 90 - "_mklist()"
Cohesion: 0.18
Nodes (4): _mklist(), TestBulkRows, TestListCRUD, TestRows

### Community 91 - "docs.ts"
Cohesion: 0.19
Nodes (11): DocsIndexClient(), metadata, DocsNav(), BY_SLUG, DOC_ARTICLES, DOC_CATEGORIES, DocArticle, DocCategory (+3 more)

### Community 92 - "Device (first-class host entity)"
Cohesion: 0.22
Nodes (18): IPAddress, Cable, connected_interface_id (structured far-end port link), connected_ip (host-side NIC binding), DeviceInterface (device-owned port), L1 trace (cable path walk), match-free-text transition endpoint, One-cable-per-interface rule (+10 more)

### Community 93 - "users.py"
Cohesion: 0.23
Nodes (16): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+8 more)

### Community 94 - "network.py"
Cohesion: 0.20
Nodes (10): _ip(), NetworkCreate, NetworkDhcpRange, NetworkOut, NetworkPrefix, NetworkVlanNew, BaseModel, field_validator (+2 more)

### Community 95 - "test_ip_source.py"
Cohesion: 0.24
Nodes (16): may_write(), Field-ownership check for source-stamped rows (ip_addresses et al.). True when…, _mk_prefix(), V6 provenance — ip_addresses.source: stamping, ownership, filtering. Every…, Manual and imported rows keep their provenance when a scan sees them — observed…, Response bodies carry `source` but never any *_enc-style field., test_csv_import_stamps_import(), test_export_filters_and_carries_source() (+8 more)

### Community 96 - "parse_site_sheet()"
Cohesion: 0.17
Nodes (8): _blocks(), parse_site_sheet(), Split duplicated column groups (031-style runaway): each block starts at an…, MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf., Bare 'Name' (Cellular) maps to the hostname field., Non-empty unnamed columns pile into cf['extra'] instead of vanishing (Pelephone…, TestSiteSheetExtras, TestSiteSheetParser

### Community 97 - "test_workbook_import.py"
Cohesion: 0.14
Nodes (13): Workbook import: normalizer/parser unit tests (no DB) + API e2e., Small synthetic workbook: sites master + one site sheet + circuits., Site sheet documenting a DHCP span AND static stations inside it — the real…, Pool-guard regression: committing a plan whose dhcp range covers documented…, Commit-time PlanError must 422 AND record the failure. The route rolls back…, test_commit_plan_error_marks_batch_failed(), test_commit_twice_rejected(), test_import_e2e() (+5 more)

### Community 98 - "parse_sites_master()"
Cohesion: 0.17
Nodes (9): _master_blocks(), parse_sites_master(), (first, second) octet pairs a master row declares — lets sheet->site matching…, parse_sites_master_records(), Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins. (+1 more)

### Community 99 - "rack-collision.ts"
Cohesion: 0.25
Nodes (12): DeviceFormDialog(), RackEditor(), canMount(), canPlace(), conflicts(), facesCollide(), freeSlots(), rangesOverlap() (+4 more)

### Community 100 - "_FakeRedis"
Cohesion: 0.14
Nodes (6): _FakeRedis, In-memory get/set/publish stand-in for the worker's redis client., _cert_warnings emits cert.expiring once per cert per day — the Redis day-stamp…, A scan that raises mid-job flips to FAILED and emits scan.failed., test_cert_warning_emits_once_per_day(), test_scan_failed_emits()

### Community 101 - "test_allocation.py"
Cohesion: 0.23
Nodes (12): sf(), _mk_prefix(), test_address_crud_and_dup_guard(), test_allocation_skips_existing(), test_concurrent_allocation_unique(), alloc(), test_exhausted_prefix_conflicts(), test_sequential_allocation_skips_boundaries() (+4 more)

### Community 102 - "test_changelog.py"
Cohesion: 0.23
Nodes (12): AsyncClient, tag_assignments.object_id has no FK — deleting a tagged object must drop its…, Tag.assignments is already ORM delete-orphan — each removed assignment lands in…, PATCH settings with a null value deletes the app_settings row — that delete…, /addresses/bulk action=delete used to issue one Core DELETE — invisible to the…, test_bulk_delete_writes_changelog_entries(), test_changelog_captures_ip_status_change(), test_changelog_records_crud() (+4 more)

### Community 103 - "test_search.py"
Cohesion: 0.31
Nodes (12): AsyncClient, Global /api/v1/search endpoint (UX-3)., Regression: list_addresses ?q= used to crash on a missing column., Site + VRF + prefix + address + one of each workbook entity., _seed(), test_addresses_q_filter_not_broken(), test_search_empty_query(), test_search_grouped_results() (+4 more)

### Community 104 - "Rack device image library"
Cohesion: 0.23
Nodes (12): Demo .Rackula.zip racks, Air-gap safe bundling, CC0 1.0 Universal license, CC0 1.0 Universal, netbox-community/devicetype-library, Rack library ATTRIBUTION, netbox-community/devicetype-library, Rack device image library (+4 more)

### Community 105 - "test_auth.py"
Cohesion: 0.29
Nodes (11): AsyncClient, When the socket peer isn't in ipambox_trusted_proxies, a supplied XFF is…, Spreading failures across many usernames from one IP trips the aggregate lock —…, Five bad logins for one (user, ip) pair must not lock out other users on the…, test_endpoints_require_auth(), test_lockout_keyed_per_user_ip_pair(), test_login_lockout(), test_per_ip_aggregate_backstop() (+3 more)

### Community 106 - "test_scan_cidr_tcp_fallback_reports_found()"
Cohesion: 0.21
Nodes (8): on_hosts fires once per detection step with that chunk's new IPs — ARP batch…, When L2+L3 find nothing, the TCP fallback publishes its batch too., test_scan_cidr_emits_found_deltas(), fake_icmp(), fake_probe(), fake_ptr(), on_hosts(), test_scan_cidr_tcp_fallback_reports_found()

### Community 107 - "docs/[slug]/page.tsx"
Cohesion: 0.24
Nodes (9): DocPage(), dynamicParams, generateMetadata(), loadMarkdown(), DocsContent(), docCategoryLabel(), getDoc(), react-markdown (+1 more)

### Community 108 - "Racks"
Cohesion: 0.24
Nodes (12): Carrier (slot-layout device: shelves/trays), Elevation editor, Find free U, Health overlay, Linked asset and IP address, Rack placement rules, Printing and QR labels, Rack elevation (+4 more)

### Community 109 - "backup_dir()"
Cohesion: 0.29
Nodes (11): backup_dir(), delete_backup_file(), list_backup_files(), prune_backups(), Fetch a scheduled backup by file name (path-traversal safe)., Delete a scheduled backup by file name (path-traversal safe)., Delete oldest scheduled backups beyond the retention count., read_backup_file() (+3 more)

### Community 110 - "_FakePool"
Cohesion: 0.20
Nodes (8): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture, Stands in for the arq Redis pool — never actually dispatches work., scan_exclude_networks=10.70.0.64/26 inside scan_networks=10.70.0.0/24: the…, test_scheduler_and_route_share_exclusion_guard()

### Community 111 - "command-palette.tsx"
Cohesion: 0.31
Nodes (10): CommandPalette(), Icon, Item, itemsFor(), PAGES, pagesFor(), remember(), SearchOut (+2 more)

### Community 112 - "Device"
Cohesion: 0.22
Nodes (9): Trap -> the device that sent it. Community names the candidate set (devices…, _resolve_device(), Device, `context` is stored in the cred blob and feeds ContextData on v3 — agents that…, dot1d FDB + basePort→ifIndex map, plus a per-VLAN community pass., test_bridge_macs_parse_and_vlan_passes(), test_v3_context_field_roundtrips_and_reaches_transport(), test_walk_if_mib_parses_columns() (+1 more)

### Community 113 - "reader.py"
Cohesion: 0.29
Nodes (8): _csv_sheet(), load_workbook_bytes(), XLSX/CSV -> sheet matrices (openpyxl read_only streams / csv module)., Drop fully-empty trailing rows/cols for a stable matrix shape., One CSV file -> one SheetMatrix named after the file stem. utf-8-sig first…, Parse workbook bytes into per-sheet row matrices. read_only + data_only:…, SheetMatrix, _trim()

### Community 114 - "worker/monitors.py"
Cohesion: 0.31
Nodes (9): check_target(), _http(), _ping(), AsyncClient, Semaphore, The monitor lane — per-target health checks on the worker's minute cron.…, Single-host ICMP echo — blocking ping/raw socket in a worker thread. uvloop…, Run one check -> (ok, error). `client` lets the sweep share one AsyncClient… (+1 more)

### Community 116 - "devDependencies"
Cohesion: 0.20
Nodes (10): devDependencies, autoprefixer, postcss, sharp, tailwindcss, @types/js-yaml, @types/node, @types/react (+2 more)

### Community 117 - "Cabling doc"
Cohesion: 0.44
Nodes (9): connected_interface structured link, Cabling doc, Interface, L1 trace, POST /api/v1/interfaces/match-free-text, Patch panel as kind=patch device, Bulk port generation, Cabling & L1 trace (+1 more)

### Community 118 - "classify.py"
Cohesion: 0.36
Nodes (6): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…

### Community 119 - "check-rack-library.mjs"
Cohesion: 0.25
Nodes (6): DIR, FACES, LAYOUTS, problems, referenced, slugs

### Community 120 - "RackFace"
Cohesion: 0.39
Nodes (7): Placed, LibraryDevice, RACK_LIBRARY, ImportDevice, PreviewRow, RackFace, SlotLayout

### Community 121 - "_positional_columns()"
Cohesion: 0.29
Nodes (4): _col_class(), _positional_columns(), Dominant content class of a column sample., Headerless sheet: locate the IP column, then assign the remaining canonical…

### Community 122 - "_mkuser()"
Cohesion: 0.33
Nodes (7): _mkuser(), User, UserRole, _mkuser(), test_snmp_endpoints_require_write_perm(), User, UserRole

### Community 123 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, build:rack-library, check:rack-library, dev, lint, start

### Community 124 - "Devices"
Cohesion: 0.29
Nodes (7): API sketch, Device detail, Devices, Devices vs racks, From the IP drawer, Health rollup, The list

### Community 125 - "test_tick_batches_due_devices_into_one_job()"
Cohesion: 0.29
Nodes (4): snmp_enabled=0 -> snmp_tick is a no-op; nothing reaches the pool., test_global_kill_switch_enqueues_nothing(), _pool(), test_tick_batches_due_devices_into_one_job()

### Community 127 - "shortcuts.ts"
Cohesion: 0.53
Nodes (5): moveRowNav(), G_CHORDS, isEditableTarget(), modalOpen(), useGlobalShortcuts()

### Community 128 - "key()"
Cohesion: 0.40
Nodes (5): key(), fixture, fixture, key(), Provision a master key on the cached settings object.

### Community 129 - ".test_legacy_bezeq_layout()"
Cohesion: 0.40
Nodes (3): קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., TestCircuitsParser

### Community 130 - "Docs: IP Addresses"
Cohesion: 0.40
Nodes (5): Docs: IP Addresses, Docs: Devices, Docs: Racks, Docs: Settings, Docs: Subnets

### Community 131 - "use-chart-theme.ts"
Cohesion: 0.50
Nodes (4): ChartTheme, FALLBACK, readTheme(), useChartTheme()

### Community 132 - "Security Policy"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 133 - "_serialize_row()"
Cohesion: 0.67
Nodes (4): Any, Base, _serialize_row(), _to_json()

### Community 134 - "test_rbac_cabling()"
Cohesion: 0.67
Nodes (4): _login(), _mkuser(), AsyncSession, test_rbac_cabling()

### Community 135 - "test_snmp_test_endpoint()"
Cohesion: 0.67
Nodes (4): _test(), test_snmp_test_endpoint(), _test(), _up()

## Ambiguous Edges - Review These
- `Cable` → `Rack`  [AMBIGUOUS]
  frontend/src/content/docs/cabling.md · relation: conceptually_related_to
- `Stats strip & saved views` → `Monitoring doc (V7)`  [AMBIGUOUS]
  frontend/src/content/docs/inventory.md · relation: semantically_similar_to

## Knowledge Gaps
- **373 isolated node(s):** `BulkResp`, `Draft`, `FeatureDef`, `Key`, `Key` (+368 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1531 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Cable` and `Rack`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Stats strip & saved views` and `Monitoring doc (V7)`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._
- **Why does `LinkedRef` connect `devices.py` to `index.ts`?**
  _High betweenness centrality (0.183) - this node is a cross-community bridge._
- **Why does `_detail()` connect `devices.py` to `Site`, `v1/racks.py`, `ip_display()`, `Device`, `Base`, `Rack`?**
  _High betweenness centrality (0.120) - this node is a cross-community bridge._
- **Why does `js-yaml` connect `build-rack-library.mjs` to `rackula.ts`, `package.json`?**
  _High betweenness centrality (0.116) - this node is a cross-community bridge._
- **Are the 69 inferred relationships involving `Device` (e.g. with `_filtered_devices()` and `_export_rows()`) actually correct?**
  _`Device` has 69 INFERRED edges - model-reasoned connections that need verification._
- **Are the 72 inferred relationships involving `IPAMError` (e.g. with `_get_interface()` and `_get_cable()`) actually correct?**
  _`IPAMError` has 72 INFERRED edges - model-reasoned connections that need verification._