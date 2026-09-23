#!/usr/bin/env node
/**
 * check-rack-library.mjs — integrity check for the bundled rack library.
 *
 *   npm run check:rack-library
 *
 * Verifies public/rack-library/manifest.json against the files on disk:
 * unique slugs, required fields, sane values, and every referenced
 * front/rear image existing as a webp. Exits non-zero on any problem —
 * cheap insurance against a bad regenerate (run after
 * `npm run build:rack-library`, and in CI if one exists).
 */
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const DIR = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "../public/rack-library"
);

const problems = [];
const bad = (msg) => problems.push(msg);

let manifest;
try {
  manifest = JSON.parse(readFileSync(path.join(DIR, "manifest.json"), "utf8"));
} catch (e) {
  console.error(`manifest.json unreadable: ${e.message}`);
  process.exit(1);
}
if (!Array.isArray(manifest)) bad("manifest is not an array");

const slugs = new Set();
const FACES = new Set(["front", "rear", "both"]);
const LAYOUTS = new Set(["halves", "quarters", "shelf"]);

for (const e of manifest ?? []) {
  const tag = e?.slug ?? JSON.stringify(e)?.slice(0, 60);
  if (typeof e?.slug !== "string" || !/^[a-z0-9][a-z0-9_-]*$/.test(e.slug))
    bad(`${tag}: bad slug`);
  if (slugs.has(e.slug)) bad(`${tag}: duplicate slug`);
  slugs.add(e.slug);
  for (const k of ["name", "manufacturer", "model", "category"])
    if (typeof e[k] !== "string" || !e[k]) bad(`${tag}: missing ${k}`);
  if (typeof e.u_height !== "number" || e.u_height < 1 || e.u_height > 100)
    bad(`${tag}: u_height ${e.u_height} out of range`);
  if (!FACES.has(e.face_default)) bad(`${tag}: bad face_default`);
  if (typeof e.colour !== "string" || !/^#[0-9a-f]{6}$/i.test(e.colour))
    bad(`${tag}: bad colour ${e.colour}`);
  if (e.slot_layout != null && !LAYOUTS.has(e.slot_layout))
    bad(`${tag}: bad slot_layout ${e.slot_layout}`);
  if (e.watts != null && (typeof e.watts !== "number" || e.watts <= 0))
    bad(`${tag}: bad watts ${e.watts}`);
  if (e.weight_kg != null && (typeof e.weight_kg !== "number" || e.weight_kg <= 0))
    bad(`${tag}: bad weight_kg ${e.weight_kg}`);
  for (const k of ["front_image", "rear_image"]) {
    if (e[k] == null) continue;
    if (typeof e[k] !== "string" || !e[k].endsWith(".webp"))
      bad(`${tag}: ${k} is not a .webp path (${e[k]})`);
    else if (!existsSync(path.join(DIR, e[k])))
      bad(`${tag}: ${k} missing on disk (${e[k]})`);
  }
}

// Orphaned images = stale output a regenerate should have removed.
import { readdirSync } from "node:fs";
const referenced = new Set(
  manifest.flatMap((e) => [e.front_image, e.rear_image].filter(Boolean))
);
for (const f of readdirSync(path.join(DIR, "images"))) {
  if (!referenced.has(`images/${f}`)) bad(`images/${f}: not referenced`);
}

if (!existsSync(path.join(DIR, "ATTRIBUTION.md")))
  bad("ATTRIBUTION.md missing");

if (problems.length) {
  console.error(`rack-library check FAILED (${problems.length}):`);
  for (const p of problems) console.error(`  - ${p}`);
  process.exit(1);
}
const nImg = manifest.filter((e) => e.front_image || e.rear_image).length;
console.log(
  `rack-library OK: ${manifest.length} entries, ${nImg} with images, ${referenced.size} files`
);
