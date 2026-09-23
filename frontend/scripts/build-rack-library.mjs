#!/usr/bin/env node
/**
 * build-rack-library.mjs — regenerate `frontend/public/rack-library/`.
 *
 * Pulls a curated subset of the NetBox devicetype-library
 * (https://github.com/netbox-community/devicetype-library — data + images
 * are CC0-1.0, see ATTRIBUTION.md) and writes:
 *
 *   public/rack-library/manifest.json   — entries consumed by
 *                                       src/lib/rack-library.ts
 *   public/rack-library/images/*.webp   — front/rear product images,
 *                                         resized to <=400px wide
 *   public/rack-library/ATTRIBUTION.md  — source + license note
 *
 * Everything is bundled in the repo so shipped builds never touch the
 * network (air-gap safe, same tradeoff as the OUI database). Re-run this
 * script to refresh the library for a release:
 *
 *   cd frontend && npm run build:rack-library
 *
 * The bundle contains the curated CURATED list, every upstream device type
 * that ships an elevation image (~1.5k), and the FULL_IMPORT vendor
 * families whole — Check Point, Aruba, HPE storage — even when no image
 * exists (colour-block fallback covers them). Pass --curated-only to skip
 * both wide sweeps.
 *
 * Network: one GitHub tree-API call plus raw.githubusercontent.com downloads
 * for the YAML/image files. Set GITHUB_TOKEN if you hit the
 * anonymous 60 req/h API cap.
 *
 * After regenerating, run `npm run check:rack-library` to verify the bundle.
 */
