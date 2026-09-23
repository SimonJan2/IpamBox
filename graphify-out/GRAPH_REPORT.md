# Graph Report - IpamBox  (2026-09-23)

## Corpus Check
- 44 files · ~305,188 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3212 nodes · 8498 edges · 201 communities (89 shown, 84 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 526 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Client UI Pages
- Rack API & Devices
- Auth & Settings UI
- Runtime Settings & Worker
- Backend Test Suite
- IPAM Prefix Logic
- App Entry & Maintenance
- Docs & Deployment
- Prefix Tree UI
- Generic CRUD Router
- Auth & Security
- Table & List UI
- IP Ranges & Discovery
- IP Addresses API
- Scanner & OUI
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21
- Community 22
- Community 23
- Community 24
- Community 25
- Community 26
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
- Community 124
- Community 125
- Community 126
- Community 127
- Community 128
- Community 129
- Community 130
- Community 131
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
- Community 149
- Community 150
- Community 151
- Community 152
- Community 154
- Community 155
- Community 156
- Community 157
- Community 158
- Community 160
- Community 161
- Community 163
- Community 164
- Community 165
- Community 166
- Community 167
- Community 168
- Community 170
- Community 171
- Community 172
- Community 173
- Community 174
- Community 175
- Community 176
- Community 177
- Community 178
- Community 179
- Community 180
- Community 182
- Community 183
- Community 184
- Community 186
- Community 187
- Community 188
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
1. `cn()` - 113 edges
2. `react` - 95 edges
3. `User` - 56 edges
4. `IPAMError` - 55 edges
5. `lucide-react` - 51 edges
6. `get_or_404()` - 50 edges
7. `api` - 50 edges
8. `IPAddress` - 48 edges
9. `get_settings()` - 42 edges
10. `UserRole` - 41 edges

## Surprising Connections (you probably didn't know these)
- `api service (FastAPI/uvicorn backend)` --implements--> `Find free U (face-aware span search)`  [INFERRED]
  docker-compose.yml → frontend/src/content/docs/racks.md
- `ImportBatch` --calls--> `upload_workbook()`  [EXTRACTED]
  frontend/src/types/index.ts → backend/app/api/v1/imports.py
- `4-tier RBAC (Administrator/Operator/Contributor/Viewer)` --semantically_similar_to--> `Four roles (Administrator, Operator, Contributor, Viewer)`  [EXTRACTED] [semantically similar]
  README.md → frontend/src/content/docs/accounts-and-roles.md
- `Certificate expiry tracking` --semantically_similar_to--> `Inventory (asset register)`  [INFERRED] [semantically similar]
  frontend/src/content/docs/certificates.md → frontend/src/content/docs/inventory.md
- `api service (FastAPI/uvicorn backend)` --implements--> `Rack placement rules (u_position, face conflicts)`  [INFERRED]
  docker-compose.yml → frontend/src/content/docs/racks.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Scan → reconcile → human-review flow** — frontend_src_content_docs_scans_scans, frontend_src_content_docs_scans_scan_pipeline, frontend_src_content_docs_scans_scapy_scanner, frontend_src_content_docs_discovery_reconciliation, frontend_src_content_docs_discovery_discovery_inbox, frontend_src_content_docs_addresses_ip_addresses, frontend_src_content_docs_addresses_mac_mismatch [EXTRACTED 1.00]
- **Site → VRF → Prefix → IP address core hierarchy** — frontend_src_content_docs_sites_sites, frontend_src_content_docs_vrfs_vrfs, frontend_src_content_docs_subnets_subnets, frontend_src_content_docs_addresses_ip_addresses, frontend_src_content_docs_overview_data_model_hierarchy [EXTRACTED 1.00]
- **X-Forwarded-For trusted-proxy pinning (web pinned IP + TEST-NET subnet + api TRUSTED_PROXIES)** — docker_compose_web_service, docker_compose_ipam_network, docker_compose_api_service [EXTRACTED 1.00]
- **Live IP scan status propagation (scanner → ip_addresses → list ip column + rack health overlay)** — docker_compose_scanner_service, frontend_src_content_docs_lists_ip_addresses, frontend_src_content_docs_lists_ip_column_type, frontend_src_content_docs_racks_health_overlay [INFERRED 0.75]
- **Workbook import lifecycle (batch provenance + key-column merge + custom-list import)** — frontend_src_content_docs_inventory_import_batch_provenance, frontend_src_content_docs_lists_key_column_merge, frontend_src_content_docs_lists_custom_lists [INFERRED 0.70]

## Communities (201 total, 84 thin omitted)

### Community 0 - "Client UI Pages"
Cohesion: 0.05
Nodes (82): CertificatesPage(), EMPTY, CircuitsPage(), EMPTY, BulkResp, metadata, PrintClient(), EMPTY (+74 more)

### Community 1 - "Rack API & Devices"
Cohesion: 0.06
Nodes (83): _check_layout_change(), _check_refs(), create_device(), create_rack(), delete_device(), delete_rack(), _device_fields(), _device_out() (+75 more)

### Community 2 - "Auth & Settings UI"
Cohesion: 0.06
Nodes (50): fmtEta(), ScansPage(), BackupSettingsPage(), downloadUrl(), fmtSize(), DataPage(), download(), fmtAgo() (+42 more)

### Community 3 - "Runtime Settings & Worker"
Cohesion: 0.04
Nodes (71): ArqRedis, do_run_migrations(), run_migrations_online(), cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), list_scans() (+63 more)

