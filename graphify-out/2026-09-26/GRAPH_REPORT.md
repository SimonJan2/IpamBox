# Graph Report - IpamBox  (2026-09-26)

## Corpus Check
- 467 files · ~1,072,488 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 22 file(s) not represented in the graph (top: (none) 8, .csv 6, .ini 2)

## Summary
- 5332 nodes · 17907 edges · 222 communities (135 shown, 48 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 1467 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9bf5609d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- react
- interfaces-panel.tsx
- devices-client.tsx
- index.ts
- lucide-react
- _FakeRedis
- IpamBox
- test_snmp.py
- v1/racks.py
- test_snmp_inventory.py
- Site
- Rack API Tests
- rack_io.py
- test_monitors.py
- NotificationChannel
- User
- cn
- IPAddress
- snmp_inventory.py
- v1/devices.py
- Rack
- cables.py
- worker.py
- services/backup.py
- v1/reports.py
- _Planner
- generate_demo_data.py
- Prefix
- IPAMError
- device_io.py
- services/snmp.py
- test_cabling.py
- Device
- scanner.py
- test_cable_validation.py
- color_rules.py
- v1/device_templates.py
- HostResult
- get_or_404
- test_rack_io.py
- demo_rack_dc.py
- test_reports.py
- test_devices.py
- device-filter-panel.tsx
- Secrets Encryption
- backend/requirements.txt
- hex_color_or_none
- test_lists.py
- Frontend Error Pages
- test_auth.py
- test_scanner.py
- test_device_io.py
- test_review.py
- Smart import dialog
- tree-client.tsx
- services/review.py
- Backup Restore Tests
- rackula.ts
- runtime_settings.py
- channels.py
- test_topology.py
- preview_import
- Device (first-class host entity)
- Command Palette Search
- Frontend Dependencies
- vlans.py
- v1/monitors.py
- clean
- v1/review.py
- readyz
- IpamBox README
- common.py
- restore_backup
- IPAM Export Tests
- package.json
- sites.py
- services/cabling.py
- RBAC Permission Tests
- test_device_templates.py
- vrfs.py
- _matrix
- Workbook Import UI
- topology-map.tsx
- Monitoring doc (V7)
- maintenance.py
- v1/topology.py
- build-rack-library.mjs
- Product Feature Docs
- parse_site_sheet
- schemas/import_batch.py
- import_devices
- tags.py
- DeviceInterface
- Row Ordering Tests
- test_settings.py
- templates-client.tsx
- smart-import-dialog.tsx
- network.py
- test_colors.py
- test_ip_source.py
- api service (FastAPI/uvicorn backend)
- trace_path
- Prefix Gateway Tests
- TypeScript Configuration
- users.py
- test_scan_cidr_tcp_fallback_reports_found
- _mklist
- Docs Index Page
- _FakePool
- rule_matches
- check_target
- auth_on
- Search Endpoint Tests
- upload_workbook
- Reports
- test_bridge_macs_parse_and_vlan_passes
- Changelog Audit Tests
- test_workbook_import.py
- Cable validation — documented vs observed
- test_cable_mismatch_event_shape
- parse_sites_master
- test_channel_test_endpoint
- test_unmanaged_port_never_flagged
- Docs Article Pages
- Command Palette
- Circuit Schemas
- auth_on
- Frontend Dev Dependencies
- stats
- TestNormalize
- ReviewDismissal
- Fake SMTP Test Helper
- Rack Library Validation Script
- NPM Scripts
- Devices Documentation
- Entity CRUD Tests
- Documentation Articles
- Security Policy
- Changelog and List Features
- key
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
1. `cn()` - 179 edges
2. `IPAddress` - 165 edges
3. `Device` - 150 edges
4. `react` - 150 edges
5. `IPAMError` - 125 edges
6. `get_or_404()` - 97 edges
7. `useAsyncData()` - 91 edges
8. `User` - 90 edges
9. `Site` - 89 edges
10. `lucide-react` - 87 edges

## Surprising Connections (you probably didn't know these)
- `SNMP Pull inventory` --semantically_similar_to--> `Inventory sync (Pull inventory)`  [INFERRED] [semantically similar]
  README.md → frontend/src/content/docs/snmp.md
- `CSV export` --semantically_similar_to--> `Address CSV import/export (UTF-8 BOM)`  [INFERRED] [semantically similar]
  frontend/src/content/docs/devices.md → README.md
- `Smart import dialog` --semantically_similar_to--> `Excel workbook import (per-sheet detection, dry-run, all-or-nothing/partial commit)`  [INFERRED] [semantically similar]
  frontend/src/content/docs/devices.md → README.md
- `Rack` --semantically_similar_to--> `Rack elevations & rack groups`  [INFERRED] [semantically similar]
  frontend/src/content/docs/racks.md → README.md
- `Stats strip & saved views` --semantically_similar_to--> `Monitoring doc (V7)`  [AMBIGUOUS] [semantically similar]
  frontend/src/content/docs/inventory.md → frontend/src/content/docs/monitoring.md

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

## Communities (222 total, 48 thin omitted)

### Community 0 - "react"
Cohesion: 0.02
Nodes (119): nextConfig, metadata, ACTION_STYLES, ChangelogPage(), metadata, metadata, DashboardPage(), DeviceDetailClient() (+111 more)

### Community 1 - "interfaces-panel.tsx"
Cohesion: 0.04
Nodes (68): metadata, viewport, AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS, NavGroup (+60 more)

### Community 2 - "devices-client.tsx"
Cohesion: 0.08
Nodes (115): CertificatesPage(), EMPTY, CircuitsPage(), EMPTY, DEVICE_VIEWS, DeviceRow, DevicesPage(), EMPTY (+107 more)

### Community 3 - "index.ts"
Cohesion: 0.03
Nodes (97): looksLikeIpv4(), NetworkWizard(), Step, Stepper(), STEPS, AUTH_PROTOS, EMPTY_CRED, PRIV_PROTOS (+89 more)

### Community 4 - "lucide-react"
Cohesion: 0.07
Nodes (75): ACTION_STYLES, CABLE_REASON, BulkResp, CapacityBars(), STATUS_HEX, StatusDonut(), CABLE_REASON, DELETE_PATH (+67 more)

### Community 5 - "_FakeRedis"
Cohesion: 0.09
Nodes (24): Exception, Raised inside the pipeline when the user cancels the scan., ScanCancelled, _api_cancel(), _FakeRedis, _mk_job(), In-memory stand-in for the worker's redis client (get/set/publish)., Point the worker at the test DB (sf) and the fake redis client. (+16 more)

### Community 6 - "IpamBox"
Cohesion: 0.13
Nodes (48): Accounts & Roles, Insecure mode (IPAMBOX_ALLOW_INSECURE), The four roles (Administrator/Operator/Contributor/Viewer), Session-cookie authentication, Address roles (vip/vrrp/hsrp/glbp/carp/secondary), Address CSV import/export, IP Addresses, IP drawer (+40 more)

### Community 7 - "test_snmp.py"
Cohesion: 0.06
Nodes (84): _apply_link_state(), _clear_unmanaged_flag(), _flag_unmanaged(), handle_trap(), datetime, (transportDomain, transportAddress) -> the sender's IP string. asyncio's UDP…, Mark a documented-but-uncredentialed sender for the review queue. The flag is a…, A resolved trap retires the flag — the sender turned out managed. (+76 more)

### Community 8 - "v1/racks.py"
Cohesion: 0.08
Nodes (53): _check_refs(), create_device(), create_rack(), delete_device(), delete_rack(), _device_out(), _devices(), _get_device() (+45 more)

### Community 9 - "test_snmp_inventory.py"
Cohesion: 0.09
Nodes (46): _bare_device(), _clean_walk(), _device(), _enable(), _ip(), _mock_inv(), _test(), _prefix() (+38 more)

### Community 10 - "Site"
Cohesion: 0.06
Nodes (58): MonitorState, MonitorTarget, V7 — continuous monitoring targets + outbound notification channels., One monitored endpoint — resolves to a concrete IP at check time.…, Site, Usable-IPv4-capacity SQL expression — the dashboard's accounting rule. IPv4…, v4_usable_expr(), apply_result() (+50 more)

### Community 11 - "Rack API Tests"
Cohesion: 0.09
Nodes (66): _carrier(), _dev(), _group(), _imports(), _mount(), _next_free(), AsyncClient, AsyncSession (+58 more)

### Community 12 - "rack_io.py"
Cohesion: 0.07
Nodes (50): _float_field(), _fold(), _name_map(), _parse_id(), #5' or '5' -> 5; None when the cell isn't an id reference., #id' or folded-name lookup -> (row, error). Ambiguity is an error — a coin flip…, _resolve_named(), apply_bundle() (+42 more)

### Community 13 - "test_monitors.py"
Cohesion: 0.06
Nodes (41): hash_password(), auth_on(), _FakeArqPool, key(), _login(), _mk_device(), _mk_prefix_and_addr(), _mkuser() (+33 more)

### Community 14 - "NotificationChannel"
Cohesion: 0.10
Nodes (31): NotificationChannel, NotificationLog, Outbound sink. ``config`` holds non-secret fields per kind; ``secret_enc`` is…, Append-only delivery attempt log — swept by ``notify_retention_days``., _deliver(), _DeliveryFailed, emit(), _log() (+23 more)

### Community 15 - "User"
Cohesion: 0.04
Nodes (121): do_run_migrations(), run_migrations_online(), auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session() (+113 more)

### Community 16 - "cn"
Cohesion: 0.05
Nodes (73): ImportListDialog(), IpCell(), SortableColRow(), IP_ROLES, IP_STATUSES, RANGE_ROLES, SplitDialog(), SplitPlan (+65 more)

### Community 17 - "IPAddress"
Cohesion: 0.07
Nodes (59): _address_csv_row(), bulk_addresses(), BulkBody, import_addresses(), ImportRow, _parse_statuses(), BaseModel, post (+51 more)

### Community 18 - "snmp_inventory.py"
Cohesion: 0.08
Nodes (35): may_write(), Field-ownership check for source-stamped rows (ip_addresses et al.). True when…, device_check_ip(), The address a device target probes: first ACTIVE ip, else the lowest-id row —…, apply_plan(), build_plan(), collect_inventory(), _fold() (+27 more)

### Community 19 - "v1/devices.py"
Cohesion: 0.04
Nodes (101): apply_device_template(), _asset_ref(), _check_iface_refs(), _check_refs(), create_interface(), delete_device(), delete_interface(), _detail() (+93 more)

### Community 20 - "Rack"
Cohesion: 0.07
Nodes (53): _check_site(), create_rack_group(), delete_rack_group(), export_rack_group_xlsx(), _get_group(), get_rack_group(), list_rack_groups(), _ordered_racks() (+45 more)

### Community 21 - "cables.py"
Cohesion: 0.17
Nodes (25): _cable_out(), _check_ends(), create_cable(), delete_cable(), _get_cable(), _get_interface(), interfaces_match_free_text(), list_cables() (+17 more)

### Community 22 - "worker.py"
Cohesion: 0.04
Nodes (102): ArqRedis, cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession (+94 more)

### Community 23 - "services/backup.py"
Cohesion: 0.04
Nodes (97): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), SyncSession, Audit trail via session flush hooks. before_flush collects (object, action,… (+89 more)

### Community 24 - "v1/reports.py"
Cohesion: 0.12
Nodes (28): email_report(), export_section_csv(), export_xlsx(), AsyncSession, get, post, V11 Reports workspace — the whole estate as one payload/workbook. GET…, Send the text digest to every enabled notification channel — summary + link, no… (+20 more)

### Community 25 - "_Planner"
Cohesion: 0.09
Nodes (16): _Planner, (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Folded sheet title vs site name/code — word-boundary matching so 'int' doesn't…, Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new…, Resolve a 10.{second}.x sheet — site_number is only meaningful inside the…, A declared octet block claims the sheet — unless its site is inactive, in which… (+8 more)

### Community 26 - "generate_demo_data.py"
Cohesion: 0.10
Nodes (49): assets_rows(), _assign_site_sheets(), _assign_site_sheets_clean(), build_en_workbook(), build_mixed_workbook(), build_sites(), certificates_rows(), circuits_rows() (+41 more)

### Community 27 - "Prefix"
Cohesion: 0.06
Nodes (77): create_network(), AsyncSession, post, POST /networks — the "add network" wizard endpoint (V6.1). One call creates or…, allocate_next_available(), create_prefix(), export_prefixes(), get_prefix() (+69 more)

### Community 28 - "IPAMError"
Cohesion: 0.08
Nodes (55): list_changelog(), AsyncSession, get, reorder_devices(), bulk_rows(), _check_columns(), create_list(), create_row() (+47 more)

### Community 29 - "device_io.py"
Cohesion: 0.10
Nodes (46): _carrier_diff_name(), _err(), _find_carrier(), _int_field(), _ip_tokens(), _load_refs(), _match(), _Occupancy (+38 more)

### Community 30 - "services/snmp.py"
Cohesion: 0.05
Nodes (79): _apply_bridge_links(), _auth(), _context(), _cred(), due_device_ids(), _get(), _idx_inet(), _idx_int() (+71 more)

### Community 31 - "test_cabling.py"
Cohesion: 0.05
Nodes (82): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., sf() (+74 more)

### Community 32 - "Device"
Cohesion: 0.09
Nodes (38): create_device(), Device, Create a device — unracked inventory by default, or placed directly when…, Device, str, RackFace, apply_device_import(), Write the ok rows in one transaction. Creates go through the create path's… (+30 more)

### Community 33 - "scanner.py"
Cohesion: 0.09
Nodes (33): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), _host_chunks(), _icmp_checksum(), _icmp_echo_packet(), _icmp_socket() (+25 more)

### Community 34 - "test_cable_validation.py"
Cohesion: 0.14
Nodes (58): poll_device(), One full enrichment pass: test -> IF-MIB -> bridge-MAC -> LLDP. Network first,…, _cable(), _commit_fresh(), _device(), _enable(), _flag(), _fresh_iface() (+50 more)

### Community 35 - "color_rules.py"
Cohesion: 0.09
Nodes (32): create_rule(), delete_rule(), get_rule(), list_rules(), preview_rule(), AsyncSession, delete, get (+24 more)

### Community 36 - "v1/device_templates.py"
Cohesion: 0.10
Nodes (32): create_template(), delete_template(), _get(), get_template(), instantiate_template(), list_templates(), AsyncSession, delete (+24 more)

### Community 37 - "HostResult"
Cohesion: 0.07
Nodes (35): _flag(), Any, AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), HostResult, _FakeRedis, In-memory get/set/publish stand-in for the worker's redis client. (+27 more)

