# Graph Report - IpamBox  (2026-09-26)

## Corpus Check
- Large corpus: 2627 files · ~1,054,908 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder.

## Summary
- 5128 nodes · 16305 edges · 230 communities (133 shown, 58 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 1291 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
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
- Community 103
- Community 104
- Community 105
- Community 106
- Community 107
- Community 108
- Community 109
- Community 110
- Community 111
- Community 112
- Community 113
- Community 114
- Community 115
- Community 116
- Community 117
- Community 118
- Community 119
- Community 120
- Community 121
- Community 122
- Community 123
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
- Community 168
- Community 169
- Community 170
- Community 172
- Community 173
- Community 174
- Community 175
- Community 176
- Community 177
- Community 178
- Community 179
- Community 181
- Community 182
- Community 184
- Community 186
- Community 187
- Community 188
- Community 190
- Community 191
- Community 193
- Community 194
- Community 195
- Community 196
- Community 197
- Community 198
- Community 199
- Community 201
- Community 202
- Community 203
- Community 204
- Community 205
- Community 206
- Community 207
- Community 208
- Community 209
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

## God Nodes (most connected - your core abstractions)
1. `cn()` - 170 edges
2. `react` - 140 edges
3. `Device` - 107 edges
4. `IPAMError` - 99 edges
5. `get_or_404()` - 86 edges
6. `useAsyncData()` - 84 edges
7. `lucide-react` - 80 edges
8. `IPAddress` - 75 edges
9. `useAuth()` - 73 edges
10. `get_settings()` - 71 edges

## Surprising Connections (you probably didn't know these)
- `SNMP Pull inventory` --semantically_similar_to--> `Inventory sync (Pull inventory)`  [INFERRED] [semantically similar]
  README.md → frontend/src/content/docs/snmp.md
- `CSV export` --semantically_similar_to--> `Address CSV import/export (UTF-8 BOM)`  [INFERRED] [semantically similar]
  frontend/src/content/docs/devices.md → README.md
- `Export dropdown (Devices toolbar)` --semantically_similar_to--> `Device smart file I/O (export dropdown + smart import)`  [INFERRED] [semantically similar]
  frontend/src/content/docs/devices.md → README.md
- `Smart import dialog` --semantically_similar_to--> `Excel workbook import (per-sheet detection, dry-run, all-or-nothing/partial commit)`  [INFERRED] [semantically similar]
  frontend/src/content/docs/devices.md → README.md
- `Secrets-at-rest contract` --semantically_similar_to--> `Encrypted channel secrets`  [INFERRED] [semantically similar]
  frontend/src/content/docs/monitoring.md → README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Documented vs discovered network sync loop** — readme_ipambox, readme_ipam_hierarchy, readme_scanner, readme_discovery_inbox, readme_review_center [EXTRACTED 0.90]
- **Pull inventory writes VLANs/prefixes/addresses with snmp provenance** — frontend_src_content_docs_snmp_inventory_sync, readme_vlans, frontend_src_content_docs_subnets_prefix, frontend_src_content_docs_addresses_ip_address, frontend_src_content_docs_snmp_import_batch [EXTRACTED 0.90]
- **IpamBox docker-compose service stack** — dockercompose_web, dockercompose_api, dockercompose_scanner, dockercompose_db, dockercompose_redis [EXTRACTED 0.95]
- **Core IPAM hierarchy: Site → VRF → Prefix → IP address** — sites_feature, vrfs_feature, overview_data_model [EXTRACTED 1.00]
- **Scan → reconcile → discovery inbox → address statuses** — scans_feature, scans_pipeline, discovery_feature [EXTRACTED 1.00]
- **Shared backend image (api + worker deps)** — dockercompose_api, dockercompose_scanner, backend_requirements_arq, backend_requirements_scapy, backend_requirements_pysnmp, backend_requirements_sqlalchemy [INFERRED 0.75]
- **Preview → one-transaction apply import pattern** — readme_workbook_importer, frontend_src_content_docs_snmp_inventory_sync, frontend_src_content_docs_racks_smart_bundle, frontend_src_content_docs_snmp_import_batch [INFERRED 0.75]
- **Rack tree bundle (group → racks → devices → interfaces/cables)** — frontend_src_content_docs_racks_rack_group, frontend_src_content_docs_racks_rack, readme_device_inventory, frontend_src_content_docs_racks_smart_bundle [INFERRED 0.75]

## Communities (230 total, 58 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.09
Nodes (92): CertificatesPage(), EMPTY, CircuitsPage(), EMPTY, DEVICE_VIEWS, DeviceRow, DevicesPage(), EMPTY (+84 more)

### Community 1 - "Community 1"
Cohesion: 0.03
Nodes (97): ArqRedis, do_run_migrations(), run_migrations_online(), cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), list_scans() (+89 more)

### Community 2 - "Community 2"
Cohesion: 0.02
Nodes (42): nextConfig, metadata, metadata, metadata, metadata, metadata, metadata, metadata (+34 more)

### Community 3 - "Community 3"
Cohesion: 0.05
Nodes (94): allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes(), get_prefix(), list_prefixes(), prefix_addresses(), _prefix_rows() (+86 more)

