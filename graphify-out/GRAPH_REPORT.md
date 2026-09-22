# Graph Report - IpamBox  (2026-09-23)

## Corpus Check
- 346 files · ~291,920 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: (none) 7, .csv 6, .ini 2)

## Summary
- 3104 nodes · 8091 edges · 201 communities (100 shown, 73 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 514 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Frontend Entity Pages
- App Shell & Layout
- Frontend Client Pages
- Auth & Setup UI
- Backup Tests
- Addresses API
- Auth API
- Sites API & Cascade
- CRUD Router Factory
- Test Fixtures & Rack Tests
- Backup API
- Entity CRUD & Asset Model
- Shared Types & Rack Schemas
- Migrations & Config
- Workbook Normalize
- Lists API
- Docs & Concepts
- Prefixes API
- App Config & Redis
- Demo Data Generator
- Community 20
- Community 21
- Racks API
- Community 23
- Community 24
- Community 25
- Rackula Interop
- Community 27
- Community 28
- Community 29
- Community 30
- Community 31
- Community 32
- Community 33
- Community 34
- Community 35
- Community 36
- Community 37
- Community 38
- Community 39
- Community 40
- Community 41
- Community 42
- Community 43
- Community 44
- Community 45
- Search Schema
- Community 47
- Community 48
- Community 49
- Community 50
- Community 51
- Community 52
- Community 53
- Community 54
- Community 55
- Community 56
- Community 57
- Community 58
- Community 59
- Community 60
- Rack Detail Page
- Community 62
- Community 63
- Community 64
- Community 65
- Community 66
- Community 67
- Community 68
- Rack Models
- Community 70
- Community 71
- Community 72
- Racks List Page
- Community 74
- Community 75
- Community 76
- Community 77
- Community 78
- Community 79
- Community 80
- Community 81
- Community 82
- Community 83
- Community 84
- Community 85
- Community 86
- Community 87
- Community 88
- Community 89
- Community 90
- Community 91
- Community 92
- Community 93
- Rack Docs
- Community 95
- Community 96
- Community 97
- Community 98
- Community 99
- Community 100
- Community 101
- Community 102
- Community 104
- Community 105
- Community 106
- Community 107
- Community 108
- Community 109
- Community 110
- Community 111
- Community 132
- Community 133
- Community 134
- Community 135
- Community 136
- Community 137
- Community 138
- Community 139
- Community 140
- Community 141
- Community 142
- Community 143
- Community 144
- Community 145
- Community 146
- Community 147
- Community 148
- Community 149
- Community 150
- Community 151
- Community 152
- Rackula Env Config
- Community 154
- Community 156
- Community 157
- Community 158
- Community 160
- Community 161
- Community 162
- Community 163
- Community 165
- Community 166
- Community 168
- Community 169
- Community 171
- Community 172
- Community 173
- Community 174
- Community 175
- Community 176
- Community 177
- Community 178
- Community 180
- Community 181
- Community 182
- Community 183
- Community 184
- Community 185
- Community 186
- Community 187
- Community 189
- Community 190
- Community 191
- Community 192
- Community 193
- Community 194
- Community 195
- Community 196
- Community 197
- Community 198
- Community 199
- Community 200

## God Nodes (most connected - your core abstractions)
1. `cn()` - 109 edges
2. `react` - 90 edges
3. `User` - 56 edges
4. `IPAMError` - 55 edges
5. `get_or_404()` - 50 edges
6. `lucide-react` - 49 edges
7. `IPAddress` - 48 edges
8. `api` - 46 edges
9. `get_settings()` - 45 edges
10. `UserRole` - 41 edges

## Surprising Connections (you probably didn't know these)
- `ImportBatch` --calls--> `upload_workbook()`  [EXTRACTED]
  frontend/src/types/index.ts → backend/app/api/v1/imports.py
- `Rack Elevations (README feature bullet)` --conceptually_related_to--> `Rack Elevation Feature`  [INFERRED]
  README.md → frontend/src/content/docs/racks.md
- `Rackula base URL env passthrough` --conceptually_related_to--> `IPAMBOX_RACKULA_BASE_URL env var`  [INFERRED]
  docker-compose.yml → README.md
- `CustomList` --uses--> `_row_label()`  [INFERRED]
  backend/app/models/custom_list.py → backend/app/api/v1/search.py
- `CustomList` --uses--> `search()`  [INFERRED]
  backend/app/models/custom_list.py → backend/app/api/v1/search.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Demo dataset suite** — examples_readme_demo_workbook, examples_readme_demo_workbook_en, examples_readme_demo_site_utf8, examples_readme_demo_site_cp1255, examples_readme_demo_addresses, examples_readme_demo_contacts, examples_readme_demo_vlans, examples_readme_demo_servers, examples_generate_demo_data [EXTRACTED 1.00]

## Communities (201 total, 73 thin omitted)

### Community 0 - "Frontend Entity Pages"
Cohesion: 0.05
Nodes (90): CertificatesPage(), EMPTY, CircuitsPage(), EMPTY, BulkResp, metadata, PrintClient(), fmtEta() (+82 more)

### Community 1 - "App Shell & Layout"
Cohesion: 0.04
Nodes (74): metadata, viewport, IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, SplitPlan, toggleIn() (+66 more)

### Community 2 - "Frontend Client Pages"
Cohesion: 0.08
Nodes (57): EMPTY, ACTION_STYLES, EMPTY, PrefixesPage(), PrefixRow, utilColor(), EMPTY, ServiceRow (+49 more)

### Community 3 - "Auth & Setup UI"
Cohesion: 0.05
Nodes (58): BackupSettingsPage(), downloadUrl(), fmtSize(), ACTION_STYLES, DashboardPage(), BulkResp, LoginPage(), metadata (+50 more)

### Community 4 - "Backup Tests"
Cohesion: 0.07
Nodes (75): str, UserRole, _backup_bytes(), _envelope_bytes(), _mkusers(), Hand-craft a backup envelope (e.g. with a forged users table)., Guard: every ORM table must be backed up (or explicitly excluded). Adding a new…, Fresh-server scenario: the migration-seeded Global VRF is replaced by the… (+67 more)

### Community 5 - "Addresses API"
Cohesion: 0.06
Nodes (58): _address_csv_row(), _addresses_stmt(), bulk_addresses(), BulkBody, delete_address(), export_addresses(), get_address(), import_addresses() (+50 more)

### Community 6 - "Auth API"
Cohesion: 0.09
Nodes (61): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+53 more)

