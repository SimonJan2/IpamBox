# Tags

Colored labels you can attach to **sites, VRFs, prefixes, and addresses** —
for "prod", "legacy", "customer-X", or whatever taxonomy you run.

## Fields

| Field | Notes |
|---|---|
| **Name** | Display name |
| **Slug** | Auto-derived identifier |
| **Color** | The chip's color, picked from a palette |
| **Description** | Inline-editable right in the table |

## Attaching tags

- From a row's **tag picker** (the tag icon in row actions) — toggle tags on
  the object.
- From an **edit dialog** — the tag field inside create/edit forms.
- In **bulk** — select rows on an entity list or a span in the subnet matrix
  and apply a tag to all of them.

Tag chips render on rows everywhere the object appears — lists, drawers,
search results.

## Working with the list

- **Drag to reorder** — this ordering is live and shared (no sort controls on
  this page).
- **Pin** a tag to keep it at the top.
- **Row colors** work here too — a tag row can itself be tinted.
- Every change is in the [Changelog](/docs/changelog); deleting a tag cleanly
  drops its assignments everywhere.

Deleting a tagged object likewise removes just the assignments — the tag
itself survives.
