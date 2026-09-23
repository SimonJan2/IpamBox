# Graph Report - IpamBox  (2026-09-24)

## Corpus Check
- 51 files · ~99,999 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3344 nodes · 11317 edges · 151 communities (93 shown, 28 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 787 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Frontend Pages
- Frontend App Shell
- Prefixes API
- Addresses API
- Device Detail UI
- Frontend Feature Pages
- Changelog Core
- Changelog & Dashboard UI
- Auth API
- Import Wizard UI
- Test Fixtures
- Rack Tests
- Docker Compose Stack
- Discovery & Scans UI
- Config & Migration Env
- Frontend Pages Misc
- Reconcile Worker
- Workbook Service
- Demo Data Generator
- Workbook Import
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
- Community 118
- Community 119
- Community 120
- Community 121
- Community 122
- Community 124
- Community 125
- Community 126
- Community 131
- Community 132
- Community 133
- Community 134
- Community 135
- Community 136
- Community 137
- Community 138
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

## God Nodes (most connected - your core abstractions)
1. `cn()` - 156 edges
2. `react` - 126 edges
3. `IPAMError` - 99 edges
4. `get_or_404()` - 80 edges
5. `IPAddress` - 76 edges
6. `useAsyncData()` - 73 edges
7. `lucide-react` - 70 edges
8. `User` - 69 edges
9. `useAuth()` - 63 edges
10. `Button` - 58 edges

## Surprising Connections (you probably didn't know these)
- `Four roles (Administrator, Operator, Contributor, Viewer)` --semantically_similar_to--> `4-tier RBAC (Administrator/Operator/Contributor/Viewer)`  [EXTRACTED] [semantically similar]
  frontend/src/content/docs/accounts-and-roles.md → README.md
- `Inventory (asset register)` --semantically_similar_to--> `Certificate expiry tracking`  [INFERRED] [semantically similar]
  frontend/src/content/docs/inventory.md → frontend/src/content/docs/certificates.md
- `Health overlay` --semantically_similar_to--> `ip column type (live IPAM resolution)`  [INFERRED] [semantically similar]
  frontend/src/content/docs/racks.md → frontend/src/content/docs/lists.md
- `scanner service (arq worker, host networking)` --shares_data_with--> `ip column type (live IPAM resolution)`  [INFERRED]
  docker-compose.yml → frontend/src/content/docs/lists.md
- `IpamBox` --references--> `Rack Group (bayed row)`  [EXTRACTED]
  README.md → frontend/src/content/docs/racks.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **L1 trace flow (host -> panel-front -> panel-back -> switch)** — frontend_src_content_docs_cabling_l1trace, frontend_src_content_docs_cabling_cable, frontend_src_content_docs_cabling_deviceinterface, frontend_src_content_docs_cabling_pairinterface, frontend_src_content_docs_devices_device [EXTRACTED 1.00]
- **Legacy switch_name/switch_port to connected_interface_id transition** — frontend_src_content_docs_cabling_matchfreetext, frontend_src_content_docs_cabling_switchnamefreetext, frontend_src_content_docs_cabling_connectedinterfaceid, frontend_src_content_docs_addresses_ipaddress [EXTRACTED 1.00]
- **Patch panel model (device + patch interfaces + front/back pairing + one-call generation)** — frontend_src_content_docs_cabling_patchpanel, frontend_src_content_docs_cabling_deviceinterface, frontend_src_content_docs_cabling_pairinterface, frontend_src_content_docs_cabling_portgeneration [EXTRACTED 1.00]

## Communities (151 total, 28 thin omitted)

### Community 0 - "Frontend Pages"
Cohesion: 0.02
Nodes (44): nextConfig, metadata, metadata, metadata, metadata, metadata, metadata, metadata (+36 more)

### Community 1 - "Frontend App Shell"
Cohesion: 0.04
Nodes (92): metadata, viewport, IP_ROLES, IP_STATUSES, RANGE_ROLES, SplitDialog(), SplitPlan, toggleIn() (+84 more)

### Community 2 - "Prefixes API"
Cohesion: 0.06
Nodes (74): allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), _prefix_rows() (+66 more)

