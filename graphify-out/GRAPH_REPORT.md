# Graph Report - IpamBox  (2026-09-26)

## Corpus Check
- 0 files · ~99,999 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 4819 nodes · 15609 edges · 205 communities (141 shown, 27 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 1194 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- react
- devices-client.tsx
- devices.py
- lucide-react
- test_snmp.py
- index.ts
- Base
- index.ts
- v1/racks.py
- app-shell.tsx
- rack_io.py
- cn()
- test_snmp.py
- scans.py
- DeviceInterface
- prefixes.py
- useAsyncData()
- User
- Rack
- test_monitors.py
- addresses.py
- IPAMError
- get_settings()
- Device
- test_racks.py
- color_rules.py
- useAsyncData()
- test_scanner.py
- _Planner
- generate_demo_data.py
- entities.py
- test_cabling.py
- _mklist()
- test_devices.py
- test_rack_io.py
- v1/monitors.py
- run_scan()
- worker.py
- test_secrets.py
- test_snmp.py
- traps.py
- route-error.tsx
- IPStatus
- _split_dsn()
- vlans.py
- test_device_io.py
- services/racks.py
- rackula.ts
- NotificationChannel
- test_backup.py
- prefixes.py
- ip_display()
- scanner.py
- test_review.py
- _matrix()
- demo_rack_dc.py
- v1/search.py
- tags.py
- clean()
- ip_display()
- channels.py
- dependencies
- imports.py
- test_ipam_extras.py
- package.json
- Monitoring doc (V7)
- runtime_settings.py
- users.py
- backend/requirements.txt
- rack-collision.ts
- UserRole
- SNMP Enrichment Documentation
- build-rack-library.mjs
- clean()
- Device (first-class host entity)
- maintenance.py
- channels.py
- ChangeLog
- group-client.tsx
- _wire_traps()
- execute_plan()
- test_colors.py
- IpamBox
- test_review.py
- run_scan()
- test_ordering.py
- test_prefix_api.py
- Excel workbook import
- compilerOptions
- docs.ts
- test_tick_batches_due_devices_into_one_job()
- v1/backup.py
- test_lists.py
- network.py
- test_ip_source.py
- parse_site_sheet()
- services/backup.py
- Smart import dialog
- backup_dir()
- test_workbook_import.py
- rack-editor.tsx
- reader.py
- parse_sites_master()
- IpamBox
- IPAddress
- test_changelog.py
- test_search.py
- Rack device image library
- worker/monitors.py
- test_auth.py
- test_scan_cidr_tcp_fallback_reports_found()
- Racks
- docs/[slug]/page.tsx
- _FakePool
- IpamBox README
- TestNormalize
- devDependencies
- IpamBox
- Smart import dialog
- ip_display()
- services/backup.py
- imports.py
- _mkuser()
- generate_demo_data.py
- services/backup.py
- ip_display()
- .test_legacy_bezeq_layout()
- test_monitors.py
- IpamBox
- check-rack-library.mjs
- IpamBox
- User
- _positional_columns()
- IPStatus
- scripts
- Devices
- classify.py
- test_entities.py
- get_settings()
- key()
- Docs: IP Addresses
- use-chart-theme.ts
- Security Policy
- scanner.py
- test_racks.py
- test_racks.py
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
- `Export dropdown (Devices toolbar)` --semantically_similar_to--> `Device smart file I/O (export dropdown + smart import)`  [INFERRED] [semantically similar]
  frontend/src/content/docs/devices.md → README.md
- `Smart import dialog` --semantically_similar_to--> `Excel workbook import (per-sheet detection, dry-run, all-or-nothing/partial commit)`  [INFERRED] [semantically similar]
  frontend/src/content/docs/devices.md → README.md
- `Stats strip & saved views` --semantically_similar_to--> `Monitoring doc (V7)`  [AMBIGUOUS] [semantically similar]
  frontend/src/content/docs/inventory.md → frontend/src/content/docs/monitoring.md
- `Live IP column resolution` --semantically_similar_to--> `Discovery Inbox reconciliation`  [INFERRED] [semantically similar]
  frontend/src/content/docs/lists.md → README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **SNMP Poll Flow** — frontend_src_content_docs_snmp_md_poll_pipeline, frontend_src_content_docs_snmp_md_if_mib_upsert, frontend_src_content_docs_snmp_md_bridge_mac_resolution, frontend_src_content_docs_snmp_md_lldp_collection [EXTRACTED 1.00]
- **Backend Dependencies Enabling SNMP Enrichment** — backend_requirements_txt_pysnmp, backend_requirements_txt_cryptography, backend_requirements_txt_arq [INFERRED 0.65]
- **Non-Destructive Enrichment Contract** — frontend_src_content_docs_snmp_md_read_only_polling, frontend_src_content_docs_snmp_md_may_write_provenance, frontend_src_content_docs_snmp_md_stale_dimming [INFERRED 0.85]

## Communities (205 total, 27 thin omitted)

### Community 0 - "react"
Cohesion: 0.02
Nodes (50): nextConfig, metadata, metadata, metadata, metadata, metadata, metadata, metadata (+42 more)

### Community 1 - "devices-client.tsx"
Cohesion: 0.09
Nodes (90): CertificatesPage(), EMPTY, CircuitsPage(), EMPTY, DEVICE_VIEWS, DeviceRow, DevicesPage(), EMPTY (+82 more)

### Community 2 - "devices.py"
Cohesion: 0.04
Nodes (104): _asset_ref(), _check_iface_refs(), _check_refs(), create_device(), create_interface(), delete_device(), delete_interface(), _detail() (+96 more)

### Community 3 - "lucide-react"
Cohesion: 0.07
Nodes (63): ACTION_STYLES, CABLE_REASON, BulkResp, DragSession, CABLE_REASON, DELETE_PATH, DeleteTarget, DismissTarget (+55 more)

### Community 4 - "test_snmp.py"
Cohesion: 0.08
Nodes (91): emit_new_flags(), _auth(), _context(), _cred(), due_device_ids(), _get(), _idx_int(), _idx_tail_ints() (+83 more)

### Community 5 - "index.ts"
Cohesion: 0.08
Nodes (65): EMPTY_EDIT, FACE_BADGE, ImportListDialog(), IPAM_FAMILIES, Step, PrefixRow, Draft, ENTITIES (+57 more)

### Community 6 - "Base"
Cohesion: 0.07
Nodes (57): POST /networks — the "add network" wizard endpoint (V6.1). One call creates or…, _cascade_site_fields(), Propagate site code/number/name changes to linked entities that were following…, after_flush(), before_flush(), SyncSession, tag_assignments garbage collection. TagAssignment references its target…, register() (+49 more)

### Community 7 - "index.ts"
Cohesion: 0.03
Nodes (85): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, PreviewResp, SheetResults(), Step (+77 more)

### Community 8 - "v1/racks.py"
Cohesion: 0.06
Nodes (82): _rack_detail(), Rack -> RackDetail with its (selectin-loaded) devices serialized, each carrying…, _check_refs(), create_device(), create_rack(), delete_device(), delete_rack(), _device_out() (+74 more)

### Community 9 - "app-shell.tsx"
Cohesion: 0.04
Nodes (76): metadata, viewport, AppearancePage(), metadata, AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT (+68 more)

### Community 10 - "rack_io.py"
Cohesion: 0.05
Nodes (73): import_racks(), Request, Smart rack/group bundle import — V5B's stateless flow for whole trees. Sheets…, RackGroup, A bayed row: racks ordered left-to-right as they stand in the DC., _alias_to_field(), apply_mapping_overrides(), auto_map_fields() (+65 more)

### Community 11 - "cn()"
Cohesion: 0.05
Nodes (67): IpCell(), SortableColRow(), IP_ROLES, IP_STATUSES, RANGE_ROLES, SplitDialog(), SplitPlan, toggleIn() (+59 more)

### Community 12 - "test_snmp.py"
Cohesion: 0.09
Nodes (64): _apply_link_state(), _clear_unmanaged_flag(), _decode(), ensure(), _flag_unmanaged(), handle_trap(), datetime, _resolve_device() (+56 more)

### Community 13 - "scans.py"
Cohesion: 0.05
Nodes (55): do_run_migrations(), run_migrations_online(), list_changelog(), AsyncSession, get, _check_range_overlap(), create_range(), delete_range() (+47 more)

### Community 14 - "DeviceInterface"
Cohesion: 0.07
Nodes (68): _cable_out(), _check_ends(), create_cable(), delete_cable(), _get_cable(), _get_interface(), interfaces_match_free_text(), list_cables() (+60 more)

### Community 15 - "prefixes.py"
Cohesion: 0.07
Nodes (63): allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), _prefix_rows() (+55 more)

