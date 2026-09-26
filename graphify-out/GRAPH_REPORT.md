# Graph Report - IpamBox  (2026-09-26)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 5235 nodes · 16459 edges · 256 communities (146 shown, 69 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 1318 edges (avg confidence: 0.91)
- Token cost: 155,928 input · 7,915 output

## Graph Freshness
- Built from commit: `42035781`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Frontend Page Routing
- Device Detail UI Components
- List Page Data Hooks
- Dashboard & Monitoring UI
- Changelog & Discovery UI
- Scan Job Progress Streaming
- Deployment & Accounts Overview
- SNMP Trap Handling
- Rack & Device API
- SNMP Inventory Import Plan
- Monitor Targets API
- Rack API Tests
- Rack Group & Export Models
- Monitor Test Fakes
- Notification Channels API
- Auth & Session Security
- Prefix Detail UI
- Discovery Inbox API
- SNMP Polling Tests
- Device API & Templates
- Generic CRUD Router
- Cable API
- Scan Policy & Notifications
- Migrations & Asset Models
- Network Wizard & Tag GC
- Workbook Import Planner
- Demo Data Generator
- Prefix API
- Custom Lists API
- Device Import IO
- SNMP Service
- Cabling Tests
- Device Model
- Network Scanner & OUI Lookup
- Cable Validation Tests
- Row Color Rules API
- Device Templates API
- IP Source Provenance
- IP Address API
- Rack Import Tests
- Demo Rack Script
- Backup & Scans API
- Device API Tests
- Device Filter UI
- Secrets Encryption
- Backend Dependencies
- Certificate & Service Schemas
- Custom List Extraction
- Frontend Error Pages
- Redis & ARQ Pool
- Test DB Setup
- Device Import Tests
- Review Queue Tests
- Auth API
- Hierarchy Tree UI
- Review Queue Service
- Backup Restore Tests
- Rack Library Utilities
- App Settings Config
- SNMP Trap Receiver
- Topology API Tests
- Workbook Import API
- Cabling Domain Model
- Command Palette Search
- Frontend Dependencies
- VLAN API
- Sheet Classification
- Workbook Cell Normalization
- Review Center API
- Health Checks & Device Templates
- IP Address Domain Concepts
- IP Range API
- Backup Service
- IPAM Export Tests
- Frontend Package Config
- Sites API
- Cabling Models & Schemas
- RBAC Permission Tests
- Device Template Tests
- Device List & Export
- Site Merge Planning
- Workbook Import UI
- Topology Map UI
- Monitoring Domain Concepts
- Maintenance Operations API
- Topology Layout API
- Rack Library Build Script
- Product Feature Docs
- Site Sheet Parsing Tests
- Prefix Split & Stats
- Rack Import Field Mapping
- Tags API
- Cable Validation Service
- Row Ordering Tests
- App Settings Tests
- Rack Elevation UI
- SNMP Inventory UI
- Network Creation API
- Row Color Tests
- Demo Dataset Files
- Rack Editor Drag-and-Drop
- Import Plan Execution
- Prefix Gateway Tests
- TypeScript Configuration
- User Management API
- Device Schemas
- Custom Lists CRUD
- Docs Index Page
- Backup Download and Restore
- Settings API
- Import Provenance and Demo Data
- Scheduled Backup Management
- Search Endpoint Tests
- Workbook Ingestion Pipeline
- Sheet Column Type Inference
- Audit Changelog Hooks
- Changelog Audit Tests
- Workbook Import Tests
- SNMP Enrichment Docs
- Rack Listing and Export
- Sites Master Parser
- Rack Library Attribution
- Rack Library Template UI
- Docs Article Pages
- Command Palette
- Circuit Schemas
- IP Allocation
- Frontend Dev Dependencies
- Dashboard Stats API
- Normalization Unit Tests
- Device Detail Assembly
- MAC Mismatch Resolution
- Circuits Parser
- Fake SMTP Test Helper
- SNMP Bridge and FDB Parsing
- Rack Library Validation Script
- Column Content Classification
- Demo Import Data Docs
- NPM Scripts
- Rack Group Device Moves
- Devices Documentation
- SNMP Polling Scheduler
- Review Dismissals Model
- Device Interface Sync
- Entity CRUD Tests
- Keyboard Shortcuts
- Documentation Articles
- Security Policy
- Changelog and List Features
- SNMP Test Endpoint
- Test Fixtures
- Next.js Environment Types
- Device and Rack Import
- Racks API Docs
- XFF Shim
- SNMP Trap Listener
- Trap Bind Failure Handling
- Rack Image Library Bundle
- Request Type
- Device Model
- Device Interface Model
- GET Handler
- Linked Reference
- Sync Database Session
- Generic Python Builtins
- Generic Python Builtins
- Pydantic Validation Helpers
- Generic Python Types
- Datetime Utilities
- Exception Handling
- Filesystem Paths
- Custom List Type
- Prefix Model
- Scan Job Model
- Device Detail Schema
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
- HTTP PATCH Handlers
- HTTP POST Handlers
- Topology Map Feature
- Security Policy
- Go-to Chords Table

## God Nodes (most connected - your core abstractions)
1. `cn()` - 174 edges
2. `react` - 144 edges
3. `Device` - 97 edges
4. `IPAMError` - 91 edges
5. `get_or_404()` - 89 edges
6. `useAsyncData()` - 87 edges
7. `lucide-react` - 83 edges
8. `useAuth()` - 77 edges
9. `IPAddress` - 71 edges
10. `Button` - 71 edges

## Surprising Connections (you probably didn't know these)
- `SNMP Pull inventory` --semantically_similar_to--> `Inventory sync (Pull inventory)`  [INFERRED] [semantically similar]
  README.md → frontend/src/content/docs/snmp.md