### Community 7 - "Sites API & Cascade"
Cohesion: 0.07
Nodes (50): _cascade_site_fields(), create_site(), delete_site(), get_site(), list_sites(), AsyncSession, delete, get (+42 more)

### Community 8 - "CRUD Router Factory"
Cohesion: 0.09
Nodes (48): _crud_router(), delete_item(), get_item(), list_items(), reorder_items(), update_item(), _check_duplicate_vid(), create_vlan() (+40 more)

### Community 9 - "Test Fixtures & Rack Tests"
Cohesion: 0.09
Nodes (44): AsyncClient, _base_dsn(), client(), engine(), _prepare_test_db(), fixture, session(), sf() (+36 more)

### Community 10 - "Backup API"
Cohesion: 0.08
Nodes (46): delete_scheduled_backup(), download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, delete, get, post (+38 more)

### Community 11 - "Entity CRUD & Asset Model"
Cohesion: 0.08
Nodes (35): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, Asset, AssetKind, Base, str, SW/HW catalog rows (תוכנות וחומרות) and serial-number inventory…, AssetCreate, AssetOut (+27 more)

### Community 12 - "Shared Types & Rack Schemas"
Cohesion: 0.04
Nodes (48): AddressPage, BackupFileInfo, BackupFilesOut, BackupPreview, Certificate, ChangeField, ChangeLogEntry, Circuit (+40 more)

### Community 13 - "Migrations & Config"
Cohesion: 0.06
Nodes (36): do_run_migrations(), run_migrations_online(), get_settings(), psycopg2-style URL for alembic offline mode / scripts., Settings, Effective, _env_sourced(), get_effective() (+28 more)

### Community 14 - "Workbook Normalize"
Cohesion: 0.08
Nodes (41): assemble_ip(), clean(), _clean_octets(), map_status(), mask_to_prefixlen(), network_of(), norm_header(), norm_mac() (+33 more)

