# IP Addresses

Individual addresses live inside a [prefix](/docs/subnets) and carry both
*documented* intent and *observed* reality.

## Statuses

| Status | Meaning |
|---|---|
| `active` | Documented and expected live |
| `reserved` | Allocated, not deployed |
| `dhcp` | Handed out dynamically |
| `discovered` | Seen by a scan but not yet confirmed — review in the [Discovery Inbox](/docs/discovery) |
| `offline` | Was `active`, but recent scans stopped finding it |

The scanner flips `active → offline → active` automatically; only
`discovered` needs a human decision.

## Roles

`vip`, `vrrp`, `hsrp`, `glbp`, `carp`, `secondary` — mark addresses that
float between devices so reconciliation doesn't treat them as ordinary
hosts.

## Fields worth knowing

- **MAC / vendor** — vendor is resolved from the bundled IEEE OUI database.
- **Hostname, open ports, device type** — filled by scans (router / printer /
  camera / nas / phone / tv / iot / vm / server / workstation).
- **NAT inside** — link an outside address to its inside translation.
- **Serial, switch name/port, counter location, custom fields, notes** —
  inventory-grade metadata per address. The switch fields also have a
  structured sibling — **connected interface** (below) — that points at a
  real port; the free text stays as the import record.
- **Connected interface** — the far-end port (usually a switch's) this
  address is patched into, picked in the drawer as device → interface.
  See [Cabling](/docs/cabling) for the full L1 model and the
  `match-free-text` transition helper.
- **Last seen** — the last scan that observed the host.
- **`mac_mismatch` flag** — a scan saw a different MAC than documented; the
  live value wins but the address is flagged for review and counted on the
  dashboard.

## Provenance

Every address records **where it came from** in `source`:

`manual` — created or reserved in the UI · `import` — workbook/CSV import ·
`scan` — first seen by the network scanner (`snmp` and `integration` are
reserved for future writers).

The scanner refreshes observed fields (last seen, MAC, vendor, ports) on any
address but **never claims ownership** — a manual or imported row keeps its
source, so a scan can't launder curated data into "discovered". The filter
panel's **Source** facet and the `?source=` API/export parameter select by
it, and the IP drawer shows it as a badge next to status.

## Bulk operations

Select rows (or drag a span in the [subnet matrix](/docs/subnets)) to set
status, set role, assign tags, or delete — all at once, each change logged.

## CSV import & export

- **Export** produces UTF-8-BOM CSV that opens cleanly in Excel — and honors
  the active filters, so a filtered view exports exactly what you see.
- **Import** is all-or-nothing with a per-row error report when anything
  fails validation.

## The IP drawer

Opening an address slides out a detail panel: every field, its tag chips,
the NAT partner, the owning [device](/docs/devices) link, the **connected
interface** picker (far-end switch port — the structured sibling of the
switch_name/switch_port free text, which still shows as fallback), and the
object's own [changelog](/docs/changelog) history.
