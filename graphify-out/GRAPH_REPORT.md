# Graph Report - IpamBox  (2026-09-26)

## Corpus Check
- 486 files · ~1,080,140 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 22 file(s) not represented in the graph (top: (none) 8, .csv 6, .ini 2)

## Summary
- 5446 nodes · 18335 edges · 215 communities (129 shown, 45 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 1495 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f153774b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- react
- interfaces-panel.tsx
- devices-client.tsx
- index.ts
- lucide-react
- ScanJob
- IpamBox
- test_snmp.py
- v1/racks.py
- test_snmp_inventory.py
- Site
- test_racks.py
- rack_io.py
- test_monitors.py
- notify.py
- security.py
- cn
- get_or_404
- _split_dsn
- v1/devices.py
- Rack
- v1/settings.py
- worker.py
- services/backup.py
- traps.py
- _Planner
- generate_demo_data.py
- IPAddress
- lists.py
- Device
- services/snmp.py
- test_cabling.py
- services/racks.py
- scanner.py
- test_cable_validation.py
- color_rules.py
- v1/device_templates.py
- test_scanner.py
- attachments.py
- test_rack_io.py
- demo_rack_dc.py
- test_reports.py
- test_devices.py
- device-filter-panel.tsx
- Secrets Encryption
- backend/requirements.txt
- common.py
- test_lists.py
- Frontend Error Pages
- get_settings
- create_scan
- test_device_io.py
- test_review.py
- schemas/dashboard.py
- tree-client.tsx
- services/review.py
- User
- rackula.ts
- runtime_settings.py
- channels.py
- test_topology.py
- imports.py
- Device (first-class host entity)
- Command Palette Search
- Frontend Dependencies
- vlans.py
- v1/monitors.py
- clean
- Inventory sync (Pull inventory)
- docs_pages.py
- IpamBox README
- IPRange
- v1/backup.py
- IPAM Export Tests
- package.json
- IPAMError
- DeviceInterface
- UserRole
- test_device_templates.py
- test_docs_attachments.py
- _plan
- classify_sheet
- topology-map.tsx
- Monitoring doc (V7)
- maintenance.py
- v1/topology.py
- build-rack-library.mjs
- Product Feature Docs
- _matrix
- test_maintenance.py
- SNMP Enrichment Documentation
- test_allocation.py
- _positional_columns
- Row Ordering Tests
- test_settings.py
- utils.ts
- group-client.tsx
- network.py
- test_colors.py
- test_ip_source.py
- api service (FastAPI/uvicorn backend)
- Demo import data — ALL FICTIONAL
- Prefix Gateway Tests
- TypeScript Configuration
- hash_password
- test_scan_cidr_tcp_fallback_reports_found
- _mklist
- docs.ts
- _FakePool
- shortcuts.ts
- Pages & Attachments
- fake_arq
- Search Endpoint Tests
- reader.py
- Reports
- test_bridge_macs_parse_and_vlan_passes
- Changelog Audit Tests
- test_workbook_import.py
- Cable validation — documented vs observed
- test_cable_mismatch_event_shape
- test_unmanaged_port_never_flagged
- prefs.ts
- Frontend Dev Dependencies
- Fake SMTP Test Helper
- Rack Library Validation Script
- NPM Scripts
- Devices Documentation
- Entity CRUD Tests
- Documentation Articles
- Security Policy
- Changelog and List Features
- Next.js Environment Types
- Device and Rack Import
- Racks API Docs
- XFF Shim
- Rack Image Library Bundle
- ChannelKind
- App Icon Asset
- Root Layout
- First-Run Setup
- Sessions & Brute-Force Protection
- Users & Roles Console
- Certificate Fields
- Changelog Coverage & Retention
- Per-Object History
- Circuit Import Provenance
- Device CSV Export
- Device XLSX Export
- Confirm/Delete Workflow
- MAC Mismatch Review
- Active/Offline Flips
- Roll-up Utilization
- IP Addresses Table
- API Docs Swagger
- UI Tour
- Rack CSV Export
- Rack XLSX Export
- Rack Group XLSX Export
- Single Rack XLSX Export
- Five-Stage Scan Pipeline
- Running Scans
- Scanner Settings
- Go-to Keyboard Chords
- Shortcut Scope Rules
- Table Keyboard Navigation
- Color Rules
- Site Fields
- Attaching Tags
- Topology Map Docs
- VLANs and VLAN Groups
- VLAN Usage Tips
- VRF Overlap Rules
- Topology Map Feature
- Go-to Chords Table

## God Nodes (most connected - your core abstractions)
1. `cn()` - 181 edges
2. `IPAddress` - 166 edges
3. `react` - 154 edges
4. `Device` - 151 edges
5. `IPAMError` - 129 edges
6. `get_or_404()` - 101 edges
7. `useAsyncData()` - 99 edges
8. `User` - 92 edges
9. `lucide-react` - 91 edges
10. `Site` - 90 edges

## Surprising Connections (you probably didn't know these)
- `CSV export` --semantically_similar_to--> `Address CSV import/export (UTF-8 BOM)`  [INFERRED] [semantically similar]
  frontend/src/content/docs/devices.md → README.md
- `Smart import dialog` --semantically_similar_to--> `Excel workbook import (per-sheet detection, dry-run, all-or-nothing/partial commit)`  [INFERRED] [semantically similar]
  frontend/src/content/docs/devices.md → README.md
- `Rack` --semantically_similar_to--> `Rack elevations & rack groups`  [INFERRED] [semantically similar]
  frontend/src/content/docs/racks.md → README.md
- `Stats strip & saved views` --semantically_similar_to--> `Monitoring doc (V7)`  [AMBIGUOUS] [semantically similar]
  frontend/src/content/docs/inventory.md → frontend/src/content/docs/monitoring.md
- `Live IP column resolution` --semantically_similar_to--> `Discovery Inbox reconciliation`  [INFERRED] [semantically similar]
  frontend/src/content/docs/lists.md → README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Documented vs discovered network sync loop** — readme_ipambox, readme_ipam_hierarchy, readme_scanner, readme_discovery_inbox, readme_review_center [EXTRACTED 0.90]
- **Pull inventory writes VLANs/prefixes/addresses with snmp provenance** — frontend_src_content_docs_snmp_inventory_sync, readme_vlans, frontend_src_content_docs_subnets_prefix, frontend_src_content_docs_addresses_ip_address, frontend_src_content_docs_snmp_import_batch [EXTRACTED 0.90]
- **IpamBox docker-compose service stack** — dockercompose_web, dockercompose_api, dockercompose_scanner, dockercompose_db, dockercompose_redis [EXTRACTED 0.95]
- **Core IPAM hierarchy: Site → VRF → Prefix → IP address** — frontend_src_content_docs_sites_feature, frontend_src_content_docs_vrfs_feature, frontend_src_content_docs_overview_data_model [EXTRACTED 1.00]
- **Scan → reconcile → discovery inbox → address statuses** — frontend_src_content_docs_scans_feature, frontend_src_content_docs_scans_pipeline, frontend_src_content_docs_discovery_feature [EXTRACTED 1.00]
- **Shared backend image (api + worker deps)** — dockercompose_api, dockercompose_scanner, backend_requirements_txt_arq, backend_requirements_txt_scapy, backend_requirements_txt_pysnmp, backend_requirements_txt_sqlalchemy [INFERRED 0.75]
- **Preview → one-transaction apply import pattern** — readme_workbook_importer, frontend_src_content_docs_snmp_inventory_sync, frontend_src_content_docs_racks_smart_bundle, frontend_src_content_docs_snmp_import_batch [INFERRED 0.75]
- **Rack tree bundle (group → racks → devices → interfaces/cables)** — frontend_src_content_docs_racks_rack_group, frontend_src_content_docs_racks_rack, readme_device_inventory, frontend_src_content_docs_racks_smart_bundle [INFERRED 0.75]

## Communities (215 total, 45 thin omitted)

### Community 0 - "react"
Cohesion: 0.02
Nodes (92): nextConfig, metadata, metadata, metadata, DeviceDetailClient(), metadata, metadata, metadata (+84 more)

### Community 1 - "interfaces-panel.tsx"
Cohesion: 0.04
Nodes (64): metadata, viewport, AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS, NavGroup (+56 more)

### Community 2 - "devices-client.tsx"
Cohesion: 0.08
Nodes (95): CertificatesPage(), EMPTY, CircuitsPage(), EMPTY, DEVICE_VIEWS, DeviceRow, DevicesPage(), EMPTY (+87 more)

### Community 3 - "index.ts"
Cohesion: 0.03
Nodes (86): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, SheetResults() (+78 more)

### Community 4 - "lucide-react"
Cohesion: 0.07
Nodes (93): ACTION_STYLES, ChangelogPage(), ACTION_STYLES, CABLE_REASON, EMPTY_EDIT, FACE_BADGE, BulkResp, PrintClient() (+85 more)

### Community 5 - "ScanJob"
Cohesion: 0.07
Nodes (44): _job_payload(), str, ScanJob, ScanStatus, Exception, Raised inside the pipeline when the user cancels the scan., ScanCancelled, _job_status() (+36 more)

### Community 6 - "IpamBox"
Cohesion: 0.06
Nodes (81): Accounts & Roles, Insecure mode (IPAMBOX_ALLOW_INSECURE), The four roles (Administrator/Operator/Contributor/Viewer), Session-cookie authentication, Address roles (vip/vrrp/hsrp/glbp/carp/secondary), Address CSV import/export, IP Addresses, IP drawer (+73 more)

### Community 7 - "test_snmp.py"
Cohesion: 0.09
Nodes (68): handle_trap(), One trap end-to-end: resolve → apply → notify. The listener callback hands…, _device(), _down(), _enable(), _iface(), _ifrow(), _ip() (+60 more)

### Community 8 - "v1/racks.py"
Cohesion: 0.07
Nodes (70): _check_refs(), create_device(), create_rack(), delete_device(), delete_rack(), _device_out(), _devices(), _export_name() (+62 more)

### Community 9 - "test_snmp_inventory.py"
Cohesion: 0.12
Nodes (36): _bare_device(), _clean_walk(), _device(), _enable(), _ip(), _mock_inv(), _test(), _prefix() (+28 more)

### Community 10 - "Site"
Cohesion: 0.05
Nodes (78): AsyncSession, get, stats(), email_report(), export_section_csv(), export_xlsx(), AsyncSession, get (+70 more)

### Community 11 - "test_racks.py"
Cohesion: 0.10
Nodes (60): _carrier(), _dev(), _group(), _imports(), _mount(), _next_free(), AsyncClient, _rack() (+52 more)

### Community 12 - "rack_io.py"
Cohesion: 0.05
Nodes (76): import_racks(), Request, Smart rack/group bundle import — V5B's stateless flow for whole trees. Sheets…, RackGroup, A bayed row: racks ordered left-to-right as they stand in the DC., _alias_to_field(), apply_mapping_overrides(), auto_map_fields() (+68 more)

### Community 13 - "test_monitors.py"
Cohesion: 0.05
Nodes (42): _FakeArqPool, _FakeRedis, _login(), _mk_device(), _mk_prefix_and_addr(), _mkuser(), V7 monitoring + notification channels. Covers target CRUD/RBAC, the exactly-…, Viewer reads targets but can't write/check/delete them. (+34 more)

### Community 14 - "notify.py"
Cohesion: 0.11
Nodes (26): NotificationLog, Append-only delivery attempt log — swept by ``notify_retention_days``., _deliver(), _DeliveryFailed, emit(), _log(), _post_json(), Any (+18 more)

### Community 15 - "security.py"
Cohesion: 0.07
Nodes (61): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+53 more)

