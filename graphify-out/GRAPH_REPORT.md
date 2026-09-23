# Graph Report - IpamBox  (2026-09-23)

## Corpus Check
- 351 files · ~294,743 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 20 file(s) not represented in the graph (top: (none) 7, .csv 6, .ini 2)

## Summary
- 3242 nodes · 8283 edges · 242 communities (112 shown, 102 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 532 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Frontend Entity Pages
- Racks API
- Frontend Client Pages
- Address Components & Print
- Auth & App Pages
- Sites & Dashboard API
- Test Infrastructure
- Entity CRUD & Asset Model
- CRUD Router & VLANs
- App Core & Settings Model
- Scans API
- Scanner & OUI
- Shared TypeScript Types
- Lists API
- App Shell & Appearance
- Docs Feature Concepts
- Migrations & Config
- Demo Data Generator
- Frontend Dependencies
- Prefix Detail UI
- Auth API
- Rack UI & Rackula Interop
- App Shell & Nav
- Addresses API
- Prefixes API
- Error Boundaries
- Community 26
- Workbook Import Planner
- Frontend Page Clients
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
- Community 46
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
- Community 61
- Community 62
- Community 63
- Community 64
- Community 65
- Community 66
- Community 67
- Community 68
- Community 69
- Community 70
- Community 71
- Community 72
- Community 73
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
- Community 94
- Community 95
- Community 96
- Community 97
- Community 98
- Community 99
- Community 100
- Community 101
- Community 102
- Community 103
- Community 104
- Community 105
- Community 106
- Community 107
- Community 108
- Community 110
- Community 111
- Community 112
- Community 113
- Community 114
- Community 115
- Community 116
- Community 117
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
- Community 153
- Community 154
- Community 155
- Community 156
- Community 157
- Community 158
- Community 159
- Community 160
- Community 161
- Community 162
- Community 163
- Community 164
- Community 166
- Community 167
- Community 168
- Community 169
- Community 170
- Community 171
- Community 172
- Community 173
- Community 174
- Community 175
- Community 176
- Community 177
- Community 179
- Community 180
- Community 181
- Community 182
- Community 184
- Community 185
- Community 187
- Community 188
- Community 190
- Community 191
- Community 192
- Community 193
- Community 194
- Community 195
- Community 196
- Community 197
- Community 199
- Community 200
- Community 201
- Community 202
- Community 203
- Community 204
- Community 205
- Community 206
- Community 207
- Community 208
- Community 210
- Community 211
- Community 212
- Community 213
- Community 214
- Community 215
- Community 216
- Community 217
- Community 218
- Community 219
- Community 220
- Community 221
- Community 222
- Community 223
- Community 224
- Community 225
- Community 226
- Community 227
- Community 228
- Community 229
- Community 230
- Community 231
- Community 232
- Community 233
- Community 234
- Community 235
- Community 236
- Community 237
- Community 238
- Community 239
- Community 240
- Community 241

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
- `create_rack()` --calls--> `Rack`  [EXTRACTED]
  backend/app/api/v1/racks.py → frontend/src/types/index.ts
- `ImportBatch` --calls--> `upload_workbook()`  [EXTRACTED]
  frontend/src/types/index.ts → backend/app/api/v1/imports.py
- `generate_demo_data.py` --references--> `Network_Address_DEMO.xlsx (clean flagship workbook)`  [EXTRACTED]
  /home/simonj/Documents/github/IpamBox/examples/README.md → examples/README.md
- `generate_demo_data.py` --references--> `Network_Address_DEMO_EN.xlsx (edge-case workbook)`  [EXTRACTED]
  /home/simonj/Documents/github/IpamBox/examples/README.md → examples/README.md
- `Rackula base URL env passthrough` --conceptually_related_to--> `IPAMBOX_RACKULA_BASE_URL env var`  [INFERRED]
  docker-compose.yml → README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **async FastAPI + SQLAlchemy + Postgres API stack** — requirements_fastapi, requirements_uvicorn, requirements_sqlalchemy, requirements_asyncpg, requirements_pydantic [INFERRED 0.85]
- **Core IPAM hierarchy: Site → VRF → Prefix → IP address** — sites_feature, vrfs_feature, subnets_feature, addresses_feature, overview_data_model [EXTRACTED 1.00]
- **Scan → reconcile → discovery inbox → address statuses** — scans_feature, scans_pipeline, discovery_feature, addresses_statuses [EXTRACTED 1.00]
- **Core IPAM hierarchy: Site → VRF → Prefix → IP address** — sites_feature, vrfs_feature, subnets_feature, addresses_feature, overview_data_model [EXTRACTED 1.00]
- **Scan → reconcile → discovery inbox → address statuses** — scans_feature, scans_pipeline, discovery_feature, addresses_statuses [EXTRACTED 1.00]
- **Rackula round-trip workflow (share URLs, .Rackula.zip, merge/replace import)** — racks_rackula, readme_rack_elevations, examples_demo_rack [EXTRACTED 1.00]

## Communities (242 total, 102 thin omitted)

### Community 0 - "Frontend Entity Pages"
Cohesion: 0.05
Nodes (100): CertificatesPage(), EMPTY, CircuitsPage(), EMPTY, BulkResp, metadata, PrintClient(), fmtEta() (+92 more)

### Community 1 - "Racks API"
Cohesion: 0.06
Nodes (74): _check_refs(), create_device(), create_rack(), delete_device(), delete_rack(), _device_fields(), _device_out(), _devices() (+66 more)

### Community 2 - "Frontend Client Pages"
Cohesion: 0.08
Nodes (53): EMPTY, ACTION_STYLES, EMPTY, BulkResp, EMPTY, ServiceRow, TagsPage(), VLAN_STATUSES (+45 more)

### Community 3 - "Address Components & Print"
Cohesion: 0.05
Nodes (67): metadata, PrintClient(), AddressFilterPanel(), STATUSES, AddressList(), AddrMapViewSwitcher(), buildRows(), IP_STATUSES (+59 more)

### Community 4 - "Auth & App Pages"
Cohesion: 0.05
Nodes (42): ChangelogPage(), metadata, ACTION_STYLES, DashboardPage(), LoginPage(), metadata, metadata, FeatureDef (+34 more)

### Community 5 - "Sites & Dashboard API"
Cohesion: 0.07
Nodes (57): AsyncSession, get, stats(), _cascade_site_fields(), create_site(), delete_site(), get_site(), list_sites() (+49 more)

### Community 6 - "Test Infrastructure"
Cohesion: 0.08
Nodes (52): AsyncClient, _base_dsn(), client(), engine(), _prepare_test_db(), fixture, session(), sf() (+44 more)

### Community 7 - "Entity CRUD & Asset Model"
Cohesion: 0.06
Nodes (40): list_changelog(), AsyncSession, get, CRUD routers for the workbook-imported entity families. Circuits, certificates,…, AssetKind, str, AssetCreate, AssetOut (+32 more)

### Community 8 - "CRUD Router & VLANs"
Cohesion: 0.09
Nodes (48): _crud_router(), delete_item(), get_item(), list_items(), reorder_items(), update_item(), _check_duplicate_vid(), create_vlan() (+40 more)

### Community 9 - "App Core & Settings Model"
Cohesion: 0.08
Nodes (28): healthz(), metrics(), get, Readiness probe: verifies DB + Redis connectivity., Prometheus-style text exposition of object + scan counters., readyz(), AppSetting, Base (+20 more)

### Community 10 - "Scans API"
Cohesion: 0.08
Nodes (42): cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession, get (+34 more)

### Community 11 - "Scanner & OUI"
Cohesion: 0.07
Nodes (41): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), _host_chunks(), HostResult, _icmp_sweep(), infer_device_type() (+33 more)

