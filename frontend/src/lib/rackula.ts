/** Rackula wire-format interop: share URLs (?l= LZ-string MinimalLayoutV2) and
 * .Rackula.zip (layout.yaml full Layout object).
 *
 * Position conventions verified against upstream
 * (src/lib/utils/share.ts, src/lib/schemas/{index,share,migrations}.ts):
 *
 * - Share `p` is the 1-based human U (U1 -> p=1) for rack-level gear; on a
 *   carrier child (`ci` set) it's the raw 0-indexed slot position.
 * - YAML `position` is internal 1/6-U units: U1 -> 6, so u = position / 6.
 *   Files with `version` missing or < 0.7.0 (or any rail position < 6) are
 *   legacy whole-U — position is the U number directly. On a container child
 *   (`container_id` set) position is 0-indexed relative to the container.
 * - Carriers: share `ci`/`si`/`a` and YAML `container_id`/`slot_id`/
 *   `auto_created` map onto IpamBox carrier_id/slot/slot_layout. `a`/
 *   `auto_created` carriers import as a "shelf"-layout row named "Shelf".
 */
import JSZip from "jszip";
import yaml from "js-yaml";
import LZString from "lz-string";

import { slotCount, slotLabel } from "@/lib/rack-collision";
import type {
  RackDevice,
  RackDeviceCreate,
  RackFace,
  SlotLayout,
} from "@/types";

export const UNITS_PER_U = 6;
const SCHEMA_VERSION = "1.1";
// `version` is the writer's app version; anything < 0.7.0 makes Rackula treat
// positions as whole-U and migrate (x6). Ours must stay >= the cutoff.
const WRITER_VERSION = "1.1.0";
const POSITION_FORMAT_CUTOFF = "0.7.0";
const FALLBACK_COLOUR = "#64748b";

/** Upstream DeviceCategory values (schemas/index.ts DeviceCategorySchema). */
export const RACKULA_CATEGORIES = [
  "server", "network", "firewall", "patch-panel", "power", "storage", "kvm",
  "av-media", "cooling", "shelf", "blank", "cable-management", "chassis",
  "other",
] as const;

const CATEGORY_TO_ABBREV: Record<string, string> = {
  server: "s", network: "n", firewall: "r", "patch-panel": "p", power: "w",
  storage: "t", kvm: "k", "av-media": "a", cooling: "l", shelf: "f",
  blank: "b", "cable-management": "c", chassis: "h", other: "o",
};
const ABBREV_TO_CATEGORY: Record<string, string> = Object.fromEntries(
  Object.entries(CATEGORY_TO_ABBREV).map(([k, v]) => [v, k]),
);

export interface ImportDevice {
  name: string;
  device_type: string | null;
  u_position: number;
  u_height: number;
  face: RackFace;
  colour: string | null;
  category: string | null;
  manufacturer: string | null;
  model: string | null;
  notes: string | null;
  /** Links a child to the carrier entry carrying the same key (real DB ids
   *  don't exist at import time). On a carrier entry it's the self-key. */
  carrier_key: string | null;
  /** Child's index into the carrier's layout. */
  slot: number | null;
  /** Non-null flags this entry as a carrier tray. */
  slot_layout: SlotLayout | null;
}

export interface ImportSkip {
  name: string | null;
  u_position: number | null;
  reason: string;
}

export interface ParsedImport {
  rack_name: string | null;
  rack_height: number | null;
  rack_count: number;
  devices: ImportDevice[];
  skipped: ImportSkip[];
  notes: string[];
}

interface ExportRack {
  name: string;
  height_u: number;
  width: number;
}

type DeviceLike = Pick<
  RackDeviceCreate,
  "name" | "device_type" | "u_position" | "u_height" | "face" | "colour" | "category" | "manufacturer" | "model" | "notes" | "carrier_id" | "slot" | "slot_layout"
> & { id?: number };

const FACES: RackFace[] = ["front", "rear", "both"];

function slugify(s: string): string {
  const slug = s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
  return slug || "device";
}

function canonicalCategory(c: string | null | undefined): string {
  const k = (c ?? "").toLowerCase().trim();
  return (RACKULA_CATEGORIES as readonly string[]).includes(k) ? k : "other";
}

function clip(s: string | null | undefined, n: number): string | undefined {
  return s ? s.slice(0, n) : undefined;
}

