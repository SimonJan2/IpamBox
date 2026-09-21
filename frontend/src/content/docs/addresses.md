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
  inventory-grade metadata per address.
- **Last seen** — the last scan that observed the host.
- **`mac_mismatch` flag** — a scan saw a different MAC than documented; the
  live value wins but the address is flagged for review and counted on the
  dashboard.

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
the NAT partner, and the object's own [changelog](/docs/changelog) history.
