# Graph Report - IpamBox  (2026-09-16)

## Corpus Check
- 60 files · ~195,794 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1572 nodes · 4137 edges · 101 communities (64 shown, 18 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 266 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Prefix Detail Pages
- Backup API
- Circuits & Import Pages
- Settings API
- Prefix Management API
- Discovery & Settings Pages
- Changelog & Stats API
- Backend Dependencies
- IP Address API
- Import API Endpoints
- Frontend Type Definitions
- Entity CRUD Router
- Scan Management API
- Tags API
- Workbook Normalizers
- Auth & Scan Pages
- Scanner Reconcile Logic
- Auth API
- Frontend App Shell
- Asset Entity Layer
- Certificates & Changelog Pages
- RBAC Tests
- Scanner OUI Lookup
- Sites & Stats API
- Import Plan Builder
- Backup Tests
- Migration Environment
- App Entry & Ops
- Circuits Import Execution
- Test Fixtures
- Frontend Package Meta
- Frontend Dependencies
- Users API
- Prefix Math Service
- Sheet Classifier
- Base Models & Changelog
- TypeScript Config
- Session Security Core
- IP Ranges API
- Backup Service
- Workbook Reader
- Cert Parser & Dates
- Maintenance Tests
- Maintenance API
- Changelog Engine
- Site Sheet Parser
- VLAN Models
- Classifier Tests
- Site Master Import
- IPAM Feature Tests
- Session Revocation
- Discovery API
- App Settings Model
- Scan Schemas
- Prefix API Tests
- Frontend Dev Dependencies
- Backup Settings UI
- Users API Tests
- Entity CRUD Tests
- Import UI Types
- Settings Page UI
- Auth Dependencies
- IPAM Tree Builder
- Changelog Tests
- Frontend Scripts
- Tailwind Config
- Project Docs
- Backup Delete Import
- Backup Request Import
- Backup Typing Import
- Backup Datetime Import
- Worker Prefix Import
- Exception Type
- Test Fixture Marker
- App Icon
- Layout TSX File
- IPAddressCreate Schema
- IPAddressUpdate Schema
- IP Status Enum
- ScanJob Type
- SiteCreate Schema
- SiteUpdate Schema

## God Nodes (most connected - your core abstractions)
1. `cn()` - 66 edges
2. `get_or_404()` - 49 edges
3. `IPAMError` - 48 edges
4. `IPAddress` - 46 edges
5. `react` - 41 edges
6. `useAuth()` - 34 edges
7. `Site` - 31 edges
8. `lucide-react` - 30 edges
9. `api` - 29 edges
10. `User` - 28 edges

## Surprising Connections (you probably didn't know these)
- `pydantic-settings==2.6.1` --semantically_similar_to--> `Hybrid settings model (.env defaults + runtime overrides in app_settings)`  [INFERRED] [semantically similar]
  backend/requirements.txt → README.md
- `Excel workbook import wizard (detect, dry-run, commit)` --references--> `api service (FastAPI backend, alembic+uvicorn entrypoint)`  [INFERRED]
  README.md → docker-compose.yml
- `scanner service (ARQ worker, network_mode: host, NET_ADMIN/NET_RAW)` --references--> `psutil==6.1.0`  [INFERRED]
  docker-compose.yml → backend/requirements.txt
- `api service (FastAPI backend, alembic+uvicorn entrypoint)` --references--> `httpx==0.28.1`  [INFERRED]
  docker-compose.yml → backend/requirements.txt
- `pytest-asyncio==0.25.0` --references--> `api service (FastAPI backend, alembic+uvicorn entrypoint)`  [INFERRED]
  backend/requirements.txt → docker-compose.yml

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **LAN scan -> fingerprint -> reconcile flow** — docker_compose_scanner, backend_requirements_arq, backend_requirements_scapy, readme_scan_pipeline, readme_discovery_reconciliation [INFERRED 0.85]
- **Scheduled snapshot backup flow (worker writes volume, API serves restore)** — docker_compose_api, docker_compose_scanner, docker_compose_backupdata, readme_backup_restore [INFERRED 0.85]
- **Shared SCAN_*/BACKUP_* env contract between api and scanner** — docker_compose_api, docker_compose_scanner, readme_hybrid_settings_model [EXTRACTED 1.00]

## Communities (101 total, 18 thin omitted)

### Community 0 - "Prefix Detail Pages"
Cohesion: 0.07
Nodes (56): ChangelogPage(), DashboardPage(), IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, toggleIn(), PrefixTreeNode() (+48 more)

### Community 1 - "Backup API"
Cohesion: 0.06
Nodes (55): Any, delete_scheduled_backup(), download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, get, post (+47 more)

### Community 2 - "Circuits & Import Pages"
Cohesion: 0.11
Nodes (38): CircuitsPage(), EMPTY, ACTION_STYLE, Counts, FAMILY_LABEL, EMPTY, InventoryPage(), PrefixesPage() (+30 more)

### Community 3 - "Settings API"
Cohesion: 0.06
Nodes (49): _build_out(), _lan_info(), _mask_url(), AsyncSession, get, patch, read_settings(), update_settings() (+41 more)

### Community 4 - "Prefix Management API"
Cohesion: 0.10
Nodes (45): AllocateIPRequest, allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses() (+37 more)

### Community 5 - "Discovery & Settings Pages"
Cohesion: 0.07
Nodes (33): DiscoveryPage(), DataPage(), download(), Key, ScanningPage(), UsersPage(), TagsPage(), VrfsPage() (+25 more)

### Community 6 - "Changelog & Stats API"
Cohesion: 0.08
Nodes (32): list_changelog(), AsyncSession, get, create_vrf(), delete_vrf(), get_vrf(), list_vrfs(), AsyncSession (+24 more)

### Community 7 - "Backend Dependencies"
Cohesion: 0.07
Nodes (43): alembic==1.14.0, arq==0.26.1, asyncpg==0.30.0, bcrypt==4.3.0, fastapi==0.115.6, httpx==0.28.1, openpyxl==3.1.5, psutil==6.1.0 (+35 more)

### Community 8 - "IP Address API"
Cohesion: 0.12
Nodes (34): bulk_addresses(), BulkBody, create_address(), delete_address(), export_addresses(), get_address(), import_addresses(), ImportRow (+26 more)

### Community 9 - "Import API Endpoints"
Cohesion: 0.11
Nodes (36): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+28 more)

