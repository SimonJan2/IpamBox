# Graph Report - IpamBox  (2026-09-18)

## Corpus Check
- 32 files · ~203,003 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1638 nodes · 5063 edges · 100 communities (71 shown, 11 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 370 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- IPAM Frontend Pages
- Backup API
- Dashboard & Settings Pages
- Circuits & Inventory Pages
- Sites API
- Login & Settings Pages
- Backup File Management
- Changelog & Data Models
- Workbook Import API
- Prefixes API
- Certificates & Scans Pages
- Addresses API
- Auth API
- Entity Models & IPAM
- Workbook Import Planner
- Changelog & Dashboard API
- Scans API
- Entities API
- Settings & Scans Pages
- CRUD Router & VRFs
- Ranges API
- VLANs API
- Redis & Runtime Settings
- Scanner & OUI Lookup
- Tags API
- Scan VRF Inference
- Settings API
- Session Security
- RBAC & User Model
- Workbook Parsing
- Frontend Package Config
- NPM Dependencies
- Prefix Math
- Test Fixtures
- TypeScript Config
- IP & Site Models
- Workbook Normalization
- Site Plan Parsing
- Project Documentation
- Workbook Import Tests
- Users API
- Python Dependencies
- Settings Tests
- Appearance & Prefs
- Entity Parser Tests
- Import Page
- App Config & Migrations
- Normalize Tests
- Site Sheet Parser Tests
- Sheet Classification
- IPAM Extras Tests
- Changelog Flush Hooks
- Infrastructure Docs
- Discovery API
- App Layout & Config
- Auth Tests
- Prefix API Tests
- Docker Services
- Dev Dependencies
- Compose Services
- Health & Metrics
- RBAC Test Fixtures
- User Tests
- Scan Reconciliation
- Entity CRUD Tests
- Docs & Security Policy
- Auth Dependency Guard
- Changelog Tests
- Backup Docs
- NPM Scripts
- README Features
- Env Password
- Backup Serialization
- Inflight Scan Cleanup
- Next Env Types
- Tailwind Config
- Doc File Nodes
- AsyncSession Stub
- Exception Stub
- App Icon
- Root Layout
- Site Stub

## God Nodes (most connected - your core abstractions)
1. `cn()` - 74 edges
2. `User` - 57 edges
3. `react` - 55 edges
4. `get_or_404()` - 51 edges
5. `IPAMError` - 50 edges
6. `IPAddress` - 48 edges
7. `Base` - 41 edges
8. `lucide-react` - 41 edges
9. `useAuth()` - 38 edges
10. `_matrix()` - 38 edges

## Surprising Connections (you probably didn't know these)
- `pydantic-settings==2.6.1` --semantically_similar_to--> `Hybrid settings model (.env defaults + runtime overrides in app_settings)`  [INFERRED] [semantically similar]
  backend/requirements.txt → README.md
- `httpx==0.28.1` --references--> `api service (FastAPI backend, alembic+uvicorn entrypoint)`  [INFERRED]
  backend/requirements.txt → docker-compose.yml
- `pytest-asyncio==0.25.0` --references--> `api service (FastAPI backend, alembic+uvicorn entrypoint)`  [INFERRED]
  backend/requirements.txt → docker-compose.yml
- `api service (FastAPI backend, alembic+uvicorn entrypoint)` --references--> `Excel workbook import wizard (detect, dry-run, commit)`  [INFERRED]
  docker-compose.yml → README.md
- `Hybrid settings model (.env defaults + runtime overrides in app_settings)` --references--> `scanner service (ARQ worker, network_mode: host, NET_ADMIN/NET_RAW)`  [INFERRED]
  README.md → docker-compose.yml

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Healthcheck-Gated Startup Ordering** — ipambox_docker_compose_db_service, ipambox_docker_compose_redis_service, ipambox_docker_compose_api_service, ipambox_docker_compose_scanner_service, ipambox_docker_compose_web_service [EXTRACTED 1.00]
- **Single Backend Image, Two Runtimes (api + scanner)** — ipambox_docker_compose_api_service, ipambox_docker_compose_scanner_service [EXTRACTED 1.00]
- **Shared Backup Subsystem** — ipambox_docker_compose_api_service, ipambox_docker_compose_scanner_service, ipambox_docker_compose_backupdata_volume [EXTRACTED 1.00]

## Communities (100 total, 11 thin omitted)

### Community 0 - "IPAM Frontend Pages"
Cohesion: 0.07
Nodes (57): ChangelogPage(), DiscoveryPage(), IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, toggleIn(), AddressList() (+49 more)

### Community 1 - "Backup API"
Cohesion: 0.06
Nodes (60): download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, get, post, Request, Restore a backup file (raw .json.gz body). Wipes every data table (users are… (+52 more)

### Community 2 - "Dashboard & Settings Pages"
Cohesion: 0.04
Nodes (50): ACTION_STYLES, DashboardPage(), downloadUrl(), fmtSize(), fmtTs(), SettingsPage(), PrefixTreeNode(), expiryBadge() (+42 more)

### Community 3 - "Circuits & Inventory Pages"
Cohesion: 0.11
Nodes (41): CircuitsPage(), EMPTY, AssetRow, EMPTY, InventoryPage(), PrefixesPage(), PrefixRow, utilColor() (+33 more)

### Community 4 - "Sites API"
Cohesion: 0.07
Nodes (38): Any, _cascade_site_fields(), create_site(), delete_site(), get_site(), list_sites(), AsyncSession, delete (+30 more)

### Community 5 - "Login & Settings Pages"
Cohesion: 0.13
Nodes (31): BackupSettingsPage(), downloadUrl(), fmtSize(), DataPage(), download(), FEATURES, Key, Key (+23 more)

### Community 6 - "Backup File Management"
Cohesion: 0.10
Nodes (43): delete_scheduled_backup(), delete, backup_dir(), delete_backup_file(), list_backup_files(), prune_backups(), Path, Fetch a scheduled backup by file name (path-traversal safe). (+35 more)

### Community 7 - "Changelog & Data Models"
Cohesion: 0.16
Nodes (18): Audit trail via session flush hooks. before_flush collects (object, action,…, AppSetting, Runtime-editable setting override. Absent row -> env var -> default., Base, Certificate, Certificate-expiry row from the תוקף תעודות sheet., ChangeLog, NetBox-style audit trail: who changed what, when, and the field diff. (+10 more)

### Community 8 - "Workbook Import API"
Cohesion: 0.10
Nodes (35): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+27 more)

### Community 9 - "Prefixes API"
Cohesion: 0.13
Nodes (36): allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), prefix_tree() (+28 more)

### Community 10 - "Certificates & Scans Pages"
Cohesion: 0.18
Nodes (21): EMPTY, ACTION_STYLES, ChangeSummary(), fmt(), fmtAgo(), SecurityPage(), Badge(), BadgeProps (+13 more)

### Community 11 - "Addresses API"
Cohesion: 0.12
Nodes (30): bulk_addresses(), BulkBody, create_address(), delete_address(), export_addresses(), get_address(), import_addresses(), ImportRow (+22 more)

### Community 12 - "Auth API"
Cohesion: 0.19
Nodes (32): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+24 more)

