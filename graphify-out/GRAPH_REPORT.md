# Graph Report - IpamBox  (2026-09-22)

## Corpus Check
- 315 files · ~256,187 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: (none) 7, .ini 2, .example 1)

## Summary
- 2758 nodes · 8036 edges · 192 communities (96 shown, 70 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 524 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Client Pages & Forms
- Discovery & Import UI
- Prefix Detail & IP Grid
- Frontend Pages
- Address API
- Core & Changelog
- Import Wizard
- App Shell & Nav
- Prefix API
- IP Normalization
- Master Planner
- DB Migrations
- Import Service
- Dependencies
- CRUD Router
- Backup & Sweep
- Scan Reconcile
- Redis & LAN
- Exclusions & Inference
- Error Pages
- Auth API
- Color Rules API
- Setup & Discovery UI
- Settings Module
- Dialogs
- Docs UI
- Sites API
- Backup API
- Scans API
- Backup Tests
- Api Module
- Status Module
- Schemas Module
- Api Module
- Core Module
- Services Module
- Services Module
- Schemas Module
- Tests Module
- Schemas Module
- Api Module
- Tests Module
- Package Module
- Package Module
- Prefix Module
- Schemas Module
- Services Module
- Worker Module
- Api Module
- Services Module
- Tests Module
- Shell Module
- Api Module
- Tests Module
- Content Module
- Tsconfig Module
- Tests Module
- Home Module
- Tests Module
- Schemas Module
- Api Module
- Services Module
- Tests Module
- Import Module
- Settings Module
- Models Module
- Tests Module
- Worker Module
- Tests Module
- Tests Module
- Tests Module
- Tests Module
- Tests Module
- Tests Module
- Schemas Module
- Core Module
- Tests Module
- Tests Module
- History Module
- Prefixes Module
- Settings Module
- Package Module
- Services Module
- Tests Module
- Prefixes Module
- Tests Module
- Inventory Module
- Tree Module
- Vlans Module
- Tests Module
- Package Module
- Shortcuts Module
- Use Module
- Status Module
- Security Module
- Vrfs Module
- Requirements Module
- Tests Module
- Changelog Module
- Page Module
- Login Module
- Setup Module
- Home Module
- Changelog Module
- Inventory Module
- Settings Module
- Settings Module
- Requirements Module
- Certificates Module
- Circuits Module
- Discovery Module
- Import Module
- Prefixes Module
- Prefixes Module
- Scans Module
- Services Module
- Settings Module
- Settings Module
- Settings Module
- Settings Module
- Settings Module
- Settings Module
- Settings Module
- Settings Module
- Sites Module
- Tags Module
- Vlans Module
- Vrfs Module
- Home Module
- Home Module
- Settings Module
- Requirements Module
- Requirements Module
- Next Module
- Tailwind Module
- Xff Module
- Next Module
- Home Module
- Home Module
- Allocateiprequest Module
- Api Module
- Api Module
- Requirements Module
- Requirements Module
- Requirements Module
- Requirements Module
- Requirements Module
- Basemodel Module
- Icon Module
- Layout Module
- Content Module
- Content Module
- Home Module
- Ipstatus Module
- Prefixcreate Module
- Prefixout Module
- Prefixupdate Module
- Readme Module
- Readme Module
- Readme Module
- Readme Module
- Home Module
- Home Module
- Home Module
- Home Module
- Home Module

## God Nodes (most connected - your core abstractions)
1. `cn()` - 114 edges
2. `react` - 97 edges
3. `User` - 62 edges
4. `IPAMError` - 60 edges
5. `IPAddress` - 59 edges
6. `lucide-react` - 56 edges
7. `get_or_404()` - 55 edges
8. `api` - 54 edges
9. `Prefix` - 53 edges
10. `Base` - 46 edges

## Surprising Connections (you probably didn't know these)
- `LanInfo` --calls--> `_lan_info()`  [EXTRACTED]
  frontend/src/types/index.ts → backend/app/api/v1/settings.py
- `SettingsOut` --calls--> `_build_out()`  [EXTRACTED]
  frontend/src/types/index.ts → backend/app/api/v1/settings.py
- `IpDrawer()` --calls--> `fmtTs()`  [EXTRACTED]
  components/ip-drawer.tsx → lib/prefs.ts
- `AppShell()` --calls--> `usePrefs()`  [EXTRACTED]
  components/app-shell.tsx → lib/prefs.ts
- `scanner service` --mounts--> `backupdata Volume`  [EXTRACTED]
  /home/simonj/Documents/github/IpamBox/docker-compose.yml → docker-compose.yml

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **async FastAPI + SQLAlchemy + Postgres API stack** — requirements_fastapi, requirements_uvicorn, requirements_sqlalchemy, requirements_asyncpg, requirements_pydantic [INFERRED 0.85]
- **Compose-level XFF trust chain (pinned bridge IP + trusted-proxies env + uvicorn flags)** — docker_compose_trusted_proxies, docker_compose_uvicorn_proxy_flags, docker_compose_web_service, docker_compose_ipam_network [EXTRACTED 1.00]
- **Loopback data plane (DB/Redis published on 127.0.0.1, reachable by host-networked scanner)** — docker_compose_db_service, docker_compose_redis_service, docker_compose_loopback_binding, docker_compose_scanner_service, docker_compose_scanner_host_mode [EXTRACTED 1.00]
- **Scan-size guard shared between API validation and worker** — docker_compose_api_service, docker_compose_scanner_service, docker_compose_scan_max_hosts [EXTRACTED 1.00]

## Communities (192 total, 70 thin omitted)

### Community 0 - "Client Pages & Forms"
Cohesion: 0.05
Nodes (89): CertificatesPage(), EMPTY, CircuitsPage(), EMPTY, AssetRow, EMPTY, InventoryPage(), metadata (+81 more)

### Community 1 - "Discovery & Import UI"
Cohesion: 0.04
Nodes (69): BulkResp, ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp (+61 more)

### Community 2 - "Prefix Detail & IP Grid"
Cohesion: 0.06
Nodes (65): IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, SplitPlan, toggleIn(), AddressList(), AddrMapViewSwitcher() (+57 more)

### Community 3 - "Frontend Pages"
Cohesion: 0.09
Nodes (52): EMPTY, EMPTY, AssetRow, EMPTY, PrefixesPage(), PrefixRow, utilColor(), EMPTY (+44 more)

### Community 4 - "Address API"
Cohesion: 0.06
Nodes (59): _address_csv_row(), _addresses_stmt(), bulk_addresses(), BulkBody, create_address(), export_addresses(), get_address(), import_addresses() (+51 more)

### Community 5 - "Core & Changelog"
Cohesion: 0.09
Nodes (38): Audit trail via session flush hooks. before_flush collects (object, action,…, healthz(), metrics(), get, Readiness probe: verifies DB + Redis connectivity., Prometheus-style text exposition of object + scan counters., readyz(), AppSetting (+30 more)

### Community 6 - "Import Wizard"
Cohesion: 0.06
Nodes (42): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, Step (+34 more)

### Community 7 - "App Shell & Nav"
Cohesion: 0.05
Nodes (41): AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS, NavGroup, NavItem, NavLink() (+33 more)

### Community 8 - "Prefix API"
Cohesion: 0.10
Nodes (44): allocate_next_available(), create_prefix(), export_prefixes(), get_prefix(), list_prefixes(), _prefix_rows(), prefix_tree(), AsyncSession (+36 more)

### Community 9 - "IP Normalization"
Cohesion: 0.08
Nodes (41): assemble_ip(), clean(), _clean_octets(), map_status(), mask_to_prefixlen(), network_of(), norm_header(), norm_mac() (+33 more)

### Community 10 - "Master Planner"
Cohesion: 0.10
Nodes (15): parse_sites_master_records(), _Planner, _preview(), (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Folded sheet title vs site name/code — word-boundary matching so 'int' doesn't…, Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new… (+7 more)

### Community 11 - "DB Migrations"
Cohesion: 0.08
Nodes (36): do_run_migrations(), run_migrations_online(), get_settings(), close_arq_pool(), close_redis(), get_redis(), Shared process-wide Redis client. Do NOT aclose() it per call — connections…, Shut down the shared client — lifespan/worker shutdown only. (+28 more)

### Community 12 - "Import Service"
Cohesion: 0.10
Nodes (39): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+31 more)

### Community 13 - "Dependencies"
Cohesion: 0.05
Nodes (41): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, lucide-react, next, @radix-ui/react-dialog (+33 more)

### Community 14 - "CRUD Router"
Cohesion: 0.09
Nodes (40): delete_address(), delete, update_address(), _crud_router(), create_item(), delete_item(), get_item(), list_items() (+32 more)

### Community 15 - "Backup & Sweep"
Cohesion: 0.08
Nodes (40): Delete assignments whose target no longer exists. For non-ORM write paths…, sweep_orphans(), _alembic_revisions(), backup_dir(), backup_filename(), BackupError, BackupPreview, BackupTable (+32 more)

### Community 16 - "Scan Reconcile"
Cohesion: 0.09
Nodes (31): AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), HostResult, _api_cancel(), _FakeRedis, _mk_job(), A stored (e.g. imported) MAC that differs from the scan is flagged in… (+23 more)

### Community 17 - "Redis & LAN"
Cohesion: 0.08
Nodes (36): ArqRedis, _lan_info(), LAN identity detected by the host-networked worker (written to Redis). Falls…, get_arq_pool(), Shared ARQ pool — callers must not close() it per job., redis_settings_from_url(), set_actor(), get_effective() (+28 more)

### Community 18 - "Exclusions & Inference"
Cohesion: 0.09
Nodes (30): _check_cidr_allowed(), exclusion_hit(), Return the first excluded CIDR overlapping ``net`` (either direction), or None.…, infer_device_type(), Best-effort device classification; None when nothing matched., _infer_scan_vrf(), Pick the VRF for a scan that didn't specify one. An exact-match prefix living…, _scan_vrf() (+22 more)

### Community 20 - "Auth API"
Cohesion: 0.17
Nodes (34): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+26 more)

