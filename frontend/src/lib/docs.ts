import type { ComponentType } from "react";
import {
  Building2,
  Cable,
  Container,
  Cpu,
  FolderTree,
  Globe,
  HardDrive,
  History,
  Inbox,
  LayoutDashboard,
  ListOrdered,
  Network,
  Palette,
  ScanLine,
  Search,
  Server,
  Settings,
  ShieldCheck,
  Tags,
  Upload,
  Users,
  Waypoints,
  Zap,
} from "lucide-react";

export type DocIcon = ComponentType<{ className?: string }>;

export const DOC_CATEGORIES = [
  { key: "getting-started", label: "Getting Started" },
  { key: "ipam", label: "IPAM" },
  { key: "inventory", label: "Inventory" },
  { key: "operations", label: "Operations" },
  { key: "system", label: "System" },
] as const;

export type DocCategory = (typeof DOC_CATEGORIES)[number]["key"];

export interface DocArticle {
  /** Matches src/content/docs/<slug>.md and the /docs/<slug> route. */
  slug: string;
  title: string;
  /** One line — shown on the index and as palette sub-label. */
  description: string;
  category: DocCategory;
  icon: DocIcon;
  /** Extra terms matched by searchDocs() (palette + index filter). */
  keywords?: string[];
}

export const DOC_ARTICLES: DocArticle[] = [
  // Getting Started
  {
    slug: "overview",
    title: "Overview",
    description: "What IpamBox is, the data model, and a tour of the UI.",
    category: "getting-started",
    icon: LayoutDashboard,
    keywords: ["intro", "home", "dashboard", "start", "about"],
  },
  {
    slug: "accounts-and-roles",
    title: "Accounts & Roles",
    description: "First-run setup, login, sessions, and the four permission tiers.",
    category: "getting-started",
    icon: Users,
    keywords: ["login", "password", "rbac", "admin", "viewer", "permissions", "users"],
  },
  {
    slug: "search-and-shortcuts",
    title: "Search & Shortcuts",
    description: "Command palette, IP jump, g-chords, and every keyboard binding.",
    category: "getting-started",
    icon: Search,
    keywords: ["keyboard", "hotkeys", "palette", "ctrl+k", "jump", "find"],
  },
  // IPAM
  {
    slug: "sites",
    title: "Sites",
    description: "Physical/logical locations at the top of the IPAM hierarchy.",
    category: "ipam",
    icon: Building2,
    keywords: ["location", "branch", "code", "site number"],
  },
  {
    slug: "vrfs",
    title: "VRFs",
    description: "Routing instances — overlapping address space done safely.",
    category: "ipam",
    icon: Waypoints,
    keywords: ["vrf", "routing", "rd", "overlap"],
  },
  {
    slug: "vlans",
    title: "VLANs",
    description: "VLAN groups and VLANs, linked to sites and prefixes.",
    category: "ipam",
    icon: Zap,
    keywords: ["vlan", "vid", "l2", "group"],
  },
  {
    slug: "subnets",
    title: "Subnets",
    description: "Prefixes, containers, overlap rules, allocation, and the subnet matrix.",
    category: "ipam",
    icon: Network,
    keywords: ["prefix", "cidr", "subnet", "matrix", "allocate", "grid", "print"],
  },
  {
    slug: "hierarchy",
    title: "Hierarchy Tree",
    description: "The Site → VRF → Prefix tree with roll-up utilization.",
    category: "ipam",
    icon: FolderTree,
    keywords: ["tree", "nesting", "utilization"],
  },
  {
    slug: "addresses",
    title: "IP Addresses",
    description: "Statuses, roles, NAT links, bulk ops, and CSV import/export.",
    category: "ipam",
    icon: Globe,
    keywords: ["ip", "address", "host", "mac", "nat", "csv", "bulk"],
  },
  // Inventory
  {
    slug: "circuits",
    title: "Circuits",
    description: "WAN circuits linked to sites — provider IDs, bandwidth, status.",
    category: "inventory",
    icon: Cable,
    keywords: ["wan", "bezeq", "line", "provider", "bandwidth"],
  },
  {
    slug: "certificates",
    title: "Certificates",
    description: "Certificate inventory with expiry countdown and alerts.",
    category: "inventory",
    icon: ShieldCheck,
    keywords: ["cert", "ssl", "tls", "expiry", "expiration"],
  },
  {
    slug: "inventory",
    title: "Inventory",
    description: "Hardware/software assets — vendor, model, serials, support status.",
    category: "inventory",
    icon: HardDrive,
    keywords: ["asset", "serial", "hardware", "software", "eol"],
  },
  {
    slug: "lists",
    title: "Custom Lists",
    description: "User-defined tables with typed columns and live IP resolution.",
    category: "inventory",
    icon: ListOrdered,
    keywords: ["list", "custom", "spreadsheet", "sheet", "table", "servers"],
  },
  {
    slug: "racks",
    title: "Racks",
    description: "Rack elevations, bayed rack groups, capacity rollups, and Rackula round-trip.",
    category: "inventory",
    icon: Container,
    keywords: ["rack", "elevation", "rackula", "cabinet", "u position", "datacenter", "group", "row", "power", "watts", "weight", "capacity"],
  },
  {
    slug: "devices",
    title: "Devices",
    description: "First-class hosts — rack placement, multi-IP ownership, health rollup.",
    category: "inventory",
    icon: Cpu,
    keywords: ["device", "server", "host", "unracked", "ilo", "management", "multi-ip", "carrier"],
  },
  {
    slug: "services",
    title: "Services",
    description: "The service catalog — beneficiaries, sites, and documentation links.",
    category: "inventory",
    icon: Server,
    keywords: ["service", "catalog", "app", "beneficiary"],
  },
  // Operations
  {
    slug: "discovery",
    title: "Discovery Inbox",
    description: "Newly found hosts from scans — confirm, reconcile, MAC mismatches.",
    category: "operations",
    icon: Inbox,
    keywords: ["discovered", "reconcile", "confirm", "new hosts", "drift"],
  },
  {
    slug: "scans",
    title: "Scans",
    description: "LAN scanning — pipeline, schedules, exclusions, and live progress.",
    category: "operations",
    icon: ScanLine,
    keywords: ["scan", "arp", "icmp", "quick scan", "schedule", "exclude"],
  },
  {
    slug: "import",
    title: "Import",
    description: "Excel workbook import — preview, per-sheet detection, commit/rollback.",
    category: "operations",
    icon: Upload,
    keywords: ["excel", "xlsx", "workbook", "upload", "migrate", "hebrew"],
  },
  {
    slug: "changelog",
    title: "Changelog",
    description: "Every create/update/delete with actor, timestamp, and field diffs.",
    category: "operations",
    icon: History,
    keywords: ["audit", "history", "diff", "log", "changes"],
  },
  // System
  {
    slug: "tags",
    title: "Tags",
    description: "Colored labels attachable to sites, VRFs, prefixes, and addresses.",
    category: "system",
    icon: Tags,
    keywords: ["tag", "label", "color"],
  },
  {
    slug: "settings",
    title: "Settings",
    description: "Every settings section — runtime values, backup, users, appearance.",
    category: "system",
    icon: Settings,
    keywords: ["config", "preferences", "administration", "options"],
  },
  {
    slug: "row-colors",
    title: "Row Colors & Color Rules",
    description: "Manual row tints and admin-managed conditional coloring.",
    category: "system",
    icon: Palette,
    keywords: ["color", "highlight", "rule", "tint"],
  },
];

const BY_SLUG = new Map(DOC_ARTICLES.map((a) => [a.slug, a]));

export function getDoc(slug: string): DocArticle | undefined {
  return BY_SLUG.get(slug);
}

export function docCategoryLabel(category: DocCategory): string {
  return DOC_CATEGORIES.find((c) => c.key === category)?.label ?? category;
}

export function docHref(slug: string): string {
  return `/docs/${slug}`;
}

/** Ranked match over title > description > keywords > slug. Empty q → []. */
export function searchDocs(q: string): DocArticle[] {
  const needle = q.trim().toLowerCase();
  if (!needle) return [];
  const score = (a: DocArticle): number => {
    let s = 0;
    if (a.title.toLowerCase().includes(needle)) s += 4;
    if (a.description.toLowerCase().includes(needle)) s += 2;
    if (a.slug.includes(needle)) s += 1;
    if (a.keywords?.some((k) => k.toLowerCase().includes(needle))) s += 1;
    return s;
  };
  return DOC_ARTICLES.map((a) => [score(a), a] as const)
    .filter(([s]) => s > 0)
    .sort((x, y) => y[0] - x[0])
    .map(([, a]) => a);
}
