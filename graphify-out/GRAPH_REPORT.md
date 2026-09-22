# Graph Report - IpamBox  (2026-09-22)

## Corpus Check
- 37 files · ~259,364 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2808 nodes · 8090 edges · 191 communities (99 shown, 67 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 495 edges (avg confidence: 0.93)
- Token cost: 9,200 input · 8,100 output

## Community Hubs (Navigation)
- Address & Entity CRUD API
- Address Table UI
- App Bootstrap & Entities
- Resource Client Pages
- Resource Pages (alt ids)
- Addresses API
- Color Rules Settings UI
- Security & Users UI
- Color Rules API
- Login & Scans UI
- Discovery & Prefix Detail UI
- Maintenance API
- Workbook Normalizer
- Prefixes API
- Changelog & Dashboard API
- User Docs Concepts
- LAN Scanner & OUI
- Workbook Planner
- Backup Service
- Config, Redis & Migrations
- Changelog & Dashboard UI
- Frontend Dependencies
- Client Pages & Forms
- Auth API
- Workbook Import API
- Core Config & Changelog
- Certificates UI
- Docs Viewer UI
- VLANs API
- Address Components
- Prefix Services
- Scan Worker
- Scan Reconcile
- Prefix Components
- Runtime Settings
- Backend Tests Test
- Tags API
- Backend Tests Test (2)
- Backend Tests Test (3)
- Backup API
- Prefs Library
- Backend Tests Test (4)
- Backend Tests Test (5)
- Ref Radix
- Frontend Package Dependencies
- Backend App Schemas
- Backend Tests Test (6)
- Backend Tests Test (7)
- Src Components App
- Scans API
- Src App Import
- Frontend Tsconfig
- Lib Prefs
- Backend Tests Test (8)
- Docker Compose
- Backend Tests Test (9)
- Users API
- Backend Tests Test (10)
- App Import
- Src App Import (2)
- Backend App Schemas (2)
- Backend Tests Test (11)
- Backend Tests Conftest
- Backend App Schemas (3)
- Backend Tests Test (12)
- Backend Tests Test (13)
- Backend Tests Test (14)
- Changelog Engine
- Backend Tests Test (15)
- Backend App Schemas (4)
- Backend Tests Test (16)
- Redis & ARQ Pool
- Prefix Api Test
- Lib Shortcuts
- Backend App Schemas (5)
- Backend App Schemas (6)
- Backend App Schemas (7)
- Src App Prefixes
- Src App Settings
- Frontend Package Devdependencies
- Backend App Schemas (8)
- Backend App Schemas (9)
- App Services Workbook
- Backend Tests Test (17)
- Backend Tests Test (18)
- Src App Prefixes (2)
- App Tree
- App Worker Worker
- Backend Tests Test (19)
- Src App Settings (2)
- Src App Tree
- Src App Vlans
- App Services Scan
- Backend Tests Test (20)
- Frontend Package Scripts
- Src App Layout
- Src Components Shortcuts
- Src Lib Use
- Lib Status
- Security
- Src App Vrfs
- Scan Streaming
- Backend Requirements Pydantic
- Src App Changelog
- Src App Page
- Src App Login
- Src App Setup
- Src App Inventory
- App Services Services
- Src App Settings (3)
- Requirements Alembic
- Src App Certificates
- Src App Circuits
- Src App Discovery
- Src App Import (3)
- Src App Inventory (2)
- Src App Prefixes (3)
- Src App Prefixes (4)
- Src App Scans
- App Services Page
- Src App Settings (4)
- Src App Settings (5)
- Src App Settings (6)
- Src App Settings (7)
- Src App Sites (2)
- Src App Tags
- Src App Tree (2)
- Src App Vlans (2)
- Src App Vrfs (2)
- Readme Document
- Src App Scans (2)
- Src App Settings (8)
- Backend Requirements Arq
- Backend Requirements Pytest
- Frontend Next
- Frontend Tailwind
- Frontend Xff
- Next Config
- Allocateiprequest
- App Api V1
- App Api V1 (2)
- Backend App Core
- Backend App Models
- Backend App Models (2)
- Backend App Schemas (11)
- App Services Runtime
- App Worker Worker (2)
- App Worker Worker (3)
- App Worker Worker (4)
- Backend Requirements Bcrypt
- Backend Requirements Httpx
- Backend Requirements Openpyxl
- Backend Requirements Psutil
- Backend Requirements Scapy
- Backend Tests Test (21)
- Basemodel
- Src App Icon
- Src App Layout (2)
- Ipstatus
- Prefixcreate
- Prefixout
- Prefixupdate
- Readme Backup
- Readme Env
- Readme Github
- Readme Mit

## God Nodes (most connected - your core abstractions)
1. `cn()` - 114 edges
2. `react` - 97 edges
3. `User` - 61 edges
4. `IPAMError` - 60 edges
5. `IPAddress` - 60 edges
6. `lucide-react` - 56 edges
7. `get_or_404()` - 55 edges
8. `api` - 54 edges
9. `Prefix` - 48 edges
10. `UserRole` - 44 edges

## Surprising Connections (you probably didn't know these)
- `IpDrawer()` --calls--> `fmtTs()`  [EXTRACTED]
  components/ip-drawer.tsx → lib/prefs.ts
- `SitesPage()` --calls--> `usePrefs()`  [EXTRACTED]
  app/sites/sites-client.tsx → lib/prefs.ts
- `TagsPage()` --calls--> `usePrefs()`  [EXTRACTED]
  app/tags/tags-client.tsx → lib/prefs.ts
- `VrfsPage()` --calls--> `fmtTs()`  [EXTRACTED]
  app/vrfs/vrfs-client.tsx → lib/prefs.ts
- `AddressList()` --calls--> `useRowNav()`  [EXTRACTED]
  components/address-list.tsx → lib/row-nav.ts

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Loopback data plane (DB/Redis published on 127.0.0.1, reachable by host-networked scanner)** — docker_compose_db_service, docker_compose_redis_service, docker_compose_loopback_binding, docker_compose_scanner_service, docker_compose_scanner_host_mode [EXTRACTED 1.00]
- **Scan-size guard shared between API validation and worker** — docker_compose_api_service, docker_compose_scanner_service, docker_compose_scan_max_hosts [EXTRACTED 1.00]
- **Compose-level XFF trust chain (pinned bridge IP + trusted-proxies env + uvicorn flags)** — docker_compose_trusted_proxies, docker_compose_uvicorn_proxy_flags, docker_compose_web_service, docker_compose_ipam_network [EXTRACTED 1.00]
- **async FastAPI + SQLAlchemy + Postgres API stack** — backend_requirements_fastapi, backend_requirements_uvicorn, backend_requirements_sqlalchemy, backend_requirements_asyncpg, backend_requirements_pydantic [INFERRED 0.85]
- **Site → VRF → Prefix → IP address core hierarchy** — frontend_src_content_docs_sites_sites, frontend_src_content_docs_vrfs_vrfs, frontend_src_content_docs_subnets_subnets, frontend_src_content_docs_addresses_ip_addresses, frontend_src_content_docs_overview_data_model_hierarchy [EXTRACTED 1.00]
- **Scan → reconcile → human-review flow** — frontend_src_content_docs_scans_scans, frontend_src_content_docs_scans_scan_pipeline, frontend_src_content_docs_scans_scapy_scanner, frontend_src_content_docs_discovery_reconciliation, frontend_src_content_docs_discovery_discovery_inbox, frontend_src_content_docs_addresses_ip_addresses, frontend_src_content_docs_addresses_mac_mismatch [EXTRACTED 1.00]
- **Workbook importer sheet families and their target registers** — frontend_src_content_docs_import_import_wizard, frontend_src_content_docs_import_import_pipeline, frontend_src_content_docs_import_import_batch_id, frontend_src_content_docs_sites_sites, frontend_src_content_docs_circuits_circuits, frontend_src_content_docs_certificates_certificates, frontend_src_content_docs_inventory_inventory, frontend_src_content_docs_services_services [EXTRACTED 1.00]

## Communities (191 total, 67 thin omitted)

### Community 0 - "Address & Entity CRUD API"
Cohesion: 0.06
Nodes (80): delete_address(), delete, update_address(), _crud_router(), create_item(), delete_item(), get_item(), list_items() (+72 more)

### Community 1 - "Address Table UI"
Cohesion: 0.06
Nodes (62): AddressList(), AddrMapViewSwitcher(), buildRows(), IP_STATUSES, Row, sortAddr(), SortKey, HistoryPanel() (+54 more)

### Community 2 - "App Bootstrap & Entities"
Cohesion: 0.08
Nodes (48): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, healthz(), metrics(), get, Readiness probe: verifies DB + Redis connectivity., Prometheus-style text exposition of object + scan counters., readyz(), AppSetting (+40 more)

### Community 3 - "Resource Client Pages"
Cohesion: 0.11
Nodes (43): EMPTY, EMPTY, AssetRow, EMPTY, EMPTY, ServiceRow, TagsPage(), VLAN_STATUSES (+35 more)

### Community 4 - "Resource Pages (alt ids)"
Cohesion: 0.12
Nodes (45): CertificatesPage(), EMPTY, CircuitsPage(), EMPTY, AssetRow, EMPTY, InventoryPage(), EMPTY (+37 more)

### Community 5 - "Addresses API"
Cohesion: 0.06
Nodes (56): _address_csv_row(), _addresses_stmt(), bulk_addresses(), BulkBody, create_address(), export_addresses(), get_address(), import_addresses() (+48 more)

### Community 6 - "Color Rules Settings UI"
Cohesion: 0.04
Nodes (56): ColorRulesPage(), Draft, ENTITIES, OP_LABEL, OPS_BY_TYPE, opsFor(), RuleDialog(), metadata (+48 more)

### Community 7 - "Security & Users UI"
Cohesion: 0.06
Nodes (42): fmtAgo(), SecurityPage(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS, NavGroup, NavItem (+34 more)

### Community 8 - "Color Rules API"
Cohesion: 0.06
Nodes (44): create_rule(), delete_rule(), get_rule(), list_rules(), preview_rule(), AsyncSession, delete, get (+36 more)

### Community 9 - "Login & Scans UI"
Cohesion: 0.07
Nodes (32): fmtEta(), ScansPage(), DataPage(), download(), ConfirmAction(), metadata, PrintClient(), FeatureDef (+24 more)

### Community 10 - "Discovery & Prefix Detail UI"
Cohesion: 0.09
Nodes (35): BulkResp, IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, SplitPlan, toggleIn(), PrefixesPage() (+27 more)

### Community 11 - "Maintenance API"
Cohesion: 0.07
Nodes (52): _audit(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession, BaseModel (+44 more)

### Community 12 - "Workbook Normalizer"
Cohesion: 0.07
Nodes (46): assemble_ip(), clean(), _clean_octets(), excel_date(), map_status(), mask_to_prefixlen(), network_of(), norm_header() (+38 more)

### Community 13 - "Prefixes API"
Cohesion: 0.09
Nodes (47): allocate_next_available(), create_prefix(), export_prefixes(), get_prefix(), list_prefixes(), _prefix_rows(), prefix_tree(), AsyncSession (+39 more)

### Community 14 - "Changelog & Dashboard API"
Cohesion: 0.08
Nodes (39): list_changelog(), AsyncSession, get, AsyncSession, get, stats(), _build_out(), _lan_info() (+31 more)

### Community 15 - "User Docs Concepts"
Cohesion: 0.13
Nodes (50): Accounts & Roles, Insecure mode (IPAMBOX_ALLOW_INSECURE), Four roles (Administrator, Operator, Contributor, Viewer), Session-cookie authentication, Address roles (vip/vrrp/hsrp/glbp/carp/secondary), Address CSV import/export, IP Addresses, IP drawer (+42 more)

### Community 16 - "LAN Scanner & OUI"
Cohesion: 0.07
Nodes (41): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), _host_chunks(), HostResult, _icmp_sweep(), infer_device_type() (+33 more)

### Community 17 - "Workbook Planner"
Cohesion: 0.10
Nodes (15): parse_sites_master_records(), _Planner, _preview(), (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Folded sheet title vs site name/code — word-boundary matching so 'int' doesn't…, Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new… (+7 more)

### Community 18 - "Backup Service"
Cohesion: 0.10
Nodes (43): backup_dir(), delete_backup_file(), list_backup_files(), prune_backups(), Path, Fetch a scheduled backup by file name (path-traversal safe)., Delete a scheduled backup by file name (path-traversal safe)., Delete oldest scheduled backups beyond the retention count. (+35 more)

### Community 19 - "Config, Redis & Migrations"
Cohesion: 0.08
Nodes (32): do_run_migrations(), run_migrations_online(), get_settings(), close_arq_pool(), close_redis(), Shut down the shared client — lifespan/worker shutdown only., lifespan(), auth_on() (+24 more)

### Community 20 - "Changelog & Dashboard UI"
Cohesion: 0.08
Nodes (29): ACTION_STYLES, ACTION_STYLES, AsyncPanel(), ExpiryBadge(), ACTION_STYLES, ChangeDiff(), ChangeVal(), fmtChangeVal() (+21 more)

### Community 21 - "Frontend Dependencies"
Cohesion: 0.05
Nodes (41): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, lucide-react, next, @radix-ui/react-dialog (+33 more)

### Community 22 - "Client Pages & Forms"
Cohesion: 0.07
Nodes (12): EMPTY, ACTION_STYLES, EMPTY, ACTION_STYLES, BulkResp, BackupSettingsPage(), downloadUrl(), fmtSize() (+4 more)

### Community 23 - "Auth API"
Cohesion: 0.16
Nodes (37): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+29 more)

### Community 24 - "Workbook Import API"
Cohesion: 0.10
Nodes (37): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+29 more)

### Community 25 - "Core Config & Changelog"
Cohesion: 0.09
Nodes (38): AsyncSession, Request, Guard for every API route. Returns the User, or None in allow_insecure mode., require_auth(), get_redis(), Shared process-wide Redis client. Do NOT aclose() it per call — connections…, clear_login_failures(), client_ip() (+30 more)

### Community 27 - "Docs Viewer UI"
Cohesion: 0.11
Nodes (24): DocsIndexClient(), metadata, DocPage(), dynamicParams, generateMetadata(), loadMarkdown(), CommandPalette(), Icon (+16 more)

### Community 28 - "VLANs API"
Cohesion: 0.14
Nodes (31): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+23 more)

