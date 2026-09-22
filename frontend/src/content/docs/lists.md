# Custom Lists

User-defined tables for data that doesn't fit a fixed entity — server
rosters, contact lists, environment matrices, anything that used to live in a
workbook sheet and lose its shape on import.

A list owns its **columns** (ordered, typed) and its **rows** (JSON data
keyed by column), so "שרתים בייצור" stays a table with a `Guest OS` column
instead of being dissolved into asset notes.

## Column types

| Type | Behavior |
|---|---|
| **text** | Free text, Hebrew-aware search |
| **ip** | Resolves live against `ip_addresses` — status dot, last-seen, click → address drawer. Unresolved IPs render muted/dashed, which surfaces drift between the list and the IPAM. Comma-separated cells resolve each address. |
| **date** | Renders through the expiry badge — overdue / days-left styling |
| **select** | Fixed options rendered as colored chips; used for facets |
| **number** | Numeric, right-aligned sort |
| **url** | Clickable external link |
| **owner** | Person/responsibility — renders like select chips |

Columns are keyed positionally (`c0`, `c1`, …) — **renaming or relabeling a
column never touches the stored data**. Removing a column hides it; the cell
values are kept.

## Working with a list

Each `/lists/{slug}` page is a full table: sorting, inline editing per cell
type, drag-and-drop reordering, pinning, row colors, Hebrew-folded search,
saved views, and CSV export — the same mechanics as every other page.

- **Pin** important rows to the top; **color** rows for status.
- **Add Row** creates a blank row; cells fill in by editing.
- **Select rows** with the checkboxes for bulk actions — pin, unpin, set or
  clear row color, delete.
- **Settings** (gear icon) renames the list, edits columns (relabel, change
  type, drag to reorder, add, remove), and picks the **key column**.

## The key column & re-imports

The key column is the merge identity (e.g. `Name`). When the same sheet is
imported again:

- Changed cells update in place; new rows are created.
- Rows absent from the source are **kept** and reported as *missing from
  source* — never silently deleted.
- Rows you edited by hand are protected: if the sheet disagrees, the manual
  value wins and the row is reported as a conflict.
- Pins, colors, ordering, and manually-added rows always survive.

## Where lists come from

- **Import file** on `/lists` — drop any `.xlsx` or `.csv`, pick the sheet,
  name the list, choose a merge key, dry-run, commit. CSV exports decode as
  UTF-8 or ANSI-Hebrew (cp1255) automatically.
- The [import wizard](/docs/import) offers **Import as → Custom list** per
  sheet; unknown-family sheets suggest it by default. With *also import to
  IPAM* enabled, a server sheet feeds both — the list keeps its human shape
  while its IPs still land in `ip_addresses`.
- Or create an empty list and build it by hand.

List names and row key values appear in [global search](/docs/search-and-shortcuts).