### Community 4 - "Community 4"
Cohesion: 0.05
Nodes (99): _asset_ref(), _check_iface_refs(), _check_refs(), create_device(), create_interface(), delete_device(), delete_interface(), _detail() (+91 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (63): BulkResp, CABLE_REASON, DELETE_PATH, DeleteTarget, DismissTarget, SECTION_ICONS, WhyCell(), Draft (+55 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (85): hash_password(), _circuit_order(), _login(), _mk_circuits(), _mkuser(), AsyncClient, AsyncSession, Global row ordering: POST /{entity}/reorder + pinned rows. Covered on both… (+77 more)

### Community 7 - "Community 7"
Cohesion: 0.05
Nodes (80): import_racks(), Request, Smart rack/group bundle import — V5B's stateless flow for whole trees. Sheets…, Rack, RackGroup, A bayed row: racks ordered left-to-right as they stand in the DC., A physical rack/cabinet at a site — devices take placement in it., _alias_to_field() (+72 more)

### Community 8 - "Community 8"
Cohesion: 0.04
Nodes (69): ACTION_STYLES, ChangelogPage(), ACTION_STYLES, CABLE_REASON, DashboardPage(), DeviceDetailClient(), EMPTY_EDIT, FACE_BADGE (+61 more)

### Community 9 - "Community 9"
Cohesion: 0.05
Nodes (79): DeviceFormDialog(), DragSession, DropRow(), EditorBlock(), errDetail(), Pending, RackEditor(), CarrierFrameSvg() (+71 more)

### Community 10 - "Community 10"
Cohesion: 0.07
Nodes (75): Device, _device(), _down(), _enable(), _iface(), _ifrow(), _ip(), _link_binds() (+67 more)

### Community 11 - "Community 11"
Cohesion: 0.05
Nodes (81): delete_scheduled_backup(), download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, delete, get, post (+73 more)

### Community 12 - "Community 12"
Cohesion: 0.06
Nodes (67): IpCell(), SortableColRow(), IP_ROLES, IP_STATUSES, RANGE_ROLES, SplitDialog(), SplitPlan, AddressFilterPanel() (+59 more)

### Community 13 - "Community 13"
Cohesion: 0.06
Nodes (74): AsyncClient, auth_on(), _bare_device(), _clean_walk(), _device(), _enable(), _ip(), key() (+66 more)

### Community 14 - "Community 14"
Cohesion: 0.06
Nodes (54): _job_payload(), healthz(), metrics(), get, Request, Prometheus-style text exposition of object + scan counters., Readiness probe: verifies DB + Redis connectivity., readyz() (+46 more)

### Community 15 - "Community 15"
Cohesion: 0.04
Nodes (73): metadata, ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), collectExpandableKeys(), flattenTree() (+65 more)

### Community 16 - "Community 16"
Cohesion: 0.09
Nodes (64): _apply_link_state(), _clear_unmanaged_flag(), _decode(), ensure(), _flag_unmanaged(), handle_trap(), datetime, _resolve_device() (+56 more)

### Community 17 - "Community 17"
Cohesion: 0.04
Nodes (65): metadata, viewport, AppearancePage(), AppShell(), AUTH_ROUTES, isActive(), NAV_FLAT, NAV_GROUPS (+57 more)

### Community 18 - "Community 18"
Cohesion: 0.09
Nodes (52): ImportListDialog(), IPAM_FAMILIES, Step, LabelClient(), FACE_BADGE, FACE_BADGE, KINDS, MonitorDialog() (+44 more)

### Community 19 - "Community 19"
Cohesion: 0.06
Nodes (61): confirm_discovered(), ConfirmBody, list_discovered(), AsyncSession, BaseModel, get, post, Unconfirmed hosts found by scanners, pending admin review. No limit -> the full… (+53 more)

### Community 20 - "Community 20"
Cohesion: 0.07
Nodes (69): _check_refs(), create_device(), create_rack(), delete_device(), delete_rack(), _device_out(), _devices(), _export_name() (+61 more)

### Community 21 - "Community 21"
Cohesion: 0.07
Nodes (67): _cable_out(), _check_ends(), create_cable(), delete_cable(), _get_cable(), _get_interface(), interfaces_match_free_text(), list_cables() (+59 more)

### Community 22 - "Community 22"
Cohesion: 0.07
Nodes (67): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+59 more)

### Community 23 - "Community 23"
Cohesion: 0.07
Nodes (60): _crud_router(), create_item(), delete_item(), get_item(), list_items(), reorder_items(), update_item(), update_row() (+52 more)

### Community 24 - "Community 24"
Cohesion: 0.08
Nodes (54): Device, Base, str, RackFace, apply_device_import(), _carrier_diff_name(), _err(), _find_carrier() (+46 more)

### Community 25 - "Community 25"
Cohesion: 0.09
Nodes (61): api service (FastAPI/uvicorn backend), db service (PostgreSQL 16), ipam bridge network (192.0.2.0/24), redis service (Redis 7, appendonly), scanner service (arq worker, host networking), web service (Next.js frontend), Accounts & Roles, Insecure mode (IPAMBOX_ALLOW_INSECURE) (+53 more)

