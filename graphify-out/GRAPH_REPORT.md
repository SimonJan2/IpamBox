# Graph Report - IpamBox  (2026-09-25)

## Corpus Check
- Large corpus: 2609 files · ~1,025,484 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder.

## Summary
- 4563 nodes · 14738 edges · 186 communities (125 shown, 26 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 1149 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Next.js App Pages & Config
- Rack Groups API
- Changelog & List Clients
- Certificates & Circuits Clients
- API Router & Tag GC
- SNMP Enrichment Service
- CRUD Router Factory
- Devices API & Interfaces
- Discovery & List Pages
- Device Detail Client
- Dashboard & SNMP Card UI
- Prefix & Rack Views
- Cables API
- Workbook Entity Models
- Auth & Session Plumbing
- Prefixes API
- Racks Test Helpers
- Changelog & Lists API
- Auth API
- Workbook Parser Utils
- Scan Reconcile
- Docker Compose Services
- Demo Data Generator
- Imports API
- Monitors API
- Color Rules API
- Device Model & Import
- Workbook Planner
- Addresses API
- Monitor Test Fakes
- Notification Channels API
- IP Normalization
- Cabling Tests
- Notify & Runtime Settings
- Common Schemas & Device IO
- Rack IO Tests
- Scan Jobs API
- Secrets Service
- Review Service
- Frontend Error Pages
- Device IO Tests
- Device Test Helpers
- Rackula Import
- Review Tests
- Monitoring & Scans Pages
- Backup Tests & Users
- Test Conftest & DB Setup
- Scanner Probes
- Tags API
- Workbook Import Integration
- Global Search API
- Notification Models
- Sites API & LAN Info
- IPAM Extra Tests
- Rack Group Client
- Review API
- Backup Service
- Frontend Dependencies
- Workbook Import Tests
- Ranges API
- Backend Dependencies
- Frontend Config
- Rack Editor & Device Form
- Device Export & Import Docs
- Import Client
- Custom List Model
- List Parser
- Site Sheet Parser
- Requirements Pins
- Rack Library Builder
- Smart Device Import
- Users API
- RBAC Tests
- Demo Rack Script
- Prefix Tree Page
- Maintenance API
- App Settings Model
- Subnets Docs & Wizard
- Sheet Classification
- Color Rule Tests
- Demo Datasets
- Fake Redis
- Ordering Tests
- Prefix API Tests
- IP-to-Interface Linking
- Monitoring Docs
- TypeScript Config
- Runtime Settings Service
- Backup API
- Settings Read & Masking
- Changelog Service
- List Tests
- Network Schemas
- Source Provenance (may_write)
- Docs Pages
- Appearance & Prefs
- Rack Collision Logic
- Backup File Ops
- Scan Status & SSE
- Sites Master Parser
- Changelog Tests
- Search Tests
- Docs Markdown Loader
- Carrier & Rack Library Docs
- Settings & DB URL
- Scan Fallback Tests
- Rack Library Licensing
- Fake ARQ Pool
- Command Palette
- Frontend Dev Dependencies
- Cabling Concepts
- Dashboard API
- Allocation Tests
- Rack Library Checker
- NPM Scripts
- Devices Docs
- Device RBAC Tests
- Entity CRUD Tests
- ARQ Job Fakes
- Keyboard Shortcuts
- Legacy Bezeq Parser Tests
- Docs Pages Index
- Chart Theme Hook
- Security Policy
- Alembic env
- Secrets Exception Handler
- OUI Vendor Lookup
- Certificates Parser Tests
- test_health_ranking_unit()
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
3. `Device` - 100 edges
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
- **Non-Destructive Enrichment Contract** — frontend_src_content_docs_snmp_md_read_only_polling, frontend_src_content_docs_snmp_md_may_write_provenance, frontend_src_content_docs_snmp_md_stale_dimming [INFERRED 0.85]
- **Backend Dependencies Enabling SNMP Enrichment** — backend_requirements_txt_pysnmp, backend_requirements_txt_cryptography, backend_requirements_txt_arq [INFERRED 0.65]

## Communities (186 total, 26 thin omitted)

### Community 0 - "Next.js App Pages & Config"
Cohesion: 0.02
Nodes (67): nextConfig, metadata, ChangelogPage(), metadata, metadata, DeviceDetailClient(), metadata, metadata (+59 more)

### Community 1 - "Rack Groups API"
Cohesion: 0.05
Nodes (113): _check_site(), create_rack_group(), delete_rack_group(), export_rack_group_xlsx(), _get_group(), get_rack_group(), list_rack_groups(), _ordered_racks() (+105 more)

### Community 2 - "Changelog & List Clients"
Cohesion: 0.10
Nodes (62): ACTION_STYLES, BulkResp, FACE_BADGE, FACE_BADGE, DELETE_PATH, DeleteTarget, DismissTarget, SECTION_ICONS (+54 more)

### Community 3 - "Certificates & Circuits Clients"
Cohesion: 0.09
Nodes (80): CertificatesPage(), EMPTY, CircuitsPage(), EMPTY, DEVICE_VIEWS, DeviceRow, DevicesPage(), EMPTY (+72 more)

### Community 4 - "API Router & Tag GC"
Cohesion: 0.06
Nodes (64): after_flush(), before_flush(), SyncSession, tag_assignments garbage collection. TagAssignment references its target…, register(), healthz(), metrics(), get (+56 more)

### Community 5 - "SNMP Enrichment Service"
Cohesion: 0.06
Nodes (86): AsyncClient, _apply_bridge_links(), _auth(), _context(), _cred(), due_device_ids(), _get(), _idx_int() (+78 more)

### Community 6 - "CRUD Router Factory"
Cohesion: 0.06
Nodes (76): _crud_router(), create_item(), delete_item(), get_item(), list_items(), reorder_items(), update_item(), create_network() (+68 more)

### Community 7 - "Devices API & Interfaces"
Cohesion: 0.05
Nodes (88): _asset_ref(), _check_iface_refs(), _check_refs(), create_device(), create_interface(), delete_device(), delete_interface(), _detail() (+80 more)

### Community 8 - "Discovery & List Pages"
Cohesion: 0.05
Nodes (76): DiscoveryPage(), ImportListDialog(), IpCell(), SortableColRow(), IP_ROLES, IP_STATUSES, RANGE_ROLES, SplitDialog() (+68 more)

### Community 9 - "Device Detail Client"
Cohesion: 0.08
Nodes (59): EMPTY_EDIT, FACE_BADGE, IPAM_FAMILIES, Step, PrefixRow, utilColor(), VrfDialog(), vrfNameFor() (+51 more)

### Community 10 - "Dashboard & SNMP Card UI"
Cohesion: 0.03
Nodes (78): ACTION_STYLES, ExpiryBadge(), AUTH_PROTOS, EMPTY_CRED, PRIV_PROTOS, SnmpCard(), VERSIONS, monitorVariant (+70 more)

### Community 11 - "Prefix & Rack Views"
Cohesion: 0.04
Nodes (70): PrefixDetailPage(), toggleIn(), EMPTY, RACK_VIEWS, RackRow, DEVICE_FILTER_PARAMS, DEVICE_TEXT_PARAMS, DeviceFilterPanel() (+62 more)

### Community 12 - "Cables API"
Cohesion: 0.06
Nodes (68): _cable_out(), _check_ends(), create_cable(), delete_cable(), _get_cable(), _get_interface(), interfaces_match_free_text(), list_cables() (+60 more)

### Community 13 - "Workbook Entity Models"
Cohesion: 0.05
Nodes (45): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, AssetKind, str, IPRole, str, AssetCreate, AssetOut, AssetUpdate (+37 more)

### Community 14 - "Auth & Session Plumbing"
Cohesion: 0.04
Nodes (73): ArqRedis, get_settings(), AsyncSession, Request, Guard for every API route. Returns the User, or None in allow_insecure mode., require_auth(), close_arq_pool(), close_redis() (+65 more)

### Community 15 - "Prefixes API"
Cohesion: 0.07
Nodes (66): allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), _prefix_rows() (+58 more)