### Community 13 - "Entity Models & IPAM"
Cohesion: 0.11
Nodes (27): Asset, SW/HW catalog rows (תוכנות וחומרות) and serial-number inventory…, Circuit, build_tree(), prefix_node(), site_node(), vrf_node(), ConflictError (+19 more)

### Community 15 - "Changelog & Dashboard API"
Cohesion: 0.10
Nodes (21): list_changelog(), AsyncSession, get, AsyncSession, get, stats(), ConfirmBody, BaseModel (+13 more)

### Community 16 - "Scans API"
Cohesion: 0.14
Nodes (27): cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession, get (+19 more)

### Community 17 - "Entities API"
Cohesion: 0.14
Nodes (21): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, AssetKind, str, AssetCreate, AssetOut, AssetUpdate, BaseModel, CertificateCreate (+13 more)

### Community 18 - "Settings & Scans Pages"
Cohesion: 0.09
Nodes (24): CertificatesPage(), expiryBadge(), fmtEta(), ScansPage(), ScanningPage(), UsersPage(), AddressFilterPanel(), AppShell() (+16 more)

### Community 19 - "CRUD Router & VRFs"
Cohesion: 0.13
Nodes (22): _crud_router(), delete_item(), get_item(), update_item(), create_vrf(), delete_vrf(), get_vrf(), list_vrfs() (+14 more)

### Community 20 - "Ranges API"
Cohesion: 0.12
Nodes (21): _check_range_overlap(), create_range(), delete_range(), list_ranges(), AsyncSession, delete, get, post (+13 more)