- `CSV export` --semantically_similar_to--> `Address CSV import/export (UTF-8 BOM)`  [INFERRED] [semantically similar]
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
- **Documented vs discovered network sync loop** — readme_ipambox, readme_ipam_hierarchy, readme_scanner, readme_discovery_inbox, readme_review_center [EXTRACTED 0.90]
- **Pull inventory writes VLANs/prefixes/addresses with snmp provenance** — frontend_src_content_docs_snmp_inventory_sync, readme_vlans, frontend_src_content_docs_subnets_prefix, frontend_src_content_docs_addresses_ip_address, frontend_src_content_docs_snmp_import_batch [EXTRACTED 0.90]
- **IpamBox docker-compose service stack** — dockercompose_web, dockercompose_api, dockercompose_scanner, dockercompose_db, dockercompose_redis [EXTRACTED 0.95]
- **Core IPAM hierarchy: Site → VRF → Prefix → IP address** — frontend_src_content_docs_sites_feature, frontend_src_content_docs_vrfs_feature, frontend_src_content_docs_overview_data_model [EXTRACTED 1.00]
- **Scan → reconcile → discovery inbox → address statuses** — frontend_src_content_docs_scans_feature, frontend_src_content_docs_scans_pipeline, frontend_src_content_docs_discovery_feature [EXTRACTED 1.00]
- **Shared backend image (api + worker deps)** — dockercompose_api, dockercompose_scanner, backend_requirements_txt_arq, backend_requirements_txt_scapy, backend_requirements_txt_pysnmp, backend_requirements_txt_sqlalchemy [INFERRED 0.75]
- **Preview → one-transaction apply import pattern** — readme_workbook_importer, frontend_src_content_docs_snmp_inventory_sync, frontend_src_content_docs_racks_smart_bundle, frontend_src_content_docs_snmp_import_batch [INFERRED 0.75]
- **Rack tree bundle (group → racks → devices → interfaces/cables)** — frontend_src_content_docs_racks_rack_group, frontend_src_content_docs_racks_rack, readme_device_inventory, frontend_src_content_docs_racks_smart_bundle [INFERRED 0.75]

## Communities (256 total, 69 thin omitted)

### Community 0 - "Frontend Page Routing"
Cohesion: 0.02
Nodes (118): nextConfig, metadata, metadata, DeviceDetailClient(), metadata, metadata, metadata, metadata (+110 more)

### Community 1 - "Device Detail UI Components"
Cohesion: 0.06
Nodes (93): EMPTY_EDIT, FACE_BADGE, EMPTY_FORM, FACES, FormState, KINDS, parseRange(), PortRow (+85 more)

### Community 2 - "List Page Data Hooks"
Cohesion: 0.08
Nodes (94): CertificatesPage(), EMPTY, CircuitsPage(), EMPTY, DEVICE_VIEWS, DeviceRow, DevicesPage(), EMPTY (+86 more)

### Community 3 - "Dashboard & Monitoring UI"
Cohesion: 0.02
Nodes (101): ACTION_STYLES, CABLE_REASON, DashboardPage(), MonitoringPage(), targetLink(), metadata, DragSession, RackDetailPage() (+93 more)

### Community 4 - "Changelog & Discovery UI"
Cohesion: 0.08
Nodes (70): ACTION_STYLES, BulkResp, DiscoveryPage(), PrintClient(), LabelClient(), FACE_BADGE, PrintClient(), FACE_BADGE (+62 more)

### Community 5 - "Scan Job Progress Streaming"
Cohesion: 0.04
Nodes (73): _job_payload(), SSE stream of scan progress (Redis pub/sub backed)., stream_scan(), gen(), str, ScanJob, ScanStatus, infer_device_type() (+65 more)

### Community 6 - "Deployment & Accounts Overview"
Cohesion: 0.05
Nodes (89): api service (FastAPI/uvicorn backend), db service (PostgreSQL 16), ipam bridge network (192.0.2.0/24), redis service (Redis 7, appendonly), scanner service (arq worker, host networking), web service (Next.js frontend), Accounts & Roles, Insecure mode (IPAMBOX_ALLOW_INSECURE) (+81 more)

### Community 7 - "SNMP Trap Handling"
Cohesion: 0.09
Nodes (64): _apply_link_state(), _clear_unmanaged_flag(), _decode(), ensure(), _flag_unmanaged(), handle_trap(), datetime, _resolve_device() (+56 more)

### Community 8 - "Rack & Device API"
Cohesion: 0.07
Nodes (66): _check_refs(), create_device(), create_rack(), delete_device(), delete_rack(), _device_out(), _devices(), _export_name() (+58 more)

### Community 9 - "SNMP Inventory Import Plan"
Cohesion: 0.06
Nodes (59): ImportBatchStatus, str, apply_plan(), build_plan(), collect_inventory(), _fold(), inventory_fingerprint(), new_batch() (+51 more)

### Community 10 - "Monitor Targets API"
Cohesion: 0.07
Nodes (64): check_now(), _check_refs(), create_target(), delete_target(), _filters(), _get(), get_target(), list_targets() (+56 more)

### Community 11 - "Rack API Tests"
Cohesion: 0.09
Nodes (66): _carrier(), _dev(), _group(), _imports(), _mount(), _next_free(), AsyncClient, AsyncSession (+58 more)

### Community 12 - "Rack Group & Export Models"
Cohesion: 0.06
Nodes (61): RackGroup, A bayed row: racks ordered left-to-right as they stand in the DC., ip_display(), Any, Normalize asyncpg-returned ipaddress objects / strings to display form. INET…, to_int(), device_export_rows(), _fold() (+53 more)

### Community 13 - "Monitor Test Fakes"
Cohesion: 0.04
Nodes (46): _FakeArqPool, _FakeRedis, _Job, _login(), _mk_device(), _mk_prefix_and_addr(), _mkuser(), V7 monitoring + notification channels. Covers target CRUD/RBAC, the exactly-… (+38 more)

### Community 14 - "Notification Channels API"
Cohesion: 0.06
Nodes (62): _config_fields(), create_channel(), delete_channel(), _get(), get_channel(), list_channels(), notification_log(), _out() (+54 more)

### Community 15 - "Auth & Session Security"
Cohesion: 0.05
Nodes (66): get_settings(), AsyncSession, Request, Guard for every API route. Returns the User, or None in allow_insecure mode., require_auth(), get_redis(), Shared process-wide Redis client. Do NOT aclose() it per call — connections…, clear_login_failures() (+58 more)