### Community 10 - "Frontend Type Definitions"
Cohesion: 0.05
Nodes (36): AddressPage, Asset, AssetKind, AuthStatus, BackupFileInfo, Certificate, ChangeField, ChangeLogEntry (+28 more)

### Community 11 - "Entity CRUD Router"
Cohesion: 0.11
Nodes (33): _crud_router(), delete_item(), get_item(), list_items(), update_item(), delete_site(), delete, _check_duplicate_vid() (+25 more)

### Community 12 - "Scan Management API"
Cohesion: 0.11
Nodes (30): cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession, get (+22 more)

### Community 13 - "Tags API"
Cohesion: 0.13
Nodes (26): AssignBody, assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession (+18 more)

### Community 14 - "Workbook Normalizers"
Cohesion: 0.11
Nodes (28): assemble_ip(), clean(), _clean_octets(), map_status(), mask_to_prefixlen(), network_of(), norm_mac(), parse_range_end() (+20 more)

### Community 15 - "Auth & Scan Pages"
Cohesion: 0.16
Nodes (17): fmtEta(), ScansPage(), IpStatusBadge(), ipVariant, PrefixStatusBadge(), prefixVariant, ScanStatusBadge(), scanVariant (+9 more)

### Community 16 - "Scanner Reconcile Logic"
Cohesion: 0.10
Nodes (21): AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), _extra_vrf(), fake_arq(), _pool(), _FakeArqJob, _FakePool (+13 more)

### Community 17 - "Auth API"
Cohesion: 0.22
Nodes (30): AsyncSession, auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout() (+22 more)

