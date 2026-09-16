# Graph Report - IpamBox  (2026-09-17)

## Corpus Check
- 8 files · ~196,477 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1596 nodes · 4947 edges · 96 communities (71 shown, 8 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 381 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Prefix Detail & Address UI
- User Management API
- Dashboard & Settings Pages
- VLAN API
- Entity List Pages
- Address API
- Prefix API
- Login & Settings UI
- Import API
- Backup API
- Workbook Normalizers
- Settings & Config API
- App Setup & Models
- Scan API
- Scanner & Reconcile
- IP Range API
- Misc Frontend Pages
- IPAM Tree & Stats
- Worker Scheduling
- Backup Service
- Workbook Plan Builder
- Scan VRF & Tests
- Maintenance API
- Entity Models & Commit
- Entity CRUD & Assets
- Prefix Math
- Next.js App Config
- Frontend Dependencies
- Auth API
- Session Security
- Frontend Package Deps
- API Router & Changelog
- Health & Core Models
- Page Components
- TypeScript Config
- VRF API
- Project Docs & Deps
- Workbook Reader & Tests
- App Shell & Auth
- Auth Sessions
- Backend Deps & Compose
- Settings Tests
- Sites API
- Tags API
- Maintenance Tests
- Sheet Parsers
- Test Fixtures
- Import Page UI
- Changelog Hooks
- Discovery API
- Tag Schemas
- IPAM Extra Tests
- Sheet Classification
- Scanner Stack Docs
- CRUD Router Factory
- Circuit Schemas
- Sheet Family Detection
- Asset & Cert Parsers
- Normalizer Tests
- Auth Tests
- Prefix API Tests
- Infra Services & Model
- Frontend Dev Deps
- User Tests
- Entity Tests
- Project Docs
- Auth Guard
- Changelog Tests
- Backup Docs
- NPM Scripts
- ARQ Redis Setup
- Alembic Env
- Inventory Parser
- Feature Docs
- Next Env Types
- Tailwind Config
- Docs Pairing
- App Icon
- Root Layout

## God Nodes (most connected - your core abstractions)
1. `cn()` - 72 edges
2. `User` - 57 edges
3. `IPAddress` - 53 edges
4. `react` - 53 edges
5. `get_or_404()` - 52 edges
6. `IPAMError` - 51 edges
7. `useAuth()` - 45 edges
8. `Base` - 43 edges
9. `lucide-react` - 40 edges
10. `UserRole` - 37 edges

## Surprising Connections (you probably didn't know these)
- `pydantic-settings==2.6.1` --semantically_similar_to--> `Hybrid settings model (.env defaults + runtime overrides in app_settings)`  [INFERRED] [semantically similar]
  backend/requirements.txt → README.md
- `scanner service (ARQ worker, network_mode: host, NET_ADMIN/NET_RAW)` --references--> `psutil==6.1.0`  [INFERRED]
  docker-compose.yml → backend/requirements.txt
- `Hybrid settings model (.env defaults + runtime overrides in app_settings)` --references--> `scanner service (ARQ worker, network_mode: host, NET_ADMIN/NET_RAW)`  [INFERRED]
  README.md → docker-compose.yml
- `api service (FastAPI backend, alembic+uvicorn entrypoint)` --references--> `httpx==0.28.1`  [INFERRED]
  docker-compose.yml → backend/requirements.txt
- `pytest-asyncio==0.25.0` --references--> `api service (FastAPI backend, alembic+uvicorn entrypoint)`  [INFERRED]
  backend/requirements.txt → docker-compose.yml

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Shared SCAN_*/BACKUP_* env contract between api and scanner** — docker_compose_api, docker_compose_scanner, readme_hybrid_settings_model [EXTRACTED 1.00]
- **LAN scan -> fingerprint -> reconcile flow** — docker_compose_scanner, backend_requirements_arq, backend_requirements_scapy, readme_scan_pipeline, readme_discovery_reconciliation [INFERRED 0.85]
- **Scheduled snapshot backup flow (worker writes volume, API serves restore)** — docker_compose_api, docker_compose_scanner, docker_compose_backupdata, readme_backup_restore [INFERRED 0.85]

## Communities (96 total, 8 thin omitted)

### Community 0 - "Prefix Detail & Address UI"
Cohesion: 0.06
Nodes (64): IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, toggleIn(), AddressFilterPanel(), STATUS_DOT, STATUSES (+56 more)

### Community 1 - "User Management API"
Cohesion: 0.08
Nodes (73): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+65 more)

