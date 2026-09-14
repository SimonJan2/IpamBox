# Graph Report - IpamBox  (2026-09-14)

## Corpus Check
- 47 files · ~99,999 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1300 nodes · 3566 edges · 83 communities (48 shown, 18 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 358 edges (avg confidence: 0.94)
- Token cost: 5,200 input · 7,300 output

## Community Hubs (Navigation)
- Backup API
- Auth API
- Env & Service Config
- Addresses API
- Frontend App Shell
- Data Pages
- Settings API
- Dashboard & Tree Views
- Settings Pages
- VLAN & VRF Pages
- Prefixes API
- Dashboard & Sites API
- VLANs API
- Data Table Pages
- Tags API
- Scans API
- RBAC Tests
- App Entry & Ops
- Compose Services
- Auth Pages & Filters
- Scanner Engine
- VRFs API
- Package Manifest
- Ranges API
- Prefix Model
- Prefix Math
- Scan Reconciliation
- Frontend Libraries
- Worker & Runtime
- TypeScript Config
- Test Fixtures
- README Doc
- Changelog Hooks
- Settings Tests
- IP Drawer UI
- Scan Cancel & Config
- Maintenance Tests
- IP Range Schemas
- Changelog API
- IPAM Extras Tests
- Scan Enqueue
- Settings Model
- Prefix API Tests
- Dev Dependencies
- User & Session Tests
- Changelog Tests
- NPM Scripts
- Badge Component
- Alembic Env
- App Icon & Metadata
- Tailwind Config
- Scanning Settings Page
- Scan Interval Env
- App Icon
- Backup Tables Registry
- Insecure Mode Env
- Cookie Secure Env
- Env Config Files
- Password Env
- Scan Excludes Env
- Scan Rate Limit Env
- Session Hours Env
- General Settings Page
- Appearance Page
- Security Doc
- bcrypt Dependency

## God Nodes (most connected - your core abstractions)
1. `cn()` - 63 edges
2. `User` - 43 edges
3. `IPAMError` - 43 edges
4. `get_or_404()` - 41 edges
5. `IPAddress` - 39 edges
6. `api service (FastAPI backend)` - 37 edges
7. `react` - 35 edges
8. `useAuth()` - 35 edges
9. `Prefix` - 33 edges
10. `Base` - 26 edges

## Surprising Connections (you probably didn't know these)
- `api service (FastAPI backend)` --implements--> `sqlalchemy[asyncio] 2.0.36`  [INFERRED]
  docker-compose.yml → /home/simonj/Documents/github/IpamBox/backend/requirements.txt
- `api service (FastAPI backend)` --implements--> `pydantic 2.10.3`  [INFERRED]
  docker-compose.yml → /home/simonj/Documents/github/IpamBox/backend/requirements.txt
- `api service (FastAPI backend)` --implements--> `fastapi 0.115.6`  [INFERRED]
  docker-compose.yml → /home/simonj/Documents/github/IpamBox/backend/requirements.txt
- `api service (FastAPI backend)` --references--> `alembic 1.14.0`  [INFERRED]
  docker-compose.yml → /home/simonj/Documents/github/IpamBox/backend/requirements.txt
- `api service (FastAPI backend)` --references--> `uvicorn[standard] 0.32.1`  [INFERRED]
  docker-compose.yml → /home/simonj/Documents/github/IpamBox/backend/requirements.txt

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Backup & Restore Flow** — readme_ep_backup, readme_ep_backup_files, readme_ep_backup_restore, readme_env_backup_dir [EXTRACTED 1.00]
- **IpamBox Container Service Stack** — docker_compose_service_db, docker_compose_service_redis, docker_compose_service_api, docker_compose_service_scanner, docker_compose_service_web [EXTRACTED 1.00]
- **Scanner Host-Network Access to Data Services** — docker_compose_service_scanner, docker_compose_service_db, docker_compose_service_redis [EXTRACTED 1.00]
- **Scheduled Backup Storage Sharing** — docker_compose_service_api, docker_compose_service_scanner, docker_compose_volume_backupdata [EXTRACTED 1.00]

## Communities (83 total, 18 thin omitted)

### Community 0 - "Backup API"
Cohesion: 0.06
Nodes (78): Any, delete_scheduled_backup(), download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, delete, get (+70 more)

### Community 1 - "Auth API"
Cohesion: 0.08
Nodes (72): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+64 more)