### Community 21 - "VLANs API"
Cohesion: 0.19
Nodes (25): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+17 more)

### Community 22 - "Redis & Runtime Settings"
Cohesion: 0.14
Nodes (26): ArqRedis, get_arq_pool(), redis_settings_from_url(), set_actor(), get_effective(), detect_interface(), detect_local_cidr(), CIDR of the default-route interface, e.g. '192.168.1.0/24'. (+18 more)

### Community 23 - "Scanner & OUI Lookup"
Cohesion: 0.12
Nodes (22): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), HostResult, _icmp_sweep(), infer_device_type(), _ptr_lookup() (+14 more)

### Community 24 - "Tags API"
Cohesion: 0.18
Nodes (20): assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession, delete (+12 more)

### Community 25 - "Scan VRF Inference"
Cohesion: 0.15
Nodes (17): _infer_scan_vrf(), Pick the VRF for a scan that didn't specify one. An exact-match prefix living…, _scan_vrf(), _extra_vrf(), fake_arq(), _pool(), _FakeArqJob, _FakePool (+9 more)

### Community 26 - "Settings API"
Cohesion: 0.17
Nodes (20): _build_out(), _lan_info(), _mask_url(), AsyncSession, get, Hide the password in a scheme://user:pass@host URL., LAN identity detected by the host-networked worker (written to Redis). Falls…, read_settings() (+12 more)

### Community 27 - "Session Security"
Cohesion: 0.16
Nodes (22): get_redis(), clear_login_failures(), destroy_other_sessions(), destroy_session(), destroy_session_by_suffix(), _fails_key(), get_session_user_id(), is_locked_out() (+14 more)

### Community 28 - "RBAC & User Model"
Cohesion: 0.34
Nodes (22): str, UserRole, login(), mkuser(), other_client(), AsyncClient, AsyncSession, allow_insecure keeps full access (existing behavior preserved). (+14 more)

### Community 29 - "Workbook Parsing"
Cohesion: 0.13
Nodes (13): norm_header(), parse_site_number(), _blocks(), _col_class(), _is_header_echo(), _leftover_bits(), _map_columns(), _master_blocks() (+5 more)

### Community 30 - "Frontend Package Config"
Cohesion: 0.09
Nodes (21): name, private, version, autoprefixer, clsx, postcss, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+13 more)

### Community 31 - "NPM Dependencies"
Cohesion: 0.10
Nodes (21): dependencies, class-variance-authority, clsx, lucide-react, next, @radix-ui/react-dialog, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+13 more)

### Community 32 - "Prefix Math"
Cohesion: 0.21
Nodes (18): children(), lowest_free(), parent_chain(), Inclusive [first, last] integer range of host-usable addresses., True when network/broadcast addresses are unusable for hosts (IPv4 <= /30)., Lowest usable address integer not in `taken` or any excluded range., Split `net` into children of `new_prefix` length., The smallest candidate network that strictly contains `net`. (+10 more)

### Community 33 - "Test Fixtures"
Cohesion: 0.17
Nodes (17): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., sf() (+9 more)

### Community 34 - "TypeScript Config"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 35 - "IP & Site Models"
Cohesion: 0.18
Nodes (13): IPAddress, Site, fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture (+5 more)

### Community 36 - "Workbook Normalization"
Cohesion: 0.25
Nodes (15): assemble_ip(), clean(), _clean_octets(), fold_hebrew(), map_status(), mask_to_prefixlen(), network_of(), norm_mac() (+7 more)

### Community 37 - "Site Plan Parsing"
Cohesion: 0.16
Nodes (9): parse_sites_master(), build_import_plan(), DbState, load_state(), parse_sites_master_records(), _preview(), AsyncSession, _site_key() (+1 more)

### Community 38 - "Project Documentation"
Cohesion: 0.12
Nodes (18): bcrypt==4.3.0, Architecture, Configuration, Development, Extended entities (WAN circuits, certificates, inventory, service catalog), First-run auth, session cookies, bcrypt hashing, IP lockout, Hebrew data support (final-letter folding, RTL rendering), IpamBox (+10 more)

### Community 39 - "Workbook Import Tests"
Cohesion: 0.37
Nodes (6): _master_row(), _matrix(), _plan(), _preview_of(), _site_key_by_name(), TestPlanSiteResolution

