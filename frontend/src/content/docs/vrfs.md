# VRFs

VRFs (virtual routing & forwarding instances) model separate routing tables.
They're the answer to "the same subnet exists in two places": overlapping
CIDRs are allowed **across** VRFs but are rejected **within** a single VRF —
enforced by a PostgreSQL exclusion constraint, not by convention.

## Fields

| Field | Notes |
|---|---|
| **Name** | e.g. `Global`, `Management`, `Guest` |
| **RD** | Route distinguisher, free text (e.g. `65000:100`) |
| **Site** | Optional site link |
| **Description** | Free text |

A **Global VRF** is seeded by the initial migration so a fresh install always
has somewhere to put prefixes.

## Overlap rules in practice

- `10.0.0.0/24` in VRF `A` **and** in VRF `B` → allowed.
- `10.0.0.0/24` and `10.0.0.0/25` both inside VRF `A` → rejected unless one is
  a `container` prefix holding the other as a child.
- Scans that don't name a VRF are assigned one automatically when an
  exact-match prefix lives in exactly one VRF.

## Working with the list

Same list affordances as everywhere: drag-to-reorder, pinning, inline
descriptions, tags, row colors, and per-row history. See
[Tags](/docs/tags) and [Row Colors](/docs/row-colors).