### Community 12 - "Shared TypeScript Types"
Cohesion: 0.04
Nodes (46): AddressPage, BackupFileInfo, BackupFilesOut, BackupPreview, Certificate, ChangeField, ChangeLogEntry, Circuit (+38 more)

### Community 13 - "Lists API"
Cohesion: 0.12
Nodes (39): bulk_rows(), _check_columns(), create_list(), create_row(), delete_list(), delete_row(), get_list(), list_lists() (+31 more)

### Community 14 - "App Shell & Appearance"
Cohesion: 0.07
Nodes (35): metadata, viewport, AppearancePage(), metadata, PrefsInit(), SettingField(), SOURCE_STYLE, CELL_SIZE (+27 more)

### Community 15 - "Docs Feature Concepts"
Cohesion: 0.14
Nodes (45): Accounts & Roles, Insecure mode (IPAMBOX_ALLOW_INSECURE), Four roles (Administrator, Operator, Contributor, Viewer), Session-cookie authentication, Address roles (vip/vrrp/hsrp/glbp/carp/secondary), Address CSV import/export, IP Addresses, IP drawer (+37 more)

### Community 16 - "Migrations & Config"
Cohesion: 0.07
Nodes (31): do_run_migrations(), run_migrations_online(), get_settings(), psycopg2-style URL for alembic offline mode / scripts., Settings, Effective, _env_sourced(), get_effective() (+23 more)

