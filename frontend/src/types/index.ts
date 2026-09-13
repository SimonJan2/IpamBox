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
  created_at: string;
}

export interface Vrf {
  id: number;
  name: string;
  rd: string | null;
  description: string | null;
  site_id: number | null;
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
  total_ips: number;
  usable_ips: number;
  used_ips: number;
  free_ips: number;
  utilization_pct: number;
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
  last_seen: string | null;
  notes: string | null;
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
}

export interface PrefixNode {
  id: number;
  prefix: string;
  status: PrefixStatus;
  vlan_id: number | null;
  vlan_name: string | null;
  description: string | null;
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

export interface AuthStatus {
  initialized: boolean;
  authenticated: boolean;
  allow_insecure: boolean;
  username: string | null;
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
}

export interface RestoreReport {
  restored: Record<string, number>;
  warnings: string[];
  backup_created_at: string | null;
}