### Community 38 - "get_or_404"
Cohesion: 0.09
Nodes (42): _addresses_stmt(), _check_interface_link(), create_address(), delete_address(), export_addresses(), get_address(), list_addresses(), _parse_tag_ids() (+34 more)

### Community 39 - "test_rack_io.py"
Cohesion: 0.15
Nodes (44): auth_on(), _bundle(), _by_sheet(), _cable(), _csv(), _device(), _group(), _iface() (+36 more)

### Community 40 - "demo_rack_dc.py"
Cohesion: 0.08
Nodes (31): Api, apply(), _device_payload(), emit_zip(), find_one(), _KeepMethodRedirect, layout_doc(), main() (+23 more)

### Community 41 - "test_reports.py"
Cohesion: 0.18
Nodes (24): _login(), _mkuser(), AsyncClient, AsyncSession, fixture, V11 Reports workspace — /reports/summary, per-section CSV, multi-sheet XLSX,…, Reports are derived — reads and email writes never hit the audit log., Two sites worth of estate: prefixes in both families, addresses in every… (+16 more)

### Community 42 - "test_devices.py"
Cohesion: 0.12
Nodes (41): auth_on(), _cable(), _device(), _group(), _iface(), _ip(), _login(), _mkuser() (+33 more)

### Community 43 - "device-filter-panel.tsx"
Cohesion: 0.08
Nodes (40): PrefixDetailPage(), toggleIn(), containsFold(), DEVICE_FILTER_PARAMS, DEVICE_TEXT_PARAMS, DeviceFilterPanel(), DeviceFilterState, DeviceTextParam (+32 more)