### Community 16 - "Racks Test Helpers"
Cohesion: 0.10
Nodes (60): _carrier(), _dev(), _group(), _imports(), _mount(), _next_free(), AsyncClient, _rack() (+52 more)

### Community 17 - "Changelog & Lists API"
Cohesion: 0.07
Nodes (59): list_changelog(), AsyncSession, get, bulk_rows(), _check_columns(), create_list(), create_row(), delete_list() (+51 more)

### Community 18 - "Auth API"
Cohesion: 0.08
Nodes (60): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+52 more)

### Community 19 - "Workbook Parser Utils"
Cohesion: 0.07
Nodes (52): _find_carrier(), _float_field(), _fold(), _name_map(), _parse_id(), carrier cell -> the carrier row. '#id' resolves a stored device; names resolve…, #5' or '5' -> 5; None when the cell isn't an id reference., #id' or folded-name lookup -> (row, error). Ambiguity is an error — a coin flip… (+44 more)

### Community 20 - "Scan Reconcile"
Cohesion: 0.06
Nodes (53): _flag(), Any, AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), HostResult, _global_vrf_id(), _infer_scan_vrf() (+45 more)

### Community 21 - "Docker Compose Services"
Cohesion: 0.09
Nodes (60): api service (FastAPI/uvicorn backend), db service (PostgreSQL 16), ipam bridge network (192.0.2.0/24), redis service (Redis 7, appendonly), scanner service (arq worker, host networking), web service (Next.js frontend), Accounts & Roles, Insecure mode (IPAMBOX_ALLOW_INSECURE) (+52 more)