### Community 16 - "Prefix Detail UI"
Cohesion: 0.06
Nodes (55): metadata, IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, SplitDialog(), SplitPlan, toggleIn() (+47 more)

### Community 17 - "Discovery Inbox API"
Cohesion: 0.06
Nodes (48): confirm_discovered(), ConfirmBody, list_discovered(), AsyncSession, BaseModel, get, post, Unconfirmed hosts found by scanners, pending admin review. No limit -> the full… (+40 more)

### Community 18 - "SNMP Polling Tests"
Cohesion: 0.12
Nodes (56): _device(), _down(), _enable(), _iface(), _ifrow(), _ip(), _link_binds(), _mock_poll() (+48 more)

### Community 19 - "Device API & Templates"
Cohesion: 0.07
Nodes (59): apply_device_template(), _check_iface_refs(), _check_refs(), create_device(), create_interface(), delete_device(), delete_interface(), generate_interfaces() (+51 more)

### Community 20 - "Generic CRUD Router"
Cohesion: 0.08
Nodes (53): _crud_router(), create_item(), delete_item(), get_item(), list_items(), reorder_items(), update_item(), _check_site() (+45 more)

### Community 21 - "Cable API"
Cohesion: 0.09
Nodes (51): _cable_out(), _check_ends(), create_cable(), delete_cable(), _get_cable(), _get_interface(), interfaces_match_free_text(), list_cables() (+43 more)

### Community 22 - "Scan Policy & Notifications"
Cohesion: 0.07
Nodes (51): _lan_info(), LAN identity detected by the host-networked worker (written to Redis). Falls…, set_actor(), emit(), Any, Fan out to every enabled channel. Returns deliveries attempted., get_effective(), AsyncSession (+43 more)

### Community 23 - "Migrations & Asset Models"
Cohesion: 0.09
Nodes (31): do_run_migrations(), run_migrations_online(), CRUD routers for the workbook-imported entity families. Circuits, certificates,…, Asset, AssetKind, str, SW/HW catalog rows (תוכנות וחומרות) and serial-number inventory…, Base (+23 more)

### Community 24 - "Network Wizard & Tag GC"
Cohesion: 0.08
Nodes (39): POST /networks — the "add network" wizard endpoint (V6.1). One call creates or…, after_flush(), before_flush(), SyncSession, tag_assignments garbage collection. TagAssignment references its target…, Delete assignments whose target no longer exists. For non-ORM write paths…, register(), sweep_orphans() (+31 more)

### Community 25 - "Workbook Import Planner"
Cohesion: 0.09
Nodes (17): parse_sites_master_records(), _Planner, (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Folded sheet title vs site name/code — word-boundary matching so 'int' doesn't…, Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new…, Resolve a 10.{second}.x sheet — site_number is only meaningful inside the… (+9 more)

### Community 26 - "Demo Data Generator"
Cohesion: 0.09
Nodes (49): assets_rows(), _assign_site_sheets(), _assign_site_sheets_clean(), build_en_workbook(), build_mixed_workbook(), build_sites(), certificates_rows(), circuits_rows() (+41 more)

### Community 27 - "Prefix API"
Cohesion: 0.10
Nodes (42): allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), _prefix_rows() (+34 more)

### Community 28 - "Custom Lists API"
Cohesion: 0.10
Nodes (45): bulk_rows(), _check_columns(), create_list(), create_row(), delete_list(), delete_row(), get_list(), list_lists() (+37 more)

### Community 29 - "Device Import IO"
Cohesion: 0.10
Nodes (47): str, RackFace, _carrier_diff_name(), _err(), _find_carrier(), _float_field(), _int_field(), _ip_tokens() (+39 more)

### Community 30 - "SNMP Service"
Cohesion: 0.12
Nodes (43): _auth(), _context(), _cred(), _get(), _idx_inet(), _idx_int(), _idx_tail_ints(), _index_suffix() (+35 more)

### Community 31 - "Cabling Tests"
Cohesion: 0.13
Nodes (46): _backup_bytes(), _cable(), _device(), _gen(), _iface(), _ip(), _login(), _mkuser() (+38 more)

### Community 32 - "Device Model"
Cohesion: 0.09
Nodes (36): Device, Base, apply_device_import(), _Occupancy, Write the ok rows in one transaction. Creates go through the create path's…, Simulated rack occupancy: DB occupants plus earlier batch rows, kept current…, apply_device_patch(), carrier_children() (+28 more)

### Community 33 - "Network Scanner & OUI Lookup"
Cohesion: 0.06
Nodes (37): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), _host_chunks(), _icmp_checksum(), _icmp_echo_packet(), _icmp_socket() (+29 more)

### Community 34 - "Cable Validation Tests"
Cohesion: 0.23
Nodes (42): poll_device(), _cable(), _commit_fresh(), _device(), _enable(), _flag(), _fresh_iface(), _iface() (+34 more)

### Community 35 - "Row Color Rules API"
Cohesion: 0.09
Nodes (36): create_rule(), delete_rule(), get_rule(), list_rules(), preview_rule(), AsyncSession, delete, get (+28 more)

### Community 36 - "Device Templates API"
Cohesion: 0.09
Nodes (29): create_template(), delete_template(), _get(), get_template(), instantiate_template(), list_templates(), AsyncSession, delete (+21 more)

### Community 37 - "IP Source Provenance"
Cohesion: 0.08
Nodes (43): may_write(), Field-ownership check for source-stamped rows (ip_addresses et al.). True when…, _apply_bridge_links(), _flag(), Any, AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile() (+35 more)

### Community 38 - "IP Address API"
Cohesion: 0.09
Nodes (43): _address_csv_row(), _addresses_stmt(), bulk_addresses(), BulkBody, _check_interface_link(), create_address(), delete_address(), export_addresses() (+35 more)

### Community 39 - "Rack Import Tests"
Cohesion: 0.16
Nodes (42): _bundle(), _by_sheet(), _cable(), _csv(), _device(), _group(), _iface(), _import() (+34 more)