### Community 18 - "Frontend App Shell"
Cohesion: 0.10
Nodes (23): nextConfig, metadata, AppearancePage(), fmtAgo(), SecurityPage(), PrefsInit(), SettingField(), SOURCE_STYLE (+15 more)

### Community 19 - "Asset Entity Layer"
Cohesion: 0.14
Nodes (20): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, AssetKind, str, AssetCreate, AssetOut, AssetUpdate, BaseModel, CertificateCreate (+12 more)

### Community 20 - "Certificates & Changelog Pages"
Cohesion: 0.19
Nodes (19): CertificatesPage(), EMPTY, expiryBadge(), ACTION_STYLES, ChangeSummary(), fmt(), Badge(), BadgeProps (+11 more)

### Community 21 - "RBAC Tests"
Cohesion: 0.21
Nodes (24): AsyncClient, auth_on(), fake_arq(), login(), mkuser(), other_client(), AsyncSession, fixture (+16 more)

### Community 22 - "Scanner OUI Lookup"
Cohesion: 0.11
Nodes (24): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), detect_interface(), detect_local_cidr(), HostResult, _icmp_sweep() (+16 more)

### Community 23 - "Sites & Stats API"
Cohesion: 0.15
Nodes (22): AsyncSession, get, stats(), create_site(), get_site(), list_sites(), AsyncSession, get (+14 more)

### Community 24 - "Import Plan Builder"
Cohesion: 0.18
Nodes (5): DbState, _Planner, Lookup indexes over the current DB contents., site_key, matched_by for a site_sheet., Counter

### Community 25 - "Backup Tests"
Cohesion: 0.23
Nodes (26): _backup_bytes(), _envelope_bytes(), _mkusers(), User, _registry_names(), _restore(), _seed(), test_backup_include_users_excludes_admins() (+18 more)

### Community 26 - "Migration Environment"
Cohesion: 0.13
Nodes (17): ArqRedis, do_run_migrations(), run_migrations_online(), get_settings(), get_arq_pool(), redis_settings_from_url(), env_password(), Password provisioned via IPAMBOX_PASSWORD_FILE / IPAMBOX_PASSWORD. (+9 more)

### Community 27 - "App Entry & Ops"
Cohesion: 0.12
Nodes (16): healthz(), metrics(), get, Readiness probe: verifies DB + Redis connectivity., Prometheus-style text exposition of object + scan counters., readyz(), Asset, Base (+8 more)

### Community 28 - "Circuits Import Execution"
Cohesion: 0.15
Nodes (16): Circuit, Base, WAN circuit row from the קוי-SDH-IPVPN sheet (Bezeq IPVPN/SDH/Metro…)., commit_batch(), execute_plan(), _get_or_create_prefix(), _get_or_create_site(), _get_or_create_vlan() (+8 more)

### Community 29 - "Test Fixtures"
Cohesion: 0.17
Nodes (18): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., session() (+10 more)

### Community 30 - "Frontend Package Meta"
Cohesion: 0.10
Nodes (20): name, private, version, autoprefixer, clsx, postcss, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+12 more)

### Community 31 - "Frontend Dependencies"
Cohesion: 0.10
Nodes (21): dependencies, class-variance-authority, clsx, lucide-react, next, @radix-ui/react-dialog, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+13 more)

### Community 32 - "Users API"
Cohesion: 0.21
Nodes (19): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+11 more)

### Community 33 - "Prefix Math Service"
Cohesion: 0.18
Nodes (17): children(), lowest_free(), parent_chain(), Inclusive [first, last] integer range of host-usable addresses., True when network/broadcast addresses are unusable for hosts (IPv4 <= /30)., Lowest usable address integer not in `taken` or any excluded range., Split `net` into children of `new_prefix` length., The smallest candidate network that strictly contains `net`. (+9 more)

### Community 34 - "Sheet Classifier"
Cohesion: 0.13
Nodes (16): _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., norm_header(), Header cell -> lowercase, single-spaced, for signature matching., _is_header_echo(), _map_columns(), parse_assets() (+8 more)