### Community 2 - "Dashboard & Settings Pages"
Cohesion: 0.05
Nodes (50): ACTION_STYLES, DashboardPage(), downloadUrl(), fmtSize(), fmtTs(), SettingsPage(), PrefixTreeNode(), expiryBadge() (+42 more)

### Community 3 - "VLAN API"
Cohesion: 0.06
Nodes (45): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+37 more)

### Community 4 - "Entity List Pages"
Cohesion: 0.16
Nodes (27): EMPTY, EMPTY, EMPTY, VLAN_STATUSES, SortHeader(), TAG_COLORS, Dialog, DialogClose (+19 more)

### Community 5 - "Address API"
Cohesion: 0.11
Nodes (37): bulk_addresses(), BulkBody, create_address(), delete_address(), export_addresses(), get_address(), import_addresses(), ImportRow (+29 more)

### Community 6 - "Prefix API"
Cohesion: 0.13
Nodes (36): allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), prefix_tree() (+28 more)

### Community 7 - "Login & Settings UI"
Cohesion: 0.15
Nodes (27): BackupSettingsPage(), downloadUrl(), fmtSize(), DataPage(), download(), Key, fmtAgo(), SecurityPage() (+19 more)

### Community 8 - "Import API"
Cohesion: 0.11
Nodes (36): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+28 more)

### Community 9 - "Backup API"
Cohesion: 0.11
Nodes (31): delete_scheduled_backup(), download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, delete, get, post (+23 more)

### Community 10 - "Workbook Normalizers"
Cohesion: 0.11
Nodes (28): assemble_ip(), clean(), _clean_octets(), map_status(), mask_to_prefixlen(), network_of(), norm_mac(), parse_range_end() (+20 more)

### Community 11 - "Settings & Config API"
Cohesion: 0.13
Nodes (24): _build_out(), _lan_info(), _mask_url(), AsyncSession, get, Hide the password in a scheme://user:pass@host URL., LAN identity detected by the host-networked worker (written to Redis). Falls…, read_settings() (+16 more)

### Community 12 - "App Setup & Models"
Cohesion: 0.19
Nodes (9): lifespan(), AppSetting, Runtime-editable setting override. Absent row -> env var -> default., Base, Polymorphic tag link — attaches a Tag to a Site/VRF/Prefix/IPAddress., Tag, TagAssignment, VLANGroup (+1 more)

### Community 13 - "Scan API"
Cohesion: 0.14
Nodes (26): cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession, get (+18 more)

### Community 14 - "Scanner & Reconcile"
Cohesion: 0.11
Nodes (25): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), _arp_scan(), HostResult (+17 more)

### Community 15 - "IP Range API"
Cohesion: 0.12
Nodes (21): _check_range_overlap(), create_range(), delete_range(), list_ranges(), AsyncSession, delete, get, post (+13 more)

### Community 16 - "Misc Frontend Pages"
Cohesion: 0.22
Nodes (17): EMPTY, ACTION_STYLES, ChangelogPage(), ChangeSummary(), fmt(), fmtEta(), ScansPage(), Table() (+9 more)

### Community 17 - "IPAM Tree & Stats"
Cohesion: 0.14
Nodes (25): AsyncSession, AsyncSession, get, stats(), build_tree(), prefix_node(), site_node(), vrf_node() (+17 more)

### Community 18 - "Worker Scheduling"
Cohesion: 0.13
Nodes (26): set_actor(), Effective, get_effective(), detect_interface(), detect_local_cidr(), Exception, CIDR of the default-route interface, e.g. '192.168.1.0/24'., Raised inside the pipeline when the user cancels the scan. (+18 more)

### Community 19 - "Backup Service"
Cohesion: 0.13
Nodes (25): BackupError, BackupPreview, BackupTable, build_backup(), _fail_inflight_scans(), _from_json(), _gunzip(), _has_serial_id() (+17 more)

### Community 20 - "Workbook Plan Builder"
Cohesion: 0.19
Nodes (5): parse_sites_master_records(), _Planner, _preview(), site_key, matched_by for a site_sheet., Counter