### Community 16 - "cn"
Cohesion: 0.05
Nodes (69): ImportListDialog(), IpCell(), SortableColRow(), IP_ROLES, IP_STATUSES, RANGE_ROLES, SplitDialog(), SplitPlan (+61 more)

### Community 17 - "get_or_404"
Cohesion: 0.06
Nodes (66): _address_csv_row(), _addresses_stmt(), bulk_addresses(), BulkBody, _check_interface_link(), create_address(), delete_address(), export_addresses() (+58 more)

### Community 18 - "_split_dsn"
Cohesion: 0.11
Nodes (26): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., _split_dsn() (+18 more)

### Community 19 - "v1/devices.py"
Cohesion: 0.04
Nodes (112): apply_device_template(), _asset_ref(), _check_iface_refs(), create_interface(), delete_device(), delete_interface(), _detail(), _devices_stmt() (+104 more)

### Community 20 - "Rack"
Cohesion: 0.14
Nodes (28): _check_site(), create_rack_group(), delete_rack_group(), export_rack_group_xlsx(), _get_group(), get_rack_group(), list_rack_groups(), _ordered_racks() (+20 more)

### Community 21 - "v1/settings.py"
Cohesion: 0.12
Nodes (28): _build_out(), _lan_info(), _mask_url(), AsyncSession, get, Hide the password in a scheme://user:pass@host URL., LAN identity detected by the host-networked worker (written to Redis). Falls…, read_settings() (+20 more)