### Community 26 - "Community 26"
Cohesion: 0.07
Nodes (41): list_changelog(), AsyncSession, get, assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments() (+33 more)

### Community 27 - "Community 27"
Cohesion: 0.07
Nodes (47): assemble_ip(), clean(), _clean_octets(), excel_date(), map_status(), mask_to_prefixlen(), network_of(), norm_header() (+39 more)

### Community 28 - "Community 28"
Cohesion: 0.05
Nodes (37): _FakeArqPool, _Job, _login(), _mk_device(), _mk_prefix_and_addr(), _mkuser(), V7 monitoring + notification channels. Covers target CRUD/RBAC, the exactly-…, Viewer reads targets but can't write/check/delete them. (+29 more)

### Community 29 - "Community 29"
Cohesion: 0.07
Nodes (34): IPRole, str, DeviceInterfaceCreate, DeviceInterfaceUpdate, field_validator, _strip_name(), DeviceCreate, DeviceUpdate (+26 more)

### Community 30 - "Community 30"
Cohesion: 0.09
Nodes (16): _Planner, (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Folded sheet title vs site name/code — word-boundary matching so 'int' doesn't…, Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new…, Resolve a 10.{second}.x sheet — site_number is only meaningful inside the…, A declared octet block claims the sheet — unless its site is inactive, in which… (+8 more)

### Community 31 - "Community 31"
Cohesion: 0.09
Nodes (49): assets_rows(), _assign_site_sheets(), _assign_site_sheets_clean(), build_en_workbook(), build_mixed_workbook(), build_sites(), certificates_rows(), circuits_rows() (+41 more)

### Community 32 - "Community 32"
Cohesion: 0.12
Nodes (43): _auth(), _context(), _cred(), _get(), _idx_inet(), _idx_int(), _idx_tail_ints(), _index_suffix() (+35 more)

### Community 33 - "Community 33"
Cohesion: 0.08
Nodes (28): CRUD routers for the workbook-imported entity families. Circuits, certificates,…, AssetKind, str, AssetCreate, AssetOut, AssetUpdate, BaseModel, field_validator (+20 more)

### Community 34 - "Community 34"
Cohesion: 0.24
Nodes (42): poll_device(), _cable(), _commit_fresh(), _device(), _enable(), _flag(), _fresh_iface(), _iface() (+34 more)

### Community 35 - "Community 35"
Cohesion: 0.09
Nodes (36): create_rule(), delete_rule(), get_rule(), list_rules(), preview_rule(), AsyncSession, delete, get (+28 more)

### Community 36 - "Community 36"
Cohesion: 0.11
Nodes (41): bulk_rows(), _check_columns(), create_list(), create_row(), delete_list(), delete_row(), get_list(), list_lists() (+33 more)

### Community 37 - "Community 37"
Cohesion: 0.10
Nodes (41): check_now(), _check_refs(), create_target(), delete_target(), _filters(), _get(), get_target(), list_targets() (+33 more)

### Community 38 - "Community 38"
Cohesion: 0.15
Nodes (42): _backup_bytes(), _cable(), _device(), _gen(), _iface(), _ip(), _panel_path(), _prefix() (+34 more)

### Community 39 - "Community 39"
Cohesion: 0.16
Nodes (42): _bundle(), _by_sheet(), _cable(), _csv(), _device(), _group(), _iface(), _import() (+34 more)

### Community 40 - "Community 40"
Cohesion: 0.14
Nodes (38): _cable(), _device(), _group(), _iface(), _ip(), _login(), _mkuser(), _prefix() (+30 more)

### Community 41 - "Community 41"
Cohesion: 0.09
Nodes (36): _data_key(), decrypt_str(), encrypt_str(), _master_key(), Exception, Secrets at rest — the credential contract v7/v8/v12/v14 build on. A single…, Unseal a "v1:…" blob. Strict prefix check — unknown formats, malformed payloads…, Base for secrets-service failures — never carries secret material. (+28 more)

### Community 42 - "Community 42"
Cohesion: 0.09
Nodes (39): _address_csv_row(), _addresses_stmt(), bulk_addresses(), BulkBody, _check_interface_link(), create_address(), delete_address(), export_addresses() (+31 more)

### Community 43 - "Community 43"
Cohesion: 0.10
Nodes (37): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), preview_import(), AsyncSession, delete (+29 more)

### Community 44 - "Community 44"
Cohesion: 0.10
Nodes (35): set_actor(), Effective, get_effective(), AsyncSession, Scan-target policy shared by the API route, the scheduler, and the worker.…, monitor_tick(), ARQ job: check a batch of targets, write states, emit on flips., Every-minute cron beside scheduler_tick: batch due targets into a single sweep… (+27 more)

### Community 45 - "Community 45"
Cohesion: 0.09
Nodes (36): PrefixDetailPage(), toggleIn(), DEVICE_FILTER_PARAMS, DEVICE_TEXT_PARAMS, DeviceFilterPanel(), DeviceFilterState, DeviceTextParam, FACES (+28 more)