import { mkdir, readdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import yaml from "js-yaml";
import sharp from "sharp";

const FRONTEND = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const OUT_DIR = path.join(FRONTEND, "public", "rack-library");
const IMG_DIR = path.join(OUT_DIR, "images");
const REPO = "netbox-community/devicetype-library";
const REF = "master";
const RAW = `https://raw.githubusercontent.com/${REPO}/${REF}`;
const API = `https://api.github.com/repos/${REPO}`;
const IMG_WIDTH = 400;
const CONCURRENCY = 8;

/* ------------------------------------------------------------------ *
 *  Curated device list — the whole point of this script is that we ship
 *  ~100 useful types, not the library's ~11k. Add a row to extend.
 *
 *  slug     — devicetype-library slug (resolved against the repo tree)
 *  category — picker grouping; also picks the fallback colour below
 *  face     — optional face_default override (default: is_full_depth ?
 *             "both" : "front")
 *  u        — optional u_height override (e.g. 0U boards racked on trays)
 *  img      — optional elevation-image basename override for the rare
 *             case where the image filename isn't `<slug>` (renames)
 * ------------------------------------------------------------------ */
const CURATED = [
  // --- Generic starters (colour blocks, no upstream def needed) -------
  { slug: "server-1u", name: "1U Server", manufacturer: "Generic", model: "1U Rack Server", u: 1, face: "front", colour: "#38bdf8", category: "server" },
  { slug: "server-2u", name: "2U Server", manufacturer: "Generic", model: "2U Rack Server", u: 2, face: "front", colour: "#0ea5e9", category: "server" },
  { slug: "server-4u", name: "4U Server", manufacturer: "Generic", model: "4U Rack Server", u: 4, face: "front", colour: "#0284c7", category: "server" },
  { slug: "switch-24p", name: "24-port Switch", manufacturer: "Generic", model: "24p L3 Switch", u: 1, face: "front", colour: "#34d399", category: "network" },
  { slug: "switch-48p", name: "48-port Switch", manufacturer: "Generic", model: "48p L3 Switch", u: 1, face: "front", colour: "#10b981", category: "network" },
  { slug: "router", name: "Router", manufacturer: "Generic", model: "Edge Router", u: 1, face: "front", colour: "#059669", category: "network" },
  { slug: "firewall-1u", name: "Firewall", manufacturer: "Generic", model: "1U Firewall", u: 1, face: "front", colour: "#f43f5e", category: "firewall" },
  { slug: "pdu-1u", name: "Rack PDU", manufacturer: "Generic", model: "1U Switched PDU", u: 1, face: "rear", colour: "#a78bfa", category: "power" },
  { slug: "ups-2u", name: "UPS 2U", manufacturer: "Generic", model: "2U Line-Interactive UPS", u: 2, face: "front", colour: "#818cf8", category: "power" },
  { slug: "blank-1u", name: "Blank Panel", manufacturer: "Generic", model: "1U Blank", u: 1, face: "front", colour: "#64748b", category: "blank" },
  { slug: "brush-1u", name: "Brush Panel", manufacturer: "Generic", model: "1U Brush Strip", u: 1, face: "front", colour: "#94a3b8", category: "cable-management" },
  { slug: "shelf-1u", name: "Rack Shelf", manufacturer: "Generic", model: "1U Cantilever Shelf", u: 1, face: "front", colour: "#cbd5e1", category: "shelf" },
  { slug: "carrier-dual", name: "1U dual shelf", manufacturer: "Generic", model: "1U Half-Width Dual Shelf", u: 1, face: "front", colour: "#cbd5e1", category: "carrier", slot_layout: "halves" },
  { slug: "carrier-quad", name: "1U quad bracket", manufacturer: "Generic", model: "1U Quad Bracket", u: 1, face: "front", colour: "#cbd5e1", category: "carrier", slot_layout: "quarters" },
  { slug: "carrier-shelf", name: "Rack shelf", manufacturer: "Generic", model: "1U Carrier Tray", u: 1, face: "front", colour: "#cbd5e1", category: "carrier", slot_layout: "shelf" },
  { slug: "kvm-console", name: "KVM Console", manufacturer: "Generic", model: "1U LCD Console", u: 1, face: "front", colour: "#e2e8f0", category: "kvm" },

  // --- Generic upstream defs (patch panels, blanks, shelves) ----------
  { slug: "generic-24-port-copper-patch-panel", category: "patch-panel" },
  { slug: "generic-48-port-copper-patch-panel", category: "patch-panel" },
  { slug: "generic-lc-24-port-fiber-patch-panel", category: "patch-panel" },
  { slug: "generic-lc-48-port-fiber-patch-panel", category: "patch-panel" },
  { slug: "generic-blanking-panel-1u", category: "blank" },
  { slug: "generic-blanking-panel-2u", category: "blank" },
  { slug: "generic-cable-management-panel-1u", category: "cable-management" },
  { slug: "generic-cable-management-panel-2u", category: "cable-management" },
  { slug: "generic-shelf-1he", category: "shelf" },
  { slug: "generic-shelf-2he", category: "shelf" },
  { slug: "generic-storage-drawer-2u", category: "shelf" },
  { slug: "generic-sliding-shelf-drawer-1u", category: "shelf" },
  { slug: "generic-1u-fan-panel", category: "accessory" },
  { slug: "generic-7port-1u-pdu", category: "power", face: "rear" },

  // --- Servers --------------------------------------------------------
  { slug: "dell-poweredge-r350", category: "server" },
  { slug: "dell-poweredge-r430", category: "server" },
  { slug: "dell-poweredge-r440", category: "server" },
  { slug: "dell-poweredge-r450", category: "server" },
  { slug: "dell-poweredge-r550", category: "server" },
  { slug: "dell-poweredge-r620", category: "server" },
  { slug: "dell-poweredge-r630", category: "server" },
  { slug: "dell-poweredge-r640", category: "server" },
  { slug: "dell-poweredge-r650", category: "server" },
  { slug: "dell-poweredge-r660", category: "server" },
  { slug: "dell-poweredge-r720", category: "server" },
  { slug: "dell-poweredge-r730xd", category: "server" },
  { slug: "dell-poweredge-r740", category: "server" },
  { slug: "dell-poweredge-r750", category: "server" },
  { slug: "dell-poweredge-r760", category: "server" },
  { slug: "hpe-proliant-dl20-gen10", category: "server" },
  { slug: "hpe-proliant-dl360-gen9", category: "server" },
  { slug: "hpe-proliant-dl360-gen10", category: "server" },
  { slug: "hpe-proliant-dl360-gen11", category: "server" },
  { slug: "hpe-proliant-dl380-gen9", category: "server" },
  { slug: "hpe-proliant-dl380-gen10", category: "server" },
  { slug: "hpe-proliant-dl380-gen11", category: "server" },
  { slug: "hpe-proliant-dl325-gen10", category: "server" },
  { slug: "lenovo-thinksystem-sr630", category: "server" },
  { slug: "lenovo-thinksystem-sr650", category: "server" },
  { slug: "cisco-ucs-c220-m4", category: "server" },
  { slug: "cisco-ucs-c240-m5sx", category: "server" },
  { slug: "supermicro-sys-1028r-wtr", category: "server" },
  { slug: "supermicro-sys-110p-wtr", category: "server" },
  { slug: "supermicro-ssg-6049p-e1cr36l", category: "server" },
  { slug: "supermicro-as-1124us-tnrp", category: "server" },
  { slug: "intel-r1304wftzsr", category: "server" },

  // --- Network --------------------------------------------------------
  { slug: "dell-powerconnect-5548p", category: "network" },
  { slug: "hpe-aruba-2530-48g", category: "network" },
  { slug: "hpe-aruba-2540-48g-4sfpp", category: "network" },
  { slug: "hpe-aruba-2930f-24g-poep-4sfpp", category: "network" },
  { slug: "hpe-aruba-2930f-48g-poep-4sfp", category: "network" },
  { slug: "cisco-c9200-24t", category: "network" },
  { slug: "cisco-c9200l-24p-4g", category: "network" },
  { slug: "cisco-c9200l-48p-4g", category: "network" },
  { slug: "cisco-c9300-24p", category: "network" },
  { slug: "cisco-c9300-48p", category: "network" },
  { slug: "cisco-c9300-48t", category: "network" },
  { slug: "cisco-c9300l-24p-4x", category: "network" },
  { slug: "cisco-c9300l-48p-4x", category: "network" },
  { slug: "cisco-ws-c3850-24p-s", category: "network" },
  { slug: "cisco-ws-c3850-48p", category: "network" },
  { slug: "cisco-ws-c2960x-24pd-l", category: "network" },
  { slug: "cisco-meraki-ms220-48fp", category: "network" },
  { slug: "cisco-meraki-ms225-48fp", category: "network" },
  { slug: "cisco-meraki-ms350-48fp", category: "network" },
  { slug: "cisco-meraki-mx95", category: "network" },
  { slug: "cisco-meraki-mx100", category: "network" },
  { slug: "juniper-ex2300-24t", category: "network" },
  { slug: "juniper-ex2300-48p", category: "network" },
  { slug: "juniper-ex3400-48p", category: "network" },
  { slug: "juniper-ex4300-24p", category: "network" },
  { slug: "juniper-ex4300-24t", category: "network" },
  { slug: "juniper-ex4300-48p", category: "network" },
  { slug: "juniper-qfx5100-48s-3afo", category: "network" },
  { slug: "arista-dcs-7050s-64-f", category: "network" },
  { slug: "arista-dcs-7050sx3-48yc8-f", category: "network" },
  { slug: "arista-dcs-7050cx3-32s", category: "network" },
  { slug: "arista-dcs-7050tx3-48c8-f", category: "network" },
  { slug: "arista-dcs-7020tr-48-f", category: "network" },
  { slug: "arista-dcs-7280sr-48c6-f", category: "network" },
  { slug: "mikrotik-crs326-24g-2s-plus-rm", category: "network" },
  { slug: "mikrotik-crs328-24p-4s-plus-rm", category: "network" },
  { slug: "mikrotik-crs354-48g-4s-plus-2q-plus-rm", category: "network" },
  { slug: "mikrotik-crs317-1g-16s-plus-rm", category: "network" },
  { slug: "mikrotik-ccr2004-16g-2s-plus", category: "network" },
  { slug: "mikrotik-ccr2004-1g-12s-plus-2xs", category: "network" },
  { slug: "mikrotik-ccr2116-12g-4s-plus", category: "network" },
  { slug: "ubiquiti-usw-24-poe", category: "network" },
  { slug: "ubiquiti-usw-48-poe", category: "network" },
  { slug: "ubiquiti-usw-pro-24-poe", category: "network" },
  { slug: "ubiquiti-usw-pro-48-poe", category: "network" },
  { slug: "ubiquiti-usw-pro-aggregation", category: "network" },
  { slug: "ubiquiti-usw-aggregation", category: "network" },
  { slug: "ubiquiti-usw-enterprise-24-poe", category: "network" },
  { slug: "ubiquiti-us-16-xg", category: "network" },
  { slug: "ubiquiti-ecs-24-poe", category: "network", img: "ubiquiti-enterprise-campus-switch-24-port-poe" },
  { slug: "ubiquiti-ecs-aggregation", category: "network", img: "ubiquiti-enterprise-campus-aggregation" },
  { slug: "netgear-m4300-12x12f", category: "network" },
  { slug: "netgear-prosafe-gs752tp", category: "network" },
  { slug: "tp-link-tl-sg3428xmp", category: "network" },
  { slug: "tp-link-tl-sg3428", category: "network" },
  { slug: "tp-link-sg3218xp-m2-v1", category: "network" },
  { slug: "opengear-cm8132", category: "console" },
  { slug: "opengear-om2224-24e", category: "console" },
  { slug: "opengear-im7248-2-dac", category: "console" },
  { slug: "raritan-dsx2-16", category: "console" },

  // --- Routers / firewalls ---------------------------------------------
  { slug: "ubiquiti-unifi-dream-machine-pro", category: "network" },
  { slug: "ubiquiti-unifi-dream-machine-pro-max", category: "network" },
  { slug: "ubiquiti-unifi-dream-machine-pro-special-edition", category: "network" },
  { slug: "ubiquiti-usg-pro-4", category: "network" },
  { slug: "fortinet-fg-60f", category: "firewall" },
  { slug: "fortinet-fg-100f", category: "firewall" },
  { slug: "fortinet-fg-200f", category: "firewall" },
  { slug: "fortinet-fg-201f", category: "firewall" },
  { slug: "palo-alto-networks-pa-440", category: "firewall" },
  { slug: "palo-alto-networks-pa-460", category: "firewall" },
  { slug: "palo-alto-networks-pa-850", category: "firewall" },
  { slug: "palo-alto-networks-pa-3220", category: "firewall" },
  { slug: "palo-alto-networks-pa-3410", category: "firewall" },

  // --- Storage ---------------------------------------------------------
  { slug: "synology-rs1221-plus", category: "storage" },
  { slug: "synology-rs1221rp-plus", category: "storage" },
  { slug: "synology-rs2421-plus", category: "storage" },
  { slug: "synology-rs2418-plus", category: "storage" },
  { slug: "synology-rs819", category: "storage" },
  { slug: "synology-rs820-plus", category: "storage" },
  { slug: "qnap-ts-1232pxu-rp", category: "storage" },
  { slug: "qnap-ts-432pxu-rp", category: "storage" },
  { slug: "qnap-ts-832pxu-rp", category: "storage" },
  { slug: "qnap-ts-h1277axu-rp", category: "storage" },
  { slug: "ubiquiti-unvr", category: "storage" },
  { slug: "ubiquiti-unvr-pro", category: "storage" },

  // --- Power (PDUs/UPS/ATS — usually rear-mounted) ----------------------
  { slug: "apc-smt1500rm2u", category: "power" },
  { slug: "apc-smt1500rmi2u", category: "power" },
  { slug: "apc-smt2200rm2u", category: "power" },
  { slug: "apc-smt3000rmi2u", category: "power" },
  { slug: "apc-smx1500rmi2u", category: "power" },
  { slug: "apc-surt2000rmxli", category: "power" },
  { slug: "apc-ap8941", category: "power", face: "rear" },
  { slug: "apc-ap8959", category: "power", face: "rear" },
  { slug: "apc-ap7900b", category: "power", face: "rear" },
  { slug: "apc-ap7921b", category: "power", face: "rear" },
  { slug: "apc-ap4421a", category: "power", face: "rear" },
  { slug: "apc-ap4423a", category: "power", face: "rear" },
  { slug: "apc-ap4424a", category: "power", face: "rear" },
  { slug: "eaton-5px1500irt", category: "power" },
  { slug: "eaton-9px1000irt2u", category: "power" },
  { slug: "eaton-9px3000irt2u", category: "power" },
  { slug: "eaton-tripp-lite-pdumh15at", category: "power", face: "rear" },
  { slug: "cyberpower-or2200lcdrt2u", category: "power" },
  { slug: "cyberpower-pdu41005", category: "power", face: "rear" },
  { slug: "raritan-px3-5528v-v2", category: "power", face: "rear" },

  // --- KVM / console / homelab extras -----------------------------------
  { slug: "aten-cs1308", category: "kvm" },
  { slug: "aten-cl1308", category: "kvm" },
  { slug: "raritan-t1700g2-led", category: "kvm" },
  { slug: "middle-atlantic-d2", category: "shelf" },
  { slug: "middle-atlantic-d4", category: "shelf" },
  { slug: "penn-elcom-5008-pec", category: "shelf" },
  { slug: "sonnet-rack-min-2xa", category: "carrier", slot_layout: "halves" },
  { slug: "raspberry-pi-rpi5", category: "compute", u: 1 },
  { slug: "raspberry-pi-rpi4-modb", category: "compute", u: 1 },
];

/** Fallback colour per category (same palette as the v1 starter catalog). */
const CATEGORY_COLOUR = {
  server: "#38bdf8",
  network: "#34d399",
  firewall: "#f43f5e",
  "patch-panel": "#fbbf24",
  power: "#a78bfa",
  blank: "#64748b",
  "cable-management": "#94a3b8",
  shelf: "#cbd5e1",
  carrier: "#cbd5e1",
  kvm: "#e2e8f0",
  storage: "#22d3ee",
  compute: "#f472b6",
  console: "#fb923c",
  accessory: "#94a3b8",
};

const WEIGHT_TO_KG = { kg: 1, g: 0.001, lb: 0.45359237, oz: 0.028349523 };

const INCLUDE_ALL_IMAGED = !process.argv.includes("--curated-only");

/* Vendor families imported whole — image or no image (colour-block
 *  fallback covers them). The KEY regex is a cheap filename prefilter so
 *  we don't fetch all ~10k YAMLs; the doc-level tests run on the parsed
 *  entry (slug/manufacturer/model) inside emitUpstream. */
const FULL_IMPORT_KEY = /^(check-point-|hpe-|hp-)/;
const FULL_IMPORT = [
  // Check Point — the whole range incl. desktop SMB boxes (upstream models
  // them u_height 1 via their rack-tray kits).
  (slug, doc) => /check.?point/i.test(doc.manufacturer ?? slug),
  // Aruba switching + ClearPass live under the HPE manufacturer dir.
  (slug, doc) =>
    /^hpe/.test(slug) && /aruba|clearpass/i.test(`${slug} ${doc.model ?? ""}`),
  // HPE storage: MSA, Alletra, Nimble, Primera, 3PAR/StoreServ, StoreOnce,
  // StoreEasy, StoreEver/MSL tape, D-series disk enclosures, StoreFabric FC.
  (slug, doc) =>
    /^hpe/.test(slug) &&
    /3par|storeserv|alletra|\bmsa\b|nimble|primera|storeonce|storeeasy|storeever|storefabric|\bmsl\b|\bd2d\b|d\d{4}[- ]disk|disk.?enclosure|tape|autoloader|ultrium|\blto\b|xp\d{3,4}|lefthand|storevirtual|san.?switch|\bsn\d{4}b/i.test(
      `${slug} ${doc.model ?? ""}`
    ),
];

const arrLen = (v) => (Array.isArray(v) ? v.length : 0);

/** Category for auto-included devices — heuristic over name, manufacturer
 *  and structural fields. Only used for non-curated entries; a wrong guess
 *  just means a different picker group/fallback colour, so keep it simple. */
function guessCategory(slug, doc) {
  const t = `${slug} ${doc.model ?? ""}`.toLowerCase();
  const mfr = (doc.manufacturer ?? "").toLowerCase();
  const nIf = arrLen(doc.interfaces);
  const nOut = arrLen(doc["power-outlets"]);
  const nFp = arrLen(doc["front-ports"]);
  const nRp = arrLen(doc["rear-ports"]);

  if (/patch.?panel|keystone|coupler|fibre?-panel|fibre?-enclosure/.test(t)) return "patch-panel";
  if (nFp > 0 && nRp > 0 && nIf === 0) return "patch-panel";
  if (/blank(ing)?[- ]?(panel|plate)|filler[- ]?panel/.test(t)) return "blank";
  if (/cable.?man|brush|lacing|routing/.test(t)) return "cable-management";
  if (/shelf|shelves|drawer|tray|cantilever/.test(t)) return "shelf";
  if (/\bups\b|uninterruptible|external.?battery|\bebm\b|battery.?pack|smart.?ups/.test(t)) return "power";
  if (nOut >= 4 || /\bpdu\b|power.?distribut|\bats\b|\bsts\b/.test(t)) return "power";
  if (/opengear|\baten\b/.test(mfr) || /kvm|lcd.?console|console.?server|terminal.?server|serial.?server/.test(t)) return "kvm";
  if (/fortinet|palo.?alto|sophos|watchguard|sonicwall|check.?point|hillstone|netgate/.test(mfr) || /firewall|fortigate/.test(t)) return "firewall";
  if (/synology|qnap|netapp|infortrend|ixsystems|terramaster|asustor/.test(mfr) ||
      /\bnas\b|storage|jbod|\bdas\b|\bsan\b|tape|autoloader|powervault|equallogic|powerstore|storeonce|storwize|\bnvr\b|unvr|\bdvr\b|expansion|alletra|\bmsa\b|nimble|primera|3par|storeserv|storeeasy|storeever|storefabric|disk.?enclosure|\bmsl\b|ultrium|\blto\b|d2d/.test(t)) return "storage";
  if (/switch|nexus|catalyst|\bex[2-4]\d{3}|\bqfx|procurve|powerconnect|interconnect|fabric|aruba|clearpass/.test(t) ||
      /arista|juniper|mikrotik|ubiquiti|netgear|tp-link|d-link|zyxel|extreme|brocade|ruckus|mellanox|nvidia|edgecore|edge-core|\bfs\b/.test(mfr)) return "network";
  if (/server|poweredge|proliant|thinksystem|\bucs\b|rackmount|compute|workstation/.test(t)) return "server";
  if (nIf >= 6) return "network";
  if (/router|gateway|\bwan\b|dream.?machine|\busg\b/.test(t) || nIf > 0) return "network";
  if (/blade|enclosure|chassis/.test(t) || arrLen(doc["device-bays"]) > 0) return "compute";
  if (doc.is_full_depth || arrLen(doc["module-bays"]) > 0) return "server";
  return "accessory";
}

const slugify = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
/** Filename stem -> slug fragment. Upstream turns `+` into `plus`
 *  (RS2421+.yaml -> synology-rs2421-plus). */
const slugStem = (s) =>
  s.toLowerCase().replace(/\+/g, "-plus").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

const ghHeaders = {
  "User-Agent": "ipambox-build-rack-library",
  Accept: "application/vnd.github+json",
  ...(process.env.GITHUB_TOKEN || process.env.GH_TOKEN
    ? { Authorization: `Bearer ${process.env.GITHUB_TOKEN ?? process.env.GH_TOKEN}` }
    : {}),
};

async function fetchJson(url) {
  const res = await fetch(url, { headers: ghHeaders });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} — ${url}`);
  return res.json();
}

async function fetchBuf(url, tries = 4) {
  let res;
  for (let i = 0; i < tries; i++) {
    res = await fetch(url, { headers: ghHeaders });
    if (res.ok) return Buffer.from(await res.arrayBuffer());
    // 429/5xx = throttling — back off; anything else is a real failure.
    if (res.status !== 429 && res.status < 500) break;
    await new Promise((r) => setTimeout(r, 800 * 2 ** i));
  }
  throw new Error(`${res.status} — ${url}`);
}

/** Run `fn` over `items` with a small concurrency pool. */
async function mapLimit(items, n, fn) {
  const out = new Array(items.length);
  let i = 0;
  await Promise.all(
    Array.from({ length: Math.min(n, items.length) }, async () => {
      while (i < items.length) {
        const k = i++;
        out[k] = await fn(items[k]);
      }
    })
  );
  return out;
}

/** Key a near-white studio background to transparency. Only pixels
 *  reachable from the border through near-white are cleared (flood fill),
 *  so light-coloured chassis details survive. */
function keyWhiteBackground(px, w, h) {
  const T = 245;
  const isWhite = (p) =>
    Math.min(px[p * 4], px[p * 4 + 1], px[p * 4 + 2]) >= T;
  const seen = new Uint8Array(w * h);
  const stack = [];
  const push = (x, y) => {
    const p = y * w + x;
    if (!seen[p] && isWhite(p)) {
      seen[p] = 1;
      stack.push(p);
    }
  };
  for (let x = 0; x < w; x++) {
    push(x, 0);
    push(x, h - 1);
  }
  for (let y = 0; y < h; y++) {
    push(0, y);
    push(w - 1, y);
  }
  while (stack.length) {
    const p = stack.pop();
    px[p * 4 + 3] = 0;
    const x = p % w;
    const y = (p - x) / w;
    if (x > 0) push(x - 1, y);
    if (x < w - 1) push(x + 1, y);
    if (y > 0) push(x, y - 1);
    if (y < h - 1) push(x, y + 1);
  }
}

/** -> <=400px webp. Sources without an alpha channel get the white
 *  background keyed out first. */
async function toWebp(buf) {
  const meta = await sharp(buf).metadata();
  let pipe = sharp(buf).resize({ width: IMG_WIDTH, withoutEnlargement: true });
  if (!meta.hasAlpha) {
    const { data, info } = await pipe
      .ensureAlpha()
      .raw()
      .toBuffer({ resolveWithObject: true });
    keyWhiteBackground(data, info.width, info.height);
    pipe = sharp(data, {
      raw: { width: info.width, height: info.height, channels: 4 },
    });
  }
  return pipe.webp({ quality: 82 }).toBuffer();
}

async function main() {
  const tree = await fetchJson(`${API}/git/trees/${REF}?recursive=1`);
  if (tree.truncated)
    throw new Error("GitHub tree response truncated — rerun with GITHUB_TOKEN");
  const paths = tree.tree.filter((t) => t.type === "blob").map((t) => t.path);

  // slug -> device-types yaml path (derived; verified against the YAML's
  // own `slug` field after download)
  const yamlBySlug = new Map();
  // image basename -> { front, rear } paths
  const imgPaths = new Map();
  const IMG_RE = /^elevation-images\/[^/]+\/(.+)\.(front|rear)\.(png|jpe?g|webp)$/;
  for (const p of paths) {
    if (p.startsWith("device-types/")) {
      const m = /^device-types\/([^/]+)\/([^/]+)\.(ya?ml)$/.exec(p);
      if (m) yamlBySlug.set(`${slugify(m[1])}-${slugStem(m[2])}`, p);
    } else {
      const m = IMG_RE.exec(p);
      if (m && !m[1].endsWith("-min")) {
        const base = m[1].toLowerCase();
        const e = imgPaths.get(base) ?? {};
        e[m[2]] = p;
        imgPaths.set(base, e);
      }
    }
  }
  console.log(
    `tree: ${yamlBySlug.size} device types, ${imgPaths.size} image sets (sha ${tree.sha.slice(0, 12)})`
  );

  await mkdir(IMG_DIR, { recursive: true });
  // Drop stale webps from previous runs so the bundle matches the manifest
  // exactly (check-rack-library flags orphans).
  for (const f of await readdir(IMG_DIR))
    if (f.endsWith(".webp")) await rm(path.join(IMG_DIR, f));
  const manifest = [];
  const problems = [];
  const seenSlugs = new Set();
  const consumedImgBases = new Set();

  /** Fetch one device-type YAML, map it to a manifest entry and convert
   *  its elevation images. `entry` carries curated overrides when present;
   *  `imgBase` pins the elevation-image basename when it isn't the slug;
   *  `gate` (slug, doc) decides pass-3 vendor-sweep inclusion. */
  async function emitUpstream(entry, imgBase, gate) {
    const yamlPath = yamlBySlug.get(entry.slug);
    if (!yamlPath) {
      problems.push(`no device-type yaml for ${entry.slug}`);
      return;
    }
    let doc;
    try {
      doc = yaml.load((await fetchBuf(`${RAW}/${encodeURI(yamlPath)}`)).toString("utf8"));
    } catch (e) {
      problems.push(`yaml fetch failed for ${entry.slug}: ${e.message}`);
      return;
    }
    const slug = doc.slug ?? entry.slug;
    if (gate && !gate(slug, doc)) return;
    const base = imgBase ?? entry.img ?? slug;
    consumedImgBases.add(base);
    // Reserve synchronously — two image sets can resolve to the same yaml
    // (e.g. a suffixed recovery + a direct hit) and the pool is concurrent.
    if (seenSlugs.has(slug)) return;
    seenSlugs.add(slug);
    if (slug !== entry.slug)
      console.warn(`  note: ${entry.slug} -> upstream slug ${slug}`);

    const imgs = imgPaths.get(base) ?? {};
    const category = entry.category ?? guessCategory(slug, doc);
    const isUps = /\bups\b|uninterruptible/.test(`${slug} ${doc.model ?? ""}`.toLowerCase());
    const out = {
      slug,
      name: doc.model ?? slug,
      manufacturer: doc.manufacturer ?? "",
      model: doc.model ?? "",
      // rack_devices.u_height is an int >= 1 — clamp 0U/half-U defs up.
      u_height: Math.max(1, Math.round(entry.u ?? doc.u_height ?? 1)),
      is_full_depth: !!doc.is_full_depth,
      // Auto-included PDUs mount facing the rear (outlets side); UPSes and
      // everything else keep the full-depth/front convention.
      face_default:
        entry.face ??
        (entry.category == null && arrLen(doc["power-outlets"]) >= 4 && !isUps
          ? "rear"
          : doc.is_full_depth
            ? "both"
            : "front"),
      colour: entry.colour ?? CATEGORY_COLOUR[category] ?? "#475569",
      category,
      ...(entry.slot_layout ? { slot_layout: entry.slot_layout } : {}),
    };
    const draws = (Array.isArray(doc["power-ports"]) ? doc["power-ports"] : [])
      .map((p) => p?.maximum_draw)
      .filter((n) => typeof n === "number");
    // Redundant PSUs share the load — the chassis draw is the largest
    // single supply's rating, not the sum.
    if (draws.length && Math.max(...draws) > 0) out.watts = Math.max(...draws);
    if (typeof doc.weight === "number" && doc.weight > 0) {
      const f = WEIGHT_TO_KG[doc.weight_unit ?? "kg"];
      const kg = f && Math.round(doc.weight * f * 1000) / 1000;
      if (kg > 0) out.weight_kg = kg;
    }

    for (const side of ["front", "rear"]) {
      if (!imgs[side]) continue;
      try {
        const webp = await toWebp(await fetchBuf(`${RAW}/${encodeURI(imgs[side])}`));
        await writeFile(path.join(IMG_DIR, `${slug}-${side}.webp`), webp);
        out[`${side}_image`] = `images/${slug}-${side}.webp`;
      } catch (e) {
        problems.push(`image ${imgs[side]}: ${e.message}`);
      }
    }
    manifest.push(out);
  }

  // Pass 1 — the curated list.
  await mapLimit(CURATED, CONCURRENCY, async (entry) => {
    // Literal (generic starter) entries have no upstream def.
    if (entry.name) {
      manifest.push(starterEntry(entry));
      seenSlugs.add(entry.slug);
      return;
    }
    await emitUpstream(entry);
  });

  // Pass 2 — every remaining device type that ships an elevation image.
  // Image basenames equal device slugs almost always; basenames that match
  // no yaml are upstream renames -> reported, add an `img` override to
  // CURATED if the device is worth having.
  if (INCLUDE_ALL_IMAGED) {
    const yamlSlugs = [...yamlBySlug.keys()];
    const auto = [];
    const orphans = [];
    for (const base of imgPaths.keys()) {
      if (consumedImgBases.has(base)) continue;
      if (yamlBySlug.has(base)) {
        auto.push([base, base]);
        continue;
      }
      // Some image files lack the manufacturer prefix (N9K-C9396TX vs
      // cisco-n9k-c9396tx) — recover only on a single unambiguous suffix hit.
      const hits = yamlSlugs.filter((k) => k.endsWith(`-${base.trim()}`));
      if (hits.length === 1) auto.push([hits[0], base]);
      else orphans.push(base);
    }
    console.log(`auto-include: ${auto.length} imaged device types`);
    let done = 0;
    await mapLimit(auto, CONCURRENCY, async ([yamlSlug, imgBase]) => {
      await emitUpstream({ slug: yamlSlug }, imgBase);
      if (++done % 200 === 0) console.log(`  … ${done}/${auto.length}`);
    });
    if (orphans.length) {
      console.warn(`\n${orphans.length} image set(s) matched no device-type yaml:`);
      for (const o of orphans.slice(0, 15)) console.warn(`  - ${o}`);
      if (orphans.length > 15) console.warn(`  … and ${orphans.length - 15} more`);
    }

    // Pass 3 — vendor families imported whole (image or no image).
    const fam = [...yamlBySlug.keys()].filter((k) => FULL_IMPORT_KEY.test(k));
    let added = 0;
    await mapLimit(fam, CONCURRENCY, async (k) => {
      const before = manifest.length;
      await emitUpstream({ slug: k }, undefined, (slug, doc) =>
        FULL_IMPORT.some((f) => f(slug, doc))
      );
      if (manifest.length > before) added++;
    });
    console.log(`vendor sweep: ${added} extra devices from ${fam.length} candidates`);
  }

  manifest.sort((a, b) =>
    a.manufacturer === b.manufacturer
      ? a.name.localeCompare(b.name)
      : a.manufacturer === "Generic"
        ? -1
        : b.manufacturer === "Generic"
          ? 1
          : a.manufacturer.localeCompare(b.manufacturer)
  );

  await writeFile(OUT_DIR + "/manifest.json", JSON.stringify(manifest, null, 2) + "\n");
  await writeFile(OUT_DIR + "/ATTRIBUTION.md", attribution(tree.sha, manifest));
  const nImg = manifest.filter((e) => e.front_image || e.rear_image).length;
  console.log(
    `wrote ${manifest.length} manifest entries (${nImg} with images) -> ${path.relative(FRONTEND, OUT_DIR)}/`
  );
  if (problems.length) {
    console.warn(`\n${problems.length} problems:`);
    for (const p of problems) console.warn(`  - ${p}`);
    process.exitCode = 1;
  }
}

function starterEntry(e) {
  return {
    slug: e.slug,
    name: e.name,
    manufacturer: e.manufacturer,
    model: e.model,
    u_height: e.u,
    is_full_depth: false,
    face_default: e.face,
    colour: e.colour,
    category: e.category,
    ...(e.slot_layout ? { slot_layout: e.slot_layout } : {}),
  };
}

function attribution(sha, manifest) {
  return `# Rack device image library

Generated by \`frontend/scripts/build-rack-library.mjs\` — do not edit by hand.

- **Source:** [netbox-community/devicetype-library](https://github.com/netbox-community/devicetype-library)
  (tree \`${sha.slice(0, 12)}\`, fetched ${new Date().toISOString().slice(0, 10)})
- **License:** [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)
  (public-domain dedication) — see \`LICENSE.txt\` in the source repo.
- **Contents:** ${manifest.length} device-type definitions — every upstream
  device that ships elevation images, the complete Check Point / Aruba /
  HPE-storage families, plus a hand-curated set of generic rack gear — and
  front/rear product images. Images were resized to
  ≤ ${IMG_WIDTH}px wide and re-encoded as WebP; white studio backgrounds
  were keyed to transparency where the source had no alpha channel.
- **Refresh:** re-run \`npm run build:rack-library\` (in \`frontend/\`) per
  IpamBox release, like the OUI database.

The bundled files are served from \`/rack-library/\` — nothing is fetched
from the network at runtime (air-gap safe).
`;
}

await main();