### Community 40 - "Demo Rack Script"
Cohesion: 0.08
Nodes (36): Api, apply(), _device_payload(), emit_zip(), find_one(), _KeepMethodRedirect, layout_doc(), main() (+28 more)

### Community 41 - "Backup & Scans API"
Cohesion: 0.10
Nodes (30): list_changelog(), AsyncSession, get, cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), list_scans() (+22 more)

### Community 42 - "Device API Tests"
Cohesion: 0.14
Nodes (38): _cable(), _device(), _group(), _iface(), _ip(), _login(), _mkuser(), _prefix() (+30 more)

### Community 43 - "Device Filter UI"
Cohesion: 0.08
Nodes (35): ChangelogPage(), metadata, DEVICE_FILTER_PARAMS, DEVICE_TEXT_PARAMS, DeviceFilterPanel(), DeviceFilterState, DeviceTextParam, FACES (+27 more)

### Community 44 - "Secrets Encryption"
Cohesion: 0.10
Nodes (34): _data_key(), decrypt_str(), encrypt_str(), _master_key(), Exception, Secrets at rest — the credential contract v7/v8/v12/v14 build on. A single…, Unseal a "v1:…" blob. Strict prefix check — unknown formats, malformed payloads…, Base for secrets-service failures — never carries secret material. (+26 more)

### Community 45 - "Backend Dependencies"
Cohesion: 0.11
Nodes (35): alembic==1.14.0, asyncpg==0.30.0, httpx==0.28.1, psutil==6.1.0, pydantic==2.10.3, pydantic-settings==2.6.1, pytest==8.3.4, pytest-asyncio==0.25.0 (+27 more)

### Community 46 - "Certificate & Service Schemas"
Cohesion: 0.07
Nodes (22): field_validator, CertificateCreate, CertificateOut, CertificateUpdate, BaseModel, field_validator, hex_color_or_none(), Shared row/tag color validator: #rrggbb, normalized to lowercase. (+14 more)

### Community 47 - "Custom List Extraction"
Cohesion: 0.10
Nodes (24): ListTarget, Import a sheet as a custom list (user-selected or suggested)., _cell_text(), extract_list_table(), pick_key_column(), Custom-list extraction: turn any sheet into {columns, rows} for a list. Unlike…, SheetMatrix -> (column defs, row dicts). columns: [{key, label, type, options?,…, Default merge column: first non-date/ip column filled in most rows (the… (+16 more)

### Community 49 - "Redis & ARQ Pool"
Cohesion: 0.08
Nodes (32): ArqRedis, close_arq_pool(), close_redis(), get_arq_pool(), Shut down the shared client — lifespan/worker shutdown only., Shared ARQ pool — callers must not close() it per job., redis_settings_from_url(), lifespan() (+24 more)

### Community 50 - "Test DB Setup"
Cohesion: 0.11
Nodes (26): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., _split_dsn() (+18 more)

### Community 51 - "Device Import Tests"
Cohesion: 0.20
Nodes (34): _csv(), _device(), _group(), _import(), _ip(), _login(), _mkuser(), _prefix() (+26 more)

### Community 52 - "Review Queue Tests"
Cohesion: 0.20
Nodes (35): _device(), _flag_mismatch(), _iface(), _ip(), _login(), _mkuser(), _prefix(), AsyncClient (+27 more)

### Community 53 - "Auth API"
Cohesion: 0.15
Nodes (33): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+25 more)

### Community 54 - "Hierarchy Tree UI"
Cohesion: 0.12
Nodes (25): metadata, ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), Breadcrumbs(), Crumb (+17 more)

### Community 55 - "Review Queue Service"
Cohesion: 0.15
Nodes (32): _aging_discovery_items(), build_review(), _cable_mismatch_items(), _cert_items(), dismiss(), _dismissal_map(), _dup_mac_items(), _emit() (+24 more)

### Community 56 - "Backup Restore Tests"
Cohesion: 0.16
Nodes (32): _backup_bytes(), _envelope_bytes(), _mkusers(), Hand-craft a backup envelope (e.g. with a forged users table)., Guard: every ORM table must be backed up (or explicitly excluded). Adding a new…, Fresh-server scenario: the migration-seeded Global VRF is replaced by the…, Fresh-server scenario: the target's admins survive; its non-admin set is fully…, A backup carrying an assignment for a missing object (e.g. taken while orphans… (+24 more)

### Community 57 - "Rack Library Utilities"
Cohesion: 0.10
Nodes (32): ABBREV_TO_CATEGORY, canonicalCategory(), CATEGORY_TO_ABBREV, clip(), compareVersions(), decodeShareUrl(), DeviceLike, deviceTypeTables() (+24 more)

### Community 58 - "App Settings Config"
Cohesion: 0.09
Nodes (22): Any, psycopg2-style URL for alembic offline mode / scripts., Settings, Effective, _env_sourced(), Any, Exception, Runtime-editable settings: app_settings rows override env defaults. Each public… (+14 more)

### Community 59 - "SNMP Trap Receiver"
Cohesion: 0.09
Nodes (26): _apply_link_state(), _clear_unmanaged_flag(), _decode(), ensure(), _flag_unmanaged(), handle_trap(), SNMP trap receiver (V8.1) — near-realtime link state. The poll lane…, (transportDomain, transportAddress) -> the sender's IP string. asyncio's UDP… (+18 more)

### Community 60 - "Topology API Tests"
Cohesion: 0.20
Nodes (31): AsyncClient, auth_on(), _cable(), _device(), _edge(), _gen(), _graph(), _iface() (+23 more)

### Community 61 - "Workbook Import API"
Cohesion: 0.13
Nodes (29): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+21 more)

### Community 62 - "Cabling Domain Model"
Cohesion: 0.11
Nodes (32): IPAddress, connected_interface_id (structured far-end port link), connected_ip (host-side NIC binding), DeviceInterface (device-owned port), L1 trace (cable path walk), match-free-text transition endpoint, One-cable-per-interface rule, Front/back port pairing (pair partner / pair_interface_id) (+24 more)

