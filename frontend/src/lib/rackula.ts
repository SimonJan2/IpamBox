/** Rackula wire-format interop: share URLs (?l= LZ-string MinimalLayoutV2) and
 * .Rackula.zip (layout.yaml full Layout object).
 *
 * Position conventions verified against upstream
 * (src/lib/utils/share.ts, src/lib/schemas/{index,share,migrations}.ts):
 *
 * - Share `p` is the 1-based human U (U1 -> p=1). Non-integer p = sub-U gear.
 * - YAML `position` is internal 1/6-U units: U1 -> 6, so u = position / 6.
 *   Files with `version` missing or < 0.7.0 (or any rail position < 6) are
 *   legacy whole-U — position is the U number directly.
 * - ci/si/slot_id/container_id/auto_created mark carrier-mounted gear, which
 *   IpamBox v1 has no model for — skipped with a note.
 */
import JSZip from "jszip";
import yaml from "js-yaml";
import LZString from "lz-string";

import type { RackDevice, RackDeviceCreate, RackFace } from "@/types";

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
  "name" | "device_type" | "u_position" | "u_height" | "face" | "colour" | "category" | "manufacturer" | "model" | "notes"
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
        d: devices.map((d) => ({
          t: slugFor.get(d)!,
          p: d.u_position,
          f: d.face ?? "front",
          ...(d.name ? { n: clip(d.name, 100) } : {}),
        })),
      },
    ],
    dt: [...types.entries()].map(([slug, d]) => ({
      s: slug,
      h: d.u_height ?? 1,
      ...(d.manufacturer ? { mf: clip(d.manufacturer, 100) } : {}),
      ...(d.model ? { m: clip(d.model, 100) } : {}),
      c: d.colour ?? FALLBACK_COLOUR,
      x: CATEGORY_TO_ABBREV[canonicalCategory(d.category)],
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
        devices: devices.map((d, i) => ({
          id: `dev-${d.id ?? i}`,
          device_type: slugFor.get(d)!,
          position: d.u_position * UNITS_PER_U,
          face: d.face ?? "front",
          ...(d.name ? { name: clip(d.name, 100) } : {}),
          ...(d.notes ? { notes: clip(d.notes, 1000) } : {}),
        })),
      },
    ],
    device_types: [...types.entries()].map(([slug, d]) => ({
      slug,
      u_height: d.u_height ?? 1,
      ...(d.manufacturer ? { manufacturer: clip(d.manufacturer, 100) } : {}),
      ...(d.model ? { model: clip(d.model, 100) } : {}),
      colour: d.colour ?? FALLBACK_COLOUR,
      category: canonicalCategory(d.category),
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

  for (const d of (rack.d as Record<string, unknown>[] | undefined) ?? []) {
    const t = dtBySlug.get(String(d.t ?? ""));
    const label = String(d.n ?? d.t ?? "device");
    if (d.ci !== undefined || d.si !== undefined || d.a) {
      skip(out, label, null, "carrier-mounted — IpamBox has no carriers");
      continue;
    }
    const p = Number(d.p);
    if (!Number.isInteger(p) || p < 1) {
      skip(out, label, null, "sub-U position — not a whole U slot");
      continue;
    }
    const face = String(d.f ?? "front") as RackFace;
    if (!FACES.includes(face)) {
      skip(out, label, p, `unknown face "${String(d.f)}"`);
      continue;
    }
    const h = t?.h ?? 1;
    if (!Number.isInteger(h) || h < 1) {
      skip(out, label, p, "sub-U height — IpamBox tracks whole-U only");
      continue;
    }
    out.devices.push({
      name: label.slice(0, 255),
      device_type: String(d.t ?? "") || null,
      u_position: p,
      u_height: h,
      face,
      colour: t?.c ?? null,
      category: t?.x ? (ABBREV_TO_CATEGORY[t.x] ?? "other") : null,
      manufacturer: t?.mf ?? null,
      model: t?.m ?? null,
      notes: null,
    });
  }
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

  for (const d of devices) {
    const slug = String(d.device_type ?? "");
    const t = dtBySlug.get(slug);
    const label = String(d.name ?? slug ?? "device");
    if (d.container_id || d.slot_id || d.auto_created) {
      skip(out, label, null, "carrier-mounted — IpamBox has no carriers");
      continue;
    }
    const pos = Number(d.position);
    let u: number;
    if (legacy) {
      if (!Number.isInteger(pos) || pos < 1) {
        skip(out, label, null, "sub-U position — not a whole U slot");
        continue;
      }
      u = pos;
    } else {
      if (!Number.isInteger(pos) || pos % UNITS_PER_U !== 0 || pos < UNITS_PER_U) {
        skip(out, label, null, "position not on a whole-U boundary");
        continue;
      }
      u = pos / UNITS_PER_U;
    }
    const face = String(d.face ?? "front") as RackFace;
    if (!FACES.includes(face)) {
      skip(out, label, u, `unknown face "${String(d.face)}"`);
      continue;
    }
    const h = Number(t?.u_height ?? 1);
    if (!Number.isInteger(h) || h < 1) {
      skip(out, label, u, "sub-U height — IpamBox tracks whole-U only");
      continue;
    }
    out.devices.push({
      name: label.slice(0, 255),
      device_type: slug || null,
      u_position: u,
      u_height: h,
      face,
      colour:
        (typeof d.colour_override === "string" ? d.colour_override : null) ??
        (typeof t?.colour === "string" ? (t.colour as string) : null),
      category:
        typeof t?.category === "string" ? (t.category as string) : null,
      manufacturer:
        typeof t?.manufacturer === "string" ? (t.manufacturer as string) : null,
      model: typeof t?.model === "string" ? (t.model as string) : null,
      notes: typeof d.notes === "string" ? (d.notes as string) : null,
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

/** First existing device colliding with the candidate span, else null. */
export function firstConflict(
  existing: Pick<RackDevice, "u_position" | "u_height" | "face">[],
  cand: { u_position: number; u_height: number; face: RackFace },
) {
  const hi = cand.u_position + cand.u_height;
  return (
    existing.find(
      (d) =>
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
 * authoritative; this only drives the preview table's status column. */
export function previewImport(
  parsed: ParsedImport,
  existing: Pick<RackDevice, "u_position" | "u_height" | "face">[],
  heightU: number,
  mode: "merge" | "replace",
): PreviewRow[] {
  const placed = mode === "replace" ? [] : [...existing];
  return parsed.devices.map((d) => {
    let status: PreviewStatus = "add";
    let reason: string | null = null;
    if (d.u_position < 1 || d.u_position + d.u_height - 1 > heightU) {
      status = "skipped";
      reason = `outside ${heightU}U rack`;
    } else {
      const hit = firstConflict(placed, d);
      if (hit) {
        status = "conflict";
        reason = `overlaps ${hit.u_position}U (${hit.face})`;
      }
    }
    if (status === "add") placed.push(d);
    return { ...d, status, reason };
  });
}