### Community 15 - "Lists API"
Cohesion: 0.12
Nodes (39): bulk_rows(), _check_columns(), create_list(), create_row(), delete_list(), delete_row(), get_list(), list_lists() (+31 more)

### Community 16 - "Docs & Concepts"
Cohesion: 0.14
Nodes (45): Accounts & Roles, Insecure mode (IPAMBOX_ALLOW_INSECURE), Four roles (Administrator, Operator, Contributor, Viewer), Session-cookie authentication, Address roles (vip/vrrp/hsrp/glbp/carp/secondary), Address CSV import/export, IP Addresses, IP drawer (+37 more)

### Community 17 - "Prefixes API"
Cohesion: 0.12
Nodes (38): allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), _prefix_rows() (+30 more)

### Community 18 - "App Config & Redis"
Cohesion: 0.09
Nodes (35): close_arq_pool(), close_redis(), get_redis(), Shared process-wide Redis client. Do NOT aclose() it per call — connections…, Shut down the shared client — lifespan/worker shutdown only., healthz(), lifespan(), get (+27 more)

### Community 19 - "Demo Data Generator"
Cohesion: 0.13
Nodes (40): assets_rows(), _assign_site_sheets(), _assign_site_sheets_clean(), build_en_workbook(), build_mixed_workbook(), build_sites(), certificates_rows(), circuits_rows() (+32 more)

### Community 20 - "Community 20"
Cohesion: 0.05
Nodes (41): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, lucide-react, next, @radix-ui/react-dialog (+33 more)

### Community 21 - "Community 21"
Cohesion: 0.09
Nodes (26): list_changelog(), AsyncSession, get, after_flush(), before_flush(), SyncSession, tag_assignments garbage collection. TagAssignment references its target…, Delete assignments whose target no longer exists. For non-ORM write paths… (+18 more)

### Community 22 - "Racks API"
Cohesion: 0.15
Nodes (37): _check_refs(), create_device(), create_rack(), delete_device(), delete_rack(), _device_fields(), _device_out(), _devices() (+29 more)

### Community 24 - "Community 24"
Cohesion: 0.07
Nodes (31): AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS, NavGroup, NavItem, NavLink() (+23 more)

### Community 25 - "Community 25"
Cohesion: 0.11
Nodes (31): cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession, get (+23 more)

### Community 26 - "Rackula Interop"
Cohesion: 0.10
Nodes (34): RackulaImportDialog(), STATUS_BADGE, ABBREV_TO_CATEGORY, canonicalCategory(), CATEGORY_TO_ABBREV, clip(), compareVersions(), decodeShareUrl() (+26 more)

### Community 27 - "Community 27"
Cohesion: 0.08
Nodes (12): EMPTY, EMPTY, ACTION_STYLES, BulkResp, fmtEta(), ScansPage(), EMPTY, ServiceRow (+4 more)

### Community 29 - "Community 29"
Cohesion: 0.11
Nodes (24): DocsIndexClient(), metadata, DocPage(), dynamicParams, generateMetadata(), loadMarkdown(), CommandPalette(), Icon (+16 more)

### Community 30 - "Community 30"
Cohesion: 0.13
Nodes (27): AssignBody, assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession (+19 more)

### Community 31 - "Community 31"
Cohesion: 0.13
Nodes (23): create_rule(), delete_rule(), get_rule(), list_rules(), preview_rule(), AsyncSession, delete, get (+15 more)

### Community 32 - "Community 32"
Cohesion: 0.09
Nodes (28): Scan-target policy shared by the API route, the scheduler, and the worker.…, _due(), _eta_seconds(), _job_status(), _publish(), Re-read the job row's status — the session's `job` instance goes stale the…, ARQ job: execute a scan and reconcile results., Enqueue a scan for every configured network (effective settings). Targets:… (+20 more)

### Community 33 - "Community 33"
Cohesion: 0.11
Nodes (23): _global_vrf_id(), _infer_scan_vrf(), Pick the VRF for a scan that didn't specify one. An exact-match prefix living…, _scan_vrf(), _extra_vrf(), _global_id(), _mk_prefix(), The cap is a runtime setting: lowering it to 2 rejects a /24. (+15 more)