function uuid(): string {
  // crypto.randomUUID is secure-context only; this is a layout id, not a secret.
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    return (c === "x" ? r : (r & 0x3) | 0x8).toString(16);
  });
}

function majorOf(v: string): number {
  const n = parseInt(v.trim().split(".")[0] ?? "", 10);
  return Number.isFinite(n) ? n : 0;
}

function compareVersions(a: string, b: string): number {
  const pa = a.trim().split(/[-+]/)[0].split(".").map((p) => parseInt(p) || 0);
  const pb = b.trim().split(/[-+]/)[0].split(".").map((p) => parseInt(p) || 0);
  for (let i = 0; i < Math.max(pa.length, pb.length); i++) {
    const d = (pa[i] ?? 0) - (pb[i] ?? 0);
    if (d !== 0) return d < 0 ? -1 : 1;
  }
  return 0;
}

/** Slot grid a layout advertises to Rackula (share `sl` / yaml `slots`):
 *  halves = 1×2, quarters = 2×2, shelf = one full-width slot. Slot ids are
 *  just the index as a string — our own importer reads the same shape. */
function slotsFor(layout: SlotLayout | null | undefined) {
  const n = slotCount(layout);
  return Array.from({ length: n }, (_, i) => ({
    id: String(i),
    r: layout === "quarters" ? Math.floor(i / 2) : 0,
    cl: n > 1 ? i % 2 : 0,
  }));
}

/** Rackula slot_width for a layout: shelf slots are full-width (2),
 *  halves/quarters slots are half-width (1). */
function slotWidth(layout: SlotLayout | null | undefined): 1 | 2 {
  return layout === "shelf" ? 2 : 1;
}

/** One device-type definition per distinct type, slugs deduplicated. */
function deviceTypeTables(devices: DeviceLike[]) {
  const slugFor = new Map<DeviceLike, string>();
  const seen = new Map<string, number>();
  const types = new Map<string, DeviceLike>();
  for (const d of devices) {
    const base = slugify(d.device_type || d.name || "device");
    let slug = base;
    const clash = types.get(slug);
    if (clash && (clash.u_height ?? 1) !== (d.u_height ?? 1)) {
      // Same slug, different height — keep both types distinct.
      let n = (seen.get(base) ?? 1) + 1;
      while (types.has(`${base}-${n}`)) n++;
      slug = `${base}-${n}`;
      seen.set(base, n);
    }
    slugFor.set(d, slug);
    if (!types.has(slug)) types.set(slug, d);
  }
  return { slugFor, types };
}

// ------------------------------------------------------------------ export

export function encodeShareUrl(
  baseUrl: string,
  rack: ExportRack,
  devices: DeviceLike[],
): string {
  const { slugFor, types } = deviceTypeTables(devices);
  // carrier db id -> index in the emitted device list (children's `ci`).
  const carrierIndex = new Map<number, number>();
  devices.forEach((d, i) => {
    if (d.id != null && d.slot_layout) carrierIndex.set(d.id, i);
  });
  const payload = {
    v: WRITER_VERSION,
    fv: 2,
    n: clip(rack.name, 100) ?? "rack",
    rs: [
      {
        i: "0",
        n: clip(rack.name, 100) ?? "rack",
        h: rack.height_u,
        w: rack.width === 10 ? 10 : 19,
        d: devices.map((d) => {
          const ci =
            d.carrier_id != null ? carrierIndex.get(d.carrier_id) : undefined;
          return {
            t: slugFor.get(d)!,
            // On a carrier child, p is the raw slot index (fv 2 encoding).
            p: ci !== undefined ? (d.slot ?? 0) : d.u_position,
            f: d.face ?? "front",
            ...(d.name ? { n: clip(d.name, 100) } : {}),
            ...(ci !== undefined
              ? { ci, si: String(d.slot ?? 0) }
              : {}),
          };
        }),
      },
    ],
    dt: [...types.entries()].map(([slug, d]) => ({
      s: slug,
      h: d.u_height ?? 1,
      ...(d.manufacturer ? { mf: clip(d.manufacturer, 100) } : {}),
      ...(d.model ? { m: clip(d.model, 100) } : {}),
      c: d.colour ?? FALLBACK_COLOUR,
      x: CATEGORY_TO_ABBREV[canonicalCategory(d.category)],
      ...(d.slot_layout
        ? { sl: slotsFor(d.slot_layout), sw: slotWidth(d.slot_layout), sr: "parent" }
        : d.carrier_id != null
          ? { sr: "child" }
          : {}),
    })),
  };
  const base = baseUrl.replace(/\/+$/, "");
  return `${base}/?l=${LZString.compressToEncodedURIComponent(JSON.stringify(payload))}`;
}