### Community 17 - "Demo Data Generator"
Cohesion: 0.13
Nodes (41): generate_demo_data.py, assets_rows(), _assign_site_sheets(), _assign_site_sheets_clean(), build_en_workbook(), build_mixed_workbook(), build_sites(), certificates_rows() (+33 more)

### Community 18 - "Frontend Dependencies"
Cohesion: 0.05
Nodes (41): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, lucide-react, next, @radix-ui/react-dialog (+33 more)

### Community 19 - "Prefix Detail UI"
Cohesion: 0.11
Nodes (26): IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, SplitPlan, toggleIn(), PrefixesPage(), PrefixRow (+18 more)

### Community 20 - "Auth API"
Cohesion: 0.16
Nodes (36): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+28 more)

### Community 21 - "Rack UI & Rackula Interop"
Cohesion: 0.09
Nodes (35): metadata, RackDetailPage(), RackulaImportDialog(), STATUS_BADGE, ABBREV_TO_CATEGORY, canonicalCategory(), CATEGORY_TO_ABBREV, clip() (+27 more)

### Community 22 - "App Shell & Nav"
Cohesion: 0.07
Nodes (31): AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS, NavGroup, NavItem, NavLink() (+23 more)

### Community 23 - "Addresses API"
Cohesion: 0.10
Nodes (36): _address_csv_row(), _addresses_stmt(), bulk_addresses(), BulkBody, create_address(), delete_address(), export_addresses(), get_address() (+28 more)

### Community 24 - "Prefixes API"
Cohesion: 0.15
Nodes (35): allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), _prefix_rows() (+27 more)

### Community 26 - "Community 26"
Cohesion: 0.10
Nodes (20): confirm_discovered(), ConfirmBody, list_discovered(), AsyncSession, BaseModel, get, post, Unconfirmed hosts found by scanners, pending admin review. No limit -> the full… (+12 more)

### Community 27 - "Workbook Import Planner"
Cohesion: 0.16
Nodes (3): _Planner, _site_key(), Counter

### Community 28 - "Frontend Page Clients"
Cohesion: 0.08
Nodes (12): EMPTY, EMPTY, ACTION_STYLES, BulkResp, fmtEta(), ScansPage(), EMPTY, ServiceRow (+4 more)

### Community 29 - "Community 29"
Cohesion: 0.11
Nodes (24): DocsIndexClient(), metadata, DocPage(), dynamicParams, generateMetadata(), loadMarkdown(), CommandPalette(), Icon (+16 more)

### Community 30 - "Community 30"
Cohesion: 0.13
Nodes (27): AssignBody, assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession (+19 more)

### Community 31 - "Community 31"
Cohesion: 0.12
Nodes (20): ListTarget, _cell_text(), extract_list_table(), _infer_type(), _ips(), _is_ip_token(), pick_key_column(), _sniff_header_row() (+12 more)

### Community 32 - "Community 32"
Cohesion: 0.10
Nodes (30): assemble_ip(), clean(), _clean_octets(), map_status(), mask_to_prefixlen(), network_of(), norm_mac(), parse_range_end() (+22 more)

### Community 33 - "Community 33"
Cohesion: 0.15
Nodes (32): _backup_bytes(), _envelope_bytes(), _mkusers(), Hand-craft a backup envelope (e.g. with a forged users table)., Guard: every ORM table must be backed up (or explicitly excluded). Adding a new…, Fresh-server scenario: the migration-seeded Global VRF is replaced by the…, Fresh-server scenario: the target's admins survive; its non-admin set is fully…, A backup carrying an assignment for a missing object (e.g. taken while orphans… (+24 more)