### Community 34 - "Community 34"
Cohesion: 0.09
Nodes (23): SettingField(), SOURCE_STYLE, Switch, SwitchProps, AppearancePage(), metadata, PrefsInit(), SavedViews() (+15 more)

### Community 35 - "Community 35"
Cohesion: 0.15
Nodes (28): _alembic_revisions(), backup_dir(), backup_filename(), BackupError, BackupPreview, BackupTable, build_backup(), delete_backup_file() (+20 more)

### Community 36 - "Community 36"
Cohesion: 0.15
Nodes (24): metadata, ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), collectExpandableKeys(), flattenTree() (+16 more)

### Community 37 - "Community 37"
Cohesion: 0.12
Nodes (22): _check_range_overlap(), create_range(), delete_range(), list_ranges(), AsyncSession, delete, get, post (+14 more)

### Community 38 - "Community 38"
Cohesion: 0.13
Nodes (26): ArqRedis, _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody (+18 more)

### Community 39 - "Community 39"
Cohesion: 0.11
Nodes (23): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), _host_chunks(), _icmp_sweep(), infer_device_type(), _ptr_lookup() (+15 more)

### Community 40 - "Community 40"
Cohesion: 0.10
Nodes (21): _api_cancel(), _FakeRedis, _mk_job(), In-memory stand-in for the worker's redis client (get/set/publish)., Point the worker at the test DB (sf) and the fake redis client., Simulate the API-side cancel: terminal status on a fresh connection., Cancel flag polled between phases -> ScanCancelled -> CANCELLED, and no…, Audit race: API writes CANCELLED mid-scan while the redis flag is lost… (+13 more)

### Community 41 - "Community 41"
Cohesion: 0.07
Nodes (28): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, js-yaml, jszip, lucide-react (+20 more)

### Community 42 - "Community 42"
Cohesion: 0.09
Nodes (20): ImportBatch, Base, One uploaded workbook (or file) import run. `stats` holds the preview result:…, excel_date(), date, datetime/date passthrough; int/float serial (20000-80000) -> date; 'd/m/yy'…, parse_assets(), parse_certificates() (+12 more)

### Community 43 - "Community 43"
Cohesion: 0.11
Nodes (25): _flag(), Any, AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), A stored (e.g. imported) MAC that differs from the scan is flagged in…, Scanning a /24 under a documented /16 must not mark the other 255 subnets'…, reconcile() called with no flags (the pre-toggles signature) must do exactly… (+17 more)

### Community 44 - "Community 44"
Cohesion: 0.15
Nodes (24): _build_out(), _lan_info(), _mask_url(), AsyncSession, get, Hide the password in a scheme://user:pass@host URL., LAN identity detected by the host-networked worker (written to Redis). Falls…, read_settings() (+16 more)

### Community 45 - "Community 45"
Cohesion: 0.20
Nodes (14): _master_row(), _matrix(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind… (+6 more)

### Community 46 - "Search Schema"
Cohesion: 0.22
Nodes (21): _folded(), AsyncSession, get, _row_label(), search(), match(), BaseModel, SearchAddress (+13 more)

### Community 47 - "Community 47"
Cohesion: 0.08
Nodes (23): name, private, version, autoprefixer, clsx, postcss, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+15 more)

### Community 48 - "Community 48"
Cohesion: 0.14
Nodes (19): QuickScanDialog(), usePrefixScanOverlay(), useScanStream(), v4NetBounds(), Dialog, DialogClose, DialogContent, DialogDescription (+11 more)

### Community 49 - "Community 49"
Cohesion: 0.17
Nodes (22): create_address(), prefix_stats_dict(), Stats payload for one prefix given its address count (no DB access). IPv6…, children(), lowest_free(), parent_chain(), Inclusive [first, last] integer range of host-usable addresses., True when network/broadcast addresses are unusable for hosts (IPv4 <= /30). (+14 more)

### Community 50 - "Community 50"
Cohesion: 0.18
Nodes (21): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+13 more)

### Community 51 - "Community 51"
Cohesion: 0.11
Nodes (17): cellLabel(), CHIP_COLORS, chipColor(), COL_TYPES, ListClient(), metadata, IpDrawer(), ROLES (+9 more)

