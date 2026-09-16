# Graph Report - IpamBox  (2026-09-16)

## Corpus Check
- 188 files · ~196,477 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: (none) 7, .ini 2, .example 1)

## Summary
- 1595 nodes · 4969 edges · 89 communities (66 shown, 6 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 392 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `574eb2ce`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [id]/page.tsx
- restore
- prefixes/page.tsx
- runtime_settings.py
- prefixes.py
- auth.tsx
- imports.py
- api service (FastAPI backend, alembic+uvicorn entrypoint)
- addresses.py
- upload_workbook
- index.ts
- get_or_404
- worker.py
- tags.py
- clean
- backup/page.tsx
- test_scanner.py
- IpamBox/backend/app/api/v1/auth.py
- prefs.ts
- entities.py
- react
- _build_out
- ip_display
- IPAddress
- _Planner
- User
- test_auth.py
- services/backup.py
- execute.py
- conftest.py
- package.json
- dependencies
- IpamBox
- usable_count
- parsers.py
- test_settings.py
- compilerOptions
- security.py
- ranges.py
- useAuth
- test_workbook_import.py
- TestNormalize
- _FakePool
- maintenance.py
- after_flush
- parse_site_sheet
- vlans.py
- classify_sheet
- create_vrf
- scanner service (ARQ worker, network_mode: host, NET_ADMIN/NET_RAW)
- backend/app/api/v1/auth.py
- confirm_discovered
- db service (postgres:16-alpine)
- Security Policy
- test_prefix_api.py
- devDependencies
- Backup & Restore
- test_users.py
- test_entities.py
- import/page.tsx
- schemas/changelog.py
- run_scan
- build_tree
- test_changelog.py
- scripts
- tailwindcss
- README.md — IpamBox project documentation
- Features
- readyz
- next-env.d.ts
- IpamBox App Icon (icon.svg)
- Root Layout (layout.tsx, title: IpamBox)

## God Nodes (most connected - your core abstractions)
1. `cn()` - 72 edges
2. `User` - 57 edges
3. `IPAddress` - 53 edges
4. `react` - 53 edges
5. `get_or_404()` - 51 edges
6. `IPAMError` - 50 edges
7. `useAuth()` - 45 edges
8. `Base` - 43 edges
9. `Prefix` - 41 edges
10. `lucide-react` - 40 edges

## Surprising Connections (you probably didn't know these)
- `pydantic-settings==2.6.1` --semantically_similar_to--> `Hybrid settings model (.env defaults + runtime overrides in app_settings)`  [INFERRED] [semantically similar]
  backend/requirements.txt → README.md
- `api service (FastAPI backend, alembic+uvicorn entrypoint)` --references--> `httpx==0.28.1`  [INFERRED]
  docker-compose.yml → backend/requirements.txt
- `scanner service (ARQ worker, network_mode: host, NET_ADMIN/NET_RAW)` --references--> `psutil==6.1.0`  [INFERRED]
  docker-compose.yml → backend/requirements.txt
- `pytest-asyncio==0.25.0` --references--> `api service (FastAPI backend, alembic+uvicorn entrypoint)`  [INFERRED]
  backend/requirements.txt → docker-compose.yml
- `Excel workbook import wizard (detect, dry-run, commit)` --references--> `api service (FastAPI backend, alembic+uvicorn entrypoint)`  [INFERRED]
  README.md → docker-compose.yml

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Shared SCAN_*/BACKUP_* env contract between api and scanner** — docker_compose_api, docker_compose_scanner, readme_hybrid_settings_model [EXTRACTED 1.00]
- **LAN scan -> fingerprint -> reconcile flow** — docker_compose_scanner, backend_requirements_arq, backend_requirements_scapy, readme_scan_pipeline, readme_discovery_reconciliation [INFERRED 0.85]
- **Scheduled snapshot backup flow (worker writes volume, API serves restore)** — docker_compose_api, docker_compose_scanner, docker_compose_backupdata, readme_backup_restore [INFERRED 0.85]

## Communities (89 total, 6 thin omitted)

### Community 0 - "[id]/page.tsx"
Cohesion: 0.07
Nodes (58): ChangelogPage(), IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, toggleIn(), TagsPage(), AddressFilterPanel() (+50 more)

### Community 1 - "restore"
Cohesion: 0.07
Nodes (42): delete_scheduled_backup(), download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, delete, get, post (+34 more)

### Community 2 - "prefixes/page.tsx"
Cohesion: 0.14
Nodes (37): EMPTY, ACTION_STYLES, ChangeSummary(), fmt(), EMPTY, EMPTY, EMPTY, VLAN_STATUSES (+29 more)

### Community 3 - "runtime_settings.py"
Cohesion: 0.10
Nodes (19): psycopg2-style URL for alembic offline mode / scripts., Settings, _env_sourced(), Any, Exception, Runtime-editable settings: app_settings rows override env defaults. Each public…, True when the field's current value differs from its declared default., Carries {key: message} so the API can return per-field 422s. (+11 more)

### Community 4 - "prefixes.py"
Cohesion: 0.13
Nodes (37): allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), AsyncSession (+29 more)