export async function exportZip(
  rack: ExportRack,
  devices: DeviceLike[],
): Promise<Blob> {
  const { slugFor, types } = deviceTypeTables(devices);
  const layout = {
    version: WRITER_VERSION,
    name: clip(rack.name, 100) ?? "rack",
    metadata: {
      id: uuid(),
      name: clip(rack.name, 100) ?? "rack",
      schema_version: SCHEMA_VERSION,
    },
    racks: [
      {
        id: "rack-1",
        name: clip(rack.name, 100) ?? "rack",
        height: rack.height_u,
        width: rack.width === 10 ? 10 : 19,
        desc_units: false,
        show_rear: true,
        form_factor: "4-post-cabinet",
        starting_unit: 1,
        position: 0,
        devices: devices.map((d, i) => {
          const carrier =
            d.carrier_id != null
              ? devices.find((x) => x.id === d.carrier_id && x.slot_layout)
              : undefined;
          return {
            id: `dev-${d.id ?? i}`,
            device_type: slugFor.get(d)!,
            // Container children: position is 0-indexed within the carrier —
            // we store the slot index, matching what our importer emits.
            position: carrier ? (d.slot ?? 0) : (d.u_position ?? 1) * UNITS_PER_U,
            face: d.face ?? "front",
            ...(d.name ? { name: clip(d.name, 100) } : {}),
            ...(d.notes ? { notes: clip(d.notes, 1000) } : {}),
            ...(carrier
              ? {
                  container_id: `dev-${carrier.id}`,
                  slot_id: String(d.slot ?? 0),
                }
              : {}),
          };
        }),
      },
    ],
    device_types: [...types.entries()].map(([slug, d]) => ({
      slug,
      u_height: d.u_height ?? 1,
      ...(d.manufacturer ? { manufacturer: clip(d.manufacturer, 100) } : {}),
      ...(d.model ? { model: clip(d.model, 100) } : {}),
      colour: d.colour ?? FALLBACK_COLOUR,
      category: canonicalCategory(d.category),
      ...(d.slot_layout
        ? {
            slot_width: slotWidth(d.slot_layout),
            subdevice_role: "parent",
            slots: slotsFor(d.slot_layout).map((s) => ({
              id: s.id,
              position: { row: s.r, col: s.cl },
            })),
          }
        : d.carrier_id != null
          ? { subdevice_role: "child" }
          : {}),
    })),
    settings: { display_mode: "label", show_labels_on_images: false },
  };
  const zip = new JSZip();
  zip.file("layout.yaml", yaml.dump(layout));
  return zip.generateAsync({ type: "blob" });
}

// ------------------------------------------------------------------ import

interface MinimalDeviceType {
  s: string;
  h?: number;
  mf?: string;
  m?: string;
  c?: string;
  x?: string;
  /** Container device types carry their slot grid. */
  sl?: { id?: string }[];
  /** Slot width: 1 = half-width slots, 2 = full-width. */
  sw?: number;
  /** Subdevice role: "parent" = carrier. */
  sr?: string;
}

/** Our three carrier layouts from a Rackula slot array: 2 side-by-side
 *  half-width slots -> halves, 4 -> quarters, anything else -> shelf. */
function layoutFromSlots(n: number): SlotLayout {
  if (n === 2) return "halves";
  if (n === 4) return "quarters";
  return "shelf";
}