### Community 22 - "Demo Data Generator"
Cohesion: 0.07
Nodes (58): assets_rows(), _assign_site_sheets(), _assign_site_sheets_clean(), build_en_workbook(), build_mixed_workbook(), build_sites(), certificates_rows(), circuits_rows() (+50 more)

### Community 23 - "Imports API"
Cohesion: 0.07
Nodes (52): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+44 more)

### Community 24 - "Monitors API"
Cohesion: 0.08
Nodes (52): check_now(), _check_refs(), create_target(), delete_target(), _filters(), _get(), get_target(), list_targets() (+44 more)

### Community 25 - "Color Rules API"
Cohesion: 0.07
Nodes (46): create_rule(), delete_rule(), get_rule(), list_rules(), preview_rule(), AsyncSession, delete, get (+38 more)

### Community 26 - "Device Model & Import"
Cohesion: 0.08
Nodes (43): Device, Base, apply_device_import(), _Occupancy, _placement_candidate(), Device, Merged post-patch Device for the occupancy simulation — the same blend…, check_placement -> error row on the plan. Shared by creates and update… (+35 more)

### Community 27 - "Workbook Planner"
Cohesion: 0.08
Nodes (18): parse_sites_master_records(), _Planner, _preview(), (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Folded sheet title vs site name/code — word-boundary matching so 'int' doesn't…, Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new… (+10 more)

### Community 28 - "Addresses API"
Cohesion: 0.07
Nodes (50): _address_csv_row(), _addresses_stmt(), bulk_addresses(), BulkBody, _check_interface_link(), create_address(), delete_address(), export_addresses() (+42 more)

### Community 29 - "Monitor Test Fakes"
Cohesion: 0.05
Nodes (35): _FakeArqPool, _FakeSMTP, _login(), _mk_device(), _mk_prefix_and_addr(), _mkuser(), V7 monitoring + notification channels. Covers target CRUD/RBAC, the exactly-…, Viewer reads targets but can't write/check/delete them. (+27 more)

### Community 30 - "Notification Channels API"
Cohesion: 0.09
Nodes (44): _config_fields(), create_channel(), delete_channel(), _get(), get_channel(), list_channels(), notification_log(), _out() (+36 more)

### Community 31 - "IP Normalization"
Cohesion: 0.08
Nodes (41): assemble_ip(), clean(), _clean_octets(), map_status(), mask_to_prefixlen(), network_of(), norm_header(), parse_range_end() (+33 more)

### Community 32 - "Cabling Tests"
Cohesion: 0.13
Nodes (46): _backup_bytes(), _cable(), _device(), _gen(), _iface(), _ip(), _login(), _mkuser() (+38 more)

### Community 33 - "Notify & Runtime Settings"
Cohesion: 0.09
Nodes (42): set_actor(), emit(), Any, Fan out to every enabled channel. Returns deliveries attempted., get_effective(), AsyncSession, exclusion_hit(), Scan-target policy shared by the API route, the scheduler, and the worker.… (+34 more)

### Community 34 - "Common Schemas & Device IO"
Cohesion: 0.11
Nodes (41): ip_display(), Any, Normalize asyncpg-returned ipaddress objects / strings to display form. INET…, to_int(), _carrier_diff_name(), device_export_rows(), _err(), _int_field() (+33 more)

### Community 35 - "Rack IO Tests"
Cohesion: 0.16
Nodes (42): _bundle(), _by_sheet(), _cable(), _csv(), _device(), _group(), _iface(), _import() (+34 more)

### Community 36 - "Scan Jobs API"
Cohesion: 0.08
Nodes (34): cancel_scan(), _job_payload(), post, str, ScanJob, ScanStatus, cancel_key(), _cancelled() (+26 more)

### Community 37 - "Secrets Service"
Cohesion: 0.10
Nodes (34): _data_key(), decrypt_str(), encrypt_str(), _master_key(), Exception, Secrets at rest — the credential contract v7/v8/v12/v14 build on. A single…, Unseal a "v1:…" blob. Strict prefix check — unknown formats, malformed payloads…, Base for secrets-service failures — never carries secret material. (+26 more)

### Community 38 - "Review Service"
Cohesion: 0.12
Nodes (37): accept_scanned_mac(), _aging_discovery_items(), build_review(), _cert_items(), _clear_flag(), dismiss(), _dismissal_map(), _dup_mac_items() (+29 more)

### Community 40 - "Device IO Tests"
Cohesion: 0.20
Nodes (34): _csv(), _device(), _group(), _import(), _ip(), _login(), _mkuser(), _prefix() (+26 more)

### Community 41 - "Device Test Helpers"
Cohesion: 0.17
Nodes (32): _cable(), _device(), _group(), _iface(), _ip(), _prefix(), AsyncClient, _rack() (+24 more)

### Community 42 - "Rackula Import"
Cohesion: 0.09
Nodes (35): RackulaImportDialog(), ABBREV_TO_CATEGORY, canonicalCategory(), CATEGORY_TO_ABBREV, clip(), compareVersions(), decodeShareUrl(), DeviceLike (+27 more)

### Community 43 - "Review Tests"
Cohesion: 0.22
Nodes (34): _device(), _flag_mismatch(), _iface(), _ip(), _login(), _mkuser(), _prefix(), AsyncClient (+26 more)

### Community 44 - "Monitoring & Scans Pages"
Cohesion: 0.07
Nodes (29): MonitoringPage(), targetLink(), fmtEta(), ScansPage(), AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT (+21 more)

### Community 45 - "Backup Tests & Users"
Cohesion: 0.16
Nodes (33): User, _backup_bytes(), _envelope_bytes(), _mkusers(), Hand-craft a backup envelope (e.g. with a forged users table)., Guard: every ORM table must be backed up (or explicitly excluded). Adding a new…, Fresh-server scenario: the migration-seeded Global VRF is replaced by the…, Fresh-server scenario: the target's admins survive; its non-admin set is fully… (+25 more)

### Community 46 - "Test Conftest & DB Setup"
Cohesion: 0.12
Nodes (25): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., sf() (+17 more)

### Community 47 - "Scanner Probes"
Cohesion: 0.09
Nodes (29): _arp_scan(), _host_chunks(), _icmp_checksum(), _icmp_echo_packet(), _icmp_socket(), _icmp_sweep(), _icmp_sweep_blocking(), infer_device_type() (+21 more)

### Community 48 - "Tags API"
Cohesion: 0.14
Nodes (25): assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession, delete (+17 more)

### Community 49 - "Workbook Import Integration"
Cohesion: 0.15
Nodes (14): _master_row(), _matrix(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind… (+6 more)

### Community 50 - "Global Search API"
Cohesion: 0.17
Nodes (27): _folded(), AsyncSession, get, Cross-object search for the command palette. One GET returns grouped matches…, Column expression with Hebrew final letters folded — pairs with fold_hebrew()…, Short label for a list-row search hit: key-column value, else the first non-…, _row_label(), search() (+19 more)

### Community 51 - "Notification Models"
Cohesion: 0.11
Nodes (27): NotificationChannel, NotificationLog, Base, Outbound sink. ``config`` holds non-secret fields per kind; ``secret_enc`` is…, Append-only delivery attempt log — swept by ``notify_retention_days``., _deliver(), _DeliveryFailed, _log() (+19 more)

### Community 52 - "Sites API & LAN Info"
Cohesion: 0.11
Nodes (27): _lan_info(), LAN identity detected by the host-networked worker (written to Redis). Falls…, _cascade_site_fields(), create_site(), get_site(), list_sites(), AsyncSession, get (+19 more)

### Community 53 - "IPAM Extra Tests"
Cohesion: 0.13
Nodes (28): _prefix(), _range(), export.csv takes the same filters as the list endpoint — a filtered view…, Same filtered-export treatment on the prefixes CSV (F8)., A documented v6 /64's 2^64 host count must not reach dashboard sums (~1.8e19 >…, A deliberate bulk import documents existing reality — statics inside pools land…, Scratch DB: seed a range + member address at 0024, upgrade to head —…, test_address_role_nat_and_bulk() (+20 more)

### Community 54 - "Rack Group Client"
Cohesion: 0.14
Nodes (23): DashboardPage(), DragSession, errDetail(), findDevice(), GroupClient(), moveDevice(), metadata, metadata (+15 more)

### Community 55 - "Review API"
Cohesion: 0.12
Nodes (27): dismiss_item(), _flagged_address(), get_review(), mac_mismatch_accept(), mac_mismatch_keep(), AsyncSession, get, IPAddress (+19 more)

### Community 56 - "Backup Service"
Cohesion: 0.12
Nodes (28): _alembic_revisions(), BackupError, BackupPreview, BackupTable, build_backup(), _fail_inflight_scans(), _from_json(), _gunzip() (+20 more)

### Community 57 - "Frontend Dependencies"
Cohesion: 0.07
Nodes (29): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, js-yaml, jszip, lucide-react (+21 more)

### Community 58 - "Workbook Import Tests"
Cohesion: 0.08
Nodes (14): Workbook import: normalizer/parser unit tests (no DB) + API e2e., Small synthetic workbook: sites master + one site sheet + circuits., Site sheet documenting a DHCP span AND static stations inside it — the real…, Pool-guard regression: committing a plan whose dhcp range covers documented…, Commit-time PlanError must 422 AND record the failure. The route rolls back…, test_commit_plan_error_marks_batch_failed(), test_commit_twice_rejected(), test_import_e2e() (+6 more)

### Community 59 - "Ranges API"
Cohesion: 0.14
Nodes (19): _check_range_overlap(), create_range(), delete_range(), list_ranges(), AsyncSession, delete, get, post (+11 more)

### Community 60 - "Backend Dependencies"
Cohesion: 0.14
Nodes (23): alembic==1.14.0, arq==0.26.1, asyncpg==0.30.0, bcrypt==4.3.0, cryptography==50.0.1, fastapi==0.115.6, httpx==0.28.1, openpyxl==3.1.5 (+15 more)

### Community 61 - "Frontend Config"
Cohesion: 0.08
Nodes (24): name, private, version, autoprefixer, clsx, postcss, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+16 more)

### Community 62 - "Rack Editor & Device Form"
Cohesion: 0.18
Nodes (24): DeviceFormDialog(), DragSession, DropRow(), EditorBlock(), errDetail(), Pending, RackEditor(), CarrierFrameSvg() (+16 more)

### Community 63 - "Device Export & Import Docs"
Cohesion: 0.10
Nodes (26): GET /api/v1/devices/export.csv, GET /api/v1/devices/export.xlsx, POST /api/v1/devices/import, Carrier two-pass mounting, Changelog / audit history, CSV export, Dry-run preview with per-row {field:[old,new]} diffs, Export dropdown (Devices toolbar) (+18 more)

### Community 64 - "Import Client"
Cohesion: 0.11
Nodes (19): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, SheetResults() (+11 more)

### Community 65 - "Custom List Model"
Cohesion: 0.15
Nodes (15): ListTarget, Import a sheet as a custom list (user-selected or suggested)., DbState, Lookup indexes over the current DB contents., _preview_of(), Custom lists: CRUD + rows + IP resolution + workbook list-target import., also_ipam=False: a servers sheet produces ONLY list rows — no addresses or…, v2 workbook: SRV2 edited, SRV3 added, SRV1 missing -> merge keeps SRV1, updates… (+7 more)

### Community 66 - "List Parser"
Cohesion: 0.13
Nodes (18): _cell_text(), extract_list_table(), _infer_type(), _ips(), _is_ip_token(), pick_key_column(), Custom-list extraction: turn any sheet into {columns, rows} for a list. Unlike…, SheetMatrix -> (column defs, row dicts). columns: [{key, label, type, options?,… (+10 more)

### Community 67 - "Site Sheet Parser"
Cohesion: 0.11
Nodes (12): _blocks(), _col_class(), parse_site_sheet(), _positional_columns(), Split duplicated column groups (031-style runaway): each block starts at an…, Dominant content class of a column sample., Headerless sheet: locate the IP column, then assign the remaining canonical…, MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf. (+4 more)

### Community 68 - "Requirements Pins"
Cohesion: 0.15
Nodes (23): arq==0.26.1, bcrypt==4.3.0, cryptography==50.0.1, fastapi==0.115.6, pysnmp==7.1.29, redis==5.2.0, scapy==2.6.1, sqlalchemy[asyncio]==2.0.36 (+15 more)

### Community 69 - "Rack Library Builder"
Cohesion: 0.13
Nodes (23): arrLen(), attribution(), CATEGORY_COLOUR, CURATED, fetchBuf(), fetchJson(), FRONTEND, FULL_IMPORT (+15 more)

### Community 70 - "Smart Device Import"
Cohesion: 0.11
Nodes (23): import_devices(), Request, Smart device import. Stateless — the file is posted twice: dry-run preview…, _alias_to_field(), apply_mapping_overrides(), auto_map_fields(), auto_map_headers(), remap() (+15 more)

### Community 71 - "Users API"
Cohesion: 0.16
Nodes (22): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+14 more)

### Community 72 - "RBAC Tests"
Cohesion: 0.34
Nodes (22): str, UserRole, login(), mkuser(), other_client(), AsyncClient, AsyncSession, allow_insecure keeps full access (existing behavior preserved). (+14 more)

### Community 73 - "Demo Rack Script"
Cohesion: 0.13
Nodes (16): Api, apply(), _device_payload(), emit_zip(), find_one(), _KeepMethodRedirect, layout_doc(), main() (+8 more)

### Community 74 - "Prefix Tree Page"
Cohesion: 0.20
Nodes (18): metadata, ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), collectExpandableKeys(), flattenTree() (+10 more)

### Community 75 - "Maintenance API"
Cohesion: 0.19
Nodes (21): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+13 more)