### Community 52 - "Community 52"
Cohesion: 0.18
Nodes (15): create_vrf(), delete_vrf(), get_vrf(), list_vrfs(), AsyncSession, delete, get, post (+7 more)

### Community 53 - "Community 53"
Cohesion: 0.13
Nodes (15): AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS, NavGroup, NavItem, NavLink() (+7 more)

### Community 54 - "Community 54"
Cohesion: 0.21
Nodes (18): HostResult, _prefix(), export.csv takes the same filters as the list endpoint — a filtered view…, Same filtered-export treatment on the prefixes CSV (F8)., A documented v6 /64's 2^64 host count must not reach dashboard sums (~1.8e19 >…, test_address_role_nat_and_bulk(), test_addresses_export_respects_filters(), test_bulk_reports_real_counts() (+10 more)

### Community 55 - "Community 55"
Cohesion: 0.28
Nodes (18): _circuit_order(), _login(), _mk_circuits(), _mkuser(), AsyncClient, AsyncSession, Global row ordering: POST /{entity}/reorder + pinned rows. Covered on both…, Reordering a subset keeps the slots those rows already had — rows outside the… (+10 more)

### Community 56 - "Community 56"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 57 - "Community 57"
Cohesion: 0.16
Nodes (12): AsyncSession, get, stats(), get_session(), AsyncSession, ChangeField, ChangeLogOut, BaseModel (+4 more)

### Community 58 - "Community 58"
Cohesion: 0.22
Nodes (11): ListTarget, auth_on(), _preview_of(), fixture, _servers_xlsx(), test_import_as_list_e2e(), test_manually_edited_row_wins_conflict(), test_reimport_merges_by_key() (+3 more)

### Community 59 - "Community 59"
Cohesion: 0.18
Nodes (4): _mklist(), TestBulkRows, TestListCRUD, TestRows

### Community 60 - "Community 60"
Cohesion: 0.19
Nodes (18): alembic upgrade head on api start, API_BIND publish binding, api service, backupdata volume, backupdata Volume, IPAMBOX_COOKIE_SECURE env, db service (postgres:16-alpine), ipam bridge network 192.0.2.0/24 (+10 more)

### Community 61 - "Rack Detail Page"
Cohesion: 0.18
Nodes (12): metadata, FACE_BADGE, RackDetailPage(), DeviceFormDialog(), EMPTY, FACE_BADGE, RackElevation(), textOn() (+4 more)

