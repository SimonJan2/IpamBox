# VLANs

Two levels: **VLAN groups** bundle related VLANs (e.g. per-site or per-role),
and **VLANs** carry the actual VID. Prefixes link to a VLAN so the subnet
list shows which L2 domain each network rides on.

## VLAN fields

| Field | Notes |
|---|---|
| **VID** | The 802.1Q tag (1–4094) |
| **Name** | e.g. `Users`, `Mgmt`, `IoT` |
| **Group** | Optional VLAN group membership |
| **Site** | Optional site link |
| **Status** | `active`, `reserved`, or `deprecated` |

## Statuses

- **active** — in production use
- **reserved** — allocated but not yet deployed
- **deprecated** — being retired; kept for history

## Tips

- Keep a group per site if the same VID is reused with different meaning at
  different locations.
- Linking a VLAN to a prefix is done from the prefix dialog, not here.
- Lists support the usual affordances: reorder, pin, tag, row color, history.
