# Graph Report - IpamBox  (2026-09-14)

## Corpus Check
- 155 files · ~167,036 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: (none) 7, .ini 2, .example 1)

## Summary
- 1202 nodes · 3188 edges · 81 communities (45 shown, 21 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 302 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Auth API & Alembic Env
- Backup API
- Settings UI Pages
- Addresses API
- IPAM List Pages
- Changelog Audit Hooks
- Prefixes API
- Dashboard & Prefix Detail Pages
- Documented Config & Endpoints
- Scans API
- Dashboard & Status Badges
- Worker & Redis Scheduling
- VLANs API
- Compose Services & Volumes
- IP Ranges API
- Tags API
- Scanner Engine & OUI
- Scans & Sites UI Pages
- Frontend Dependencies
- App Shell & UI Primitives
- Router & Dashboard API
- Scan Reconciliation
- Package Dependencies
- Auth & Tree Pages
- AppSetting Model & Tests
- Prefix Math Library
- VRFs API
- Runtime Settings Service
- TypeScript Config
- Settings API
- Test Infrastructure
- Sites API
- Users API
- README Documentation
- Prefix Schemas
- Backup Tests
- Maintenance Tests
- IP Drawer UI
- IPAM Extras Tests
- Prefix API Tests
- Dev Dependencies
- Users & Auth Tests
- Changelog Tests
- NPM Scripts
- Data Maintenance UI
- Settings Navigation
- App Icon & Title
- Tailwind Config
- Scan Interval Setting
- Scan Targeting Settings
- Scan Interval Env Var
- Backup Tables Registry
- Allow-Insecure Env Var
- Backup Keep Env Var
- Cookie Secure Env Var
- .env Config Files
- Admin Password Env Var
- Scan Exclude Env Var
- Scan Interface Env Var
- Scan Rate-Limit Env Var
- Scan TCP Ports Env Var
- Session Hours Env Var
- Settings General Page
- Settings Appearance Page
- Security Doc
- bcrypt Dependency

## God Nodes (most connected - your core abstractions)
1. `cn()` - 63 edges
2. `IPAMError` - 43 edges
3. `get_or_404()` - 41 edges
4. `IPAddress` - 39 edges
5. `react` - 35 edges
6. `Prefix` - 33 edges
7. `Base` - 26 edges
8. `VRF` - 24 edges
9. `api` - 24 edges
10. `get_settings()` - 23 edges

## Surprising Connections (you probably didn't know these)
- `api service (FastAPI backend)` --implements--> `sqlalchemy[asyncio] 2.0.36`  [INFERRED]
  docker-compose.yml → backend/requirements.txt
- `api service (FastAPI backend)` --implements--> `pydantic 2.10.3`  [INFERRED]
  docker-compose.yml → backend/requirements.txt
- `api service (FastAPI backend)` --implements--> `fastapi 0.115.6`  [INFERRED]
  docker-compose.yml → backend/requirements.txt
- `api service (FastAPI backend)` --references--> `alembic 1.14.0`  [INFERRED]
  docker-compose.yml → backend/requirements.txt
- `api service (FastAPI backend)` --references--> `uvicorn[standard] 0.32.1`  [INFERRED]
  docker-compose.yml → backend/requirements.txt

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Docker Compose full-stack services** — readme_svc_web, readme_svc_api, readme_svc_scanner, readme_svc_db, readme_svc_redis [EXTRACTED 1.00]
- **Hybrid env/DB runtime configuration flow** — readme_env_file, readme_table_app_settings, readme_ep_settings, readme_page_settings_scanning [EXTRACTED 1.00]
- **Settings area sub-navigation sections** — readme_page_settings, readme_page_settings_scanning, readme_page_settings_backup, readme_page_settings_security, readme_page_settings_appearance, readme_page_settings_data [EXTRACTED 1.00]

## Communities (81 total, 21 thin omitted)

### Community 0 - "Auth API & Alembic Env"
Cohesion: 0.06
Nodes (72): do_run_migrations(), run_migrations_online(), auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session() (+64 more)

### Community 1 - "Backup API"
Cohesion: 0.07
Nodes (64): Any, delete_scheduled_backup(), download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, delete, get (+56 more)

### Community 2 - "Settings UI Pages"
Cohesion: 0.06
Nodes (40): nextConfig, metadata, AppearancePage(), BackupSettingsPage(), downloadUrl(), fmtSize(), downloadUrl(), fmtSize() (+32 more)

### Community 3 - "Addresses API"
Cohesion: 0.10
Nodes (40): bulk_addresses(), BulkBody, create_address(), delete_address(), export_addresses(), get_address(), import_addresses(), ImportRow (+32 more)

### Community 4 - "IPAM List Pages"
Cohesion: 0.11
Nodes (30): PrefixesPage(), utilColor(), VLAN_STATUSES, QuickScanDialog(), useScanStream(), TAG_COLORS, TagPicker(), Dialog (+22 more)

### Community 5 - "Changelog Audit Hooks"
Cohesion: 0.14
Nodes (28): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), Audit trail via session flush hooks. before_flush collects (object, action,…, register(), _repr() (+20 more)

### Community 6 - "Prefixes API"
Cohesion: 0.14
Nodes (37): allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), prefix_tree() (+29 more)

