# Graph Report - IpamBox  (2026-09-23)

## Corpus Check
- 0 files · ~99,999 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3043 nodes · 10125 edges · 187 communities (98 shown, 61 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 672 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- IP List Components & Prefs
- Entity List Pages
- Prefix IPAM Logic
- API Routers & CRUD Factory
- Changelog / Audit Hooks
- Shared UI & Types
- Test Fixtures & Rack Tests
- IP Addresses API
- History & Print UI
- Auth & Security
- Deployment & Docs
- Custom Lists API
- Backup & Export
- Scan Reconciliation
- Demo Data Generator
- Color Rules & Shared Types
- Workbook Parsing
- Import UI
- Scan API & Models
- Scanner Worker
- Color Rules API
- Docs & Command Palette
- Prefix Tree UI
- Error Boundaries
- Infra & Lifespan
- Community 25
- Community 26
- Community 27
- Community 28
- Community 29
- Cross-Entity Search
- Community 31
- Community 32
- Rack Groups API & Model
- Community 34
- Rack Schemas
- Community 36
- Community 37
- Rack Row View (Groups UI)
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
- Community 161
- Community 162
- Community 167
- Community 168
- Community 169
- Community 170
- Community 171
- Community 172
- Community 173
- Community 174
- Community 177
- Community 178
- Community 179
- Community 180
- Community 181
- Community 182
- Community 183
- Community 184
- Community 185
- Community 186

## God Nodes (most connected - your core abstractions)
1. `cn()` - 148 edges
2. `react` - 121 edges
3. `IPAMError` - 87 edges
4. `get_or_404()` - 72 edges
5. `useAsyncData()` - 67 edges
6. `lucide-react` - 67 edges
7. `User` - 66 edges
8. `IPAddress` - 63 edges
9. `useAuth()` - 57 edges
10. `Prefix` - 55 edges

## Surprising Connections (you probably didn't know these)
- `scanner service (arq worker, host networking)` --shares_data_with--> `ip column type (live IPAM resolution)`  [INFERRED]
  docker-compose.yml → frontend/src/content/docs/lists.md
- `Four roles (Administrator, Operator, Contributor, Viewer)` --semantically_similar_to--> `4-tier RBAC (Administrator/Operator/Contributor/Viewer)`  [EXTRACTED] [semantically similar]
  frontend/src/content/docs/accounts-and-roles.md → README.md
- `ip column type (live IPAM resolution)` --semantically_similar_to--> `Health overlay`  [INFERRED] [semantically similar]
  frontend/src/content/docs/lists.md → frontend/src/content/docs/racks.md
- `Inventory (asset register)` --semantically_similar_to--> `Certificate expiry tracking`  [INFERRED] [semantically similar]
  frontend/src/content/docs/inventory.md → frontend/src/content/docs/certificates.md
- `AppSetting` --uses--> `get_effective()`  [INFERRED]
  backend/app/models/app_setting.py → backend/app/services/runtime_settings.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Site → VRF → Prefix → IP address core hierarchy** — frontend_src_content_docs_sites_sites, frontend_src_content_docs_vrfs_vrfs, frontend_src_content_docs_subnets_subnets, frontend_src_content_docs_addresses_ip_addresses, frontend_src_content_docs_overview_data_model_hierarchy [EXTRACTED 1.00]
- **Scan → reconcile → human-review flow** — frontend_src_content_docs_scans_scans, frontend_src_content_docs_scans_scan_pipeline, frontend_src_content_docs_scans_scapy_scanner, frontend_src_content_docs_discovery_reconciliation, frontend_src_content_docs_discovery_discovery_inbox, frontend_src_content_docs_addresses_ip_addresses, frontend_src_content_docs_addresses_mac_mismatch [EXTRACTED 1.00]
- **X-Forwarded-For trusted-proxy pinning (web pinned IP + TEST-NET subnet + api TRUSTED_PROXIES)** — docker_compose_web_service, docker_compose_ipam_network, docker_compose_api_service [EXTRACTED 1.00]
- **Workbook import lifecycle (batch provenance + key-column merge + custom-list import)** — frontend_src_content_docs_inventory_import_batch_provenance, frontend_src_content_docs_lists_key_column_merge, frontend_src_content_docs_lists_custom_lists [INFERRED 0.70]
- **Live IP scan status propagation (scanner → ip_addresses → list ip column + rack health overlay)** — docker_compose_scanner_service, frontend_src_content_docs_lists_ip_addresses, frontend_src_content_docs_lists_ip_column_type, frontend_src_content_docs_racks_health_overlay [INFERRED 0.75]
- **Rack library bundling pipeline** — frontend_public_rack_library_attribution_netbox_devicetype_library, frontend_scripts_build_rack_library, frontend_public_rack_library_attribution_rack_device_image_library, frontend_src_content_docs_racks_device_image_library [INFERRED 0.85]

## Communities (187 total, 61 thin omitted)

### Community 0 - "IP List Components & Prefs"
Cohesion: 0.03
Nodes (104): ImportListDialog(), IpCell(), SortableColRow(), IP_ROLES, IP_STATUSES, PrefixDetailPage(), RANGE_ROLES, SplitDialog() (+96 more)

### Community 1 - "Entity List Pages"
Cohesion: 0.10
Nodes (79): CertificatesPage(), EMPTY, CircuitsPage(), EMPTY, AssetRow, EMPTY, InventoryPage(), cellLabel() (+71 more)

### Community 2 - "Prefix IPAM Logic"
Cohesion: 0.05
Nodes (90): allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), _prefix_rows() (+82 more)

