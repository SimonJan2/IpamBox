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

[Devices](/devices) works like the other entity pages: column sort, pin,
drag to reorder, row colors, history. Each row shows the device's
**placement** (rack + U range, or *unracked*), its **IP count**, and its
**health rollup**.

The **Filters** button opens a faceted panel (a Sheet on narrow screens)
with live counts — search on top, then facets for health (the five IP
statuses + *unmonitored*), placement (racked / unracked / in-carrier), site,
rack, rack group, manufacturer / model / category / device type (substring,
Hebrew-folded, with datalists of values present), face, has-IP, and wiring
(cabled / partial / uncabled — computed from the interface/cable rollup).
Active facets render as removable chips in the toolbar, and every facet is a
URL param (`?unracked=1&site_id=3&face=front&wiring=uncabled`), so a filtered
view is bookmarkable, survives reload, and can be named via **Saved views**
(built-ins: *Unracked inventory*, *Offline*, *No IP linked*).

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

## Export & import

The toolbar's **Export** dropdown downloads the *currently filtered* set —
the URL's facet params are appended to the export URL, so a filtered view
exports exactly what it shows (the filename marks it `devices-filtered.*`).

- **CSV** — UTF-8 with BOM (opens cleanly in Excel, Hebrew included).
  `columns=` whitelists columns for lean exports.
- **XLSX** — a single `devices` sheet, plain values.

Column order is the round-trip contract: `id, name, device_type,
manufacturer, model, category, serial_number, mac_address, site, rack,
rack_group, u_position, u_height, face, carrier, slot, slot_layout, watts,
weight_kg, ips, ip_count, interface_count, cabled_count, source, notes,
created_at`. Site/rack/rack-group/carrier export as **names**, `ips` as a
space-separated address list, and `id` stays so re-import can pin exact
rows for updates.

**Import** (write permission) opens the smart-import dialog: pick a `.csv`
or `.xlsx`, review the auto-mapped columns (English, Hebrew and NetBox
headers all map — NetBox's `device_role`→device type, `device_type`→model,
`position`→U), fix any flagged-unmapped column, then **Run preview**.
Rows match existing devices by `id` → `serial_number` → `mac_address` →
`name`+site (an ambiguous name is an error, never a coin flip), and the
preview shows each row's action with honest `{field: [old, new]}` diffs in
update mode. Placement conflicts, unknown sites/racks/carriers and bad
values are per-row errors that name the offender; `unracked_on_missing`
salvages rows whose rack (or its rack_group qualifier) can't be resolved —
they land as unracked inventory with a note, ambiguity still errors. Carrier trays and their
children are handled two-pass — a file can mount children on a carrier it
also creates, and children inherit rack/U/face. `ips` only ever links
*existing* addresses (unknown tokens warn, never create). Commit is
all-or-nothing unless `force` is on; every write goes through the normal
device paths so the [changelog](/docs/history) records imported changes.

The same importer runs inside [rack bundles](/docs/racks#export--import) —
a `devices` sheet in a rack/group workbook follows these exact rules, with
`name` matching scoped to the rack the row is being placed into.

## API sketch

```
GET    /api/v1/devices?q=&rack_id=&site_id=&group_id=&unracked=&mounted=
       &face=&manufacturer=&model=&category=&device_type=&source=&has_ip=
       &wiring=&health=            # every page facet is a param; CSV sets
                                   # (face=front,rear), AND semantics, 422
                                   # on bad values; wiring/health facet after
                                   # the aggregates so total stays honest
POST   /api/v1/devices              # unracked or placed (rack_id + u_position)
GET    /api/v1/devices/{id}         # detail: ips[], asset, rack, carrier, health
PATCH  /api/v1/devices/{id}         # attrs + placement (rack_id=null unracks)
DELETE /api/v1/devices/{id}         # real delete — IPs unlink
POST   /api/v1/devices/reorder
GET    /api/v1/devices/export.csv   # every list param + columns= whitelist
GET    /api/v1/devices/export.xlsx  # same set, one 'devices' sheet
POST   /api/v1/devices/import       # raw file + filename=; dry_run=1 (default),
                                    # on_match=skip|update, unracked_on_missing,
                                    # mapping={header:field}, force, detect
PATCH  /api/v1/addresses/{id}       # device_id link/unlink lives here too
```

The rack routes (`/racks/{id}/devices…`) are unchanged — they manipulate the
same `devices` rows' placement columns, and a rack-side DELETE unracks
rather than deletes.