### Community 5 - "auth.tsx"
Cohesion: 0.14
Nodes (17): AppShell(), AUTH_ROUTES, NAV, QuickScanDialog(), useScanStream(), SETTINGS_SECTIONS, SettingsNav(), AuthContext (+9 more)

### Community 6 - "imports.py"
Cohesion: 0.14
Nodes (19): do_run_migrations(), run_migrations_online(), list_changelog(), AsyncSession, get, Workbook import endpoints: upload -> detect -> preview -> commit. The uploaded…, get_settings(), get_session() (+11 more)

### Community 7 - "api service (FastAPI backend, alembic+uvicorn entrypoint)"
Cohesion: 0.15
Nodes (16): alembic==1.14.0, fastapi==0.115.6, httpx==0.28.1, openpyxl==3.1.5, pydantic==2.10.3, pydantic-settings==2.6.1, pytest==8.3.4, pytest-asyncio==0.25.0 (+8 more)

### Community 8 - "addresses.py"
Cohesion: 0.13
Nodes (29): bulk_addresses(), BulkBody, create_address(), delete_address(), export_addresses(), get_address(), import_addresses(), ImportRow (+21 more)

### Community 9 - "upload_workbook"
Cohesion: 0.10
Nodes (31): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+23 more)

### Community 10 - "index.ts"
Cohesion: 0.06
Nodes (33): PrefixTreeNode(), IpStatusBadge(), ipVariant, PrefixStatusBadge(), prefixVariant, ScanStatusBadge(), scanVariant, Asset (+25 more)

### Community 11 - "get_or_404"
Cohesion: 0.09
Nodes (37): _crud_router(), delete_item(), get_item(), list_items(), update_item(), _check_range_overlap(), create_range(), delete_range() (+29 more)

### Community 12 - "worker.py"
Cohesion: 0.09
Nodes (41): ArqRedis, cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession (+33 more)

### Community 13 - "tags.py"
Cohesion: 0.18
Nodes (20): assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession, delete (+12 more)

### Community 14 - "clean"
Cohesion: 0.11
Nodes (28): assemble_ip(), clean(), _clean_octets(), map_status(), mask_to_prefixlen(), network_of(), norm_mac(), parse_range_end() (+20 more)

### Community 15 - "backup/page.tsx"
Cohesion: 0.08
Nodes (45): fmtEta(), ScansPage(), BackupSettingsPage(), downloadUrl(), fmtSize(), DataPage(), download(), downloadUrl() (+37 more)

### Community 16 - "test_scanner.py"
Cohesion: 0.06
Nodes (55): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), _arp_scan(), HostResult (+47 more)

### Community 17 - "IpamBox/backend/app/api/v1/auth.py"
Cohesion: 0.25
Nodes (20): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), AsyncSession (+12 more)

### Community 18 - "prefs.ts"
Cohesion: 0.12
Nodes (18): nextConfig, metadata, AppearancePage(), PrefsInit(), TooltipProvider, AddrMapView, applyPrefs(), DEFAULT_PREFS (+10 more)