### Community 21 - "Scan VRF & Tests"
Cohesion: 0.14
Nodes (18): _global_vrf_id(), _infer_scan_vrf(), Pick the VRF for a scan that didn't specify one. An exact-match prefix living…, _scan_vrf(), _extra_vrf(), fake_arq(), _pool(), _FakeArqJob (+10 more)

### Community 22 - "Maintenance API"
Cohesion: 0.17
Nodes (23): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+15 more)

### Community 23 - "Entity Models & Commit"
Cohesion: 0.13
Nodes (18): Certificate, Certificate-expiry row from the תוקף תעודות sheet., Circuit, WAN circuit row from the קוי-SDH-IPVPN sheet (Bezeq IPVPN/SDH/Metro…)., Service catalog row from the שירותים sheet., Service, commit_batch(), execute_plan() (+10 more)

### Community 24 - "Entity CRUD & Assets"
Cohesion: 0.17
Nodes (17): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, Asset, AssetKind, str, SW/HW catalog rows (תוכנות וחומרות) and serial-number inventory…, AssetCreate, AssetOut, AssetUpdate (+9 more)

### Community 25 - "Prefix Math"
Cohesion: 0.17
Nodes (21): children(), lowest_free(), parent_chain(), Inclusive [first, last] integer range of host-usable addresses., True when network/broadcast addresses are unusable for hosts (IPv4 <= /30)., Lowest usable address integer not in `taken` or any excluded range., Split `net` into children of `new_prefix` length., The smallest candidate network that strictly contains `net`. (+13 more)

### Community 26 - "Next.js App Config"
Cohesion: 0.12
Nodes (18): nextConfig, metadata, AppearancePage(), PrefsInit(), TooltipProvider, AddrMapView, applyPrefs(), DEFAULT_PREFS (+10 more)

### Community 27 - "Frontend Dependencies"
Cohesion: 0.09
Nodes (21): name, private, version, autoprefixer, clsx, postcss, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+13 more)

### Community 28 - "Auth API"
Cohesion: 0.25
Nodes (20): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), AsyncSession (+12 more)

### Community 29 - "Session Security"
Cohesion: 0.19
Nodes (20): get_redis(), clear_login_failures(), create_session(), destroy_other_sessions(), destroy_session(), destroy_session_by_suffix(), _fails_key(), get_session_user_id() (+12 more)

### Community 30 - "Frontend Package Deps"
Cohesion: 0.10
Nodes (21): dependencies, class-variance-authority, clsx, lucide-react, next, @radix-ui/react-dialog, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+13 more)

### Community 31 - "API Router & Changelog"
Cohesion: 0.15
Nodes (13): list_changelog(), AsyncSession, get, get_session(), AsyncSession, ChangeField, ChangeLogOut, BaseModel (+5 more)

### Community 32 - "Health & Core Models"
Cohesion: 0.14
Nodes (16): healthz(), metrics(), get, Readiness probe: verifies DB + Redis connectivity., Prometheus-style text exposition of object + scan counters., readyz(), IPRange, A named block of addresses inside a prefix (e.g. a DHCP scope). Any defined… (+8 more)

### Community 33 - "Page Components"
Cohesion: 0.14
Nodes (17): CertificatesPage(), expiryBadge(), CircuitsPage(), DiscoveryPage(), InventoryPage(), PrefixesPage(), utilColor(), ServicesPage() (+9 more)

### Community 34 - "TypeScript Config"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 35 - "VRF API"
Cohesion: 0.20
Nodes (14): create_vrf(), delete_vrf(), get_vrf(), list_vrfs(), AsyncSession, delete, get, post (+6 more)

### Community 36 - "Project Docs & Deps"
Cohesion: 0.12
Nodes (18): bcrypt==4.3.0, Architecture, Configuration, Development, Extended entities (WAN circuits, certificates, inventory, service catalog), First-run auth, session cookies, bcrypt hashing, IP lockout, Hebrew data support (final-letter folding, RTL rendering), IpamBox (+10 more)

### Community 37 - "Workbook Reader & Tests"
Cohesion: 0.16
Nodes (10): Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, parse_sites_master(), XLSX -> sheet matrices via openpyxl (read_only streams, values only)., SheetMatrix, Workbook import: normalizer/parser unit tests (no DB) + API e2e., Small synthetic workbook: sites master + one site sheet + circuits., test_commit_twice_rejected(), test_import_e2e() (+2 more)