export function decodeShareUrl(url: string): ParsedImport {
  let parsed: URL;
  try {
    parsed = new URL(url.trim());
  } catch {
    throw new Error("not a URL — paste a Rackula share link");
  }
  const l = parsed.searchParams.get("l");
  if (!l) throw new Error("no layout payload — expected a ?l= share link");
  const json = LZString.decompressFromEncodedURIComponent(l);
  if (!json) throw new Error("corrupt share payload (lz-string decode failed)");
  const data = JSON.parse(json) as Record<string, unknown>;

  const dtBySlug = new Map<string, MinimalDeviceType>(
    ((data.dt as MinimalDeviceType[] | undefined) ?? []).map((t) => [t.s, t]),
  );
  const racks = Array.isArray(data.rs)
    ? (data.rs as Record<string, unknown>[])
    : data.r
      ? [data.r as Record<string, unknown>]
      : [];
  if (!racks.length) throw new Error("share payload has no racks");

  const out = emptyImport();
  out.rack_count = racks.length;
  if (racks.length > 1) {
    out.notes.push(`layout has ${racks.length} racks — imported the first`);
  }
  const rack = racks[0];
  out.rack_name = typeof rack.n === "string" ? rack.n : null;
  out.rack_height = typeof rack.h === "number" ? rack.h : null;

  const devs = (rack.d as Record<string, unknown>[] | undefined) ?? [];

  // Pass A — which indexes are carriers? Any entry referenced by a child's
  // `ci`, or flagged `a` (Rackula synthesizes these trays automatically).
  const carrierIdxs = new Set<number>();
  devs.forEach((d, i) => {
    if (d.a) carrierIdxs.add(i);
    const ci = Number(d.ci);
    if (d.ci !== undefined && Number.isInteger(ci) && ci >= 0 && ci < devs.length) {
      carrierIdxs.add(ci);
    }
  });

  const carrierU = (ci: number): number => {
    const p = Number(devs[ci]?.p);
    return Number.isInteger(p) && p >= 1 ? p : 1;
  };

  devs.forEach((d, i) => {
    const t = dtBySlug.get(String(d.t ?? ""));
    const label = String(d.n ?? d.t ?? "device");
    const face = String(d.f ?? "front") as RackFace;
    const h = t?.h ?? 1;
    const base = {
      device_type: String(d.t ?? "") || null,
      face: FACES.includes(face) ? face : ("front" as RackFace),
      colour: t?.c ?? null,
      category: t?.x ? (ABBREV_TO_CATEGORY[t.x] ?? "other") : null,
      manufacturer: t?.mf ?? null,
      model: t?.m ?? null,
      notes: null,
    };

    if (carrierIdxs.has(i)) {
      // Carrier row — `a` marks an auto-created tray: import it as a
      // "shelf"-layout carrier named "Shelf". Explicit carriers take their
      // layout from the device type's slot grid (sl).
      const p = Number(d.p);
      if (!Number.isInteger(p) || p < 1) {
        skip(out, label, null, "carrier at a sub-U position — can't place it");
        return;
      }
      if (!FACES.includes(face)) {
        skip(out, label, p, `unknown face "${String(d.f)}"`);
        return;
      }
      if (!Number.isInteger(h) || h < 1) {
        skip(out, label, p, "sub-U height — IpamBox tracks whole-U only");
        return;
      }
      const auto = Boolean(d.a);
      const slot_layout = auto ? "shelf" : layoutFromSlots(t?.sl?.length ?? 1);
      out.devices.push({
        name: auto ? "Shelf" : label.slice(0, 255),
        u_position: p,
        u_height: h,
        carrier_key: `s${i}`,
        slot: null,
        slot_layout,
        ...base,
      });
      return;
    }

    if (d.ci !== undefined) {
      // Carrier child — `p` is the raw slot index; `si` is the parent's
      // slot id (fallback for resolving the index via the type's slot list).
      const ci = Number(d.ci);
      if (!Number.isInteger(ci) || ci < 0 || ci >= devs.length) {
        skip(out, label, null, "carrier not in the layout");
        return;
      }
      if (!Number.isInteger(h) || h < 1) {
        skip(out, label, null, "sub-U height — IpamBox tracks whole-U only");
        return;
      }
      let slot = Number(d.p);
      const pt = dtBySlug.get(String(devs[ci]?.t ?? ""));
      if ((!Number.isInteger(slot) || slot < 0) && typeof d.si === "string") {
        const idx = (pt?.sl ?? []).findIndex((s) => s.id === d.si);
        if (idx >= 0) slot = idx;
      }
      out.devices.push({
        name: label.slice(0, 255),
        u_position: carrierU(ci),
        u_height: h,
        carrier_key: `s${ci}`,
        slot: Number.isInteger(slot) && slot >= 0 ? slot : null,
        slot_layout: null,
        ...base,
      });
      return;
    }

    const p = Number(d.p);
    if (!Number.isInteger(p) || p < 1) {
      skip(out, label, null, "sub-U position — not a whole U slot");
      return;
    }
    if (!FACES.includes(face)) {
      skip(out, label, p, `unknown face "${String(d.f)}"`);
      return;
    }
    if (!Number.isInteger(h) || h < 1) {
      skip(out, label, p, "sub-U height — IpamBox tracks whole-U only");
      return;
    }
    out.devices.push({
      name: label.slice(0, 255),
      u_position: p,
      u_height: h,
      carrier_key: null,
      slot: null,
      slot_layout: null,
      ...base,
    });
  });
  return out;
}