### Community 2 - "Env & Service Config"
Cohesion: 0.05
Nodes (68): CORS_ORIGINS env var, DATABASE_URL env var, NEXT_PUBLIC_API_URL env var, REDIS_URL env var, api service (FastAPI backend), db service (postgres:16-alpine), redis service (redis:7-alpine), scanner service (ARQ worker) (+60 more)

### Community 3 - "Addresses API"
Cohesion: 0.08
Nodes (46): bulk_addresses(), BulkBody, create_address(), delete_address(), export_addresses(), get_address(), import_addresses(), ImportRow (+38 more)

### Community 4 - "Frontend App Shell"
Cohesion: 0.06
Nodes (39): nextConfig, metadata, AppearancePage(), BackupSettingsPage(), downloadUrl(), fmtSize(), downloadUrl(), fmtSize() (+31 more)

### Community 5 - "Data Pages"
Cohesion: 0.10
Nodes (32): ChangelogPage(), DiscoveryPage(), DashboardPage(), AddressTable(), IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES (+24 more)

### Community 6 - "Settings API"
Cohesion: 0.10
Nodes (33): _build_out(), _lan_info(), _mask_url(), AsyncSession, get, patch, read_settings(), update_settings() (+25 more)

### Community 7 - "Dashboard & Tree Views"
Cohesion: 0.07
Nodes (29): PrefixTreeNode(), IpStatusBadge(), ipVariant, PrefixStatusBadge(), prefixVariant, ScanStatusBadge(), scanVariant, Progress (+21 more)

### Community 8 - "Settings Pages"
Cohesion: 0.10
Nodes (25): DataPage(), download(), UsersPage(), SitesPage(), TagsPage(), VlansPage(), VrfsPage(), AppShell() (+17 more)

### Community 9 - "VLAN & VRF Pages"
Cohesion: 0.13
Nodes (28): VLAN_STATUSES, QuickScanDialog(), useScanStream(), CardDescription(), CardFooter(), Checkbox, CheckboxProps, Dialog (+20 more)

### Community 10 - "Prefixes API"
Cohesion: 0.13
Nodes (30): AllocateIPRequest, allocate_next_available(), create_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), prefix_tree() (+22 more)

### Community 11 - "Dashboard & Sites API"
Cohesion: 0.11
Nodes (25): AsyncSession, get, stats(), create_site(), delete_site(), get_site(), list_sites(), AsyncSession (+17 more)

### Community 12 - "VLANs API"
Cohesion: 0.14
Nodes (29): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+21 more)

### Community 13 - "Data Table Pages"
Cohesion: 0.18
Nodes (18): ACTION_STYLES, ChangeSummary(), fmt(), PrefixesPage(), utilColor(), fmtEta(), ScansPage(), Table() (+10 more)

### Community 14 - "Tags API"
Cohesion: 0.12
Nodes (25): AssignBody, assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession (+17 more)

### Community 15 - "Scans API"
Cohesion: 0.14
Nodes (23): get_scan(), _job_payload(), list_scans(), AsyncSession, get, SSE stream of scan progress (Redis pub/sub backed)., Scanner configuration surfaced to the UI., scan_config() (+15 more)

### Community 16 - "RBAC Tests"
Cohesion: 0.25
Nodes (22): AsyncClient, UserRole, auth_on(), fake_arq(), login(), mkuser(), other_client(), AsyncSession (+14 more)

### Community 17 - "App Entry & Ops"
Cohesion: 0.19
Nodes (14): healthz(), metrics(), get, Readiness probe: verifies DB + Redis connectivity., Prometheus-style text exposition of object + scan counters., readyz(), Base, IPRange (+6 more)