### Community 3 - "API Routers & CRUD Factory"
Cohesion: 0.05
Nodes (82): list_changelog(), AsyncSession, get, AsyncSession, get, stats(), _crud_router(), create_item() (+74 more)

### Community 4 - "Changelog / Audit Hooks"
Cohesion: 0.08
Nodes (54): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), SyncSession, Audit trail via session flush hooks. before_flush collects (object, action,…, register() (+46 more)

### Community 5 - "Shared UI & Types"
Cohesion: 0.11
Nodes (47): ACTION_STYLES, BulkResp, FeatureDef, GROUPS, Key, Key, STATUSES, AsyncPanel() (+39 more)

### Community 6 - "Test Fixtures & Rack Tests"
Cohesion: 0.09
Nodes (73): AsyncClient, _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it. (+65 more)

### Community 7 - "IP Addresses API"
Cohesion: 0.06
Nodes (60): _address_csv_row(), _addresses_stmt(), bulk_addresses(), BulkBody, create_address(), delete_address(), export_addresses(), get_address() (+52 more)

### Community 8 - "History & Print UI"
Cohesion: 0.05
Nodes (57): ACTION_STYLES, ChangelogPage(), DiscoveryPage(), ImportPage(), ListsClient(), PrintClient(), LabelClient(), FACE_BADGE (+49 more)

### Community 9 - "Auth & Security"
Cohesion: 0.07
Nodes (66): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+58 more)

### Community 10 - "Deployment & Docs"
Cohesion: 0.09
Nodes (61): api service (FastAPI/uvicorn backend), db service (PostgreSQL 16), ipam bridge network (192.0.2.0/24), redis service (Redis 7, appendonly), scanner service (arq worker, host networking), web service (Next.js frontend), Accounts & Roles, Insecure mode (IPAMBOX_ALLOW_INSECURE) (+53 more)

### Community 11 - "Custom Lists API"
Cohesion: 0.08
Nodes (51): bulk_rows(), _check_columns(), create_list(), create_row(), delete_list(), delete_row(), get_list(), list_lists() (+43 more)

### Community 12 - "Backup & Export"
Cohesion: 0.05
Nodes (56): delete_scheduled_backup(), download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, delete, get, post (+48 more)