### Community 76 - "App Settings Model"
Cohesion: 0.14
Nodes (17): AppSetting, Runtime-editable setting override. Absent row -> env var -> default., fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture (+9 more)

### Community 77 - "Subnets Docs & Wizard"
Cohesion: 0.18
Nodes (21): Changelog bypass for state writes, Add network wizard, Subnets doc, Gateway/DNS technical addresses, IP address, IP range (dhcp/pool/reserved), Subnet matrix, Pool override (force=1) (+13 more)

### Community 78 - "Sheet Classification"
Cohesion: 0.16
Nodes (16): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, _csv_sheet(), load_upload() (+8 more)

### Community 79 - "Color Rule Tests"
Cohesion: 0.27
Nodes (19): _login(), _mk_rule(), _mk_site(), _mkuser(), AsyncClient, AsyncSession, Global row colors: manual row_color + rule-computed display_color. Covers the…, test_backup_roundtrips_color_rules() (+11 more)

### Community 80 - "Demo Datasets"
Cohesion: 0.16
Nodes (20): Demo CSV files, Fictional demo dataset, Demo import data README, Demo VLAN scheme, Network_Address_DEMO.xlsx, Network_Address_DEMO_EN.xlsx, backend/app/services/workbook parser, Asset (SW/HW inventory) (+12 more)