### Community 44 - "Secrets Encryption"
Cohesion: 0.10
Nodes (34): _data_key(), decrypt_str(), encrypt_str(), _master_key(), Exception, Secrets at rest — the credential contract v7/v8/v12/v14 build on. A single…, Unseal a "v1:…" blob. Strict prefix check — unknown formats, malformed payloads…, Base for secrets-service failures — never carries secret material. (+26 more)

### Community 45 - "backend/requirements.txt"
Cohesion: 0.08
Nodes (49): alembic==1.14.0, asyncpg==0.30.0, httpx==0.28.1, psutil==6.1.0, pydantic==2.10.3, pydantic-settings==2.6.1, pytest==8.3.4, pytest-asyncio==0.25.0 (+41 more)

### Community 46 - "hex_color_or_none"
Cohesion: 0.13
Nodes (11): hex_color_or_none(), Shared row/tag color validator: #rrggbb, normalized to lowercase., field_validator, BaseModel, field_validator, ServiceCreate, ServiceOut, ServiceUpdate (+3 more)

### Community 47 - "test_lists.py"
Cohesion: 0.09
Nodes (28): _cell_text(), extract_list_table(), _infer_type(), _ips(), _is_ip_token(), pick_key_column(), Custom-list extraction: turn any sheet into {columns, rows} for a list. Unlike…, SheetMatrix -> (column defs, row dicts). columns: [{key, label, type, options?,… (+20 more)

### Community 49 - "test_auth.py"
Cohesion: 0.21
Nodes (14): auth_on(), AsyncClient, fixture, Turn auth on for a test, restore insecure mode after, and flush session/lockout…, When the socket peer isn't in ipambox_trusted_proxies, a supplied XFF is…, Spreading failures across many usernames from one IP trips the aggregate lock —…, Five bad logins for one (user, ip) pair must not lock out other users on the…, test_endpoints_require_auth() (+6 more)

### Community 50 - "test_scanner.py"
Cohesion: 0.13
Nodes (21): _global_vrf_id(), _infer_scan_vrf(), Pick the VRF for a scan that didn't specify one. An exact-match prefix living…, _scan_vrf(), WorkerSettings, _extra_vrf(), _global_id(), The cap is a runtime setting: lowering it to 2 rejects a /24. (+13 more)

### Community 51 - "test_device_io.py"
Cohesion: 0.18
Nodes (36): auth_on(), _csv(), _device(), _group(), _import(), _ip(), _login(), _mkuser() (+28 more)

### Community 52 - "test_review.py"
Cohesion: 0.23
Nodes (33): _device(), _flag_mismatch(), _iface(), _ip(), _login(), _mkuser(), _prefix(), AsyncClient (+25 more)

### Community 53 - "Smart import dialog"
Cohesion: 0.10
Nodes (26): GET /api/v1/devices/export.csv, GET /api/v1/devices/export.xlsx, POST /api/v1/devices/import, Carrier two-pass mounting, Changelog / audit history, CSV export, Dry-run preview with per-row {field:[old,new]} diffs, Export dropdown (Devices toolbar) (+18 more)

### Community 54 - "tree-client.tsx"
Cohesion: 0.17
Nodes (21): metadata, ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), collectExpandableKeys(), flattenTree() (+13 more)

### Community 55 - "services/review.py"
Cohesion: 0.12
Nodes (37): ip_display(), Any, Normalize asyncpg-returned ipaddress objects / strings to display form. INET…, to_int(), _aging_discovery_items(), build_review(), _cable_mismatch_items(), _cert_items() (+29 more)

### Community 56 - "Backup Restore Tests"
Cohesion: 0.16
Nodes (32): _backup_bytes(), _envelope_bytes(), _mkusers(), Hand-craft a backup envelope (e.g. with a forged users table)., Guard: every ORM table must be backed up (or explicitly excluded). Adding a new…, Fresh-server scenario: the migration-seeded Global VRF is replaced by the…, Fresh-server scenario: the target's admins survive; its non-admin set is fully…, A backup carrying an assignment for a missing object (e.g. taken while orphans… (+24 more)

### Community 57 - "rackula.ts"
Cohesion: 0.05
Nodes (82): parseRange(), TemplateDialog(), templateToRows(), DeviceFormDialog(), DragSession, DropRow(), EditorBlock(), errDetail() (+74 more)

### Community 58 - "runtime_settings.py"
Cohesion: 0.09
Nodes (20): psycopg2-style URL for alembic offline mode / scripts., Settings, Effective, _env_sourced(), Any, Exception, Runtime-editable settings: app_settings rows override env defaults. Each public…, True when the field's current value differs from its declared default. (+12 more)

### Community 59 - "channels.py"
Cohesion: 0.18
Nodes (22): _config_fields(), create_channel(), delete_channel(), _get(), get_channel(), list_channels(), notification_log(), _out() (+14 more)

### Community 60 - "test_topology.py"
Cohesion: 0.17
Nodes (34): auth_on(), _cable(), _device(), _edge(), _gen(), _graph(), _iface(), _ip() (+26 more)

### Community 61 - "preview_import"
Cohesion: 0.22
Nodes (11): commit_import(), delete_import(), get_import(), list_imports(), preview_import(), AsyncSession, delete, get (+3 more)

### Community 62 - "Device (first-class host entity)"
Cohesion: 0.10
Nodes (36): netbox-community/devicetype-library, IPAddress, Cable, connected_interface_id (structured far-end port link), connected_ip (host-side NIC binding), DeviceInterface (device-owned port), L1 trace (cable path walk), match-free-text transition endpoint (+28 more)

### Community 63 - "Command Palette Search"
Cohesion: 0.17
Nodes (27): _folded(), AsyncSession, get, Cross-object search for the command palette. One GET returns grouped matches…, Column expression with Hebrew final letters folded — pairs with fold_hebrew()…, Short label for a list-row search hit: key-column value, else the first non-…, _row_label(), search() (+19 more)

### Community 64 - "Frontend Dependencies"
Cohesion: 0.06
Nodes (31): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, elkjs, js-yaml, jszip (+23 more)

### Community 65 - "vlans.py"
Cohesion: 0.15
Nodes (28): update_range(), _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), AsyncSession (+20 more)