### Community 29 - "Address Components"
Cohesion: 0.09
Nodes (21): BulkResp, BackupSettingsPage(), downloadUrl(), fmtSize(), AddressList(), buildRows(), IP_STATUSES, Row (+13 more)

### Community 30 - "Prefix Services"
Cohesion: 0.12
Nodes (28): split_prefix(), _check_range_overlap(), create_range(), list_ranges(), AsyncSession, get, post, prefix_stats_dict() (+20 more)

### Community 31 - "Scan Worker"
Cohesion: 0.10
Nodes (27): Effective, get_effective(), AsyncSession, cancel_key(), _due(), _eta_seconds(), _job_status(), _publish() (+19 more)

### Community 32 - "Scan Reconcile"
Cohesion: 0.11
Nodes (28): _flag(), Any, AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), _mk_prefix(), A stored (e.g. imported) MAC that differs from the scan is flagged in…, Scanning a /24 under a documented /16 must not mark the other 255 subnets'… (+20 more)

### Community 33 - "Prefix Components"
Cohesion: 0.16
Nodes (26): ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), collectExpandableKeys(), flattenTree(), prefixKey() (+18 more)

### Community 34 - "Runtime Settings"
Cohesion: 0.10
Nodes (18): psycopg2-style URL for alembic offline mode / scripts., Settings, _env_sourced(), Any, Runtime-editable settings: app_settings rows override env defaults. Each public…, True when the field's current value differs from its declared default., Carries {key: message} so the API can return per-field 422s., One runtime-editable setting. field: the env-backed attribute on… (+10 more)