### Community 63 - "Command Palette Search"
Cohesion: 0.17
Nodes (27): _folded(), AsyncSession, get, Cross-object search for the command palette. One GET returns grouped matches…, Column expression with Hebrew final letters folded — pairs with fold_hebrew()…, Short label for a list-row search hit: key-column value, else the first non-…, _row_label(), search() (+19 more)

### Community 64 - "Frontend Dependencies"
Cohesion: 0.06
Nodes (31): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, elkjs, js-yaml, jszip (+23 more)

### Community 65 - "VLAN API"
Cohesion: 0.18
Nodes (26): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+18 more)

### Community 66 - "Sheet Classification"
Cohesion: 0.09
Nodes (24): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, norm_header(), Header cell -> lowercase, single-spaced, for signature matching. Edge…, _blocks() (+16 more)

### Community 67 - "Workbook Cell Normalization"
Cohesion: 0.11
Nodes (27): assemble_ip(), clean(), _clean_octets(), map_status(), mask_to_prefixlen(), network_of(), parse_range_end(), parse_vlan() (+19 more)

### Community 68 - "Review Center API"
Cohesion: 0.12
Nodes (27): dismiss_item(), _flagged_address(), get_review(), mac_mismatch_accept(), mac_mismatch_keep(), AsyncSession, get, IPAddress (+19 more)

### Community 69 - "Health Checks & Device Templates"
Cohesion: 0.09
Nodes (24): healthz(), metrics(), Request, Readiness probe: verifies DB + Redis connectivity., Prometheus-style text exposition of object + scan counters., readyz(), _secrets_not_configured(), DeviceTemplate (+16 more)

### Community 70 - "IP Address Domain Concepts"
Cohesion: 0.13
Nodes (28): IP address, Changelog bypass for state writes, Users & Roles console, Add network wizard, container prefix status, Subnets doc, Gateway & DNS technical rows, GiST exclusion constraint (within-VRF overlap) (+20 more)

### Community 71 - "IP Range API"
Cohesion: 0.15
Nodes (19): _check_range_overlap(), create_range(), delete_range(), list_ranges(), AsyncSession, delete, get, post (+11 more)

### Community 72 - "Backup Service"
Cohesion: 0.12
Nodes (26): _alembic_revisions(), BackupError, BackupPreview, BackupTable, build_backup(), _fail_inflight_scans(), _from_json(), _gunzip() (+18 more)

### Community 73 - "IPAM Export Tests"
Cohesion: 0.16
Nodes (26): _prefix(), _range(), export.csv takes the same filters as the list endpoint — a filtered view…, Same filtered-export treatment on the prefixes CSV (F8)., A documented v6 /64's 2^64 host count must not reach dashboard sums (~1.8e19 >…, A deliberate bulk import documents existing reality — statics inside pools land…, test_address_role_nat_and_bulk(), test_addresses_export_respects_filters() (+18 more)

### Community 74 - "Frontend Package Config"
Cohesion: 0.07
Nodes (25): name, private, version, autoprefixer, clsx, jszip, postcss, @radix-ui/react-dropdown-menu (+17 more)

### Community 75 - "Sites API"
Cohesion: 0.14
Nodes (22): _cascade_site_fields(), create_site(), delete_site(), get_site(), list_sites(), AsyncSession, delete, get (+14 more)

### Community 76 - "Cabling Models & Schemas"
Cohesion: 0.15
Nodes (24): CableKind, InterfaceKind, str, Cabling (V4A): device interfaces and the cables between them. A DeviceInterface…, CableCreate, CableEndOut, CableOut, CableTraceHop (+16 more)

### Community 77 - "RBAC Permission Tests"
Cohesion: 0.28
Nodes (24): str, UserRole, Viewer tier can read lists/rows but every mutation is 403., TestPermissions, login(), mkuser(), other_client(), AsyncClient (+16 more)

### Community 78 - "Device Template Tests"
Cohesion: 0.15
Nodes (24): _device(), _interfaces(), _login(), _mkuser(), AsyncSession, V10.1 device templates: CRUD + RBAC + JSONB layout validation, the apply…, _template(), test_apply_merge_and_reapply_skips() (+16 more)

### Community 79 - "Device List & Export"
Cohesion: 0.11
Nodes (24): _devices_stmt(), export_devices_csv(), export_devices_xlsx(), _export_name(), _export_rows(), _filtered_devices(), _health_class(), list_devices() (+16 more)

### Community 80 - "Site Merge Planning"
Cohesion: 0.17
Nodes (13): _master_row(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind…, Mashapan TA + MATPASH share number 200 — merge + conflict, not a silent… (+5 more)

### Community 81 - "Workbook Import UI"
Cohesion: 0.11
Nodes (19): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, SheetResults() (+11 more)

### Community 82 - "Topology Map UI"
Cohesion: 0.09
Nodes (20): buildTree(), DeviceNodeData, elk, ELK_OPTIONS, ElkChild, GROUP_STYLE, GroupNodeData, IpNodeData (+12 more)

### Community 83 - "Monitoring Domain Concepts"
Cohesion: 0.16
Nodes (25): Address status lifecycle (active/reserved/dhcp/discovered/offline), Check kinds (ping/tcp/http), Monitoring doc (V7), Event sources, down_after hysteresis, Deliberate limits, Monitor target, Notification channel (+17 more)

### Community 84 - "Maintenance Operations API"
Cohesion: 0.17
Nodes (23): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+15 more)

### Community 85 - "Topology Layout API"
Cohesion: 0.22
Nodes (20): get_layout(), put_layout(), AsyncSession, topology_graph(), DiagramLayout, Base, DiagramLayoutOut, DiagramLayoutPut (+12 more)

### Community 86 - "Rack Library Build Script"
Cohesion: 0.13
Nodes (23): arrLen(), attribution(), CATEGORY_COLOUR, CURATED, fetchBuf(), fetchJson(), FRONTEND, FULL_IMPORT (+15 more)