### Community 21 - "Color Rules API"
Cohesion: 0.11
Nodes (29): create_rule(), delete_rule(), get_rule(), list_rules(), preview_rule(), AsyncSession, delete, get (+21 more)

### Community 22 - "Setup & Discovery UI"
Cohesion: 0.13
Nodes (20): BulkResp, metadata, PrintClient(), FEATURES, FeaturesPage(), Key, Key, ScanningPage() (+12 more)

### Community 23 - "Settings Module"
Cohesion: 0.08
Nodes (12): EMPTY, EMPTY, ACTION_STYLES, BulkResp, fmtEta(), ScansPage(), EMPTY, ServiceRow (+4 more)

### Community 24 - "Dialogs"
Cohesion: 0.14
Nodes (21): QuickScanDialog(), usePrefixScanOverlay(), useScanStream(), v4NetBounds(), TAG_COLORS, Button, ButtonProps, buttonVariants (+13 more)

### Community 25 - "Docs UI"
Cohesion: 0.11
Nodes (24): DocsIndexClient(), metadata, DocPage(), dynamicParams, generateMetadata(), loadMarkdown(), CommandPalette(), Icon (+16 more)

### Community 26 - "Sites API"
Cohesion: 0.13
Nodes (25): _cascade_site_fields(), Propagate site code/number/name changes to linked entities that were following…, Base, Site, Base, VRF, BaseModel, SiteCreate (+17 more)