### Community 4 - "Backend Test Suite"
Cohesion: 0.07
Nodes (70): AsyncClient, _base_dsn(), client(), engine(), _prepare_test_db(), fixture, session(), sf() (+62 more)

### Community 5 - "IPAM Prefix Logic"
Cohesion: 0.06
Nodes (69): allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), _prefix_rows() (+61 more)

### Community 6 - "App Entry & Maintenance"
Cohesion: 0.07
Nodes (46): _job_payload(), gen(), healthz(), metrics(), get, Readiness probe: verifies DB + Redis connectivity., Prometheus-style text exposition of object + scan counters., readyz() (+38 more)

### Community 7 - "Docs & Deployment"
Cohesion: 0.08
Nodes (69): api service (FastAPI/uvicorn backend), db service (PostgreSQL 16), ipam bridge network (192.0.2.0/24), redis service (Redis 7, appendonly), scanner service (arq worker, host networking), web service (Next.js frontend), Accounts & Roles, Insecure mode (IPAMBOX_ALLOW_INSECURE) (+61 more)

### Community 8 - "Prefix Tree UI"
Cohesion: 0.07
Nodes (47): IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, SplitPlan, toggleIn(), PrefixesPage(), PrefixRow (+39 more)

### Community 9 - "Generic CRUD Router"
Cohesion: 0.07
Nodes (57): _crud_router(), delete_item(), get_item(), list_items(), reorder_items(), update_item(), _cascade_site_fields(), create_site() (+49 more)

### Community 10 - "Auth & Security"
Cohesion: 0.09
Nodes (62): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+54 more)

### Community 11 - "Table & List UI"
Cohesion: 0.10
Nodes (40): EMPTY, EMPTY, EMPTY, ServiceRow, TagsPage(), VLAN_STATUSES, VlanRow, VrfDialog() (+32 more)

### Community 12 - "IP Ranges & Discovery"
Cohesion: 0.06
Nodes (46): list_changelog(), AsyncSession, get, AsyncSession, get, stats(), confirm_discovered(), ConfirmBody (+38 more)

### Community 13 - "IP Addresses API"
Cohesion: 0.07
Nodes (51): _address_csv_row(), _addresses_stmt(), bulk_addresses(), BulkBody, create_address(), delete_address(), export_addresses(), get_address() (+43 more)

### Community 14 - "Scanner & OUI"
Cohesion: 0.07
Nodes (44): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), Exception, Carries {key: message} so the API can return per-field 422s., SettingsValidationError, _arp_scan(), _host_chunks() (+36 more)

### Community 15 - "Community 15"
Cohesion: 0.06
Nodes (37): SettingField(), SOURCE_STYLE, metadata, viewport, AppearancePage(), metadata, PrefsInit(), SavedViews() (+29 more)

### Community 16 - "Community 16"
Cohesion: 0.04
Nodes (49): AddressPage, BackupFileInfo, BackupFilesOut, BackupPreview, Certificate, ChangeField, ChangeLogEntry, Circuit (+41 more)

### Community 17 - "Community 17"
Cohesion: 0.07
Nodes (43): assemble_ip(), clean(), _clean_octets(), map_status(), mask_to_prefixlen(), network_of(), norm_header(), norm_mac() (+35 more)

