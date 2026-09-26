# Reports

**Reports** (`/reports`) is the estate on one page: every aggregate the
other pages compute, assembled into a single print-ready report — per-site
fill, address status, utilization outliers, rack capacity, expiring
certificates, scan history, open flags, device health and monitor state.
Reports are **derived**: nothing is stored, nothing appears in the
changelog, and every number is the same calculation the underlying page
runs. If the report disagrees with the dashboard, that's a bug.

## Scoping

The site picker scopes the whole report — headline strip and every
section. Scoping rules follow ownership: prefixes/addresses/devices/racks
by their `site_id`, certificates and scans stay estate-wide… except scans
narrow via the job's resolved prefix. Monitors scope through their
device's site or their address's prefix site.

## Sections

| Section | What it measures | Link target |
|---|---|---|
| Sites | Per-site prefix count, addresses used/usable, fill %, device count | `/sites` |
| Address status | Counts and share per status (active/reserved/dhcp/discovered/offline) + the dashboard's used/usable/utilization totals | `/addresses` |
| Utilization | Fullest 10 + emptiest 5 IPv4 prefixes (containers excluded — same rule as the dashboard chart) | `/prefixes` |
| Rack capacity | Per rack group: racks, used/free U, fill %, Σ watts, Σ kg — rolled up from `stamp_rack_stats` | `/racks` |
| Certificates | Expiring within the effective `cert_warn_days` window + expired, oldest first | `/certificates` |
| Scans | Status totals + hosts seen (all jobs) and the last 20 jobs | `/scans` |
| Flags | Detection-state counts: MAC mismatches, cable mismatches, duplicate MACs, unconfirmed discovered hosts | `/review` |
| Devices | By category, by health (worst linked-IP status, same as the devices page), racked vs unracked | `/devices` |
| Monitors | Up/down/unknown, kind mix, enabled count, due-for-check now — only present when the monitor lane exists (v7) | `/monitors` |
| Rack audits | Placeholder section that appears only if the v9 `rack_audits` table exists | `/review` |

Big sections are capped at **500 rows** and show a
*truncated* marker when the cap bites — honesty over completeness. The
per-section CSVs carry the same bounded rows; full exports live on the
entity pages.

## Export

- **Print** — `/reports/print` renders every section as a flat detail
  table for `window.print()` (save-as-PDF works there). Charts don't
  print; the tables are the report.
- **Export .xlsx** — one workbook, one sheet per section in the page's
  order, header row + values only. Filename:
  `ipambox-report[-<site-slug>]-YYYYmmdd.xlsx`.
- **Per-section CSV** — the `⤓` button on each card downloads
  `report-<section>[-<site>]-YYYYmmdd.csv` with a UTF-8 BOM (the
  Hebrew-in-Excel convention).

## Email

**Email** (requires write permission) sends a text digest — headline
metrics plus open flags, expiring certs, monitors down, failed scans —
to every enabled notification channel, with a link back to `/reports`.
No attachment by design: channels carry text.

A weekly digest rides the same path when *Settings → Monitoring → Weekly
report digest* is on (`report_email_weekly`, off by default). The
scheduler's stamp lives in Redis alongside the other schedule marks — no
report-run registry exists.

## Not here

- **No historical trending** — there is no snapshots table, and reports
  deliberately don't create one. Everything you see is computed from live
  state at request time.
- **No report-run records** — the report is re-derived on every load; the
  changelog gains nothing from a report view.