### Community 19 - "entities.py"
Cohesion: 0.17
Nodes (18): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, AssetKind, str, AssetCreate, AssetOut, AssetUpdate, BaseModel, CertificateCreate (+10 more)

### Community 20 - "react"
Cohesion: 0.17
Nodes (13): ACTION_STYLES, DashboardPage(), expiryBadge(), Badge(), BadgeProps, badgeVariants, Progress, Separator (+5 more)

### Community 21 - "_build_out"
Cohesion: 0.18
Nodes (17): _build_out(), _mask_url(), AsyncSession, get, Hide the password in a scheme://user:pass@host URL., read_settings(), update_settings(), ChangePasswordBody (+9 more)

### Community 22 - "ip_display"
Cohesion: 0.16
Nodes (10): CircuitCreate, CircuitOut, CircuitUpdate, BaseModel, field_validator, ip_display(), Any, Normalize asyncpg-returned ipaddress objects / strings to display form. INET… (+2 more)

### Community 23 - "IPAddress"
Cohesion: 0.12
Nodes (29): AsyncSession, get, stats(), create_site(), post, IPAddress, Site, VRF (+21 more)

### Community 24 - "_Planner"
Cohesion: 0.19
Nodes (5): parse_sites_master_records(), _Planner, _preview(), site_key, matched_by for a site_sheet., Counter

### Community 25 - "User"
Cohesion: 0.07
Nodes (83): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+75 more)

### Community 26 - "test_auth.py"
Cohesion: 0.32
Nodes (7): auth_on(), AsyncClient, fixture, Turn auth on for a test, restore insecure mode after, and flush session/lockout…, test_endpoints_require_auth(), test_login_lockout(), test_setup_login_flow()

### Community 27 - "services/backup.py"
Cohesion: 0.12
Nodes (28): Audit trail via session flush hooks. before_flush collects (object, action,…, healthz(), metrics(), get, Prometheus-style text exposition of object + scan counters., AppSetting, Runtime-editable setting override. Absent row -> env var -> default., Asset (+20 more)

### Community 28 - "execute.py"
Cohesion: 0.21
Nodes (13): commit_batch(), execute_plan(), _get_or_create_prefix(), _get_or_create_site(), _get_or_create_vlan(), _get_or_create_vrf(), _group_by_sheet(), _insert_address() (+5 more)

### Community 29 - "conftest.py"
Cohesion: 0.17
Nodes (18): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., session() (+10 more)

### Community 30 - "package.json"
Cohesion: 0.10
Nodes (20): name, private, version, autoprefixer, clsx, postcss, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+12 more)

### Community 31 - "dependencies"
Cohesion: 0.10
Nodes (21): dependencies, class-variance-authority, clsx, lucide-react, next, @radix-ui/react-dialog, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+13 more)

### Community 32 - "IpamBox"
Cohesion: 0.12
Nodes (18): bcrypt==4.3.0, Architecture, Configuration, Development, Extended entities (WAN circuits, certificates, inventory, service catalog), First-run auth, session cookies, bcrypt hashing, IP lockout, Hebrew data support (final-letter folding, RTL rendering), IpamBox (+10 more)

### Community 33 - "usable_count"
Cohesion: 0.17
Nodes (17): children(), lowest_free(), parent_chain(), Inclusive [first, last] integer range of host-usable addresses., True when network/broadcast addresses are unusable for hosts (IPv4 <= /30)., Lowest usable address integer not in `taken` or any excluded range., Split `net` into children of `new_prefix` length., The smallest candidate network that strictly contains `net`. (+9 more)

### Community 34 - "parsers.py"
Cohesion: 0.17
Nodes (13): norm_header(), Header cell -> lowercase, single-spaced, for signature matching., _is_header_echo(), _map_columns(), parse_assets(), parse_inventory(), parse_servers(), parse_services() (+5 more)

### Community 35 - "test_settings.py"
Cohesion: 0.19
Nodes (13): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_files_report_effective_schedule(), test_internal_keys_hidden() (+5 more)