### Community 13 - "Scan Reconciliation"
Cohesion: 0.08
Nodes (47): _flag(), Any, AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), HostResult, _global_vrf_id(), _infer_scan_vrf() (+39 more)

### Community 14 - "Demo Data Generator"
Cohesion: 0.09
Nodes (49): assets_rows(), _assign_site_sheets(), _assign_site_sheets_clean(), build_en_workbook(), build_mixed_workbook(), build_sites(), certificates_rows(), circuits_rows() (+41 more)

### Community 15 - "Color Rules & Shared Types"
Cohesion: 0.05
Nodes (46): Draft, ENTITIES, OP_LABEL, OPS_BY_TYPE, opsFor(), RuleDialog(), ROW_COLOR_PALETTE, Asset (+38 more)

### Community 16 - "Workbook Parsing"
Cohesion: 0.08
Nodes (41): assemble_ip(), clean(), _clean_octets(), map_status(), mask_to_prefixlen(), network_of(), norm_header(), norm_mac() (+33 more)

### Community 17 - "Import UI"
Cohesion: 0.10
Nodes (32): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, PreviewResp, SheetResults(), Step (+24 more)

### Community 18 - "Scan API & Models"
Cohesion: 0.08
Nodes (34): ArqRedis, cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession (+26 more)

### Community 19 - "Scanner Worker"
Cohesion: 0.11
Nodes (40): set_actor(), str, ScanJob, ScanStatus, detect_interface(), detect_local_cidr(), CIDR of the default-route interface, e.g. '192.168.1.0/24'., _due() (+32 more)

### Community 20 - "Color Rules API"
Cohesion: 0.09
Nodes (38): create_rule(), delete_rule(), get_rule(), list_rules(), preview_rule(), AsyncSession, delete, get (+30 more)

### Community 21 - "Docs & Command Palette"
Cohesion: 0.10
Nodes (28): DocsIndexClient(), metadata, DocPage(), dynamicParams, generateMetadata(), loadMarkdown(), CommandPalette(), Icon (+20 more)

### Community 22 - "Prefix Tree UI"
Cohesion: 0.11
Nodes (32): ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), collectExpandableKeys(), flattenTree(), prefixKey() (+24 more)

### Community 24 - "Infra & Lifespan"
Cohesion: 0.07
Nodes (34): close_arq_pool(), close_redis(), get_redis(), Shared process-wide Redis client. Do NOT aclose() it per call — connections…, Shut down the shared client — lifespan/worker shutdown only., healthz(), lifespan(), get (+26 more)

### Community 25 - "Community 25"
Cohesion: 0.12
Nodes (33): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+25 more)

### Community 26 - "Community 26"
Cohesion: 0.10
Nodes (34): RackulaImportDialog(), ABBREV_TO_CATEGORY, canonicalCategory(), CATEGORY_TO_ABBREV, clip(), compareVersions(), decodeShareUrl(), DeviceLike (+26 more)

### Community 27 - "Community 27"
Cohesion: 0.16
Nodes (33): User, _backup_bytes(), _envelope_bytes(), _mkusers(), Hand-craft a backup envelope (e.g. with a forged users table)., Guard: every ORM table must be backed up (or explicitly excluded). Adding a new…, Fresh-server scenario: the migration-seeded Global VRF is replaced by the…, Fresh-server scenario: the target's admins survive; its non-admin set is fully… (+25 more)

### Community 28 - "Community 28"
Cohesion: 0.16
Nodes (32): _check_refs(), create_device(), create_rack(), delete_device(), delete_rack(), _device_fields(), _devices(), _get_device() (+24 more)

### Community 29 - "Community 29"
Cohesion: 0.09
Nodes (25): Exception, Raised inside the pipeline when the user cancels the scan., ScanCancelled, sf(), _api_cancel(), _FakeRedis, _mk_job(), In-memory stand-in for the worker's redis client (get/set/publish). (+17 more)