### Community 46 - "Community 46"
Cohesion: 0.08
Nodes (31): Exception, Raised inside the pipeline when the user cancels the scan., ScanCancelled, _job_status(), _publish(), Re-read the job row's status — the session's `job` instance goes stale the…, ARQ job: execute a scan and reconcile results., run_scan() (+23 more)

### Community 48 - "Community 48"
Cohesion: 0.11
Nodes (34): alembic==1.14.0, arq==0.26.1, asyncpg==0.30.0, bcrypt==4.3.0, cryptography==50.0.1, fastapi==0.115.6, httpx==0.28.1, psutil==6.1.0 (+26 more)

### Community 49 - "Community 49"
Cohesion: 0.10
Nodes (27): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., sf() (+19 more)

### Community 50 - "Community 50"
Cohesion: 0.11
Nodes (27): DocsIndexClient(), metadata, DocPage(), dynamicParams, generateMetadata(), loadMarkdown(), CommandPalette(), Icon (+19 more)

### Community 51 - "Community 51"
Cohesion: 0.10
Nodes (32): NotificationChannel, NotificationLog, Base, Outbound sink. ``config`` holds non-secret fields per kind; ``secret_enc`` is…, Append-only delivery attempt log — swept by ``notify_retention_days``., _deliver(), _DeliveryFailed, emit() (+24 more)

### Community 52 - "Community 52"
Cohesion: 0.20
Nodes (34): _csv(), _device(), _group(), _import(), _ip(), _login(), _mkuser(), _prefix() (+26 more)

### Community 53 - "Community 53"
Cohesion: 0.20
Nodes (35): _device(), _flag_mismatch(), _iface(), _ip(), _login(), _mkuser(), _prefix(), AsyncClient (+27 more)

### Community 54 - "Community 54"
Cohesion: 0.11
Nodes (33): _check_site(), create_rack_group(), delete_rack_group(), export_rack_group_xlsx(), _get_group(), get_rack_group(), list_rack_groups(), _ordered_racks() (+25 more)

### Community 55 - "Community 55"
Cohesion: 0.14
Nodes (33): ip_display(), Any, Normalize asyncpg-returned ipaddress objects / strings to display form. INET…, to_int(), _aging_discovery_items(), build_review(), _cable_mismatch_items(), _cert_items() (+25 more)

### Community 56 - "Community 56"
Cohesion: 0.10
Nodes (31): _flag(), Any, AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), HostResult, reconcile raising a mac_mismatch flag emits once; a follow-up scan that leaves…, test_mac_mismatch_emits_once() (+23 more)

### Community 57 - "Community 57"
Cohesion: 0.10
Nodes (27): Api, apply(), _device_payload(), emit_zip(), find_one(), _KeepMethodRedirect, layout_doc(), main() (+19 more)

### Community 58 - "Community 58"
Cohesion: 0.16
Nodes (29): _folded(), AsyncSession, get, Cross-object search for the command palette. One GET returns grouped matches…, Column expression with Hebrew final letters folded — pairs with fold_hebrew()…, Short label for a list-row search hit: key-column value, else the first non-…, _row_label(), search() (+21 more)

### Community 59 - "Community 59"
Cohesion: 0.09
Nodes (29): _arp_scan(), _host_chunks(), _icmp_checksum(), _icmp_echo_packet(), _icmp_socket(), _icmp_sweep(), _icmp_sweep_blocking(), infer_device_type() (+21 more)

### Community 60 - "Community 60"
Cohesion: 0.16
Nodes (32): _backup_bytes(), _envelope_bytes(), _mkusers(), Hand-craft a backup envelope (e.g. with a forged users table)., Guard: every ORM table must be backed up (or explicitly excluded). Adding a new…, Fresh-server scenario: the migration-seeded Global VRF is replaced by the…, Fresh-server scenario: the target's admins survive; its non-admin set is fully…, A backup carrying an assignment for a missing object (e.g. taken while orphans… (+24 more)

### Community 61 - "Community 61"
Cohesion: 0.09
Nodes (25): metadata, EdgePopup, TopologyClient(), buildTree(), DeviceNodeData, elk, ELK_OPTIONS, ElkChild (+17 more)

### Community 62 - "Community 62"
Cohesion: 0.15
Nodes (14): _master_row(), _matrix(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind… (+6 more)

### Community 63 - "Community 63"
Cohesion: 0.11
Nodes (26): exclusion_hit(), Return the first excluded CIDR overlapping ``net`` (either direction), or None.…, _global_vrf_id(), _infer_scan_vrf(), Pick the VRF for a scan that didn't specify one. An exact-match prefix living…, _resolve_prefix(), _scan_vrf(), WorkerSettings (+18 more)

### Community 64 - "Community 64"
Cohesion: 0.07
Nodes (28): name, private, version, DocsContent(), autoprefixer, clsx, lz-string, postcss (+20 more)

### Community 65 - "Community 65"
Cohesion: 0.06
Nodes (31): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, elkjs, js-yaml, jszip (+23 more)

### Community 66 - "Community 66"
Cohesion: 0.18
Nodes (26): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+18 more)

