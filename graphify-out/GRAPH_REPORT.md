# Graph Report - IpamBox  (2026-09-14)

## Corpus Check
- 47 files · ~99,999 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1312 nodes · 3618 edges · 82 communities (47 shown, 18 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 358 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Auth API
- Env & Service Config
- Maintenance & Backup API
- App Layout & Settings Pages
- Settings API
- Prefixes API
- Prefix Detail Page
- Addresses API
- Changelog & Dashboard API
- Settings Data & Security Pages
- IP Drawer & Badges
- Prefixes & VLANs Pages
- VLANs API
- Changelog & Discovery Pages
- Changelog Hooks & App Entry
- Login, Setup & Tree Pages
- RBAC Tests
- Compose Services
- Ranges API
- Worker & Runtime
- Scans API
- Prefix Math & Stats
- Tags API
- Package Manifest
- VRFs API
- README & Docs
- Frontend Dependencies
- Scanner Engine
- Sites API
- Test Fixtures
- TypeScript Config
- Scan Reconciliation
- Backup Tests
- Maintenance Tests
- Address Map UI Components
- Changelog Flush Hooks
- Tag Schemas
- IPAM Extras Tests
- Settings Model
- Device Type Inference
- Prefix API Tests
- Dev Dependencies
- User & Session Tests
- Health Probes
- Changelog Tests
- NPM Scripts
- Alembic Env
- Changelog Schemas
- App Icon & Metadata
- Tailwind Config
- Scan Interval Env
- Scan Interval Default
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
7. `useAuth()` - 35 edges
8. `react` - 35 edges
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

## Communities (82 total, 18 thin omitted)

### Community 0 - "Auth API"
Cohesion: 0.05
Nodes (101): AsyncSession, auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout() (+93 more)

### Community 1 - "Env & Service Config"
Cohesion: 0.05
Nodes (68): CORS_ORIGINS env var, DATABASE_URL env var, NEXT_PUBLIC_API_URL env var, REDIS_URL env var, api service (FastAPI backend), db service (postgres:16-alpine), redis service (redis:7-alpine), scanner service (ARQ worker) (+60 more)

### Community 2 - "Maintenance & Backup API"
Cohesion: 0.07
Nodes (54): Any, _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody (+46 more)

### Community 3 - "App Layout & Settings Pages"
Cohesion: 0.05
Nodes (47): nextConfig, metadata, AppearancePage(), BackupSettingsPage(), downloadUrl(), fmtSize(), downloadUrl(), fmtSize() (+39 more)

### Community 4 - "Settings API"
Cohesion: 0.06
Nodes (49): _build_out(), _lan_info(), _mask_url(), AsyncSession, get, patch, read_settings(), update_settings() (+41 more)

### Community 5 - "Prefixes API"
Cohesion: 0.10
Nodes (44): AllocateIPRequest, allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses() (+36 more)

### Community 6 - "Prefix Detail Page"
Cohesion: 0.09
Nodes (36): IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, toggleIn(), CellState, stateClass, SubnetGrid() (+28 more)

### Community 7 - "Addresses API"
Cohesion: 0.11
Nodes (35): bulk_addresses(), BulkBody, create_address(), delete_address(), export_addresses(), get_address(), import_addresses(), ImportRow (+27 more)

### Community 8 - "Changelog & Dashboard API"
Cohesion: 0.08
Nodes (29): list_changelog(), AsyncSession, get, AsyncSession, get, stats(), confirm_discovered(), ConfirmBody (+21 more)

### Community 9 - "Settings Data & Security Pages"
Cohesion: 0.09
Nodes (28): DataPage(), download(), fmtAgo(), UsersPage(), SitesPage(), TagsPage(), VlansPage(), VrfsPage() (+20 more)

### Community 10 - "IP Drawer & Badges"
Cohesion: 0.07
Nodes (34): ROLES, STATUSES, IpStatusBadge(), ipVariant, prefixVariant, scanVariant, Textarea, Sheet (+26 more)

### Community 11 - "Prefixes & VLANs Pages"
Cohesion: 0.16
Nodes (20): PrefixesPage(), utilColor(), VLAN_STATUSES, QuickScanDialog(), useScanStream(), Dialog, DialogClose, DialogContent (+12 more)

### Community 12 - "VLANs API"
Cohesion: 0.14
Nodes (30): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+22 more)

