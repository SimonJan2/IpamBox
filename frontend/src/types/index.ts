export type PrefixStatus = "container" | "active" | "reserved" | "deprecated";
export type IpStatus = "active" | "reserved" | "dhcp" | "discovered" | "offline";
export type ScanStatus = "queued" | "running" | "completed" | "failed" | "cancelled";
export type IpRole = "vip" | "vrrp" | "hsrp" | "glbp" | "carp" | "secondary";
export type RangeRole = "dhcp" | "pool" | "reserved";
export type VlanStatus = "active" | "reserved" | "deprecated";

export interface Tag {
  id: number;
  name: string;
  slug: string;
  color: string;
  description: string | null;
  sort_order: number | null;
  pinned: boolean;
  row_color: string | null;
  display_color: string | null;
  created_at: string;
}

export interface TagAssignment {
  id: number;
  tag_id: number;
  object_type: string;
  object_id: number;
}

export interface VlanGroup {
  id: number;
  name: string;
  description: string | null;
  vlan_count: number;
  created_at: string;
}

export interface Vlan {
  id: number;
  vid: number;
  name: string;
  group_id: number | null;
  site_id: number | null;
  status: VlanStatus;
  description: string | null;
  sort_order: number | null;
  pinned: boolean;
  row_color: string | null;
  display_color: string | null;
  created_at: string;
}

export interface IpRange {
  id: number;
  prefix_id: number;
  vrf_id: number;
  start_address: string;
  start_int: number;
  end_address: string;
  end_int: number;
  role: RangeRole;
  description: string | null;
  created_at: string;
}

/** POST /networks — the "add network" wizard payload. Creates the VLAN
 *  (or reuses `vlan_id`), prefix, protected gateway/DNS address rows and
 *  the DHCP range in a single transaction. */
export interface NetworkCreate {
  site_id?: number | null;
  vlan?: { vid: number; name: string; group_id?: number | null } | null;
  vlan_id?: number | null;
  prefix: {
    cidr: string;
    vrf_id: number;
    status?: PrefixStatus;
    description?: string | null;
  };
  gateway?: string | null;
  dns_servers?: string[] | null;
  dhcp_range?: { start: string; end: string; description?: string | null } | null;
}

export interface NetworkOut {
  vlan_id: number;
  prefix_id: number;
  ip_range_id: number | null;
  address_ids: number[];
}

export interface Site {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  code: string | null;
  site_number: number | null;
  size: string | null;
  is_active: boolean;
  contact: string | null;
  address: string | null;
  sort_order: number | null;
  pinned: boolean;
  row_color: string | null;
  display_color: string | null;
  created_at: string;
}

export interface Vrf {
  id: number;
  name: string;
  rd: string | null;
  description: string | null;
  site_id: number | null;
  sort_order: number | null;
  pinned: boolean;
  row_color: string | null;
  display_color: string | null;
  created_at: string;
}

export interface VlanRef {
  id: number;
  vid: number;
  name: string;
}

export interface Prefix {
  id: number;
  prefix: string;
  vrf_id: number;
  site_id: number | null;
  vlan_id: number | null;
  vlan: VlanRef | null;
  status: PrefixStatus;
  description: string | null;
  /** Gateway inside the prefix — the API keeps a protected "technical"
   *  address row in sync with this value. */
  gateway: string | null;
  /** Resolvers for the subnet — may live outside the prefix. */
  dns_servers: string[] | null;
  created_at: string;
  // null for IPv6 — 2^n host counts exceed Number.MAX_SAFE_INTEGER and are
  // meaningless; render '—' for capacity, used_ips stays real
  total_ips: number | null;
  usable_ips: number | null;
  used_ips: number;
  free_ips: number | null;
  utilization_pct: number | null;
  unusable_first: boolean;
  unusable_last: boolean;
}

