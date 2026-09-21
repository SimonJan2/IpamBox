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