### Community 22 - "worker.py"
Cohesion: 0.08
Nodes (45): ArqRedis, get_arq_pool(), Shared ARQ pool — callers must not close() it per job., set_actor(), prune_backups(), Delete oldest scheduled backups beyond the retention count., get_effective(), AsyncSession (+37 more)

### Community 23 - "services/backup.py"
Cohesion: 0.04
Nodes (93): after_flush(), before_flush(), SyncSession, attachments garbage collection. Attachment rows reference their owner…, Delete attachments whose owner no longer exists. For non-ORM write paths…, register(), sweep_orphans(), after_flush() (+85 more)

### Community 24 - "traps.py"
Cohesion: 0.09
Nodes (24): _apply_link_state(), _clear_unmanaged_flag(), ensure(), _flag_unmanaged(), datetime, SNMP trap receiver (V8.1) — near-realtime link state. The poll lane…, (transportDomain, transportAddress) -> the sender's IP string. asyncio's UDP…, Mark a documented-but-uncredentialed sender for the review queue. The flag is a… (+16 more)

### Community 25 - "_Planner"
Cohesion: 0.09
Nodes (16): _Planner, (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Folded sheet title vs site name/code — word-boundary matching so 'int' doesn't…, Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new…, Resolve a 10.{second}.x sheet — site_number is only meaningful inside the…, A declared octet block claims the sheet — unless its site is inactive, in which… (+8 more)

### Community 26 - "generate_demo_data.py"
Cohesion: 0.10
Nodes (49): assets_rows(), _assign_site_sheets(), _assign_site_sheets_clean(), build_en_workbook(), build_mixed_workbook(), build_sites(), certificates_rows(), circuits_rows() (+41 more)

### Community 27 - "IPAddress"
Cohesion: 0.04
Nodes (102): create_network(), AsyncSession, post, allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix() (+94 more)

### Community 28 - "lists.py"
Cohesion: 0.06
Nodes (61): list_changelog(), AsyncSession, get, bulk_rows(), _check_columns(), create_list(), create_row(), delete_list() (+53 more)

### Community 29 - "Device"
Cohesion: 0.08
Nodes (55): Device, ip_display(), Any, Normalize asyncpg-returned ipaddress objects / strings to display form. INET…, to_int(), apply_device_import(), _carrier_diff_name(), _err() (+47 more)

### Community 30 - "services/snmp.py"
Cohesion: 0.05
Nodes (79): _apply_bridge_links(), _auth(), _context(), _cred(), due_device_ids(), _get(), _idx_inet(), _idx_int() (+71 more)

### Community 31 - "test_cabling.py"
Cohesion: 0.13
Nodes (46): _backup_bytes(), _cable(), _device(), _gen(), _iface(), _ip(), _login(), _mkuser() (+38 more)

### Community 32 - "services/racks.py"
Cohesion: 0.10
Nodes (33): create_device(), Device, Create a device — unracked inventory by default, or placed directly when…, apply_device_patch(), carrier_children(), CarrierError, _check_carrier_mount(), check_layout_change() (+25 more)

### Community 33 - "scanner.py"
Cohesion: 0.09
Nodes (33): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), _host_chunks(), _icmp_checksum(), _icmp_echo_packet(), _icmp_socket() (+25 more)