### Community 40 - "Users API"
Cohesion: 0.24
Nodes (16): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+8 more)

### Community 41 - "Python Dependencies"
Cohesion: 0.15
Nodes (16): alembic==1.14.0, fastapi==0.115.6, httpx==0.28.1, openpyxl==3.1.5, pydantic==2.10.3, pydantic-settings==2.6.1, pytest==8.3.4, pytest-asyncio==0.25.0 (+8 more)

### Community 42 - "Settings Tests"
Cohesion: 0.19
Nodes (13): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_files_report_effective_schedule(), test_internal_keys_hidden() (+5 more)

### Community 43 - "Appearance & Prefs"
Cohesion: 0.18
Nodes (15): AppearancePage(), TagsPage(), AddrMapView, applyPrefs(), DEFAULT_PREFS, DensityChoice, fmtTs(), getPrefs() (+7 more)

### Community 44 - "Entity Parser Tests"
Cohesion: 0.21
Nodes (8): parse_certificates(), parse_servers(), test_commit_twice_rejected(), test_import_e2e(), TestAssetsParser, TestCertificatesParser, TestServersParser, _xlsx_bytes()

### Community 45 - "Import Page"
Cohesion: 0.22
Nodes (9): ACTION_STYLE, CommitResp, Counts, FAMILY_LABEL, PreviewResp, UploadResp, ImportBatch, RowResult (+1 more)

### Community 46 - "App Config & Migrations"
Cohesion: 0.21
Nodes (7): do_run_migrations(), run_migrations_online(), VRF, slugify(), main(), Seed sample data: a Site, the Global VRF, and the auto-detected LAN prefix. Run…, _global_vrf_id()

### Community 47 - "Normalize Tests"
Cohesion: 0.17
Nodes (3): excel_date(), TestNormalize, date

### Community 48 - "Site Sheet Parser Tests"
Cohesion: 0.27
Nodes (3): parse_site_sheet(), TestSiteSheetExtras, TestSiteSheetParser

### Community 49 - "Sheet Classification"
Cohesion: 0.31
Nodes (4): classify_sheet(), _has(), _looks_like_header(), TestClassify

### Community 50 - "IPAM Extras Tests"
Cohesion: 0.40
Nodes (10): _prefix(), test_address_role_nat_and_bulk(), test_container_move_with_children_rejected(), test_csv_export_import(), test_dashboard_attention_fields(), test_ip_ranges_exclude_allocator(), test_prefix_move_vrf(), test_tags_crud_and_assignment() (+2 more)

### Community 51 - "Changelog Flush Hooks"
Cohesion: 0.29
Nodes (10): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), register(), _repr(), _ser() (+2 more)

### Community 52 - "Infrastructure Docs"
Cohesion: 0.24
Nodes (10): arq==0.26.1, asyncpg==0.30.0, psutil==6.1.0, redis==5.2.0 (Python client), scapy==2.6.1, sqlalchemy[asyncio]==2.0.36, scanner service (ARQ worker, network_mode: host, NET_ADMIN/NET_RAW), Discovery Inbox and drift reconciliation (+2 more)

### Community 53 - "Discovery API"
Cohesion: 0.22
Nodes (9): confirm_discovered(), list_discovered(), AsyncSession, get, post, Unconfirmed hosts found by scanners, pending admin review., Unconfirmed hosts found by scanners, pending admin review., One-click confirm a discovered host (default -> Active). (+1 more)

### Community 54 - "App Layout & Config"
Cohesion: 0.25
Nodes (5): nextConfig, metadata, PrefsInit(), TooltipProvider, next

### Community 55 - "Auth Tests"
Cohesion: 0.32
Nodes (7): auth_on(), AsyncClient, fixture, Turn auth on for a test, restore insecure mode after, and flush session/lockout…, test_endpoints_require_auth(), test_login_lockout(), test_setup_login_flow()

### Community 56 - "Prefix API Tests"
Cohesion: 0.46
Nodes (7): _global_vrf_id(), test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_same_cidr_allowed_across_vrfs(), test_split_endpoint(), test_tree_endpoint(), test_unknown_vlan_rejected()

### Community 57 - "Docker Services"
Cohesion: 0.32
Nodes (8): db service (postgres:16-alpine), pgdata volume, redis service (redis:7-alpine, appendonly), redisdata volume, Atomic next-available-IP allocation (SELECT FOR UPDATE + UNIQUE), PostgreSQL GiST exclusion constraint for CIDR overlap safety, Site -> VRF -> Prefix -> IP address hierarchy, Loopback-only Postgres/Redis binding (not exposed to LAN)