### Community 38 - "App Shell & Auth"
Cohesion: 0.18
Nodes (14): AppShell(), AUTH_ROUTES, NAV, QuickScanDialog(), useScanStream(), AuthContext, AuthCtx, authCtxValue() (+6 more)

### Community 39 - "Auth Sessions"
Cohesion: 0.19
Nodes (14): me(), get, sessions(), Effective permission set; insecure mode (user=None) gets everything., user_permissions(), env_password(), list_sessions(), All live sessions for a user; tokens surface only as an 8-char suffix. (+6 more)

### Community 40 - "Backend Deps & Compose"
Cohesion: 0.15
Nodes (16): alembic==1.14.0, fastapi==0.115.6, httpx==0.28.1, openpyxl==3.1.5, pydantic==2.10.3, pydantic-settings==2.6.1, pytest==8.3.4, pytest-asyncio==0.25.0 (+8 more)

### Community 41 - "Settings Tests"
Cohesion: 0.19
Nodes (13): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_files_report_effective_schedule(), test_internal_keys_hidden() (+5 more)

### Community 42 - "Sites API"
Cohesion: 0.25
Nodes (13): create_site(), delete_site(), get_site(), list_sites(), AsyncSession, delete, get, post (+5 more)

### Community 43 - "Tags API"
Cohesion: 0.26
Nodes (14): assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession, delete (+6 more)

### Community 44 - "Maintenance Tests"
Cohesion: 0.21
Nodes (12): Site, fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_now_enqueues() (+4 more)

### Community 45 - "Sheet Parsers"
Cohesion: 0.20
Nodes (9): _blocks(), _map_columns(), parse_site_sheet(), _positional_columns(), Per-family sheet parsers -> normalized record dicts. Every parser takes…, canonical field -> column indexes (multi-index for duplicated blocks)., Headerless sheet: find the IP-fragment column, map the canonical layout…, Split duplicated column groups (031-style runaway): each block starts at an… (+1 more)

### Community 46 - "Test Fixtures"
Cohesion: 0.29
Nodes (11): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., session() (+3 more)

### Community 47 - "Import Page UI"
Cohesion: 0.22
Nodes (10): ACTION_STYLE, CommitResp, Counts, FAMILY_LABEL, ImportPage(), PreviewResp, UploadResp, ImportBatch (+2 more)