### Community 34 - "Community 34"
Cohesion: 0.10
Nodes (32): AsyncSession, Request, Guard for every API route. Returns the User, or None in allow_insecure mode., require_auth(), clear_login_failures(), client_ip(), create_session(), destroy_session() (+24 more)

### Community 35 - "Community 35"
Cohesion: 0.13
Nodes (23): create_rule(), delete_rule(), get_rule(), list_rules(), preview_rule(), AsyncSession, delete, get (+15 more)

### Community 36 - "Community 36"
Cohesion: 0.12
Nodes (30): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+22 more)

### Community 37 - "Community 37"
Cohesion: 0.09
Nodes (22): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, Step (+14 more)

### Community 38 - "Community 38"
Cohesion: 0.11
Nodes (26): ArqRedis, close_arq_pool(), close_redis(), get_arq_pool(), get_redis(), Shared process-wide Redis client. Do NOT aclose() it per call — connections…, Shut down the shared client — lifespan/worker shutdown only., Shared ARQ pool — callers must not close() it per job. (+18 more)

### Community 39 - "Community 39"
Cohesion: 0.15
Nodes (25): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+17 more)

### Community 40 - "Community 40"
Cohesion: 0.15
Nodes (28): _alembic_revisions(), backup_dir(), backup_filename(), BackupError, BackupPreview, BackupTable, build_backup(), delete_backup_file() (+20 more)

### Community 41 - "Community 41"
Cohesion: 0.15
Nodes (24): metadata, ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), collectExpandableKeys(), flattenTree() (+16 more)

### Community 42 - "Community 42"
Cohesion: 0.11
Nodes (28): _flag(), Any, AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), _mk_prefix(), A stored (e.g. imported) MAC that differs from the scan is flagged in…, Scanning a /24 under a documented /16 must not mark the other 255 subnets'… (+20 more)

### Community 43 - "Community 43"
Cohesion: 0.07
Nodes (29): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, js-yaml, jszip, lucide-react (+21 more)

### Community 44 - "Community 44"
Cohesion: 0.11
Nodes (22): _check_range_overlap(), create_range(), delete_range(), list_ranges(), AsyncSession, delete, get, post (+14 more)

### Community 45 - "Community 45"
Cohesion: 0.10
Nodes (21): _api_cancel(), _FakeRedis, _mk_job(), In-memory stand-in for the worker's redis client (get/set/publish)., Point the worker at the test DB (sf) and the fake redis client., Simulate the API-side cancel: terminal status on a fresh connection., Cancel flag polled between phases -> ScanCancelled -> CANCELLED, and no…, Audit race: API writes CANCELLED mid-scan while the redis flag is lost… (+13 more)

### Community 46 - "Community 46"
Cohesion: 0.15
Nodes (24): _build_out(), _lan_info(), _mask_url(), AsyncSession, get, Hide the password in a scheme://user:pass@host URL., LAN identity detected by the host-networked worker (written to Redis). Falls…, read_settings() (+16 more)

### Community 47 - "Community 47"
Cohesion: 0.13
Nodes (17): _global_vrf_id(), _infer_scan_vrf(), Pick the VRF for a scan that didn't specify one. An exact-match prefix living…, _scan_vrf(), _extra_vrf(), _global_id(), The cap is a runtime setting: lowering it to 2 rejects a /24., scan_infers_vrf=off: no prefix-matching — scans without an explicit VRF always… (+9 more)

### Community 48 - "Community 48"
Cohesion: 0.20
Nodes (14): _master_row(), _matrix(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind… (+6 more)

### Community 49 - "Community 49"
Cohesion: 0.22
Nodes (21): _folded(), AsyncSession, get, _row_label(), search(), match(), BaseModel, SearchAddress (+13 more)

### Community 50 - "Community 50"
Cohesion: 0.10
Nodes (19): ImportBatchStatus, str, excel_date(), date, datetime/date passthrough; int/float serial (20000-80000) -> date; 'd/m/yy'…, parse_assets(), parse_certificates(), Positional 5-col layout: platform, target/VS, server, cert, expiry. (+11 more)

### Community 51 - "Community 51"
Cohesion: 0.08
Nodes (23): name, private, version, autoprefixer, clsx, postcss, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+15 more)