export interface IpAddress {
  id: number;
  address: string;
  address_int: number;
  prefix_id: number;
  /** Pool/range this address falls inside, if any (informational — set
   *  automatically from ip_ranges membership). */
  ip_range_id: number | null;
  /** Role of the containing range — stamped by the API, not a column. */
  range_role: RangeRole | null;
  vrf_id: number;
  mac_address: string | null;
  vendor: string | null;
  hostname: string | null;
  status: IpStatus;
  role: IpRole | null;
  nat_inside_id: number | null;
  device_id: number | null;
  /** Resolved device name — stamped by the API, not a column. */
  device_name: string | null;
  open_ports: number[] | null;
  device_type: string | null;
  missed_scans: number;
  serial_number: string | null;
  switch_name: string | null;
  switch_port: string | null;
  /** Structured sibling of switch_name/switch_port — the far-end interface
   *  (usually a switch port) this address is patched into. */
  connected_interface_id: number | null;
  /** Resolved far-end port — stamped by the API, not a column. */
  connected_interface: ConnectedInterfaceRef | null;
  counter_location: string | null;
  custom_fields: Record<string, unknown> | null;
  import_batch_id: number | null;
  /** Provenance — who created/maintains the row:
   *  manual | import | scan | snmp | integration. */
  source: string;
  last_seen: string | null;
  notes: string | null;
  row_color: string | null;
  display_color: string | null;
  created_at: string;
  updated_at: string;
}

/** Resolved `connected_interface_id` — device name + port name. */
export interface ConnectedInterfaceRef {
  id: number;
  name: string;
  device_id: number;
  device_name: string;
}

export interface AddressPage {
  items: IpAddress[];
  total: number;
  prefix: string | null;
  usable_first: string | null;
  usable_last: string | null;
}

export interface ScanJob {
  id: number;
  cidr: string;
  vrf_id: number | null;
  prefix_id: number | null;
  status: ScanStatus;
  progress: number;
  total_hosts: number;
  hosts_discovered: number;
  hosts_new: number;
  error: string | null;
  started_at: string | null;
  finished_at: string | null;
  duration_seconds: number | null;
  created_at: string;
}

export interface MacMismatchItem {
  id: number;
  address: string;
  prefix_id: number;
  mac_was: string | null;
  mac_seen: string | null;
  flagged_at: string | null;
}

/** A cable_mismatch-flagged interface — V8.2's physical-layer twin. */
export interface CableMismatchItem {
  /** Interface id (the flagged port). */
  id: number;
  device_id: number;
  device: string;
  port: string;
  reason: string | null;
  detail: string | null;
  flagged_at: string | null;
}

export interface DashboardStats {
  sites_total: number;
  vrfs_total: number;
  prefixes_total: number;
  ips_total: number;
  ips_used: number;
  ips_free: number;
  utilization_pct: number;
  devices_active: number;
  devices_discovered: number;
  devices_offline: number;
  devices_reserved: number;
  scans_total: number;
  last_scan: ScanJob | null;
  circuits_total: number;
  certificates_total: number;
  certs_expiring_30d: number;
  assets_total: number;
  services_total: number;
  racks_total: number;
  rack_u_used: number;
  rack_u_total: number;
  mac_mismatches: number;
  /** Cable validation (V8.2) — interfaces carrying cable_mismatch. */
  cable_mismatches: number;
  /** Review center (V7.1): open findings across all sections. */
  review_open: number;
  /** Title of the highest-priority non-empty review section (or null). */
  review_worst: string | null;
  certs_expiring: Certificate[];
  mac_mismatch_items: MacMismatchItem[];
  cable_mismatch_items: CableMismatchItem[];
}

// --- Review center (V7.1): one queue for every flag ----------------------

export type ReviewEntityType =
  | "ip_address"
  | "device"
  | "certificate"
  | "mac_group"
  | "device_interface";

export interface ReviewItem {
  /** Together with the section key this is the dismissal tuple —
   *  POST /review/dismiss takes the same fields back. */
  entity_type: ReviewEntityType;
  entity_id: number;
  label: string;
  sub: string | null;
  detail: Record<string, unknown>;
  flagged_at: string | null;
  fingerprint: string;
  // Populated only on entries of a section's `dismissed` list.
  dismissed_at: string | null;
  dismissed_by: string | null;
  dismiss_notes: string | null;
}

