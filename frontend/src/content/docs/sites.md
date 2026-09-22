# Sites

Sites are the top of the IpamBox hierarchy — physical or logical locations
such as branches, data centers, or floors. VRFs, VLANs, prefixes, circuits,
assets, and services can all be linked to a site.

## Fields

| Field | Notes |
|---|---|
| **Name** | Display name; Hebrew is fully supported (`dir="auto"` rendering) |
| **Slug** | URL-safe identifier, auto-derived from the name |
| **Code** | Short site code (e.g. `NYC1`) — used by workbook import for sheet→site matching |
| **Site number** | Numeric identifier used by the import planner |
| **Size** | Free-text size classification |
| **Active** | Inactive sites are kept for history but excluded from import matching |
| **Contact / Address / Description** | Free-text metadata |

## Working with the list

- **New site** — needs the *data:write* permission (Contributor and up).
- **Drag to reorder** rows; **pin** important sites to the top. Ordering is
  shared for everyone.
- **Inline edit** the description directly in the table.
- Attach **tags** and set a **row color** from the row actions.
- Every change lands in the [Changelog](/docs/changelog), and each row's
  history button shows its own audit trail.

## Related settings

The **Site codes follow site changes** feature flag (Settings → Features,
on by default) controls whether linked VRF names and circuit/service site
fields update automatically when a site's code, number, or name changes.
When off, stored mismatches are treated as deliberate manual overrides.