### Community 36 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 37 - "security.py"
Cohesion: 0.17
Nodes (22): get_redis(), clear_login_failures(), create_session(), destroy_other_sessions(), destroy_session(), destroy_session_by_suffix(), _fails_key(), get_session_user_id() (+14 more)

### Community 38 - "ranges.py"
Cohesion: 0.23
Nodes (11): list_ranges(), get, IPRange, IPRangeRole, str, A named block of addresses inside a prefix (e.g. a DHCP scope). Any defined…, IPRangeCreate, IPRangeOut (+3 more)

### Community 39 - "useAuth"
Cohesion: 0.21
Nodes (14): CertificatesPage(), expiryBadge(), CircuitsPage(), DiscoveryPage(), InventoryPage(), PrefixesPage(), utilColor(), ServicesPage() (+6 more)

### Community 40 - "test_workbook_import.py"
Cohesion: 0.16
Nodes (10): Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, parse_sites_master(), XLSX -> sheet matrices via openpyxl (read_only streams, values only)., SheetMatrix, Workbook import: normalizer/parser unit tests (no DB) + API e2e., Small synthetic workbook: sites master + one site sheet + circuits., test_commit_twice_rejected(), test_import_e2e() (+2 more)

### Community 41 - "TestNormalize"
Cohesion: 0.13
Nodes (6): excel_date(), datetime/date passthrough; int/float serial (20000-80000) -> date; 'd/m/yy'…, parse_certificates(), Positional 5-col layout: platform, target/VS, server, cert, expiry., TestNormalize, date

### Community 42 - "_FakePool"
Cohesion: 0.29
Nodes (5): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture

### Community 43 - "maintenance.py"
Cohesion: 0.15
Nodes (26): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+18 more)

### Community 44 - "after_flush"
Cohesion: 0.29
Nodes (10): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), register(), _repr(), _ser() (+2 more)

### Community 45 - "parse_site_sheet"
Cohesion: 0.25
Nodes (6): _blocks(), parse_site_sheet(), _positional_columns(), Headerless sheet: find the IP-fragment column, map the canonical layout…, Split duplicated column groups (031-style runaway): each block starts at an…, TestSiteSheetParser

### Community 46 - "vlans.py"
Cohesion: 0.18
Nodes (23): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+15 more)

### Community 47 - "classify_sheet"
Cohesion: 0.27
Nodes (7): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, _matrix(), TestClassify

### Community 48 - "create_vrf"
Cohesion: 0.27
Nodes (7): create_vrf(), post, BaseModel, field_validator, VRFCreate, VRFOut, VRFUpdate

### Community 49 - "scanner service (ARQ worker, network_mode: host, NET_ADMIN/NET_RAW)"
Cohesion: 0.24
Nodes (10): arq==0.26.1, asyncpg==0.30.0, psutil==6.1.0, redis==5.2.0 (Python client), scapy==2.6.1, sqlalchemy[asyncio]==2.0.36, scanner service (ARQ worker, network_mode: host, NET_ADMIN/NET_RAW), Discovery Inbox and drift reconciliation (+2 more)

### Community 50 - "backend/app/api/v1/auth.py"
Cohesion: 0.22
Nodes (12): me(), get, sessions(), Effective permission set; insecure mode (user=None) gets everything., user_permissions(), env_password(), Password provisioned via IPAMBOX_PASSWORD_FILE / IPAMBOX_PASSWORD., Password provisioned via IPAMBOX_PASSWORD_FILE / IPAMBOX_PASSWORD. (+4 more)

### Community 51 - "confirm_discovered"
Cohesion: 0.18
Nodes (11): confirm_discovered(), ConfirmBody, list_discovered(), AsyncSession, BaseModel, get, post, Unconfirmed hosts found by scanners, pending admin review. (+3 more)