### Community 81 - "Fake Redis"
Cohesion: 0.11
Nodes (9): _FakeRedis, run_monitor_sweep checks each id, writes via bulk update, emits on transitions…, In-memory get/set/publish stand-in for the worker's redis client., _cert_warnings emits cert.expiring once per cert per day — the Redis day-stamp…, A scan that raises mid-job flips to FAILED and emits scan.failed., test_cert_warning_emits_once_per_day(), fake_emit(), test_scan_failed_emits() (+1 more)

### Community 82 - "Ordering Tests"
Cohesion: 0.28
Nodes (18): _circuit_order(), _login(), _mk_circuits(), _mkuser(), AsyncClient, AsyncSession, Global row ordering: POST /{entity}/reorder + pinned rows. Covered on both…, Reordering a subset keeps the slots those rows already had — rows outside the… (+10 more)

### Community 83 - "Prefix API Tests"
Cohesion: 0.22
Nodes (18): _addrs(), _global_vrf_id(), _mkprefix(), Splits are counted arithmetically before materializing: anything over…, test_gateway_clear_removes_only_pristine_row(), test_gateway_never_clobbers_manual_row(), test_gateway_validation(), test_next_ip_never_hands_out_gateway() (+10 more)

### Community 84 - "IP-to-Interface Linking"
Cohesion: 0.18
Nodes (19): IPAddress, connected_interface_id (structured far-end port link), connected_ip (host-side NIC binding), DeviceInterface (device-owned port), L1 trace (cable path walk), match-free-text transition endpoint, One-cable-per-interface rule, Front/back port pairing (pair partner / pair_interface_id) (+11 more)