### Community 18 - "Community 18"
Cohesion: 0.08
Nodes (31): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, AssetKind, str, AssetCreate, AssetOut, AssetUpdate, BaseModel, field_validator (+23 more)

### Community 19 - "Community 19"
Cohesion: 0.13
Nodes (28): FACE_BADGE, STATUSES, QuickScanDialog(), usePrefixScanOverlay(), useScanStream(), v4NetBounds(), EMPTY, STATUS_BADGE (+20 more)

### Community 20 - "Community 20"
Cohesion: 0.06
Nodes (40): close_arq_pool(), close_redis(), get_redis(), Shared process-wide Redis client. Do NOT aclose() it per call — connections…, Shut down the shared client — lifespan/worker shutdown only., lifespan(), auth_on(), AsyncClient (+32 more)

### Community 21 - "Community 21"
Cohesion: 0.08
Nodes (39): AddressList(), AddrMapViewSwitcher(), buildRows(), IP_STATUSES, Row, sortAddr(), SortKey, InlineText() (+31 more)

### Community 22 - "Community 22"
Cohesion: 0.08
Nodes (39): metadata, RackDetailPage(), RackulaImportDialog(), Placed, LibraryDevice, RACK_LIBRARY, ABBREV_TO_CATEGORY, canonicalCategory() (+31 more)

### Community 23 - "Community 23"
Cohesion: 0.08
Nodes (40): Any, _alembic_revisions(), backup_dir(), backup_filename(), BackupError, BackupPreview, BackupTable, build_backup() (+32 more)

### Community 24 - "Community 24"
Cohesion: 0.05
Nodes (41): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, lucide-react, next, @radix-ui/react-dialog (+33 more)

### Community 25 - "Community 25"
Cohesion: 0.07
Nodes (12): EMPTY, ACTION_STYLES, EMPTY, ACTION_STYLES, BulkResp, BackupSettingsPage(), downloadUrl(), fmtSize() (+4 more)

### Community 26 - "Community 26"
Cohesion: 0.12
Nodes (35): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+27 more)

### Community 27 - "Community 27"
Cohesion: 0.12
Nodes (36): bulk_rows(), _check_columns(), create_list(), create_row(), delete_list(), delete_row(), get_list(), list_lists() (+28 more)

### Community 28 - "Community 28"
Cohesion: 0.07
Nodes (31): AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS, NavGroup, NavItem, NavLink() (+23 more)

### Community 29 - "Community 29"
Cohesion: 0.11
Nodes (31): DeviceFormDialog(), DragSession, errDetail(), Pending, RackEditor(), CarrierFrameSvg(), DeviceBlockSvg(), FACE_BADGE (+23 more)

### Community 30 - "Community 30"
Cohesion: 0.14
Nodes (36): delete_scheduled_backup(), delete, Base, User, _backup_bytes(), _envelope_bytes(), _mkusers(), Hand-craft a backup envelope (e.g. with a forged users table). (+28 more)

### Community 31 - "Community 31"
Cohesion: 0.15
Nodes (37): generate_demo_data.py, assets_rows(), _assign_site_sheets(), _assign_site_sheets_clean(), build_en_workbook(), build_mixed_workbook(), build_sites(), certificates_rows() (+29 more)

### Community 33 - "Community 33"
Cohesion: 0.08
Nodes (27): ACTION_STYLES, metadata, PrintClient(), ExpiryBadge(), ACTION_STYLES, ChangeDiff(), ChangeVal(), fmtChangeVal() (+19 more)

### Community 34 - "Community 34"
Cohesion: 0.16
Nodes (3): parse_sites_master_records(), _Planner, Counter

### Community 35 - "Community 35"
Cohesion: 0.11
Nodes (24): DocsIndexClient(), metadata, DocPage(), dynamicParams, generateMetadata(), loadMarkdown(), CommandPalette(), Icon (+16 more)

### Community 36 - "Community 36"
Cohesion: 0.11
Nodes (25): CustomList, CustomListRow, Base, _apply_list(), commit_batch(), execute_plan(), rep(), _get_or_create_list() (+17 more)

### Community 37 - "Community 37"
Cohesion: 0.12
Nodes (20): ListTarget, _cell_text(), extract_list_table(), _infer_type(), _ips(), _is_ip_token(), pick_key_column(), _sniff_header_row() (+12 more)