### Community 35 - "Backend Tests Test"
Cohesion: 0.10
Nodes (21): _api_cancel(), _FakeRedis, _mk_job(), In-memory stand-in for the worker's redis client (get/set/publish)., Point the worker at the test DB (sf) and the fake redis client., Simulate the API-side cancel: terminal status on a fresh connection., Cancel flag polled between phases -> ScanCancelled -> CANCELLED, and no…, Audit race: API writes CANCELLED mid-scan while the redis flag is lost… (+13 more)

### Community 36 - "Tags API"
Cohesion: 0.17
Nodes (24): AssignBody, assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession (+16 more)

### Community 37 - "Backend Tests Test (2)"
Cohesion: 0.13
Nodes (17): _global_vrf_id(), _infer_scan_vrf(), Pick the VRF for a scan that didn't specify one. An exact-match prefix living…, _scan_vrf(), _extra_vrf(), _global_id(), The cap is a runtime setting: lowering it to 2 rejects a /24., scan_infers_vrf=off: no prefix-matching — scans without an explicit VRF always… (+9 more)

### Community 38 - "Backend Tests Test (3)"
Cohesion: 0.21
Nodes (13): _master_row(), _matrix(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind… (+5 more)

### Community 39 - "Backup API"
Cohesion: 0.14
Nodes (22): delete_scheduled_backup(), download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, delete, get, post (+14 more)

### Community 40 - "Prefs Library"
Cohesion: 0.13
Nodes (21): CommandPalette(), Icon, Item, itemsFor(), remember(), SearchOut, PrefsInit(), AddrMapView (+13 more)

### Community 41 - "Backend Tests Test (4)"
Cohesion: 0.34
Nodes (22): str, UserRole, login(), mkuser(), other_client(), AsyncClient, AsyncSession, allow_insecure keeps full access (existing behavior preserved). (+14 more)

### Community 42 - "Backend Tests Test (5)"
Cohesion: 0.11
Nodes (15): Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, parse_certificates(), Positional 5-col layout: platform, target/VS, server, cert, expiry., XLSX -> sheet matrices via openpyxl (read_only streams, values only)., SheetMatrix, Workbook import: normalizer/parser unit tests (no DB) + API e2e., Small synthetic workbook: sites master + one site sheet + circuits., Commit-time PlanError must 422 AND record the failure. The route rolls back… (+7 more)

### Community 43 - "Ref Radix"
Cohesion: 0.09
Nodes (22): name, private, version, autoprefixer, clsx, postcss, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+14 more)