export interface ReviewSection {
  key: string;
  title: string;
  /** Honest open-item count — `items`/`dismissed` are capped at ~50. */
  count: number;
  items: ReviewItem[];
  dismissed: ReviewItem[];
  /** Set when a section is inert by configuration (e.g. aging disabled). */
  note: string | null;
}

export interface ReviewOut {
  sections: ReviewSection[];
}

export interface PrefixNode {
  id: number;
  prefix: string;
  status: PrefixStatus;
  vlan_id: number | null;
  vlan_vid: number | null;
  vlan_name: string | null;
  description: string | null;
  used_ips: number;
  usable_ips: number | null; // null for IPv6 (see Prefix)
  utilization_pct: number | null;
  descendant_count: number;
  agg_used_ips: number;
  allocated_pct: number;
  children: PrefixNode[];
}

export interface VrfNode {
  id: number;
  name: string;
  rd: string | null;
  prefixes: PrefixNode[];
}

export interface SiteNode {
  id: number | null;
  name: string;
  slug: string | null;
  vrfs: VrfNode[];
}

export interface ChangeField {
  field: string;
  before: unknown;
  after: unknown;
}

export interface ChangeLogEntry {
  id: number;
  ts: string;
  actor: string;
  action: "create" | "update" | "delete";
  object_type: string;
  object_id: number | null;
  object_repr: string;
  changes: ChangeField[];
}

export type RoleName = "admin" | "operator" | "contributor" | "viewer";

export interface AuthStatus {
  initialized: boolean;
  authenticated: boolean;
  allow_insecure: boolean;
  username: string | null;
  role: RoleName | null;
  permissions: string[];
}

export interface ScanEvent {
  scan_id: number;
  status: string;
  phase: string;
  progress: number;
  cidr?: string;
  hosts_discovered?: number;
  hosts_new?: number;
  eta_seconds?: number | null;
  error?: string | null;
  /** Additive delta — IPs confirmed live since the last event (F15). */
  found?: string[];
}

export interface ScanConfig {
  networks: string[];
  exclude_networks: string[];
  only_configured: boolean;
  interval_minutes: number;
  detected_cidr: string | null;
  tcp_ports: number[];
}

export interface BackupFileInfo {
  name: string;
  size: number;
  created_at: string;
}

export interface BackupFilesOut {
  files: BackupFileInfo[];
  interval_minutes: number;
  keep: number;
}

export interface BackupPreview {
  format: string;
  format_version: number;
  app_version: string | null;
  alembic_revision: string | null;
  created_at: string | null;
  tables: Record<string, number>;
  warnings: string[];
  includes_users: boolean;
}

export interface RestoreReport {
  restored: Record<string, number>;
  warnings: string[];
  backup_created_at: string | null;
}

export type SettingSource = "db" | "env" | "default";

export interface LanInfo {
  iface: string | null;
  cidr: string | null;
  source: "worker" | "local" | null;
}

export interface SystemInfo {
  app_version: string;
  alembic_head: string | null;
  lan: LanInfo;
}