### Community 3 - "Addresses API"
Cohesion: 0.06
Nodes (68): _address_csv_row(), _addresses_stmt(), bulk_addresses(), BulkBody, _check_interface_link(), create_address(), delete_address(), export_addresses() (+60 more)

### Community 4 - "Device Detail UI"
Cohesion: 0.10
Nodes (49): EMPTY_EDIT, FACE_BADGE, ImportListDialog(), IPAM_FAMILIES, Step, PrefixRow, Draft, ENTITIES (+41 more)

### Community 5 - "Frontend Feature Pages"
Cohesion: 0.12
Nodes (51): EMPTY, EMPTY, DeviceRow, EMPTY, AssetRow, EMPTY, cellLabel(), CHIP_COLORS (+43 more)

### Community 6 - "Changelog Core"
Cohesion: 0.10
Nodes (41): Audit trail via session flush hooks. before_flush collects (object, action,…, after_flush(), before_flush(), SyncSession, tag_assignments garbage collection. TagAssignment references its target…, register(), healthz(), metrics() (+33 more)

### Community 7 - "Changelog & Dashboard UI"
Cohesion: 0.08
Nodes (47): ACTION_STYLES, ACTION_STYLES, DashboardPage(), DragSession, LabelClient(), metadata, FACE_BADGE, FACE_BADGE (+39 more)

### Community 8 - "Auth API"
Cohesion: 0.08
Nodes (60): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+52 more)

### Community 9 - "Import Wizard UI"
Cohesion: 0.04
Nodes (58): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, PreviewResp, SheetResults(), Step (+50 more)

### Community 10 - "Test Fixtures"
Cohesion: 0.08
Nodes (51): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., _split_dsn() (+43 more)

### Community 11 - "Rack Tests"
Cohesion: 0.11
Nodes (59): _carrier(), _dev(), _group(), _imports(), _mount(), _next_free(), AsyncClient, AsyncSession (+51 more)

### Community 12 - "Docker Compose Stack"
Cohesion: 0.09
Nodes (61): api service (FastAPI/uvicorn backend), db service (PostgreSQL 16), ipam bridge network (192.0.2.0/24), redis service (Redis 7, appendonly), scanner service (arq worker, host networking), web service (Next.js frontend), Accounts & Roles, Insecure mode (IPAMBOX_ALLOW_INSECURE) (+53 more)

### Community 13 - "Discovery & Scans UI"
Cohesion: 0.11
Nodes (33): BulkResp, DataPage(), download(), FeatureDef, GROUPS, Key, Key, ConfirmAction() (+25 more)

### Community 14 - "Config & Migration Env"
Cohesion: 0.05
Nodes (49): do_run_migrations(), run_migrations_online(), close_arq_pool(), close_redis(), get_redis(), Shared process-wide Redis client. Do NOT aclose() it per call — connections…, Shut down the shared client — lifespan/worker shutdown only., lifespan() (+41 more)

### Community 15 - "Frontend Pages Misc"
Cohesion: 0.12
Nodes (56): CertificatesPage(), ChangelogPage(), CircuitsPage(), DevicesPage(), DeviceDetailClient(), DiscoveryPage(), ImportPage(), InventoryPage() (+48 more)

### Community 16 - "Reconcile Worker"
Cohesion: 0.08
Nodes (47): _flag(), Any, AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), HostResult, _global_vrf_id(), _infer_scan_vrf() (+39 more)

