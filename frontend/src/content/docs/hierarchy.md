# Hierarchy Tree

**Hierarchy** (`/tree`) renders the whole IPAM as an expandable tree:

```
Site → VRF → Prefix → child Prefix → …
```

It's the fastest way to see *where* a subnet lives and how full each branch
is.

## Reading the tree

- **Site nodes** — all prefixes grouped under their site; a catch-all bucket
  holds prefixes with no site.
- **VRF nodes** — per-site routing instances with their RD.
- **Prefix nodes** — the CIDR, its status, linked VLAN, and utilization.

## Roll-up utilization

Parent prefixes aggregate their descendants: `agg_used_ips` sums every used
address beneath the node, `allocated_pct` tells you how much of the container
is carved into children, and `descendant_count` sizes the branch. A container
that's 100 % allocated but 40 % used is fully *assigned* yet still half
*empty* — the tree surfaces that difference at a glance.

## Tips

- Click a prefix to jump to its [detail page](/docs/subnets) (matrix, list,
  ranges, actions).
- Expand/collapse state is per-session; use the tree for orientation and the
  [command palette](/docs/search-and-shortcuts) for targeted jumps.