### Community 27 - "Backup API"
Cohesion: 0.12
Nodes (29): delete_scheduled_backup(), download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, delete, get, post (+21 more)

### Community 28 - "Scans API"
Cohesion: 0.12
Nodes (30): cancel_scan(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession, get, post (+22 more)

### Community 29 - "Backup Tests"
Cohesion: 0.16
Nodes (32): _backup_bytes(), _envelope_bytes(), _mkusers(), Hand-craft a backup envelope (e.g. with a forged users table)., Guard: every ORM table must be backed up (or explicitly excluded). Adding a new…, Fresh-server scenario: the migration-seeded Global VRF is replaced by the…, Fresh-server scenario: the target's admins survive; its non-admin set is fully…, A backup carrying an assignment for a missing object (e.g. taken while orphans… (+24 more)

### Community 30 - "Api Module"
Cohesion: 0.14
Nodes (30): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+22 more)

### Community 31 - "Status Module"
Cohesion: 0.11
Nodes (21): fmtEta(), ScansPage(), ACTION_STYLES, ACTION_STYLES, expiryBadge(), IpStatusBadge(), prefixVariant, ScanStatusBadge() (+13 more)

### Community 32 - "Schemas Module"
Cohesion: 0.11
Nodes (24): _check_range_overlap(), create_range(), delete_range(), list_ranges(), AsyncSession, delete, get, post (+16 more)