### Community 34 - "test_cable_validation.py"
Cohesion: 0.14
Nodes (58): poll_device(), One full enrichment pass: test -> IF-MIB -> bridge-MAC -> LLDP. Network first,…, _cable(), _commit_fresh(), _device(), _enable(), _flag(), _fresh_iface() (+50 more)

### Community 35 - "color_rules.py"
Cohesion: 0.07
Nodes (45): create_rule(), delete_rule(), get_rule(), list_rules(), preview_rule(), AsyncSession, delete, get (+37 more)

### Community 36 - "v1/device_templates.py"
Cohesion: 0.08
Nodes (36): create_template(), delete_template(), _get(), get_template(), instantiate_template(), list_templates(), AsyncSession, delete (+28 more)

### Community 37 - "test_scanner.py"
Cohesion: 0.07
Nodes (49): _flag(), Any, AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), HostResult, _global_vrf_id(), _infer_scan_vrf() (+41 more)

### Community 38 - "attachments.py"
Cohesion: 0.14
Nodes (19): _allowed(), _content_disposition(), _content_type(), delete_attachment(), download_attachment(), list_attachments(), AsyncSession, delete (+11 more)

### Community 39 - "test_rack_io.py"
Cohesion: 0.16
Nodes (42): _bundle(), _by_sheet(), _cable(), _csv(), _device(), _group(), _iface(), _import() (+34 more)

### Community 40 - "demo_rack_dc.py"
Cohesion: 0.10
Nodes (29): Api, apply(), _device_payload(), emit_zip(), find_one(), _KeepMethodRedirect, layout_doc(), main() (+21 more)

### Community 41 - "test_reports.py"
Cohesion: 0.23
Nodes (20): _login(), _mkuser(), AsyncClient, AsyncSession, V11 Reports workspace — /reports/summary, per-section CSV, multi-sheet XLSX,…, Reports are derived — reads and email writes never hit the audit log., _sec(), _summary() (+12 more)

### Community 42 - "test_devices.py"
Cohesion: 0.13
Nodes (39): _cable(), _device(), _group(), _iface(), _ip(), _login(), _mkuser(), _prefix() (+31 more)

### Community 43 - "device-filter-panel.tsx"
Cohesion: 0.09
Nodes (36): PrefixDetailPage(), DEVICE_FILTER_PARAMS, DEVICE_TEXT_PARAMS, DeviceFilterPanel(), DeviceFilterState, DeviceTextParam, FACES, HealthFacet (+28 more)

### Community 44 - "Secrets Encryption"
Cohesion: 0.10
Nodes (34): _data_key(), decrypt_str(), encrypt_str(), _master_key(), Exception, Secrets at rest — the credential contract v7/v8/v12/v14 build on. A single…, Unseal a "v1:…" blob. Strict prefix check — unknown formats, malformed payloads…, Base for secrets-service failures — never carries secret material. (+26 more)

### Community 45 - "backend/requirements.txt"
Cohesion: 0.11
Nodes (35): alembic==1.14.0, asyncpg==0.30.0, httpx==0.28.1, psutil==6.1.0, pydantic==2.10.3, pydantic-settings==2.6.1, pytest==8.3.4, pytest-asyncio==0.25.0 (+27 more)

### Community 46 - "common.py"
Cohesion: 0.06
Nodes (38): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, AssetKind, str, AssetCreate, AssetOut, AssetUpdate, BaseModel, field_validator (+30 more)

### Community 47 - "test_lists.py"
Cohesion: 0.08
Nodes (30): ListTarget, PreviewOptions, Import a sheet as a custom list (user-selected or suggested)., User-confirmed mapping choices applied before building the plan., _cell_text(), extract_list_table(), _infer_type(), _ips() (+22 more)

### Community 49 - "get_settings"
Cohesion: 0.04
Nodes (79): get_settings(), close_arq_pool(), close_redis(), get_redis(), Shared process-wide Redis client. Do NOT aclose() it per call — connections…, Shut down the shared client — lifespan/worker shutdown only., redis_settings_from_url(), create_session() (+71 more)

### Community 50 - "create_scan"
Cohesion: 0.12
Nodes (19): cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), list_scans(), AsyncSession, get, post (+11 more)

### Community 51 - "test_device_io.py"
Cohesion: 0.20
Nodes (34): _csv(), _device(), _group(), _import(), _ip(), _login(), _mkuser(), _prefix() (+26 more)

### Community 52 - "test_review.py"
Cohesion: 0.22
Nodes (34): _device(), _flag_mismatch(), _iface(), _ip(), _login(), _mkuser(), _prefix(), AsyncClient (+26 more)

### Community 53 - "schemas/dashboard.py"
Cohesion: 0.15
Nodes (15): CertificateCreate, CertificateOut, CertificateUpdate, BaseModel, field_validator, CableMismatchItem, DashboardStats, MacMismatchItem (+7 more)

### Community 54 - "tree-client.tsx"
Cohesion: 0.19
Nodes (19): metadata, ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), collectExpandableKeys(), flattenTree() (+11 more)