### Community 87 - "Product Feature Docs"
Cohesion: 0.09
Nodes (24): Accounts & role-based access control, Expiry tracking (badge, certs_expiring_30d dashboard count), Certificates — expiry tracking register, Circuits — WAN circuit register, Circuit fields (line type, Bezeq circuit ID, WAN IP, is_retired), Discovery Inbox — reconciliation queue, Hierarchy tree (/tree) — Site→VRF→Prefix, Tree navigation (click-to-prefix, session expand state) (+16 more)

### Community 88 - "Site Sheet Parsing Tests"
Cohesion: 0.17
Nodes (8): parse_site_sheet(), _matrix(), MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf., Bare 'Name' (Cellular) maps to the hostname field., Non-empty unnamed columns pile into cf['extra'] instead of vanishing (Pelephone…, TestClassify, TestSiteSheetExtras, TestSiteSheetParser

### Community 89 - "Prefix Split & Stats"
Cohesion: 0.16
Nodes (21): split_prefix(), prefix_stats_dict(), Stats payload for one prefix given its address count (no DB access). IPv6…, children(), lowest_free(), parent_chain(), Inclusive [first, last] integer range of host-usable addresses., True when network/broadcast addresses are unusable for hosts (IPv4 <= /30). (+13 more)

### Community 90 - "Rack Import Field Mapping"
Cohesion: 0.11
Nodes (22): import_racks(), Request, Smart rack/group bundle import — V5B's stateless flow for whole trees. Sheets…, _alias_to_field(), apply_mapping_overrides(), auto_map_fields(), auto_map_headers(), remap() (+14 more)

### Community 91 - "Tags API"
Cohesion: 0.23
Nodes (20): assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession, delete (+12 more)

### Community 92 - "Cable Validation Service"
Cohesion: 0.14
Nodes (20): _disproved(), emit_new_flags(), _evaluate(), flag_fingerprint(), flagged_counts(), _known_peer_macs(), _map_lldp(), _norm_mac() (+12 more)

### Community 93 - "Row Ordering Tests"
Cohesion: 0.22
Nodes (21): auth_on(), _circuit_order(), _login(), _mk_circuits(), _mkuser(), AsyncClient, AsyncSession, fixture (+13 more)

### Community 94 - "App Settings Tests"
Cohesion: 0.14
Nodes (17): AppSetting, Runtime-editable setting override. Absent row -> env var -> default., fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture (+9 more)

### Community 95 - "Rack Elevation UI"
Cohesion: 0.20
Nodes (19): CarrierFrameSvg(), DeviceBlockSvg(), deviceImage(), FACE_BADGE, HEALTH_KEY, RackElevation(), RackGeom, RackUGrid() (+11 more)

### Community 96 - "SNMP Inventory UI"
Cohesion: 0.11
Nodes (18): AUTH_PROTOS, EMPTY_CRED, PRIV_PROTOS, SnmpCard(), VERSIONS, ACTION_STYLE, APPLYABLE, fmt() (+10 more)

### Community 97 - "Network Creation API"
Cohesion: 0.16
Nodes (13): create_network(), AsyncSession, post, _ip(), NetworkCreate, NetworkDhcpRange, NetworkOut, NetworkPrefix (+5 more)

### Community 98 - "Row Color Tests"
Cohesion: 0.27
Nodes (19): _login(), _mk_rule(), _mk_site(), _mkuser(), AsyncClient, AsyncSession, Global row colors: manual row_color + rule-computed display_color. Covers the…, test_backup_roundtrips_color_rules() (+11 more)

### Community 99 - "Demo Dataset Files"
Cohesion: 0.16
Nodes (20): Demo CSV files, Fictional demo dataset, Demo import data README, Demo list CSVs (contacts/vlans/servers), Demo VLAN scheme, Network_Address_DEMO.xlsx, Network_Address_DEMO_EN.xlsx, backend/app/services/workbook parser (+12 more)

### Community 100 - "Rack Editor Drag-and-Drop"
Cohesion: 0.20
Nodes (16): DragSession, DropRow(), EditorBlock(), errDetail(), Pending, RackEditor(), canMount(), canPlace() (+8 more)

### Community 101 - "Import Plan Execution"
Cohesion: 0.18
Nodes (17): _apply_list(), commit_batch(), execute_plan(), rep(), _get_or_create_list(), _get_or_create_prefix(), _get_or_create_vlan(), _get_or_create_vrf() (+9 more)

### Community 102 - "Prefix Gateway Tests"
Cohesion: 0.22
Nodes (18): _addrs(), _global_vrf_id(), _mkprefix(), Splits are counted arithmetically before materializing: anything over…, test_gateway_clear_removes_only_pristine_row(), test_gateway_never_clobbers_manual_row(), test_gateway_validation(), test_next_ip_never_hands_out_gateway() (+10 more)

### Community 103 - "TypeScript Configuration"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 104 - "User Management API"
Cohesion: 0.22
Nodes (17): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+9 more)

### Community 105 - "Device Schemas"
Cohesion: 0.19
Nodes (14): DeviceCreate, DeviceDetail, DeviceOut, DeviceUpdate, BaseModel, field_validator, Device entity schemas — a host that may be racked and owns IPs. Placement…, SnmpCredIn (+6 more)

### Community 106 - "Custom Lists CRUD"
Cohesion: 0.18
Nodes (4): _mklist(), TestBulkRows, TestListCRUD, TestRows

### Community 107 - "Docs Index Page"
Cohesion: 0.19
Nodes (11): DocsIndexClient(), metadata, DocsNav(), BY_SLUG, DOC_ARTICLES, DOC_CATEGORIES, DocArticle, DocCategory (+3 more)