### Community 13 - "Changelog & Discovery Pages"
Cohesion: 0.17
Nodes (22): ACTION_STYLES, ChangelogPage(), ChangeSummary(), fmt(), DiscoveryPage(), DashboardPage(), fmtEta(), ScansPage() (+14 more)

### Community 14 - "Changelog Hooks & App Entry"
Cohesion: 0.23
Nodes (12): Audit trail via session flush hooks. before_flush collects (object, action,…, metrics(), Prometheus-style text exposition of object + scan counters., Base, ChangeLog, NetBox-style audit trail: who changed what, when, and the field diff., Site, VRF (+4 more)

### Community 15 - "Login, Setup & Tree Pages"
Cohesion: 0.14
Nodes (16): PrefixTreeNode(), PrefixStatusBadge(), ScanStatusBadge(), Card, CardContent(), CardDescription(), CardFooter(), CardHeader() (+8 more)

### Community 16 - "RBAC Tests"
Cohesion: 0.25
Nodes (22): AsyncClient, UserRole, auth_on(), fake_arq(), login(), mkuser(), other_client(), AsyncSession (+14 more)

### Community 17 - "Compose Services"
Cohesion: 0.11
Nodes (26): api service (FastAPI backend), db service (postgres:16-alpine), redis service (redis:7-alpine), scanner service (ARQ worker), web service (Next.js frontend), alembic upgrade head on api start, BACKUP_DIR env (default /backups), BACKUP_INTERVAL_MINUTES env (default 0) (+18 more)

### Community 18 - "Ranges API"
Cohesion: 0.16
Nodes (20): _check_range_overlap(), create_range(), delete_range(), list_ranges(), AsyncSession, delete, get, patch (+12 more)

### Community 19 - "Worker & Runtime"
Cohesion: 0.16
Nodes (22): ArqRedis, get_arq_pool(), redis_settings_from_url(), set_actor(), cancel_key(), _cron_jobs(), _due(), _eta_seconds() (+14 more)

### Community 20 - "Scans API"
Cohesion: 0.13
Nodes (23): cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession, get (+15 more)

### Community 21 - "Prefix Math & Stats"
Cohesion: 0.19
Nodes (21): dashboard_stats(), prefix_stats(), AsyncSession, children(), lowest_free(), parent_chain(), Inclusive [first, last] integer range of host-usable addresses., True when network/broadcast addresses are unusable for hosts (IPv4 <= /30). (+13 more)

### Community 22 - "Tags API"
Cohesion: 0.19
Nodes (20): AssignBody, assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession (+12 more)

### Community 23 - "Package Manifest"
Cohesion: 0.09
Nodes (21): name, private, version, autoprefixer, clsx, postcss, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+13 more)

### Community 24 - "VRFs API"
Cohesion: 0.16
Nodes (17): create_vrf(), delete_vrf(), get_vrf(), list_vrfs(), AsyncSession, delete, get, patch (+9 more)

### Community 25 - "README & Docs"
Cohesion: 0.10
Nodes (21): backend/app/services/backup.py (BACKUP_TABLES registry — one entry per table ordered by FK dependency), .env.example (annotated list of environment variables), LICENSE (MIT © SimonJan2), SECURITY.md (threat model, deployment hardening, vulnerability reporting), IpamBox README — self-hosted, containerized IPAM with built-in LAN scanner (v0.2.0, MIT), Architecture, Configuration, Development (+13 more)

### Community 26 - "Frontend Dependencies"
Cohesion: 0.10
Nodes (21): dependencies, class-variance-authority, clsx, lucide-react, next, @radix-ui/react-dialog, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+13 more)

### Community 27 - "Scanner Engine"
Cohesion: 0.15
Nodes (17): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), detect_interface(), detect_local_cidr(), _icmp_sweep(), Exception (+9 more)

### Community 28 - "Sites API"
Cohesion: 0.19
Nodes (17): create_site(), delete_site(), get_site(), list_sites(), AsyncSession, delete, get, patch (+9 more)

### Community 29 - "Test Fixtures"
Cohesion: 0.19
Nodes (16): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Create the test database (if missing) and run migrations against it., session(), sf() (+8 more)

### Community 30 - "TypeScript Config"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 31 - "Scan Reconciliation"
Cohesion: 0.15
Nodes (11): AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), HostResult, fake_arq(), _pool(), _FakeArqJob, _FakePool (+3 more)

### Community 32 - "Backup Tests"
Cohesion: 0.36
Nodes (14): _backup_bytes(), _registry_names(), _restore(), _seed(), test_backup_roundtrip(), test_dry_run_does_not_write(), test_registry_covers_all_tables(), test_restore_preserves_users() (+6 more)