### Community 55 - "services/review.py"
Cohesion: 0.06
Nodes (65): dismiss_item(), _flagged_address(), get_review(), mac_mismatch_accept(), mac_mismatch_keep(), AsyncSession, get, post (+57 more)

### Community 56 - "User"
Cohesion: 0.16
Nodes (33): User, _backup_bytes(), _envelope_bytes(), _mkusers(), Hand-craft a backup envelope (e.g. with a forged users table)., Guard: every ORM table must be backed up (or explicitly excluded). Adding a new…, Fresh-server scenario: the migration-seeded Global VRF is replaced by the…, Fresh-server scenario: the target's admins survive; its non-admin set is fully… (+25 more)

### Community 57 - "rackula.ts"
Cohesion: 0.05
Nodes (78): parseRange(), TemplateDialog(), templateToRows(), DragSession, DropRow(), EditorBlock(), errDetail(), Pending (+70 more)

### Community 58 - "runtime_settings.py"
Cohesion: 0.11
Nodes (17): psycopg2-style URL for alembic offline mode / scripts., Settings, Effective, _env_sourced(), Any, Runtime-editable settings: app_settings rows override env defaults. Each public…, True when the field's current value differs from its declared default., One runtime-editable setting. field: the env-backed attribute on… (+9 more)

### Community 59 - "channels.py"
Cohesion: 0.18
Nodes (22): _config_fields(), create_channel(), delete_channel(), _get(), get_channel(), list_channels(), notification_log(), _out() (+14 more)

### Community 60 - "test_topology.py"
Cohesion: 0.19
Nodes (32): _cable(), _device(), _edge(), _gen(), _graph(), _iface(), _ip(), _login() (+24 more)

### Community 61 - "imports.py"
Cohesion: 0.09
Nodes (40): do_run_migrations(), run_migrations_online(), commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets() (+32 more)

### Community 62 - "Device (first-class host entity)"
Cohesion: 0.10
Nodes (33): netbox-community/devicetype-library, IPAddress, connected_interface_id (structured far-end port link), connected_ip (host-side NIC binding), DeviceInterface (device-owned port), L1 trace (cable path walk), match-free-text transition endpoint, One-cable-per-interface rule (+25 more)

### Community 63 - "Command Palette Search"
Cohesion: 0.17
Nodes (27): _folded(), AsyncSession, get, Cross-object search for the command palette. One GET returns grouped matches…, Column expression with Hebrew final letters folded — pairs with fold_hebrew()…, Short label for a list-row search hit: key-column value, else the first non-…, _row_label(), search() (+19 more)

### Community 64 - "Frontend Dependencies"
Cohesion: 0.06
Nodes (31): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, elkjs, js-yaml, jszip (+23 more)

### Community 65 - "vlans.py"
Cohesion: 0.18
Nodes (26): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+18 more)

### Community 66 - "v1/monitors.py"
Cohesion: 0.08
Nodes (51): check_now(), _check_refs(), create_target(), delete_target(), _filters(), _get(), get_target(), list_targets() (+43 more)

### Community 67 - "clean"
Cohesion: 0.07
Nodes (52): row(), assemble_ip(), clean(), _clean_octets(), excel_date(), map_status(), mask_to_prefixlen(), network_of() (+44 more)

### Community 68 - "Inventory sync (Pull inventory)"
Cohesion: 0.13
Nodes (20): openpyxl==3.1.5, pysnmp==7.1.29, demo-addresses.csv, Network_Address_DEMO.xlsx, Network_Address_DEMO_EN.xlsx, connected_interface link, Address source provenance field, import_batch_id provenance (+12 more)

### Community 69 - "docs_pages.py"
Cohesion: 0.20
Nodes (17): create_page(), delete_page(), get_page(), get_page_by_slug(), list_pages(), AsyncSession, delete, get (+9 more)

### Community 70 - "IpamBox README"
Cohesion: 0.08
Nodes (48): Demo CSV files, Fictional demo dataset, Demo import data README, Demo list CSVs (contacts/vlans/servers), Demo VLAN scheme, Network_Address_DEMO.xlsx, Network_Address_DEMO_EN.xlsx, backend/app/services/workbook parser (+40 more)

### Community 71 - "IPRange"
Cohesion: 0.14
Nodes (19): _check_range_overlap(), create_range(), delete_range(), list_ranges(), AsyncSession, delete, get, post (+11 more)

### Community 72 - "v1/backup.py"
Cohesion: 0.09
Nodes (38): delete_scheduled_backup(), download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, delete, get, post (+30 more)

### Community 73 - "IPAM Export Tests"
Cohesion: 0.16
Nodes (26): _prefix(), _range(), export.csv takes the same filters as the list endpoint — a filtered view…, Same filtered-export treatment on the prefixes CSV (F8)., A documented v6 /64's 2^64 host count must not reach dashboard sums (~1.8e19 >…, A deliberate bulk import documents existing reality — statics inside pools land…, test_address_role_nat_and_bulk(), test_addresses_export_respects_filters() (+18 more)

### Community 74 - "package.json"
Cohesion: 0.07
Nodes (26): name, private, version, autoprefixer, clsx, elkjs, jszip, lz-string (+18 more)

### Community 75 - "IPAMError"
Cohesion: 0.06
Nodes (77): _crud_router(), create_item(), delete_item(), get_item(), list_items(), reorder_items(), update_item(), reorder_lists() (+69 more)

