# Devices

First-class hosts — a device *exists* independently of any rack and owns any
number of IP addresses.

A device is the thing that has a rack placement (optionally), has IPs (often
several — management + service + iLO), and may link an
[asset](/docs/inventory) record for lifecycle/catalog data. Devices used to
live inside racks as `rack_devices` rows; now they're their own entity — the
same rows appear on rack elevations, but they survive being unracked and can
carry many addresses.

## The list

[Devices](/devices) works like the other entity pages: search (name, model,
serial — Hebrew-folded), column sort, pin, drag to reorder, row colors,
history. Each row shows the device's **placement** (rack + U range, or
*unracked*), its **IP count**, and its **health rollup**. The **Unracked**
filter button scopes the table to devices with no rack placement.

- **New device** creates unracked inventory — fill in placement later by
  patching `rack_id`/`u_position`, from the rack editor, or from the rack's
  device form.
- Clicking a row opens the device detail page.

## Device detail

`/devices/[id]` is the device's home:

- **Placement card** — the rack name (linking straight to its elevation at
  the right U), U range, face; or "unracked". Carrier children see their
  carrier + slot; carriers see their slot layout.
- **Identity card** — manufacturer/model, serial, MAC, site, linked
  [asset](/docs/inventory), power/weight.
- **IP addresses** — the device's whole address set with status and last
  seen. Link an existing address with the picker (type to search across all
  addresses — hostname, vendor and address all match) and unlink with the
  broken-link icon. Linking an address that's on another device moves it —
  one IP belongs to at most one device.
- **Interfaces** — the device's port grid: generate a whole set in one
  click (`Gi1/0/` × 48, or a patch panel's front+back via a pair prefix),
  cable ports to other devices, and trace the L1 path. See
  [Cabling](/docs/cabling).
- **Notes** — inline-editable.
- **History** — every create/update/delete, including placement moves
  (rack → unrack → rack changes are audited as updates).

## Health rollup

Device health is the **worst status across its linked IPs** — that's what
the elevation dot and the list/detail badges show:

| Precedence (worst first) | Dot |
|---|---|
| `offline` | zinc |
| `discovered` | violet |
| `dhcp` | cyan |
| `reserved` | amber |
| `active` | green |
| *(no linked IPs)* | grey — unmonitored |

So the box goes red-dot the moment its iLO drops off even if the service IP
is fine — the "health IP" shown on the rack panel is the worst-status
address driving that rollup.

## Devices vs racks

- Placing a device (via `PATCH rack_id`, the rack form, the elevation
  editor, or create-with-placement) runs the same face-aware collision
  rules as always — see [Racks](/docs/racks).
- **Unracking** (the rack row's unrack action, or `PATCH rack_id=null`)
  clears placement but keeps the device and every IP link.
- **Deleting a rack** unracks every device in it — devices are never
  cascade-deleted.
- **Deleting a device** (`/devices/[id]` → trash) removes the row itself:
  its IPs unlink (SET NULL — the addresses survive) and carrier children
  unmount.
- The rack device form's single **Linked IP** field keeps its replace
  semantics — it sets the device's whole IP set at once. Additive per-IP
  management lives here and on the IP drawer's **Device** field.

## From the IP drawer

Every [IP address](/docs/addresses) drawer has a **Device** field: pick an
existing device (name/model/serial search) or use **+ create device from
this IP** — it pre-fills the device from the address's hostname, MAC and
vendor, then links the address on save.

## API sketch

```
GET    /api/v1/devices?q=&rack_id=&unracked=&site_id=
POST   /api/v1/devices              # unracked or placed (rack_id + u_position)
GET    /api/v1/devices/{id}         # detail: ips[], asset, rack, carrier, health
PATCH  /api/v1/devices/{id}         # attrs + placement (rack_id=null unracks)
DELETE /api/v1/devices/{id}         # real delete — IPs unlink
POST   /api/v1/devices/reorder
PATCH  /api/v1/addresses/{id}       # device_id link/unlink lives here too
```

The rack routes (`/racks/{id}/devices…`) are unchanged — they manipulate the
same `devices` rows' placement columns, and a rack-side DELETE unracks
rather than deletes.