export interface SettingsValues {
  scan_networks: string[];
  scan_exclude_networks: string[];
  scan_only_configured: boolean;
  scan_interval_minutes: number;
  scan_min_interval_seconds: number;
  scan_max_hosts: number;
  scan_tcp_ports: number[];
  scan_interface: string;
  scan_icmp_timeout: number;
  scan_tcp_timeout: number;
  scan_concurrency: number;
  backup_interval_minutes: number;
  backup_keep: number;
  ipambox_session_hours: number;
  site_code_follow_site: boolean;
  // Scanner reconcile policy (Settings > Features)
  scan_marks_offline: boolean;
  scan_reactivates_offline: boolean;
  scan_new_hosts_discovered: boolean;
  scan_stored_mac_wins: boolean;
  scan_overwrites_hostname: boolean;
  scan_infers_device_type: boolean;
  scan_auto_create_prefix: boolean;
  scan_infers_vrf: boolean;
  // Lifecycle & retention — 0 = disabled
  scan_offline_grace_scans: number;
  discovery_expire_days: number;
  changelog_retention_days: number;
  scan_job_retention_days: number;
  cert_warn_days: number;
  rackula_base_url: string;
  // Monitoring (V7)
  monitoring_enabled: boolean;
  monitor_concurrency: number;
  monitor_http_timeout: number;
  notify_retention_days: number;
  // SNMP enrichment (V8)
  snmp_enabled: boolean;
  snmp_interval_minutes: number;
  snmp_concurrency: number;
  snmp_timeout: number;
  snmp_learns_interfaces: boolean;
  snmp_fills_connected: boolean;
  // SNMP trap receiver (V8.1)
  snmp_traps_enabled: boolean;
  snmp_trap_port: number;
}

export interface SettingsOut {
  values: SettingsValues;
  sources: Partial<Record<keyof SettingsValues, SettingSource>>;
  env: {
    database_url: string;
    redis_url: string;
    cors_origins: string[];
    ipambox_allow_insecure: boolean;
    ipambox_cookie_secure: boolean;
    ipambox_password_set: boolean;
    secret_key_configured: boolean;
    backup_dir: string;
  };
  system: SystemInfo;
}

export interface UserOut {
  id: number;
  username: string;
  role: RoleName;
  created_at: string;
}

export interface SessionOut {
  id: string;
  created_at: string | null;
  ip: string | null;
  ua: string | null;
  expires_in: number | null;
  current: boolean;
}

export type ImportBatchStatus = "draft" | "committed" | "failed";
export type AssetKind = "hardware" | "software";
export type SheetFamily =
  | "sites_master"
  | "circuits"
  | "certificates"
  | "assets"
  | "services"
  | "inventory"
  | "servers"
  | "site_sheet"
  | "empty"
  | "unknown";

export interface ImportBatch {
  id: number;
  filename: string;
  sha256: string;
  status: ImportBatchStatus;
  stats: Record<string, unknown> | null;
  actor: string | null;
  created_at: string;
  committed_at: string | null;
}

export interface SheetPreview {
  sheet: string;
  family: SheetFamily;
  rows: number;
  headers: string[];
  site_id: number | null;
  site_name: string | null;
  matched_by: "octet" | "code" | "name" | "override" | null;
  warnings: string[];
  /** set when the sheet is imported as a custom list */
  list_name?: string | null;
  /** inferred column defs for list-targeted sheets */
  list_columns?: ListColumn[] | null;
}

export interface RowResult {
  sheet: string;
  row: number;
  action: "create" | "update" | "skip" | "conflict" | "error";
  detail: string;
}

export interface Circuit {
  id: number;
  env: string | null;
  site_id: number | null;
  site_number: number | null;
  site_code: string | null;
  site_name: string | null;
  line_type: string | null;
  bezeq_circuit_id: string | null;
  node: string | null;
  bw_down: string | null;
  bw_up: string | null;
  wan_ip: string | null;
  app_client_num: string | null;
  app_client_name: string | null;
  app_service_type: string | null;
  contact: string | null;
  status: string | null;
  notes: string | null;
  is_retired: boolean;
  import_batch_id: number | null;
  sort_order: number | null;
  pinned: boolean;
  row_color: string | null;
  display_color: string | null;
  created_at: string;
}

export interface Certificate {
  id: number;
  platform: string | null;
  target: string | null;
  server_name: string | null;
  cert_name: string | null;
  expires_on: string | null;
  serial_raw: string | null;
  notes: string | null;
  import_batch_id: number | null;
  sort_order: number | null;
  pinned: boolean;
  row_color: string | null;
  display_color: string | null;
  created_at: string;
}