### Community 58 - "Dev Dependencies"
Cohesion: 0.25
Nodes (8): devDependencies, autoprefixer, postcss, tailwindcss, @types/node, @types/react, @types/react-dom, typescript

### Community 59 - "Compose Services"
Cohesion: 0.36
Nodes (8): api — FastAPI Backend Service, backupdata Volume, db — PostgreSQL 16 Database Service, pgdata Volume, redis — Redis 7 Queue/Cache Service, redisdata Volume, scanner — Network Scan Worker Service, web — Next.js Frontend Service

### Community 60 - "Health & Metrics"
Cohesion: 0.29
Nodes (7): healthz(), metrics(), get, Readiness probe: verifies DB + Redis connectivity., Prometheus-style text exposition of object + scan counters., readyz(), JSONResponse

### Community 61 - "RBAC Test Fixtures"
Cohesion: 0.29
Nodes (4): auth_on(), fake_arq(), fixture, Turn auth on for a test, restore insecure mode after, and flush session/lockout…

### Community 62 - "User Tests"
Cohesion: 0.38
Nodes (6): auth_on(), AsyncClient, fixture, test_change_password_and_sessions(), test_revoke_session_endpoint(), test_users_crud_and_guards()

### Community 63 - "Scan Reconciliation"
Cohesion: 0.33
Nodes (6): AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), A stored (e.g. imported) MAC that differs from the scan is flagged in…, test_reconcile_flags_mac_mismatch(), test_reconcile_persists_ports_and_type()

### Community 65 - "Docs & Security Policy"
Cohesion: 0.33
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 66 - "Auth Dependency Guard"
Cohesion: 0.40
Nodes (5): AsyncSession, Request, Guard for every API route. Returns the User, or None in allow_insecure mode., Guard for every API route. Returns the User, or None in allow_insecure mode., require_auth()

### Community 67 - "Changelog Tests"
Cohesion: 0.60
Nodes (4): AsyncClient, test_changelog_captures_ip_status_change(), test_changelog_records_crud(), test_changelog_scoped_filters()

### Community 68 - "Backup Docs"
Cohesion: 0.40
Nodes (5): backupdata volume (/backups), Backup file format, Backup & Restore, Restore, Take a backup

### Community 69 - "NPM Scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 70 - "README Features"
Cohesion: 0.50
Nodes (4): Features, IPAM, Platform, Scanner

### Community 83 - "Env Password"
Cohesion: 0.67
Nodes (3): env_password(), Password provisioned via IPAMBOX_PASSWORD_FILE / IPAMBOX_PASSWORD., Password provisioned via IPAMBOX_PASSWORD_FILE / IPAMBOX_PASSWORD.

### Community 84 - "Backup Serialization"
Cohesion: 1.00
Nodes (3): Any, _serialize_row(), _to_json()

## Knowledge Gaps
- **171 isolated node(s):** `Row`, `SortKey`, `CellState`, `BadgeProps`, `CheckboxProps` (+166 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 473 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ScanJob` connect `Dashboard & Settings Pages` to `Scans API`, `Certificates & Scans Pages`, `Circuits & Inventory Pages`, `Redis & Runtime Settings`?**
  _High betweenness centrality (0.131) - this node is a cross-community bridge._
- **Why does `create_site()` connect `Sites API` to `IP & Site Models`, `Circuits & Inventory Pages`, `App Config & Migrations`?**
  _High betweenness centrality (0.116) - this node is a cross-community bridge._
- **Why does `Site` connect `Circuits & Inventory Pages` to `Certificates & Scans Pages`, `Dashboard & Settings Pages`, `Sites API`, `Import Page`?**
  _High betweenness centrality (0.115) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `User` (e.g. with `bulk_addresses()` and `auth_status()`) actually correct?**
  _`User` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 35 inferred relationships involving `IPAMError` (e.g. with `create_address()` and `delete_address()`) actually correct?**
  _`IPAMError` has 35 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Row`, `SortKey`, `CellState` to the rest of the system?**
  _171 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `IPAM Frontend Pages` be split into smaller, more focused modules?**
  _Cohesion score 0.07039337474120083 - nodes in this community are weakly interconnected._