### Community 38 - "Community 38"
Cohesion: 0.09
Nodes (23): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, Step (+15 more)

### Community 39 - "Community 39"
Cohesion: 0.13
Nodes (23): create_rule(), delete_rule(), get_rule(), list_rules(), preview_rule(), AsyncSession, delete, get (+15 more)

### Community 40 - "Community 40"
Cohesion: 0.15
Nodes (27): AssignBody, assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession (+19 more)

### Community 41 - "Community 41"
Cohesion: 0.12
Nodes (29): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+21 more)

### Community 42 - "Community 42"
Cohesion: 0.16
Nodes (26): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+18 more)

### Community 43 - "Community 43"
Cohesion: 0.11
Nodes (29): _flag(), Any, AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), _mk_prefix(), A stored (e.g. imported) MAC that differs from the scan is flagged in…, Scanning a /24 under a documented /16 must not mark the other 255 subnets'… (+21 more)

### Community 44 - "Community 44"
Cohesion: 0.09
Nodes (22): ImportBatch, ImportBatchStatus, Base, str, One uploaded workbook (or file) import run. `stats` holds the preview result:…, excel_date(), date, datetime/date passthrough; int/float serial (20000-80000) -> date; 'd/m/yy'… (+14 more)

### Community 45 - "Community 45"
Cohesion: 0.07
Nodes (29): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, js-yaml, jszip, lucide-react (+21 more)

### Community 46 - "Community 46"
Cohesion: 0.10
Nodes (21): _api_cancel(), _FakeRedis, _mk_job(), In-memory stand-in for the worker's redis client (get/set/publish)., Point the worker at the test DB (sf) and the fake redis client., Simulate the API-side cancel: terminal status on a fresh connection., Cancel flag polled between phases -> ScanCancelled -> CANCELLED, and no…, Audit race: API writes CANCELLED mid-scan while the redis flag is lost… (+13 more)

### Community 47 - "Community 47"
Cohesion: 0.13
Nodes (17): _global_vrf_id(), _infer_scan_vrf(), Pick the VRF for a scan that didn't specify one. An exact-match prefix living…, _scan_vrf(), _extra_vrf(), _global_id(), The cap is a runtime setting: lowering it to 2 rejects a /24., scan_infers_vrf=off: no prefix-matching — scans without an explicit VRF always… (+9 more)

### Community 48 - "Community 48"
Cohesion: 0.22
Nodes (21): _folded(), AsyncSession, get, _row_label(), search(), match(), BaseModel, SearchAddress (+13 more)

