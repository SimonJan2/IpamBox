# Circuits

The WAN circuit register — one row per provider line, linked to a site.

## Fields

| Field | Notes |
|---|---|
| **Env** | Environment tag (prod / backup / test…) |
| **Site** | Site link; `site_number`, `site_code`, `site_name` are denormalized for fast lists |
| **Line type** | Fiber / ETH / DSL… |
| **Bezeq circuit ID** | Provider circuit identifier |
| **Node** | Aggregation node / POP |
| **BW down / up** | Provisioned bandwidth |
| **WAN IP** | The circuit's WAN address |
| **App client # / name** | Application-portal client reference |
| **App service type** | Provider service classification |
| **Contact / Status / Notes** | Free text |
| **Retired** | `is_retired` keeps history without deleting |

## Sources

Most circuit data typically arrives via the
[workbook importer](/docs/import) — the circuits sheet doubles as a site
directory (site name → site number + prefix mapping), so it's a good first
sheet to import. Rows keep their `import_batch_id` provenance.

## Working with the list

Reorder, pin, tag, color rows, inline-edit cells, and per-row history — the
same affordances as every IpamBox list. Search hits appear in the
[command palette](/docs/search-and-shortcuts) under "Circuits".