### Community 76 - "DeviceInterface"
Cohesion: 0.06
Nodes (84): _cable_out(), _check_ends(), create_cable(), delete_cable(), _get_cable(), _get_interface(), interfaces_match_free_text(), list_cables() (+76 more)

### Community 77 - "UserRole"
Cohesion: 0.34
Nodes (22): str, UserRole, login(), mkuser(), other_client(), AsyncClient, AsyncSession, allow_insecure keeps full access (existing behavior preserved). (+14 more)

### Community 78 - "test_device_templates.py"
Cohesion: 0.23
Nodes (21): auth_on(), _device(), _interfaces(), _login(), _mkuser(), AsyncClient, AsyncSession, fixture (+13 more)

### Community 79 - "test_docs_attachments.py"
Cohesion: 0.29
Nodes (18): _mk_page(), _mk_site(), AsyncClient, Response, V13 — user-authored docs pages + entity attachments., Bulk ORM deletes (addresses bulk action) sweep attachments too., test_attachment_cascade_via_bulk_delete(), test_attachment_cascades_on_entity_delete() (+10 more)

### Community 80 - "_plan"
Cohesion: 0.17
Nodes (13): _master_row(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind…, Mashapan TA + MATPASH share number 200 — merge + conflict, not a silent… (+5 more)

### Community 81 - "classify_sheet"
Cohesion: 0.24
Nodes (6): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, TestClassify

### Community 82 - "topology-map.tsx"
Cohesion: 0.09
Nodes (24): EdgePopup, buildTree(), DeviceNodeData, elk, ELK_OPTIONS, ElkChild, GROUP_STYLE, GroupNode() (+16 more)

### Community 83 - "Monitoring doc (V7)"
Cohesion: 0.16
Nodes (25): Address status lifecycle (active/reserved/dhcp/discovered/offline), Check kinds (ping/tcp/http), Monitoring doc (V7), Event sources, down_after hysteresis, Deliberate limits, Monitor target, Notification channel (+17 more)

### Community 84 - "maintenance.py"
Cohesion: 0.11
Nodes (34): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+26 more)

### Community 85 - "v1/topology.py"
Cohesion: 0.18
Nodes (24): get_layout(), put_layout(), AsyncSession, get, Topology map (V10): GET /topology/graph + GET/PUT /topology/layout. One honest…, topology_graph(), DiagramLayoutOut, DiagramLayoutPut (+16 more)

### Community 86 - "build-rack-library.mjs"
Cohesion: 0.08
Nodes (36): Demo .Rackula.zip racks, Demo .Rackula.zip rack layouts, Air-gap safe bundling, CC0 1.0 Universal license, CC0 1.0 Universal, netbox-community/devicetype-library, Rack library ATTRIBUTION, Rack device image library (+28 more)

### Community 87 - "Product Feature Docs"
Cohesion: 0.09
Nodes (24): Accounts & role-based access control, Expiry tracking (badge, certs_expiring_30d dashboard count), Certificates — expiry tracking register, Circuits — WAN circuit register, Circuit fields (line type, Bezeq circuit ID, WAN IP, is_retired), Discovery Inbox — reconciliation queue, Hierarchy tree (/tree) — Site→VRF→Prefix, Tree navigation (click-to-prefix, session expand state) (+16 more)

### Community 88 - "_matrix"
Cohesion: 0.09
Nodes (21): _blocks(), _master_blocks(), parse_site_sheet(), parse_sites_master(), Split duplicated column groups (031-style runaway): each block starts at an…, (first, second) octet pairs a master row declares — lets sheet->site matching…, parse_sites_master_records(), _matrix() (+13 more)

### Community 89 - "test_maintenance.py"
Cohesion: 0.22
Nodes (10): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_now_enqueues(), test_clear_discovery() (+2 more)

### Community 90 - "SNMP Enrichment Documentation"
Cohesion: 0.29
Nodes (13): SNMP Enrichment Documentation, Bridge-MAC to connected_interface_id Resolution, Per-VLAN Community Indexing (Cisco FDB), IF-MIB Interface Upsert (source=snmp), LLDP Neighbor Collection, may_write Provenance, Poll Pipeline (sysName/sysDescr -> IF-MIB -> bridge-MAC -> LLDP), Read-Only Polling Guarantee (+5 more)

### Community 91 - "test_allocation.py"
Cohesion: 0.43
Nodes (7): _mk_prefix(), test_address_crud_and_dup_guard(), test_allocation_skips_existing(), test_concurrent_allocation_unique(), alloc(), test_exhausted_prefix_conflicts(), test_sequential_allocation_skips_boundaries()

### Community 92 - "_positional_columns"
Cohesion: 0.29
Nodes (4): _col_class(), _positional_columns(), Dominant content class of a column sample., Headerless sheet: locate the IP column, then assign the remaining canonical…

### Community 93 - "Row Ordering Tests"
Cohesion: 0.22
Nodes (21): auth_on(), _circuit_order(), _login(), _mk_circuits(), _mkuser(), AsyncClient, AsyncSession, fixture (+13 more)

### Community 94 - "test_settings.py"
Cohesion: 0.17
Nodes (15): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, Every new Settings > Features key is runtime-editable; untouched keys keep the…, test_backup_files_report_effective_schedule() (+7 more)

### Community 95 - "utils.ts"
Cohesion: 0.06
Nodes (63): EMPTY_FORM, FACES, FormState, KINDS, PortRow, SPEED_PRESETS, metadata, IPAM_FAMILIES (+55 more)

