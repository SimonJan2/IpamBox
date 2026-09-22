# Inventory

The asset register — hardware and software inventory with serials, linked to
sites.

## Fields

| Field | Notes |
|---|---|
| **Kind** | `hardware` or `software` |
| **Category** | Free-text grouping (server, switch, license…) |
| **Vendor / Model** | What it is |
| **Purpose / Version** | What it's for / what it runs |
| **EOL on** | End-of-life date |
| **Support status** | e.g. `under support`, `EOL`, `best effort` |
| **Serial number** | Primary tracking key — searchable from the palette |
| **Site** | Where it lives |
| **Notes** | Free text |

## Sources

Assets usually arrive through the [workbook importer](/docs/import) (the
assets/inventory sheet families) and keep `import_batch_id` provenance back
to their upload batch — but rows can also be created and edited by hand.

## Working with the list

Reorder, pin, tag, row color, inline edits, history. Serial numbers and
vendor/model pairs surface in [command palette](/docs/search-and-shortcuts)
results under "Inventory".

## Reading the page

- **Stats strip** — hardware/software split, EOL passed, EOL within 90 days,
  missing serial, no site. Each card is a click-to-filter shortcut.
- **Kind tabs** — All / Hardware / Software segment the table.
- **Group by** — collapse rows under category, site, or vendor headers.
- **Columns** — visibility picker for dense vs. minimal views.
- **Saved views** — built-ins like "EOL < 90 days" and "Routers w/o site".

For sheet-shaped data that isn't an asset (server rosters, contact lists…),
see [custom lists](/docs/lists).