export async function parseZip(data: Blob | ArrayBuffer): Promise<ParsedImport> {
  const zip = await JSZip.loadAsync(data);
  const file = zip.file("layout.yaml") ?? zip.file("layout.yml");
  if (!file) throw new Error("no layout.yaml inside the archive");
  const doc = yaml.load(await file.async("text")) as Record<
    string,
    unknown
  > | null;
  if (!doc || typeof doc !== "object") throw new Error("layout.yaml is invalid");

  // Same gate as upstream assertSchemaVersionSupported: reject only a NEWER
  // major, before touching anything — the file is never modified.
  const sv = (doc.metadata as { schema_version?: unknown } | undefined)
    ?.schema_version;
  if (sv !== undefined && majorOf(String(sv)) > majorOf(SCHEMA_VERSION)) {
    throw new Error(
      `layout was made by a newer Rackula (format ${sv}) — file not changed`,
    );
  }

  const racks = Array.isArray(doc.racks) && doc.racks.length
    ? (doc.racks as Record<string, unknown>[])
    : doc.rack
      ? [doc.rack as Record<string, unknown>]
      : [];
  if (!racks.length) throw new Error("layout has no racks");

  const out = emptyImport();
  out.rack_count = racks.length;
  if (racks.length > 1) {
    out.notes.push(`layout has ${racks.length} racks — imported the first`);
  }
  const rack = racks[0];
  out.rack_name = typeof rack.name === "string" ? rack.name : null;
  out.rack_height = typeof rack.height === "number" ? rack.height : null;

  const dtBySlug = new Map<string, Record<string, unknown>>(
    ((doc.device_types as Record<string, unknown>[] | undefined) ?? [])
      .filter((t) => typeof t.slug === "string")
      .map((t) => [t.slug as string, t]),
  );

  // Legacy detection mirrors upstream needsPositionMigration: a missing or
  // pre-0.7.0 `version`, or any rail position in [1,6), means whole-U values.
  const devices = (rack.devices as Record<string, unknown>[] | undefined) ?? [];
  const legacy =
    typeof doc.version !== "string" ||
    compareVersions(doc.version, POSITION_FORMAT_CUTOFF) < 0 ||
    devices.some(
      (d) =>
        !d.container_id &&
        typeof d.position === "number" &&
        d.position >= 1 &&
        d.position < UNITS_PER_U,
    );

  /** Rail position -> U under the file's position format, else null. */
  const posToU = (pos: number): number | null => {
    if (legacy) {
      return Number.isInteger(pos) && pos >= 1 ? pos : null;
    }
    return Number.isInteger(pos) && pos % UNITS_PER_U === 0 && pos >= UNITS_PER_U
      ? pos / UNITS_PER_U
      : null;
  };

  // Pass A — which device ids are carriers? Referenced by a child's
  // container_id, or flagged auto_created (Rackula-synthesized tray).
  const byId = new Map<string, Record<string, unknown>>();
  for (const d of devices) {
    if (d.id !== undefined && d.id !== null) byId.set(String(d.id), d);
  }
  const carrierIds = new Set<string>();
  for (const d of devices) {
    if (d.auto_created && d.id !== undefined) carrierIds.add(String(d.id));
    if (d.container_id !== undefined && d.container_id !== null) {
      carrierIds.add(String(d.container_id));
    }
  }

  for (const d of devices) {
    const slug = String(d.device_type ?? "");
    const t = dtBySlug.get(slug);
    const label = String(d.name ?? slug ?? "device");
    const face = String(d.face ?? "front") as RackFace;
    const h = Number(t?.u_height ?? 1);
    const colour =
      (typeof d.colour_override === "string" ? d.colour_override : null) ??
      (typeof t?.colour === "string" ? (t.colour as string) : null);
    const base = {
      device_type: slug || null,
      face: FACES.includes(face) ? face : ("front" as RackFace),
      colour,
      category: typeof t?.category === "string" ? (t.category as string) : null,
      manufacturer:
        typeof t?.manufacturer === "string" ? (t.manufacturer as string) : null,
      model: typeof t?.model === "string" ? (t.model as string) : null,
      notes: typeof d.notes === "string" ? (d.notes as string) : null,
    };

    const myId = d.id !== undefined && d.id !== null ? String(d.id) : null;
    if (myId !== null && carrierIds.has(myId)) {
      // Carrier row — auto_created = Rackula-synthesized tray: import it as
      // a "shelf"-layout carrier named "Shelf". Explicit carriers take their
      // layout from the device type's slots[] grid.
      const u = posToU(Number(d.position));
      if (u === null) {
        skip(out, label, null, "carrier at a sub-U position — can't place it");
        continue;
      }
      if (!FACES.includes(face)) {
        skip(out, label, u, `unknown face "${String(d.face)}"`);
        continue;
      }
      if (!Number.isInteger(h) || h < 1) {
        skip(out, label, u, "sub-U height — IpamBox tracks whole-U only");
        continue;
      }
      const auto = Boolean(d.auto_created);
      const slots = (t?.slots as { id?: string }[] | undefined) ?? [];
      out.devices.push({
        name: auto ? "Shelf" : label.slice(0, 255),
        u_position: u,
        u_height: h,
        carrier_key: `z${myId}`,
        slot: null,
        slot_layout: auto ? "shelf" : layoutFromSlots(slots.length),
        ...base,
      });
      continue;
    }

    if (d.container_id !== undefined && d.container_id !== null) {
      // Carrier child — position is 0-indexed relative to the container;
      // slot_id names a slot in the carrier type's slots[] grid.
      const cid = String(d.container_id);
      const carrier = byId.get(cid);
      if (!carrier) {
        skip(out, label, null, "carrier not in the layout");
        continue;
      }
      if (!Number.isInteger(h) || h < 1) {
        skip(out, label, null, "sub-U height — IpamBox tracks whole-U only");
        continue;
      }
      const carrierType = dtBySlug.get(String(carrier.device_type ?? ""));
      const slots =
        (carrierType?.slots as { id?: string }[] | undefined) ?? [];
      let slot = slots.findIndex((s) => s.id === d.slot_id);
      if (slot < 0) {
        const rel = Number(d.position);
        slot = Number.isInteger(rel) && rel >= 0 ? rel : -1;
      }
      const cu = posToU(Number(carrier.position));
      out.devices.push({
        name: label.slice(0, 255),
        u_position: cu ?? 1,
        u_height: h,
        carrier_key: `z${cid}`,
        slot: slot >= 0 ? slot : null,
        slot_layout: null,
        ...base,
      });
      continue;
    }

    const u = posToU(Number(d.position));
    if (u === null) {
      skip(
        out,
        label,
        null,
        legacy
          ? "sub-U position — not a whole U slot"
          : "position not on a whole-U boundary",
      );
      continue;
    }
    if (!FACES.includes(face)) {
      skip(out, label, u, `unknown face "${String(d.face)}"`);
      continue;
    }
    if (!Number.isInteger(h) || h < 1) {
      skip(out, label, u, "sub-U height — IpamBox tracks whole-U only");
      continue;
    }
    out.devices.push({
      name: label.slice(0, 255),
      u_position: u,
      u_height: h,
      carrier_key: null,
      slot: null,
      slot_layout: null,
      ...base,
    });
  }
  return out;
}