### Community 44 - "Frontend Package Dependencies"
Cohesion: 0.09
Nodes (23): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, lucide-react, next, @radix-ui/react-dialog (+15 more)

### Community 45 - "Backend App Schemas"
Cohesion: 0.24
Nodes (19): _folded(), AsyncSession, get, search(), match(), BaseModel, SearchAddress, SearchAsset (+11 more)

### Community 46 - "Backend Tests Test (6)"
Cohesion: 0.22
Nodes (21): auth_on(), _circuit_order(), _login(), _mk_circuits(), _mkuser(), AsyncClient, AsyncSession, fixture (+13 more)

### Community 47 - "Backend Tests Test (7)"
Cohesion: 0.27
Nodes (19): _login(), _mk_rule(), _mk_site(), _mkuser(), AsyncClient, AsyncSession, Global row colors: manual row_color + rule-computed display_color. Covers the…, test_backup_roundtrips_color_rules() (+11 more)

### Community 48 - "Src Components App"
Cohesion: 0.13
Nodes (15): AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS, NavGroup, NavItem, NavLink() (+7 more)

### Community 49 - "Scans API"
Cohesion: 0.19
Nodes (16): cancel_scan(), create_scan(), get_scan(), list_scans(), AsyncSession, get, post, ScanJob (+8 more)

