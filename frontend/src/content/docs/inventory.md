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