### Community 17 - "Workbook Service"
Cohesion: 0.08
Nodes (18): parse_sites_master_records(), _Planner, _preview(), (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Folded sheet title vs site name/code — word-boundary matching so 'int' doesn't…, Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new… (+10 more)

### Community 18 - "Demo Data Generator"
Cohesion: 0.09
Nodes (49): assets_rows(), _assign_site_sheets(), _assign_site_sheets_clean(), build_en_workbook(), build_mixed_workbook(), build_sites(), certificates_rows(), circuits_rows() (+41 more)

### Community 19 - "Workbook Import"
Cohesion: 0.08
Nodes (43): assemble_ip(), clean(), _clean_octets(), map_status(), mask_to_prefixlen(), network_of(), norm_header(), norm_mac() (+35 more)

### Community 20 - "Community 20"
Cohesion: 0.09
Nodes (42): download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, get, post, Request, Restore a backup file (raw .json.gz body). Wipes every data table (users are… (+34 more)

### Community 21 - "Community 21"
Cohesion: 0.10
Nodes (44): _asset_ref(), _check_iface_refs(), _check_refs(), create_device(), create_interface(), delete_device(), delete_interface(), _detail() (+36 more)

### Community 22 - "Community 22"
Cohesion: 0.09
Nodes (36): create_rule(), delete_rule(), get_rule(), list_rules(), preview_rule(), AsyncSession, delete, get (+28 more)

### Community 23 - "Community 23"
Cohesion: 0.10
Nodes (41): bulk_rows(), _check_columns(), create_list(), create_row(), delete_list(), delete_row(), get_list(), list_lists() (+33 more)

### Community 24 - "Community 24"
Cohesion: 0.08
Nodes (42): _audit(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession, BaseModel (+34 more)

### Community 25 - "Community 25"
Cohesion: 0.17
Nodes (40): auth_on(), _backup_bytes(), _cable(), _device(), _gen(), _iface(), _ip(), _login() (+32 more)

### Community 26 - "Community 26"
Cohesion: 0.09
Nodes (39): ArqRedis, backup_now(), Enqueue an immediate scheduled-style backup on the worker., _lan_info(), LAN identity detected by the host-networked worker (written to Redis). Falls…, get_arq_pool(), Shared ARQ pool — callers must not close() it per job., redis_settings_from_url() (+31 more)

### Community 27 - "Community 27"
Cohesion: 0.09
Nodes (31): CustomList, CustomListRow, User-defined table — preserves a workbook sheet's own shape (e.g. 'שרתים…, One row of a custom list — ``data`` maps column key -> string value., VRF naming convention: the site code, then site-N, then a name slug., slugify(), vrf_name_for(), _apply_list() (+23 more)

### Community 28 - "Community 28"
Cohesion: 0.10
Nodes (28): DocsIndexClient(), metadata, DocPage(), dynamicParams, generateMetadata(), loadMarkdown(), CommandPalette(), Icon (+20 more)

### Community 29 - "Community 29"
Cohesion: 0.08
Nodes (27): list_changelog(), AsyncSession, get, AsyncSession, get, stats(), CRUD routers for the workbook-imported entity families. Circuits, certificates,…, get_session() (+19 more)

### Community 31 - "Community 31"
Cohesion: 0.08
Nodes (28): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), _host_chunks(), _icmp_sweep(), infer_device_type(), _ptr_lookup() (+20 more)

### Community 32 - "Community 32"
Cohesion: 0.11
Nodes (35): CC0 1.0 Universal, netbox-community/devicetype-library, Rack device image library, IPAddress, Cable, connected_interface_id (structured far-end port link), connected_ip (host-side NIC binding), DeviceInterface (device-owned port) (+27 more)

### Community 33 - "Community 33"
Cohesion: 0.17
Nodes (31): _cable_out(), _check_ends(), create_cable(), delete_cable(), _get_cable(), _get_interface(), interfaces_match_free_text(), list_cables() (+23 more)

### Community 34 - "Community 34"
Cohesion: 0.11
Nodes (29): ReorderBody, reorder_devices(), reorder_items(), reorder_sites(), reorder_vlans(), create_vrf(), delete_vrf(), get_vrf() (+21 more)

### Community 35 - "Community 35"
Cohesion: 0.12
Nodes (35): _check_refs(), create_device(), create_rack(), delete_device(), delete_rack(), _device_out(), _devices(), _get_device() (+27 more)

### Community 36 - "Community 36"
Cohesion: 0.10
Nodes (34): canMount(), slotCount(), ABBREV_TO_CATEGORY, canonicalCategory(), CATEGORY_TO_ABBREV, clip(), compareVersions(), decodeShareUrl() (+26 more)

### Community 37 - "Community 37"
Cohesion: 0.12
Nodes (31): list_devices(), _crud_router(), create_item(), delete_item(), get_item(), list_items(), update_item(), _cascade_site_fields() (+23 more)

### Community 38 - "Community 38"
Cohesion: 0.12
Nodes (32): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+24 more)

### Community 39 - "Community 39"
Cohesion: 0.09
Nodes (27): cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession, get (+19 more)

### Community 40 - "Community 40"
Cohesion: 0.16
Nodes (33): _backup_bytes(), _envelope_bytes(), _mkusers(), User, Hand-craft a backup envelope (e.g. with a forged users table)., Guard: every ORM table must be backed up (or explicitly excluded). Adding a new…, Fresh-server scenario: the migration-seeded Global VRF is replaced by the…, Fresh-server scenario: the target's admins survive; its non-admin set is fully… (+25 more)

### Community 41 - "Community 41"
Cohesion: 0.13
Nodes (25): Rack elevations: racks + nested devices + Rackula import. Not a `_crud_router`…, str, RackFace, IpRef, NextFreeUOut, BaseModel, field_validator, RackCreate (+17 more)

### Community 42 - "Community 42"
Cohesion: 0.12
Nodes (29): _check_site(), create_rack_group(), delete_rack_group(), _get_group(), get_rack_group(), list_rack_groups(), _ordered_racks(), AsyncSession (+21 more)

### Community 43 - "Community 43"
Cohesion: 0.11
Nodes (31): ConflictError, apply_device_patch(), carrier_children(), CarrierError, _check_carrier_mount(), check_layout_change(), check_placement(), device_fields() (+23 more)

### Community 44 - "Community 44"
Cohesion: 0.16
Nodes (29): DeviceFormDialog(), DragSession, DropRow(), EditorBlock(), errDetail(), Pending, RackEditor(), CarrierFrameSvg() (+21 more)

### Community 45 - "Community 45"
Cohesion: 0.11
Nodes (22): _check_range_overlap(), create_range(), delete_range(), list_ranges(), AsyncSession, delete, get, post (+14 more)

### Community 46 - "Community 46"
Cohesion: 0.17
Nodes (27): _folded(), AsyncSession, get, Cross-object search for the command palette. One GET returns grouped matches…, Column expression with Hebrew final letters folded — pairs with fold_hebrew()…, Short label for a list-row search hit: key-column value, else the first non-…, _row_label(), search() (+19 more)

### Community 47 - "Community 47"
Cohesion: 0.10
Nodes (27): str, ScanJob, ScanStatus, Auto-purge rows past their configured retention (0 = keep forever). Mirrors the…, _retention_sweeps(), fake_arq(), _pool(), _FakeArqJob (+19 more)

### Community 48 - "Community 48"
Cohesion: 0.09
Nodes (16): CircuitCreate, CircuitOut, CircuitUpdate, BaseModel, field_validator, hex_color_or_none(), Shared row/tag color validator: #rrggbb, normalized to lowercase., field_validator (+8 more)

### Community 49 - "Community 49"
Cohesion: 0.22
Nodes (26): str, UserRole, auth_on(), fake_arq(), login(), mkuser(), other_client(), AsyncClient (+18 more)

### Community 50 - "Community 50"
Cohesion: 0.12
Nodes (12): _mklist(), Custom lists: CRUD + rows + IP resolution + workbook list-target import., v2 workbook: SRV2 edited, SRV3 added, SRV1 missing -> merge keeps SRV1, updates…, _servers_xlsx(), test_import_as_list_e2e(), test_manually_edited_row_wins_conflict(), test_reimport_merges_by_key(), TestBulkRows (+4 more)

### Community 51 - "Community 51"
Cohesion: 0.07
Nodes (29): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, js-yaml, jszip, lucide-react (+21 more)

### Community 52 - "Community 52"
Cohesion: 0.16
Nodes (26): update_range(), _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), AsyncSession (+18 more)

