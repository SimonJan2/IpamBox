# Graph Report - IpamBox  (2026-09-26)

## Corpus Check
- 2618 files · ~1,047,600 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 5030 nodes · 16068 edges · 222 communities (128 shown, 56 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 1274 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- devices-client.tsx
- lucide-react
- react
- prefixes.py
- devices.py
- DeviceInterface
- entities.py
- IPAMError
- rack-collision.ts
- v1/racks.py
- Device
- test_snmp.py
- cn()
- IpamBox
- test_snmp.py
- app-shell.tsx
- key()
- Base
- index.ts
- rack_io.py
- get_settings()
- User
- services/backup.py
- useAsyncData()
- imports.py
- test_monitors.py
- color_rules.py
- test_scanner.py
- _Planner
- generate_demo_data.py
- addresses.py
- channels.py
- worker.py
- clean()
- test_snmp.py
- test_cabling.py
- test_snmp.py
- test_racks.py
- test_devices.py
- test_rack_io.py
- test_secrets.py
- scans.py
- backend/requirements.txt
- useAsyncData()
- route-error.tsx
- v1/monitors.py
- v1/monitors.py
- scanner.py
- traps.py
- _split_dsn()
- test_device_io.py
- runtime_settings.py
- rackula.ts
- test_backup.py
- _mklist()
- Device (first-class host entity)
- Rack
- v1/search.py
- test_review.py
- ip_display()
- _matrix()
- tags.py
- vlans.py
- demo_rack_dc.py
- ip_display()
- Excel workbook import
- dependencies
- maintenance.py
- Monitoring doc (V7)
- test_ipam_extras.py
- test_workbook_import.py
- package.json
- rack_io.py
- run_scan()
- UserRole
- docs.ts
- useAsyncData()
- Community 77
- SNMP Enrichment Documentation
- build-rack-library.mjs
- users.py
- ChangeLog
- generate_demo_data.py
- index.ts
- reader.py
- test_colors.py
- IpamBox README
- test_ordering.py
- test_prefix_api.py
- compilerOptions
- users.py
- _mklist()
- Rack device image library
- prefixes.py
- test_lists.py
- network.py
- test_ip_source.py
- parse_site_sheet()
- NotificationChannel
- index.ts
- parse_sites_master()
- test_review.py
- IPAddress
- prefixes.py
- test_changelog.py
- test_search.py
- test_auth.py
- test_scan_cidr_tcp_fallback_reports_found()
- test_racks.py
- _FakePool
- app-shell.tsx
- ip_display()
- devDependencies
- ip_display()
- test_review.py
- _mkuser()
- test_monitors.py
- IpamBox
- check-rack-library.mjs
- _positional_columns()
- scripts
- Devices
- test_entities.py
- test_monitors.py
- app-shell.tsx
- .test_legacy_bezeq_layout()
- Docs: IP Addresses
- Security Policy
- test_snmp.py
- test_racks.py
- test_racks.py
- Community 131
- test_snmp.py
- test_snmp.py
- next-env.d.ts
- POST /api/v1/devices/import
- Racks REST API (GET /api/v1/racks)
- xff-shim.js
- Community 170
- Community 171
- Community 172
- Community 173
- Rack device image library bundle
- Request
- SyncSession
- str
- model_validator
- Path
- CustomList
- Prefix
- ScanJob
- Community 188
- Community 189
- Community 190
- Community 191
- Community 192
- Community 193
- Community 194
- IpamBox App Icon (icon.svg)
- Root Layout (layout.tsx, title: IpamBox)
- GET /api/v1/devices/export.csv
- GET /api/v1/devices/export.xlsx
- ip_addresses table
- GET /api/v1/racks/export.csv
- GET /api/v1/racks/export.xlsx
- GET /api/v1/rack-groups/{id}/export.xlsx
- GET /api/v1/racks/{id}/export.xlsx
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
- `Next-free-IP allocation` --semantically_similar_to--> `Atomic next-IP allocation`  [INFERRED] [semantically similar]
  frontend/src/content/docs/subnets.md → README.md
- `CSV export` --semantically_similar_to--> `Address CSV import/export (UTF-8 BOM)`  [INFERRED] [semantically similar]
  frontend/src/content/docs/devices.md → README.md
- `Discovery Inbox reconciliation` --semantically_similar_to--> `Live IP column resolution`  [INFERRED] [semantically similar]
  README.md → frontend/src/content/docs/lists.md
- `Monitoring doc (V7)` --semantically_similar_to--> `Stats strip & saved views`  [AMBIGUOUS] [semantically similar]
  frontend/src/content/docs/monitoring.md → frontend/src/content/docs/inventory.md

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

## Communities (222 total, 56 thin omitted)

### Community 0 - "devices-client.tsx"
Cohesion: 0.08
Nodes (109): CertificatesPage(), EMPTY, CircuitsPage(), EMPTY, DEVICE_VIEWS, DeviceRow, DevicesPage(), EMPTY (+101 more)

### Community 1 - "lucide-react"
Cohesion: 0.07
Nodes (90): ACTION_STYLES, ACTION_STYLES, CABLE_REASON, BulkResp, ImportListDialog(), FACE_BADGE, CABLE_REASON, DELETE_PATH (+82 more)

### Community 2 - "react"
Cohesion: 0.02
Nodes (47): nextConfig, metadata, metadata, metadata, metadata, metadata, metadata, metadata (+39 more)

### Community 3 - "prefixes.py"
Cohesion: 0.05
Nodes (100): create_network(), AsyncSession, post, POST /networks — the "add network" wizard endpoint (V6.1). One call creates or…, allocate_next_available(), create_prefix(), delete_prefix(), export_prefixes() (+92 more)

### Community 4 - "devices.py"
Cohesion: 0.05
Nodes (96): _asset_ref(), _check_iface_refs(), _check_refs(), create_device(), create_interface(), delete_device(), delete_interface(), _detail() (+88 more)

### Community 5 - "DeviceInterface"
Cohesion: 0.05
Nodes (89): _cable_out(), _check_ends(), create_cable(), delete_cable(), _get_cable(), _get_interface(), interfaces_match_free_text(), list_cables() (+81 more)

### Community 6 - "entities.py"
Cohesion: 0.05
Nodes (70): list_changelog(), AsyncSession, get, list_discovered(), AsyncSession, get, Unconfirmed hosts found by scanners, pending admin review. No limit -> the full…, CRUD routers for the workbook-imported entity families. Circuits, certificates,… (+62 more)

### Community 7 - "IPAMError"
Cohesion: 0.05
Nodes (85): _crud_router(), create_item(), delete_item(), get_item(), list_items(), reorder_items(), update_item(), bulk_rows() (+77 more)

### Community 8 - "rack-collision.ts"
Cohesion: 0.06
Nodes (74): DragSession, errDetail(), findDevice(), GroupClient(), moveDevice(), metadata, FACE_BADGE, RackDetailPage() (+66 more)

### Community 9 - "v1/racks.py"
Cohesion: 0.06
Nodes (79): _check_refs(), create_device(), create_rack(), delete_device(), delete_rack(), _device_out(), _devices(), _export_name() (+71 more)

### Community 10 - "Device"
Cohesion: 0.06
Nodes (78): Device, Base, str, RackFace, apply_device_import(), _carrier_diff_name(), _err(), _find_carrier() (+70 more)

### Community 11 - "test_snmp.py"
Cohesion: 0.07
Nodes (75): Device, _device(), _down(), _enable(), _iface(), _ifrow(), _ip(), _link_binds() (+67 more)

### Community 12 - "cn()"
Cohesion: 0.06
Nodes (63): IpCell(), SortableColRow(), IP_ROLES, IP_STATUSES, RANGE_ROLES, SplitDialog(), SplitPlan, AddressFilterPanel() (+55 more)

### Community 13 - "IpamBox"
Cohesion: 0.06
Nodes (82): Accounts & Roles, Insecure mode (IPAMBOX_ALLOW_INSECURE), Four roles (Administrator, Operator, Contributor, Viewer), Session-cookie authentication, Address roles (vip/vrrp/hsrp/glbp/carp/secondary), Address CSV import/export, IP Addresses, IP drawer (+74 more)

### Community 14 - "test_snmp.py"
Cohesion: 0.09
Nodes (65): _apply_link_state(), _clear_unmanaged_flag(), _decode(), ensure(), _flag_unmanaged(), handle_trap(), datetime, _resolve_device() (+57 more)

### Community 15 - "app-shell.tsx"
Cohesion: 0.04
Nodes (64): EMPTY_EDIT, FACE_BADGE, metadata, viewport, AppearancePage(), AppShell(), AUTH_ROUTES, isActive() (+56 more)

### Community 16 - "key()"
Cohesion: 0.06
Nodes (58): AsyncClient, apply_plan(), build_plan(), collect_inventory(), _fold(), inventory_fingerprint(), new_batch(), Plan (+50 more)

### Community 17 - "Base"
Cohesion: 0.07
Nodes (41): do_run_migrations(), run_migrations_online(), healthz(), metrics(), get, Request, Prometheus-style text exposition of object + scan counters., Readiness probe: verifies DB + Redis connectivity. (+33 more)

### Community 18 - "index.ts"
Cohesion: 0.03
Nodes (67): ACTION_STYLE, CommitResp, Counts, csvCell(), FAMILY_LABEL, PreviewResp, SheetResults(), Step (+59 more)

### Community 19 - "rack_io.py"
Cohesion: 0.07
Nodes (58): RackGroup, A bayed row: racks ordered left-to-right as they stand in the DC., device_export_rows(), _float_field(), _fold(), _name_map(), _parse_id(), #5' or '5' -> 5; None when the cell isn't an id reference. (+50 more)

### Community 20 - "get_settings()"
Cohesion: 0.05
Nodes (62): ArqRedis, backup_now(), Enqueue an immediate scheduled-style backup on the worker., get_settings(), close_arq_pool(), close_redis(), get_arq_pool(), get_redis() (+54 more)

### Community 21 - "User"
Cohesion: 0.07
Nodes (62): auth_status(), change_password(), _current_user(), ensure_env_password_user(), login(), _login_session(), logout(), me() (+54 more)

### Community 22 - "services/backup.py"
Cohesion: 0.06
Nodes (61): delete_scheduled_backup(), download_backup(), download_scheduled_backup(), list_scheduled_backups(), AsyncSession, delete, get, post (+53 more)

### Community 23 - "useAsyncData()"
Cohesion: 0.06
Nodes (53): ChangelogPage(), metadata, DashboardPage(), DeviceDetailClient(), DiscoveryPage(), ImportPage(), ListsClient(), MonitoringPage() (+45 more)

### Community 24 - "imports.py"
Cohesion: 0.06
Nodes (53): commit_import(), delete_import(), get_import(), _import_dir(), list_imports(), _load_sheets(), preview_import(), AsyncSession (+45 more)

### Community 25 - "test_monitors.py"
Cohesion: 0.05
Nodes (37): _FakeArqPool, _FakeRedis, _login(), _mk_device(), _mk_prefix_and_addr(), _mkuser(), V7 monitoring + notification channels. Covers target CRUD/RBAC, the exactly-…, Viewer reads targets but can't write/check/delete them. (+29 more)

### Community 26 - "color_rules.py"
Cohesion: 0.07
Nodes (46): create_rule(), delete_rule(), get_rule(), list_rules(), preview_rule(), AsyncSession, delete, get (+38 more)

### Community 27 - "test_scanner.py"
Cohesion: 0.07
Nodes (49): _flag(), Any, AsyncSession, Merge scan results into the address table. Existing rows: refresh…, reconcile(), HostResult, _global_vrf_id(), _infer_scan_vrf() (+41 more)

### Community 28 - "_Planner"
Cohesion: 0.08
Nodes (18): parse_sites_master_records(), _Planner, _preview(), (first, second) octet-pair histogram of a sheet's addresses. Counting full…, Folded sheet title vs site name/code — word-boundary matching so 'int' doesn't…, Sheet title -> site key via code/name. Checks DB sites first, then sites…, A sheet that octet-matches a master row with no real name gives the site its…, The octet block belongs to an inactive (closed) site, which must not claim new… (+10 more)

### Community 29 - "generate_demo_data.py"
Cohesion: 0.09
Nodes (49): assets_rows(), _assign_site_sheets(), _assign_site_sheets_clean(), build_en_workbook(), build_mixed_workbook(), build_sites(), certificates_rows(), circuits_rows() (+41 more)

### Community 30 - "addresses.py"
Cohesion: 0.08
Nodes (49): _address_csv_row(), _addresses_stmt(), bulk_addresses(), BulkBody, _check_interface_link(), create_address(), delete_address(), export_addresses() (+41 more)

### Community 31 - "channels.py"
Cohesion: 0.08
Nodes (45): _config_fields(), create_channel(), delete_channel(), _get(), get_channel(), list_channels(), notification_log(), _out() (+37 more)

### Community 32 - "worker.py"
Cohesion: 0.08
Nodes (46): set_actor(), emit(), Any, Fan out to every enabled channel. Returns deliveries attempted., get_effective(), monitor_tick(), Every-minute cron beside scheduler_tick: batch due targets into a single sweep…, detect_interface() (+38 more)

### Community 33 - "clean()"
Cohesion: 0.08
Nodes (41): assemble_ip(), clean(), _clean_octets(), map_status(), mask_to_prefixlen(), network_of(), norm_header(), parse_range_end() (+33 more)

### Community 34 - "test_snmp.py"
Cohesion: 0.12
Nodes (43): _auth(), _context(), _cred(), _get(), _idx_inet(), _idx_int(), _idx_tail_ints(), _index_suffix() (+35 more)

### Community 35 - "test_cabling.py"
Cohesion: 0.13
Nodes (46): _backup_bytes(), _cable(), _device(), _gen(), _iface(), _ip(), _login(), _mkuser() (+38 more)

### Community 36 - "test_snmp.py"
Cohesion: 0.24
Nodes (42): poll_device(), _cable(), _commit_fresh(), _device(), _enable(), _flag(), _fresh_iface(), _iface() (+34 more)

### Community 37 - "test_racks.py"
Cohesion: 0.14
Nodes (44): _dev(), _group(), _imports(), _next_free(), AsyncClient, _rack(), Rack elevations: CRUD, face-aware collision rules, Rackula import., check_placement runs on update too: a rear device may share a U with front… (+36 more)

### Community 38 - "test_devices.py"
Cohesion: 0.13
Nodes (39): _cable(), _device(), _group(), _iface(), _ip(), _login(), _mkuser(), _prefix() (+31 more)

### Community 39 - "test_rack_io.py"
Cohesion: 0.16
Nodes (42): _bundle(), _by_sheet(), _cable(), _csv(), _device(), _group(), _iface(), _import() (+34 more)

### Community 40 - "test_secrets.py"
Cohesion: 0.09
Nodes (36): _data_key(), decrypt_str(), encrypt_str(), _master_key(), Exception, Secrets at rest — the credential contract v7/v8/v12/v14 build on. A single…, Unseal a "v1:…" blob. Strict prefix check — unknown formats, malformed payloads…, Base for secrets-service failures — never carries secret material. (+28 more)

### Community 41 - "scans.py"
Cohesion: 0.08
Nodes (36): cancel_scan(), _check_cidr_allowed(), create_scan(), get_scan(), _job_payload(), list_scans(), AsyncSession, get (+28 more)

### Community 42 - "backend/requirements.txt"
Cohesion: 0.10
Nodes (37): alembic==1.14.0, arq==0.26.1, asyncpg==0.30.0, bcrypt==4.3.0, cryptography==50.0.1, fastapi==0.115.6, httpx==0.28.1, psutil==6.1.0 (+29 more)

### Community 43 - "useAsyncData()"
Cohesion: 0.09
Nodes (36): PrefixDetailPage(), toggleIn(), DEVICE_FILTER_PARAMS, DEVICE_TEXT_PARAMS, DeviceFilterPanel(), DeviceFilterState, DeviceTextParam, FACES (+28 more)

### Community 45 - "v1/monitors.py"
Cohesion: 0.12
Nodes (34): check_now(), _check_refs(), create_target(), delete_target(), _filters(), _get(), get_target(), list_targets() (+26 more)

### Community 46 - "v1/monitors.py"
Cohesion: 0.10
Nodes (33): MonitorState, MonitorTarget, V7 — continuous monitoring targets + outbound notification channels., One monitored endpoint — resolves to a concrete IP at check time.…, apply_result(), device_check_ip(), due_target_ids(), due_where() (+25 more)

### Community 47 - "scanner.py"
Cohesion: 0.08
Nodes (32): Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)., _table(), vendor_for(), _arp_scan(), _host_chunks(), _icmp_checksum(), _icmp_echo_packet(), _icmp_socket() (+24 more)