### Community 67 - "Community 67"
Cohesion: 0.09
Nodes (24): _apply_link_state(), _clear_unmanaged_flag(), _decode(), ensure(), _flag_unmanaged(), handle_trap(), SNMP trap receiver (V8.1) — near-realtime link state. The poll lane…, (transportDomain, transportAddress) -> the sender's IP string. asyncio's UDP… (+16 more)

### Community 68 - "Community 68"
Cohesion: 0.12
Nodes (27): dismiss_item(), _flagged_address(), get_review(), mac_mismatch_accept(), mac_mismatch_keep(), AsyncSession, get, IPAddress (+19 more)

### Community 69 - "Community 69"
Cohesion: 0.13
Nodes (25): ChannelKind, MonitorKind, MonitorState, V7 — continuous monitoring targets + outbound notification channels., ChannelCreate, ChannelOut, ChannelTestOut, ChannelUpdate (+17 more)

### Community 70 - "Community 70"
Cohesion: 0.12
Nodes (28): apply_device_patch(), carrier_children(), CarrierError, _check_carrier_mount(), check_layout_change(), check_placement(), _faces_collide(), find_free_u() (+20 more)

### Community 71 - "Community 71"
Cohesion: 0.13
Nodes (28): IP address, Changelog bypass for state writes, Users & Roles console, Add network wizard, container prefix status, Subnets doc, Gateway & DNS technical rows, GiST exclusion constraint (within-VRF overlap) (+20 more)

### Community 72 - "Community 72"
Cohesion: 0.15
Nodes (20): apply_plan(), build_plan(), collect_inventory(), _fold(), inventory_fingerprint(), new_batch(), Plan, _plan_addresses() (+12 more)

### Community 73 - "Community 73"
Cohesion: 0.16
Nodes (26): _prefix(), _range(), export.csv takes the same filters as the list endpoint — a filtered view…, Same filtered-export treatment on the prefixes CSV (F8)., A documented v6 /64's 2^64 host count must not reach dashboard sums (~1.8e19 >…, A deliberate bulk import documents existing reality — statics inside pools land…, test_address_role_nat_and_bulk(), test_addresses_export_respects_filters() (+18 more)

### Community 74 - "Community 74"
Cohesion: 0.08
Nodes (13): Workbook import: normalizer/parser unit tests (no DB) + API e2e., Small synthetic workbook: sites master + one site sheet + circuits., Site sheet documenting a DHCP span AND static stations inside it — the real…, Pool-guard regression: committing a plan whose dhcp range covers documented…, test_commit_twice_rejected(), test_import_e2e(), test_workbook_statics_inside_dhcp_span_import_marked(), TestAssetsParser (+5 more)

### Community 75 - "Community 75"
Cohesion: 0.11
Nodes (21): DragSession, errDetail(), findDevice(), GroupClient(), moveDevice(), metadata, parseRowDev(), parseRowDrop() (+13 more)

### Community 76 - "Community 76"
Cohesion: 0.11
Nodes (23): close_arq_pool(), close_redis(), Shut down the shared client — lifespan/worker shutdown only., lifespan(), shutdown(), auth_on(), AsyncClient, fixture (+15 more)

### Community 77 - "Community 77"
Cohesion: 0.28
Nodes (24): str, UserRole, Viewer tier can read lists/rows but every mutation is 403., TestPermissions, login(), mkuser(), other_client(), AsyncClient (+16 more)

### Community 78 - "Community 78"
Cohesion: 0.10
Nodes (25): pysnmp==7.1.29, Demo import data — ALL FICTIONAL, demo_rack_dc.py, Demo .Rackula.zip rack layouts, /devices/import endpoint, Examples README (demo import data), Files, `Network_Address_DEMO_EN.xlsx` — the edge-case workbook (+17 more)

### Community 79 - "Community 79"
Cohesion: 0.09
Nodes (24): Accounts & role-based access control, Expiry tracking (badge, certs_expiring_30d dashboard count), Certificates — expiry tracking register, Circuits — WAN circuit register, Circuit fields (line type, Bezeq circuit ID, WAN IP, is_retired), Discovery Inbox — reconciliation queue, Hierarchy tree (/tree) — Site→VRF→Prefix, Tree navigation (click-to-prefix, session expand state) (+16 more)

### Community 80 - "Community 80"
Cohesion: 0.22
Nodes (20): get_layout(), put_layout(), AsyncSession, topology_graph(), DiagramLayout, Base, DiagramLayoutOut, DiagramLayoutPut (+12 more)

### Community 81 - "Community 81"
Cohesion: 0.15
Nodes (23): arq==0.26.1, bcrypt==4.3.0, cryptography==50.0.1, fastapi==0.115.6, pysnmp==7.1.29, redis==5.2.0, scapy==2.6.1, sqlalchemy[asyncio]==2.0.36 (+15 more)