### Community 53 - "Community 53"
Cohesion: 0.10
Nodes (19): psycopg2-style URL for alembic offline mode / scripts., Settings, Effective, _env_sourced(), get_effective(), Any, AsyncSession, Runtime-editable settings: app_settings rows override env defaults. Each public… (+11 more)

### Community 54 - "Community 54"
Cohesion: 0.07
Nodes (26): name, private, version, autoprefixer, clsx, jszip, lz-string, postcss (+18 more)

### Community 55 - "Community 55"
Cohesion: 0.12
Nodes (17): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, _csv_sheet(), load_upload() (+9 more)

### Community 56 - "Community 56"
Cohesion: 0.17
Nodes (21): metadata, ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), collectExpandableKeys(), flattenTree() (+13 more)

### Community 57 - "Community 57"
Cohesion: 0.09
Nodes (11): parse_certificates(), Positional 5-col layout: platform, target/VS, server, cert, expiry., Workbook import: normalizer/parser unit tests (no DB) + API e2e., Small synthetic workbook: sites master + one site sheet + circuits., test_commit_twice_rejected(), test_import_e2e(), TestAssetsParser, TestCertificatesParser (+3 more)

### Community 58 - "Community 58"
Cohesion: 0.21
Nodes (13): _master_row(), _matrix(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind… (+5 more)

### Community 59 - "Community 59"
Cohesion: 0.18
Nodes (18): CableKind, InterfaceKind, str, CableCreate, CableEndOut, CableOut, CableTraceHop, CableUpdate (+10 more)

### Community 60 - "Community 60"
Cohesion: 0.13
Nodes (18): _cell_text(), extract_list_table(), _infer_type(), _ips(), _is_ip_token(), pick_key_column(), Custom-list extraction: turn any sheet into {columns, rows} for a list. Unlike…, SheetMatrix -> (column defs, row dicts). columns: [{key, label, type, options?,… (+10 more)

### Community 61 - "Community 61"
Cohesion: 0.11
Nodes (12): _blocks(), _col_class(), parse_site_sheet(), _positional_columns(), Split duplicated column groups (031-style runaway): each block starts at an…, Dominant content class of a column sample., Headerless sheet: locate the IP column, then assign the remaining canonical…, MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf. (+4 more)

### Community 62 - "Community 62"
Cohesion: 0.12
Nodes (17): _FakeRedis, _mk_job(), In-memory stand-in for the worker's redis client (get/set/publish)., Point the worker at the test DB (sf) and the fake redis client., Cancel flag polled between phases -> ScanCancelled -> CANCELLED, and no…, Audit race: API writes CANCELLED mid-scan while the redis flag is lost…, Cancel landing while reconcile writes rows: the flag + row re-check right…, A job already terminal when the worker picks it up is skipped — no RUNNING… (+9 more)

### Community 63 - "Community 63"
Cohesion: 0.13
Nodes (23): arrLen(), attribution(), CATEGORY_COLOUR, CURATED, fetchBuf(), fetchJson(), FRONTEND, FULL_IMPORT (+15 more)

### Community 64 - "Community 64"
Cohesion: 0.17
Nodes (20): _build_out(), _mask_url(), AsyncSession, get, Hide the password in a scheme://user:pass@host URL., read_settings(), update_settings(), ChangePasswordBody (+12 more)

### Community 65 - "Community 65"
Cohesion: 0.23
Nodes (20): assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession, delete (+12 more)

### Community 66 - "Community 66"
Cohesion: 0.16
Nodes (20): delete_scheduled_backup(), delete, _alembic_revisions(), backup_dir(), build_backup(), delete_backup_file(), list_backup_files(), prune_backups() (+12 more)

### Community 67 - "Community 67"
Cohesion: 0.27
Nodes (19): _login(), _mk_rule(), _mk_site(), _mkuser(), AsyncClient, AsyncSession, Global row colors: manual row_color + rule-computed display_color. Covers the…, test_backup_roundtrips_color_rules() (+11 more)

### Community 68 - "Community 68"
Cohesion: 0.28
Nodes (18): _circuit_order(), _login(), _mk_circuits(), _mkuser(), AsyncClient, AsyncSession, Global row ordering: POST /{entity}/reorder + pinned rows. Covered on both…, Reordering a subset keeps the slots those rows already had — rows outside the… (+10 more)

### Community 69 - "Community 69"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 70 - "Community 70"
Cohesion: 0.22
Nodes (17): _prefix(), export.csv takes the same filters as the list endpoint — a filtered view…, Same filtered-export treatment on the prefixes CSV (F8)., A documented v6 /64's 2^64 host count must not reach dashboard sums (~1.8e19 >…, test_address_role_nat_and_bulk(), test_addresses_export_respects_filters(), test_bulk_reports_real_counts(), test_container_move_with_children_rejected() (+9 more)

### Community 71 - "Community 71"
Cohesion: 0.17
Nodes (15): fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture, Every new Settings > Features key is runtime-editable; untouched keys keep the…, test_backup_files_report_effective_schedule() (+7 more)

### Community 72 - "Community 72"
Cohesion: 0.21
Nodes (12): CommitOptions, ListTarget, PreviewOptions, BaseModel, Per-sheet detection result shown in the wizard., Import a sheet as a custom list (user-selected or suggested)., User-confirmed mapping choices applied before building the plan., RowResult (+4 more)

### Community 73 - "Community 73"
Cohesion: 0.15
Nodes (15): AppearancePage(), PrefsInit(), AddrMapView, applyPrefs(), DEFAULT_PREFS, DensityChoice, FxLevel, Prefs (+7 more)

### Community 74 - "Community 74"
Cohesion: 0.19
Nodes (13): canPlace(), conflicts(), facesCollide(), freeSlots(), Placed, rangesOverlap(), SLOT_LAYOUTS, LibraryDevice (+5 more)

### Community 75 - "Community 75"
Cohesion: 0.16
Nodes (11): CABLE_KINDS, CableDialog(), fmtSpeed(), IFACE_KINDS, InterfacesPanel(), useDevicePick(), Cable, CableKind (+3 more)

### Community 76 - "Community 76"
Cohesion: 0.19
Nodes (8): _master_blocks(), parse_sites_master(), (first, second) octet pairs a master row declares — lets sheet->site matching…, Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins., TestSitesMasterParser

### Community 77 - "Community 77"
Cohesion: 0.23
Nodes (12): sf(), _mk_prefix(), test_address_crud_and_dup_guard(), test_allocation_skips_existing(), test_concurrent_allocation_unique(), alloc(), test_exhausted_prefix_conflicts(), test_sequential_allocation_skips_boundaries() (+4 more)

### Community 78 - "Community 78"
Cohesion: 0.23
Nodes (12): AsyncClient, tag_assignments.object_id has no FK — deleting a tagged object must drop its…, Tag.assignments is already ORM delete-orphan — each removed assignment lands in…, PATCH settings with a null value deletes the app_settings row — that delete…, /addresses/bulk action=delete used to issue one Core DELETE — invisible to the…, test_bulk_delete_writes_changelog_entries(), test_changelog_captures_ip_status_change(), test_changelog_records_crud() (+4 more)

### Community 79 - "Community 79"
Cohesion: 0.31
Nodes (12): AsyncClient, Global /api/v1/search endpoint (UX-3)., Regression: list_addresses ?q= used to crash on a missing column., Site + VRF + prefix + address + one of each workbook entity., _seed(), test_addresses_q_filter_not_broken(), test_search_empty_query(), test_search_grouped_results() (+4 more)

### Community 80 - "Community 80"
Cohesion: 0.27
Nodes (11): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), SyncSession, register(), _repr() (+3 more)

### Community 81 - "Community 81"
Cohesion: 0.29
Nodes (11): _as_date(), _as_str(), display_color_for(), _ordered_cmp(), Any, date, -1/0/1 comparing a column value to a rule's value string. Tries date first when…, Does ``rule`` fire on this row? NULL fields never match. (+3 more)

### Community 82 - "Community 82"
Cohesion: 0.33
Nodes (10): _global_vrf_id(), Splits are counted arithmetically before materializing: anything over…, test_overlap_same_vrf_rejected(), test_prefix_stats_fields(), test_prefixes_order_by_utilization_and_limit(), test_same_cidr_allowed_across_vrfs(), test_split_cardinality_cap(), test_split_endpoint() (+2 more)

### Community 83 - "Community 83"
Cohesion: 0.20
Nodes (8): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture, Stands in for the arq Redis pool — never actually dispatches work., scan_exclude_networks=10.70.0.64/26 inside scan_networks=10.70.0.0/24: the…, test_scheduler_and_route_share_exclusion_guard()

### Community 84 - "Community 84"
Cohesion: 0.20
Nodes (10): devDependencies, autoprefixer, postcss, sharp, tailwindcss, @types/js-yaml, @types/node, @types/react (+2 more)

### Community 85 - "Community 85"
Cohesion: 0.25
Nodes (6): DIR, FACES, LAYOUTS, problems, referenced, slugs

### Community 86 - "Community 86"
Cohesion: 0.25
Nodes (7): API sketch, Device detail, Devices, Devices vs racks, From the IP drawer, Health rollup, The list

### Community 87 - "Community 87"
Cohesion: 0.29
Nodes (6): Demo import data — ALL FICTIONAL, Files, `Network_Address_DEMO_EN.xlsx` — the edge-case workbook, `Network_Address_DEMO.xlsx` — the clean flagship, Regenerating, VLAN scheme (both workbooks + `demo-vlans.csv`)

### Community 88 - "Community 88"
Cohesion: 0.29
Nodes (7): scripts, build, build:rack-library, check:rack-library, dev, lint, start

### Community 89 - "Community 89"
Cohesion: 0.33
Nodes (7): errDetail(), findDevice(), GroupClient(), moveDevice(), freeByRack(), parseRowDev(), parseRowDrop()

### Community 91 - "Community 91"
Cohesion: 0.53
Nodes (5): moveRowNav(), G_CHORDS, isEditableTarget(), modalOpen(), useGlobalShortcuts()

### Community 92 - "Community 92"
Cohesion: 0.40
Nodes (3): קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., TestCircuitsParser

### Community 93 - "Community 93"
Cohesion: 0.50
Nodes (4): ChartTheme, FALLBACK, readTheme(), useChartTheme()

### Community 94 - "Community 94"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

## Ambiguous Edges - Review These
- `Cable` → `Rack`  [AMBIGUOUS]
  frontend/src/content/docs/cabling.md · relation: conceptually_related_to

## Knowledge Gaps
- **323 isolated node(s):** `SplitPlan`, `Row`, `SortKey`, `Crumb`, `CellState` (+318 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1072 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Cable` and `Rack`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `IPAddress` connect `Addresses API` to `Community 33`, `Prefixes API`, `Community 35`, `Changelog Core`, `Community 41`, `Test Fixtures`, `Rack Tests`, `Community 46`, `Community 47`, `Reconcile Worker`, `Community 50`, `Community 21`, `Community 23`, `Community 24`, `Community 26`, `Community 27`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Why does `react` connect `Frontend Pages` to `Frontend App Shell`, `Device Detail UI`, `Frontend Feature Pages`, `Changelog & Dashboard UI`, `Import Wizard UI`, `Community 73`, `Community 44`, `Discovery & Scans UI`, `Frontend Pages Misc`, `Community 54`, `Community 56`, `Community 91`, `Community 28`, `Community 93`, `Community 30`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Why does `User` connect `Community 20` to `Community 66`, `Community 67`, `Community 68`, `Addresses API`, `Community 38`, `Changelog Core`, `Auth API`, `Community 40`, `Test Fixtures`, `Rack Tests`, `Community 49`, `Community 23`, `Community 24`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 73 inferred relationships involving `IPAMError` (e.g. with `_check_interface_link()` and `create_address()`) actually correct?**
  _`IPAMError` has 73 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `IPAddress` (e.g. with `_device_out()` and `device_health()`) actually correct?**
  _`IPAddress` has 33 INFERRED edges - model-reasoned connections that need verification._
- **What connects `SplitPlan`, `Row`, `SortKey` to the rest of the system?**
  _323 weakly-connected nodes found - possible documentation gaps or missing edges._