### Community 49 - "Community 49"
Cohesion: 0.17
Nodes (13): _master_row(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind…, Mashapan TA + MATPASH share number 200 — merge + conflict, not a silent… (+5 more)

### Community 50 - "Community 50"
Cohesion: 0.08
Nodes (22): name, private, version, autoprefixer, clsx, postcss, @radix-ui/react-dropdown-menu, @radix-ui/react-label (+14 more)

### Community 51 - "Community 51"
Cohesion: 0.34
Nodes (22): str, UserRole, login(), mkuser(), other_client(), AsyncClient, AsyncSession, allow_insecure keeps full access (existing behavior preserved). (+14 more)

### Community 52 - "Community 52"
Cohesion: 0.11
Nodes (16): cellLabel(), CHIP_COLORS, chipColor(), COL_TYPES, ListClient(), metadata, IpDrawer(), ROLES (+8 more)

### Community 53 - "Community 53"
Cohesion: 0.17
Nodes (10): parse_site_sheet(), _matrix(), קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf., Bare 'Name' (Cellular) maps to the hostname field., Non-empty unnamed columns pile into cf['extra'] instead of vanishing (Pelephone…, TestCircuitsParser (+2 more)

### Community 54 - "Community 54"
Cohesion: 0.27
Nodes (19): _login(), _mk_rule(), _mk_site(), _mkuser(), AsyncClient, AsyncSession, Global row colors: manual row_color + rule-computed display_color. Covers the…, test_backup_roundtrips_color_rules() (+11 more)

### Community 55 - "Community 55"
Cohesion: 0.13
Nodes (15): AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS, NavGroup, NavItem, NavLink() (+7 more)

### Community 56 - "Community 56"
Cohesion: 0.16
Nodes (18): _build_out(), _mask_url(), AsyncSession, get, Hide the password in a scheme://user:pass@host URL., read_settings(), update_settings(), ChangePasswordBody (+10 more)

### Community 57 - "Community 57"
Cohesion: 0.28
Nodes (18): _circuit_order(), _login(), _mk_circuits(), _mkuser(), AsyncClient, AsyncSession, Global row ordering: POST /{entity}/reorder + pinned rows. Covered on both…, Reordering a subset keeps the slots those rows already had — rows outside the… (+10 more)

### Community 58 - "Community 58"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 59 - "Community 59"
Cohesion: 0.18
Nodes (4): _mklist(), TestBulkRows, TestListCRUD, TestRows

### Community 60 - "Community 60"
Cohesion: 0.17
Nodes (16): download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, get, post, Request, Restore a backup file (raw .json.gz body). Wipes every data table (users are… (+8 more)

### Community 61 - "Community 61"
Cohesion: 0.24
Nodes (16): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+8 more)

### Community 62 - "Community 62"
Cohesion: 0.20
Nodes (10): LabelClient(), metadata, metadata, FACE_BADGE, PrintClient(), RackQrCode(), RackQrDialog(), rackUrl() (+2 more)

### Community 63 - "Community 63"
Cohesion: 0.13
Nodes (10): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, Step (+2 more)

### Community 64 - "Community 64"
Cohesion: 0.21
Nodes (7): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, TestClassify

### Community 65 - "Community 65"
Cohesion: 0.19
Nodes (8): _master_blocks(), parse_sites_master(), (first, second) octet pairs a master row declares — lets sheet->site matching…, Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins., TestSitesMasterParser

### Community 66 - "Community 66"
Cohesion: 0.27
Nodes (13): auth_on(), auth_on(), AsyncClient, fixture, _seed(), test_addresses_q_filter_not_broken(), test_search_empty_query(), test_search_grouped_results() (+5 more)

### Community 67 - "Community 67"
Cohesion: 0.15
Nodes (9): AssetRow, EMPTY, metadata, EMPTY, RackRow, RacksPage(), Asset, AssetKind (+1 more)

### Community 68 - "Community 68"
Cohesion: 0.31
Nodes (10): _as_date(), _as_str(), count_matches(), display_color_for(), _ordered_cmp(), Any, AsyncSession, date (+2 more)

### Community 69 - "Community 69"
Cohesion: 0.23
Nodes (12): AsyncClient, tag_assignments.object_id has no FK — deleting a tagged object must drop its…, Tag.assignments is already ORM delete-orphan — each removed assignment lands in…, PATCH settings with a null value deletes the app_settings row — that delete…, /addresses/bulk action=delete used to issue one Core DELETE — invisible to the…, test_bulk_delete_writes_changelog_entries(), test_changelog_captures_ip_status_change(), test_changelog_records_crud() (+4 more)

### Community 70 - "Community 70"
Cohesion: 0.21
Nodes (8): on_hosts fires once per detection step with that chunk's new IPs — ARP batch…, When L2+L3 find nothing, the TCP fallback publishes its batch too., test_scan_cidr_emits_found_deltas(), fake_icmp(), fake_probe(), fake_ptr(), on_hosts(), test_scan_cidr_tcp_fallback_reports_found()

### Community 71 - "Community 71"
Cohesion: 0.20
Nodes (8): ColorRulesPage(), Draft, ENTITIES, OP_LABEL, OPS_BY_TYPE, opsFor(), RuleDialog(), metadata

### Community 72 - "Community 72"
Cohesion: 0.24
Nodes (11): _job_status(), _publish(), Re-read the job row's status — the session's `job` instance goes stale the…, ARQ job: execute a scan and reconcile results., _resolve_prefix(), run_scan(), _cancelled(), hosts_found() (+3 more)

### Community 73 - "Community 73"
Cohesion: 0.20
Nodes (8): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture, Stands in for the arq Redis pool — never actually dispatches work., scan_exclude_networks=10.70.0.64/26 inside scan_networks=10.70.0.0/24: the…, test_scheduler_and_route_share_exclusion_guard()

### Community 75 - "Community 75"
Cohesion: 0.38
Nodes (9): _global_vrf_id(), test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_prefixes_order_by_utilization_and_limit(), test_same_cidr_allowed_across_vrfs(), test_split_cardinality_cap(), test_split_endpoint(), test_tree_endpoint() (+1 more)

### Community 76 - "Community 76"
Cohesion: 0.20
Nodes (8): Sheet, SheetClose, SheetContent, SheetDescription, SheetPortal, SheetTitle, SheetTrigger, @radix-ui/react-dialog

### Community 77 - "Community 77"
Cohesion: 0.22
Nodes (9): devDependencies, autoprefixer, postcss, tailwindcss, @types/js-yaml, @types/node, @types/react, @types/react-dom (+1 more)

### Community 78 - "Community 78"
Cohesion: 0.25
Nodes (6): IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, SplitPlan, toggleIn()

### Community 79 - "Community 79"
Cohesion: 0.25
Nodes (6): Draft, ENTITIES, OP_LABEL, OPS_BY_TYPE, opsFor(), RuleDialog()

### Community 80 - "Community 80"
Cohesion: 0.43
Nodes (7): _mk_prefix(), test_address_crud_and_dup_guard(), test_allocation_skips_existing(), test_concurrent_allocation_unique(), alloc(), test_exhausted_prefix_conflicts(), test_sequential_allocation_skips_boundaries()

### Community 81 - "Community 81"
Cohesion: 0.29
Nodes (4): _col_class(), _positional_columns(), Dominant content class of a column sample., Headerless sheet: locate the IP column, then assign the remaining canonical…

### Community 82 - "Community 82"
Cohesion: 0.29
Nodes (7): Fail live jobs that outlived the worker's job_timeout. An OOM-killed or…, Every-minute cron: reaps live jobs that outlived job_timeout., reap_stale_scan_jobs(), scan_watchdog(), WorkerSettings, A worker killed mid-scan leaves RUNNING rows that would wedge the single-live-…, test_watchdog_reaps_stale_jobs()

### Community 83 - "Community 83"
Cohesion: 0.29
Nodes (5): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture

### Community 84 - "Community 84"
Cohesion: 0.33
Nodes (3): PrefixesPage(), PrefixRow, utilColor()

### Community 86 - "Community 86"
Cohesion: 0.33
Nodes (3): nextConfig, metadata, next

### Community 87 - "Community 87"
Cohesion: 0.53
Nodes (5): ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText()

### Community 89 - "Community 89"
Cohesion: 0.40
Nodes (5): AsyncSession, Request, Guard for every API route. Returns the User, or None in allow_insecure mode., require_auth(), set_actor()

### Community 91 - "Community 91"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 92 - "Community 92"
Cohesion: 0.40
Nodes (4): GRID_CELL_TOKENS, STATUS_TOKENS, StatusBadgeVariant, StatusTokenSet

### Community 94 - "Community 94"
Cohesion: 0.67
Nodes (3): ChangeField, ChangeLogOut, BaseModel

## Knowledge Gaps
- **444 isolated node(s):** `ChartTheme`, `PrefixRow`, `VlanRow`, `Group`, `StatusBadgeVariant` (+439 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1155 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **84 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `upload_workbook()` connect `Community 42` to `Auth & Security`, `Community 38`?**
  _High betweenness centrality (0.340) - this node is a cross-community bridge._
- **Why does `ImportBatch` connect `Community 38` to `Community 16`, `Community 42`?**
  _High betweenness centrality (0.340) - this node is a cross-community bridge._
- **Why does `react` connect `Auth & Settings UI` to `Client UI Pages`, `Community 128`, `Community 129`, `Community 130`, `Community 131`, `Community 132`, `Community 133`, `Community 134`, `Prefix Tree UI`, `Community 135`, `Community 136`, `Table & List UI`, `Community 137`, `Community 138`, `Community 139`, `Community 15`, `Community 19`, `Community 21`, `Community 29`, `Community 32`, `Community 33`, `Community 50`, `Community 76`, `Community 86`, `Community 95`, `Community 96`, `Community 97`, `Community 98`, `Community 99`, `Community 124`, `Community 125`, `Community 126`, `Community 127`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `User` (e.g. with `bulk_addresses()` and `auth_status()`) actually correct?**
  _`User` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 38 inferred relationships involving `IPAMError` (e.g. with `create_address()` and `delete_address()`) actually correct?**
  _`IPAMError` has 38 INFERRED edges - model-reasoned connections that need verification._
- **What connects `ChartTheme`, `PrefixRow`, `VlanRow` to the rest of the system?**
  _444 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Client UI Pages` be split into smaller, more focused modules?**
  _Cohesion score 0.05307346326836582 - nodes in this community are weakly interconnected._