// ------------------------------------------------------------- preview math

const emptyImport = (): ParsedImport => ({
  rack_name: null,
  rack_height: null,
  rack_count: 0,
  devices: [],
  skipped: [],
  notes: [],
});

function skip(
  out: ParsedImport,
  name: string | null,
  u_position: number | null,
  reason: string,
) {
  out.skipped.push({ name, u_position, reason });
}

function facesCollide(a: RackFace, b: RackFace): boolean {
  return a === "both" || b === "both" || a === b;
}

/** First existing rack-level device colliding with the candidate span.
 *  Mounted children are invisible here — their carrier already reserved
 *  the span (mirrors the backend's placement_conflicts). */
export function firstConflict(
  existing: Pick<RackDevice, "u_position" | "u_height" | "face" | "carrier_id">[],
  cand: { u_position: number; u_height: number; face: RackFace },
) {
  const hi = cand.u_position + cand.u_height;
  return (
    existing.find(
      (d) =>
        d.carrier_id == null &&
        cand.u_position < d.u_position + d.u_height &&
        d.u_position < hi &&
        facesCollide(d.face, cand.face),
    ) ?? null
  );
}

export type PreviewStatus = "add" | "conflict" | "skipped";
export interface PreviewRow extends ImportDevice {
  status: PreviewStatus;
  reason: string | null;
}