### Community 7 - "Dashboard & Prefix Detail Pages"
Cohesion: 0.09
Nodes (32): ChangelogPage(), DiscoveryPage(), DashboardPage(), AddressTable(), IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES (+24 more)

### Community 8 - "Documented Config & Endpoints"
Cohesion: 0.07
Nodes (40): Alembic migrations (chain 0001→0009, auto-run on api start), API_PORT / WEB_PORT, BACKUP_DIR (scheduled-snapshot docker volume, default /backups), BACKUP_INTERVAL_MINUTES, POSTGRES_* credentials, GET /api/v1/backup, GET /api/v1/backup/files, POST /api/v1/backup/restore (?dry_run=1 preview) (+32 more)

### Community 9 - "Scans API"
Cohesion: 0.12
Nodes (30): cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession, get (+22 more)

### Community 10 - "Dashboard & Status Badges"
Cohesion: 0.08
Nodes (27): IpStatusBadge(), ipVariant, prefixVariant, ScanStatusBadge(), scanVariant, Badge(), BadgeProps, badgeVariants (+19 more)

### Community 11 - "Worker & Redis Scheduling"
Cohesion: 0.14
Nodes (26): ArqRedis, get_arq_pool(), redis_settings_from_url(), set_actor(), get_effective(), _cron_jobs(), _due(), _eta_seconds() (+18 more)

### Community 12 - "VLANs API"
Cohesion: 0.17
Nodes (25): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+17 more)

### Community 13 - "Compose Services & Volumes"
Cohesion: 0.11
Nodes (26): api service (FastAPI backend), db service (postgres:16-alpine), redis service (redis:7-alpine), scanner service (ARQ worker), web service (Next.js frontend), alembic upgrade head on api start, BACKUP_DIR env (default /backups), BACKUP_INTERVAL_MINUTES env (default 0) (+18 more)

### Community 14 - "IP Ranges API"
Cohesion: 0.14
Nodes (18): _check_range_overlap(), create_range(), delete_range(), list_ranges(), AsyncSession, delete, get, patch (+10 more)

### Community 15 - "Tags API"
Cohesion: 0.16
Nodes (20): assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession, delete (+12 more)

### Community 16 - "Scanner Engine & OUI"
Cohesion: 0.12
Nodes (21): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), detect_interface(), detect_local_cidr(), _icmp_sweep(), _ptr_lookup() (+13 more)

### Community 17 - "Scans & Sites UI Pages"
Cohesion: 0.20
Nodes (14): ACTION_STYLES, ChangeSummary(), fmt(), fmtEta(), ScansPage(), Table(), TableBody(), TableCell() (+6 more)

### Community 18 - "Frontend Dependencies"
Cohesion: 0.09
Nodes (22): name, private, version, autoprefixer, clsx, postcss, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+14 more)

### Community 19 - "App Shell & UI Primitives"
Cohesion: 0.16
Nodes (18): AppShell(), AUTH_ROUTES, NAV, Button, ButtonProps, buttonVariants, CardDescription(), CardFooter() (+10 more)

### Community 20 - "Router & Dashboard API"
Cohesion: 0.13
Nodes (14): list_changelog(), AsyncSession, get, AsyncSession, get, stats(), get_session(), AsyncSession (+6 more)

### Community 21 - "Scan Reconciliation"
Cohesion: 0.13
Nodes (14): AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), HostResult, infer_device_type(), Best-effort device classification; None when nothing matched., fake_arq(), _pool() (+6 more)

### Community 22 - "Package Dependencies"
Cohesion: 0.10
Nodes (21): dependencies, class-variance-authority, clsx, lucide-react, next, @radix-ui/react-dialog, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+13 more)

### Community 23 - "Auth & Tree Pages"
Cohesion: 0.20
Nodes (11): PrefixTreeNode(), PrefixStatusBadge(), Card, CardContent(), CardHeader(), CardTitle(), Checkbox, CheckboxProps (+3 more)

### Community 24 - "AppSetting Model & Tests"
Cohesion: 0.15
Nodes (15): AppSetting, Base, fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture (+7 more)

### Community 25 - "Prefix Math Library"
Cohesion: 0.21
Nodes (18): children(), lowest_free(), parent_chain(), Inclusive [first, last] integer range of host-usable addresses., True when network/broadcast addresses are unusable for hosts (IPv4 <= /30)., Lowest usable address integer not in `taken` or any excluded range., Split `net` into children of `new_prefix` length., The smallest candidate network that strictly contains `net`. (+10 more)

### Community 26 - "VRFs API"
Cohesion: 0.18
Nodes (15): create_vrf(), delete_vrf(), get_vrf(), list_vrfs(), AsyncSession, delete, get, patch (+7 more)