### Community 16 - "useAsyncData()"
Cohesion: 0.06
Nodes (59): PrefixDetailPage(), metadata, ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), DEVICE_FILTER_PARAMS (+51 more)

### Community 17 - "User"
Cohesion: 0.07
Nodes (63): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+55 more)

### Community 18 - "Rack"
Cohesion: 0.06
Nodes (59): delete_address(), delete, _crud_router(), create_item(), delete_item(), get_item(), update_item(), _check_site() (+51 more)

### Community 19 - "test_monitors.py"
Cohesion: 0.05
Nodes (42): _FakeArqPool, _FakeRedis, _Job, _login(), _mk_device(), _mk_prefix_and_addr(), _mkuser(), V7 monitoring + notification channels. Covers target CRUD/RBAC, the exactly-… (+34 more)

### Community 20 - "addresses.py"
Cohesion: 0.06
Nodes (60): _address_csv_row(), _addresses_stmt(), bulk_addresses(), BulkBody, _check_interface_link(), create_address(), export_addresses(), get_address() (+52 more)

### Community 21 - "IPAMError"
Cohesion: 0.08
Nodes (56): reorder_items(), bulk_rows(), _check_columns(), create_list(), create_row(), delete_list(), delete_row(), get_list() (+48 more)

### Community 22 - "get_settings()"
Cohesion: 0.05
Nodes (56): get_settings(), close_arq_pool(), close_redis(), get_redis(), Shared process-wide Redis client. Do NOT aclose() it per call — connections…, Shut down the shared client — lifespan/worker shutdown only., _trusted_nets(), lifespan() (+48 more)

### Community 23 - "Device"
Cohesion: 0.08
Nodes (53): Device, Base, ip_display(), Any, Normalize asyncpg-returned ipaddress objects / strings to display form. INET…, to_int(), _carrier_diff_name(), _err() (+45 more)

### Community 24 - "test_racks.py"
Cohesion: 0.12
Nodes (55): _carrier(), _dev(), _group(), _imports(), _mount(), _next_free(), AsyncClient, _rack() (+47 more)

### Community 25 - "color_rules.py"
Cohesion: 0.07
Nodes (46): create_rule(), delete_rule(), get_rule(), list_rules(), preview_rule(), AsyncSession, delete, get (+38 more)