### Community 50 - "Src App Import"
Cohesion: 0.14
Nodes (13): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, Step (+5 more)

### Community 51 - "Frontend Tsconfig"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 52 - "Lib Prefs"
Cohesion: 0.16
Nodes (15): metadata, PrintClient(), applyPrefs(), DEFAULT_PREFS, DensityChoice, fmtTs(), getPrefs(), Prefs (+7 more)

### Community 53 - "Backend Tests Test (8)"
Cohesion: 0.17
Nodes (15): AsyncClient, fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture, Every new Settings > Features key is runtime-editable; untouched keys keep the…, test_backup_files_report_effective_schedule() (+7 more)

### Community 54 - "Docker Compose"
Cohesion: 0.19
Nodes (18): alembic upgrade head on api start, API_BIND publish binding, api service, backupdata volume, backupdata Volume, IPAMBOX_COOKIE_SECURE env, db service (postgres:16-alpine), ipam bridge network 192.0.2.0/24 (+10 more)

### Community 55 - "Backend Tests Test (9)"
Cohesion: 0.19
Nodes (15): _job_payload(), Base, str, ScanJob, ScanStatus, AsyncClient, test_backup_now_enqueues(), test_clear_discovery() (+7 more)

### Community 56 - "Users API"
Cohesion: 0.24
Nodes (16): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+8 more)