### Community 52 - "Community 52"
Cohesion: 0.34
Nodes (22): str, UserRole, login(), mkuser(), other_client(), AsyncClient, AsyncSession, allow_insecure keeps full access (existing behavior preserved). (+14 more)

### Community 53 - "Community 53"
Cohesion: 0.11
Nodes (19): Scan-target policy shared by the API route, the scheduler, and the worker.…, _due(), Enqueue a scan for every configured network (effective settings). Targets:…, Write a full snapshot into BACKUP_DIR, prune old ones., Auto-purge rows past their configured retention (0 = keep forever). Mirrors the…, Runs every minute: fires scheduled scans/backups whose configured interval has…, Fail live jobs that outlived the worker's job_timeout. An OOM-killed or…, Every-minute cron: reaps live jobs that outlived job_timeout. (+11 more)

### Community 54 - "Community 54"
Cohesion: 0.19
Nodes (20): prefix_stats_dict(), Stats payload for one prefix given its address count (no DB access). IPv6…, children(), lowest_free(), parent_chain(), Inclusive [first, last] integer range of host-usable addresses., True when network/broadcast addresses are unusable for hosts (IPv4 <= /30)., Lowest usable address integer not in `taken` or any excluded range. (+12 more)

### Community 55 - "Community 55"
Cohesion: 0.11
Nodes (15): cellLabel(), CHIP_COLORS, chipColor(), COL_TYPES, ListClient(), metadata, IpDrawer(), ROLES (+7 more)

### Community 56 - "Community 56"
Cohesion: 0.18
Nodes (18): delete_scheduled_backup(), download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, delete, get, post (+10 more)

### Community 57 - "Community 57"
Cohesion: 0.13
Nodes (15): norm_header(), Header cell -> lowercase, single-spaced, for signature matching. Edge…, _col_class(), _is_header_echo(), _leftover_bits(), _map_columns(), parse_servers(), parse_services() (+7 more)

### Community 58 - "Community 58"
Cohesion: 0.27
Nodes (19): _login(), _mk_rule(), _mk_site(), _mkuser(), AsyncClient, AsyncSession, Global row colors: manual row_color + rule-computed display_color. Covers the…, test_backup_roundtrips_color_rules() (+11 more)

### Community 59 - "Community 59"
Cohesion: 0.13
Nodes (15): AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS, NavGroup, NavItem, NavLink() (+7 more)

### Community 60 - "Community 60"
Cohesion: 0.28
Nodes (18): _circuit_order(), _login(), _mk_circuits(), _mkuser(), AsyncClient, AsyncSession, Global row ordering: POST /{entity}/reorder + pinned rows. Covered on both…, Reordering a subset keeps the slots those rows already had — rows outside the… (+10 more)

### Community 61 - "Community 61"
Cohesion: 0.17
Nodes (14): FACE_BADGE, DeviceFormDialog(), EMPTY, FACE_BADGE, RackElevation(), textOn(), usedUSlots(), LibraryDevice (+6 more)

### Community 62 - "Community 62"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 63 - "Community 63"
Cohesion: 0.24
Nodes (17): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+9 more)

### Community 64 - "Community 64"
Cohesion: 0.18
Nodes (4): _mklist(), TestBulkRows, TestListCRUD, TestRows

### Community 65 - "Community 65"
Cohesion: 0.19
Nodes (18): alembic upgrade head on api start, API_BIND publish binding, api service, backupdata volume, backupdata Volume, IPAMBOX_COOKIE_SECURE env, db service (postgres:16-alpine), ipam bridge network 192.0.2.0/24 (+10 more)

### Community 66 - "Community 66"
Cohesion: 0.21
Nodes (15): _apply_list(), commit_batch(), execute_plan(), rep(), _get_or_create_list(), _get_or_create_prefix(), _get_or_create_site(), _get_or_create_vlan() (+7 more)