### Community 52 - "db service (postgres:16-alpine)"
Cohesion: 0.32
Nodes (8): db service (postgres:16-alpine), pgdata volume, redis service (redis:7-alpine, appendonly), redisdata volume, Atomic next-available-IP allocation (SELECT FOR UPDATE + UNIQUE), PostgreSQL GiST exclusion constraint for CIDR overlap safety, Site -> VRF -> Prefix -> IP address hierarchy, Loopback-only Postgres/Redis binding (not exposed to LAN)

### Community 53 - "Security Policy"
Cohesion: 0.33
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 54 - "test_prefix_api.py"
Cohesion: 0.46
Nodes (7): _global_vrf_id(), test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_same_cidr_allowed_across_vrfs(), test_split_endpoint(), test_tree_endpoint(), test_unknown_vlan_rejected()

### Community 55 - "devDependencies"
Cohesion: 0.25
Nodes (8): devDependencies, autoprefixer, postcss, tailwindcss, @types/node, @types/react, @types/react-dom, typescript

### Community 56 - "Backup & Restore"
Cohesion: 0.40
Nodes (5): backupdata volume (/backups), Backup file format, Backup & Restore, Restore, Take a backup

### Community 57 - "test_users.py"
Cohesion: 0.38
Nodes (6): auth_on(), AsyncClient, fixture, test_change_password_and_sessions(), test_revoke_session_endpoint(), test_users_crud_and_guards()

### Community 59 - "import/page.tsx"
Cohesion: 0.22
Nodes (10): ACTION_STYLE, CommitResp, Counts, FAMILY_LABEL, ImportPage(), PreviewResp, UploadResp, ImportBatch (+2 more)

### Community 60 - "schemas/changelog.py"
Cohesion: 0.67
Nodes (3): ChangeField, ChangeLogOut, BaseModel

### Community 61 - "run_scan"
Cohesion: 0.12
Nodes (21): AsyncSession, Request, Guard for every API route. Returns the User, or None in allow_insecure mode., Guard for every API route. Returns the User, or None in allow_insecure mode., require_auth(), set_actor(), Effective, get_effective() (+13 more)

### Community 62 - "build_tree"
Cohesion: 0.36
Nodes (8): prefix_tree(), Site -> VRF -> nested prefix containment hierarchy., Site -> VRF -> nested prefix containment hierarchy., build_tree(), prefix_node(), site_node(), vrf_node(), Site -> VRF -> nested prefix containment tree.

### Community 63 - "test_changelog.py"
Cohesion: 0.60
Nodes (4): AsyncClient, test_changelog_captures_ip_status_change(), test_changelog_records_crud(), test_changelog_scoped_filters()

### Community 64 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 79 - "Features"
Cohesion: 0.50
Nodes (4): Features, IPAM, Platform, Scanner

### Community 80 - "readyz"
Cohesion: 0.67
Nodes (3): Readiness probe: verifies DB + Redis connectivity., readyz(), JSONResponse

## Knowledge Gaps
- **161 isolated node(s):** `WorkerSettings`, `nextConfig`, `name`, `version`, `private` (+156 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 493 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ScanJob` connect `react` to `prefixes/page.tsx`, `index.ts`, `worker.py`, `backup/page.tsx`, `run_scan`?**
  _High betweenness centrality (0.199) - this node is a cross-community bridge._
- **Why does `Prefix` connect `[id]/page.tsx` to `prefixes/page.tsx`, `prefixes.py`, `index.ts`, `backup/page.tsx`, `react`?**
  _High betweenness centrality (0.136) - this node is a cross-community bridge._
- **Why does `_resolve_prefix()` connect `prefixes.py` to `[id]/page.tsx`, `worker.py`, `run_scan`?**
  _High betweenness centrality (0.136) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `User` (e.g. with `bulk_addresses()` and `auth_status()`) actually correct?**
  _`User` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `IPAddress` (e.g. with `bulk_addresses()` and `create_address()`) actually correct?**
  _`IPAddress` has 18 INFERRED edges - model-reasoned connections that need verification._
- **What connects `WorkerSettings`, `nextConfig`, `name` to the rest of the system?**
  _161 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `[id]/page.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.0676056338028169 - nodes in this community are weakly interconnected._