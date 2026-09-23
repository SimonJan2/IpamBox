# Graph Report - IpamBox  (2026-09-24)

## Corpus Check
- 372 files · ~930,993 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 20 file(s) not represented in the graph (top: (none) 7, .csv 6, .ini 2)

## Summary
- 3165 nodes · 10700 edges · 182 communities (90 shown, 63 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 720 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c820f926`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- cn
- list-client.tsx
- prefixes.py
- get_or_404
- services/backup.py
- react
- test_racks.py
- IPAddress
- history-panel.tsx
- v1/auth.py
- IpamBox
- IPAMError
- restore
- test_scanner.py
- generate_demo_data.py
- index.ts
- clean
- import-client.tsx
- ScanJob
- worker.py
- color_rules.py
- command-palette.tsx
- tree-client.tsx
- route-error.tsx
- get_settings
- imports.py
- rackula.ts
- User
- v1/racks.py
- _FakeRedis
- v1/search.py
- vlans.py
- dependencies
- rack_groups.py
- runtime_settings.py
- v1/devices.py
- _Planner
- package.json
- rack-row.tsx
- build-rack-library.mjs
- maintenance.py
- _build_out
- scanner.py
- test_workbook_import.py
- _matrix
- Device
- UserRole
- test_colors.py
- rack-editor.tsx
- schemas/ip_range.py
- test_ordering.py
- compilerOptions
- test_ipam_extras.py
- test_settings.py
- Racks
- update_user
- color-rules-client.tsx
- extract_list_table
- parse_site_sheet
- prefixes-client.tsx
- _mklist
- tags.py
- workbook/__init__.py
- parse_sites_master
- classify_sheet
- test_changelog.py
- test_lists.py
- test_search.py
- api service (FastAPI/uvicorn backend)
- hex_color_or_none
- Devices
- test_scan_cidr_tcp_fallback_reports_found
- rack-collision.ts
- schemas/certificate.py
- test_prefix_api.py
- _FakePool
- TestNormalize
- devDependencies
- schemas/asset.py
- schemas/vrf.py
- devices/[id]/page.tsx
- next
- devices/page.tsx
- import/page.tsx
- test_devices.py
- check-rack-library.mjs
- RackFace
- parsers.py
- test_maintenance.py
- fake_arq
- Demo import data — ALL FICTIONAL
- scripts
- test_entities.py
- ip-drawer.tsx
- shortcuts.ts
- scans/page.tsx
- DashboardPage
- Security Policy
- env.py
- appearance/page.tsx
- Rack device image library bundle
- login/page.tsx
- setup/page.tsx
- changelog/page.tsx
- circuits/page.tsx
- discovery/page.tsx
- inventory/page.tsx
- lists/page.tsx
- lists/[slug]/page.tsx
- prefixes/[id]/page.tsx
- prefixes/[id]/print/page.tsx
- prefixes/page.tsx
- label/page.tsx
- racks/[id]/print/page.tsx
- racks/page.tsx
- services/page.tsx
- backup/page.tsx
- color-rules/page.tsx
- data/page.tsx
- features/page.tsx
- settings/page.tsx
- scanning/page.tsx
- security/page.tsx
- users/page.tsx
- sites/page.tsx
- tags/page.tsx
- vlans/page.tsx
- vrfs/page.tsx
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

## God Nodes (most connected - your core abstractions)
1. `cn()` - 156 edges
2. `react` - 126 edges
3. `IPAMError` - 94 edges
4. `get_or_404()` - 75 edges
5. `useAsyncData()` - 73 edges
6. `IPAddress` - 70 edges
7. `lucide-react` - 70 edges
8. `User` - 69 edges
9. `useAuth()` - 63 edges
10. `Button` - 58 edges

## Surprising Connections (you probably didn't know these)
- `scanner service (arq worker, host networking)` --shares_data_with--> `ip column type (live IPAM resolution)`  [INFERRED]
  docker-compose.yml → frontend/src/content/docs/lists.md
- `Four roles (Administrator, Operator, Contributor, Viewer)` --semantically_similar_to--> `4-tier RBAC (Administrator/Operator/Contributor/Viewer)`  [EXTRACTED] [semantically similar]
  frontend/src/content/docs/accounts-and-roles.md → README.md
- `ip column type (live IPAM resolution)` --semantically_similar_to--> `Health overlay`  [INFERRED] [semantically similar]
  frontend/src/content/docs/lists.md → frontend/src/content/docs/racks.md
- `Inventory (asset register)` --semantically_similar_to--> `Certificate expiry tracking`  [INFERRED] [semantically similar]
  frontend/src/content/docs/inventory.md → frontend/src/content/docs/certificates.md
- `_addresses_stmt()` --uses--> `TagAssignment`  [INFERRED]
  backend/app/api/v1/addresses.py → backend/app/models/tag.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Site → VRF → Prefix → IP address core hierarchy** — frontend_src_content_docs_sites_sites, frontend_src_content_docs_vrfs_vrfs, frontend_src_content_docs_subnets_subnets, frontend_src_content_docs_addresses_ip_addresses, frontend_src_content_docs_overview_data_model_hierarchy [EXTRACTED 1.00]
- **Scan → reconcile → human-review flow** — frontend_src_content_docs_scans_scans, frontend_src_content_docs_scans_scan_pipeline, frontend_src_content_docs_scans_scapy_scanner, frontend_src_content_docs_discovery_reconciliation, frontend_src_content_docs_discovery_discovery_inbox, frontend_src_content_docs_addresses_ip_addresses, frontend_src_content_docs_addresses_mac_mismatch [EXTRACTED 1.00]
- **X-Forwarded-For trusted-proxy pinning (web pinned IP + TEST-NET subnet + api TRUSTED_PROXIES)** — docker_compose_web_service, docker_compose_ipam_network, docker_compose_api_service [EXTRACTED 1.00]
- **Workbook import lifecycle (batch provenance + key-column merge + custom-list import)** — frontend_src_content_docs_inventory_import_batch_provenance, frontend_src_content_docs_lists_key_column_merge, frontend_src_content_docs_lists_custom_lists [INFERRED 0.70]
- **Live IP scan status propagation (scanner → ip_addresses → list ip column + rack health overlay)** — docker_compose_scanner_service, frontend_src_content_docs_lists_ip_addresses, frontend_src_content_docs_lists_ip_column_type, frontend_src_content_docs_racks_health_overlay [INFERRED 0.75]
- **Rack library bundling pipeline** — frontend_public_rack_library_attribution_netbox_devicetype_library, frontend_scripts_build_rack_library, frontend_public_rack_library_attribution_rack_device_image_library, frontend_src_content_docs_racks_device_image_library [INFERRED 0.85]

## Communities (182 total, 63 thin omitted)

### Community 0 - "cn"
Cohesion: 0.07
Nodes (54): IpCell(), SortableColRow(), IP_ROLES, IP_STATUSES, RANGE_ROLES, SplitDialog(), SplitPlan, toggleIn() (+46 more)

### Community 1 - "list-client.tsx"
Cohesion: 0.11
Nodes (80): CertificatesPage(), EMPTY, CircuitsPage(), EMPTY, DeviceRow, DevicesPage(), EMPTY, AssetRow (+72 more)

### Community 2 - "prefixes.py"
Cohesion: 0.07
Nodes (64): allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), _prefix_rows() (+56 more)

### Community 3 - "get_or_404"
Cohesion: 0.05
Nodes (65): list_changelog(), AsyncSession, get, AsyncSession, get, stats(), get_item(), update_item() (+57 more)

### Community 4 - "services/backup.py"
Cohesion: 0.06
Nodes (76): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), SyncSession, Audit trail via session flush hooks. before_flush collects (object, action,…, register() (+68 more)

### Community 5 - "react"
Cohesion: 0.10
Nodes (46): ACTION_STYLES, BulkResp, BackupSettingsPage(), downloadUrl(), fmtSize(), DataPage(), download(), FeatureDef (+38 more)

### Community 6 - "test_racks.py"
Cohesion: 0.11
Nodes (59): _carrier(), _dev(), _group(), _imports(), _mount(), _next_free(), AsyncClient, AsyncSession (+51 more)

### Community 7 - "IPAddress"
Cohesion: 0.05
Nodes (68): _address_csv_row(), _addresses_stmt(), bulk_addresses(), BulkBody, create_address(), delete_address(), export_addresses(), get_address() (+60 more)

### Community 8 - "history-panel.tsx"
Cohesion: 0.12
Nodes (22): ACTION_STYLES, ChangelogPage(), DiscoveryPage(), PrefixDetailPage(), fmtEta(), ScansPage(), ACTION_STYLES, ChangeDiff() (+14 more)

### Community 9 - "v1/auth.py"
Cohesion: 0.08
Nodes (60): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+52 more)

### Community 10 - "IpamBox"
Cohesion: 0.11
Nodes (53): Accounts & Roles, Insecure mode (IPAMBOX_ALLOW_INSECURE), Four roles (Administrator, Operator, Contributor, Viewer), Session-cookie authentication, Address roles (vip/vrrp/hsrp/glbp/carp/secondary), Address CSV import/export, IP Addresses, IP drawer (+45 more)

### Community 11 - "IPAMError"
Cohesion: 0.07
Nodes (62): reorder_devices(), _crud_router(), create_item(), delete_item(), list_items(), reorder_items(), bulk_rows(), _check_columns() (+54 more)

### Community 12 - "restore"
Cohesion: 0.10
Nodes (29): delete_scheduled_backup(), download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, delete, get, post (+21 more)

### Community 13 - "test_scanner.py"
Cohesion: 0.07
Nodes (50): _flag(), Any, AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), HostResult, _global_vrf_id(), _infer_scan_vrf() (+42 more)

### Community 14 - "generate_demo_data.py"
Cohesion: 0.09
Nodes (49): assets_rows(), _assign_site_sheets(), _assign_site_sheets_clean(), build_en_workbook(), build_mixed_workbook(), build_sites(), certificates_rows(), circuits_rows() (+41 more)

### Community 15 - "index.ts"
Cohesion: 0.05
Nodes (55): PrintClient(), DragSession, STATUSES, IpStatusBadge(), PrefixStatusBadge(), prefixVariant, scanVariant, STATUS_TOKENS (+47 more)

### Community 16 - "clean"
Cohesion: 0.09
Nodes (32): assemble_ip(), clean(), _clean_octets(), map_status(), mask_to_prefixlen(), network_of(), norm_mac(), parse_range_end() (+24 more)

### Community 17 - "import-client.tsx"
Cohesion: 0.09
Nodes (24): DeviceDetailClient(), ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, ImportPage(), PreviewResp (+16 more)

### Community 18 - "ScanJob"
Cohesion: 0.08
Nodes (35): ArqRedis, cancel_scan(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession, get (+27 more)

### Community 19 - "worker.py"
Cohesion: 0.08
Nodes (41): _check_cidr_allowed(), _lan_info(), LAN identity detected by the host-networked worker (written to Redis). Falls…, set_actor(), get_effective(), AsyncSession, exclusion_hit(), Scan-target policy shared by the API route, the scheduler, and the worker.… (+33 more)

### Community 20 - "color_rules.py"
Cohesion: 0.07
Nodes (46): create_rule(), delete_rule(), get_rule(), list_rules(), preview_rule(), AsyncSession, delete, get (+38 more)

### Community 21 - "command-palette.tsx"
Cohesion: 0.08
Nodes (33): DocsIndexClient(), metadata, DocPage(), dynamicParams, generateMetadata(), loadMarkdown(), metadata, viewport (+25 more)

### Community 22 - "tree-client.tsx"
Cohesion: 0.19
Nodes (19): metadata, ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), collectExpandableKeys(), flattenTree() (+11 more)

### Community 24 - "get_settings"
Cohesion: 0.07
Nodes (47): get_settings(), close_arq_pool(), close_redis(), get_redis(), Shared process-wide Redis client. Do NOT aclose() it per call — connections…, Shut down the shared client — lifespan/worker shutdown only., _trusted_nets(), lifespan() (+39 more)

### Community 25 - "imports.py"
Cohesion: 0.10
Nodes (38): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+30 more)

### Community 26 - "rackula.ts"
Cohesion: 0.09
Nodes (36): metadata, RackDetailPage(), RackulaImportDialog(), ABBREV_TO_CATEGORY, canonicalCategory(), CATEGORY_TO_ABBREV, clip(), compareVersions() (+28 more)

### Community 27 - "User"
Cohesion: 0.14
Nodes (37): AsyncSession, Request, Guard for every API route. Returns the User, or None in allow_insecure mode., require_auth(), User, _backup_bytes(), _envelope_bytes(), _mkusers() (+29 more)

### Community 28 - "v1/racks.py"
Cohesion: 0.11
Nodes (51): _check_refs(), create_device(), create_rack(), delete_device(), delete_rack(), _device_out(), _devices(), _get_device() (+43 more)

### Community 29 - "_FakeRedis"
Cohesion: 0.10
Nodes (21): _api_cancel(), _FakeRedis, _mk_job(), In-memory stand-in for the worker's redis client (get/set/publish)., Point the worker at the test DB (sf) and the fake redis client., Simulate the API-side cancel: terminal status on a fresh connection., Cancel flag polled between phases -> ScanCancelled -> CANCELLED, and no…, Audit race: API writes CANCELLED mid-scan while the redis flag is lost… (+13 more)

### Community 30 - "v1/search.py"
Cohesion: 0.17
Nodes (27): _folded(), AsyncSession, get, Cross-object search for the command palette. One GET returns grouped matches…, Column expression with Hebrew final letters folded — pairs with fold_hebrew()…, Short label for a list-row search hit: key-column value, else the first non-…, _row_label(), search() (+19 more)

### Community 31 - "vlans.py"
Cohesion: 0.16
Nodes (27): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+19 more)

### Community 32 - "dependencies"
Cohesion: 0.07
Nodes (29): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, js-yaml, jszip, lucide-react (+21 more)

### Community 33 - "rack_groups.py"
Cohesion: 0.12
Nodes (29): _check_site(), create_rack_group(), delete_rack_group(), _get_group(), get_rack_group(), list_rack_groups(), _ordered_racks(), AsyncSession (+21 more)

### Community 34 - "runtime_settings.py"
Cohesion: 0.09
Nodes (20): psycopg2-style URL for alembic offline mode / scripts., Settings, Effective, _env_sourced(), Any, Exception, Runtime-editable settings: app_settings rows override env defaults. Each public…, True when the field's current value differs from its declared default. (+12 more)

### Community 35 - "v1/devices.py"
Cohesion: 0.10
Nodes (35): _asset_ref(), _check_refs(), create_device(), delete_device(), _detail(), _get_device(), list_devices(), AsyncSession (+27 more)

### Community 36 - "_Planner"
Cohesion: 0.09
Nodes (16): _Planner, (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Folded sheet title vs site name/code — word-boundary matching so 'int' doesn't…, Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new…, Resolve a 10.{second}.x sheet — site_number is only meaningful inside the…, A declared octet block claims the sheet — unless its site is inactive, in which… (+8 more)

### Community 37 - "package.json"
Cohesion: 0.07
Nodes (27): name, private, version, autoprefixer, clsx, jszip, postcss, @radix-ui/react-dialog (+19 more)

### Community 38 - "rack-row.tsx"
Cohesion: 0.15
Nodes (16): errDetail(), findDevice(), GroupClient(), moveDevice(), metadata, RackUGrid(), freeByRack(), parseRowDev() (+8 more)

### Community 39 - "build-rack-library.mjs"
Cohesion: 0.13
Nodes (23): arrLen(), attribution(), CATEGORY_COLOUR, CURATED, fetchBuf(), fetchJson(), FRONTEND, FULL_IMPORT (+15 more)

### Community 40 - "maintenance.py"
Cohesion: 0.07
Nodes (49): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+41 more)

### Community 41 - "_build_out"
Cohesion: 0.15
Nodes (19): _build_out(), _mask_url(), AsyncSession, get, Hide the password in a scheme://user:pass@host URL., read_settings(), update_settings(), ChangePasswordBody (+11 more)

### Community 42 - "scanner.py"
Cohesion: 0.12
Nodes (20): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), _host_chunks(), _icmp_sweep(), infer_device_type(), _ptr_lookup() (+12 more)

### Community 43 - "test_workbook_import.py"
Cohesion: 0.15
Nodes (12): parse_certificates(), parse_servers(), Positional 5-col layout: platform, target/VS, server, cert, expiry., 002 שרתים בייצור: Name, Guest OS, IP Address(multi), Cert, License, owner., Workbook import: normalizer/parser unit tests (no DB) + API e2e., Small synthetic workbook: sites master + one site sheet + circuits., test_commit_twice_rejected(), test_import_e2e() (+4 more)

### Community 44 - "_matrix"
Cohesion: 0.21
Nodes (13): _master_row(), _matrix(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind… (+5 more)

### Community 45 - "Device"
Cohesion: 0.12
Nodes (32): Device, ConflictError, apply_device_patch(), carrier_children(), CarrierError, _check_carrier_mount(), check_layout_change(), check_placement() (+24 more)

### Community 46 - "UserRole"
Cohesion: 0.28
Nodes (24): str, UserRole, Viewer tier can read lists/rows but every mutation is 403., TestPermissions, login(), mkuser(), other_client(), AsyncClient (+16 more)

### Community 47 - "test_colors.py"
Cohesion: 0.27
Nodes (19): _login(), _mk_rule(), _mk_site(), _mkuser(), AsyncClient, AsyncSession, Global row colors: manual row_color + rule-computed display_color. Covers the…, test_backup_roundtrips_color_rules() (+11 more)

### Community 48 - "rack-editor.tsx"
Cohesion: 0.17
Nodes (26): DeviceFormDialog(), DragSession, DropRow(), EditorBlock(), errDetail(), Pending, RackEditor(), CarrierFrameSvg() (+18 more)

### Community 49 - "schemas/ip_range.py"
Cohesion: 0.24
Nodes (8): IPRangeRole, str, IPRangeCreate, IPRangeOut, IPRangeUpdate, BaseModel, field_validator, model_validator

### Community 50 - "test_ordering.py"
Cohesion: 0.28
Nodes (18): _circuit_order(), _login(), _mk_circuits(), _mkuser(), AsyncClient, AsyncSession, Global row ordering: POST /{entity}/reorder + pinned rows. Covered on both…, Reordering a subset keeps the slots those rows already had — rows outside the… (+10 more)

### Community 51 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 52 - "test_ipam_extras.py"
Cohesion: 0.22
Nodes (17): _prefix(), export.csv takes the same filters as the list endpoint — a filtered view…, Same filtered-export treatment on the prefixes CSV (F8)., A documented v6 /64's 2^64 host count must not reach dashboard sums (~1.8e19 >…, test_address_role_nat_and_bulk(), test_addresses_export_respects_filters(), test_bulk_reports_real_counts(), test_container_move_with_children_rejected() (+9 more)

### Community 53 - "test_settings.py"
Cohesion: 0.17
Nodes (15): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, Every new Settings > Features key is runtime-editable; untouched keys keep the…, test_backup_files_report_effective_schedule() (+7 more)

### Community 54 - "Racks"
Cohesion: 0.16
Nodes (17): CC0 1.0 Universal, netbox-community/devicetype-library, Rack device image library, Carrier slot layout, Device image library, Elevation editor, Find free U, Health overlay (+9 more)

### Community 55 - "update_user"
Cohesion: 0.19
Nodes (15): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+7 more)

### Community 56 - "color-rules-client.tsx"
Cohesion: 0.10
Nodes (42): ImportListDialog(), IPAM_FAMILIES, Step, LabelClient(), FACE_BADGE, PrintClient(), FACE_BADGE, Draft (+34 more)

### Community 57 - "extract_list_table"
Cohesion: 0.11
Nodes (20): ListTarget, Import a sheet as a custom list (user-selected or suggested)., _cell_text(), extract_list_table(), _infer_type(), _ips(), _is_ip_token(), SheetMatrix -> (column defs, row dicts). columns: [{key, label, type, options?,… (+12 more)

### Community 58 - "parse_site_sheet"
Cohesion: 0.20
Nodes (6): parse_site_sheet(), MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf., Bare 'Name' (Cellular) maps to the hostname field., Non-empty unnamed columns pile into cf['extra'] instead of vanishing (Pelephone…, TestSiteSheetExtras, TestSiteSheetParser

### Community 59 - "prefixes-client.tsx"
Cohesion: 0.14
Nodes (19): EMPTY_EDIT, FACE_BADGE, PrefixRow, utilColor(), InlineSelect(), QuickScanDialog(), usePrefixScanOverlay(), useScanStream() (+11 more)

### Community 60 - "_mklist"
Cohesion: 0.18
Nodes (4): _mklist(), TestBulkRows, TestListCRUD, TestRows

### Community 61 - "tags.py"
Cohesion: 0.23
Nodes (16): assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession, delete (+8 more)

### Community 62 - "workbook/__init__.py"
Cohesion: 0.26
Nodes (9): Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, _csv_sheet(), load_workbook_bytes(), XLSX/CSV -> sheet matrices (openpyxl read_only streams / csv module)., Drop fully-empty trailing rows/cols for a stable matrix shape., One CSV file -> one SheetMatrix named after the file stem. utf-8-sig first…, Parse workbook bytes into per-sheet row matrices. read_only + data_only:…, SheetMatrix (+1 more)

### Community 63 - "parse_sites_master"
Cohesion: 0.21
Nodes (7): parse_sites_master(), parse_sites_master_records(), Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins., TestSitesMasterParser

### Community 64 - "classify_sheet"
Cohesion: 0.24
Nodes (6): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, TestClassify

### Community 65 - "test_changelog.py"
Cohesion: 0.23
Nodes (12): AsyncClient, tag_assignments.object_id has no FK — deleting a tagged object must drop its…, Tag.assignments is already ORM delete-orphan — each removed assignment lands in…, PATCH settings with a null value deletes the app_settings row — that delete…, /addresses/bulk action=delete used to issue one Core DELETE — invisible to the…, test_bulk_delete_writes_changelog_entries(), test_changelog_captures_ip_status_change(), test_changelog_records_crud() (+4 more)

### Community 66 - "test_lists.py"
Cohesion: 0.26
Nodes (10): pick_key_column(), Default merge column: first non-date/ip column filled in most rows (the…, Custom lists: CRUD + rows + IP resolution + workbook list-target import., v2 workbook: SRV2 edited, SRV3 added, SRV1 missing -> merge keeps SRV1, updates…, _servers_xlsx(), test_import_as_list_e2e(), test_manually_edited_row_wins_conflict(), test_reimport_merges_by_key() (+2 more)

### Community 67 - "test_search.py"
Cohesion: 0.31
Nodes (12): AsyncClient, Global /api/v1/search endpoint (UX-3)., Regression: list_addresses ?q= used to crash on a missing column., Site + VRF + prefix + address + one of each workbook entity., _seed(), test_addresses_q_filter_not_broken(), test_search_empty_query(), test_search_grouped_results() (+4 more)

### Community 68 - "api service (FastAPI/uvicorn backend)"
Cohesion: 0.43
Nodes (8): api service (FastAPI/uvicorn backend), db service (PostgreSQL 16), ipam bridge network (192.0.2.0/24), redis service (Redis 7, appendonly), scanner service (arq worker, host networking), web service (Next.js frontend), ip_addresses table (IPAM data store), ip column type (live IPAM resolution)

### Community 69 - "hex_color_or_none"
Cohesion: 0.07
Nodes (26): CircuitCreate, CircuitOut, CircuitUpdate, BaseModel, field_validator, hex_color_or_none(), ip_display(), Any (+18 more)

### Community 70 - "Devices"
Cohesion: 0.25
Nodes (7): API sketch, Device detail, Devices, Devices vs racks, From the IP drawer, Health rollup, The list

### Community 71 - "test_scan_cidr_tcp_fallback_reports_found"
Cohesion: 0.21
Nodes (8): on_hosts fires once per detection step with that chunk's new IPs — ARP batch…, When L2+L3 find nothing, the TCP fallback publishes its batch too., test_scan_cidr_emits_found_deltas(), fake_icmp(), fake_probe(), fake_ptr(), on_hosts(), test_scan_cidr_tcp_fallback_reports_found()

### Community 72 - "rack-collision.ts"
Cohesion: 0.33
Nodes (6): canPlace(), conflicts(), facesCollide(), freeSlots(), rangesOverlap(), SLOT_LAYOUTS

### Community 73 - "schemas/certificate.py"
Cohesion: 0.17
Nodes (13): CertificateCreate, CertificateOut, CertificateUpdate, BaseModel, field_validator, DashboardStats, MacMismatchItem, BaseModel (+5 more)

### Community 74 - "test_prefix_api.py"
Cohesion: 0.33
Nodes (10): _global_vrf_id(), Splits are counted arithmetically before materializing: anything over…, test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_prefixes_order_by_utilization_and_limit(), test_same_cidr_allowed_across_vrfs(), test_split_cardinality_cap(), test_split_endpoint() (+2 more)

### Community 75 - "_FakePool"
Cohesion: 0.20
Nodes (8): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture, Stands in for the arq Redis pool — never actually dispatches work., scan_exclude_networks=10.70.0.64/26 inside scan_networks=10.70.0.0/24: the…, test_scheduler_and_route_share_exclusion_guard()

### Community 78 - "devDependencies"
Cohesion: 0.20
Nodes (10): devDependencies, autoprefixer, postcss, sharp, tailwindcss, @types/js-yaml, @types/node, @types/react (+2 more)

### Community 79 - "schemas/asset.py"
Cohesion: 0.36
Nodes (7): AssetKind, str, AssetCreate, AssetOut, AssetUpdate, BaseModel, field_validator

### Community 80 - "schemas/vrf.py"
Cohesion: 0.33
Nodes (5): BaseModel, field_validator, VRFCreate, VRFOut, VRFUpdate

### Community 82 - "next"
Cohesion: 0.33
Nodes (3): nextConfig, metadata, next

### Community 85 - "test_devices.py"
Cohesion: 0.07
Nodes (57): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., sf() (+49 more)

### Community 86 - "check-rack-library.mjs"
Cohesion: 0.25
Nodes (6): DIR, FACES, LAYOUTS, problems, referenced, slugs

### Community 87 - "RackFace"
Cohesion: 0.39
Nodes (7): Placed, LibraryDevice, RACK_LIBRARY, ImportDevice, PreviewRow, RackFace, SlotLayout

### Community 88 - "parsers.py"
Cohesion: 0.09
Nodes (21): norm_header(), Header cell -> lowercase, single-spaced, for signature matching. Edge…, _blocks(), _col_class(), _is_header_echo(), _leftover_bits(), _map_columns(), _master_blocks() (+13 more)

### Community 89 - "test_maintenance.py"
Cohesion: 0.22
Nodes (10): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, test_backup_now_enqueues(), test_clear_discovery() (+2 more)

### Community 91 - "Demo import data — ALL FICTIONAL"
Cohesion: 0.29
Nodes (6): Demo import data — ALL FICTIONAL, Files, `Network_Address_DEMO_EN.xlsx` — the edge-case workbook, `Network_Address_DEMO.xlsx` — the clean flagship, Regenerating, VLAN scheme (both workbooks + `demo-vlans.csv`)

### Community 92 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, build:rack-library, check:rack-library, dev, lint, start

### Community 94 - "ip-drawer.tsx"
Cohesion: 0.06
Nodes (47): AppearancePage(), AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS, NavGroup, NavItem (+39 more)

### Community 95 - "shortcuts.ts"
Cohesion: 0.53
Nodes (5): moveRowNav(), G_CHORDS, isEditableTarget(), modalOpen(), useGlobalShortcuts()

### Community 97 - "DashboardPage"
Cohesion: 0.25
Nodes (6): DashboardPage(), metadata, ChartTheme, FALLBACK, readTheme(), useChartTheme()

### Community 98 - "Security Policy"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

## Knowledge Gaps
- **317 isolated node(s):** `nextConfig`, `name`, `version`, `private`, `dev` (+312 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1038 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **63 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `IPAddress` connect `IPAddress` to `prefixes.py`, `get_or_404`, `services/backup.py`, `v1/devices.py`, `test_lists.py`, `test_racks.py`, `maintenance.py`, `IPAMError`, `test_scanner.py`, `_mklist`, `worker.py`, `test_devices.py`, `test_maintenance.py`, `v1/racks.py`, `v1/search.py`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Why does `react` connect `react` to `circuits/page.tsx`, `list-client.tsx`, `discovery/page.tsx`, `inventory/page.tsx`, `lists/page.tsx`, `lists/[slug]/page.tsx`, `prefixes/[id]/page.tsx`, `cn`, `history-panel.tsx`, `prefixes/[id]/print/page.tsx`, `prefixes/page.tsx`, `label/page.tsx`, `racks/[id]/print/page.tsx`, `racks/page.tsx`, `services/page.tsx`, `index.ts`, `backup/page.tsx`, `import-client.tsx`, `color-rules/page.tsx`, `data/page.tsx`, `features/page.tsx`, `command-palette.tsx`, `settings/page.tsx`, `scanning/page.tsx`, `security/page.tsx`, `users/page.tsx`, `rackula.ts`, `sites/page.tsx`, `tags/page.tsx`, `tree-client.tsx`, `vlans/page.tsx`, `vrfs/page.tsx`, `route-error.tsx`, `package.json`, `rack-editor.tsx`, `color-rules-client.tsx`, `prefixes-client.tsx`, `devices/[id]/page.tsx`, `next`, `devices/page.tsx`, `import/page.tsx`, `ip-drawer.tsx`, `shortcuts.ts`, `scans/page.tsx`, `DashboardPage`, `appearance/page.tsx`, `login/page.tsx`, `setup/page.tsx`, `changelog/page.tsx`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `get_settings` to `prefixes.py`, `get_or_404`, `env.py`, `runtime_settings.py`, `services/backup.py`, `test_lists.py`, `test_racks.py`, `v1/auth.py`, `_build_out`, `test_search.py`, `UserRole`, `test_colors.py`, `test_ordering.py`, `worker.py`, `test_devices.py`, `imports.py`, `User`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Are the 69 inferred relationships involving `IPAMError` (e.g. with `create_address()` and `delete_address()`) actually correct?**
  _`IPAMError` has 69 INFERRED edges - model-reasoned connections that need verification._
- **What connects `nextConfig`, `name`, `version` to the rest of the system?**
  _317 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `cn` be split into smaller, more focused modules?**
  _Cohesion score 0.06749482401656315 - nodes in this community are weakly interconnected._
- **Should `list-client.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.10907457322551663 - nodes in this community are weakly interconnected._