### Community 96 - "group-client.tsx"
Cohesion: 0.07
Nodes (36): DashboardPage(), DragSession, errDetail(), findDevice(), GroupClient(), moveDevice(), metadata, RackDetailPage() (+28 more)

### Community 97 - "network.py"
Cohesion: 0.20
Nodes (10): _ip(), NetworkCreate, NetworkDhcpRange, NetworkOut, NetworkPrefix, NetworkVlanNew, BaseModel, field_validator (+2 more)

### Community 98 - "test_colors.py"
Cohesion: 0.22
Nodes (22): auth_on(), _login(), _mk_rule(), _mk_site(), _mkuser(), AsyncClient, AsyncSession, fixture (+14 more)

### Community 99 - "test_ip_source.py"
Cohesion: 0.32
Nodes (13): _mk_prefix(), V6 provenance — ip_addresses.source: stamping, ownership, filtering. Every…, Manual and imported rows keep their provenance when a scan sees them — observed…, Response bodies carry `source` but never any *_enc-style field., test_csv_import_stamps_import(), test_export_filters_and_carries_source(), test_manual_create_stamps_manual(), test_no_secret_columns_leak() (+5 more)

### Community 100 - "api service (FastAPI/uvicorn backend)"
Cohesion: 0.43
Nodes (8): api service (FastAPI/uvicorn backend), db service (PostgreSQL 16), ipam bridge network (192.0.2.0/24), redis service (Redis 7, appendonly), scanner service (arq worker, host networking), web service (Next.js frontend), ip_addresses table (IPAM data store), ip column type (live IPAM resolution)

### Community 101 - "Demo import data — ALL FICTIONAL"
Cohesion: 0.29
Nodes (7): Demo import data — ALL FICTIONAL, Examples README (demo import data), Files, `Network_Address_DEMO_EN.xlsx` — the edge-case workbook, `Network_Address_DEMO.xlsx` — the clean flagship, Regenerating, VLAN scheme (both workbooks + `demo-vlans.csv`)

### Community 102 - "Prefix Gateway Tests"
Cohesion: 0.22
Nodes (18): _addrs(), _global_vrf_id(), _mkprefix(), Splits are counted arithmetically before materializing: anything over…, test_gateway_clear_removes_only_pristine_row(), test_gateway_never_clobbers_manual_row(), test_gateway_validation(), test_next_ip_never_hands_out_gateway() (+10 more)

### Community 103 - "TypeScript Configuration"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 104 - "hash_password"
Cohesion: 0.16
Nodes (22): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+14 more)

### Community 105 - "test_scan_cidr_tcp_fallback_reports_found"
Cohesion: 0.21
Nodes (8): on_hosts fires once per detection step with that chunk's new IPs — ARP batch…, When L2+L3 find nothing, the TCP fallback publishes its batch too., test_scan_cidr_emits_found_deltas(), fake_icmp(), fake_probe(), fake_ptr(), on_hosts(), test_scan_cidr_tcp_fallback_reports_found()

### Community 106 - "_mklist"
Cohesion: 0.18
Nodes (4): _mklist(), TestBulkRows, TestListCRUD, TestRows

### Community 107 - "docs.ts"
Cohesion: 0.11
Nodes (22): DocsIndexClient(), DocPage(), dynamicParams, generateMetadata(), loadMarkdown(), CommandPalette(), itemsFor(), pagesFor() (+14 more)

### Community 108 - "_FakePool"
Cohesion: 0.20
Nodes (8): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture, Stands in for the arq Redis pool — never actually dispatches work., scan_exclude_networks=10.70.0.64/26 inside scan_networks=10.70.0.0/24: the…, test_scheduler_and_route_share_exclusion_guard()

### Community 109 - "shortcuts.ts"
Cohesion: 0.53
Nodes (5): moveRowNav(), G_CHORDS, isEditableTarget(), modalOpen(), useGlobalShortcuts()

### Community 110 - "Pages & Attachments"
Cohesion: 0.40
Nodes (4): Attachments, Pages, Pages & Attachments, What's not here (yet)

### Community 111 - "fake_arq"
Cohesion: 0.33
Nodes (3): _Job, fake_arq(), enqueue_job()

### Community 112 - "Search Endpoint Tests"
Cohesion: 0.25
Nodes (14): auth_on(), AsyncClient, fixture, Global /api/v1/search endpoint (UX-3)., Regression: list_addresses ?q= used to crash on a missing column., Site + VRF + prefix + address + one of each workbook entity., _seed(), test_addresses_q_filter_not_broken() (+6 more)

### Community 113 - "reader.py"
Cohesion: 0.24
Nodes (11): Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, _csv_sheet(), load_upload(), load_workbook_bytes(), XLSX/CSV -> sheet matrices (openpyxl read_only streams / csv module)., Drop fully-empty trailing rows/cols for a stable matrix shape., One CSV file -> one SheetMatrix named after the file stem. utf-8-sig first…, Dispatch on container type: ZIP -> xlsx workbook; otherwise try CSV text… (+3 more)

### Community 114 - "Reports"
Cohesion: 0.29
Nodes (6): Email, Export, Not here, Reports, Scoping, Sections