### Community 35 - "Base Models & Changelog"
Cohesion: 0.27
Nodes (7): Base, ChangeLog, NetBox-style audit trail: who changed what, when, and the field diff., ScanJob, VLANGroup, datetime, DeclarativeBase

### Community 36 - "TypeScript Config"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 37 - "Session Security Core"
Cohesion: 0.23
Nodes (17): get_redis(), clear_login_failures(), create_session(), destroy_other_sessions(), destroy_session(), destroy_user_sessions(), _fails_key(), get_session_user_id() (+9 more)

### Community 38 - "IP Ranges API"
Cohesion: 0.18
Nodes (14): _check_range_overlap(), create_range(), delete_range(), list_ranges(), AsyncSession, delete, get, patch (+6 more)

### Community 39 - "Backup Service"
Cohesion: 0.20
Nodes (14): BackupPreview, BackupTable, _fail_inflight_scans(), _has_serial_id(), AsyncSession, Full-database backup & restore. Data tables are exported into a single gzipped…, Replace the non-admin user set from a users-inclusive envelope. Admin rows in…, Wipe all registered tables and re-load them from the backup envelope. Runs… (+6 more)

### Community 40 - "Workbook Reader"
Cohesion: 0.20
Nodes (10): Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, load_workbook_bytes(), XLSX -> sheet matrices via openpyxl (read_only streams, values only)., Parse workbook bytes into per-sheet row matrices. read_only + data_only:…, SheetMatrix, Workbook import: normalizer/parser unit tests (no DB) + API e2e., Small synthetic workbook: sites master + one site sheet + circuits., test_commit_twice_rejected() (+2 more)

### Community 41 - "Cert Parser & Dates"
Cohesion: 0.13
Nodes (6): excel_date(), datetime/date passthrough; int/float serial (20000-80000) -> date; 'd/m/yy'…, parse_certificates(), Positional 5-col layout: platform, target/VS, server, cert, expiry., TestNormalize, date

### Community 42 - "Maintenance Tests"
Cohesion: 0.21
Nodes (11): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_now_enqueues(), test_clear_discovery() (+3 more)

### Community 43 - "Maintenance API"
Cohesion: 0.41
Nodes (12): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+4 more)