### Community 30 - "Cross-Entity Search"
Cohesion: 0.17
Nodes (26): _folded(), AsyncSession, get, Cross-object search for the command palette. One GET returns grouped matches…, Column expression with Hebrew final letters folded — pairs with fold_hebrew()…, Short label for a list-row search hit: key-column value, else the first non-…, _row_label(), search() (+18 more)

### Community 31 - "Community 31"
Cohesion: 0.18
Nodes (26): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+18 more)

### Community 32 - "Community 32"
Cohesion: 0.07
Nodes (29): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, js-yaml, jszip, lucide-react (+21 more)

### Community 33 - "Rack Groups API & Model"
Cohesion: 0.15
Nodes (25): _check_site(), create_rack_group(), delete_rack_group(), _get_group(), get_rack_group(), list_rack_groups(), _ordered_racks(), AsyncSession (+17 more)

### Community 34 - "Community 34"
Cohesion: 0.10
Nodes (19): psycopg2-style URL for alembic offline mode / scripts., Settings, Effective, _env_sourced(), get_effective(), Any, AsyncSession, Runtime-editable settings: app_settings rows override env defaults. Each public… (+11 more)

### Community 35 - "Rack Schemas"
Cohesion: 0.14
Nodes (21): str, RackFace, BaseModel, field_validator, RackCreate, RackDetail, RackDeviceCreate, RackDeviceImport (+13 more)