### Community 85 - "Monitoring Docs"
Cohesion: 0.23
Nodes (19): Check kinds (ping/tcp/http), Monitoring doc (V7), Event sources, Deliberate limits, Monitor target, Notification channel, Notification log, Secrets contract (+11 more)

### Community 86 - "TypeScript Config"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 87 - "Runtime Settings Service"
Cohesion: 0.20
Nodes (14): Any, Effective, Any, Exception, Runtime-editable settings: app_settings rows override env defaults. Each public…, Carries {key: message} so the API can return per-field 422s., SettingsValidationError, _v_bool() (+6 more)

### Community 88 - "Backup API"
Cohesion: 0.21
Nodes (16): download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, get, post, Request, Restore a backup file (raw .json.gz body). Wipes every data table (users are… (+8 more)

### Community 89 - "Settings Read & Masking"
Cohesion: 0.18
Nodes (17): _build_out(), _mask_url(), AsyncSession, get, Hide the password in a scheme://user:pass@host URL., read_settings(), update_settings(), ChangePasswordBody (+9 more)

### Community 90 - "Changelog Service"
Cohesion: 0.20
Nodes (15): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), Audit trail via session flush hooks. before_flush collects (object, action,…, register(), _repr() (+7 more)

### Community 91 - "List Tests"
Cohesion: 0.18
Nodes (4): _mklist(), TestBulkRows, TestListCRUD, TestRows

### Community 92 - "Network Schemas"
Cohesion: 0.20
Nodes (10): _ip(), NetworkCreate, NetworkDhcpRange, NetworkOut, NetworkPrefix, NetworkVlanNew, BaseModel, field_validator (+2 more)

### Community 93 - "Source Provenance (may_write)"
Cohesion: 0.24
Nodes (16): may_write(), Field-ownership check for source-stamped rows (ip_addresses et al.). True when…, _mk_prefix(), V6 provenance — ip_addresses.source: stamping, ownership, filtering. Every…, Manual and imported rows keep their provenance when a scan sees them — observed…, Response bodies carry `source` but never any *_enc-style field., test_csv_import_stamps_import(), test_export_filters_and_carries_source() (+8 more)

### Community 94 - "Docs Pages"
Cohesion: 0.19
Nodes (10): DocsIndexClient(), metadata, DocsNav(), BY_SLUG, DOC_CATEGORIES, DocArticle, DocCategory, docHref() (+2 more)

### Community 95 - "Appearance & Prefs"
Cohesion: 0.15
Nodes (15): AppearancePage(), PrefsInit(), AddrMapView, applyPrefs(), DEFAULT_PREFS, DensityChoice, FxLevel, Prefs (+7 more)

### Community 96 - "Rack Collision Logic"
Cohesion: 0.19
Nodes (13): canPlace(), conflicts(), facesCollide(), freeSlots(), Placed, rangesOverlap(), SLOT_LAYOUTS, LibraryDevice (+5 more)

### Community 97 - "Backup File Ops"
Cohesion: 0.17
Nodes (15): delete_scheduled_backup(), delete, backup_dir(), backup_filename(), delete_backup_file(), list_backup_files(), prune_backups(), datetime (+7 more)

### Community 98 - "Scan Status & SSE"
Cohesion: 0.16
Nodes (14): get_scan(), list_scans(), AsyncSession, get, SSE stream of scan progress (Redis pub/sub backed)., Effective scanner configuration surfaced to the UI., scan_config(), stream_scan() (+6 more)

### Community 99 - "Sites Master Parser"
Cohesion: 0.19
Nodes (8): _master_blocks(), parse_sites_master(), (first, second) octet pairs a master row declares — lets sheet->site matching…, Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins., TestSitesMasterParser

### Community 100 - "Changelog Tests"
Cohesion: 0.23
Nodes (12): AsyncClient, tag_assignments.object_id has no FK — deleting a tagged object must drop its…, Tag.assignments is already ORM delete-orphan — each removed assignment lands in…, PATCH settings with a null value deletes the app_settings row — that delete…, /addresses/bulk action=delete used to issue one Core DELETE — invisible to the…, test_bulk_delete_writes_changelog_entries(), test_changelog_captures_ip_status_change(), test_changelog_records_crud() (+4 more)

### Community 101 - "Search Tests"
Cohesion: 0.31
Nodes (12): AsyncClient, Global /api/v1/search endpoint (UX-3)., Regression: list_addresses ?q= used to crash on a missing column., Site + VRF + prefix + address + one of each workbook entity., _seed(), test_addresses_q_filter_not_broken(), test_search_empty_query(), test_search_grouped_results() (+4 more)

### Community 102 - "Docs Markdown Loader"
Cohesion: 0.22
Nodes (10): DocPage(), dynamicParams, generateMetadata(), loadMarkdown(), DocsContent(), DOC_ARTICLES, docCategoryLabel(), getDoc() (+2 more)

### Community 103 - "Carrier & Rack Library Docs"
Cohesion: 0.23
Nodes (13): Carrier (slot-layout device: shelves/trays), Device image library, Elevation editor, Find free U, Health overlay, Linked asset and IP address, Rack placement rules, Printing and QR labels (+5 more)

### Community 104 - "Settings & DB URL"
Cohesion: 0.18
Nodes (7): psycopg2-style URL for alembic offline mode / scripts., Settings, _env_sourced(), True when the field's current value differs from its declared default., One runtime-editable setting. field: the env-backed attribute on…, SettingSpec, BaseSettings

### Community 105 - "Scan Fallback Tests"
Cohesion: 0.21
Nodes (8): on_hosts fires once per detection step with that chunk's new IPs — ARP batch…, When L2+L3 find nothing, the TCP fallback publishes its batch too., test_scan_cidr_emits_found_deltas(), fake_icmp(), fake_probe(), fake_ptr(), on_hosts(), test_scan_cidr_tcp_fallback_reports_found()

### Community 106 - "Rack Library Licensing"
Cohesion: 0.24
Nodes (11): Demo .Rackula.zip racks, Air-gap safe bundling, CC0 1.0 Universal license, CC0 1.0 Universal, netbox-community/devicetype-library, Rack library ATTRIBUTION, netbox-community/devicetype-library, Rack device image library (+3 more)

### Community 107 - "Fake ARQ Pool"
Cohesion: 0.20
Nodes (8): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture, Stands in for the arq Redis pool — never actually dispatches work., scan_exclude_networks=10.70.0.64/26 inside scan_networks=10.70.0.0/24: the…, test_scheduler_and_route_share_exclusion_guard()

### Community 108 - "Command Palette"
Cohesion: 0.31
Nodes (10): CommandPalette(), Icon, Item, itemsFor(), PAGES, pagesFor(), remember(), SearchOut (+2 more)

### Community 109 - "Frontend Dev Dependencies"
Cohesion: 0.20
Nodes (10): devDependencies, autoprefixer, postcss, sharp, tailwindcss, @types/js-yaml, @types/node, @types/react (+2 more)

### Community 110 - "Cabling Concepts"
Cohesion: 0.42
Nodes (10): Cable, connected_interface structured link, Cabling doc, Interface, L1 trace, POST /api/v1/interfaces/match-free-text, Patch panel as kind=patch device, Bulk port generation (+2 more)

### Community 111 - "Dashboard API"
Cohesion: 0.32
Nodes (6): AsyncSession, get, stats(), DashboardStats, MacMismatchItem, BaseModel

### Community 112 - "Allocation Tests"
Cohesion: 0.43
Nodes (7): _mk_prefix(), test_address_crud_and_dup_guard(), test_allocation_skips_existing(), test_concurrent_allocation_unique(), alloc(), test_exhausted_prefix_conflicts(), test_sequential_allocation_skips_boundaries()

### Community 113 - "Rack Library Checker"
Cohesion: 0.25
Nodes (6): DIR, FACES, LAYOUTS, problems, referenced, slugs

### Community 114 - "NPM Scripts"
Cohesion: 0.29
Nodes (7): scripts, build, build:rack-library, check:rack-library, dev, lint, start

### Community 115 - "Devices Docs"
Cohesion: 0.29
Nodes (7): API sketch, Device detail, Devices, Devices vs racks, From the IP drawer, Health rollup, The list

### Community 116 - "Device RBAC Tests"
Cohesion: 0.53
Nodes (6): _login(), _mkuser(), AsyncSession, RBAC unchanged: the facet vocabulary stays DATA_READ., test_devices_list_filters_viewer(), test_devices_rbac()

### Community 118 - "ARQ Job Fakes"
Cohesion: 0.33
Nodes (3): _Job, fake_arq(), enqueue_job()

### Community 119 - "Keyboard Shortcuts"
Cohesion: 0.53
Nodes (5): moveRowNav(), G_CHORDS, isEditableTarget(), modalOpen(), useGlobalShortcuts()

### Community 120 - "Legacy Bezeq Parser Tests"
Cohesion: 0.40
Nodes (3): קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., TestCircuitsParser

### Community 121 - "Docs Pages Index"
Cohesion: 0.40
Nodes (5): Docs: IP Addresses, Docs: Devices, Docs: Racks, Docs: Settings, Docs: Subnets

### Community 122 - "Chart Theme Hook"
Cohesion: 0.50
Nodes (4): ChartTheme, FALLBACK, readTheme(), useChartTheme()

### Community 123 - "Security Policy"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 125 - "Secrets Exception Handler"
Cohesion: 0.50
Nodes (4): Request, _secrets_not_configured(), exception_handler, JSONResponse

### Community 126 - "OUI Vendor Lookup"
Cohesion: 0.67
Nodes (3): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for()

### Community 127 - "Certificates Parser Tests"
Cohesion: 0.50
Nodes (3): parse_certificates(), Positional 5-col layout: platform, target/VS, server, cert, expiry., TestCertificatesParser

## Ambiguous Edges - Review These
- `Cable` → `Rack`  [AMBIGUOUS]
  frontend/src/content/docs/cabling.md · relation: conceptually_related_to
- `Stats strip & saved views` → `Monitoring doc (V7)`  [AMBIGUOUS]
  frontend/src/content/docs/inventory.md · relation: semantically_similar_to

## Knowledge Gaps
- **373 isolated node(s):** `Icon`, `Item`, `SearchOut`, `Counts`, `Step` (+368 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1477 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Cable` and `Rack`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Stats strip & saved views` and `Monitoring doc (V7)`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._
- **Why does `LinkedRef` connect `Devices API & Interfaces` to `Dashboard & SNMP Card UI`?**
  _High betweenness centrality (0.208) - this node is a cross-community bridge._
- **Why does `_detail()` connect `Devices API & Interfaces` to `Rack Groups API`, `Device Model & Import`, `API Router & Tag GC`, `Common Schemas & Device IO`?**
  _High betweenness centrality (0.130) - this node is a cross-community bridge._
- **Why does `js-yaml` connect `Rack Library Builder` to `Rackula Import`, `Frontend Config`?**
  _High betweenness centrality (0.092) - this node is a cross-community bridge._
- **Are the 64 inferred relationships involving `Device` (e.g. with `_Occupancy` and `Planned`) actually correct?**
  _`Device` has 64 INFERRED edges - model-reasoned connections that need verification._
- **Are the 72 inferred relationships involving `IPAMError` (e.g. with `_get_cable()` and `_get_interface()`) actually correct?**
  _`IPAMError` has 72 INFERRED edges - model-reasoned connections that need verification._