### Community 82 - "Community 82"
Cohesion: 0.13
Nodes (23): arrLen(), attribution(), CATEGORY_COLOUR, CURATED, fetchBuf(), fetchJson(), FRONTEND, FULL_IMPORT (+15 more)

### Community 83 - "Community 83"
Cohesion: 0.20
Nodes (20): _config_fields(), create_channel(), delete_channel(), _get(), get_channel(), list_channels(), notification_log(), _out() (+12 more)

### Community 84 - "Community 84"
Cohesion: 0.14
Nodes (17): AppSetting, Runtime-editable setting override. Absent row -> env var -> default., fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture (+9 more)

### Community 85 - "Community 85"
Cohesion: 0.15
Nodes (15): _cell_text(), extract_list_table(), _infer_type(), _ips(), _is_ip_token(), pick_key_column(), Custom-list extraction: turn any sheet into {columns, rows} for a list. Unlike…, SheetMatrix -> (column defs, row dicts). columns: [{key, label, type, options?,… (+7 more)

### Community 86 - "Community 86"
Cohesion: 0.12
Nodes (17): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, PreviewResp, SheetResults(), Step (+9 more)

### Community 87 - "Community 87"
Cohesion: 0.11
Nodes (18): AUTH_PROTOS, EMPTY_CRED, PRIV_PROTOS, SnmpCard(), VERSIONS, ACTION_STYLE, APPLYABLE, fmt() (+10 more)

### Community 88 - "Community 88"
Cohesion: 0.27
Nodes (19): _login(), _mk_rule(), _mk_site(), _mkuser(), AsyncClient, AsyncSession, Global row colors: manual row_color + rule-computed display_color. Covers the…, test_backup_roundtrips_color_rules() (+11 more)

### Community 89 - "Community 89"
Cohesion: 0.16
Nodes (20): Demo CSV files, Fictional demo dataset, Demo import data README, Demo list CSVs (contacts/vlans/servers), Demo VLAN scheme, Network_Address_DEMO.xlsx, Network_Address_DEMO_EN.xlsx, backend/app/services/workbook parser (+12 more)

### Community 90 - "Community 90"
Cohesion: 0.22
Nodes (20): Address status lifecycle (active/reserved/dhcp/discovered/offline), Check kinds (ping/tcp/http), Monitoring doc (V7), Event sources, down_after hysteresis, Deliberate limits, Monitor target, Notification channel (+12 more)

### Community 91 - "Community 91"
Cohesion: 0.22
Nodes (18): _addrs(), _global_vrf_id(), _mkprefix(), Splits are counted arithmetically before materializing: anything over…, test_gateway_clear_removes_only_pristine_row(), test_gateway_never_clobbers_manual_row(), test_gateway_validation(), test_next_ip_never_hands_out_gateway() (+10 more)

### Community 92 - "Community 92"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 93 - "Community 93"
Cohesion: 0.14
Nodes (18): POST /api/v1/devices/import, Carrier two-pass mounting, Changelog / audit history, Dry-run preview with per-row {field:[old,new]} diffs, force commit mode (valid rows only), Header auto-mapping (English/Hebrew/NetBox), IP address, IP linking: existing addresses only, never creates (+10 more)

### Community 94 - "Community 94"
Cohesion: 0.23
Nodes (16): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+8 more)

### Community 95 - "Community 95"
Cohesion: 0.20
Nodes (10): _ip(), NetworkCreate, NetworkDhcpRange, NetworkOut, NetworkPrefix, NetworkVlanNew, BaseModel, field_validator (+2 more)

### Community 96 - "Community 96"
Cohesion: 0.24
Nodes (16): may_write(), Field-ownership check for source-stamped rows (ip_addresses et al.). True when…, _mk_prefix(), V6 provenance — ip_addresses.source: stamping, ownership, filtering. Every…, Manual and imported rows keep their provenance when a scan sees them — observed…, Response bodies carry `source` but never any *_enc-style field., test_csv_import_stamps_import(), test_export_filters_and_carries_source() (+8 more)

### Community 97 - "Community 97"
Cohesion: 0.18
Nodes (15): _apply_list(), execute_plan(), rep(), _get_or_create_list(), _get_or_create_prefix(), _get_or_create_site(), _get_or_create_vlan(), _get_or_create_vrf() (+7 more)

### Community 98 - "Community 98"
Cohesion: 0.17
Nodes (8): _blocks(), parse_site_sheet(), Split duplicated column groups (031-style runaway): each block starts at an…, MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf., Bare 'Name' (Cellular) maps to the hostname field., Non-empty unnamed columns pile into cf['extra'] instead of vanishing (Pelephone…, TestSiteSheetExtras, TestSiteSheetParser

### Community 99 - "Community 99"
Cohesion: 0.21
Nodes (3): _mklist(), TestListCRUD, TestRows

### Community 100 - "Community 100"
Cohesion: 0.24
Nodes (16): IPAddress, Cable, connected_interface_id (structured far-end port link), connected_ip (host-side NIC binding), DeviceInterface (device-owned port), L1 trace (cable path walk), match-free-text transition endpoint, One-cable-per-interface rule (+8 more)

### Community 101 - "Community 101"
Cohesion: 0.19
Nodes (16): Carrier (shelf/tray slot layout), Device image library, Elevation editor, Find free U, Health overlay, Linked asset and IP address, Rack placement rules, Printing and QR labels (+8 more)

### Community 102 - "Community 102"
Cohesion: 0.17
Nodes (9): _master_blocks(), parse_sites_master(), (first, second) octet pairs a master row declares — lets sheet->site matching…, parse_sites_master_records(), Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins. (+1 more)

### Community 103 - "Community 103"
Cohesion: 0.25
Nodes (14): auth_on(), AsyncClient, fixture, Global /api/v1/search endpoint (UX-3)., Regression: list_addresses ?q= used to crash on a missing column., Site + VRF + prefix + address + one of each workbook entity., _seed(), test_addresses_q_filter_not_broken() (+6 more)

### Community 104 - "Community 104"
Cohesion: 0.20
Nodes (14): openpyxl==3.1.5, demo-addresses.csv, Network_Address_DEMO.xlsx, Network_Address_DEMO_EN.xlsx, generate_demo_data.py, Address source provenance field, import_batch_id provenance, Rack XLSX bundle export/import (+6 more)

### Community 105 - "Community 105"
Cohesion: 0.24
Nodes (11): _load_sheets(), _csv_sheet(), load_upload(), load_workbook_bytes(), XLSX/CSV -> sheet matrices (openpyxl read_only streams / csv module)., Drop fully-empty trailing rows/cols for a stable matrix shape., One CSV file -> one SheetMatrix named after the file stem. utf-8-sig first…, Dispatch on container type: ZIP -> xlsx workbook; otherwise try CSV text… (+3 more)

### Community 106 - "Community 106"
Cohesion: 0.31
Nodes (11): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), Audit trail via session flush hooks. before_flush collects (object, action,…, register(), _repr() (+3 more)

### Community 107 - "Community 107"
Cohesion: 0.23
Nodes (12): AsyncClient, tag_assignments.object_id has no FK — deleting a tagged object must drop its…, Tag.assignments is already ORM delete-orphan — each removed assignment lands in…, PATCH settings with a null value deletes the app_settings row — that delete…, /addresses/bulk action=delete used to issue one Core DELETE — invisible to the…, test_bulk_delete_writes_changelog_entries(), test_changelog_captures_ip_status_change(), test_changelog_records_crud() (+4 more)

### Community 108 - "Community 108"
Cohesion: 0.26
Nodes (9): Custom lists: CRUD + rows + IP resolution + workbook list-target import., v2 workbook: SRV2 edited, SRV3 added, SRV1 missing -> merge keeps SRV1, updates…, _servers_xlsx(), test_import_as_list_e2e(), test_manually_edited_row_wins_conflict(), test_reimport_merges_by_key(), TestBulkRows, TestCsvImport (+1 more)

### Community 109 - "Community 109"
Cohesion: 0.21
Nodes (8): on_hosts fires once per detection step with that chunk's new IPs — ARP batch…, When L2+L3 find nothing, the TCP fallback publishes its batch too., test_scan_cidr_emits_found_deltas(), fake_icmp(), fake_probe(), fake_ptr(), on_hosts(), test_scan_cidr_tcp_fallback_reports_found()

### Community 110 - "Community 110"
Cohesion: 0.23
Nodes (11): Air-gap safe bundling, frontend/scripts/build-rack-library.mjs, CC0 1.0 Universal license, CC0 1.0 Universal, netbox-community/devicetype-library, Rack library ATTRIBUTION, netbox-community/devicetype-library, Rack device image library (+3 more)

### Community 111 - "Community 111"
Cohesion: 0.31
Nodes (9): Any, Any, _v_bool(), _v_cidr_list(), _v_float(), _v_int(), check(), _v_port_list() (+1 more)

### Community 112 - "Community 112"
Cohesion: 0.18
Nodes (4): _FakeRedis, In-memory get/set/publish stand-in for the worker's redis client., A scan that raises mid-job flips to FAILED and emits scan.failed., test_scan_failed_emits()

### Community 113 - "Community 113"
Cohesion: 0.20
Nodes (8): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture, Stands in for the arq Redis pool — never actually dispatches work., scan_exclude_networks=10.70.0.64/26 inside scan_networks=10.70.0.0/24: the…, test_scheduler_and_route_share_exclusion_guard()

### Community 114 - "Community 114"
Cohesion: 0.31
Nodes (9): check_target(), _http(), _ping(), AsyncClient, Semaphore, The monitor lane — per-target health checks on the worker's minute cron.…, Single-host ICMP echo — blocking ping/raw socket in a worker thread. uvloop…, Run one check -> (ok, error). `client` lets the sweep share one AsyncClient… (+1 more)

### Community 115 - "Community 115"
Cohesion: 0.20
Nodes (10): devDependencies, autoprefixer, postcss, sharp, tailwindcss, @types/js-yaml, @types/node, @types/react (+2 more)

### Community 116 - "Community 116"
Cohesion: 0.22
Nodes (10): GET /api/v1/devices/export.csv, GET /api/v1/devices/export.xlsx, CSV export, Export dropdown (Devices toolbar), Filtered-set export parity (devices-filtered.*), Filter facets as URL params, Export column round-trip contract, UTF-8 BOM encoding (Excel/Hebrew-safe) (+2 more)

### Community 117 - "Community 117"
Cohesion: 0.31
Nodes (7): AsyncSession, get, stats(), CableMismatchItem, DashboardStats, MacMismatchItem, BaseModel

### Community 118 - "Community 118"
Cohesion: 0.22
Nodes (7): Base, Review center (V7.1): operator dismissals for computed findings. Every review…, ReviewDismissal, dismiss(), Record a dismissal; re-dismissing the same tuple returns the row., test_review_dismissals_backed_up_and_audited(), ReviewDismissal

### Community 119 - "Community 119"
Cohesion: 0.39
Nodes (5): ListTarget, Import a sheet as a custom list (user-selected or suggested)., _preview_of(), also_ipam=False: a servers sheet produces ONLY list rows — no addresses or…, TestPlanListTarget

### Community 120 - "Community 120"
Cohesion: 0.50
Nodes (8): accept_scanned_mac(), _clear_flag(), keep_stored_mac(), _mismatch_flag(), IPAddress, Trust the scanner: scanned MAC becomes the stored mac_address., Trust inventory: restore the documented MAC and dismiss the pair so the…, IPAddress

### Community 121 - "Community 121"
Cohesion: 0.39
Nodes (8): _apply_bridge_links(), due_device_ids(), AsyncSession, datetime, DeviceInterface, _stamp_device(), _upsert_interfaces(), datetime

### Community 122 - "Community 122"
Cohesion: 0.36
Nodes (6): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…

### Community 124 - "Community 124"
Cohesion: 0.25
Nodes (6): DIR, FACES, LAYOUTS, problems, referenced, slugs

### Community 125 - "Community 125"
Cohesion: 0.29
Nodes (4): _col_class(), _positional_columns(), Dominant content class of a column sample., Headerless sheet: locate the IP column, then assign the remaining canonical…

### Community 126 - "Community 126"
Cohesion: 0.29
Nodes (7): scripts, build, build:rack-library, check:rack-library, dev, lint, start

### Community 127 - "Community 127"
Cohesion: 0.29
Nodes (7): API sketch, Device detail, Devices, Devices vs racks, From the IP drawer, Health rollup, The list

### Community 129 - "Community 129"
Cohesion: 0.40
Nodes (3): קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., TestCircuitsParser

### Community 130 - "Community 130"
Cohesion: 0.40
Nodes (5): Docs: IP Addresses, Docs: Devices, Docs: Racks, Docs: Settings, Docs: Subnets

### Community 131 - "Community 131"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 132 - "Community 132"
Cohesion: 0.50
Nodes (3): emit_new_flags(), test_cable_mismatch_event_shape(), _rec()

### Community 133 - "Community 133"
Cohesion: 0.67
Nodes (3): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for()

### Community 134 - "Community 134"
Cohesion: 0.67
Nodes (4): _login(), _mkuser(), AsyncSession, test_rbac_cabling()

### Community 135 - "Community 135"
Cohesion: 0.50
Nodes (4): Changelog — global /changelog audit log, Row color storage & coverage, Site list affordances (reorder, pin, inline edit, tags, row color), Tag list management & deletion semantics

## Ambiguous Edges - Review These
- `Cable` → `Rack`  [AMBIGUOUS]
  frontend/src/content/docs/cabling.md · relation: conceptually_related_to
- `Stats strip & saved views` → `Monitoring doc (V7)`  [AMBIGUOUS]
  frontend/src/content/docs/inventory.md · relation: semantically_similar_to

## Knowledge Gaps
- **450 isolated node(s):** `DeviceRow`, `AssetRow`, `Step`, `PrefixRow`, `RackRow` (+445 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1644 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **58 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Cable` and `Rack`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Stats strip & saved views` and `Monitoring doc (V7)`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._
- **Why does `create_device()` connect `Community 4` to `Community 70`, `Community 7`, `Community 17`, `Community 23`, `Community 24`, `Community 29`?**
  _High betweenness centrality (0.119) - this node is a cross-community bridge._
- **Why does `Device` connect `Community 17` to `Community 0`, `Community 4`, `Community 45`, `Community 15`, `Community 18`?**
  _High betweenness centrality (0.118) - this node is a cross-community bridge._
- **Why does `js-yaml` connect `Community 82` to `Community 64`, `Community 9`?**
  _High betweenness centrality (0.115) - this node is a cross-community bridge._
- **Are the 69 inferred relationships involving `Device` (e.g. with `_filtered_devices()` and `_export_rows()`) actually correct?**
  _`Device` has 69 INFERRED edges - model-reasoned connections that need verification._
- **Are the 72 inferred relationships involving `IPAMError` (e.g. with `_get_interface()` and `_get_cable()`) actually correct?**
  _`IPAMError` has 72 INFERRED edges - model-reasoned connections that need verification._