### Community 66 - "v1/monitors.py"
Cohesion: 0.21
Nodes (20): check_now(), _check_refs(), create_target(), delete_target(), _filters(), _get(), get_target(), list_targets() (+12 more)

### Community 67 - "clean"
Cohesion: 0.06
Nodes (55): row(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., assemble_ip(), clean(), _clean_octets(), excel_date() (+47 more)

### Community 68 - "v1/review.py"
Cohesion: 0.13
Nodes (26): dismiss_item(), _flagged_address(), get_review(), mac_mismatch_accept(), mac_mismatch_keep(), AsyncSession, get, post (+18 more)

### Community 69 - "readyz"
Cohesion: 0.33
Nodes (6): Request, Readiness probe: verifies DB + Redis connectivity., readyz(), _secrets_not_configured(), exception_handler, JSONResponse

### Community 70 - "IpamBox README"
Cohesion: 0.05
Nodes (71): openpyxl==3.1.5, Demo CSV files, Fictional demo dataset, Demo import data README, demo-addresses.csv, Demo list CSVs (contacts/vlans/servers), Network_Address_DEMO.xlsx, Network_Address_DEMO_EN.xlsx (+63 more)

### Community 71 - "common.py"
Cohesion: 0.08
Nodes (31): _check_range_overlap(), create_range(), list_ranges(), AsyncSession, get, post, AssetKind, str (+23 more)

### Community 72 - "restore_backup"
Cohesion: 0.06
Nodes (49): download_backup(), list_scheduled_backups(), AsyncSession, get, post, Request, Restore a backup file (raw .json.gz body). Wipes every data table (users are…, Download a full snapshot (every table except users) as .json.gz.… (+41 more)

### Community 73 - "IPAM Export Tests"
Cohesion: 0.16
Nodes (26): _prefix(), _range(), export.csv takes the same filters as the list endpoint — a filtered view…, Same filtered-export treatment on the prefixes CSV (F8)., A documented v6 /64's 2^64 host count must not reach dashboard sums (~1.8e19 >…, A deliberate bulk import documents existing reality — statics inside pools land…, test_address_role_nat_and_bulk(), test_addresses_export_respects_filters() (+18 more)

### Community 74 - "package.json"
Cohesion: 0.07
Nodes (25): name, private, version, autoprefixer, clsx, elkjs, jszip, postcss (+17 more)

### Community 75 - "sites.py"
Cohesion: 0.17
Nodes (18): _cascade_site_fields(), create_site(), delete_site(), get_site(), list_sites(), AsyncSession, delete, get (+10 more)

### Community 76 - "services/cabling.py"
Cohesion: 0.08
Nodes (32): CableKind, InterfaceKind, str, Cabling (V4A): device interfaces and the cables between them. A DeviceInterface…, CableCreate, CableEndOut, CableOut, CableTraceHop (+24 more)

### Community 77 - "RBAC Permission Tests"
Cohesion: 0.28
Nodes (24): str, UserRole, Viewer tier can read lists/rows but every mutation is 403., TestPermissions, login(), mkuser(), other_client(), AsyncClient (+16 more)

### Community 78 - "test_device_templates.py"
Cohesion: 0.23
Nodes (21): auth_on(), _device(), _interfaces(), _login(), _mkuser(), AsyncClient, AsyncSession, fixture (+13 more)

### Community 79 - "vrfs.py"
Cohesion: 0.18
Nodes (15): create_vrf(), delete_vrf(), get_vrf(), list_vrfs(), AsyncSession, delete, get, post (+7 more)

### Community 80 - "_matrix"
Cohesion: 0.14
Nodes (17): classify_sheet(), (family, header_row_index, warnings). header_row_index = index of the row…, _master_row(), _matrix(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches… (+9 more)

### Community 81 - "Workbook Import UI"
Cohesion: 0.11
Nodes (19): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, SheetResults() (+11 more)

### Community 82 - "topology-map.tsx"
Cohesion: 0.08
Nodes (25): EdgePopup, buildTree(), DeviceNodeData, elk, ELK_OPTIONS, ElkChild, GROUP_STYLE, GroupNode() (+17 more)

### Community 83 - "Monitoring doc (V7)"
Cohesion: 0.15
Nodes (27): Demo .Rackula.zip rack layouts, Address status lifecycle (active/reserved/dhcp/discovered/offline), Check kinds (ping/tcp/http), Monitoring doc (V7), Event sources, down_after hysteresis, Deliberate limits, Monitor target (+19 more)

### Community 84 - "maintenance.py"
Cohesion: 0.18
Nodes (22): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+14 more)

### Community 85 - "v1/topology.py"
Cohesion: 0.17
Nodes (25): get_layout(), put_layout(), AsyncSession, get, Topology map (V10): GET /topology/graph + GET/PUT /topology/layout. One honest…, topology_graph(), DiagramLayout, DiagramLayoutOut (+17 more)

### Community 86 - "build-rack-library.mjs"
Cohesion: 0.09
Nodes (34): Demo .Rackula.zip racks, Air-gap safe bundling, CC0 1.0 Universal license, CC0 1.0 Universal, netbox-community/devicetype-library, Rack library ATTRIBUTION, Rack device image library, Rack device image library (/rack-library/) (+26 more)

### Community 87 - "Product Feature Docs"
Cohesion: 0.09
Nodes (24): Accounts & role-based access control, Expiry tracking (badge, certs_expiring_30d dashboard count), Certificates — expiry tracking register, Circuits — WAN circuit register, Circuit fields (line type, Bezeq circuit ID, WAN IP, is_retired), Discovery Inbox — reconciliation queue, Hierarchy tree (/tree) — Site→VRF→Prefix, Tree navigation (click-to-prefix, session expand state) (+16 more)

### Community 88 - "parse_site_sheet"
Cohesion: 0.11
Nodes (12): _blocks(), _col_class(), parse_site_sheet(), _positional_columns(), Split duplicated column groups (031-style runaway): each block starts at an…, Dominant content class of a column sample., Headerless sheet: locate the IP column, then assign the remaining canonical…, MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf. (+4 more)

### Community 89 - "schemas/import_batch.py"
Cohesion: 0.21
Nodes (12): CommitOptions, ImportBatchOut, ListTarget, PreviewOptions, BaseModel, Per-sheet detection result shown in the wizard., Import a sheet as a custom list (user-selected or suggested)., User-confirmed mapping choices applied before building the plan. (+4 more)

### Community 90 - "import_devices"
Cohesion: 0.12
Nodes (22): import_devices(), Request, Smart device import. Stateless — the file is posted twice: dry-run preview…, _alias_to_field(), apply_mapping_overrides(), auto_map_fields(), auto_map_headers(), remap() (+14 more)

### Community 91 - "tags.py"
Cohesion: 0.22
Nodes (21): assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession, delete (+13 more)

### Community 92 - "DeviceInterface"
Cohesion: 0.14
Nodes (24): DeviceInterface, _disproved(), emit_new_flags(), _evaluate(), flag_fingerprint(), flagged_counts(), _known_peer_macs(), _map_lldp() (+16 more)

### Community 93 - "Row Ordering Tests"
Cohesion: 0.22
Nodes (21): auth_on(), _circuit_order(), _login(), _mk_circuits(), _mkuser(), AsyncClient, AsyncSession, fixture (+13 more)

### Community 94 - "test_settings.py"
Cohesion: 0.17
Nodes (15): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, Every new Settings > Features key is runtime-editable; untouched keys keep the…, test_backup_files_report_effective_schedule() (+7 more)

### Community 95 - "templates-client.tsx"
Cohesion: 0.15
Nodes (13): metadata, EMPTY_FORM, FACES, FormState, KINDS, PortRow, SPEED_PRESETS, TemplatesPage() (+5 more)

### Community 96 - "smart-import-dialog.tsx"
Cohesion: 0.15
Nodes (13): ACTION_STYLE, ColumnMap, DetectResp, FieldOption, fmt(), ImportOption, ImportResp, ResultRows() (+5 more)

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
Cohesion: 0.22
Nodes (13): api service (FastAPI/uvicorn backend), db service (PostgreSQL 16), ipam bridge network (192.0.2.0/24), redis service (Redis 7, appendonly), scanner service (arq worker, host networking), web service (Next.js frontend), import_batch_id provenance, Custom Lists (user-defined tables) (+5 more)

### Community 101 - "trace_path"
Cohesion: 0.23
Nodes (12): cable_for(), match_free_text(), pair_of(), AsyncSession, The L1 path through an interface, ordered end to end. From `start` the walk…, The (at most one) cable terminating at an interface, on either end., Link legacy switch_name/switch_port pairs to real interfaces. For every…, A patch position's front↔back partner on the SAME device. Follows the self-FK… (+4 more)

### Community 102 - "Prefix Gateway Tests"
Cohesion: 0.22
Nodes (18): _addrs(), _global_vrf_id(), _mkprefix(), Splits are counted arithmetically before materializing: anything over…, test_gateway_clear_removes_only_pristine_row(), test_gateway_never_clobbers_manual_row(), test_gateway_validation(), test_next_ip_never_hands_out_gateway() (+10 more)

### Community 103 - "TypeScript Configuration"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 104 - "users.py"
Cohesion: 0.23
Nodes (16): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+8 more)

### Community 105 - "test_scan_cidr_tcp_fallback_reports_found"
Cohesion: 0.21
Nodes (8): on_hosts fires once per detection step with that chunk's new IPs — ARP batch…, When L2+L3 find nothing, the TCP fallback publishes its batch too., test_scan_cidr_emits_found_deltas(), fake_icmp(), fake_probe(), fake_ptr(), on_hosts(), test_scan_cidr_tcp_fallback_reports_found()

### Community 106 - "_mklist"
Cohesion: 0.21
Nodes (3): _mklist(), TestListCRUD, TestRows

### Community 107 - "Docs Index Page"
Cohesion: 0.19
Nodes (11): DocsIndexClient(), metadata, DocsNav(), BY_SLUG, DOC_ARTICLES, DOC_CATEGORIES, DocArticle, DocCategory (+3 more)

### Community 108 - "_FakePool"
Cohesion: 0.20
Nodes (8): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture, Stands in for the arq Redis pool — never actually dispatches work., scan_exclude_networks=10.70.0.64/26 inside scan_networks=10.70.0.0/24: the…, test_scheduler_and_route_share_exclusion_guard()

### Community 109 - "rule_matches"
Cohesion: 0.33
Nodes (10): _as_date(), _as_str(), display_color_for(), _ordered_cmp(), Any, date, -1/0/1 comparing a column value to a rule's value string. Tries date first when…, Does ``rule`` fire on this row? NULL fields never match. (+2 more)

### Community 110 - "check_target"
Cohesion: 0.24
Nodes (10): parse_http_expect(), (ok, error) for an HTTP response against the expectation grammar., check_target(), _http(), _ping(), AsyncClient, Semaphore, Single-host ICMP echo — blocking ping/raw socket in a worker thread. uvloop… (+2 more)

### Community 111 - "auth_on"
Cohesion: 0.22
Nodes (6): _Job, auth_on(), fake_arq(), enqueue_job(), fixture, Turn auth on for a test, restore insecure mode after, and flush session/lockout…

### Community 112 - "Search Endpoint Tests"
Cohesion: 0.25
Nodes (14): auth_on(), AsyncClient, fixture, Global /api/v1/search endpoint (UX-3)., Regression: list_addresses ?q= used to crash on a missing column., Site + VRF + prefix + address + one of each workbook entity., _seed(), test_addresses_q_filter_not_broken() (+6 more)

### Community 113 - "upload_workbook"
Cohesion: 0.14
Nodes (19): _import_dir(), _load_sheets(), ImportBatch, Path, Request, Upload an .xlsx/.csv as raw body (?filename=…). Stores the file, runs sheet…, _safe_stored(), upload_workbook() (+11 more)

### Community 114 - "Reports"
Cohesion: 0.29
Nodes (6): Email, Export, Not here, Reports, Scoping, Sections

### Community 115 - "test_bridge_macs_parse_and_vlan_passes"
Cohesion: 0.40
Nodes (5): dot1d FDB + basePort→ifIndex map, plus a per-VLAN community pass., test_bridge_macs_parse_and_vlan_passes(), test_walk_if_mib_parses_columns(), _walk(), host()

### Community 116 - "Changelog Audit Tests"
Cohesion: 0.23
Nodes (12): AsyncClient, tag_assignments.object_id has no FK — deleting a tagged object must drop its…, Tag.assignments is already ORM delete-orphan — each removed assignment lands in…, PATCH settings with a null value deletes the app_settings row — that delete…, /addresses/bulk action=delete used to issue one Core DELETE — invisible to the…, test_bulk_delete_writes_changelog_entries(), test_changelog_captures_ip_status_change(), test_changelog_records_crud() (+4 more)

### Community 117 - "test_workbook_import.py"
Cohesion: 0.09
Nodes (17): Workbook import: normalizer/parser unit tests (no DB) + API e2e., קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., Small synthetic workbook: sites master + one site sheet + circuits., Site sheet documenting a DHCP span AND static stations inside it — the real…, Pool-guard regression: committing a plan whose dhcp range covers documented…, Commit-time PlanError must 422 AND record the failure. The route rolls back…, test_commit_plan_error_marks_batch_failed() (+9 more)

### Community 118 - "Cable validation — documented vs observed"
Cohesion: 0.40
Nodes (5): Cabling validation section, Flagged-port badge on device interfaces, Cable mismatches review section, Cable validation — documented vs observed, cable_mismatch feature bullet

### Community 119 - "test_cable_mismatch_event_shape"
Cohesion: 0.50
Nodes (3): emit_new_flags wraps the poll's new_flags into one cable.mismatch event per…, test_cable_mismatch_event_shape(), _rec()

### Community 120 - "parse_sites_master"
Cohesion: 0.17
Nodes (9): _master_blocks(), parse_sites_master(), (first, second) octet pairs a master row declares — lets sheet->site matching…, parse_sites_master_records(), Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins. (+1 more)

### Community 122 - "test_unmanaged_port_never_flagged"
Cohesion: 0.67
Nodes (3): DeviceInterface, An unmanaged (un-polled) device has no SNMP evidence — its ports can never be…, test_unmanaged_port_never_flagged()

### Community 123 - "Docs Article Pages"
Cohesion: 0.24
Nodes (9): DocPage(), dynamicParams, generateMetadata(), loadMarkdown(), DocsContent(), docCategoryLabel(), getDoc(), react-markdown (+1 more)

### Community 124 - "Command Palette"
Cohesion: 0.31
Nodes (10): CommandPalette(), Icon, Item, itemsFor(), PAGES, pagesFor(), remember(), SearchOut (+2 more)

### Community 125 - "Circuit Schemas"
Cohesion: 0.33
Nodes (5): CircuitCreate, CircuitOut, CircuitUpdate, BaseModel, field_validator

### Community 127 - "Frontend Dev Dependencies"
Cohesion: 0.20
Nodes (10): devDependencies, autoprefixer, postcss, sharp, tailwindcss, @types/js-yaml, @types/node, @types/react (+2 more)

### Community 128 - "stats"
Cohesion: 0.67
Nodes (3): AsyncSession, get, stats()

### Community 131 - "ReviewDismissal"
Cohesion: 0.17
Nodes (12): ReviewDismissal, accept_scanned_mac(), _clear_flag(), dismiss(), keep_stored_mac(), mac_fingerprint(), _mismatch_flag(), The stable identity of a MAC mismatch: the documented→observed pair. (+4 more)

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

### Community 183 - "key"
Cohesion: 0.67
Nodes (3): key(), fixture, Provision a master key on the cached settings object.

### Community 202 - "ChannelKind"
Cohesion: 0.14
Nodes (22): ChannelKind, MonitorKind, str, ChannelCreate, ChannelOut, ChannelTestOut, ChannelUpdate, MonitorTargetCreate (+14 more)

## Ambiguous Edges - Review These
- `Cable` → `Rack`  [AMBIGUOUS]
  frontend/src/content/docs/cabling.md · relation: conceptually_related_to
- `Monitoring doc (V7)` → `Stats strip & saved views`  [AMBIGUOUS]
  frontend/src/content/docs/inventory.md · relation: semantically_similar_to

## Knowledge Gaps
- **465 isolated node(s):** `nextConfig`, `name`, `version`, `private`, `dev` (+460 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1789 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **48 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Cable` and `Rack`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Monitoring doc (V7)` and `Stats strip & saved views`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._
- **Why does `host()` connect `test_bridge_macs_parse_and_vlan_passes` to `test_snmp_inventory.py`, `generate_demo_data.py`?**
  _High betweenness centrality (0.379) - this node is a cross-community bridge._
- **Why does `servers_rows()` connect `generate_demo_data.py` to `test_bridge_macs_parse_and_vlan_passes`?**
  _High betweenness centrality (0.379) - this node is a cross-community bridge._
- **Why does `Rack device image library` connect `build-rack-library.mjs` to `Device (first-class host entity)`?**
  _High betweenness centrality (0.288) - this node is a cross-community bridge._
- **Are the 90 inferred relationships involving `IPAddress` (e.g. with `_address_csv_row()` and `_addresses_stmt()`) actually correct?**
  _`IPAddress` has 90 INFERRED edges - model-reasoned connections that need verification._
- **Are the 98 inferred relationships involving `Device` (e.g. with `create_address()` and `update_address()`) actually correct?**
  _`Device` has 98 INFERRED edges - model-reasoned connections that need verification._