### Community 33 - "Api Module"
Cohesion: 0.14
Nodes (22): AssignBody, assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession (+14 more)

### Community 34 - "Core Module"
Cohesion: 0.12
Nodes (26): clear_login_failures(), client_ip(), destroy_session(), destroy_session_by_suffix(), _fails_key(), get_session_user_id(), _in_trusted(), _ip_fails_key() (+18 more)

### Community 35 - "Services Module"
Cohesion: 0.10
Nodes (18): Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, excel_date(), date, datetime/date passthrough; int/float serial (20000-80000) -> date; 'd/m/yy'…, parse_assets(), parse_certificates(), Positional 5-col layout: platform, target/VS, server, cert, expiry., 003 תוכנות וחומרות: סוג,חברה,דגם,שם התוכנה,ייעוד,גירסה,EOL,… (+10 more)

### Community 36 - "Services Module"
Cohesion: 0.11
Nodes (17): psycopg2-style URL for alembic offline mode / scripts., Settings, Effective, _env_sourced(), Any, Runtime-editable settings: app_settings rows override env defaults. Each public…, True when the field's current value differs from its declared default., One runtime-editable setting. field: the env-backed attribute on… (+9 more)

### Community 37 - "Schemas Module"
Cohesion: 0.12
Nodes (14): field_validator, CircuitCreate, CircuitOut, CircuitUpdate, BaseModel, field_validator, hex_color_or_none(), ip_display() (+6 more)

### Community 38 - "Tests Module"
Cohesion: 0.21
Nodes (13): _master_row(), _matrix(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind… (+5 more)

### Community 39 - "Schemas Module"
Cohesion: 0.16
Nodes (21): _build_out(), _mask_url(), AsyncSession, get, Hide the password in a scheme://user:pass@host URL., read_settings(), update_settings(), ChangePasswordBody (+13 more)

### Community 40 - "Api Module"
Cohesion: 0.18
Nodes (22): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+14 more)

### Community 41 - "Tests Module"
Cohesion: 0.34
Nodes (22): str, UserRole, login(), mkuser(), other_client(), AsyncClient, AsyncSession, allow_insecure keeps full access (existing behavior preserved). (+14 more)

### Community 42 - "Package Module"
Cohesion: 0.09
Nodes (22): name, private, version, autoprefixer, clsx, postcss, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+14 more)

### Community 43 - "Package Module"
Cohesion: 0.09
Nodes (23): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, lucide-react, next, @radix-ui/react-dialog (+15 more)

### Community 44 - "Prefix Module"
Cohesion: 0.20
Nodes (18): metadata, ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), collectExpandableKeys(), flattenTree() (+10 more)

### Community 45 - "Schemas Module"
Cohesion: 0.24
Nodes (19): _folded(), AsyncSession, get, search(), match(), BaseModel, SearchAddress, SearchAsset (+11 more)

### Community 46 - "Services Module"
Cohesion: 0.19
Nodes (20): prefix_stats_dict(), Stats payload for one prefix given its address count (no DB access). IPv6…, children(), lowest_free(), parent_chain(), Inclusive [first, last] integer range of host-usable addresses., True when network/broadcast addresses are unusable for hosts (IPv4 <= /30)., Lowest usable address integer not in `taken` or any excluded range. (+12 more)