### Community 48 - "traps.py"
Cohesion: 0.08
Nodes (31): _apply_link_state(), _clear_unmanaged_flag(), _decode(), ensure(), _flag_unmanaged(), handle_trap(), SNMP trap receiver (V8.1) — near-realtime link state. The poll lane…, (transportDomain, transportAddress) -> the sender's IP string. asyncio's UDP… (+23 more)

### Community 49 - "_split_dsn()"
Cohesion: 0.11
Nodes (26): _base_dsn(), client(), engine(), _prepare_test_db(), fixture, Split 'postgresql://host/db?params' into ('postgresql://host', '?params')., Create the test database (if missing) and run migrations against it., _split_dsn() (+18 more)

### Community 50 - "test_device_io.py"
Cohesion: 0.20
Nodes (34): _csv(), _device(), _group(), _import(), _ip(), _login(), _mkuser(), _prefix() (+26 more)

### Community 51 - "runtime_settings.py"
Cohesion: 0.09
Nodes (25): Any, psycopg2-style URL for alembic offline mode / scripts., Settings, Effective, _env_sourced(), patch(), Any, AsyncSession (+17 more)

### Community 52 - "rackula.ts"
Cohesion: 0.10
Nodes (34): RackulaImportDialog(), ABBREV_TO_CATEGORY, canonicalCategory(), CATEGORY_TO_ABBREV, clip(), compareVersions(), decodeShareUrl(), DeviceLike (+26 more)