### Community 44 - "Changelog Engine"
Cohesion: 0.35
Nodes (11): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), Audit trail via session flush hooks. before_flush collects (object, action,…, register(), _repr() (+3 more)

### Community 45 - "Site Sheet Parser"
Cohesion: 0.25
Nodes (6): _blocks(), parse_site_sheet(), _positional_columns(), Headerless sheet: find the IP-fragment column, map the canonical layout…, Split duplicated column groups (031-style runaway): each block starts at an…, TestSiteSheetParser

### Community 46 - "VLAN Models"
Cohesion: 0.38
Nodes (9): str, VLANStatus, BaseModel, VLANCreate, VLANGroupCreate, VLANGroupOut, VLANGroupUpdate, VLANOut (+1 more)

### Community 47 - "Classifier Tests"
Cohesion: 0.42
Nodes (4): classify_sheet(), (family, header_row_index, warnings). header_row_index = index of the row…, _matrix(), TestClassify

### Community 48 - "Site Master Import"
Cohesion: 0.22
Nodes (7): parse_sites_master(), parse_sites_master_records(), _preview(), Build the import plan: classify+parse sheets, resolve sites/VRFs/prefixes,…, _site_key(), _vrf_name_for(), TestSitesMasterParser

### Community 49 - "IPAM Feature Tests"
Cohesion: 0.42
Nodes (9): _prefix(), test_address_role_nat_and_bulk(), test_container_move_with_children_rejected(), test_csv_export_import(), test_ip_ranges_exclude_allocator(), test_prefix_move_vrf(), test_tags_crud_and_assignment(), test_vlan_group_and_prefix_link() (+1 more)

### Community 50 - "Session Revocation"
Cohesion: 0.39
Nodes (7): delete, revoke_session(), destroy_session_by_suffix(), AuthStatus, LoginBody, BaseModel, SetupBody

### Community 51 - "Discovery API"
Cohesion: 0.22
Nodes (9): confirm_discovered(), ConfirmBody, list_discovered(), AsyncSession, BaseModel, get, post, Unconfirmed hosts found by scanners, pending admin review. (+1 more)

### Community 52 - "App Settings Model"
Cohesion: 0.22
Nodes (3): psycopg2-style URL for alembic offline mode / scripts., Settings, BaseSettings

### Community 53 - "Scan Schemas"
Cohesion: 0.31
Nodes (7): str, ScanStatus, BaseModel, field_validator, ScanConfigOut, ScanCreate, ScanJobOut

### Community 54 - "Prefix API Tests"
Cohesion: 0.46
Nodes (7): _global_vrf_id(), test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_same_cidr_allowed_across_vrfs(), test_split_endpoint(), test_tree_endpoint(), test_unknown_vlan_rejected()

### Community 55 - "Frontend Dev Dependencies"
Cohesion: 0.25
Nodes (8): devDependencies, autoprefixer, postcss, tailwindcss, @types/node, @types/react, @types/react-dom, typescript

### Community 56 - "Backup Settings UI"
Cohesion: 0.32
Nodes (7): BackupSettingsPage(), downloadUrl(), fmtSize(), BackupFilesOut, BackupPreview, RestoreReport, SettingsOut

### Community 57 - "Users API Tests"
Cohesion: 0.38
Nodes (6): auth_on(), AsyncClient, fixture, test_change_password_and_sessions(), test_revoke_session_endpoint(), test_users_crud_and_guards()

### Community 59 - "Import UI Types"
Cohesion: 0.33
Nodes (6): CommitResp, PreviewResp, UploadResp, ImportBatch, RowResult, SheetPreview

### Community 60 - "Settings Page UI"
Cohesion: 0.53
Nodes (4): downloadUrl(), fmtSize(), fmtTs(), SettingsPage()

### Community 61 - "Auth Dependencies"
Cohesion: 0.40
Nodes (5): AsyncSession, Request, Guard for every API route. Returns the User, or None in allow_insecure mode., require_auth(), set_actor()

### Community 62 - "IPAM Tree Builder"
Cohesion: 0.70
Nodes (5): build_tree(), prefix_node(), site_node(), vrf_node(), Site -> VRF -> nested prefix containment tree.

### Community 63 - "Changelog Tests"
Cohesion: 0.60
Nodes (4): AsyncClient, test_changelog_captures_ip_status_change(), test_changelog_records_crud(), test_changelog_scoped_filters()

### Community 64 - "Frontend Scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

## Knowledge Gaps
- **152 isolated node(s):** `CheckboxProps`, `WorkerSettings`, `CellState`, `BadgeProps`, `AuthCtx` (+147 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 489 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ScanJob` connect `Scan Management API` to `Frontend Type Definitions`, `Auth & Scan Pages`?**
  _High betweenness centrality (0.189) - this node is a cross-community bridge._
- **Are the 34 inferred relationships involving `IPAMError` (e.g. with `create_address()` and `delete_address()`) actually correct?**
  _`IPAMError` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `IPAddress` (e.g. with `bulk_addresses()` and `create_address()`) actually correct?**
  _`IPAddress` has 17 INFERRED edges - model-reasoned connections that need verification._
- **What connects `CheckboxProps`, `WorkerSettings`, `CellState` to the rest of the system?**
  _152 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Prefix Detail Pages` be split into smaller, more focused modules?**
  _Cohesion score 0.06862745098039216 - nodes in this community are weakly interconnected._
- **Should `Backup API` be split into smaller, more focused modules?**
  _Cohesion score 0.05632360471070148 - nodes in this community are weakly interconnected._
- **Should `Circuits & Import Pages` be split into smaller, more focused modules?**
  _Cohesion score 0.1111111111111111 - nodes in this community are weakly interconnected._