### Community 33 - "Maintenance Tests"
Cohesion: 0.21
Nodes (11): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_now_enqueues(), test_clear_discovery() (+3 more)

### Community 34 - "Address Map UI Components"
Cohesion: 0.26
Nodes (9): AddressFilterPanel(), STATUS_DOT, STATUSES, TAG_COLORS, TagDialog(), Button, ButtonProps, buttonVariants (+1 more)

### Community 35 - "Changelog Flush Hooks"
Cohesion: 0.25
Nodes (10): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), register(), _repr(), _ser() (+2 more)

### Community 36 - "Tag Schemas"
Cohesion: 0.29
Nodes (7): AssignBody, BaseModel, field_validator, TagAssignmentOut, TagCreate, TagOut, TagUpdate

### Community 37 - "IPAM Extras Tests"
Cohesion: 0.42
Nodes (9): _prefix(), test_address_role_nat_and_bulk(), test_container_move_with_children_rejected(), test_csv_export_import(), test_ip_ranges_exclude_allocator(), test_prefix_move_vrf(), test_tags_crud_and_assignment(), test_vlan_group_and_prefix_link() (+1 more)

### Community 38 - "Settings Model"
Cohesion: 0.25
Nodes (3): psycopg2-style URL for alembic offline mode / scripts., Settings, BaseSettings

### Community 39 - "Device Type Inference"
Cohesion: 0.29
Nodes (7): infer_device_type(), _ptr_lookup(), Best-effort device classification; None when nothing matched., enrich(), _tcp_probe(), test_device_type_inference(), Semaphore

### Community 40 - "Prefix API Tests"
Cohesion: 0.46
Nodes (7): _global_vrf_id(), test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_same_cidr_allowed_across_vrfs(), test_split_endpoint(), test_tree_endpoint(), test_unknown_vlan_rejected()

### Community 41 - "Dev Dependencies"
Cohesion: 0.25
Nodes (8): devDependencies, autoprefixer, postcss, tailwindcss, @types/node, @types/react, @types/react-dom, typescript

### Community 42 - "User & Session Tests"
Cohesion: 0.38
Nodes (6): auth_on(), AsyncClient, fixture, test_change_password_and_sessions(), test_revoke_session_endpoint(), test_users_crud_and_guards()

### Community 43 - "Health Probes"
Cohesion: 0.40
Nodes (5): healthz(), get, Readiness probe: verifies DB + Redis connectivity., readyz(), JSONResponse

### Community 44 - "Changelog Tests"
Cohesion: 0.60
Nodes (4): AsyncClient, test_changelog_captures_ip_status_change(), test_changelog_records_crud(), test_changelog_scoped_filters()

### Community 45 - "NPM Scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 47 - "Changelog Schemas"
Cohesion: 0.67
Nodes (3): ChangeField, ChangeLogOut, BaseModel

## Knowledge Gaps
- **181 isolated node(s):** `BackupFileInfo`, `ChangeField`, `LanInfo`, `RangeRole`, `SystemInfo` (+176 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 392 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Prefix` connect `Login, Setup & Tree Pages` to `Prefixes API`, `Prefix Detail Page`, `IP Drawer & Badges`, `Prefixes & VLANs Pages`, `Changelog & Discovery Pages`?**
  _High betweenness centrality (0.213) - this node is a cross-community bridge._
- **Why does `create_prefix()` connect `Prefixes API` to `VLANs API`, `Changelog Hooks & App Entry`, `Login, Setup & Tree Pages`, `Ranges API`, `Prefix Math & Stats`, `Sites API`?**
  _High betweenness centrality (0.117) - this node is a cross-community bridge._
- **Why does `_resolve_prefix()` connect `Prefixes API` to `Worker & Runtime`, `Prefix Math & Stats`, `Login, Setup & Tree Pages`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `User` (e.g. with `bulk_addresses()` and `me()`) actually correct?**
  _`User` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 30 inferred relationships involving `IPAMError` (e.g. with `create_address()` and `get_address()`) actually correct?**
  _`IPAMError` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `IPAddress` (e.g. with `bulk_addresses()` and `list_addresses()`) actually correct?**
  _`IPAddress` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `BackupFileInfo`, `ChangeField`, `LanInfo` to the rest of the system?**
  _181 weakly-connected nodes found - possible documentation gaps or missing edges._