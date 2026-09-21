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
  vrf_id: number;
  mac_address: string | null;
  vendor: string | null;
  hostname: string | null;
  status: IpStatus;
  role: IpRole | null;
  nat_inside_id: number | null;
  open_ports: number[] | null;
  device_type: string | null;
  serial_number: string | null;
  switch_name: string | null;
  switch_port: string | null;
  counter_location: string | null;
  custom_fields: Record<string, unknown> | null;
  import_batch_id: number | null;
  last_seen: string | null;
  notes: string | null;
  row_color: string | null;
  display_color: string | null;
  created_at: string;
  updated_at: string;
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
  mac_mismatches: number;
  certs_expiring: Certificate[];
  mac_mismatch_items: MacMismatchItem[];
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