/** Client-side mirror of the backend placement rules — the server stays
 * authoritative; this only drives the preview table's status column.
 * Carrier children resolve against the payload's carrier rows via
 * carrier_key, then against their siblings' slots. */
export function previewImport(
  parsed: ParsedImport,
  existing: Pick<RackDevice, "u_position" | "u_height" | "face" | "carrier_id">[],
  heightU: number,
  mode: "merge" | "replace",
): PreviewRow[] {
  const placed: Pick<
    RackDevice,
    "u_position" | "u_height" | "face" | "carrier_id"
  >[] = mode === "replace" ? [] : [...existing];
  const rows: (PreviewRow | null)[] = new Array(parsed.devices.length).fill(null);
  const carrierStatus = new Map<string, boolean>();
  const carrierRow = new Map<string, ImportDevice>();

  // Pass 1 — rack-level rows and carriers (children defer to pass 2).
  parsed.devices.forEach((d, i) => {
    if (d.carrier_key && !d.slot_layout) return;
    let status: PreviewStatus = "add";
    let reason: string | null = null;
    if (d.u_position < 1 || d.u_position + d.u_height - 1 > heightU) {
      status = "skipped";
      reason = `outside ${heightU}U rack`;
    } else {
      const hit = firstConflict(placed, d);
      if (hit) {
        status = "conflict";
        reason = `overlaps U${hit.u_position} (${hit.face})`;
      }
    }
    // Pass-1 rows are rack-level by definition (children defer to pass 2).
    if (status === "add") {
      placed.push({
        u_position: d.u_position,
        u_height: d.u_height,
        face: d.face,
        carrier_id: null,
      });
    }
    if (d.carrier_key && d.slot_layout) {
      carrierStatus.set(d.carrier_key, status === "add");
      carrierRow.set(d.carrier_key, d);
    }
    rows[i] = { ...d, status, reason };
  });

  // Pass 2 — carrier children: mountable iff their carrier will exist and
  // the slot is free within it.
  const slotTaken = new Map<string, Set<number>>();
  parsed.devices.forEach((d, i) => {
    if (!(d.carrier_key && !d.slot_layout)) return;
    const carrier = carrierRow.get(d.carrier_key);
    let status: PreviewStatus = "add";
    let reason: string | null = null;
    if (!carrier) {
      status = "skipped";
      reason = "carrier not in the import";
    } else if (!carrierStatus.get(d.carrier_key)) {
      status = "skipped";
      reason = `carrier “${carrier.name}” won't import`;
    } else if (
      d.slot === null ||
      d.slot < 0 ||
      d.slot >= slotCount(carrier.slot_layout)
    ) {
      status = "skipped";
      reason = `slot ${d.slot ?? "?"} outside a ${carrier.slot_layout} carrier`;
    } else {
      const taken = slotTaken.get(d.carrier_key) ?? new Set<number>();
      slotTaken.set(d.carrier_key, taken);
      if (taken.has(d.slot)) {
        status = "conflict";
        reason = `${slotLabel(carrier.slot_layout, d.slot)} already taken`;
      } else {
        taken.add(d.slot);
        reason = `→ ${carrier.name}, ${slotLabel(carrier.slot_layout, d.slot)}`;
      }
    }
    rows[i] = { ...d, status, reason };
  });

  return rows.filter((r): r is PreviewRow => r !== null);
}
