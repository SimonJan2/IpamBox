# Import

The **Import** wizard ingests a `Network_Address.xlsx`-style workbook and
turns messy real-world spreadsheets into clean IPAM data — with a full
dry-run before anything is committed.

## The pipeline

```
upload → per-sheet type detection → dry-run preview → commit
```

1. **Upload** — the file lands under `IMPORT_DIR` as a batch you can
   re-preview or commit later. Every imported row keeps an
   `import_batch_id` back to this upload.
2. **Detection** — each sheet is classified by header signature (Hebrew and
   English variants) into a family: sites-master, site sheet, circuits,
   certificates, assets, services, inventory, servers, or unknown/empty.
   The **Import as** column lets you override the target per sheet —
   *Custom list* preserves the sheet's own columns as a
   [custom list](/docs/lists) instead of dissolving it into typed entities.
   Unknown-family sheets suggest this automatically. Optionally the sheet
   *also* feeds its normal IPAM targets, so a server sheet lands in both
   `ip_addresses` and the list. Re-importing the same sheet **merges by key
   column**: changed cells update, new rows are created, vanished rows are
   kept and reported, and hand-edited rows win conflicts.
3. **Preview** — a per-row report of what *would* happen:
   `create / update / skip / conflict / error`, plus sheet-level warnings.
4. **Commit** — all-or-nothing per run, or partial with **per-sheet
   rollback** if a sheet fails.

## How site sheets resolve their site

A site sheet is matched to a site by (in order): declared octet-pair blocks,
site code, site name — checked against both existing DB rows and sites
planned earlier in the same batch. Inactive sites can't claim new rows, and
title/name matching uses Hebrew-aware folding. A nameless master row becomes
`Site N` instead of being dropped.

## What the normalizers handle

- **Split-octet IPs** (`172.20` + `15.1` fragments → assembled addresses)
- **Multi-IP cells** — several addresses in one cell become several rows
- **MACs** in four formats — normalized
- **Excel serial dates** — `44927` → a real date
- **Repeated headers and duplicated column blocks** — detected and skipped
- **Hebrew content** — final-letter folding, status mapping, RTL-safe values

## CSV alternative

For flat data, the address list has its own
[CSV import/export](/docs/addresses) — simpler, but all-or-nothing and
address-only.

## Batches

The import page lists past batches (filename, sha256, status
`draft/committed/failed`, actor, row stats). Drafts can be committed later;
committed batches are the audit trail for where every row came from.