### Community 57 - "Backend Tests Test (10)"
Cohesion: 0.17
Nodes (8): _blocks(), parse_site_sheet(), Split duplicated column groups (031-style runaway): each block starts at an…, MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf., Bare 'Name' (Cellular) maps to the hostname field., Non-empty unnamed columns pile into cf['extra'] instead of vanishing (Pelephone…, TestSiteSheetExtras, TestSiteSheetParser

### Community 58 - "App Import"
Cohesion: 0.13
Nodes (10): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, Step (+2 more)

### Community 59 - "Src App Import (2)"
Cohesion: 0.13
Nodes (10): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, Step (+2 more)

### Community 60 - "Backend App Schemas (2)"
Cohesion: 0.22
Nodes (9): CircuitCreate, CircuitOut, CircuitUpdate, BaseModel, field_validator, ip_display(), Any, Normalize asyncpg-returned ipaddress objects / strings to display form. INET… (+1 more)

### Community 61 - "Backend Tests Test (11)"
Cohesion: 0.19
Nodes (8): _master_blocks(), parse_sites_master(), (first, second) octet pairs a master row declares — lets sheet->site matching…, Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins., TestSitesMasterParser

### Community 62 - "Backend Tests Conftest"
Cohesion: 0.26
Nodes (12): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., session() (+4 more)

### Community 63 - "Backend App Schemas (3)"
Cohesion: 0.24
Nodes (8): IPRangeRole, str, IPRangeCreate, IPRangeOut, IPRangeUpdate, BaseModel, field_validator, model_validator

### Community 64 - "Backend Tests Test (12)"
Cohesion: 0.24
Nodes (6): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, TestClassify

### Community 65 - "Backend Tests Test (13)"
Cohesion: 0.23
Nodes (12): AsyncClient, tag_assignments.object_id has no FK — deleting a tagged object must drop its…, Tag.assignments is already ORM delete-orphan — each removed assignment lands in…, PATCH settings with a null value deletes the app_settings row — that delete…, /addresses/bulk action=delete used to issue one Core DELETE — invisible to the…, test_bulk_delete_writes_changelog_entries(), test_changelog_captures_ip_status_change(), test_changelog_records_crud() (+4 more)

### Community 66 - "Backend Tests Test (14)"
Cohesion: 0.31
Nodes (12): auth_on(), AsyncClient, fixture, _seed(), test_addresses_q_filter_not_broken(), test_search_empty_query(), test_search_grouped_results(), test_search_hebrew_folding() (+4 more)

### Community 67 - "Changelog Engine"
Cohesion: 0.35
Nodes (11): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), Audit trail via session flush hooks. before_flush collects (object, action,…, register(), _repr() (+3 more)

### Community 68 - "Backend Tests Test (15)"
Cohesion: 0.21
Nodes (8): on_hosts fires once per detection step with that chunk's new IPs — ARP batch…, When L2+L3 find nothing, the TCP fallback publishes its batch too., test_scan_cidr_emits_found_deltas(), fake_icmp(), fake_probe(), fake_ptr(), on_hosts(), test_scan_cidr_tcp_fallback_reports_found()

### Community 69 - "Backend App Schemas (4)"
Cohesion: 0.27
Nodes (8): CertificateCreate, CertificateOut, CertificateUpdate, BaseModel, field_validator, DashboardStats, MacMismatchItem, BaseModel

### Community 70 - "Backend Tests Test (16)"
Cohesion: 0.20
Nodes (8): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture, Stands in for the arq Redis pool — never actually dispatches work., scan_exclude_networks=10.70.0.64/26 inside scan_networks=10.70.0.0/24: the…, test_scheduler_and_route_share_exclusion_guard()

### Community 71 - "Redis & ARQ Pool"
Cohesion: 0.20
Nodes (9): ArqRedis, backup_now(), Enqueue an immediate scheduled-style backup on the worker., get_arq_pool(), Shared ARQ pool — callers must not close() it per job., redis_settings_from_url(), The pool is created once per loop — verified without touching Redis by faking…, test_get_arq_pool_returns_one_shared_pool() (+1 more)

### Community 72 - "Prefix Api Test"
Cohesion: 0.38
Nodes (9): _global_vrf_id(), test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_prefixes_order_by_utilization_and_limit(), test_same_cidr_allowed_across_vrfs(), test_split_cardinality_cap(), test_split_endpoint(), test_tree_endpoint() (+1 more)

### Community 73 - "Lib Shortcuts"
Cohesion: 0.29
Nodes (7): AppShell(), moveRowNav(), RowNavApi, G_CHORDS, isEditableTarget(), modalOpen(), useGlobalShortcuts()

### Community 74 - "Backend App Schemas (5)"
Cohesion: 0.36
Nodes (7): AssetKind, str, AssetCreate, AssetOut, AssetUpdate, BaseModel, field_validator

### Community 75 - "Backend App Schemas (6)"
Cohesion: 0.28
Nodes (4): hex_color_or_none(), Shared row/tag color validator: #rrggbb, normalized to lowercase., field_validator, field_validator

### Community 76 - "Backend App Schemas (7)"
Cohesion: 0.33
Nodes (5): BaseModel, field_validator, VRFCreate, VRFOut, VRFUpdate

### Community 77 - "Src App Prefixes"
Cohesion: 0.25
Nodes (6): IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, SplitPlan, toggleIn()

### Community 78 - "Src App Settings"
Cohesion: 0.25
Nodes (6): Draft, ENTITIES, OP_LABEL, OPS_BY_TYPE, opsFor(), RuleDialog()

### Community 79 - "Frontend Package Devdependencies"
Cohesion: 0.25
Nodes (8): devDependencies, autoprefixer, postcss, tailwindcss, @types/node, @types/react, @types/react-dom, typescript

### Community 80 - "Backend App Schemas (8)"
Cohesion: 0.38
Nodes (5): BaseModel, field_validator, ServiceCreate, ServiceOut, ServiceUpdate

### Community 81 - "Backend App Schemas (9)"
Cohesion: 0.38
Nodes (5): BaseModel, field_validator, SiteCreate, SiteOut, SiteUpdate

### Community 82 - "App Services Workbook"
Cohesion: 0.29
Nodes (4): _col_class(), _positional_columns(), Dominant content class of a column sample., Headerless sheet: locate the IP column, then assign the remaining canonical…

### Community 83 - "Backend Tests Test (17)"
Cohesion: 0.52
Nodes (6): _mk_prefix(), test_address_crud_and_dup_guard(), test_allocation_skips_existing(), test_concurrent_allocation_unique(), test_exhausted_prefix_conflicts(), test_sequential_allocation_skips_boundaries()

### Community 84 - "Backend Tests Test (18)"
Cohesion: 0.29
Nodes (5): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture

### Community 85 - "Src App Prefixes (2)"
Cohesion: 0.33
Nodes (3): PrefixesPage(), PrefixRow, utilColor()

### Community 86 - "App Tree"
Cohesion: 0.53
Nodes (5): ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText()

### Community 87 - "App Worker Worker"
Cohesion: 0.33
Nodes (6): Fail live jobs that outlived the worker's job_timeout. An OOM-killed or…, Every-minute cron: reaps live jobs that outlived job_timeout., reap_stale_scan_jobs(), scan_watchdog(), A worker killed mid-scan leaves RUNNING rows that would wedge the single-live-…, test_watchdog_reaps_stale_jobs()

### Community 89 - "Src App Settings (2)"
Cohesion: 0.33
Nodes (3): nextConfig, metadata, next

### Community 90 - "Src App Tree"
Cohesion: 0.53
Nodes (5): ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText()

### Community 92 - "App Services Scan"
Cohesion: 0.40
Nodes (4): _check_cidr_allowed(), exclusion_hit(), Scan-target policy shared by the API route, the scheduler, and the worker.…, Return the first excluded CIDR overlapping ``net`` (either direction), or None.…

### Community 93 - "Backend Tests Test (20)"
Cohesion: 0.40
Nodes (3): קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., TestCircuitsParser

### Community 94 - "Frontend Package Scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 95 - "Src App Layout"
Cohesion: 0.40
Nodes (3): metadata, viewport, TooltipProvider

### Community 97 - "Src Lib Use"
Cohesion: 0.50
Nodes (4): ChartTheme, FALLBACK, readTheme(), useChartTheme()

### Community 98 - "Lib Status"
Cohesion: 0.40
Nodes (4): GRID_CELL_TOKENS, STATUS_TOKENS, StatusBadgeVariant, StatusTokenSet

### Community 99 - "Security"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 101 - "Scan Streaming"
Cohesion: 0.50
Nodes (4): SSE stream of scan progress (Redis pub/sub backed)., stream_scan(), gen(), StreamingResponse

### Community 102 - "Backend Requirements Pydantic"
Cohesion: 0.50
Nodes (4): fastapi 0.115.6, pydantic 2.10.3, pydantic-settings 2.6.1, uvicorn[standard] 0.32.1

### Community 128 - "Requirements Alembic"
Cohesion: 0.67
Nodes (3): alembic 1.14.0, asyncpg 0.30.0, sqlalchemy[asyncio] 2.0.36

## Knowledge Gaps
- **364 isolated node(s):** `AssetRow`, `ServiceRow`, `VlanRow`, `Row`, `SortKey` (+359 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1046 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **67 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_settings()` connect `Config, Redis & Migrations` to `Address & Entity CRUD API`, `Runtime Settings`, `App Bootstrap & Entities`, `Backend Tests Test (14)`, `Backup API`, `Backend Tests Test (4)`, `Prefixes API`, `Changelog & Dashboard API`, `Backend Tests Test (7)`, `Backend Tests Test (6)`, `Scans API`, `Auth API`, `Workbook Import API`, `Core Config & Changelog`, `Prefix Services`, `Scan Worker`?**
  _High betweenness centrality (0.112) - this node is a cross-community bridge._
- **Why does `_build_out()` connect `Changelog & Dashboard API` to `Maintenance API`, `Login & Scans UI`, `Config, Redis & Migrations`, `Scan Worker`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._
- **Why does `SettingsOut` connect `Login & Scans UI` to `Address Components`, `Color Rules Settings UI`, `Changelog & Dashboard API`?**
  _High betweenness centrality (0.110) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `User` (e.g. with `bulk_addresses()` and `auth_status()`) actually correct?**
  _`User` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 42 inferred relationships involving `IPAMError` (e.g. with `create_address()` and `delete_address()`) actually correct?**
  _`IPAMError` has 42 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `IPAddress` (e.g. with `_address_csv_row()` and `_addresses_stmt()`) actually correct?**
  _`IPAddress` has 22 INFERRED edges - model-reasoned connections that need verification._
- **What connects `AssetRow`, `ServiceRow`, `VlanRow` to the rest of the system?**
  _364 weakly-connected nodes found - possible documentation gaps or missing edges._