export interface Asset {
  id: number;
  kind: AssetKind;
  category: string | null;
  vendor: string | null;
  model: string | null;
  purpose: string | null;
  version: string | null;
  eol_on: string | null;
  support_status: string | null;
  serial_number: string | null;
  site_id: number | null;
  notes: string | null;
  import_batch_id: number | null;
  sort_order: number | null;
  pinned: boolean;
  row_color: string | null;
  display_color: string | null;
  created_at: string;
}

export interface Service {
  id: number;
  name: string | null;
  beneficiary: string | null;
  site_id: number | null;
  site_code: string | null;
  doc_path: string | null;
  test_info: string | null;
  notes: string | null;
  import_batch_id: number | null;
  sort_order: number | null;
  pinned: boolean;
  row_color: string | null;
  display_color: string | null;
  created_at: string;
}

// --- Global row colors (manual row_color + admin color_rules) --------------

export type ColorRuleOperator =
  | "eq"
  | "neq"
  | "contains"
  | "lt"
  | "gt"
  | "within_days";

export interface ColorRule {
  id: number;
  entity_type: string;
  field: string;
  operator: ColorRuleOperator;
  value: string;
  color: string;
  position: number;
}

/** Rule-targetable column metadata from GET /color-rules/fields. */
export interface ColorRuleFieldMeta {
  name: string;
  type: "text" | "date" | "bool" | "number" | "enum";
  values: string[] | null;
}

/** Paginated list envelope returned by the unbounded list routes.
 * `limit: null` = the caller asked for the full set. */
export interface Page<T> {
  items: T[];
  total: number;
  limit: number | null;
  offset: number;
}

// --- Custom lists (user-defined tables from workbook sheets) ----------------

export type ListColumnType =
  | "text"
  | "ip"
  | "date"
  | "select"
  | "number"
  | "url"
  | "owner";

export interface ListColumn {
  /** Positional key ("c0"…) — stable across renames; row data keys on it. */
  key: string;
  label: string;
  type: ListColumnType;
  /** select only */
  options?: string[] | null;
  /** ip only: comma-separated multi-value cells */
  multi?: boolean | null;
}

export interface CustomList {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  icon: string | null;
  columns: ListColumn[] | null;
  key_column: string | null;
  source_sheet: string | null;
  import_batch_id: number | null;
  sort_order: number | null;
  created_at: string;
  row_count: number;
}

export interface CustomListRow {
  id: number;
  list_id: number;
  data: Record<string, string> | null;
  site_id: number | null;
  sort_order: number | null;
  pinned: boolean;
  row_color: string | null;
  display_color: string | null;
  manually_edited: boolean;
  import_batch_id: number | null;
  created_at: string;
}

/** Live ip_addresses lookup for an ip-typed cell. */
export interface ResolvedIp {
  id: number;
  prefix_id: number;
  status: IpStatus;
  hostname: string | null;
  last_seen: string | null;
}

export interface ListRowsPage extends Page<CustomListRow> {
  /** ip -> the address-table row it resolves to (empty when none resolve) */
  resolved: Record<string, ResolvedIp>;
}

/** Import wizard: target a sheet as a custom list. */
export interface ListTarget {
  name?: string | null;
  key_column?: string | null;
  also_ipam: boolean;
}

// --- Racks (elevation view + Rackula round-trip) ----------------------------

export type RackFace = "front" | "rear" | "both";

/** Carrier tray layouts: halves = 2 side-by-side slots, quarters = 4,
 *  shelf = 1 full-width slot. Slot counts live in rack-collision.ts. */
export type SlotLayout = "halves" | "quarters" | "shelf";

export interface Rack {
  id: number;
  site_id: number | null;
  /** Bayed-row membership — group + left-to-right position inside it. */
  group_id: number | null;
  group_position: number | null;
  name: string;
  description: string | null;
  room: string | null;
  height_u: number;
  width: number;
  notes: string | null;
  pinned: boolean;
  sort_order: number | null;
  row_color: string | null;
  display_color: string | null;
  created_at: string;
  device_count: number;
  used_u: number;
  /** Transient aggregates — null when no device supplies a value (the UI
   *  hides them rather than showing a misleading zero). */
  group_name: string | null;
  power_w: number | null;
  weight_kg: number | null;
}