### Community 47 - "Worker Module"
Cohesion: 0.14
Nodes (17): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), _host_chunks(), _icmp_sweep(), _ptr_lookup(), Blocking scapy ARP sweep -> {ip: mac}. Runs in a thread. (+9 more)

### Community 48 - "Api Module"
Cohesion: 0.16
Nodes (18): create_vrf(), delete_vrf(), get_vrf(), list_vrfs(), AsyncSession, delete, get, post (+10 more)

### Community 49 - "Services Module"
Cohesion: 0.12
Nodes (12): _as_date(), _as_str(), display_color_for(), _ordered_cmp(), Any, date, -1/0/1 comparing a column value to a rule's value string. Tries date first when…, Does ``rule`` fire on this row? NULL fields never match. (+4 more)

### Community 50 - "Tests Module"
Cohesion: 0.27
Nodes (19): _login(), _mk_rule(), _mk_site(), _mkuser(), AsyncClient, AsyncSession, Global row colors: manual row_color + rule-computed display_color. Covers the…, test_backup_roundtrips_color_rules() (+11 more)

### Community 51 - "Shell Module"
Cohesion: 0.13
Nodes (15): AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS, NavGroup, NavItem, NavLink() (+7 more)

### Community 52 - "Api Module"
Cohesion: 0.15
Nodes (12): list_changelog(), AsyncSession, get, AsyncSession, get, stats(), get_session(), AsyncSession (+4 more)

### Community 53 - "Tests Module"
Cohesion: 0.28
Nodes (18): _circuit_order(), _login(), _mk_circuits(), _mkuser(), AsyncClient, AsyncSession, Global row ordering: POST /{entity}/reorder + pinned rows. Covered on both…, Reordering a subset keeps the slots those rows already had — rows outside the… (+10 more)

### Community 54 - "Content Module"
Cohesion: 0.18
Nodes (19): Accounts & Roles, IP Addresses, Certificates, Changelog, Circuits, Discovery Inbox, Hierarchy Tree, Import (+11 more)

### Community 55 - "Tsconfig Module"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 56 - "Tests Module"
Cohesion: 0.22
Nodes (17): _prefix(), export.csv takes the same filters as the list endpoint — a filtered view…, Same filtered-export treatment on the prefixes CSV (F8)., A documented v6 /64's 2^64 host count must not reach dashboard sums (~1.8e19 >…, test_address_role_nat_and_bulk(), test_addresses_export_respects_filters(), test_bulk_reports_real_counts(), test_container_move_with_children_rejected() (+9 more)

### Community 57 - "Home Module"
Cohesion: 0.19
Nodes (18): alembic upgrade head on api start, API_BIND publish binding, api service, backupdata volume, backupdata Volume, IPAMBOX_COOKIE_SECURE env, db service (postgres:16-alpine), ipam bridge network 192.0.2.0/24 (+10 more)

### Community 58 - "Tests Module"
Cohesion: 0.17
Nodes (8): _blocks(), parse_site_sheet(), Split duplicated column groups (031-style runaway): each block starts at an…, MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf., Bare 'Name' (Cellular) maps to the hostname field., Non-empty unnamed columns pile into cf['extra'] instead of vanishing (Pelephone…, TestSiteSheetExtras, TestSiteSheetParser

### Community 59 - "Schemas Module"
Cohesion: 0.23
Nodes (12): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, AssetKind, str, AssetCreate, AssetOut, AssetUpdate, BaseModel, BaseModel (+4 more)

### Community 60 - "Api Module"
Cohesion: 0.24
Nodes (15): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+7 more)

### Community 61 - "Services Module"
Cohesion: 0.21
Nodes (13): commit_batch(), execute_plan(), _get_or_create_prefix(), _get_or_create_site(), _get_or_create_vlan(), _get_or_create_vrf(), _group_by_sheet(), _insert_address() (+5 more)

### Community 62 - "Tests Module"
Cohesion: 0.19
Nodes (13): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_files_report_effective_schedule(), test_internal_keys_hidden() (+5 more)

### Community 63 - "Import Module"
Cohesion: 0.13
Nodes (10): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, Step (+2 more)