### Community 18 - "Compose Services"
Cohesion: 0.11
Nodes (26): api service (FastAPI backend), db service (postgres:16-alpine), redis service (redis:7-alpine), scanner service (ARQ worker), web service (Next.js frontend), alembic upgrade head on api start, BACKUP_DIR env (default /backups), BACKUP_INTERVAL_MINUTES env (default 0) (+18 more)

### Community 19 - "Auth Pages & Filters"
Cohesion: 0.18
Nodes (16): AddressFilterPanel(), STATUS_DOT, STATUSES, TAG_COLORS, TagDialog(), Button, ButtonProps, buttonVariants (+8 more)

### Community 20 - "Scanner Engine"
Cohesion: 0.12
Nodes (21): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), detect_interface(), detect_local_cidr(), _icmp_sweep(), _ptr_lookup() (+13 more)

### Community 21 - "VRFs API"
Cohesion: 0.17
Nodes (19): create_vrf(), delete_vrf(), get_vrf(), list_vrfs(), AsyncSession, delete, get, patch (+11 more)

### Community 22 - "Package Manifest"
Cohesion: 0.09
Nodes (22): name, private, version, autoprefixer, clsx, postcss, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+14 more)

### Community 23 - "Ranges API"
Cohesion: 0.13
Nodes (20): delete_prefix(), delete, _check_range_overlap(), create_range(), delete_range(), list_ranges(), AsyncSession, delete (+12 more)

### Community 24 - "Prefix Model"
Cohesion: 0.21
Nodes (18): Prefix, PrefixStatus, str, Site, build_tree(), prefix_node(), site_node(), vrf_node() (+10 more)

### Community 25 - "Prefix Math"
Cohesion: 0.20
Nodes (19): prefix_stats(), children(), lowest_free(), parent_chain(), Inclusive [first, last] integer range of host-usable addresses., True when network/broadcast addresses are unusable for hosts (IPv4 <= /30)., Lowest usable address integer not in `taken` or any excluded range., Split `net` into children of `new_prefix` length. (+11 more)

### Community 26 - "Scan Reconciliation"
Cohesion: 0.13
Nodes (14): AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), HostResult, infer_device_type(), Best-effort device classification; None when nothing matched., fake_arq(), _pool() (+6 more)

### Community 27 - "Frontend Libraries"
Cohesion: 0.10
Nodes (21): dependencies, class-variance-authority, clsx, lucide-react, next, @radix-ui/react-dialog, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+13 more)

### Community 28 - "Worker & Runtime"
Cohesion: 0.21
Nodes (19): set_actor(), get_effective(), _cron_jobs(), _due(), _eta_seconds(), _global_vrf_id(), _periodic(), _publish() (+11 more)

### Community 29 - "TypeScript Config"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 30 - "Test Fixtures"
Cohesion: 0.19
Nodes (15): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Create the test database (if missing) and run migrations against it., sf(), test_url() (+7 more)

### Community 31 - "README Doc"
Cohesion: 0.12
Nodes (16): Architecture, Configuration, Development, Features, IPAM, IpamBox, LICENSE (MIT), Operations (+8 more)