export interface RackGroup {
  id: number;
  site_id: number | null;
  name: string;
  description: string | null;
  pinned: boolean;
  sort_order: number | null;
  row_color: string | null;
  display_color: string | null;
  created_at: string;
  rack_count: number;
}

/** GET /rack-groups/{id} — the row view payload: member racks in
 *  group_position order, each with devices + aggregates. */
export interface RackGroupDetail extends RackGroup {
  racks: RackDetail[];
}

/** Resolved FK summary on a rack device — id for the link, label to show. */
export interface LinkedRef {
  id: number;
  label: string;
}

export interface IpRef extends LinkedRef {
  prefix_id: number;
}

export interface RackDevice {
  id: number;
  rack_id: number;
  name: string;
  device_type: string | null;
  u_position: number;
  u_height: number;
  face: RackFace;
  colour: string | null;
  category: string | null;
  manufacturer: string | null;
  model: string | null;
  asset_id: number | null;
  ip_address_id: number | null;
  /** Set on a carrier child — the tray device it rides in. */
  carrier_id: number | null;
  /** Child's index into the carrier's slot_layout. */
  slot: number | null;
  /** Non-null flags this device as a carrier tray. */
  slot_layout: SlotLayout | null;
  /** Nameplate draw / installed weight — feed rack + group capacity rollups. */
  watts: number | null;
  weight_kg: number | null;
  asset: LinkedRef | null;
  ip: IpRef | null;
  /** Live scan health of the linked IP — null when unlinked. */
  ip_status: IpStatus | null;
  ip_last_seen: string | null;
  /** L1 coverage for the elevation panel — cabled ports / total ports. */
  interface_count: number;
  cabled_count: number;
  source: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface RackDetail extends Rack {
  devices: RackDevice[];
}

/** POST /racks/{id}/devices payload (also one entry of the import body). */
export interface RackDeviceCreate {
  name: string;
  device_type?: string | null;
  /** Optional when mounting into a carrier — the server derives it. */
  u_position?: number | null;
  u_height?: number;
  face?: RackFace;
  colour?: string | null;
  category?: string | null;
  manufacturer?: string | null;
  model?: string | null;
  asset_id?: number | null;
  ip_address_id?: number | null;
  watts?: number | null;
  weight_kg?: number | null;
  source?: "manual" | "rackula";
  notes?: string | null;
  carrier_id?: number | null;
  slot?: number | null;
  slot_layout?: SlotLayout | null;
}

/** Import-payload entry: `carrier_key` groups a child under the carrier
 *  entry carrying the same key (real ids don't exist at import time). */
export interface RackDeviceImportItem extends RackDeviceCreate {
  carrier_key?: string | null;
}

export interface SkippedDevice {
  name: string | null;
  u_position: number | null;
  reason: string;
}

export interface RackImportResult {
  created: number;
  skipped: SkippedDevice[];
}

// --- Devices (first-class hosts — rack_devices grown up) -------------------

/** A host that may hold a rack placement and owns any number of IPs.
 *  rack_id null = unracked inventory. */
export interface Device {
  id: number;
  name: string;
  device_type: string | null;
  serial_number: string | null;
  site_id: number | null;
  asset_id: number | null;
  mac_address: string | null;
  // Placement — all null when unracked.
  rack_id: number | null;
  u_position: number | null;
  u_height: number | null;
  face: RackFace | null;
  carrier_id: number | null;
  slot: number | null;
  slot_layout: SlotLayout | null;
  colour: string | null;
  category: string | null;
  manufacturer: string | null;
  model: string | null;
  watts: number | null;
  weight_kg: number | null;
  custom_fields: Record<string, unknown> | null;
  source: string;
  notes: string | null;
  row_color: string | null;
  sort_order: number | null;
  pinned: boolean;
  import_batch_id: number | null;
  created_at: string;
  updated_at: string;
  // SNMP enrichment (V8) — snmp_cred itself is write-only and never
  // returned; snmp_cred_set only reports that one is stored.
  snmp_enabled: boolean;
  snmp_version: SnmpVersion | null;
  snmp_port: number;
  snmp_cred_set: boolean;
  snmp_sys_name: string | null;
  snmp_sys_descr: string | null;
  snmp_last_ok_at: string | null;
  snmp_last_trap_at: string | null;
  snmp_last_error: string | null;
  // API-stamped transients — not columns.
  display_color: string | null;
  /** Worst-of across linked IPs; null = unmonitored. */
  health: IpStatus | null;
  ip_count: number;
  /** L1 coverage — how many ports the device has and how many are cabled. */
  interface_count: number;
  cabled_count: number;
  /** V8.2 — ports carrying a cable_mismatch flag right now. */
  flagged_count: number;
}

export type SnmpVersion = "v1" | "v2c" | "v3";

/** Write-only credential accepted by PATCH /devices/{id} — encrypted to
 *  snmp_cred_enc and never returned. */
export interface SnmpCredIn {
  community?: string;
  user?: string;
  auth_key?: string;
  priv_key?: string;
  auth_proto?: "sha" | "md5" | "sha224" | "sha256" | "sha384" | "sha512";
  priv_proto?: "aes128" | "aes192" | "aes256" | "des" | "3des";
  /** v3 only — named contextName for context-scoped agents. */
  context?: string;
}

/** POST /devices/{id}/snmp/test — a live sysName/sysDescr probe. */
export interface SnmpTestResult {
  up: boolean;
  sys_name: string | null;
  sys_descr: string | null;
  error: string | null;
}

/** POST /devices/{id}/snmp/poll — one full enrichment pass inline. */
export interface SnmpPollResult {
  device_id: number;
  up: boolean;
  sys_name: string | null;
  sys_descr: string | null;
  interfaces_seen: number;
  interfaces_created: number;
  interfaces_updated: number;
  macs_learned: number;
  links_applied: number;
  links_skipped: number;
  lldp_neighbors: number;
  /** Cable validation (V8.2) — evaluated ports, open flags, deltas. */
  cable_checked: number;
  cable_flags: number;
  cable_flags_raised: number;
  cable_flags_cleared: number;
  cable_flags_new: {
    interface_id: number;
    interface: string;
    reason: string;
    detail: string;
  }[];
  error: string | null;
  errors: string[];
}

/** One of a device's IPs — link id/label plus scan status for the table. */
export interface DeviceIpRef extends LinkedRef {
  address: string;
  hostname: string | null;
  status: IpStatus;
  last_seen: string | null;
  prefix_id: number;
}

export interface DeviceDetail extends Device {
  ips: DeviceIpRef[];
  asset: LinkedRef | null;
  site: LinkedRef | null;
  rack: LinkedRef | null;
  carrier: LinkedRef | null;
}

// --- Cabling (V4A): device interfaces + cables -----------------------------

export type InterfaceKind =
  | "rj45"
  | "sfp"
  | "sfp28"
  | "qsfp"
  | "console"
  | "patch"
  | "power"
  | "other";

export type CableKind =
  | "cat5e"
  | "cat6"
  | "cat6a"
  | "dac"
  | "fiber_sm"
  | "fiber_mm"
  | "power"
  | "console"
  | "other";

/** The far end of an interface's cable — enough to label and link it. */
export interface InterfacePeer {
  cable_id: number;
  cable_kind: CableKind;
  cable_label: string | null;
  interface_id: number;
  interface_name: string;
  device_id: number;
  device_name: string;
}

/** Resolved `connected_ip_id` — the IP this port serves. */
export interface ConnectedIpRef {
  id: number;
  label: string;
  prefix_id: number;
}

/** One LLDP neighbor observed on a port (V8.2 evidence blob). */
export interface LldpNeighbor {
  remote_name: string | null;
  remote_port: string | null;
  remote_mac: string | null;
  local_port_id: string | null;
}

/** A cable_mismatch flag — a finding, never a fix. */
export interface CableMismatchFlag {
  reason: "documented_down" | "far_end_absent" | "lldp_neighbor" | string;
  detail: string | null;
  at: string | null;
  cable_id?: number | null;
  remote_name?: string | null;
  remote_port?: string | null;
}

/** The observed L1 evidence blob on an interface (V8.2). */
export interface InterfaceValidation {
  cable_mismatch?: CableMismatchFlag;
  lldp?: LldpNeighbor[];
  macs_seen?: string[];
  notes?: string[];
  checked_at?: string;
}

/** One named port/NIC on a device. `pair_interface_id` links a patch
 *  position's front and back ports on the same (panel) device. */
export interface DeviceInterface {
  id: number;
  device_id: number;
  name: string;
  kind: InterfaceKind;
  speed_mbps: number | null;
  mac_address: string | null;
  position: number;
  connected_ip_id: number | null;
  pair_interface_id: number | null;
  /** SNMP-observed state (V8) — null on ports the poller never reported. */
  if_index: number | null;
  oper_status: string | null;
  admin_status: string | null;
  snmp_seen_at: string | null;
  /** V8.2 — observed L1 evidence; cable_mismatch key = flagged port. */
  validation: InterfaceValidation | null;
  /** Provenance — manual | snmp (poller-owned). */
  source: string;
  created_at: string;
  updated_at: string;
  // Resolved by the API — not columns.
  peer: InterfacePeer | null;
  connected_ip: ConnectedIpRef | null;
}

/** One cable termination resolved for display. */
export interface CableEnd {
  interface_id: number;
  interface_name: string;
  device_id: number;
  device_name: string;
}

export interface Cable {
  id: number;
  a_interface_id: number;
  b_interface_id: number;
  kind: CableKind;
  color: string | null;
  label: string | null;
  length_m: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  a: CableEnd | null;
  b: CableEnd | null;
}

/** One step of an L1 path. cable_* are null on the start hop and on
 *  patch-panel front→back pair hops (the pass-through isn't a cable). */
export interface CableTraceHop {
  device_id: number;
  device_name: string;
  interface_id: number;
  interface_name: string;
  cable_id: number | null;
  cable_kind: CableKind | null;
  cable_label: string | null;
}

/** Report of the legacy switch_name/switch_port → connected_interface_id
 *  matcher (POST /interfaces/match-free-text). */
export interface MatchFreeTextReport {
  matched: number;
  ambiguous: number;
  unmatched: number;
  matched_ids: number[];
  ambiguous_ids: number[];
  unmatched_ids: number[];
}

// --- Monitoring (V7): per-target health checks + notification channels ------

export type MonitorKind = "ping" | "tcp" | "http";
export type MonitorState = "up" | "down" | "unknown";

export interface MonitorTarget {
  id: number;
  device_id: number | null;
  address_id: number | null;
  kind: MonitorKind;
  port: number | null;
  http_path: string;
  http_expect: string | null;
  interval_seconds: number;
  down_after: number;
  enabled: boolean;
  state: MonitorState;
  consecutive_failures: number;
  last_checked_at: string | null;
  last_change_at: string | null;
  last_error: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  // API-stamped display fields — not columns.
  target_label: string | null;
  resolved_ip: string | null;
  device_name: string | null;
}

export interface MonitorSummary {
  up: number;
  down: number;
  unknown: number;
  due: number;
}

export type ChannelKind = "webhook" | "smtp" | "discord" | "telegram";

/** Secret material never reaches the client: `secret_set` says whether
 *  `secret_enc` holds a value; `config` carries only non-secret fields. */
export interface NotificationChannel {
  id: number;
  name: string;
  kind: ChannelKind;
  enabled: boolean;
  created_at: string;
  config: Record<string, unknown>;
  secret_set: boolean;
}

export interface ChannelTestOut {
  ok: boolean;
  error: string | null;
}

export interface NotificationLogEntry {
  id: number;
  channel_id: number | null;
  event_type: string;
  summary: string;
  ok: boolean;
  error: string | null;
  created_at: string;
  channel_name: string | null;
}
