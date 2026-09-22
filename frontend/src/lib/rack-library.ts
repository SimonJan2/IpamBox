/** Starter device catalog for the add-device form's library picker.
 *
 * Slugs double as Rackula `device_type` values on export, so keep them
 * stable lowercase-dash identifiers. `face_default` preselects the mounting
 * face; everything prefills the form and stays editable.
 */
import type { RackFace } from "@/types";

export interface LibraryDevice {
  slug: string;
  name: string;
  manufacturer: string;
  model: string;
  u_height: number;
  face_default: RackFace;
  colour: string;
  category: string;
}

export const RACK_LIBRARY: LibraryDevice[] = [
  { slug: "server-1u", name: "1U Server", manufacturer: "Generic", model: "1U Rack Server", u_height: 1, face_default: "front", colour: "#38bdf8", category: "server" },
  { slug: "server-2u", name: "2U Server", manufacturer: "Generic", model: "2U Rack Server", u_height: 2, face_default: "front", colour: "#0ea5e9", category: "server" },
  { slug: "server-4u", name: "4U Server", manufacturer: "Generic", model: "4U Rack Server", u_height: 4, face_default: "front", colour: "#0284c7", category: "server" },
  { slug: "switch-24p", name: "24-port Switch", manufacturer: "Generic", model: "24p L3 Switch", u_height: 1, face_default: "front", colour: "#34d399", category: "network" },
  { slug: "switch-48p", name: "48-port Switch", manufacturer: "Generic", model: "48p L3 Switch", u_height: 1, face_default: "front", colour: "#10b981", category: "network" },
  { slug: "router", name: "Router", manufacturer: "Generic", model: "Edge Router", u_height: 1, face_default: "front", colour: "#059669", category: "network" },
  { slug: "firewall-1u", name: "Firewall", manufacturer: "Generic", model: "1U Firewall", u_height: 1, face_default: "front", colour: "#f43f5e", category: "firewall" },
  { slug: "patch-panel-24", name: "Patch Panel 24", manufacturer: "Generic", model: "24p Cat6", u_height: 1, face_default: "front", colour: "#fbbf24", category: "patch-panel" },
  { slug: "patch-panel-48", name: "Patch Panel 48", manufacturer: "Generic", model: "48p Cat6A", u_height: 1, face_default: "front", colour: "#f59e0b", category: "patch-panel" },
  { slug: "pdu-1u", name: "Rack PDU", manufacturer: "Generic", model: "1U Switched PDU", u_height: 1, face_default: "rear", colour: "#a78bfa", category: "power" },
  { slug: "ups-2u", name: "UPS 2U", manufacturer: "Generic", model: "2U Line-Interactive UPS", u_height: 2, face_default: "front", colour: "#818cf8", category: "power" },
  { slug: "blank-1u", name: "Blank Panel", manufacturer: "Generic", model: "1U Blank", u_height: 1, face_default: "front", colour: "#64748b", category: "blank" },
  { slug: "brush-1u", name: "Brush Panel", manufacturer: "Generic", model: "1U Brush Strip", u_height: 1, face_default: "front", colour: "#94a3b8", category: "cable-management" },
  { slug: "shelf-1u", name: "Rack Shelf", manufacturer: "Generic", model: "1U Cantilever Shelf", u_height: 1, face_default: "front", colour: "#cbd5e1", category: "shelf" },
  { slug: "kvm-console", name: "KVM Console", manufacturer: "Generic", model: "1U LCD Console", u_height: 1, face_default: "front", colour: "#e2e8f0", category: "kvm" },
  { slug: "dell-r650", name: "Dell PowerEdge R650", manufacturer: "Dell", model: "PowerEdge R650", u_height: 1, face_default: "front", colour: "#38bdf8", category: "server" },
  { slug: "dell-r750", name: "Dell PowerEdge R750", manufacturer: "Dell", model: "PowerEdge R750", u_height: 2, face_default: "front", colour: "#0ea5e9", category: "server" },
  { slug: "dl380-g10", name: "HPE ProLiant DL380", manufacturer: "HPE", model: "ProLiant DL380 Gen10", u_height: 2, face_default: "front", colour: "#22d3ee", category: "server" },
  { slug: "udm-pro", name: "UniFi Dream Machine Pro", manufacturer: "Ubiquiti", model: "UDM-Pro", u_height: 1, face_default: "front", colour: "#34d399", category: "network" },
  { slug: "usw-48poe", name: "UniFi Switch 48 PoE", manufacturer: "Ubiquiti", model: "USW-48-PoE", u_height: 1, face_default: "front", colour: "#4ade80", category: "network" },
  { slug: "apc-sm1500", name: "APC Smart-UPS", manufacturer: "APC", model: "SMX1500RM2U", u_height: 2, face_default: "front", colour: "#a78bfa", category: "power" },
];