### Community 32 - "Changelog Hooks"
Cohesion: 0.24
Nodes (13): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), Audit trail via session flush hooks. before_flush collects (object, action,…, register(), _repr() (+5 more)

### Community 33 - "Settings Tests"
Cohesion: 0.19
Nodes (13): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_files_report_effective_schedule(), test_internal_keys_hidden() (+5 more)

### Community 34 - "IP Drawer UI"
Cohesion: 0.17
Nodes (14): ROLES, STATUSES, Textarea, Sheet, SheetClose, SheetContent, SheetDescription, SheetHeader() (+6 more)

### Community 35 - "Scan Cancel & Config"
Cohesion: 0.19
Nodes (12): cancel_scan(), get_redis(), cancel_key(), _cancelled(), auth_on(), AsyncClient, fixture, Turn auth on for a test, restore insecure mode after, and flush session/lockout… (+4 more)

### Community 36 - "Maintenance Tests"
Cohesion: 0.21
Nodes (11): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_now_enqueues(), test_clear_discovery() (+3 more)

### Community 37 - "IP Range Schemas"
Cohesion: 0.24
Nodes (8): IPRangeRole, str, IPRangeCreate, IPRangeOut, IPRangeUpdate, BaseModel, field_validator, model_validator

### Community 38 - "Changelog API"
Cohesion: 0.27
Nodes (8): list_changelog(), AsyncSession, get, ChangeLog, NetBox-style audit trail: who changed what, when, and the field diff., ChangeField, ChangeLogOut, BaseModel

### Community 39 - "IPAM Extras Tests"
Cohesion: 0.42
Nodes (9): _prefix(), test_address_role_nat_and_bulk(), test_container_move_with_children_rejected(), test_csv_export_import(), test_ip_ranges_exclude_allocator(), test_prefix_move_vrf(), test_tags_crud_and_assignment(), test_vlan_group_and_prefix_link() (+1 more)

### Community 40 - "Scan Enqueue"
Cohesion: 0.22
Nodes (9): ArqRedis, _check_cidr_allowed(), create_scan(), post, get_arq_pool(), redis_settings_from_url(), RedisSettings, ScanCreate (+1 more)

### Community 41 - "Settings Model"
Cohesion: 0.25
Nodes (3): psycopg2-style URL for alembic offline mode / scripts., Settings, BaseSettings

### Community 42 - "Prefix API Tests"
Cohesion: 0.46
Nodes (7): _global_vrf_id(), test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_same_cidr_allowed_across_vrfs(), test_split_endpoint(), test_tree_endpoint(), test_unknown_vlan_rejected()

### Community 43 - "Dev Dependencies"
Cohesion: 0.25
Nodes (8): devDependencies, autoprefixer, postcss, tailwindcss, @types/node, @types/react, @types/react-dom, typescript

### Community 44 - "User & Session Tests"
Cohesion: 0.38
Nodes (6): auth_on(), AsyncClient, fixture, test_change_password_and_sessions(), test_revoke_session_endpoint(), test_users_crud_and_guards()

### Community 45 - "Changelog Tests"
Cohesion: 0.60
Nodes (4): AsyncClient, test_changelog_captures_ip_status_change(), test_changelog_records_crud(), test_changelog_scoped_filters()

### Community 46 - "NPM Scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 47 - "Badge Component"
Cohesion: 0.50
Nodes (4): Badge(), BadgeProps, badgeVariants, class-variance-authority

## Knowledge Gaps
- **175 isolated node(s):** `ButtonProps`, `WorkerSettings`, `Key`, `SwitchProps`, `DensityChoice` (+170 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 388 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Prefix` connect `Dashboard & Tree Views` to `Prefix Model`, `Prefixes API`, `Data Pages`, `Data Table Pages`?**
  _High betweenness centrality (0.200) - this node is a cross-community bridge._
- **Why does `create_prefix()` connect `Prefixes API` to `Dashboard & Tree Views`, `VLANs API`, `VRFs API`, `Ranges API`, `Prefix Model`, `Prefix Math`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Why does `create_scan()` connect `Scan Enqueue` to `Dashboard & Tree Views`, `Scans API`, `VRFs API`, `Ranges API`, `Worker & Runtime`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `User` (e.g. with `bulk_addresses()` and `change_password()`) actually correct?**
  _`User` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 30 inferred relationships involving `IPAMError` (e.g. with `create_address()` and `get_address()`) actually correct?**
  _`IPAMError` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `IPAddress` (e.g. with `bulk_addresses()` and `list_addresses()`) actually correct?**
  _`IPAddress` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `ButtonProps`, `WorkerSettings`, `Key` to the rest of the system?**
  _175 weakly-connected nodes found - possible documentation gaps or missing edges._