### Community 64 - "Settings Module"
Cohesion: 0.15
Nodes (11): ColorRulesPage(), Draft, ENTITIES, OP_LABEL, OPS_BY_TYPE, opsFor(), RuleDialog(), metadata (+3 more)

### Community 65 - "Models Module"
Cohesion: 0.21
Nodes (12): after_flush(), before_flush(), SyncSession, tag_assignments garbage collection. TagAssignment references its target…, register(), ChangeLog, Base, NetBox-style audit trail: who changed what, when, and the field diff. (+4 more)

### Community 66 - "Tests Module"
Cohesion: 0.19
Nodes (8): _master_blocks(), parse_sites_master(), (first, second) octet pairs a master row declares — lets sheet->site matching…, Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins., TestSitesMasterParser

### Community 67 - "Worker Module"
Cohesion: 0.19
Nodes (14): Exception, Raised inside the pipeline when the user cancels the scan., ScanCancelled, _job_status(), _publish(), Prefix, Re-read the job row's status — the session's `job` instance goes stale the…, ARQ job: execute a scan and reconcile results. (+6 more)

### Community 68 - "Tests Module"
Cohesion: 0.26
Nodes (12): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., session() (+4 more)

### Community 69 - "Tests Module"
Cohesion: 0.24
Nodes (6): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, TestClassify

### Community 70 - "Tests Module"
Cohesion: 0.23
Nodes (12): AsyncClient, tag_assignments.object_id has no FK — deleting a tagged object must drop its…, Tag.assignments is already ORM delete-orphan — each removed assignment lands in…, PATCH settings with a null value deletes the app_settings row — that delete…, /addresses/bulk action=delete used to issue one Core DELETE — invisible to the…, test_bulk_delete_writes_changelog_entries(), test_changelog_captures_ip_status_change(), test_changelog_records_crud() (+4 more)

### Community 71 - "Tests Module"
Cohesion: 0.22
Nodes (10): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_now_enqueues(), test_clear_discovery() (+2 more)

### Community 72 - "Tests Module"
Cohesion: 0.29
Nodes (11): AsyncClient, When the socket peer isn't in ipambox_trusted_proxies, a supplied XFF is…, Spreading failures across many usernames from one IP trips the aggregate lock —…, Five bad logins for one (user, ip) pair must not lock out other users on the…, test_endpoints_require_auth(), test_lockout_keyed_per_user_ip_pair(), test_login_lockout(), test_per_ip_aggregate_backstop() (+3 more)

### Community 73 - "Tests Module"
Cohesion: 0.21
Nodes (8): on_hosts fires once per detection step with that chunk's new IPs — ARP batch…, When L2+L3 find nothing, the TCP fallback publishes its batch too., test_scan_cidr_emits_found_deltas(), fake_icmp(), fake_probe(), fake_ptr(), on_hosts(), test_scan_cidr_tcp_fallback_reports_found()

### Community 74 - "Schemas Module"
Cohesion: 0.27
Nodes (8): CertificateCreate, CertificateOut, CertificateUpdate, BaseModel, field_validator, DashboardStats, MacMismatchItem, BaseModel

### Community 75 - "Core Module"
Cohesion: 0.29
Nodes (10): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), SyncSession, register(), _repr() (+2 more)

### Community 76 - "Tests Module"
Cohesion: 0.38
Nodes (9): _global_vrf_id(), test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_prefixes_order_by_utilization_and_limit(), test_same_cidr_allowed_across_vrfs(), test_split_cardinality_cap(), test_split_endpoint(), test_tree_endpoint() (+1 more)

### Community 77 - "Tests Module"
Cohesion: 0.47
Nodes (9): AsyncClient, _seed(), test_addresses_q_filter_not_broken(), test_search_empty_query(), test_search_grouped_results(), test_search_hebrew_folding(), test_search_ip_jump(), test_search_ip_jump_prefers_owner_then_deepest() (+1 more)

### Community 78 - "History Module"
Cohesion: 0.28
Nodes (8): ACTION_STYLES, ChangeDiff(), ChangeVal(), fmtChangeVal(), HistoryEntry(), HistoryPanel(), summary(), ChangeField