### Community 53 - "test_backup.py"
Cohesion: 0.16
Nodes (33): User, _backup_bytes(), _envelope_bytes(), _mkusers(), Hand-craft a backup envelope (e.g. with a forged users table)., Guard: every ORM table must be backed up (or explicitly excluded). Adding a new…, Fresh-server scenario: the migration-seeded Global VRF is replaced by the…, Fresh-server scenario: the target's admins survive; its non-admin set is fully… (+25 more)

### Community 54 - "_mklist()"
Cohesion: 0.10
Nodes (16): pick_key_column(), Default merge column: first non-date/ip column filled in most rows (the…, DbState, Lookup indexes over the current DB contents., _mklist(), Custom lists: CRUD + rows + IP resolution + workbook list-target import., v2 workbook: SRV2 edited, SRV3 added, SRV1 missing -> merge keeps SRV1, updates…, _servers_xlsx() (+8 more)

### Community 55 - "Device (first-class host entity)"
Cohesion: 0.11
Nodes (34): netbox-community/devicetype-library, IPAddress, Cable, connected_interface_id (structured far-end port link), connected_ip (host-side NIC binding), DeviceInterface (device-owned port), L1 trace (cable path walk), match-free-text transition endpoint (+26 more)

### Community 56 - "Rack"
Cohesion: 0.12
Nodes (30): _check_site(), create_rack_group(), delete_rack_group(), export_rack_group_xlsx(), _get_group(), get_rack_group(), list_rack_groups(), _ordered_racks() (+22 more)

### Community 57 - "v1/search.py"
Cohesion: 0.16
Nodes (29): _folded(), AsyncSession, get, Cross-object search for the command palette. One GET returns grouped matches…, Column expression with Hebrew final letters folded — pairs with fold_hebrew()…, Short label for a list-row search hit: key-column value, else the first non-…, _row_label(), search() (+21 more)

### Community 58 - "test_review.py"
Cohesion: 0.23
Nodes (32): _device(), _flag_mismatch(), _iface(), _ip(), _login(), _prefix(), AsyncClient, AsyncSession (+24 more)

### Community 59 - "ip_display()"
Cohesion: 0.16
Nodes (31): ip_display(), Any, Normalize asyncpg-returned ipaddress objects / strings to display form. INET…, to_int(), _aging_discovery_items(), build_review(), _cable_mismatch_items(), _cert_items() (+23 more)

### Community 60 - "_matrix()"
Cohesion: 0.15
Nodes (14): _master_row(), _matrix(), _plan(), _preview_of(), INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration Site via its…, טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site matches…, LEV_DR has no 10.x addresses — on a fresh DB it can only match a site planned…, int' is a substring of 'maintenence' — word-boundary matching must NOT bind… (+6 more)

### Community 61 - "tags.py"
Cohesion: 0.15
Nodes (24): assign_tag(), create_tag(), delete_tag(), get_tag(), list_assignments(), list_tags(), AsyncSession, delete (+16 more)

### Community 62 - "vlans.py"
Cohesion: 0.16
Nodes (27): _check_duplicate_vid(), create_vlan(), create_vlan_group(), delete_vlan(), delete_vlan_group(), list_vlan_groups(), list_vlans(), AsyncSession (+19 more)

### Community 63 - "demo_rack_dc.py"
Cohesion: 0.11
Nodes (24): Api, apply(), _device_payload(), emit_zip(), find_one(), _KeepMethodRedirect, layout_doc(), main() (+16 more)

### Community 64 - "ip_display()"
Cohesion: 0.12
Nodes (27): dismiss_item(), _flagged_address(), get_review(), mac_mismatch_accept(), mac_mismatch_keep(), AsyncSession, get, IPAddress (+19 more)

### Community 65 - "Excel workbook import"
Cohesion: 0.10
Nodes (29): openpyxl==3.1.5, Demo CSV files, Fictional demo dataset, Demo import data README, demo-addresses.csv, Demo list CSVs (contacts/vlans/servers), Network_Address_DEMO.xlsx, Network_Address_DEMO_EN.xlsx (+21 more)

### Community 66 - "dependencies"
Cohesion: 0.07
Nodes (29): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, js-yaml, jszip, lucide-react (+21 more)

### Community 67 - "maintenance.py"
Cohesion: 0.14
Nodes (26): _audit(), clear_discovery(), factory_reset(), purge_changelog(), purge_scans(), PurgeBody, AsyncSession, BaseModel (+18 more)

### Community 68 - "Monitoring doc (V7)"
Cohesion: 0.14
Nodes (28): Address status lifecycle (active/reserved/dhcp/discovered/offline), Changelog bypass for state writes, Check kinds (ping/tcp/http), Monitoring doc (V7), Event sources, down_after hysteresis, Deliberate limits, Monitor target (+20 more)

### Community 69 - "test_ipam_extras.py"
Cohesion: 0.16
Nodes (26): _prefix(), _range(), export.csv takes the same filters as the list endpoint — a filtered view…, Same filtered-export treatment on the prefixes CSV (F8)., A documented v6 /64's 2^64 host count must not reach dashboard sums (~1.8e19 >…, A deliberate bulk import documents existing reality — statics inside pools land…, test_address_role_nat_and_bulk(), test_addresses_export_respects_filters() (+18 more)

### Community 70 - "test_workbook_import.py"
Cohesion: 0.08
Nodes (14): Workbook import: normalizer/parser unit tests (no DB) + API e2e., Small synthetic workbook: sites master + one site sheet + circuits., Site sheet documenting a DHCP span AND static stations inside it — the real…, Pool-guard regression: committing a plan whose dhcp range covers documented…, Commit-time PlanError must 422 AND record the failure. The route rolls back…, test_commit_plan_error_marks_batch_failed(), test_commit_twice_rejected(), test_import_e2e() (+6 more)

### Community 71 - "package.json"
Cohesion: 0.07
Nodes (25): name, private, version, autoprefixer, clsx, lz-string, postcss, @radix-ui/react-dropdown-menu (+17 more)

### Community 72 - "rack_io.py"
Cohesion: 0.10
Nodes (26): import_devices(), Request, Smart device import. Stateless — the file is posted twice: dry-run preview…, import_racks(), Request, Smart rack/group bundle import — V5B's stateless flow for whole trees. Sheets…, _alias_to_field(), apply_mapping_overrides() (+18 more)

### Community 73 - "run_scan()"
Cohesion: 0.13
Nodes (19): str, ScanStatus, _FakeRedis, _mk_job(), In-memory stand-in for the worker's redis client (get/set/publish)., Point the worker at the test DB (sf) and the fake redis client., Cancel flag polled between phases -> ScanCancelled -> CANCELLED, and no…, Audit race: API writes CANCELLED mid-scan while the redis flag is lost… (+11 more)

### Community 74 - "UserRole"
Cohesion: 0.28
Nodes (24): str, UserRole, Viewer tier can read lists/rows but every mutation is 403., TestPermissions, login(), mkuser(), other_client(), AsyncClient (+16 more)

### Community 75 - "docs.ts"
Cohesion: 0.13
Nodes (19): DocsIndexClient(), metadata, DocPage(), dynamicParams, generateMetadata(), loadMarkdown(), DocsContent(), BY_SLUG (+11 more)

### Community 76 - "useAsyncData()"
Cohesion: 0.17
Nodes (21): metadata, ALL_STATUSES, prefixText(), siteText(), TreePage(), vrfText(), collectExpandableKeys(), flattenTree() (+13 more)

### Community 77 - "Community 77"
Cohesion: 0.09
Nodes (24): Accounts & role-based access control, Expiry tracking (badge, certs_expiring_30d dashboard count), Certificates — expiry tracking register, Circuits — WAN circuit register, Circuit fields (line type, Bezeq circuit ID, WAN IP, is_retired), Discovery Inbox — reconciliation queue, Hierarchy tree (/tree) — Site→VRF→Prefix, Tree navigation (click-to-prefix, session expand state) (+16 more)

### Community 78 - "SNMP Enrichment Documentation"
Cohesion: 0.15
Nodes (23): arq==0.26.1, bcrypt==4.3.0, cryptography==50.0.1, fastapi==0.115.6, pysnmp==7.1.29, redis==5.2.0, scapy==2.6.1, sqlalchemy[asyncio]==2.0.36 (+15 more)

### Community 79 - "build-rack-library.mjs"
Cohesion: 0.13
Nodes (23): arrLen(), attribution(), CATEGORY_COLOUR, CURATED, fetchBuf(), fetchJson(), FRONTEND, FULL_IMPORT (+15 more)

### Community 80 - "users.py"
Cohesion: 0.16
Nodes (22): _admin_count(), create_user(), delete_user(), list_users(), _out(), AsyncSession, BaseModel, delete (+14 more)

### Community 81 - "ChangeLog"
Cohesion: 0.14
Nodes (17): AppSetting, Runtime-editable setting override. Absent row -> env var -> default., fake_arq(), _pool(), _FakeArqJob, _FakePool, AsyncClient, fixture (+9 more)

### Community 82 - "generate_demo_data.py"
Cohesion: 0.12
Nodes (21): pysnmp==7.1.29, Demo import data — ALL FICTIONAL, demo_rack_dc.py, /devices/import endpoint, Examples README (demo import data), Files, `Network_Address_DEMO_EN.xlsx` — the edge-case workbook, `Network_Address_DEMO.xlsx` — the clean flagship (+13 more)

### Community 83 - "index.ts"
Cohesion: 0.11
Nodes (18): AUTH_PROTOS, EMPTY_CRED, PRIV_PROTOS, SnmpCard(), VERSIONS, ACTION_STYLE, APPLYABLE, fmt() (+10 more)

### Community 84 - "reader.py"
Cohesion: 0.16
Nodes (16): classify_sheet(), _has(), _looks_like_header(), Sheet family detection by header signature (Hebrew + English variants)., (family, header_row_index, warnings). header_row_index = index of the row…, Network_Address.xlsx ingestion. Pipeline: reader (xlsx -> matrices) -> classify…, _csv_sheet(), load_upload() (+8 more)

### Community 85 - "test_colors.py"
Cohesion: 0.27
Nodes (19): _login(), _mk_rule(), _mk_site(), _mkuser(), AsyncClient, AsyncSession, Global row colors: manual row_color + rule-computed display_color. Covers the…, test_backup_roundtrips_color_rules() (+11 more)

### Community 86 - "IpamBox README"
Cohesion: 0.22
Nodes (20): IP address, Address source provenance field, Inventory sync (Pull inventory), SOURCE_RANK precedence (scan < snmp < integration < import < manual), Add network wizard, Add network wizard (POST /networks), container prefix status, Subnets doc (+12 more)

### Community 87 - "test_ordering.py"
Cohesion: 0.28
Nodes (18): _circuit_order(), _login(), _mk_circuits(), _mkuser(), AsyncClient, AsyncSession, Global row ordering: POST /{entity}/reorder + pinned rows. Covered on both…, Reordering a subset keeps the slots those rows already had — rows outside the… (+10 more)

### Community 88 - "test_prefix_api.py"
Cohesion: 0.22
Nodes (18): _addrs(), _global_vrf_id(), _mkprefix(), Splits are counted arithmetically before materializing: anything over…, test_gateway_clear_removes_only_pristine_row(), test_gateway_never_clobbers_manual_row(), test_gateway_validation(), test_next_ip_never_hands_out_gateway() (+10 more)

### Community 89 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 90 - "users.py"
Cohesion: 0.18
Nodes (17): _build_out(), _mask_url(), AsyncSession, get, Hide the password in a scheme://user:pass@host URL., read_settings(), update_settings(), ChangePasswordBody (+9 more)

### Community 91 - "_mklist()"
Cohesion: 0.13
Nodes (15): _cell_text(), _infer_type(), _ips(), _is_ip_token(), Custom-list extraction: turn any sheet into {columns, rows} for a list. Unlike…, Raw cell -> stored string. Dates iso-format; everything else cleans., (type, extra) for one column — extra carries options/multi., Row 0 of an unrecognized sheet looks like headers when every cell is a short… (+7 more)

### Community 92 - "Rack device image library"
Cohesion: 0.15
Nodes (17): Demo .Rackula.zip racks, Demo .Rackula.zip rack layouts, Air-gap safe bundling, frontend/scripts/build-rack-library.mjs, CC0 1.0 Universal license, CC0 1.0 Universal, netbox-community/devicetype-library, Rack library ATTRIBUTION (+9 more)

### Community 93 - "prefixes.py"
Cohesion: 0.21
Nodes (10): IPRole, str, ConnectedInterfaceRef, IPAddressCreate, IPAddressOut, IPAddressPage, IPAddressUpdate, BaseModel (+2 more)

### Community 94 - "test_lists.py"
Cohesion: 0.22
Nodes (9): ListTarget, Import a sheet as a custom list (user-selected or suggested)., extract_list_table(), SheetMatrix -> (column defs, row dicts). columns: [{key, label, type, options?,…, _matrix(), _preview_of(), also_ipam=False: a servers sheet produces ONLY list rows — no addresses or…, TestExtract (+1 more)

### Community 95 - "network.py"
Cohesion: 0.20
Nodes (10): _ip(), NetworkCreate, NetworkDhcpRange, NetworkOut, NetworkPrefix, NetworkVlanNew, BaseModel, field_validator (+2 more)

### Community 96 - "test_ip_source.py"
Cohesion: 0.24
Nodes (16): may_write(), Field-ownership check for source-stamped rows (ip_addresses et al.). True when…, _mk_prefix(), V6 provenance — ip_addresses.source: stamping, ownership, filtering. Every…, Manual and imported rows keep their provenance when a scan sees them — observed…, Response bodies carry `source` but never any *_enc-style field., test_csv_import_stamps_import(), test_export_filters_and_carries_source() (+8 more)

### Community 97 - "parse_site_sheet()"
Cohesion: 0.17
Nodes (8): _blocks(), parse_site_sheet(), Split duplicated column groups (031-style runaway): each block starts at an…, MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf., Bare 'Name' (Cellular) maps to the hostname field., Non-empty unnamed columns pile into cf['extra'] instead of vanishing (Pelephone…, TestSiteSheetExtras, TestSiteSheetParser

### Community 98 - "NotificationChannel"
Cohesion: 0.21
Nodes (15): _deliver(), _DeliveryFailed, _log(), _post_json(), AsyncSession, Exception, Outbound notification fan-out — the watchdog's voice (V7). ``emit(event_type,…, Exercise one channel's stored credentials — used by POST /notification-… (+7 more)

### Community 99 - "index.ts"
Cohesion: 0.15
Nodes (13): ACTION_STYLE, ColumnMap, DetectResp, FieldOption, fmt(), ImportOption, ImportResp, ResultRows() (+5 more)

### Community 100 - "parse_sites_master()"
Cohesion: 0.19
Nodes (8): _master_blocks(), parse_sites_master(), (first, second) octet pairs a master row declares — lets sheet->site matching…, Integration Site's '172,20-21' fragments -> octet-pair blocks, no 10.x…, Nameless master rows (10.22/35/37/39) become 'Site N' instead of being dropped…, היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name, suffixed so…, The real header has 'הערות' twice — first non-empty wins., TestSitesMasterParser

### Community 101 - "test_review.py"
Cohesion: 0.31
Nodes (11): after_flush(), before_flush(), _columns(), _create_changes(), _delete_changes(), Audit trail via session flush hooks. before_flush collects (object, action,…, register(), _repr() (+3 more)

### Community 102 - "IPAddress"
Cohesion: 0.24
Nodes (8): IPRangeRole, str, IPRangeCreate, IPRangeOut, IPRangeUpdate, BaseModel, field_validator, model_validator

### Community 103 - "prefixes.py"
Cohesion: 0.23
Nodes (12): sf(), _mk_prefix(), test_address_crud_and_dup_guard(), test_allocation_skips_existing(), test_concurrent_allocation_unique(), alloc(), test_exhausted_prefix_conflicts(), test_sequential_allocation_skips_boundaries() (+4 more)

### Community 104 - "test_changelog.py"
Cohesion: 0.23
Nodes (12): AsyncClient, tag_assignments.object_id has no FK — deleting a tagged object must drop its…, Tag.assignments is already ORM delete-orphan — each removed assignment lands in…, PATCH settings with a null value deletes the app_settings row — that delete…, /addresses/bulk action=delete used to issue one Core DELETE — invisible to the…, test_bulk_delete_writes_changelog_entries(), test_changelog_captures_ip_status_change(), test_changelog_records_crud() (+4 more)

### Community 105 - "test_search.py"
Cohesion: 0.31
Nodes (12): AsyncClient, Global /api/v1/search endpoint (UX-3)., Regression: list_addresses ?q= used to crash on a missing column., Site + VRF + prefix + address + one of each workbook entity., _seed(), test_addresses_q_filter_not_broken(), test_search_empty_query(), test_search_grouped_results() (+4 more)

### Community 106 - "test_auth.py"
Cohesion: 0.29
Nodes (11): AsyncClient, When the socket peer isn't in ipambox_trusted_proxies, a supplied XFF is…, Spreading failures across many usernames from one IP trips the aggregate lock —…, Five bad logins for one (user, ip) pair must not lock out other users on the…, test_endpoints_require_auth(), test_lockout_keyed_per_user_ip_pair(), test_login_lockout(), test_per_ip_aggregate_backstop() (+3 more)

### Community 107 - "test_scan_cidr_tcp_fallback_reports_found()"
Cohesion: 0.21
Nodes (8): on_hosts fires once per detection step with that chunk's new IPs — ARP batch…, When L2+L3 find nothing, the TCP fallback publishes its batch too., test_scan_cidr_emits_found_deltas(), fake_icmp(), fake_probe(), fake_ptr(), on_hosts(), test_scan_cidr_tcp_fallback_reports_found()

### Community 108 - "test_racks.py"
Cohesion: 0.29
Nodes (11): _carrier(), _mount(), Children ride inside the carrier's span — it's the carrier (not the child) that…, Unracking a carrier lifts the whole tray out: children leave the rack but stay…, test_carrier_crud_and_mount(), test_carrier_layout_shrink_strands_children(), test_carrier_move_syncs_children(), test_carrier_move_takes_children_across_racks() (+3 more)

### Community 109 - "_FakePool"
Cohesion: 0.20
Nodes (8): fake_arq(), _pool(), _FakeArqJob, _FakePool, fixture, Stands in for the arq Redis pool — never actually dispatches work., scan_exclude_networks=10.70.0.64/26 inside scan_networks=10.70.0.0/24: the…, test_scheduler_and_route_share_exclusion_guard()

### Community 110 - "app-shell.tsx"
Cohesion: 0.31
Nodes (10): CommandPalette(), Icon, Item, itemsFor(), PAGES, pagesFor(), remember(), SearchOut (+2 more)

### Community 111 - "ip_display()"
Cohesion: 0.36
Nodes (10): accept_scanned_mac(), _clear_flag(), keep_stored_mac(), mac_fingerprint(), _mismatch_flag(), IPAddress, The stable identity of a MAC mismatch: the documented→observed pair., Trust the scanner: scanned MAC becomes the stored mac_address. (+2 more)

### Community 112 - "devDependencies"
Cohesion: 0.20
Nodes (10): devDependencies, autoprefixer, postcss, sharp, tailwindcss, @types/js-yaml, @types/node, @types/react (+2 more)

### Community 113 - "ip_display()"
Cohesion: 0.31
Nodes (7): AsyncSession, get, stats(), CableMismatchItem, DashboardStats, MacMismatchItem, BaseModel

### Community 114 - "test_review.py"
Cohesion: 0.22
Nodes (7): Base, Review center (V7.1): operator dismissals for computed findings. Every review…, ReviewDismissal, dismiss(), Record a dismissal; re-dismissing the same tuple returns the row., test_review_dismissals_backed_up_and_audited(), ReviewDismissal

### Community 115 - "_mkuser()"
Cohesion: 0.28
Nodes (9): _mkuser(), User, UserRole, _mkuser(), User, UserRole, _mkuser(), User (+1 more)

### Community 117 - "IpamBox"
Cohesion: 0.43
Nodes (8): api service (FastAPI/uvicorn backend), db service (PostgreSQL 16), ipam bridge network (192.0.2.0/24), redis service (Redis 7, appendonly), scanner service (arq worker, host networking), web service (Next.js frontend), ip_addresses table (IPAM data store), ip column type (live IPAM resolution)

### Community 118 - "check-rack-library.mjs"
Cohesion: 0.25
Nodes (6): DIR, FACES, LAYOUTS, problems, referenced, slugs

### Community 119 - "_positional_columns()"
Cohesion: 0.29
Nodes (4): _col_class(), _positional_columns(), Dominant content class of a column sample., Headerless sheet: locate the IP column, then assign the remaining canonical…

### Community 120 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, build:rack-library, check:rack-library, dev, lint, start

### Community 121 - "Devices"
Cohesion: 0.29
Nodes (7): API sketch, Device detail, Devices, Devices vs racks, From the IP drawer, Health rollup, The list

### Community 123 - "test_monitors.py"
Cohesion: 0.33
Nodes (3): _Job, fake_arq(), enqueue_job()

### Community 124 - "app-shell.tsx"
Cohesion: 0.53
Nodes (5): moveRowNav(), G_CHORDS, isEditableTarget(), modalOpen(), useGlobalShortcuts()

### Community 125 - ".test_legacy_bezeq_layout()"
Cohesion: 0.40
Nodes (3): קוי בזק ישן (029) — bandwidth/contact map to real fields, the rest of the…, שם לקוח באפל'' (trailing gershayim) still hits the alias., TestCircuitsParser

### Community 126 - "Docs: IP Addresses"
Cohesion: 0.40
Nodes (5): Docs: IP Addresses, Docs: Devices, Docs: Racks, Docs: Settings, Docs: Subnets

### Community 127 - "Security Policy"
Cohesion: 0.40
Nodes (4): Deployment notes, Reporting a vulnerability, Security Policy, Supported versions

### Community 128 - "test_snmp.py"
Cohesion: 0.50
Nodes (3): emit_new_flags(), test_cable_mismatch_event_shape(), _rec()

### Community 129 - "test_racks.py"
Cohesion: 0.50
Nodes (3): Every /racks list param filters; all compose with AND semantics., _site(), test_racks_list_facet_params()

### Community 131 - "Community 131"
Cohesion: 0.50
Nodes (4): Changelog — global /changelog audit log, Row color storage & coverage, Site list affordances (reorder, pin, inline edit, tags, row color), Tag list management & deletion semantics

## Ambiguous Edges - Review These
- `Monitoring doc (V7)` → `Stats strip & saved views`  [AMBIGUOUS]
  frontend/src/content/docs/inventory.md · relation: semantically_similar_to
- `Cable` → `Rack`  [AMBIGUOUS]
  frontend/src/content/docs/cabling.md · relation: conceptually_related_to

## Knowledge Gaps
- **433 isolated node(s):** `DeviceRow`, `AssetRow`, `RackRow`, `ServiceRow`, `VlanRow` (+428 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1616 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **56 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Monitoring doc (V7)` and `Stats strip & saved views`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._
- **What is the exact relationship between `Cable` and `Rack`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `js-yaml` connect `build-rack-library.mjs` to `rackula.ts`, `package.json`?**
  _High betweenness centrality (0.103) - this node is a cross-community bridge._
- **Why does `create_device()` connect `devices.py` to `Rack`, `Device`, `app-shell.tsx`, `IPAMError`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Why does `Device` connect `app-shell.tsx` to `devices-client.tsx`, `index.ts`, `useAsyncData()`, `devices.py`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Are the 69 inferred relationships involving `Device` (e.g. with `_filtered_devices()` and `_export_rows()`) actually correct?**
  _`Device` has 69 INFERRED edges - model-reasoned connections that need verification._
- **Are the 72 inferred relationships involving `IPAMError` (e.g. with `_get_cable()` and `_get_interface()`) actually correct?**
  _`IPAMError` has 72 INFERRED edges - model-reasoned connections that need verification._