### Community 26 - "useAsyncData()"
Cohesion: 0.07
Nodes (47): ACTION_STYLES, ChangelogPage(), DashboardPage(), DeviceDetailClient(), DiscoveryPage(), ImportPage(), ListsClient(), MonitoringPage() (+39 more)

### Community 27 - "test_scanner.py"
Cohesion: 0.08
Nodes (48): _flag(), Any, AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), HostResult, _global_vrf_id(), _infer_scan_vrf() (+40 more)

### Community 28 - "_Planner"
Cohesion: 0.09
Nodes (17): parse_sites_master_records(), _Planner, (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Folded sheet title vs site name/code — word-boundary matching so 'int' doesn't…, Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new…, Resolve a 10.{second}.x sheet — site_number is only meaningful inside the… (+9 more)

### Community 29 - "generate_demo_data.py"
Cohesion: 0.09
Nodes (49): assets_rows(), _assign_site_sheets(), _assign_site_sheets_clean(), build_en_workbook(), build_mixed_workbook(), build_sites(), certificates_rows(), circuits_rows() (+41 more)

### Community 30 - "entities.py"
Cohesion: 0.08
Nodes (31): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, AssetKind, str, AssetCreate, AssetOut, AssetUpdate, BaseModel, field_validator (+23 more)

### Community 31 - "test_cabling.py"
Cohesion: 0.13
Nodes (46): _backup_bytes(), _cable(), _device(), _gen(), _iface(), _ip(), _login(), _mkuser() (+38 more)

### Community 32 - "_mklist()"
Cohesion: 0.08
Nodes (25): _cell_text(), extract_list_table(), _infer_type(), _ips(), _is_ip_token(), pick_key_column(), Custom-list extraction: turn any sheet into {columns, rows} for a list. Unlike…, SheetMatrix -> (column defs, row dicts). columns: [{key, label, type, options?,… (+17 more)

### Community 33 - "test_devices.py"
Cohesion: 0.13
Nodes (39): _cable(), _device(), _group(), _iface(), _ip(), _login(), _mkuser(), _prefix() (+31 more)

### Community 34 - "test_rack_io.py"
Cohesion: 0.16
Nodes (42): _bundle(), _by_sheet(), _cable(), _csv(), _device(), _group(), _iface(), _import() (+34 more)

### Community 35 - "v1/monitors.py"
Cohesion: 0.10
Nodes (39): check_now(), _check_refs(), create_target(), delete_target(), _filters(), _get(), get_target(), list_targets() (+31 more)

### Community 36 - "run_scan()"
Cohesion: 0.08
Nodes (34): _job_payload(), str, ScanJob, ScanStatus, _api_cancel(), _FakeRedis, _mk_job(), In-memory stand-in for the worker's redis client (get/set/publish). (+26 more)

### Community 37 - "worker.py"
Cohesion: 0.09
Nodes (38): _lan_info(), LAN identity detected by the host-networked worker (written to Redis). Falls…, set_actor(), Effective, get_effective(), AsyncSession, monitor_tick(), ARQ job: check a batch of targets, write states, emit on flips. (+30 more)

### Community 38 - "test_secrets.py"
Cohesion: 0.09
Nodes (36): _data_key(), decrypt_str(), encrypt_str(), _master_key(), Exception, Secrets at rest — the credential contract v7/v8/v12/v14 build on. A single…, Unseal a "v1:…" blob. Strict prefix check — unknown formats, malformed payloads…, Base for secrets-service failures — never carries secret material. (+28 more)

### Community 39 - "test_snmp.py"
Cohesion: 0.16
Nodes (37): AsyncClient, _device(), _down(), _enable(), _ifrow(), _ip(), _mock_poll(), _orm_device() (+29 more)

### Community 40 - "traps.py"
Cohesion: 0.07
Nodes (32): _apply_link_state(), _clear_unmanaged_flag(), _decode(), ensure(), _flag_unmanaged(), handle_trap(), SNMP trap receiver (V8.1) — near-realtime link state. The poll lane…, (transportDomain, transportAddress) -> the sender's IP string. asyncio's UDP… (+24 more)

### Community 42 - "IPStatus"
Cohesion: 0.09
Nodes (21): field_validator, _strip_name(), field_validator, _norm_mac(), field_validator, _disproved(), _evaluate(), flag_fingerprint() (+13 more)

### Community 43 - "_split_dsn()"
Cohesion: 0.10
Nodes (27): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., sf() (+19 more)

### Community 44 - "vlans.py"
Cohesion: 0.13
Nodes (32): list_items(), _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans() (+24 more)

### Community 45 - "test_device_io.py"
Cohesion: 0.20
Nodes (34): _csv(), _device(), _group(), _import(), _ip(), _login(), _mkuser(), _prefix() (+26 more)

### Community 46 - "services/racks.py"
Cohesion: 0.10
Nodes (32): apply_device_import(), Write the ok rows in one transaction. Creates go through the create path's…, apply_device_patch(), carrier_children(), CarrierError, _check_carrier_mount(), check_layout_change(), check_placement() (+24 more)

### Community 47 - "rackula.ts"
Cohesion: 0.09
Nodes (34): ABBREV_TO_CATEGORY, canonicalCategory(), CATEGORY_TO_ABBREV, clip(), compareVersions(), decodeShareUrl(), DeviceLike, deviceTypeTables() (+26 more)

### Community 48 - "NotificationChannel"
Cohesion: 0.11
Nodes (30): NotificationChannel, NotificationLog, Base, Outbound sink. ``config`` holds non-secret fields per kind; ``secret_enc`` is…, Append-only delivery attempt log — swept by ``notify_retention_days``., _deliver(), _DeliveryFailed, emit() (+22 more)

### Community 49 - "test_backup.py"
Cohesion: 0.16
Nodes (33): User, _backup_bytes(), _envelope_bytes(), _mkusers(), Hand-craft a backup envelope (e.g. with a forged users table)., Guard: every ORM table must be backed up (or explicitly excluded). Adding a new…, Fresh-server scenario: the migration-seeded Global VRF is replaced by the…, Fresh-server scenario: the target's admins survive; its non-admin set is fully… (+25 more)

### Community 50 - "prefixes.py"
Cohesion: 0.11
Nodes (31): NotFoundError, prefix_stats_dict(), IPAddress, Atomically allocate the lowest free usable IP in a prefix. SERIALIZES on the…, Stats payload for one prefix given its address count (no DB access). IPv6…, reserve_next_available(), children(), lowest_free() (+23 more)

### Community 51 - "ip_display()"
Cohesion: 0.15
Nodes (32): _aging_discovery_items(), build_review(), _cable_mismatch_items(), _cert_items(), dismiss(), _dismissal_map(), _dup_mac_items(), _emit() (+24 more)

### Community 52 - "scanner.py"
Cohesion: 0.09
Nodes (29): _arp_scan(), _host_chunks(), _icmp_checksum(), _icmp_echo_packet(), _icmp_socket(), _icmp_sweep(), _icmp_sweep_blocking(), infer_device_type() (+21 more)

### Community 53 - "test_review.py"
Cohesion: 0.23
Nodes (32): _device(), _flag_mismatch(), _iface(), _ip(), _login(), _prefix(), AsyncClient, AsyncSession (+24 more)

### Community 54 - "_matrix()"
Cohesion: 0.15
Nodes (14): _master_row(), _matrix(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind… (+6 more)

### Community 55 - "demo_rack_dc.py"
Cohesion: 0.11
Nodes (25): Api, apply(), _device_payload(), emit_zip(), find_one(), _KeepMethodRedirect, layout_doc(), main() (+17 more)

### Community 56 - "v1/search.py"
Cohesion: 0.17
Nodes (27): _folded(), AsyncSession, get, Cross-object search for the command palette. One GET returns grouped matches…, Column expression with Hebrew final letters folded — pairs with fold_hebrew()…, Short label for a list-row search hit: key-column value, else the first non-…, _row_label(), search() (+19 more)

### Community 57 - "tags.py"
Cohesion: 0.15
Nodes (23): assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession, delete (+15 more)

### Community 58 - "clean()"
Cohesion: 0.11
Nodes (27): assemble_ip(), clean(), _clean_octets(), map_status(), mask_to_prefixlen(), network_of(), parse_range_end(), parse_vlan() (+19 more)

### Community 59 - "ip_display()"
Cohesion: 0.12
Nodes (27): dismiss_item(), _flagged_address(), get_review(), mac_mismatch_accept(), mac_mismatch_keep(), AsyncSession, get, IPAddress (+19 more)

### Community 60 - "channels.py"
Cohesion: 0.13
Nodes (25): ChannelKind, MonitorKind, MonitorState, V7 — continuous monitoring targets + outbound notification channels., ChannelCreate, ChannelOut, ChannelTestOut, ChannelUpdate (+17 more)

### Community 61 - "dependencies"
Cohesion: 0.07
Nodes (29): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, js-yaml, jszip, lucide-react (+21 more)

### Community 62 - "imports.py"
Cohesion: 0.13
Nodes (26): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+18 more)

### Community 63 - "test_ipam_extras.py"
Cohesion: 0.16
Nodes (26): _prefix(), _range(), export.csv takes the same filters as the list endpoint — a filtered view…, Same filtered-export treatment on the prefixes CSV (F8)., A documented v6 /64's 2^64 host count must not reach dashboard sums (~1.8e19 >…, A deliberate bulk import documents existing reality — statics inside pools land…, test_address_role_nat_and_bulk(), test_addresses_export_respects_filters() (+18 more)

### Community 64 - "package.json"
Cohesion: 0.07
Nodes (25): name, private, version, autoprefixer, clsx, jszip, postcss, @radix-ui/react-dropdown-menu (+17 more)

### Community 65 - "Monitoring doc (V7)"
Cohesion: 0.15
Nodes (27): Changelog bypass for state writes, Check kinds (ping/tcp/http), Monitoring doc (V7), Event sources, Deliberate limits, Monitor target, Notification channel, Notification log (+19 more)

### Community 66 - "runtime_settings.py"
Cohesion: 0.12
Nodes (17): Any, psycopg2-style URL for alembic offline mode / scripts., Settings, _env_sourced(), Any, Runtime-editable settings: app_settings rows override env defaults. Each public…, True when the field's current value differs from its declared default., One runtime-editable setting. field: the env-backed attribute on… (+9 more)

### Community 67 - "users.py"
Cohesion: 0.14
Nodes (24): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+16 more)

### Community 68 - "backend/requirements.txt"
Cohesion: 0.14
Nodes (23): alembic==1.14.0, arq==0.26.1, asyncpg==0.30.0, bcrypt==4.3.0, cryptography==50.0.1, fastapi==0.115.6, httpx==0.28.1, openpyxl==3.1.5 (+15 more)

### Community 69 - "rack-collision.ts"
Cohesion: 0.15
Nodes (21): DragSession, DropRow(), EditorBlock(), errDetail(), Pending, RackEditor(), CarrierFrameSvg(), DeviceBlockSvg() (+13 more)

### Community 70 - "UserRole"
Cohesion: 0.32
Nodes (22): str, UserRole, login(), mkuser(), other_client(), AsyncClient, AsyncSession, allow_insecure keeps full access (existing behavior preserved). (+14 more)

### Community 71 - "SNMP Enrichment Documentation"
Cohesion: 0.15
Nodes (23): arq==0.26.1, bcrypt==4.3.0, cryptography==50.0.1, fastapi==0.115.6, pysnmp==7.1.29, redis==5.2.0, scapy==2.6.1, sqlalchemy[asyncio]==2.0.36 (+15 more)

### Community 72 - "build-rack-library.mjs"
Cohesion: 0.13
Nodes (23): arrLen(), attribution(), CATEGORY_COLOUR, CURATED, fetchBuf(), fetchJson(), FRONTEND, FULL_IMPORT (+15 more)

### Community 73 - "clean()"
Cohesion: 0.11
Nodes (19): excel_date(), norm_header(), date, datetime/date passthrough; int/float serial (20000-80000) -> date; 'd/m/yy'…, Header cell -> lowercase, single-spaced, for signature matching. Edge…, _is_header_echo(), _leftover_bits(), _map_columns() (+11 more)

### Community 74 - "Device (first-class host entity)"
Cohesion: 0.16
Nodes (23): IPAddress, Cable, connected_interface_id (structured far-end port link), connected_ip (host-side NIC binding), DeviceInterface (device-owned port), L1 trace (cable path walk), match-free-text transition endpoint, One-cable-per-interface rule (+15 more)

### Community 75 - "maintenance.py"
Cohesion: 0.19
Nodes (21): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+13 more)

### Community 76 - "channels.py"
Cohesion: 0.20
Nodes (20): _config_fields(), create_channel(), delete_channel(), _get(), get_channel(), list_channels(), notification_log(), _out() (+12 more)

### Community 77 - "ChangeLog"
Cohesion: 0.14
Nodes (17): AppSetting, Runtime-editable setting override. Absent row -> env var -> default., fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture (+9 more)

### Community 78 - "group-client.tsx"
Cohesion: 0.19
Nodes (19): errDetail(), findDevice(), GroupClient(), moveDevice(), RackDetailPage(), RackGeom, slotRect, freeByRack() (+11 more)

### Community 79 - "_wire_traps()"
Cohesion: 0.14
Nodes (18): _iface(), _link_binds(), An interface already learned by a poll — traps never create rows., Two devices, distinct communities — the community alone resolves., Same community on two devices — source IP decides., Credentialed device sending a wrong community is a config problem on the sender…, A real v2c datagram through the live listener: pysnmp decode -> sentinel…, Point the trap handler at the test DB and capture side effects. (+10 more)

### Community 80 - "execute_plan()"
Cohesion: 0.17
Nodes (18): _apply_list(), commit_batch(), execute_plan(), rep(), _get_or_create_list(), _get_or_create_prefix(), _get_or_create_site(), _get_or_create_vlan() (+10 more)

### Community 81 - "test_colors.py"
Cohesion: 0.27
Nodes (19): _login(), _mk_rule(), _mk_site(), _mkuser(), AsyncClient, AsyncSession, Global row colors: manual row_color + rule-computed display_color. Covers the…, test_backup_roundtrips_color_rules() (+11 more)

### Community 82 - "IpamBox"
Cohesion: 0.32
Nodes (20): Circuits (WAN circuit register), Hierarchy Tree, Roll-up utilization, Site → VRF → Prefix → IP address data model, IpamBox, Row Colors, Command palette, Services (service catalog) (+12 more)

### Community 83 - "test_review.py"
Cohesion: 0.18
Nodes (15): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), Audit trail via session flush hooks. before_flush collects (object, action,…, register(), _repr() (+7 more)

### Community 84 - "run_scan()"
Cohesion: 0.13
Nodes (17): exclusion_hit(), Scan-target policy shared by the API route, the scheduler, and the worker.…, Return the first excluded CIDR overlapping ``net`` (either direction), or None.…, Exception, Raised inside the pipeline when the user cancels the scan., ScanCancelled, _job_status(), _publish() (+9 more)

### Community 85 - "test_ordering.py"
Cohesion: 0.28
Nodes (18): _circuit_order(), _login(), _mk_circuits(), _mkuser(), AsyncClient, AsyncSession, Global row ordering: POST /{entity}/reorder + pinned rows. Covered on both…, Reordering a subset keeps the slots those rows already had — rows outside the… (+10 more)

### Community 86 - "test_prefix_api.py"
Cohesion: 0.22
Nodes (18): _addrs(), _global_vrf_id(), _mkprefix(), Splits are counted arithmetically before materializing: anything over…, test_gateway_clear_removes_only_pristine_row(), test_gateway_never_clobbers_manual_row(), test_gateway_validation(), test_next_ip_never_hands_out_gateway() (+10 more)

### Community 87 - "Excel workbook import"
Cohesion: 0.17
Nodes (19): Demo CSV files, Fictional demo dataset, Demo import data README, Demo VLAN scheme, Network_Address_DEMO.xlsx, Network_Address_DEMO_EN.xlsx, backend/app/services/workbook parser, Asset (SW/HW inventory) (+11 more)

### Community 88 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 89 - "docs.ts"
Cohesion: 0.19
Nodes (11): DocsIndexClient(), metadata, DocsNav(), BY_SLUG, DOC_ARTICLES, DOC_CATEGORIES, DocArticle, DocCategory (+3 more)

### Community 90 - "test_tick_batches_due_devices_into_one_job()"
Cohesion: 0.13
Nodes (14): _test(), V8 SNMP enrichment — write-only creds, IF-MIB upsert, bridge-MAC links, manual-…, The opt-in socket: ensure(False) is a clean no-op, ensure(True, 0) binds an…, A port that's already taken must fail cleanly — one log, no loop., snmp_enabled=0 -> snmp_tick is a no-op; nothing reaches the pool., test_enable_requires_version_and_cred(), test_global_kill_switch_enqueues_nothing(), _pool() (+6 more)

### Community 91 - "v1/backup.py"
Cohesion: 0.17
Nodes (16): download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, get, post, Request, Restore a backup file (raw .json.gz body). Wipes every data table (users are… (+8 more)

### Community 92 - "test_lists.py"
Cohesion: 0.21
Nodes (9): ListTarget, PreviewOptions, Import a sheet as a custom list (user-selected or suggested)., User-confirmed mapping choices applied before building the plan., _matrix(), _preview_of(), also_ipam=False: a servers sheet produces ONLY list rows — no addresses or…, TestExtract (+1 more)

### Community 93 - "network.py"
Cohesion: 0.20
Nodes (10): _ip(), NetworkCreate, NetworkDhcpRange, NetworkOut, NetworkPrefix, NetworkVlanNew, BaseModel, field_validator (+2 more)

### Community 94 - "test_ip_source.py"
Cohesion: 0.24
Nodes (16): may_write(), Field-ownership check for source-stamped rows (ip_addresses et al.). True when…, _mk_prefix(), V6 provenance — ip_addresses.source: stamping, ownership, filtering. Every…, Manual and imported rows keep their provenance when a scan sees them — observed…, Response bodies carry `source` but never any *_enc-style field., test_csv_import_stamps_import(), test_export_filters_and_carries_source() (+8 more)

### Community 95 - "parse_site_sheet()"
Cohesion: 0.17
Nodes (8): _blocks(), parse_site_sheet(), Split duplicated column groups (031-style runaway): each block starts at an…, MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf., Bare 'Name' (Cellular) maps to the hostname field., Non-empty unnamed columns pile into cf['extra'] instead of vanishing (Pelephone…, TestSiteSheetExtras, TestSiteSheetParser

### Community 96 - "services/backup.py"
Cohesion: 0.17
Nodes (15): backup_filename(), BackupError, BackupPreview, BackupTable, _fail_inflight_scans(), _gunzip(), _has_serial_id(), inspect_backup() (+7 more)

### Community 97 - "Smart import dialog"
Cohesion: 0.17
Nodes (16): POST /api/v1/devices/import, Carrier two-pass mounting, Changelog / audit history, Dry-run preview with per-row {field:[old,new]} diffs, force commit mode (valid rows only), Header auto-mapping (English/Hebrew/NetBox), Match precedence: id → serial_number → mac_address → name+site, NetBox header aliases (device_role→device type, device_type→model, position→U) (+8 more)

### Community 98 - "backup_dir()"
Cohesion: 0.20
Nodes (15): delete_scheduled_backup(), delete, backup_dir(), delete_backup_file(), list_backup_files(), prune_backups(), Fetch a scheduled backup by file name (path-traversal safe)., Delete a scheduled backup by file name (path-traversal safe). (+7 more)

### Community 99 - "test_workbook_import.py"
Cohesion: 0.16
Nodes (11): Workbook import: normalizer/parser unit tests (no DB) + API e2e., Small synthetic workbook: sites master + one site sheet + circuits., Site sheet documenting a DHCP span AND static stations inside it — the real…, Pool-guard regression: committing a plan whose dhcp range covers documented…, test_commit_twice_rejected(), test_import_e2e(), test_workbook_statics_inside_dhcp_span_import_marked(), TestAssetsParser (+3 more)

### Community 100 - "rack-editor.tsx"
Cohesion: 0.27
Nodes (13): deviceImage(), FACE_BADGE, RackElevation(), usedUSlots(), useLibraryBySlug(), Placed, libraryBySlug(), LibraryDevice (+5 more)

### Community 101 - "reader.py"
Cohesion: 0.24
Nodes (11): Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, _csv_sheet(), load_upload(), load_workbook_bytes(), XLSX/CSV -> sheet matrices (openpyxl read_only streams / csv module)., Drop fully-empty trailing rows/cols for a stable matrix shape., One CSV file -> one SheetMatrix named after the file stem. utf-8-sig first…, Dispatch on container type: ZIP -> xlsx workbook; otherwise try CSV text… (+3 more)

### Community 102 - "parse_sites_master()"
Cohesion: 0.19
Nodes (8): _master_blocks(), parse_sites_master(), (first, second) octet pairs a master row declares — lets sheet->site matching…, Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins., TestSitesMasterParser

### Community 103 - "IpamBox"
Cohesion: 0.29
Nodes (14): Address roles (vip/vrrp/hsrp/glbp/carp/secondary), Address CSV import/export, IP Addresses, IP drawer, mac_mismatch flag, Changelog, Per-object history, Discovery Inbox (+6 more)

### Community 104 - "IPAddress"
Cohesion: 0.24
Nodes (8): IPRangeRole, str, IPRangeCreate, IPRangeOut, IPRangeUpdate, BaseModel, field_validator, model_validator

### Community 105 - "test_changelog.py"
Cohesion: 0.23
Nodes (12): AsyncClient, tag_assignments.object_id has no FK — deleting a tagged object must drop its…, Tag.assignments is already ORM delete-orphan — each removed assignment lands in…, PATCH settings with a null value deletes the app_settings row — that delete…, /addresses/bulk action=delete used to issue one Core DELETE — invisible to the…, test_bulk_delete_writes_changelog_entries(), test_changelog_captures_ip_status_change(), test_changelog_records_crud() (+4 more)

### Community 106 - "test_search.py"
Cohesion: 0.31
Nodes (12): AsyncClient, Global /api/v1/search endpoint (UX-3)., Regression: list_addresses ?q= used to crash on a missing column., Site + VRF + prefix + address + one of each workbook entity., _seed(), test_addresses_q_filter_not_broken(), test_search_empty_query(), test_search_grouped_results() (+4 more)

### Community 107 - "Rack device image library"
Cohesion: 0.22
Nodes (12): Demo .Rackula.zip racks, Air-gap safe bundling, CC0 1.0 Universal license, CC0 1.0 Universal, netbox-community/devicetype-library, Rack library ATTRIBUTION, Rack device image library, IpamBox (+4 more)

### Community 108 - "worker/monitors.py"
Cohesion: 0.24
Nodes (11): parse_http_expect(), (ok, error) for an HTTP response against the expectation grammar., check_target(), _http(), _ping(), AsyncClient, Semaphore, The monitor lane — per-target health checks on the worker's minute cron.… (+3 more)

### Community 109 - "test_auth.py"
Cohesion: 0.29
Nodes (11): AsyncClient, When the socket peer isn't in ipambox_trusted_proxies, a supplied XFF is…, Spreading failures across many usernames from one IP trips the aggregate lock —…, Five bad logins for one (user, ip) pair must not lock out other users on the…, test_endpoints_require_auth(), test_lockout_keyed_per_user_ip_pair(), test_login_lockout(), test_per_ip_aggregate_backstop() (+3 more)

### Community 110 - "test_scan_cidr_tcp_fallback_reports_found()"
Cohesion: 0.21
Nodes (8): on_hosts fires once per detection step with that chunk's new IPs — ARP batch…, When L2+L3 find nothing, the TCP fallback publishes its batch too., test_scan_cidr_emits_found_deltas(), fake_icmp(), fake_probe(), fake_ptr(), on_hosts(), test_scan_cidr_tcp_fallback_reports_found()

### Community 111 - "Racks"
Cohesion: 0.21
Nodes (12): netbox-community/devicetype-library, Device image library, Elevation editor, Find free U, Health overlay, Linked asset and IP address, NetBox devicetype-library, Rack placement rules (+4 more)

### Community 112 - "docs/[slug]/page.tsx"
Cohesion: 0.24
Nodes (9): DocPage(), dynamicParams, generateMetadata(), loadMarkdown(), DocsContent(), docCategoryLabel(), getDoc(), react-markdown (+1 more)

### Community 113 - "_FakePool"
Cohesion: 0.20
Nodes (8): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture, Stands in for the arq Redis pool — never actually dispatches work., scan_exclude_networks=10.70.0.64/26 inside scan_networks=10.70.0.0/24: the…, test_scheduler_and_route_share_exclusion_guard()

### Community 114 - "IpamBox README"
Cohesion: 0.42
Nodes (11): Add network wizard, Subnets doc, Gateway/DNS technical addresses, IP address, IP range (dhcp/pool/reserved), Subnet matrix, Pool override (force=1), Prefix (subnet) (+3 more)

### Community 116 - "devDependencies"
Cohesion: 0.20
Nodes (10): devDependencies, autoprefixer, postcss, sharp, tailwindcss, @types/js-yaml, @types/node, @types/react (+2 more)

### Community 117 - "IpamBox"
Cohesion: 0.31
Nodes (10): Accounts & Roles, Insecure mode (IPAMBOX_ALLOW_INSECURE), Four roles (Administrator, Operator, Contributor, Viewer), Session-cookie authentication, Certificates, Color rules, Scan targeting policy, Backup & Restore (+2 more)

### Community 118 - "Smart import dialog"
Cohesion: 0.22
Nodes (10): GET /api/v1/devices/export.csv, GET /api/v1/devices/export.xlsx, CSV export, Export dropdown (Devices toolbar), Filtered-set export parity (devices-filtered.*), Filter facets as URL params, Export column round-trip contract, UTF-8 BOM encoding (Excel/Hebrew-safe) (+2 more)

### Community 119 - "ip_display()"
Cohesion: 0.31
Nodes (7): AsyncSession, get, stats(), CableMismatchItem, DashboardStats, MacMismatchItem, BaseModel

### Community 120 - "services/backup.py"
Cohesion: 0.28
Nodes (9): Delete assignments whose target no longer exists. For non-ORM write paths…, sweep_orphans(), _from_json(), AsyncSession, Convert a JSON value back to what asyncpg expects for this column., Replace the non-admin user set from a users-inclusive envelope. Admin rows in…, Wipe all registered tables and re-load them from the backup envelope. Runs…, restore_backup() (+1 more)

### Community 121 - "imports.py"
Cohesion: 0.33
Nodes (8): ImportBatchStatus, str, CommitOptions, ImportBatchOut, BaseModel, Per-sheet detection result shown in the wizard., RowResult, SheetPreview

### Community 122 - "_mkuser()"
Cohesion: 0.28
Nodes (9): _mkuser(), User, UserRole, _mkuser(), User, UserRole, _mkuser(), User (+1 more)

### Community 123 - "generate_demo_data.py"
Cohesion: 0.22
Nodes (9): Demo import data — ALL FICTIONAL, demo_rack_dc.py (emit | apply), /devices/import endpoint, Examples README (demo import data), Files, `Network_Address_DEMO_EN.xlsx` — the edge-case workbook, `Network_Address_DEMO.xlsx` — the clean flagship, Regenerating (+1 more)

### Community 124 - "services/backup.py"
Cohesion: 0.29
Nodes (8): _alembic_revisions(), build_backup(), Any, Base, Known migration revisions, head first (linear chain)., Serialize every registered table into the gzipped JSON envelope. With…, _serialize_row(), _to_json()

### Community 125 - "ip_display()"
Cohesion: 0.50
Nodes (8): accept_scanned_mac(), _clear_flag(), keep_stored_mac(), _mismatch_flag(), IPAddress, Trust the scanner: scanned MAC becomes the stored mac_address., Trust inventory: restore the documented MAC and dismiss the pair so the…, IPAddress

### Community 126 - ".test_legacy_bezeq_layout()"
Cohesion: 0.29
Nodes (5): parse_site_number(), parse_circuits(), קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., TestCircuitsParser

### Community 128 - "IpamBox"
Cohesion: 0.43
Nodes (8): api service (FastAPI/uvicorn backend), db service (PostgreSQL 16), ipam bridge network (192.0.2.0/24), redis service (Redis 7, appendonly), scanner service (arq worker, host networking), web service (Next.js frontend), ip_addresses table (IPAM data store), ip column type (live IPAM resolution)

### Community 129 - "check-rack-library.mjs"
Cohesion: 0.25
Nodes (6): DIR, FACES, LAYOUTS, problems, referenced, slugs

### Community 130 - "IpamBox"
Cohesion: 0.29
Nodes (8): Certificate expiry tracking, EOL & support-status tracking, import_batch_id provenance, Inventory (asset register), Custom Lists (user-defined tables), Hebrew-aware text handling, Key-column merge identity on re-import, Positional column keys (c0, c1, …)

### Community 131 - "User"
Cohesion: 0.43
Nodes (7): hash_password(), AsyncSession, RBAC unchanged: the facet vocabulary stays DATA_READ., test_next_free_u_viewer_can_read(), test_rack_group_rbac(), test_racks_list_filters_viewer(), test_viewer_cannot_write_racks()

### Community 132 - "_positional_columns()"
Cohesion: 0.29
Nodes (4): _col_class(), _positional_columns(), Dominant content class of a column sample., Headerless sheet: locate the IP column, then assign the remaining canonical…

### Community 133 - "IPStatus"
Cohesion: 0.29
Nodes (5): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture

### Community 134 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, build:rack-library, check:rack-library, dev, lint, start

### Community 135 - "Devices"
Cohesion: 0.29
Nodes (7): API sketch, Device detail, Devices, Devices vs racks, From the IP drawer, Health rollup, The list

### Community 136 - "classify.py"
Cohesion: 0.47
Nodes (5): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…

### Community 138 - "get_settings()"
Cohesion: 0.40
Nodes (5): ArqRedis, get_arq_pool(), Shared ARQ pool — callers must not close() it per job., redis_settings_from_url(), RedisSettings

### Community 139 - "key()"
Cohesion: 0.40
Nodes (5): key(), fixture, fixture, key(), Provision a master key on the cached settings object.

### Community 140 - "Docs: IP Addresses"
Cohesion: 0.40
Nodes (5): Docs: IP Addresses, Docs: Devices, Docs: Racks, Docs: Settings, Docs: Subnets

### Community 141 - "use-chart-theme.ts"
Cohesion: 0.50
Nodes (4): ChartTheme, FALLBACK, readTheme(), useChartTheme()

### Community 142 - "Security Policy"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 143 - "scanner.py"
Cohesion: 0.67
Nodes (3): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for()

### Community 144 - "test_racks.py"
Cohesion: 0.50
Nodes (3): Every /racks list param filters; all compose with AND semantics., _site(), test_racks_list_facet_params()

## Ambiguous Edges - Review These
- `Stats strip & saved views` → `Monitoring doc (V7)`  [AMBIGUOUS]
  frontend/src/content/docs/inventory.md · relation: semantically_similar_to
- `Cable` → `Rack`  [AMBIGUOUS]
  frontend/src/content/docs/cabling.md · relation: conceptually_related_to

## Knowledge Gaps
- **383 isolated node(s):** `Counts`, `Step`, `Step`, `PrefixRow`, `MonitorPrefill` (+378 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1549 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Stats strip & saved views` and `Monitoring doc (V7)`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._
- **What is the exact relationship between `Cable` and `Rack`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `create_device()` connect `devices.py` to `index.ts`, `v1/racks.py`, `services/racks.py`, `Rack`, `IPAMError`, `Device`?**
  _High betweenness centrality (0.155) - this node is a cross-community bridge._
- **Why does `Device` connect `index.ts` to `devices-client.tsx`, `devices.py`, `index.ts`, `app-shell.tsx`, `useAsyncData()`?**
  _High betweenness centrality (0.148) - this node is a cross-community bridge._
- **Why does `js-yaml` connect `build-rack-library.mjs` to `package.json`, `rackula.ts`?**
  _High betweenness centrality (0.107) - this node is a cross-community bridge._
- **Are the 69 inferred relationships involving `Device` (e.g. with `_filtered_devices()` and `_export_rows()`) actually correct?**
  _`Device` has 69 INFERRED edges - model-reasoned connections that need verification._
- **Are the 72 inferred relationships involving `IPAMError` (e.g. with `_get_interface()` and `_get_cable()`) actually correct?**
  _`IPAMError` has 72 INFERRED edges - model-reasoned connections that need verification._