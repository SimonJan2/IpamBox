# Row Colors & Color Rules

Two ways to tint list rows so the important things pop — **manual**, set per
row by anyone who can write data, and **rule-based**, managed by admins and
computed server-side.

## Manual row colors

Every list — sites, VRFs, VLANs, subnets, circuits, certificates, assets,
services, tags, and the address list — has a **Set color** action per row.
Pick a tint and the row renders with it for everyone. Clear it the same way.

The **legend** button on a list explains the tints currently in use.

## Color rules (admin)

**Settings → Color Rules** defines conditions that color rows automatically:

| Part | Example |
|---|---|
| **Entity** | `Certificate` |
| **Field** | `expires_on` |
| **Operator** | `within_days` |
| **Value** | `7` |
| **Color** | red |

→ "Certificates expiring within 7 days render red." Operators: `eq`, `neq`,
`contains`, `lt`, `gt`, `within_days`; fields are typed (text, date, bool,
number, enum) so the rule editor only offers operators that make sense.

Rules have a **position** — they apply in order, and the first matching rule
wins. A manual row color overrides rules for that row (the effective tint is
exposed as `display_color`).

## Coverage

Colors are stored in Postgres, computed server-side, and covered by
[backup](/docs/settings) and [changelog](/docs/changelog) — a restore brings
your colors back too.