### Community 115 - "test_bridge_macs_parse_and_vlan_passes"
Cohesion: 0.13
Nodes (15): dot1qVlanStaticName + egress bitmaps (static and timeMark.vid current-table)…, ipAddressTable + ipAddressPrefixTable containment, plus ifName / ifPhysAddress…, v4-only agents: ipAddrTable's index IS the address; the mask is an IpAddress…, ipNetToPhysical (ifIndex.atype.addr index) and legacy ipNetToMedia…, _target_patch(), test_walk_arp_both_tables_dedupe(), test_walk_ip_interfaces_legacy_ipadent(), test_walk_ip_interfaces_rfc4293() (+7 more)

### Community 116 - "Changelog Audit Tests"
Cohesion: 0.23
Nodes (12): AsyncClient, tag_assignments.object_id has no FK — deleting a tagged object must drop its…, Tag.assignments is already ORM delete-orphan — each removed assignment lands in…, PATCH settings with a null value deletes the app_settings row — that delete…, /addresses/bulk action=delete used to issue one Core DELETE — invisible to the…, test_bulk_delete_writes_changelog_entries(), test_changelog_captures_ip_status_change(), test_changelog_records_crud() (+4 more)

### Community 117 - "test_workbook_import.py"
Cohesion: 0.08
Nodes (13): Workbook import: normalizer/parser unit tests (no DB) + API e2e., Small synthetic workbook: sites master + one site sheet + circuits., Site sheet documenting a DHCP span AND static stations inside it — the real…, Pool-guard regression: committing a plan whose dhcp range covers documented…, test_commit_twice_rejected(), test_import_e2e(), test_workbook_statics_inside_dhcp_span_import_marked(), TestAssetsParser (+5 more)

### Community 118 - "Cable validation — documented vs observed"
Cohesion: 0.40
Nodes (5): Cabling validation section, Flagged-port badge on device interfaces, Cable mismatches review section, Cable validation — documented vs observed, cable_mismatch feature bullet

### Community 119 - "test_cable_mismatch_event_shape"
Cohesion: 0.50
Nodes (3): emit_new_flags wraps the poll's new_flags into one cable.mismatch event per…, test_cable_mismatch_event_shape(), _rec()

### Community 122 - "test_unmanaged_port_never_flagged"
Cohesion: 0.67
Nodes (3): DeviceInterface, An unmanaged (un-polled) device has no SNMP evidence — its ports can never be…, test_unmanaged_port_never_flagged()

### Community 124 - "prefs.ts"
Cohesion: 0.13
Nodes (22): AppearancePage(), Icon, Item, PAGES, remember(), SearchOut, PrefsInit(), AddrMapView (+14 more)

### Community 127 - "Frontend Dev Dependencies"
Cohesion: 0.20
Nodes (10): devDependencies, autoprefixer, postcss, sharp, tailwindcss, @types/js-yaml, @types/node, @types/react (+2 more)

### Community 135 - "Rack Library Validation Script"
Cohesion: 0.25
Nodes (6): DIR, FACES, LAYOUTS, problems, referenced, slugs

### Community 138 - "NPM Scripts"
Cohesion: 0.29
Nodes (7): scripts, build, build:rack-library, check:rack-library, dev, lint, start

### Community 140 - "Devices Documentation"
Cohesion: 0.29
Nodes (7): API sketch, Device detail, Devices, Devices vs racks, From the IP drawer, Health rollup, The list

### Community 146 - "Documentation Articles"
Cohesion: 0.40
Nodes (5): Docs: IP Addresses, Docs: Devices, Docs: Racks, Docs: Settings, Docs: Subnets

### Community 147 - "Security Policy"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 148 - "Changelog and List Features"
Cohesion: 0.50
Nodes (4): Changelog — global /changelog audit log, Row color storage & coverage, Site list affordances (reorder, pin, inline edit, tags, row color), Tag list management & deletion semantics

### Community 202 - "ChannelKind"
Cohesion: 0.12
Nodes (26): ChannelKind, MonitorKind, MonitorState, str, ChannelCreate, ChannelOut, ChannelTestOut, ChannelUpdate (+18 more)

## Ambiguous Edges - Review These
- `Cable` → `Rack`  [AMBIGUOUS]
  frontend/src/content/docs/cabling.md · relation: conceptually_related_to
- `Stats strip & saved views` → `Monitoring doc (V7)`  [AMBIGUOUS]
  frontend/src/content/docs/inventory.md · relation: semantically_similar_to

## Knowledge Gaps
- **469 isolated node(s):** `nextConfig`, `name`, `version`, `private`, `dev` (+464 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1824 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **45 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Cable` and `Rack`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Stats strip & saved views` and `Monitoring doc (V7)`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._
- **Why does `host()` connect `test_bridge_macs_parse_and_vlan_passes` to `generate_demo_data.py`?**
  _High betweenness centrality (0.372) - this node is a cross-community bridge._
- **Why does `servers_rows()` connect `generate_demo_data.py` to `test_bridge_macs_parse_and_vlan_passes`?**
  _High betweenness centrality (0.372) - this node is a cross-community bridge._
- **Why does `Rack device image library` connect `build-rack-library.mjs` to `Device (first-class host entity)`?**
  _High betweenness centrality (0.287) - this node is a cross-community bridge._
- **Are the 90 inferred relationships involving `IPAddress` (e.g. with `_address_csv_row()` and `_addresses_stmt()`) actually correct?**
  _`IPAddress` has 90 INFERRED edges - model-reasoned connections that need verification._
- **Are the 98 inferred relationships involving `Device` (e.g. with `create_address()` and `update_address()`) actually correct?**
  _`Device` has 98 INFERRED edges - model-reasoned connections that need verification._