### Community 79 - "Prefixes Module"
Cohesion: 0.25
Nodes (6): IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, SplitPlan, toggleIn()

### Community 80 - "Settings Module"
Cohesion: 0.25
Nodes (6): Draft, ENTITIES, OP_LABEL, OPS_BY_TYPE, opsFor(), RuleDialog()

### Community 81 - "Package Module"
Cohesion: 0.25
Nodes (8): devDependencies, autoprefixer, postcss, tailwindcss, @types/node, @types/react, @types/react-dom, typescript

### Community 82 - "Services Module"
Cohesion: 0.29
Nodes (4): _col_class(), _positional_columns(), Dominant content class of a column sample., Headerless sheet: locate the IP column, then assign the remaining canonical…

### Community 83 - "Tests Module"
Cohesion: 0.52
Nodes (6): _mk_prefix(), test_address_crud_and_dup_guard(), test_allocation_skips_existing(), test_concurrent_allocation_unique(), test_exhausted_prefix_conflicts(), test_sequential_allocation_skips_boundaries()

### Community 84 - "Prefixes Module"
Cohesion: 0.33
Nodes (3): PrefixesPage(), PrefixRow, utilColor()

### Community 86 - "Inventory Module"
Cohesion: 0.33
Nodes (3): nextConfig, metadata, next

### Community 87 - "Tree Module"
Cohesion: 0.53
Nodes (5): ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText()

### Community 89 - "Tests Module"
Cohesion: 0.40
Nodes (3): קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., TestCircuitsParser

### Community 90 - "Package Module"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 92 - "Use Module"
Cohesion: 0.50
Nodes (4): ChartTheme, FALLBACK, readTheme(), useChartTheme()

### Community 93 - "Status Module"
Cohesion: 0.40
Nodes (4): GRID_CELL_TOKENS, STATUS_TOKENS, StatusBadgeVariant, StatusTokenSet

### Community 94 - "Security Module"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 97 - "Requirements Module"
Cohesion: 0.50
Nodes (4): fastapi 0.115.6, pydantic 2.10.3, pydantic-settings 2.6.1, uvicorn[standard] 0.32.1

### Community 103 - "Home Module"
Cohesion: 0.50
Nodes (4): fastapi 0.115.6, pydantic 2.10.3, pydantic-settings 2.6.1, uvicorn[standard] 0.32.1

### Community 106 - "Settings Module"
Cohesion: 0.83
Nodes (3): BackupSettingsPage(), downloadUrl(), fmtSize()

### Community 125 - "Requirements Module"
Cohesion: 0.67
Nodes (3): alembic 1.14.0, asyncpg 0.30.0, sqlalchemy[asyncio] 2.0.36

### Community 148 - "Home Module"
Cohesion: 0.67
Nodes (3): alembic 1.14.0, asyncpg 0.30.0, sqlalchemy[asyncio] 2.0.36

## Knowledge Gaps
- **378 isolated node(s):** `Row`, `SortKey`, `SwitchProps`, `RowNavApi`, `AssetRow` (+373 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1034 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **70 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_lan_info()` connect `Redis & LAN` to `DB Migrations`, `Scans API`, `Schemas Module`?**
  _High betweenness centrality (0.184) - this node is a cross-community bridge._
- **Why does `LanInfo` connect `Redis & LAN` to `Discovery & Import UI`?**
  _High betweenness centrality (0.181) - this node is a cross-community bridge._
- **Why does `_build_out()` connect `Schemas Module` to `Redis & LAN`, `DB Migrations`, `Setup & Discovery UI`, `Backup & Sweep`?**
  _High betweenness centrality (0.174) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `User` (e.g. with `bulk_addresses()` and `change_password()`) actually correct?**
  _`User` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 42 inferred relationships involving `IPAMError` (e.g. with `create_address()` and `delete_address()`) actually correct?**
  _`IPAMError` has 42 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `IPAddress` (e.g. with `_address_csv_row()` and `_addresses_stmt()`) actually correct?**
  _`IPAddress` has 19 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Row`, `SortKey`, `SwitchProps` to the rest of the system?**
  _378 weakly-connected nodes found - possible documentation gaps or missing edges._