### Community 36 - "Community 36"
Cohesion: 0.17
Nodes (7): parse_sites_master_records(), _Planner, _preview(), (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Match a site among pre-existing DB rows AND sites already planned in this batch…, The circuits sheet doubles as a site directory (מאתר -> מספר אתר + קידומת…, Counter

### Community 37 - "Community 37"
Cohesion: 0.07
Nodes (25): name, private, version, autoprefixer, clsx, jszip, postcss, @radix-ui/react-dropdown-menu (+17 more)

### Community 38 - "Rack Row View (Groups UI)"
Cohesion: 0.18
Nodes (21): DashboardPage(), DragSession, errDetail(), findDevice(), GroupClient(), moveDevice(), metadata, slotRect (+13 more)

### Community 39 - "Community 39"
Cohesion: 0.12
Nodes (24): Rack device image library bundle, arrLen(), attribution(), CATEGORY_COLOUR, CURATED, fetchBuf(), fetchJson(), FRONTEND (+16 more)

### Community 40 - "Community 40"
Cohesion: 0.16
Nodes (24): _audit(), backup_now(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession (+16 more)

### Community 41 - "Community 41"
Cohesion: 0.15
Nodes (22): _build_out(), _lan_info(), _mask_url(), AsyncSession, get, Hide the password in a scheme://user:pass@host URL., LAN identity detected by the host-networked worker (written to Redis). Falls…, read_settings() (+14 more)

### Community 42 - "Community 42"
Cohesion: 0.12
Nodes (20): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), _host_chunks(), _icmp_sweep(), infer_device_type(), _ptr_lookup() (+12 more)

### Community 43 - "Community 43"
Cohesion: 0.10
Nodes (19): Row 0 of an unrecognized sheet looks like headers when every cell is a short…, _sniff_header_row(), excel_date(), date, datetime/date passthrough; int/float serial (20000-80000) -> date; 'd/m/yy'…, parse_assets(), parse_certificates(), Positional 5-col layout: platform, target/VS, server, cert, expiry. (+11 more)

### Community 44 - "Community 44"
Cohesion: 0.21
Nodes (13): _master_row(), _matrix(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind… (+5 more)

### Community 45 - "Community 45"
Cohesion: 0.15
Nodes (21): _check_layout_change(), A carrier's slot_layout can only shrink/clear when no mounted child sits in a…, RackDevice, ConflictError, CarrierError, _check_carrier_mount(), check_placement(), _faces_collide() (+13 more)

### Community 46 - "Community 46"
Cohesion: 0.34
Nodes (22): str, UserRole, login(), mkuser(), other_client(), AsyncClient, AsyncSession, allow_insecure keeps full access (existing behavior preserved). (+14 more)

### Community 47 - "Community 47"
Cohesion: 0.22
Nodes (22): auth_on(), _login(), _mk_rule(), _mk_site(), _mkuser(), AsyncClient, AsyncSession, fixture (+14 more)

### Community 48 - "Community 48"
Cohesion: 0.19
Nodes (19): DragSession, DropRow(), EditorBlock(), errDetail(), Pending, CarrierFrameSvg(), DeviceBlockSvg(), deviceImage() (+11 more)

### Community 49 - "Community 49"
Cohesion: 0.14
Nodes (13): IPRangeRole, str, ip_display(), Any, Normalize asyncpg-returned ipaddress objects / strings to display form. INET…, to_int(), IPRangeCreate, IPRangeOut (+5 more)

### Community 50 - "Community 50"
Cohesion: 0.28
Nodes (18): _circuit_order(), _login(), _mk_circuits(), _mkuser(), AsyncClient, AsyncSession, Global row ordering: POST /{entity}/reorder + pinned rows. Covered on both…, Reordering a subset keeps the slots those rows already had — rows outside the… (+10 more)

### Community 51 - "Community 51"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 52 - "Community 52"
Cohesion: 0.22
Nodes (17): _prefix(), export.csv takes the same filters as the list endpoint — a filtered view…, Same filtered-export treatment on the prefixes CSV (F8)., A documented v6 /64's 2^64 host count must not reach dashboard sums (~1.8e19 >…, test_address_role_nat_and_bulk(), test_addresses_export_respects_filters(), test_bulk_reports_real_counts(), test_container_move_with_children_rejected() (+9 more)

### Community 53 - "Community 53"
Cohesion: 0.17
Nodes (15): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, Every new Settings > Features key is runtime-editable; untouched keys keep the…, test_backup_files_report_effective_schedule() (+7 more)

### Community 54 - "Community 54"
Cohesion: 0.16
Nodes (17): CC0 1.0 Universal, netbox-community/devicetype-library, Rack device image library, Carrier slot layout, Device image library, Elevation editor, Find free U, Health overlay (+9 more)

### Community 55 - "Community 55"
Cohesion: 0.23
Nodes (16): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+8 more)

### Community 56 - "Community 56"
Cohesion: 0.21
Nodes (12): CommitOptions, ListTarget, PreviewOptions, BaseModel, Per-sheet detection result shown in the wizard., Import a sheet as a custom list (user-selected or suggested)., User-confirmed mapping choices applied before building the plan., RowResult (+4 more)

### Community 57 - "Community 57"
Cohesion: 0.18
Nodes (11): _cell_text(), extract_list_table(), _infer_type(), _ips(), _is_ip_token(), Custom-list extraction: turn any sheet into {columns, rows} for a list. Unlike…, SheetMatrix -> (column defs, row dicts). columns: [{key, label, type, options?,…, Raw cell -> stored string. Dates iso-format; everything else cleans. (+3 more)

### Community 58 - "Community 58"
Cohesion: 0.17
Nodes (8): _blocks(), parse_site_sheet(), Split duplicated column groups (031-style runaway): each block starts at an…, MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf., Bare 'Name' (Cellular) maps to the hostname field., Non-empty unnamed columns pile into cf['extra'] instead of vanishing (Pelephone…, TestSiteSheetExtras, TestSiteSheetParser

### Community 59 - "Community 59"
Cohesion: 0.19
Nodes (9): ColorRuleCreate, ColorRuleOut, ColorRuleUpdate, BaseModel, field_validator, model_validator, POST /color-rules/reorder: rule ids of ONE entity_type in new order., RulePreviewOut (+1 more)

### Community 60 - "Community 60"
Cohesion: 0.21
Nodes (3): _mklist(), TestListCRUD, TestRows

### Community 61 - "Community 61"
Cohesion: 0.21
Nodes (6): Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new…, Resolve a 10.{second}.x sheet — site_number is only meaningful inside the…, A declared octet block claims the sheet — unless its site is inactive, in which…, site_key, matched_by for a site_sheet.

### Community 62 - "Community 62"
Cohesion: 0.24
Nodes (11): Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, _csv_sheet(), load_upload(), load_workbook_bytes(), XLSX/CSV -> sheet matrices (openpyxl read_only streams / csv module)., Drop fully-empty trailing rows/cols for a stable matrix shape., One CSV file -> one SheetMatrix named after the file stem. utf-8-sig first…, Dispatch on container type: ZIP -> xlsx workbook; otherwise try CSV text… (+3 more)

### Community 63 - "Community 63"
Cohesion: 0.19
Nodes (8): _master_blocks(), parse_sites_master(), (first, second) octet pairs a master row declares — lets sheet->site matching…, Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins., TestSitesMasterParser

### Community 64 - "Community 64"
Cohesion: 0.24
Nodes (6): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, TestClassify

### Community 65 - "Community 65"
Cohesion: 0.23
Nodes (12): AsyncClient, tag_assignments.object_id has no FK — deleting a tagged object must drop its…, Tag.assignments is already ORM delete-orphan — each removed assignment lands in…, PATCH settings with a null value deletes the app_settings row — that delete…, /addresses/bulk action=delete used to issue one Core DELETE — invisible to the…, test_bulk_delete_writes_changelog_entries(), test_changelog_captures_ip_status_change(), test_changelog_records_crud() (+4 more)

### Community 66 - "Community 66"
Cohesion: 0.26
Nodes (9): Custom lists: CRUD + rows + IP resolution + workbook list-target import., v2 workbook: SRV2 edited, SRV3 added, SRV1 missing -> merge keeps SRV1, updates…, _servers_xlsx(), test_import_as_list_e2e(), test_manually_edited_row_wins_conflict(), test_reimport_merges_by_key(), TestBulkRows, TestCsvImport (+1 more)

### Community 67 - "Community 67"
Cohesion: 0.31
Nodes (12): AsyncClient, Global /api/v1/search endpoint (UX-3)., Regression: list_addresses ?q= used to crash on a missing column., Site + VRF + prefix + address + one of each workbook entity., _seed(), test_addresses_q_filter_not_broken(), test_search_empty_query(), test_search_grouped_results() (+4 more)

### Community 68 - "Community 68"
Cohesion: 0.24
Nodes (11): _check_range_overlap(), create_range(), delete_range(), list_ranges(), AsyncSession, delete, get, post (+3 more)

### Community 69 - "Community 69"
Cohesion: 0.27
Nodes (7): AssignBody, BaseModel, field_validator, TagAssignmentOut, TagCreate, TagOut, TagUpdate

### Community 70 - "Community 70"
Cohesion: 0.29
Nodes (11): AsyncClient, When the socket peer isn't in ipambox_trusted_proxies, a supplied XFF is…, Spreading failures across many usernames from one IP trips the aggregate lock —…, Five bad logins for one (user, ip) pair must not lock out other users on the…, test_endpoints_require_auth(), test_lockout_keyed_per_user_ip_pair(), test_login_lockout(), test_per_ip_aggregate_backstop() (+3 more)

### Community 71 - "Community 71"
Cohesion: 0.21
Nodes (8): on_hosts fires once per detection step with that chunk's new IPs — ARP batch…, When L2+L3 find nothing, the TCP fallback publishes its batch too., test_scan_cidr_emits_found_deltas(), fake_icmp(), fake_probe(), fake_ptr(), on_hosts(), test_scan_cidr_tcp_fallback_reports_found()

### Community 72 - "Community 72"
Cohesion: 0.30
Nodes (9): RackEditor(), canMount(), canPlace(), conflicts(), facesCollide(), freeSlots(), rangesOverlap(), SLOT_LAYOUTS (+1 more)

### Community 73 - "Community 73"
Cohesion: 0.27
Nodes (8): CertificateCreate, CertificateOut, CertificateUpdate, BaseModel, field_validator, DashboardStats, MacMismatchItem, BaseModel

### Community 74 - "Community 74"
Cohesion: 0.33
Nodes (10): _global_vrf_id(), Splits are counted arithmetically before materializing: anything over…, test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_prefixes_order_by_utilization_and_limit(), test_same_cidr_allowed_across_vrfs(), test_split_cardinality_cap(), test_split_endpoint() (+2 more)

### Community 75 - "Community 75"
Cohesion: 0.20
Nodes (8): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture, Stands in for the arq Redis pool — never actually dispatches work., scan_exclude_networks=10.70.0.64/26 inside scan_networks=10.70.0.0/24: the…, test_scheduler_and_route_share_exclusion_guard()

### Community 76 - "Community 76"
Cohesion: 0.33
Nodes (5): CircuitCreate, CircuitOut, CircuitUpdate, BaseModel, field_validator

### Community 78 - "Community 78"
Cohesion: 0.20
Nodes (10): devDependencies, autoprefixer, postcss, sharp, tailwindcss, @types/js-yaml, @types/node, @types/react (+2 more)

### Community 79 - "Community 79"
Cohesion: 0.36
Nodes (7): AssetKind, str, AssetCreate, AssetOut, AssetUpdate, BaseModel, field_validator

### Community 80 - "Community 80"
Cohesion: 0.33
Nodes (5): BaseModel, field_validator, VRFCreate, VRFOut, VRFUpdate

### Community 81 - "Community 81"
Cohesion: 0.22
Nodes (5): pick_key_column(), Default merge column: first non-date/ip column filled in most rows (the…, Map incoming column keys onto an existing list's defs by folded label — a re-…, User-picked key column may arrive as a key ('c0') or a header label ('Name');…, Extract a sheet as custom-list rows and diff it against the existing list…

### Community 82 - "Community 82"
Cohesion: 0.22
Nodes (4): nextConfig, metadata, metadata, next

### Community 83 - "Community 83"
Cohesion: 0.28
Nodes (6): metadata, viewport, PrefsInit(), TooltipProvider, THEMES, useApplyPrefs()

### Community 84 - "Community 84"
Cohesion: 0.25
Nodes (5): hex_color_or_none(), Shared row/tag color validator: #rrggbb, normalized to lowercase., field_validator, field_validator, field_validator

### Community 85 - "Community 85"
Cohesion: 0.43
Nodes (7): _mk_prefix(), test_address_crud_and_dup_guard(), test_allocation_skips_existing(), test_concurrent_allocation_unique(), alloc(), test_exhausted_prefix_conflicts(), test_sequential_allocation_skips_boundaries()

### Community 86 - "Community 86"
Cohesion: 0.25
Nodes (6): DIR, FACES, LAYOUTS, problems, referenced, slugs

### Community 87 - "Community 87"
Cohesion: 0.39
Nodes (7): Placed, LibraryDevice, RACK_LIBRARY, ImportDevice, PreviewRow, RackFace, SlotLayout

### Community 88 - "Community 88"
Cohesion: 0.29
Nodes (4): _col_class(), _positional_columns(), Dominant content class of a column sample., Headerless sheet: locate the IP column, then assign the remaining canonical…

### Community 89 - "Community 89"
Cohesion: 0.29
Nodes (5): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture

### Community 90 - "Community 90"
Cohesion: 0.29
Nodes (4): auth_on(), fake_arq(), fixture, Turn auth on for a test, restore insecure mode after, and flush session/lockout…

### Community 91 - "Community 91"
Cohesion: 0.29
Nodes (6): Demo import data — ALL FICTIONAL, Files, `Network_Address_DEMO_EN.xlsx` — the edge-case workbook, `Network_Address_DEMO.xlsx` — the clean flagship, Regenerating, VLAN scheme (both workbooks + `demo-vlans.csv`)

### Community 92 - "Community 92"
Cohesion: 0.29
Nodes (7): scripts, build, build:rack-library, check:rack-library, dev, lint, start

### Community 94 - "Community 94"
Cohesion: 0.33
Nodes (4): AppearancePage(), metadata, applyPrefs(), resolveTheme()

### Community 95 - "Community 95"
Cohesion: 0.53
Nodes (5): moveRowNav(), G_CHORDS, isEditableTarget(), modalOpen(), useGlobalShortcuts()

### Community 96 - "Community 96"
Cohesion: 0.40
Nodes (3): קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., TestCircuitsParser

### Community 97 - "Community 97"
Cohesion: 0.50
Nodes (4): ChartTheme, FALLBACK, readTheme(), useChartTheme()

### Community 98 - "Community 98"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 100 - "Community 100"
Cohesion: 0.67
Nodes (4): _device_out(), IpRef, LinkedRef, Resolved FK summary for the detail UI: id for the link, label to show.

### Community 101 - "Community 101"
Cohesion: 0.67
Nodes (3): ChangeField, ChangeLogOut, BaseModel

## Knowledge Gaps
- **305 isolated node(s):** `SplitPlan`, `Row`, `SortKey`, `Crumb`, `CellState` (+300 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 987 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **61 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `IPAddress` connect `IP Addresses API` to `Prefix IPAM Logic`, `API Routers & CRUD Factory`, `Changelog / Audit Hooks`, `Community 66`, `Test Fixtures & Rack Tests`, `Community 40`, `Custom Lists API`, `Scan Reconciliation`, `Community 28`, `Scanner Worker`, `Community 25`, `Community 60`, `Cross-Entity Search`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `react` connect `Shared UI & Types` to `IP List Components & Prefs`, `Entity List Pages`, `Community 128`, `Community 129`, `Community 130`, `Community 132`, `Community 131`, `Community 133`, `History & Print UI`, `Community 134`, `Community 135`, `Community 136`, `Community 137`, `Community 138`, `Community 139`, `Color Rules & Shared Types`, `Community 140`, `Import UI`, `Community 141`, `Community 142`, `Community 143`, `Docs & Command Palette`, `Prefix Tree UI`, `Community 144`, `Community 145`, `Community 146`, `Community 147`, `Community 148`, `Community 149`, `Community 150`, `Community 151`, `Community 152`, `Community 153`, `Community 154`, `Community 37`, `Community 48`, `Community 82`, `Community 83`, `Community 94`, `Community 95`, `Community 97`, `Community 103`, `Community 104`, `Error Boundaries`, `Community 126`, `Community 127`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Why does `User` connect `Community 27` to `API Routers & CRUD Factory`, `Changelog / Audit Hooks`, `Test Fixtures & Rack Tests`, `IP Addresses API`, `Community 40`, `Auth & Security`, `Custom Lists API`, `Backup & Export`, `Community 46`, `Community 47`, `Community 50`, `Community 55`, `Community 25`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Are the 63 inferred relationships involving `IPAMError` (e.g. with `_check_site()` and `_get_group()`) actually correct?**
  _`IPAMError` has 63 INFERRED edges - model-reasoned connections that need verification._
- **What connects `SplitPlan`, `Row`, `SortKey` to the rest of the system?**
  _305 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `IP List Components & Prefs` be split into smaller, more focused modules?**
  _Cohesion score 0.034412698412698416 - nodes in this community are weakly interconnected._
- **Should `Entity List Pages` be split into smaller, more focused modules?**
  _Cohesion score 0.10142711518858308 - nodes in this community are weakly interconnected._