### Community 108 - "Backup Download and Restore"
Cohesion: 0.17
Nodes (16): download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, get, post, Request, Restore a backup file (raw .json.gz body). Wipes every data table (users are… (+8 more)

### Community 109 - "Settings API"
Cohesion: 0.19
Nodes (15): _build_out(), _mask_url(), AsyncSession, get, Hide the password in a scheme://user:pass@host URL., read_settings(), update_settings(), LanInfo (+7 more)

### Community 110 - "Import Provenance and Demo Data"
Cohesion: 0.16
Nodes (16): openpyxl==3.1.5, pysnmp==7.1.29, demo-addresses.csv, Network_Address_DEMO.xlsx, Network_Address_DEMO_EN.xlsx, Address source provenance field, import_batch_id provenance, Rack XLSX bundle export/import (+8 more)

### Community 111 - "Scheduled Backup Management"
Cohesion: 0.20
Nodes (15): delete_scheduled_backup(), delete, backup_dir(), delete_backup_file(), list_backup_files(), prune_backups(), Fetch a scheduled backup by file name (path-traversal safe)., Delete a scheduled backup by file name (path-traversal safe). (+7 more)

### Community 112 - "Search Endpoint Tests"
Cohesion: 0.25
Nodes (14): auth_on(), AsyncClient, fixture, Global /api/v1/search endpoint (UX-3)., Regression: list_addresses ?q= used to crash on a missing column., Site + VRF + prefix + address + one of each workbook entity., _seed(), test_addresses_q_filter_not_broken() (+6 more)

### Community 113 - "Workbook Ingestion Pipeline"
Cohesion: 0.24
Nodes (11): Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, _csv_sheet(), load_upload(), load_workbook_bytes(), XLSX/CSV -> sheet matrices (openpyxl read_only streams / csv module)., Drop fully-empty trailing rows/cols for a stable matrix shape., One CSV file -> one SheetMatrix named after the file stem. utf-8-sig first…, Dispatch on container type: ZIP -> xlsx workbook; otherwise try CSV text… (+3 more)

### Community 114 - "Sheet Column Type Inference"
Cohesion: 0.15
Nodes (12): _infer_type(), _ips(), _is_ip_token(), (type, extra) for one column — extra carries options/multi., Row 0 of an unrecognized sheet looks like headers when every cell is a short…, _sniff_header_row(), excel_date(), date (+4 more)

### Community 115 - "Audit Changelog Hooks"
Cohesion: 0.31
Nodes (11): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), Audit trail via session flush hooks. before_flush collects (object, action,…, register(), _repr() (+3 more)

### Community 116 - "Changelog Audit Tests"
Cohesion: 0.23
Nodes (12): AsyncClient, tag_assignments.object_id has no FK — deleting a tagged object must drop its…, Tag.assignments is already ORM delete-orphan — each removed assignment lands in…, PATCH settings with a null value deletes the app_settings row — that delete…, /addresses/bulk action=delete used to issue one Core DELETE — invisible to the…, test_bulk_delete_writes_changelog_entries(), test_changelog_captures_ip_status_change(), test_changelog_records_crud() (+4 more)

### Community 117 - "Workbook Import Tests"
Cohesion: 0.19
Nodes (11): Workbook import: normalizer/parser unit tests (no DB) + API e2e., Small synthetic workbook: sites master + one site sheet + circuits., Site sheet documenting a DHCP span AND static stations inside it — the real…, Pool-guard regression: committing a plan whose dhcp range covers documented…, Commit-time PlanError must 422 AND record the failure. The route rolls back…, test_commit_plan_error_marks_batch_failed(), test_commit_twice_rejected(), test_import_e2e() (+3 more)

### Community 118 - "SNMP Enrichment Docs"
Cohesion: 0.29
Nodes (13): SNMP Enrichment Documentation, Bridge-MAC to connected_interface_id Resolution, Per-VLAN Community Indexing (Cisco FDB), IF-MIB Interface Upsert (source=snmp), LLDP Neighbor Collection, may_write Provenance, Poll Pipeline (sysName/sysDescr -> IF-MIB -> bridge-MAC -> LLDP), Read-Only Polling Guarantee (+5 more)

### Community 119 - "Rack Listing and Export"
Cohesion: 0.26
Nodes (11): _export_racks(), _filtered_racks(), list_racks(), _occupancy_class(), _racks_stmt(), Every SQL-side filter the rack list + exports share — filter parity is the…, SQL set + computed-field facets (occupancy, free-U) run after the aggregate…, Rack (+3 more)

### Community 120 - "Sites Master Parser"
Cohesion: 0.23
Nodes (6): parse_sites_master(), Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins., TestSitesMasterParser

### Community 121 - "Rack Library Attribution"
Cohesion: 0.24
Nodes (11): Air-gap safe bundling, CC0 1.0 Universal license, CC0 1.0 Universal, netbox-community/devicetype-library, Rack library ATTRIBUTION, netbox-community/devicetype-library, Rack device image library, Rack device image library (/rack-library/) (+3 more)

### Community 122 - "Rack Library Template UI"
Cohesion: 0.24
Nodes (11): TemplateDialog(), templateToRows(), Placed, libraryBySlug(), LibraryDevice, loadRackLibrary(), RACK_LIBRARY, ImportDevice (+3 more)

### Community 123 - "Docs Article Pages"
Cohesion: 0.24
Nodes (9): DocPage(), dynamicParams, generateMetadata(), loadMarkdown(), DocsContent(), docCategoryLabel(), getDoc(), react-markdown (+1 more)

### Community 124 - "Command Palette"
Cohesion: 0.31
Nodes (10): CommandPalette(), Icon, Item, itemsFor(), PAGES, pagesFor(), remember(), SearchOut (+2 more)

### Community 125 - "Circuit Schemas"
Cohesion: 0.33
Nodes (5): CircuitCreate, CircuitOut, CircuitUpdate, BaseModel, field_validator

### Community 126 - "IP Allocation"
Cohesion: 0.33
Nodes (9): IPAddress, Atomically allocate the lowest free usable IP in a prefix. SERIALIZES on the…, reserve_next_available(), _mk_prefix(), test_address_crud_and_dup_guard(), test_allocation_skips_existing(), test_concurrent_allocation_unique(), test_exhausted_prefix_conflicts() (+1 more)

### Community 127 - "Frontend Dev Dependencies"
Cohesion: 0.20
Nodes (10): devDependencies, autoprefixer, postcss, sharp, tailwindcss, @types/js-yaml, @types/node, @types/react (+2 more)

### Community 128 - "Dashboard Stats API"
Cohesion: 0.31
Nodes (7): AsyncSession, get, stats(), CableMismatchItem, DashboardStats, MacMismatchItem, BaseModel

### Community 130 - "Device Detail Assembly"
Cohesion: 0.32
Nodes (8): _asset_ref(), _detail(), Device -> DeviceDetail: IPs, asset, site/rack/carrier context, health rollup —…, DeviceIpRef, One of the device's IPs: link id/label + scan status for the table., DeviceIpRef, IpRef, LinkedRef

### Community 131 - "MAC Mismatch Resolution"
Cohesion: 0.50
Nodes (8): accept_scanned_mac(), _clear_flag(), keep_stored_mac(), _mismatch_flag(), IPAddress, Trust the scanner: scanned MAC becomes the stored mac_address., Trust inventory: restore the documented MAC and dismiss the pair so the…, IPAddress

### Community 132 - "Circuits Parser"
Cohesion: 0.29
Nodes (5): parse_site_number(), parse_circuits(), קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., TestCircuitsParser

### Community 134 - "SNMP Bridge and FDB Parsing"
Cohesion: 0.29
Nodes (7): Device, `context` is stored in the cred blob and feeds ContextData on v3 — agents that…, dot1d FDB + basePort→ifIndex map, plus a per-VLAN community pass., test_bridge_macs_parse_and_vlan_passes(), test_v3_context_field_roundtrips_and_reaches_transport(), test_walk_if_mib_parses_columns(), _walk()

### Community 135 - "Rack Library Validation Script"
Cohesion: 0.25
Nodes (6): DIR, FACES, LAYOUTS, problems, referenced, slugs

### Community 136 - "Column Content Classification"
Cohesion: 0.29
Nodes (4): _col_class(), _positional_columns(), Dominant content class of a column sample., Headerless sheet: locate the IP column, then assign the remaining canonical…

### Community 137 - "Demo Import Data Docs"
Cohesion: 0.29
Nodes (7): Demo import data — ALL FICTIONAL, Examples README (demo import data), Files, `Network_Address_DEMO_EN.xlsx` — the edge-case workbook, `Network_Address_DEMO.xlsx` — the clean flagship, Regenerating, VLAN scheme (both workbooks + `demo-vlans.csv`)

### Community 138 - "NPM Scripts"
Cohesion: 0.29
Nodes (7): scripts, build, build:rack-library, check:rack-library, dev, lint, start

### Community 139 - "Rack Group Device Moves"
Cohesion: 0.33
Nodes (7): errDetail(), findDevice(), GroupClient(), moveDevice(), freeByRack(), parseRowDev(), parseRowDrop()

### Community 140 - "Devices Documentation"
Cohesion: 0.29
Nodes (7): API sketch, Device detail, Devices, Devices vs racks, From the IP drawer, Health rollup, The list

### Community 141 - "SNMP Polling Scheduler"
Cohesion: 0.29
Nodes (4): snmp_enabled=0 -> snmp_tick is a no-op; nothing reaches the pool., test_global_kill_switch_enqueues_nothing(), _pool(), test_tick_batches_due_devices_into_one_job()

### Community 142 - "Review Dismissals Model"
Cohesion: 0.33
Nodes (4): Base, Review center (V7.1): operator dismissals for computed findings. Every review…, ReviewDismissal, test_review_dismissals_backed_up_and_audited()

### Community 143 - "Device Interface Sync"
Cohesion: 0.47
Nodes (6): due_device_ids(), AsyncSession, datetime, DeviceInterface, _stamp_device(), _upsert_interfaces()

### Community 145 - "Keyboard Shortcuts"
Cohesion: 0.53
Nodes (5): moveRowNav(), G_CHORDS, isEditableTarget(), modalOpen(), useGlobalShortcuts()

### Community 146 - "Documentation Articles"
Cohesion: 0.40
Nodes (5): Docs: IP Addresses, Docs: Devices, Docs: Racks, Docs: Settings, Docs: Subnets

### Community 147 - "Security Policy"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 148 - "Changelog and List Features"
Cohesion: 0.50
Nodes (4): Changelog — global /changelog audit log, Row color storage & coverage, Site list affordances (reorder, pin, inline edit, tags, row color), Tag list management & deletion semantics

### Community 149 - "SNMP Test Endpoint"
Cohesion: 0.67
Nodes (4): _test(), test_snmp_test_endpoint(), _test(), _up()

## Ambiguous Edges - Review These
- `Cable` → `Rack`  [AMBIGUOUS]
  frontend/src/content/docs/cabling.md · relation: conceptually_related_to
- `Monitoring doc (V7)` → `Stats strip & saved views`  [AMBIGUOUS]
  frontend/src/content/docs/inventory.md · relation: semantically_similar_to

## Knowledge Gaps
- **457 isolated node(s):** `NavGroup`, `NavItem`, `DensityChoice`, `FxLevel`, `Prefs` (+452 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1698 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **69 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Cable` and `Rack`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Monitoring doc (V7)` and `Stats strip & saved views`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._
- **Why does `js-yaml` connect `Rack Library Build Script` to `Rack Library Utilities`, `Frontend Package Config`?**
  _High betweenness centrality (0.107) - this node is a cross-community bridge._
- **Why does `DeviceInterface` connect `Device API & Templates` to `Device Detail UI Components`, `Dashboard & Monitoring UI`, `Device Interface Sync`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Why does `Rack device image library` connect `Rack Library Attribution` to `Demo Rack Script`, `Rack Library Build Script`?**
  _High betweenness centrality (0.089) - this node is a cross-community bridge._
- **Are the 61 inferred relationships involving `Device` (e.g. with `instantiate_template()` and `list_cables()`) actually correct?**
  _`Device` has 61 INFERRED edges - model-reasoned connections that need verification._
- **Are the 65 inferred relationships involving `IPAMError` (e.g. with `_get_cable()` and `_get_interface()`) actually correct?**
  _`IPAMError` has 65 INFERRED edges - model-reasoned connections that need verification._