### Community 67 - "Community 67"
Cohesion: 0.17
Nodes (8): _blocks(), parse_site_sheet(), Split duplicated column groups (031-style runaway): each block starts at an…, MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf., Bare 'Name' (Cellular) maps to the hostname field., Non-empty unnamed columns pile into cf['extra'] instead of vanishing (Pelephone…, TestSiteSheetExtras, TestSiteSheetParser

### Community 68 - "Community 68"
Cohesion: 0.20
Nodes (10): LabelClient(), metadata, metadata, FACE_BADGE, PrintClient(), RackQrCode(), RackQrDialog(), rackUrl() (+2 more)

### Community 69 - "Community 69"
Cohesion: 0.14
Nodes (11): AssetRow, EMPTY, metadata, EMPTY, RackRow, RacksPage(), Asset, AssetKind (+3 more)

### Community 70 - "Community 70"
Cohesion: 0.13
Nodes (10): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, Step (+2 more)

### Community 71 - "Community 71"
Cohesion: 0.19
Nodes (15): IP Addresses — documented intent + observed reality, Hierarchy tree (/tree) — Site→VRF→Prefix, Tree navigation (click-to-prefix, session expand state), Data model — Site→VRF→Prefix→IP address, Next-free-U finder (lowest/highest contiguous span, face-aware), Placement & collision rules (u_position bottom-up), Manual row colors (per-row Set color), Command palette (⌘K/Ctrl+K) (+7 more)

### Community 72 - "Community 72"
Cohesion: 0.21
Nodes (7): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, TestClassify

### Community 73 - "Community 73"
Cohesion: 0.19
Nodes (8): _master_blocks(), parse_sites_master(), (first, second) octet pairs a master row declares — lets sheet->site matching…, Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins., TestSitesMasterParser

### Community 74 - "Community 74"
Cohesion: 0.17
Nodes (13): The four roles (Administrator/Operator/Contributor/Viewer), Expiry tracking (badge, certs_expiring_30d dashboard count), Certificates — expiry tracking register, Circuits — WAN circuit register, demo-rack.Rackula.zip — 42U/18-device demo rack, Rackula round-trip (share URL, .Rackula.zip, merge/replace import), 4-tier RBAC (Administrator/Operator/Contributor/Viewer), Color rules — admin-managed conditional row coloring (+5 more)

### Community 75 - "Community 75"
Cohesion: 0.19
Nodes (13): cancel_key(), _eta_seconds(), _job_status(), _publish(), Re-read the job row's status — the session's `job` instance goes stale the…, ARQ job: execute a scan and reconcile results., _resolve_prefix(), run_scan() (+5 more)

### Community 76 - "Community 76"
Cohesion: 0.23
Nodes (12): AsyncClient, tag_assignments.object_id has no FK — deleting a tagged object must drop its…, Tag.assignments is already ORM delete-orphan — each removed assignment lands in…, PATCH settings with a null value deletes the app_settings row — that delete…, /addresses/bulk action=delete used to issue one Core DELETE — invisible to the…, test_bulk_delete_writes_changelog_entries(), test_changelog_captures_ip_status_change(), test_changelog_records_crud() (+4 more)

### Community 77 - "Community 77"
Cohesion: 0.31
Nodes (12): auth_on(), AsyncClient, fixture, _seed(), test_addresses_q_filter_not_broken(), test_search_empty_query(), test_search_grouped_results(), test_search_hebrew_folding() (+4 more)

### Community 78 - "Community 78"
Cohesion: 0.20
Nodes (12): Accounts & role-based access control, Address statuses (active/reserved/dhcp/discovered/offline), Changelog coverage & retention, Confirm/delete workflow, Discovery Inbox — reconciliation queue, Going quiet — active↔offline flips, Overview — what IpamBox is, Health overlay — scan-status dots on device blocks (+4 more)

### Community 79 - "Community 79"
Cohesion: 0.29
Nodes (11): AsyncClient, When the socket peer isn't in ipambox_trusted_proxies, a supplied XFF is…, Spreading failures across many usernames from one IP trips the aggregate lock —…, Five bad logins for one (user, ip) pair must not lock out other users on the…, test_endpoints_require_auth(), test_lockout_keyed_per_user_ip_pair(), test_login_lockout(), test_per_ip_aggregate_backstop() (+3 more)

### Community 80 - "Community 80"
Cohesion: 0.18
Nodes (10): W8: no N+1 stats queries, filters run in SQL before LIMIT, the existing-address…, import_addresses used to SELECT every ip_addresses row into a set. The probe…, The old _with_stats ran one COUNT(ip_addresses) per row — N prefixes meant N+1…, ?q= used to filter in Python on an already-LIMITed page — matches past the…, The unbounded list routes now answer {items, total, limit, offset}; no limit ->…, test_addresses_q_filters_before_limit(), test_import_existing_probe_scoped_to_file_prefixes(), test_list_envelopes() (+2 more)

### Community 81 - "Community 81"
Cohesion: 0.21
Nodes (8): on_hosts fires once per detection step with that chunk's new IPs — ARP batch…, When L2+L3 find nothing, the TCP fallback publishes its batch too., test_scan_cidr_emits_found_deltas(), fake_icmp(), fake_probe(), fake_ptr(), on_hosts(), test_scan_cidr_tcp_fallback_reports_found()

### Community 82 - "Community 82"
Cohesion: 0.20
Nodes (8): ColorRulesPage(), Draft, ENTITIES, OP_LABEL, OPS_BY_TYPE, opsFor(), RuleDialog(), metadata

### Community 83 - "Community 83"
Cohesion: 0.20
Nodes (8): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture, Stands in for the arq Redis pool — never actually dispatches work., scan_exclude_networks=10.70.0.64/26 inside scan_networks=10.70.0.0/24: the…, test_scheduler_and_route_share_exclusion_guard()

### Community 84 - "Community 84"
Cohesion: 0.36
Nodes (9): Atomically allocate the lowest free usable IP in a prefix. SERIALIZES on the…, reserve_next_available(), _mk_prefix(), test_address_crud_and_dup_guard(), test_allocation_skips_existing(), test_concurrent_allocation_unique(), alloc(), test_exhausted_prefix_conflicts() (+1 more)

### Community 85 - "Community 85"
Cohesion: 0.29
Nodes (7): key_for(), build_import_plan(), DbState, load_state(), parse_sites_master_records(), _preview(), AsyncSession

### Community 86 - "Community 86"
Cohesion: 0.38
Nodes (9): _global_vrf_id(), test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_prefixes_order_by_utilization_and_limit(), test_same_cidr_allowed_across_vrfs(), test_split_cardinality_cap(), test_split_endpoint(), test_tree_endpoint() (+1 more)

### Community 87 - "Community 87"
Cohesion: 0.20
Nodes (8): Sheet, SheetClose, SheetContent, SheetDescription, SheetPortal, SheetTitle, SheetTrigger, @radix-ui/react-dialog

### Community 88 - "Community 88"
Cohesion: 0.33
Nodes (5): BaseModel, field_validator, VRFCreate, VRFOut, VRFUpdate

### Community 89 - "Community 89"
Cohesion: 0.22
Nodes (9): devDependencies, autoprefixer, postcss, tailwindcss, @types/js-yaml, @types/node, @types/react, @types/react-dom (+1 more)

### Community 90 - "Community 90"
Cohesion: 0.25
Nodes (6): IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, SplitPlan, toggleIn()

### Community 91 - "Community 91"
Cohesion: 0.25
Nodes (6): Draft, ENTITIES, OP_LABEL, OPS_BY_TYPE, opsFor(), RuleDialog()

### Community 92 - "Community 92"
Cohesion: 0.29
Nodes (7): IP drawer — per-address detail panel, Changelog — global /changelog audit log, Backup & restore (.json.gz snapshots), Row color storage & coverage, Backup & restore settings, Site list affordances (reorder, pin, inline edit, tags, row color), Tag list management & deletion semantics

### Community 93 - "Community 93"
Cohesion: 0.43
Nodes (7): build_tree(), site_node(), vrf_node(), vrf_prefix_tree(), prefix_node(), AsyncSession, Site -> VRF -> nested prefix containment tree.

### Community 94 - "Community 94"
Cohesion: 0.29
Nodes (7): Circuit fields (line type, Bezeq circuit ID, WAN IP, is_retired), Racks — physical rack elevations (/racks), Rack elevations feature (front/rear U placement, Rackula round-trip), Service fields (beneficiary, site, doc path, test info), Sites — top of the IpamBox hierarchy, VLAN fields (VID 1–4094, name, group, site, status), VRF fields (name, RD, site) + seeded Global VRF

### Community 95 - "Community 95"
Cohesion: 0.33
Nodes (3): PrefixesPage(), PrefixRow, utilColor()

### Community 96 - "Community 96"
Cohesion: 0.53
Nodes (5): ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText()

### Community 98 - "Community 98"
Cohesion: 0.33
Nodes (3): nextConfig, metadata, next

### Community 99 - "Community 99"
Cohesion: 0.33
Nodes (6): Inventory doc article, Custom Lists doc article, Rack Placement Rules, Rack Elevation Feature, Rackula Round-trip Workflow, Rack Elevations (README feature bullet)

### Community 100 - "Community 100"
Cohesion: 0.53
Nodes (5): moveRowNav(), G_CHORDS, isEditableTarget(), modalOpen(), useGlobalShortcuts()

### Community 101 - "Community 101"
Cohesion: 0.53
Nodes (5): ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText()

### Community 104 - "Community 104"
Cohesion: 0.40
Nodes (3): קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., TestCircuitsParser

### Community 106 - "Community 106"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 107 - "Community 107"
Cohesion: 0.40
Nodes (4): GRID_CELL_TOKENS, STATUS_TOKENS, StatusBadgeVariant, StatusTokenSet

### Community 108 - "Community 108"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 111 - "Community 111"
Cohesion: 0.50
Nodes (4): Bulk operations & CSV import/export, Demo CSV files (addresses, VLANs, servers, contacts, site encodings), Table & subnet-grid keyboard navigation, Prefix detail views — subnet matrix + list view + utilization

### Community 112 - "Community 112"
Cohesion: 0.50
Nodes (4): fastapi 0.115.6, pydantic 2.10.3, pydantic-settings 2.6.1, uvicorn[standard] 0.32.1

### Community 113 - "Community 113"
Cohesion: 0.50
Nodes (4): fastapi 0.115.6, pydantic 2.10.3, pydantic-settings 2.6.1, uvicorn[standard] 0.32.1

### Community 116 - "Community 116"
Cohesion: 0.83
Nodes (3): BackupSettingsPage(), downloadUrl(), fmtSize()

### Community 138 - "Community 138"
Cohesion: 0.67
Nodes (3): alembic 1.14.0, asyncpg 0.30.0, sqlalchemy[asyncio] 2.0.36

### Community 139 - "Community 139"
Cohesion: 0.67
Nodes (3): Circuit import provenance (import_batch_id), Network_Address_DEMO.xlsx — clean flagship demo workbook, IPAM feature set (hierarchy, overlap safety, allocation, CSV, workbook import)

### Community 156 - "Community 156"
Cohesion: 0.67
Nodes (3): SVG rack elevation with Front/Rear toggle, Print report — /racks/[id]/print, QR dialog & /racks/[id]/label sticker

### Community 158 - "Community 158"
Cohesion: 0.67
Nodes (3): alembic 1.14.0, asyncpg 0.30.0, sqlalchemy[asyncio] 2.0.36

## Knowledge Gaps
- **526 isolated node(s):** `BulkResp`, `ServiceRow`, `VlanRow`, `Row`, `SortKey` (+521 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1194 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **102 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RackDevice` connect `Racks API` to `Rack UI & Rackula Interop`, `Shared TypeScript Types`, `Community 61`?**
  _High betweenness centrality (0.172) - this node is a cross-community bridge._
- **Why does `update_device()` connect `Racks API` to `CRUD Router & VLANs`, `Lists API`?**
  _High betweenness centrality (0.148) - this node is a cross-community bridge._
- **Why does `upload_workbook()` connect `Community 39` to `Community 37`, `Auth API`, `Community 85`?**
  _High betweenness centrality (0.141) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `User` (e.g. with `bulk_addresses()` and `me()`) actually correct?**
  _`User` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 38 inferred relationships involving `IPAMError` (e.g. with `create_address()` and `get_address()`) actually correct?**
  _`IPAMError` has 38 INFERRED edges - model-reasoned connections that need verification._
- **What connects `BulkResp`, `ServiceRow`, `VlanRow` to the rest of the system?**
  _526 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Frontend Entity Pages` be split into smaller, more focused modules?**
  _Cohesion score 0.04652562779497764 - nodes in this community are weakly interconnected._