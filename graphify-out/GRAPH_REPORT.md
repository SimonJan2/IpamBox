# Graph Report - IpamBox  (2026-09-23)

## Corpus Check
- 355 files · ~911,845 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 20 file(s) not represented in the graph (top: (none) 7, .csv 6, .ini 2)

## Summary
- 2955 nodes · 9754 edges · 181 communities (92 shown, 62 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 641 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `408c2a0a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- services/backup.py
- react
- IPAMError
- cn
- prefixes.py
- list-client.tsx
- rackula.ts
- _get_rack
- worker.py
- v1/auth.py
- IPAddress
- test_racks.py
- IpamBox
- index.ts
- addresses.py
- get_redis
- generate_demo_data.py
- useAsyncData
- ip-drawer.tsx
- command-palette.tsx
- restore_backup
- color_rules.py
- imports.py
- entities.py
- clean
- route-error.tsx
- _Planner
- User
- reconcile
- package.json
- test_scanner.py
- tree/page.tsx
- parse_site_sheet
- dependencies
- maintenance.py
- v1/search.py
- UserRole
- HostResult
- scanner.py
- _matrix
- test_workbook_import.py
- test_ordering.py
- extract_list_table
- test_colors.py
- build-rack-library.mjs
- compilerOptions
- users.py
- schemas/certificate.py
- schemas/import_batch.py
- test_ipam_extras.py
- test_settings.py
- v1/settings.py
- vlans.py
- ip_display
- import-client.tsx
- v1/racks.py
- _mklist
- classify_sheet
- test_search.py
- RackDevice
- TestSitesMasterParser
- run_scan
- Settings
- schemas/ip_range.py
- test_changelog.py
- _upload
- hex_color_or_none
- restore
- test_allocation.py
- test_scan_cidr_tcp_fallback_reports_found
- Racks
- test_prefix_api.py
- _FakePool
- runtime_settings.py
- TestNormalize
- devDependencies
- schemas/asset.py
- schemas/vrf.py
- check-rack-library.mjs
- run_scheduled_backup
- schemas/service.py
- test_auth.py
- _FakePool
- auth_on
- Demo import data — ALL FICTIONAL
- scripts
- test_entities.py
- next
- quick-scan.tsx
- use-chart-theme.ts
- get_effective
- .test_legacy_bezeq_layout
- env.py
- Security Policy
- schemas/changelog.py
- _positional_columns
- login/page.tsx
- SettingsValidationError
- setup/page.tsx
- certificates/page.tsx
- changelog/page.tsx
- circuits/page.tsx
- discovery/page.tsx
- import/page.tsx
- inventory/page.tsx
- lists/page.tsx
- lists/[slug]/page.tsx
- app/page.tsx
- prefixes/[id]/page.tsx
- prefixes/[id]/print/page.tsx
- racks/[id]/page.tsx
- prefixes/page.tsx
- label/page.tsx
- racks/[id]/print/page.tsx
- racks/page.tsx
- scans/page.tsx
- services/page.tsx
- appearance/page.tsx
- backup/page.tsx
- color-rules/page.tsx
- data/page.tsx
- settings/page.tsx
- scanning/page.tsx
- security/page.tsx
- users/page.tsx
- sites/page.tsx
- tags/page.tsx
- vlans/page.tsx
- arq==0.26.1
- asyncpg==0.30.0
- pydantic==2.10.3
- pytest==8.3.4
- next-env.d.ts
- xff-shim.js
- README.md
- alembic==1.14.0
- bcrypt==4.3.0
- fastapi==0.115.6
- httpx==0.28.1
- openpyxl==3.1.5
- psutil==6.1.0
- scapy==2.6.1
- uvicorn[standard]==0.32.1
- IpamBox App Icon (icon.svg)
- Root Layout (layout.tsx, title: IpamBox)
- ip_addresses table
- Architecture — web/api/scanner/db/redis services
- Backup & restore (.json.gz snapshots)
- IPAM feature set (hierarchy, overlap safety, allocation, CSV, workbook import)
- IpamBox — self-hosted IPAM with built-in LAN scanner
- Ops endpoints (/healthz, /readyz, /metrics, /api/v1/*)
- Rack elevations feature (front/rear U placement, Rackula round-trip)
- LAN scanner (ARP/ICMP/TCP/PTR/OUI reconciliation)
- vrfs/page.tsx

## God Nodes (most connected - your core abstractions)
1. `cn()` - 148 edges
2. `react` - 121 edges
3. `IPAMError` - 81 edges
4. `lucide-react` - 67 edges
5. `useAsyncData()` - 67 edges
6. `User` - 66 edges
7. `get_or_404()` - 66 edges
8. `IPAddress` - 63 edges
9. `useAuth()` - 57 edges
10. `Prefix` - 55 edges

## Surprising Connections (you probably didn't know these)
- `scanner service (arq worker, host networking)` --shares_data_with--> `ip column type (live IPAM resolution)`  [INFERRED]
  docker-compose.yml → frontend/src/content/docs/lists.md
- `4-tier RBAC (Administrator/Operator/Contributor/Viewer)` --semantically_similar_to--> `Four roles (Administrator, Operator, Contributor, Viewer)`  [EXTRACTED] [semantically similar]
  README.md → frontend/src/content/docs/accounts-and-roles.md
- `ip column type (live IPAM resolution)` --semantically_similar_to--> `Health overlay`  [INFERRED] [semantically similar]
  frontend/src/content/docs/lists.md → frontend/src/content/docs/racks.md
- `Certificate expiry tracking` --semantically_similar_to--> `Inventory (asset register)`  [INFERRED] [semantically similar]
  frontend/src/content/docs/certificates.md → frontend/src/content/docs/inventory.md
- `_addresses_stmt()` --uses--> `IPAddress`  [INFERRED]
  backend/app/api/v1/addresses.py → backend/app/models/ip_address.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Site → VRF → Prefix → IP address core hierarchy** — frontend_src_content_docs_sites_sites, frontend_src_content_docs_vrfs_vrfs, frontend_src_content_docs_subnets_subnets, frontend_src_content_docs_addresses_ip_addresses, frontend_src_content_docs_overview_data_model_hierarchy [EXTRACTED 1.00]
- **Scan → reconcile → human-review flow** — frontend_src_content_docs_scans_scans, frontend_src_content_docs_scans_scan_pipeline, frontend_src_content_docs_scans_scapy_scanner, frontend_src_content_docs_discovery_reconciliation, frontend_src_content_docs_discovery_discovery_inbox, frontend_src_content_docs_addresses_ip_addresses, frontend_src_content_docs_addresses_mac_mismatch [EXTRACTED 1.00]
- **X-Forwarded-For trusted-proxy pinning (web pinned IP + TEST-NET subnet + api TRUSTED_PROXIES)** — docker_compose_web_service, docker_compose_ipam_network, docker_compose_api_service [EXTRACTED 1.00]
- **Workbook import lifecycle (batch provenance + key-column merge + custom-list import)** — frontend_src_content_docs_inventory_import_batch_provenance, frontend_src_content_docs_lists_key_column_merge, frontend_src_content_docs_lists_custom_lists [INFERRED 0.70]
- **Live IP scan status propagation (scanner → ip_addresses → list ip column + rack health overlay)** — docker_compose_scanner_service, frontend_src_content_docs_lists_ip_addresses, frontend_src_content_docs_lists_ip_column_type, frontend_src_content_docs_racks_health_overlay [INFERRED 0.75]
- **Rack library bundling pipeline** — frontend_public_rack_library_attribution_netbox_devicetype_library, frontend_scripts_build_rack_library, frontend_public_rack_library_attribution_rack_device_image_library, frontend_src_content_docs_racks_device_image_library [INFERRED 0.85]

## Communities (181 total, 62 thin omitted)

### Community 0 - "services/backup.py"
Cohesion: 0.09
Nodes (44): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), SyncSession, Audit trail via session flush hooks. before_flush collects (object, action,…, register() (+36 more)

### Community 1 - "react"
Cohesion: 0.08
Nodes (77): ACTION_STYLES, ACTION_STYLES, BulkResp, ImportListDialog(), IPAM_FAMILIES, Step, LabelClient(), FACE_BADGE (+69 more)

### Community 2 - "IPAMError"
Cohesion: 0.05
Nodes (99): update_address(), _crud_router(), create_item(), delete_item(), get_item(), list_items(), reorder_items(), update_item() (+91 more)

### Community 3 - "cn"
Cohesion: 0.05
Nodes (83): IpCell(), SortableColRow(), IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, SplitDialog(), SplitPlan (+75 more)

### Community 4 - "prefixes.py"
Cohesion: 0.06
Nodes (81): allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), _prefix_rows() (+73 more)

### Community 5 - "list-client.tsx"
Cohesion: 0.10
Nodes (79): CertificatesPage(), EMPTY, CircuitsPage(), EMPTY, AssetRow, EMPTY, InventoryPage(), ListsClient() (+71 more)

### Community 6 - "rackula.ts"
Cohesion: 0.05
Nodes (74): DeviceFormDialog(), DragSession, DropRow(), EditorBlock(), errDetail(), Pending, RackEditor(), CarrierFrameSvg() (+66 more)

### Community 7 - "_get_rack"
Cohesion: 0.17
Nodes (24): _check_refs(), create_device(), create_rack(), delete_device(), delete_rack(), _device_fields(), _devices(), _get_device() (+16 more)

### Community 8 - "worker.py"
Cohesion: 0.09
Nodes (38): ArqRedis, cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession (+30 more)

### Community 9 - "v1/auth.py"
Cohesion: 0.07
Nodes (66): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+58 more)

### Community 10 - "IPAddress"
Cohesion: 0.08
Nodes (44): list_lists(), Short label for a list-row search hit: key-column value, else the first non-…, _row_label(), CustomList, CustomListRow, User-defined table — preserves a workbook sheet's own shape (e.g. 'שרתים…, One row of a custom list — ``data`` maps column key -> string value., IPAddress (+36 more)

### Community 11 - "test_racks.py"
Cohesion: 0.10
Nodes (57): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., _split_dsn() (+49 more)

### Community 12 - "IpamBox"
Cohesion: 0.09
Nodes (61): api service (FastAPI/uvicorn backend), db service (PostgreSQL 16), ipam bridge network (192.0.2.0/24), redis service (Redis 7, appendonly), scanner service (arq worker, host networking), web service (Next.js frontend), Accounts & Roles, Insecure mode (IPAMBOX_ALLOW_INSECURE) (+53 more)

### Community 13 - "index.ts"
Cohesion: 0.05
Nodes (48): AddressFilterPanel(), STATUSES, EMPTY, PrefixStatusBadge(), prefixVariant, scanVariant, TAG_COLORS, TagDialog() (+40 more)

### Community 14 - "addresses.py"
Cohesion: 0.07
Nodes (46): _address_csv_row(), _addresses_stmt(), bulk_addresses(), BulkBody, create_address(), delete_address(), export_addresses(), get_address() (+38 more)

### Community 15 - "get_redis"
Cohesion: 0.07
Nodes (34): close_arq_pool(), close_redis(), get_redis(), Shared process-wide Redis client. Do NOT aclose() it per call — connections…, Shut down the shared client — lifespan/worker shutdown only., healthz(), lifespan(), get (+26 more)

### Community 16 - "generate_demo_data.py"
Cohesion: 0.09
Nodes (49): assets_rows(), _assign_site_sheets(), _assign_site_sheets_clean(), build_en_workbook(), build_mixed_workbook(), build_sites(), certificates_rows(), circuits_rows() (+41 more)

### Community 17 - "useAsyncData"
Cohesion: 0.08
Nodes (35): ChangelogPage(), DashboardPage(), DiscoveryPage(), PrintClient(), PrintClient(), RackDetailPage(), fmtEta(), ScansPage() (+27 more)

### Community 18 - "ip-drawer.tsx"
Cohesion: 0.04
Nodes (57): metadata, viewport, AppearancePage(), AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS (+49 more)

### Community 19 - "command-palette.tsx"
Cohesion: 0.11
Nodes (25): DocsIndexClient(), metadata, DocPage(), dynamicParams, generateMetadata(), loadMarkdown(), CommandPalette(), Icon (+17 more)

### Community 20 - "restore_backup"
Cohesion: 0.16
Nodes (16): Delete assignments whose target no longer exists. For non-ORM write paths…, sweep_orphans(), BackupError, BackupPreview, _from_json(), _gunzip(), inspect_backup(), AsyncSession (+8 more)

### Community 21 - "color_rules.py"
Cohesion: 0.07
Nodes (46): create_rule(), delete_rule(), get_rule(), list_rules(), preview_rule(), AsyncSession, delete, get (+38 more)

### Community 22 - "imports.py"
Cohesion: 0.13
Nodes (26): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+18 more)

### Community 23 - "entities.py"
Cohesion: 0.06
Nodes (51): delete_scheduled_backup(), download_backup(), download_scheduled_backup(), delete, get, Download a full snapshot (every table except users) as .json.gz.…, list_changelog(), AsyncSession (+43 more)

### Community 24 - "clean"
Cohesion: 0.07
Nodes (48): _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., assemble_ip(), clean(), _clean_octets(), map_status(), mask_to_prefixlen(), network_of() (+40 more)

### Community 26 - "_Planner"
Cohesion: 0.08
Nodes (18): parse_sites_master_records(), _Planner, _preview(), (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Folded sheet title vs site name/code — word-boundary matching so 'int' doesn't…, Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new… (+10 more)

### Community 27 - "User"
Cohesion: 0.16
Nodes (33): User, _backup_bytes(), _envelope_bytes(), _mkusers(), Hand-craft a backup envelope (e.g. with a forged users table)., Guard: every ORM table must be backed up (or explicitly excluded). Adding a new…, Fresh-server scenario: the migration-seeded Global VRF is replaced by the…, Fresh-server scenario: the target's admins survive; its non-admin set is fully… (+25 more)

### Community 28 - "reconcile"
Cohesion: 0.11
Nodes (18): _flag(), Any, AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), A stored (e.g. imported) MAC that differs from the scan is flagged in…, Scanning a /24 under a documented /16 must not mark the other 255 subnets'…, reconcile() called with no flags (the pre-toggles signature) must do exactly… (+10 more)

### Community 29 - "package.json"
Cohesion: 0.07
Nodes (26): name, private, version, DocsContent(), autoprefixer, clsx, postcss, @radix-ui/react-dropdown-menu (+18 more)

### Community 30 - "test_scanner.py"
Cohesion: 0.09
Nodes (36): exclusion_hit(), Return the first excluded CIDR overlapping ``net`` (either direction), or None.…, _global_vrf_id(), _infer_scan_vrf(), Fail live jobs that outlived the worker's job_timeout. An OOM-killed or…, Pick the VRF for a scan that didn't specify one. An exact-match prefix living…, reap_stale_scan_jobs(), _scan_vrf() (+28 more)

### Community 32 - "parse_site_sheet"
Cohesion: 0.17
Nodes (8): _blocks(), parse_site_sheet(), Split duplicated column groups (031-style runaway): each block starts at an…, MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf., Bare 'Name' (Cellular) maps to the hostname field., Non-empty unnamed columns pile into cf['extra'] instead of vanishing (Pelephone…, TestSiteSheetExtras, TestSiteSheetParser

### Community 33 - "dependencies"
Cohesion: 0.07
Nodes (29): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, js-yaml, jszip, lucide-react (+21 more)

### Community 34 - "maintenance.py"
Cohesion: 0.13
Nodes (29): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+21 more)

### Community 35 - "v1/search.py"
Cohesion: 0.19
Nodes (23): _folded(), AsyncSession, get, Cross-object search for the command palette. One GET returns grouped matches…, Column expression with Hebrew final letters folded — pairs with fold_hebrew()…, search(), match(), BaseModel (+15 more)

### Community 36 - "UserRole"
Cohesion: 0.28
Nodes (24): str, UserRole, Viewer tier can read lists/rows but every mutation is 403., TestPermissions, login(), mkuser(), other_client(), AsyncClient (+16 more)

### Community 37 - "HostResult"
Cohesion: 0.13
Nodes (19): HostResult, _FakeRedis, _mk_job(), In-memory stand-in for the worker's redis client (get/set/publish)., Point the worker at the test DB (sf) and the fake redis client., Cancel flag polled between phases -> ScanCancelled -> CANCELLED, and no…, Audit race: API writes CANCELLED mid-scan while the redis flag is lost…, Cancel landing while reconcile writes rows: the flag + row re-check right… (+11 more)

### Community 38 - "scanner.py"
Cohesion: 0.12
Nodes (20): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), _host_chunks(), _icmp_sweep(), infer_device_type(), _ptr_lookup() (+12 more)

### Community 39 - "_matrix"
Cohesion: 0.21
Nodes (13): _master_row(), _matrix(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind… (+5 more)

### Community 40 - "test_workbook_import.py"
Cohesion: 0.10
Nodes (21): Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, parse_certificates(), Positional 5-col layout: platform, target/VS, server, cert, expiry., _csv_sheet(), load_upload(), load_workbook_bytes(), XLSX/CSV -> sheet matrices (openpyxl read_only streams / csv module)., Drop fully-empty trailing rows/cols for a stable matrix shape. (+13 more)

### Community 41 - "test_ordering.py"
Cohesion: 0.22
Nodes (21): auth_on(), _circuit_order(), _login(), _mk_circuits(), _mkuser(), AsyncClient, AsyncSession, fixture (+13 more)

### Community 42 - "extract_list_table"
Cohesion: 0.14
Nodes (15): _cell_text(), extract_list_table(), _infer_type(), _ips(), _is_ip_token(), SheetMatrix -> (column defs, row dicts). columns: [{key, label, type, options?,…, Raw cell -> stored string. Dates iso-format; everything else cleans., (type, extra) for one column — extra carries options/multi. (+7 more)

### Community 43 - "test_colors.py"
Cohesion: 0.27
Nodes (19): _login(), _mk_rule(), _mk_site(), _mkuser(), AsyncClient, AsyncSession, Global row colors: manual row_color + rule-computed display_color. Covers the…, test_backup_roundtrips_color_rules() (+11 more)

### Community 44 - "build-rack-library.mjs"
Cohesion: 0.13
Nodes (23): arrLen(), attribution(), CATEGORY_COLOUR, CURATED, fetchBuf(), fetchJson(), FRONTEND, FULL_IMPORT (+15 more)

### Community 45 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 46 - "users.py"
Cohesion: 0.24
Nodes (16): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+8 more)

### Community 47 - "schemas/certificate.py"
Cohesion: 0.17
Nodes (13): CertificateCreate, CertificateOut, CertificateUpdate, BaseModel, field_validator, DashboardStats, MacMismatchItem, BaseModel (+5 more)

### Community 48 - "schemas/import_batch.py"
Cohesion: 0.20
Nodes (13): CommitOptions, ImportBatchOut, ListTarget, PreviewOptions, BaseModel, Per-sheet detection result shown in the wizard., Import a sheet as a custom list (user-selected or suggested)., User-confirmed mapping choices applied before building the plan. (+5 more)

### Community 49 - "test_ipam_extras.py"
Cohesion: 0.22
Nodes (17): _prefix(), export.csv takes the same filters as the list endpoint — a filtered view…, Same filtered-export treatment on the prefixes CSV (F8)., A documented v6 /64's 2^64 host count must not reach dashboard sums (~1.8e19 >…, test_address_role_nat_and_bulk(), test_addresses_export_respects_filters(), test_bulk_reports_real_counts(), test_container_move_with_children_rejected() (+9 more)

### Community 50 - "test_settings.py"
Cohesion: 0.17
Nodes (15): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, Every new Settings > Features key is runtime-editable; untouched keys keep the…, test_backup_files_report_effective_schedule() (+7 more)

### Community 51 - "v1/settings.py"
Cohesion: 0.18
Nodes (20): _build_out(), _lan_info(), _mask_url(), AsyncSession, get, Hide the password in a scheme://user:pass@host URL., LAN identity detected by the host-networked worker (written to Redis). Falls…, read_settings() (+12 more)

### Community 52 - "vlans.py"
Cohesion: 0.19
Nodes (21): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), AsyncSession, delete (+13 more)

### Community 53 - "ip_display"
Cohesion: 0.17
Nodes (10): CircuitCreate, CircuitOut, CircuitUpdate, BaseModel, field_validator, ip_display(), Any, Normalize asyncpg-returned ipaddress objects / strings to display form. INET… (+2 more)

### Community 54 - "import-client.tsx"
Cohesion: 0.12
Nodes (18): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp, SheetResults() (+10 more)

### Community 55 - "v1/racks.py"
Cohesion: 0.22
Nodes (21): _device_out(), Rack elevations: racks + nested devices + Rackula import. Not a `_crud_router`…, str, RackFace, IpRef, LinkedRef, NextFreeUOut, BaseModel (+13 more)

### Community 56 - "_mklist"
Cohesion: 0.18
Nodes (4): _mklist(), TestBulkRows, TestListCRUD, TestRows

### Community 57 - "classify_sheet"
Cohesion: 0.31
Nodes (4): classify_sheet(), _has(), (family, header_row_index, warnings). header_row_index = index of the row…, TestClassify

### Community 58 - "test_search.py"
Cohesion: 0.25
Nodes (14): auth_on(), AsyncClient, fixture, Global /api/v1/search endpoint (UX-3)., Regression: list_addresses ?q= used to crash on a missing column., Site + VRF + prefix + address + one of each workbook entity., _seed(), test_addresses_q_filter_not_broken() (+6 more)

### Community 59 - "RackDevice"
Cohesion: 0.15
Nodes (23): _check_layout_change(), import_devices(), _inherit_carrier(), When `carrier_id` is set, derive u_position/face from the carrier — a child's…, A carrier's slot_layout can only shrink/clear when no mounted child sits in a…, Bulk-load parsed Rackula devices in one transaction. `replace` wipes existing…, RackDevice, ConflictError (+15 more)

### Community 60 - "TestSitesMasterParser"
Cohesion: 0.20
Nodes (5): Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins., TestSitesMasterParser

### Community 61 - "run_scan"
Cohesion: 0.15
Nodes (17): Exception, Raised inside the pipeline when the user cancels the scan., ScanCancelled, _due(), _eta_seconds(), _job_status(), _publish(), datetime (+9 more)

### Community 62 - "Settings"
Cohesion: 0.22
Nodes (3): psycopg2-style URL for alembic offline mode / scripts., Settings, BaseSettings

### Community 63 - "schemas/ip_range.py"
Cohesion: 0.24
Nodes (8): IPRangeRole, str, IPRangeCreate, IPRangeOut, IPRangeUpdate, BaseModel, field_validator, model_validator

### Community 64 - "test_changelog.py"
Cohesion: 0.23
Nodes (12): AsyncClient, tag_assignments.object_id has no FK — deleting a tagged object must drop its…, Tag.assignments is already ORM delete-orphan — each removed assignment lands in…, PATCH settings with a null value deletes the app_settings row — that delete…, /addresses/bulk action=delete used to issue one Core DELETE — invisible to the…, test_bulk_delete_writes_changelog_entries(), test_changelog_captures_ip_status_change(), test_changelog_records_crud() (+4 more)

### Community 65 - "_upload"
Cohesion: 0.31
Nodes (7): v2 workbook: SRV2 edited, SRV3 added, SRV1 missing -> merge keeps SRV1, updates…, _servers_xlsx(), test_import_as_list_e2e(), test_manually_edited_row_wins_conflict(), test_reimport_merges_by_key(), TestCsvImport, _upload()

### Community 66 - "hex_color_or_none"
Cohesion: 0.11
Nodes (14): hex_color_or_none(), Shared row/tag color validator: #rrggbb, normalized to lowercase., field_validator, field_validator, _rail_width(), field_validator, AssignBody, BaseModel (+6 more)

### Community 67 - "restore"
Cohesion: 0.23
Nodes (12): list_scheduled_backups(), AsyncSession, post, Request, Restore a backup file (raw .json.gz body). Wipes every data table (users are…, Scheduled snapshot files written by the worker into BACKUP_DIR., restore(), BackupFileInfo (+4 more)

### Community 68 - "test_allocation.py"
Cohesion: 0.24
Nodes (11): sf(), _mk_prefix(), test_address_crud_and_dup_guard(), test_allocation_skips_existing(), test_concurrent_allocation_unique(), alloc(), test_exhausted_prefix_conflicts(), test_sequential_allocation_skips_boundaries() (+3 more)

### Community 69 - "test_scan_cidr_tcp_fallback_reports_found"
Cohesion: 0.21
Nodes (8): on_hosts fires once per detection step with that chunk's new IPs — ARP batch…, When L2+L3 find nothing, the TCP fallback publishes its batch too., test_scan_cidr_emits_found_deltas(), fake_icmp(), fake_probe(), fake_ptr(), on_hosts(), test_scan_cidr_tcp_fallback_reports_found()

### Community 70 - "Racks"
Cohesion: 0.16
Nodes (17): CC0 1.0 Universal, netbox-community/devicetype-library, Rack device image library, Carrier slot layout, Device image library, Elevation editor, Find free U, Health overlay (+9 more)

### Community 71 - "test_prefix_api.py"
Cohesion: 0.33
Nodes (10): _global_vrf_id(), Splits are counted arithmetically before materializing: anything over…, test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_prefixes_order_by_utilization_and_limit(), test_same_cidr_allowed_across_vrfs(), test_split_cardinality_cap(), test_split_endpoint() (+2 more)

### Community 72 - "_FakePool"
Cohesion: 0.20
Nodes (8): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture, Stands in for the arq Redis pool — never actually dispatches work., scan_exclude_networks=10.70.0.64/26 inside scan_networks=10.70.0.0/24: the…, test_scheduler_and_route_share_exclusion_guard()

### Community 73 - "runtime_settings.py"
Cohesion: 0.19
Nodes (13): _env_sourced(), Any, Runtime-editable settings: app_settings rows override env defaults. Each public…, True when the field's current value differs from its declared default., One runtime-editable setting. field: the env-backed attribute on…, SettingSpec, _v_bool(), _v_cidr_list() (+5 more)

### Community 75 - "devDependencies"
Cohesion: 0.20
Nodes (10): devDependencies, autoprefixer, postcss, sharp, tailwindcss, @types/js-yaml, @types/node, @types/react (+2 more)

### Community 76 - "schemas/asset.py"
Cohesion: 0.36
Nodes (7): AssetKind, str, AssetCreate, AssetOut, AssetUpdate, BaseModel, field_validator

### Community 77 - "schemas/vrf.py"
Cohesion: 0.33
Nodes (5): BaseModel, field_validator, VRFCreate, VRFOut, VRFUpdate

### Community 78 - "check-rack-library.mjs"
Cohesion: 0.25
Nodes (6): DIR, FACES, LAYOUTS, problems, referenced, slugs

### Community 79 - "run_scheduled_backup"
Cohesion: 0.24
Nodes (13): backup_dir(), delete_backup_file(), list_backup_files(), prune_backups(), Path, Fetch a scheduled backup by file name (path-traversal safe)., Delete a scheduled backup by file name (path-traversal safe)., Delete oldest scheduled backups beyond the retention count. (+5 more)

### Community 80 - "schemas/service.py"
Cohesion: 0.38
Nodes (5): BaseModel, field_validator, ServiceCreate, ServiceOut, ServiceUpdate

### Community 81 - "test_auth.py"
Cohesion: 0.29
Nodes (11): AsyncClient, When the socket peer isn't in ipambox_trusted_proxies, a supplied XFF is…, Spreading failures across many usernames from one IP trips the aggregate lock —…, Five bad logins for one (user, ip) pair must not lock out other users on the…, test_endpoints_require_auth(), test_lockout_keyed_per_user_ip_pair(), test_login_lockout(), test_per_ip_aggregate_backstop() (+3 more)

### Community 82 - "_FakePool"
Cohesion: 0.29
Nodes (5): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture

### Community 83 - "auth_on"
Cohesion: 0.29
Nodes (4): auth_on(), fake_arq(), fixture, Turn auth on for a test, restore insecure mode after, and flush session/lockout…

### Community 84 - "Demo import data — ALL FICTIONAL"
Cohesion: 0.29
Nodes (6): Demo import data — ALL FICTIONAL, Files, `Network_Address_DEMO_EN.xlsx` — the edge-case workbook, `Network_Address_DEMO.xlsx` — the clean flagship, Regenerating, VLAN scheme (both workbooks + `demo-vlans.csv`)

### Community 85 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, build:rack-library, check:rack-library, dev, lint, start

### Community 87 - "next"
Cohesion: 0.33
Nodes (3): nextConfig, metadata, next

### Community 88 - "quick-scan.tsx"
Cohesion: 0.15
Nodes (13): QuickScanDialog(), useScanStream(), DialogClose, DialogDescription, DialogOverlay, DialogPortal, DialogTrigger, scanStreamUrl() (+5 more)

### Community 89 - "use-chart-theme.ts"
Cohesion: 0.50
Nodes (4): ChartTheme, FALLBACK, readTheme(), useChartTheme()

### Community 90 - "get_effective"
Cohesion: 0.24
Nodes (11): Effective, get_effective(), AsyncSession, detect_interface(), detect_local_cidr(), CIDR of the default-route interface, e.g. '192.168.1.0/24'., ScanJob, Enqueue a scan for every configured network (effective settings). Targets:… (+3 more)

### Community 91 - ".test_legacy_bezeq_layout"
Cohesion: 0.40
Nodes (3): קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., TestCircuitsParser

### Community 93 - "Security Policy"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 94 - "schemas/changelog.py"
Cohesion: 0.67
Nodes (3): ChangeField, ChangeLogOut, BaseModel

### Community 95 - "_positional_columns"
Cohesion: 0.29
Nodes (4): _col_class(), _positional_columns(), Dominant content class of a column sample., Headerless sheet: locate the IP column, then assign the remaining canonical…

### Community 117 - "SettingsValidationError"
Cohesion: 0.67
Nodes (3): Exception, Carries {key: message} so the API can return per-field 422s., SettingsValidationError

## Knowledge Gaps
- **302 isolated node(s):** `nextConfig`, `name`, `version`, `private`, `dev` (+297 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 967 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **62 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `IPAddress` connect `IPAddress` to `services/backup.py`, `IPAMError`, `maintenance.py`, `prefixes.py`, `v1/search.py`, `_get_rack`, `worker.py`, `test_racks.py`, `addresses.py`, `v1/racks.py`, `entities.py`, `_mklist`, `reconcile`, `test_scanner.py`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Why does `User` connect `User` to `services/backup.py`, `IPAMError`, `restore`, `maintenance.py`, `UserRole`, `v1/auth.py`, `test_ordering.py`, `test_colors.py`, `test_racks.py`, `addresses.py`, `users.py`, `restore_backup`, `imports.py`, `entities.py`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Why does `react` connect `react` to `prefixes/[id]/page.tsx`, `prefixes/[id]/print/page.tsx`, `racks/[id]/page.tsx`, `cn`, `prefixes/page.tsx`, `list-client.tsx`, `label/page.tsx`, `racks/[id]/print/page.tsx`, `racks/page.tsx`, `scans/page.tsx`, `services/page.tsx`, `appearance/page.tsx`, `backup/page.tsx`, `color-rules/page.tsx`, `data/page.tsx`, `settings/page.tsx`, `scanning/page.tsx`, `security/page.tsx`, `users/page.tsx`, `command-palette.tsx`, `sites/page.tsx`, `tags/page.tsx`, `vlans/page.tsx`, `ip-drawer.tsx`, `useAsyncData`, `route-error.tsx`, `package.json`, `tree/page.tsx`, `rackula.ts`, `vrfs/page.tsx`, `import-client.tsx`, `index.ts`, `next`, `quick-scan.tsx`, `use-chart-theme.ts`, `login/page.tsx`, `setup/page.tsx`, `certificates/page.tsx`, `changelog/page.tsx`, `circuits/page.tsx`, `discovery/page.tsx`, `import/page.tsx`, `inventory/page.tsx`, `lists/page.tsx`, `lists/[slug]/page.tsx`, `app/page.tsx`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Are the 58 inferred relationships involving `IPAMError` (e.g. with `create_address()` and `delete_address()`) actually correct?**
  _`IPAMError` has 58 INFERRED edges - model-reasoned connections that need verification._
- **What connects `nextConfig`, `name`, `version` to the rest of the system?**
  _302 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `services/backup.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08612612612612612 - nodes in this community are weakly interconnected._
- **Should `react` be split into smaller, more focused modules?**
  _Cohesion score 0.07961904761904762 - nodes in this community are weakly interconnected._