### Community 62 - "Community 62"
Cohesion: 0.17
Nodes (8): _blocks(), parse_site_sheet(), Split duplicated column groups (031-style runaway): each block starts at an…, MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf., Bare 'Name' (Cellular) maps to the hostname field., Non-empty unnamed columns pile into cf['extra'] instead of vanishing (Pelephone…, TestSiteSheetExtras, TestSiteSheetParser

### Community 63 - "Community 63"
Cohesion: 0.14
Nodes (11): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, Step (+3 more)

### Community 64 - "Community 64"
Cohesion: 0.22
Nodes (14): _apply_list(), execute_plan(), rep(), _get_or_create_list(), _get_or_create_prefix(), _get_or_create_site(), _get_or_create_vlan(), _get_or_create_vrf() (+6 more)

### Community 65 - "Community 65"
Cohesion: 0.23
Nodes (9): _cell_text(), extract_list_table(), _infer_type(), _ips(), _is_ip_token(), pick_key_column(), _sniff_header_row(), _matrix() (+1 more)

### Community 66 - "Community 66"
Cohesion: 0.19
Nodes (12): UploadResp, ImportListDialog(), IPAM_FAMILIES, PreviewResp, Step, UploadResp, ListsClient(), metadata (+4 more)

### Community 67 - "Community 67"
Cohesion: 0.13
Nodes (10): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, Step (+2 more)

### Community 68 - "Community 68"
Cohesion: 0.21
Nodes (7): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, TestClassify

### Community 69 - "Rack Models"
Cohesion: 0.30
Nodes (9): Base, Rack, RackDevice, RackFace, check_placement(), _faces_collide(), placement_conflicts(), PlacementBoundsError (+1 more)

### Community 70 - "Community 70"
Cohesion: 0.32
Nodes (11): _as_date(), _as_str(), count_matches(), display_color_for(), _ordered_cmp(), Any, AsyncSession, date (+3 more)

### Community 71 - "Community 71"
Cohesion: 0.19
Nodes (8): _master_blocks(), parse_sites_master(), (first, second) octet pairs a master row declares — lets sheet->site matching…, Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins., TestSitesMasterParser

### Community 72 - "Community 72"
Cohesion: 0.21
Nodes (11): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_now_enqueues(), test_clear_discovery() (+3 more)

### Community 73 - "Racks List Page"
Cohesion: 0.15
Nodes (9): AssetRow, EMPTY, metadata, EMPTY, RackRow, RacksPage(), Asset, AssetKind (+1 more)

### Community 74 - "Community 74"
Cohesion: 0.23
Nodes (12): AsyncClient, tag_assignments.object_id has no FK — deleting a tagged object must drop its…, Tag.assignments is already ORM delete-orphan — each removed assignment lands in…, PATCH settings with a null value deletes the app_settings row — that delete…, /addresses/bulk action=delete used to issue one Core DELETE — invisible to the…, test_bulk_delete_writes_changelog_entries(), test_changelog_captures_ip_status_change(), test_changelog_records_crud() (+4 more)

### Community 75 - "Community 75"
Cohesion: 0.21
Nodes (8): on_hosts fires once per detection step with that chunk's new IPs — ARP batch…, When L2+L3 find nothing, the TCP fallback publishes its batch too., test_scan_cidr_emits_found_deltas(), fake_icmp(), fake_probe(), fake_ptr(), on_hosts(), test_scan_cidr_tcp_fallback_reports_found()

### Community 76 - "Community 76"
Cohesion: 0.20
Nodes (8): ColorRulesPage(), Draft, ENTITIES, OP_LABEL, OPS_BY_TYPE, opsFor(), RuleDialog(), metadata

### Community 77 - "Community 77"
Cohesion: 0.40
Nodes (10): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), register(), _repr(), _ser() (+2 more)

### Community 78 - "Community 78"
Cohesion: 0.31
Nodes (10): ConflictError, Atomically allocate the lowest free usable IP in a prefix. SERIALIZES on the…, reserve_next_available(), _mk_prefix(), test_address_crud_and_dup_guard(), test_allocation_skips_existing(), test_concurrent_allocation_unique(), alloc() (+2 more)

### Community 79 - "Community 79"
Cohesion: 0.25
Nodes (8): key_for(), build_import_plan(), DbState, load_state(), parse_sites_master_records(), _preview(), AsyncSession, _site_key()

### Community 80 - "Community 80"
Cohesion: 0.20
Nodes (8): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture, Stands in for the arq Redis pool — never actually dispatches work., scan_exclude_networks=10.70.0.64/26 inside scan_networks=10.70.0.0/24: the…, test_scheduler_and_route_share_exclusion_guard()

### Community 82 - "Community 82"
Cohesion: 0.38
Nodes (9): _global_vrf_id(), test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_prefixes_order_by_utilization_and_limit(), test_same_cidr_allowed_across_vrfs(), test_split_cardinality_cap(), test_split_endpoint(), test_tree_endpoint() (+1 more)

### Community 83 - "Community 83"
Cohesion: 0.47
Nodes (9): AsyncClient, _seed(), test_addresses_q_filter_not_broken(), test_search_empty_query(), test_search_grouped_results(), test_search_hebrew_folding(), test_search_ip_jump(), test_search_ip_jump_prefers_owner_then_deepest() (+1 more)

### Community 84 - "Community 84"
Cohesion: 0.20
Nodes (8): Sheet, SheetClose, SheetContent, SheetDescription, SheetPortal, SheetTitle, SheetTrigger, @radix-ui/react-dialog

### Community 85 - "Community 85"
Cohesion: 0.22
Nodes (9): devDependencies, autoprefixer, postcss, tailwindcss, @types/js-yaml, @types/node, @types/react, @types/react-dom (+1 more)

### Community 86 - "Community 86"
Cohesion: 0.25
Nodes (6): IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, SplitPlan, toggleIn()