### Community 27 - "Runtime Settings Service"
Cohesion: 0.17
Nodes (15): Effective, _env_sourced(), patch(), Any, AsyncSession, Exception, SettingSpec, SettingsValidationError (+7 more)

### Community 28 - "TypeScript Config"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 29 - "Settings API"
Cohesion: 0.24
Nodes (16): _build_out(), _lan_info(), _mask_url(), AsyncSession, get, read_settings(), update_settings(), ChangePasswordBody (+8 more)

### Community 30 - "Test Infrastructure"
Cohesion: 0.19
Nodes (15): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Create the test database (if missing) and run migrations against it., sf(), test_url() (+7 more)

### Community 31 - "Sites API"
Cohesion: 0.21
Nodes (15): create_site(), delete_site(), get_site(), list_sites(), AsyncSession, delete, get, patch (+7 more)

### Community 32 - "Users API"
Cohesion: 0.21
Nodes (16): create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete, get (+8 more)

### Community 33 - "README Documentation"
Cohesion: 0.12
Nodes (16): Architecture, Configuration, Development, Features, IPAM, IpamBox, LICENSE (MIT), Operations (+8 more)

### Community 34 - "Prefix Schemas"
Cohesion: 0.22
Nodes (13): PrefixStatus, str, ip_display(), Normalize asyncpg-returned ipaddress objects / strings to display form. INET…, AllocateIPRequest, AvailableIPOut, PrefixCreate, PrefixOut (+5 more)

### Community 35 - "Backup Tests"
Cohesion: 0.36
Nodes (14): _backup_bytes(), _registry_names(), _restore(), _seed(), test_backup_roundtrip(), test_dry_run_does_not_write(), test_registry_covers_all_tables(), test_restore_preserves_users() (+6 more)

### Community 36 - "Maintenance Tests"
Cohesion: 0.21
Nodes (11): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_now_enqueues(), test_clear_discovery() (+3 more)

### Community 37 - "IP Drawer UI"
Cohesion: 0.21
Nodes (12): ROLES, STATUSES, Sheet, SheetClose, SheetContent, SheetDescription, SheetHeader(), SheetPortal (+4 more)

### Community 38 - "IPAM Extras Tests"
Cohesion: 0.42
Nodes (9): _prefix(), test_address_role_nat_and_bulk(), test_container_move_with_children_rejected(), test_csv_export_import(), test_ip_ranges_exclude_allocator(), test_prefix_move_vrf(), test_tags_crud_and_assignment(), test_vlan_group_and_prefix_link() (+1 more)

### Community 39 - "Prefix API Tests"
Cohesion: 0.46
Nodes (7): _global_vrf_id(), test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_same_cidr_allowed_across_vrfs(), test_split_endpoint(), test_tree_endpoint(), test_unknown_vlan_rejected()

### Community 40 - "Dev Dependencies"
Cohesion: 0.25
Nodes (8): devDependencies, autoprefixer, postcss, tailwindcss, @types/node, @types/react, @types/react-dom, typescript

### Community 41 - "Users & Auth Tests"
Cohesion: 0.38
Nodes (6): auth_on(), AsyncClient, fixture, test_change_password_and_sessions(), test_revoke_session_endpoint(), test_users_crud_and_guards()

### Community 42 - "Changelog Tests"
Cohesion: 0.60
Nodes (4): AsyncClient, test_changelog_captures_ip_status_change(), test_changelog_records_crud(), test_changelog_scoped_filters()

### Community 43 - "NPM Scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 44 - "Data Maintenance UI"
Cohesion: 0.60
Nodes (3): DataPage(), download(), ConfirmAction()

## Knowledge Gaps
- **173 isolated node(s):** `BackupFileInfo`, `ChangeField`, `RangeRole`, `VlanRef`, `VrfNode` (+168 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 361 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_resolve_prefix()` connect `Worker & Redis Scheduling` to `Prefix Math Library`, `Dashboard & Status Badges`, `Prefix Schemas`, `Prefixes API`?**
  _High betweenness centrality (0.157) - this node is a cross-community bridge._
- **Why does `Prefix` connect `Dashboard & Status Badges` to `Worker & Redis Scheduling`, `Dashboard & Prefix Detail Pages`, `IPAM List Pages`, `Auth & Tree Pages`?**
  _High betweenness centrality (0.156) - this node is a cross-community bridge._
- **Why does `create_scan()` connect `Scans API` to `Dashboard & Status Badges`, `Worker & Redis Scheduling`, `Changelog Audit Hooks`, `Prefixes API`?**
  _High betweenness centrality (0.145) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `IPAMError` (e.g. with `create_address()` and `get_address()`) actually correct?**
  _`IPAMError` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `IPAddress` (e.g. with `bulk_addresses()` and `list_addresses()`) actually correct?**
  _`IPAddress` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `BackupFileInfo`, `ChangeField`, `RangeRole` to the rest of the system?**
  _173 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Auth API & Alembic Env` be split into smaller, more focused modules?**
  _Cohesion score 0.05966386554621849 - nodes in this community are weakly interconnected._