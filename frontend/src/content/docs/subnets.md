# Subnets

Subnets (prefixes) are the heart of the IPAM. Each lives inside a VRF, may
link to a site and a VLAN, and contains IP addresses — or, as a `container`,
other prefixes.

## Statuses

| Status | Meaning |
|---|---|
| `active` | Production network |
| `reserved` | Allocated, not yet deployed |
| `deprecated` | Being retired |
| `container` | Holds child subnets — exempt from overlap checks |

## Overlap safety

Within one VRF, overlapping CIDRs are rejected by a PostgreSQL GiST exclusion
constraint — the database enforces it, not app code. Across VRFs the same
CIDR is fine. `container` prefixes are exempt so `10.0.0.0/16` (container)
can hold `10.0.1.0/24` (active) as a child. Containers can't be moved under
a prefix they'd conflict with, and moving a container takes its children
along.

## The prefix detail page

Opening a subnet shows breadcrumbs (Site → VRF → prefix), utilization stats,
and two views of its address space:

### Subnet matrix

A `/24`-style grid — one cell per address, banded by IP ranges. Arrow keys
move between cells, **Enter** opens an address, **drag** selects a span for
bulk actions, **Esc** clears the selection.

### List view

A sortable table of every address with aggregated **free ranges** between
used blocks, plus per-IP actions. The filter panel narrows by status, role,
hostname, and more.

### Utilization numbers

`total_ips` / `usable_ips` / `used_ips` / `free_ips` and a utilization
percentage are computed per prefix. IPv6 prefixes show `—` for capacity —
a /64 has more hosts than `Number.MAX_SAFE_INTEGER` — but `used_ips` stays
accurate. Network and broadcast addresses (`unusable_first`/`unusable_last`)
are excluded from usable counts.

## Allocating the next free IP

"Next available" uses `SELECT … FOR UPDATE` plus `UNIQUE(vrf_id, address)`:
concurrent allocations can never hand out the same address twice, network/
broadcast boundaries are skipped, and defined **IP ranges** are excluded
automatically.

## IP ranges

Named ranges inside a prefix with a role of `dhcp`, `pool`, or `reserved`.
They show up as bands in the subnet matrix and are skipped by allocation.

## Print view

Each prefix has a print-friendly page (the print action on the detail view)
that renders the address list cleanly for audits and wall-of-ops printouts.

## Gateway & DNS

A prefix can record its **gateway** and up to four **DNS resolvers** — edit
the subnet or use the *Add network* wizard. The gateway must be inside the
prefix (resolvers may live anywhere — they often do).

Each technical address that falls inside the prefix is mirrored into a real
`reserved` address row tagged `technical: gateway|dns` — it appears on the
matrix with its own glyph (⌂ gateway, ≋ resolver), is excluded from next-IP
allocation, and is fully audited in the changelog. Clearing the field removes
the row *only* while it's still exactly what the system wrote — a row anyone
edited is kept. A row you created yourself at that address is never touched.

## Pools & static assignments

Addresses inside an `ip_ranges` range automatically record membership
(`ip_range_id`) — the drawer shows "in pool …" and the address list can be
filtered by `ip_range_id`. Creating or editing an `active`/`reserved` address
inside a `dhcp`/`pool` range is rejected with a conflict naming the range —
a DHCP server may hand the address to a client. Pass `force=1` (or click
*Assign anyway* in the drawer) to allow it anyway; the override is recorded
as `custom_fields.pool_override` for auditing. `dhcp`-status rows inside a
pool are always fine, and scanner observations are never blocked.

Workbook/CSV imports document existing reality, so a deliberate import acts
as the force: statics inside a pool land with the `pool_override` marker and
the commit report notes them ("inside a pool (override marked)") instead of
rejecting the row — or the whole batch.

## Add network wizard

The **Add network** button on the Subnets page walks through VLAN (new or
existing) → subnet → gateway/DNS → DHCP pool → review, then creates
everything in a single transaction via `POST /networks`. If any step is
invalid, nothing is created — a half-built network is worse than none.