### Community 87 - "Community 87"
Cohesion: 0.25
Nodes (6): Draft, ENTITIES, OP_LABEL, OPS_BY_TYPE, opsFor(), RuleDialog()

### Community 88 - "Community 88"
Cohesion: 0.29
Nodes (4): _col_class(), _positional_columns(), Dominant content class of a column sample., Headerless sheet: locate the IP column, then assign the remaining canonical…

### Community 89 - "Community 89"
Cohesion: 0.62
Nodes (5): _csv_sheet(), load_upload(), load_workbook_bytes(), SheetMatrix, _trim()

### Community 90 - "Community 90"
Cohesion: 0.33
Nodes (3): PrefixesPage(), PrefixRow, utilColor()

### Community 91 - "Community 91"
Cohesion: 0.53
Nodes (5): ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText()

### Community 93 - "Community 93"
Cohesion: 0.33
Nodes (3): nextConfig, metadata, next

### Community 94 - "Rack Docs"
Cohesion: 0.33
Nodes (6): Inventory doc article, Custom Lists doc article, Rack Placement Rules, Rack Elevation Feature, Rackula Round-trip Workflow, Rack Elevations (README feature bullet)

### Community 95 - "Community 95"
Cohesion: 0.53
Nodes (5): moveRowNav(), G_CHORDS, isEditableTarget(), modalOpen(), useGlobalShortcuts()

### Community 96 - "Community 96"
Cohesion: 0.53
Nodes (5): ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText()

### Community 98 - "Community 98"
Cohesion: 0.40
Nodes (3): קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., TestCircuitsParser

### Community 100 - "Community 100"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 101 - "Community 101"
Cohesion: 0.40
Nodes (4): GRID_CELL_TOKENS, STATUS_TOKENS, StatusBadgeVariant, StatusTokenSet

### Community 102 - "Community 102"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 105 - "Community 105"
Cohesion: 0.50
Nodes (4): fastapi 0.115.6, pydantic 2.10.3, pydantic-settings 2.6.1, uvicorn[standard] 0.32.1

### Community 110 - "Community 110"
Cohesion: 0.83
Nodes (3): BackupSettingsPage(), downloadUrl(), fmtSize()

### Community 132 - "Community 132"
Cohesion: 0.67
Nodes (3): alembic 1.14.0, asyncpg 0.30.0, sqlalchemy[asyncio] 2.0.36

## Knowledge Gaps
- **447 isolated node(s):** `BulkResp`, `ServiceRow`, `VlanRow`, `AccessibleName`, `CheckboxBaseProps` (+442 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1115 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **73 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `upload_workbook()` connect `Community 50` to `Community 89`, `Community 66`, `Auth API`, `Community 79`?**
  _High betweenness centrality (0.350) - this node is a cross-community bridge._
- **Why does `ImportBatch` connect `Community 66` to `Community 50`, `Shared Types & Rack Schemas`, `Community 63`?**
  _High betweenness centrality (0.347) - this node is a cross-community bridge._
- **Why does `react` connect `Auth & Setup UI` to `Frontend Entity Pages`, `App Shell & Layout`, `Frontend Client Pages`, `Community 133`, `Community 134`, `Community 135`, `Community 136`, `Community 137`, `Community 138`, `Community 139`, `Community 140`, `Community 141`, `Community 142`, `Community 143`, `Community 144`, `Community 145`, `Community 146`, `Community 147`, `Community 148`, `Community 23`, `Community 34`, `Community 36`, `Community 47`, `Community 48`, `Community 84`, `Community 93`, `Community 106`, `Community 107`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `User` (e.g. with `bulk_addresses()` and `me()`) actually correct?**
  _`User` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 38 inferred relationships involving `IPAMError` (e.g. with `create_address()` and `get_address()`) actually correct?**
  _`IPAMError` has 38 INFERRED edges - model-reasoned connections that need verification._
- **What connects `BulkResp`, `ServiceRow`, `VlanRow` to the rest of the system?**
  _447 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Frontend Entity Pages` be split into smaller, more focused modules?**
  _Cohesion score 0.048795746011886146 - nodes in this community are weakly interconnected._