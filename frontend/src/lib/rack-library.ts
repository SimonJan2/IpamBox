/** Device catalog for the add-device form's library picker and the
 *  elevation's product images.
 *
 *  The real catalog is generated at build time into
 *  `public/rack-library/manifest.json` by `scripts/build-rack-library.mjs`
 *  (curated NetBox devicetype-library subset — see public/rack-library/
 *  ATTRIBUTION.md). `loadRackLibrary()` fetches it once and caches it in
 *  module scope; `RACK_LIBRARY` starts as a tiny inline fallback so a
 *  source checkout without the generated bundle still works.
 *
 *  Slugs double as Rackula `device_type` values on export, so keep them
 *  stable lowercase-dash identifiers. `face_default` preselects the
 *  mounting face; everything prefills the form and stays editable.
 *  `watts`/`weight_kg` are informational here — the V2.5 capacity rollup
 *  consumes them; they are NOT stored on rack_devices.
 */
import type { RackFace, SlotLayout } from "@/types";

export interface LibraryDevice {
  slug: string;
  name: string;
  manufacturer: string;
  model: string;
  u_height: number;
  is_full_depth?: boolean;
  face_default: RackFace;
  colour: string;
  category: string;
  /** Typical max draw (W) from the upstream def, when published. */
  watts?: number;
  weight_kg?: number;
  /** Paths relative to /rack-library/ — present only when bundled. */
  front_image?: string;
  rear_image?: string;
  /** Set = this entry is a carrier tray other gear mounts into. */
  slot_layout?: SlotLayout;
}

/** Inline fallback — used until the manifest loads and whenever it 404s
 *  (dev checkout without a generated bundle). Deliberately tiny; the
 *  manifest carries the full catalog. */
export const RACK_LIBRARY: LibraryDevice[] = [
  { slug: "server-1u", name: "1U Server", manufacturer: "Generic", model: "1U Rack Server", u_height: 1, face_default: "front", colour: "#38bdf8", category: "server" },
  { slug: "server-2u", name: "2U Server", manufacturer: "Generic", model: "2U Rack Server", u_height: 2, face_default: "front", colour: "#0ea5e9", category: "server" },
  { slug: "switch-24p", name: "24-port Switch", manufacturer: "Generic", model: "24p L3 Switch", u_height: 1, face_default: "front", colour: "#34d399", category: "network" },
  { slug: "blank-1u", name: "Blank Panel", manufacturer: "Generic", model: "1U Blank", u_height: 1, face_default: "front", colour: "#64748b", category: "blank" },
  { slug: "carrier-dual", name: "1U dual shelf", manufacturer: "Generic", model: "1U Half-Width Dual Shelf", u_height: 1, face_default: "front", colour: "#cbd5e1", category: "carrier", slot_layout: "halves" },
  { slug: "carrier-shelf", name: "Rack shelf", manufacturer: "Generic", model: "1U Carrier Tray", u_height: 1, face_default: "front", colour: "#cbd5e1", category: "carrier", slot_layout: "shelf" },
];

let loading: Promise<LibraryDevice[]> | null = null;

/** Fetch `/rack-library/manifest.json` once (module-scoped cache). On any
 *  failure the inline fallback stays in place — the returned array is
 *  always `RACK_LIBRARY`, mutated in place so late readers see the full
 *  catalog too. */
export function loadRackLibrary(): Promise<LibraryDevice[]> {
  loading ??= (async () => {
    try {
      const res = await fetch("/rack-library/manifest.json");
      if (res.ok) {
        const list = (await res.json()) as LibraryDevice[];
        if (Array.isArray(list) && list.length > 0)
          RACK_LIBRARY.splice(0, RACK_LIBRARY.length, ...list);
      }
    } catch {
      // Offline or no generated bundle — keep the inline fallback.
    }
    return RACK_LIBRARY;
  })();
  return loading;
}

/** slug -> entry lookup for `device_type` matching on the elevation. */
export function libraryBySlug(
  list: LibraryDevice[] = RACK_LIBRARY
): Map<string, LibraryDevice> {
  return new Map(list.map((d) => [d.slug, d]));
}

/** Bundled image URL for `entry` viewed from `view`, or undefined when the
 *  entry has no image (caller falls back to the colour block). Rear view
 *  prefers `rear_image` and falls back to `front_image`. */
export function libraryImage(
  entry: LibraryDevice | undefined,
  view: "front" | "rear"
): string | undefined {
  const rel = view === "rear" ? entry?.rear_image ?? entry?.front_image : entry?.front_image;
  return rel ? `/rack-library/${rel}` : undefined;
}