### Community 48 - "Changelog Hooks"
Cohesion: 0.35
Nodes (11): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), Audit trail via session flush hooks. before_flush collects (object, action,…, register(), _repr() (+3 more)

### Community 49 - "Discovery API"
Cohesion: 0.18
Nodes (11): confirm_discovered(), ConfirmBody, list_discovered(), AsyncSession, BaseModel, get, post, Unconfirmed hosts found by scanners, pending admin review. (+3 more)

### Community 50 - "Tag Schemas"
Cohesion: 0.29
Nodes (7): AssignBody, BaseModel, field_validator, TagAssignmentOut, TagCreate, TagOut, TagUpdate

### Community 51 - "IPAM Extra Tests"
Cohesion: 0.40
Nodes (10): _prefix(), test_address_role_nat_and_bulk(), test_container_move_with_children_rejected(), test_csv_export_import(), test_dashboard_attention_fields(), test_ip_ranges_exclude_allocator(), test_prefix_move_vrf(), test_tags_crud_and_assignment() (+2 more)

### Community 52 - "Sheet Classification"
Cohesion: 0.42
Nodes (4): classify_sheet(), (family, header_row_index, warnings). header_row_index = index of the row…, _matrix(), TestClassify

### Community 53 - "Scanner Stack Docs"
Cohesion: 0.24
Nodes (10): arq==0.26.1, asyncpg==0.30.0, psutil==6.1.0, redis==5.2.0 (Python client), scapy==2.6.1, sqlalchemy[asyncio]==2.0.36, scanner service (ARQ worker, network_mode: host, NET_ADMIN/NET_RAW), Discovery Inbox and drift reconciliation (+2 more)

### Community 54 - "CRUD Router Factory"
Cohesion: 0.33
Nodes (8): _crud_router(), delete_item(), get_item(), list_items(), update_item(), get_or_404(), fold_hebrew(), Fold Hebrew final letters to base form (ך->כ …) for loose matching.

### Community 55 - "Circuit Schemas"
Cohesion: 0.36
Nodes (5): CircuitCreate, CircuitOut, CircuitUpdate, BaseModel, field_validator

### Community 56 - "Sheet Family Detection"
Cohesion: 0.25
Nodes (7): _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., norm_header(), Header cell -> lowercase, single-spaced, for signature matching., _is_header_echo(), parse_services()

### Community 57 - "Asset & Cert Parsers"
Cohesion: 0.22
Nodes (7): excel_date(), datetime/date passthrough; int/float serial (20000-80000) -> date; 'd/m/yy'…, parse_assets(), parse_certificates(), Positional 5-col layout: platform, target/VS, server, cert, expiry., 003 תוכנות וחומרות: סוג,חברה,דגם,שם התוכנה,ייעוד,גירסה,EOL,…, date

### Community 59 - "Auth Tests"
Cohesion: 0.32
Nodes (7): auth_on(), AsyncClient, fixture, Turn auth on for a test, restore insecure mode after, and flush session/lockout…, test_endpoints_require_auth(), test_login_lockout(), test_setup_login_flow()

### Community 60 - "Prefix API Tests"
Cohesion: 0.46
Nodes (7): _global_vrf_id(), test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_same_cidr_allowed_across_vrfs(), test_split_endpoint(), test_tree_endpoint(), test_unknown_vlan_rejected()

### Community 61 - "Infra Services & Model"
Cohesion: 0.32
Nodes (8): db service (postgres:16-alpine), pgdata volume, redis service (redis:7-alpine, appendonly), redisdata volume, Atomic next-available-IP allocation (SELECT FOR UPDATE + UNIQUE), PostgreSQL GiST exclusion constraint for CIDR overlap safety, Site -> VRF -> Prefix -> IP address hierarchy, Loopback-only Postgres/Redis binding (not exposed to LAN)

### Community 62 - "Frontend Dev Deps"
Cohesion: 0.25
Nodes (8): devDependencies, autoprefixer, postcss, tailwindcss, @types/node, @types/react, @types/react-dom, typescript

### Community 63 - "User Tests"
Cohesion: 0.38
Nodes (6): auth_on(), AsyncClient, fixture, test_change_password_and_sessions(), test_revoke_session_endpoint(), test_users_crud_and_guards()

### Community 65 - "Project Docs"
Cohesion: 0.33
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 66 - "Auth Guard"
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

### Community 70 - "ARQ Redis Setup"
Cohesion: 0.50
Nodes (4): ArqRedis, get_arq_pool(), redis_settings_from_url(), RedisSettings

### Community 72 - "Inventory Parser"
Cohesion: 0.50
Nodes (4): PCB Serial Number : 31231187' -> ['31231187']; multi-line cells -> one serial…, split_serial_blob(), parse_inventory(), 105/106 serial-number lists -> hardware assets.

### Community 73 - "Feature Docs"
Cohesion: 0.50
Nodes (4): Features, IPAM, Platform, Scanner

## Knowledge Gaps
- **161 isolated node(s):** `Row`, `SortKey`, `CellState`, `SwitchProps`, `WorkerSettings` (+156 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 492 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ScanJob` connect `Dashboard & Settings Pages` to `Misc Frontend Pages`, `Worker Scheduling`, `Entity List Pages`, `Scan API`?**
  _High betweenness centrality (0.193) - this node is a cross-community bridge._
- **Why does `create_scan()` connect `Scan API` to `Health & Core Models`, `Dashboard & Settings Pages`, `ARQ Redis Setup`, `Prefix API`, `Worker Scheduling`, `CRUD Router Factory`?**
  _High betweenness centrality (0.141) - this node is a cross-community bridge._
- **Why does `_resolve_prefix()` connect `Prefix Math` to `Worker Scheduling`, `Dashboard & Settings Pages`, `Prefix API`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `User` (e.g. with `bulk_addresses()` and `auth_status()`) actually correct?**
  _`User` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `IPAddress` (e.g. with `bulk_addresses()` and `create_address()`) actually correct?**
  _`IPAddress` has 18 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Row`, `SortKey`, `CellState` to the rest of the system?**
  _161 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Prefix Detail & Address UI` be split into smaller, more focused modules?**
  _Cohesion score 0.06388888888888888 - nodes in this community are weakly interconnected._