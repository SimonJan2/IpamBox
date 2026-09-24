# Racks

Physical rack elevations — which devices sit in which U slots, on which face.

## The list

[Racks](/racks) works like the other entity pages: column sort, pin, drag
to reorder, row colors, history. Each row shows the device count and a
used-U bar (`used_u / height_u` — front and rear gear sharing a U counts
once), plus a **Capacity** column summing device `watts`/`weight_kg` (dashes
when no device supplies a value).

The **Filters** button opens a faceted panel (a Sheet on narrow screens)
with live counts — search on top (name, room, description, site and group
names — Hebrew-folded), then facets for site, group (with an *ungrouped*
entry), room, height (distinct values present), occupancy (empty / partial /
full over the used-U rollup), and a free-U range. Active facets render as
removable chips in the toolbar, and every facet is a URL param
(`?site_id=58&occupancy=partial&min_free_u=4`), so a filtered view is
bookmarkable, survives reload, and can be named via **Saved views**
(built-ins: *Ungrouped*, *Nearly full*, *Empty*). `min_free_u=4` is the
"where can this 4U box go" query — it facets on the computed
`height_u − used_u` aggregate.

## Rack groups (bayed rows)

A datacenter row is never one rack. **Rack groups** collect racks standing
side by side — the "Rack groups" panel at the top of the racks page lists
them with member counts; clicking a name opens the **row view**
(`/racks/groups/[id]`): the member racks drawn left to right, bottom-aligned
like a real bayed row, each with its own health dots. The strip scrolls
horizontally for wide rows; the header rolls up group totals (U used/free,
Σ watts, Σ kg).

- Assign a rack to a group in its dialog — pick the group and optionally a
  **Position** (left-to-right; blank appends at the row's right end). Setting
  the group back to *None* removes it.
- Group rows filter like VLAN groups: the filter button on a group row
  scopes the rack table to its members (sets the `group_id` facet).
- With write access, the row view's **Edit** toggle lets you drag a device
  sideways onto another rack's U row — a real cross-rack move validated by
  the API. A mounted child dropped on a U row unmounts; a carrier carries
  its children across racks with it.

## Rack detail

Open a rack to see its **elevation**: an SVG drawing of the rack, U1 at the
bottom. Devices whose *device type* matches the bundled library render as
real product photos (front and rear); everything else renders as a colour
block. The **Front / Rear** toggle picks which face is drawn — front and
rear devices legitimately share U slots, so each view shows only its own
face (plus `both`-face gear like shelves).

### Editing the elevation

With write access, the **Edit** toggle (remembered per browser) turns the
elevation into an editor:

- **Drag** a device onto another U slot. Valid start slots tint green,
  conflicting or out-of-range ones red. Dropping on the **rear** view places
  the device on the rear face (front view → front) unless it's `both`.
  Moves are validated by the API — a conflict reverts the move and explains
  which device blocks it. The success toast offers a one-step **Undo**.
- **Keyboard**: focus a device block, then ↑/↓ moves it (skipping blocked
  slots), **F**/**B** sets the face, **Enter** commits, **Esc** cancels.
- **Click an empty slot** to open the add-device form prefilled with that U
  and the view's face.
- **Carrier slots**: dropping a device on a carrier's slot mounts it there
  (slot outlines appear while dragging); dragging a mounted child onto a
  plain U row un-mounts it. Carrier children don't take the arrow keys —
  their slots aren't a linear range.

### Carriers (shelves & trays)

Real racks hold gear that isn't a whole-U full-width box — half-width
switches, RPi trays, quad brackets. A **carrier** is an ordinary rack
device flagged with a *slot layout*; other devices mount into its slots:

| Layout | Slots | Renders as |
|---|---|---|
| `halves` | 2 | vertical split — left / right |
| `quarters` | 4 | 2×2 grid |
| `shelf` | 1 | one full-width tray (useful for grouping) |

- The carrier occupies its whole U span and face like any device; children
  inherit its U position and face (those fields hide in the device form).
- One child per slot; a child never conflicts with rack-level devices — the
  carrier already reserved that space. Children only collide with a sibling
  in the same slot.
- Single level only: a carrier can't mount inside another carrier, and a
  child can't be taller than its carrier.
- Unracking a carrier lifts the whole tray out of the rack — its mounted
  children leave the rack too but stay mounted to it (the tray still
  physically holds them). Devices are first-class rows: removing one from
  a rack never deletes it — it becomes unracked inventory on the
  [Devices](/devices) page.
- The device library includes **1U dual shelf**, **1U quad bracket**, and
  **Rack shelf** starters; any device can become a carrier via the *Carrier
  layout* field.

To mount a device: pick it in the form's **Mounted in** select and choose a
**Slot**, or drag it onto a carrier's slot in the editor.

### Health overlay

The **Health** toggle (on by default, remembered per browser) draws a status
dot on every device block — the device's **health rollup**: the worst status
across *all* its linked IP addresses (a server can own mgmt + service + iLO
IPs; offline beats discovered beats dhcp beats reserved beats active),
using the same colors as the address table:

| Dot | Meaning |
|---|---|
| green | `active` |
| amber | `reserved` |
| cyan | `dhcp` |
| violet | `discovered` |
| zinc | `offline` |
| grey | unmonitored — no linked IPs |

Click a device block (or a table row) for a detail card: name, U range, face,
linked [asset](/docs/inventory) and the health-driving IP — with its status
badge and relative *last seen* ("2h ago"). The **Device →** button jumps to
the [device page](/docs/devices) (all its IPs, links, placement). The device
table below lists every placement top-down, including a Status column for
the health rollup.

### Capacity totals

When any device in the rack carries **Power (W)** or **Weight (kg)**, the
header shows the rack's roll-up — e.g. `Σ 1.2 kW · 34 kg` — hidden entirely
when no device supplies either value. The same sums appear per rack in the
group row view and per group in its header, and the
[dashboard](/) "Rack capacity" card charts the fleet's used/total U with the
fullest racks.

### Finding free space

The header shows a **next free U** hint for a 1U front device. In the
add/edit device dialog, **Find free U** next to the U position field asks the
API for the *lowest* or *highest* contiguous span that fits the entered
height on the chosen face — face-aware, so a front device may legally sit
opposite rear gear in the same U. To find a rack for the device rather than
a slot in a rack, the list's **Free U** filter (`min_free_u`) facets racks
by remaining capacity.

## Export & import

A rack isn't a row — it's a tree: group → racks → devices (→ carriers →
children → interfaces → cables). The toolbar's **Export** dropdown covers
both shapes:

- **CSV (this view)** — flat rack rows for the *currently filtered* set
  (the URL's facet params ride along, so a filtered view exports exactly
  what it shows; the filename marks it `racks-filtered.csv`). Columns:
  `id, name, site, group, group_position, room, height_u, width,
  device_count, used_u, free_u, power_w, weight_kg, description, notes,
  created_at` — `columns=` whitelists them for lean exports.
- **XLSX bundle (this view)** — a multi-sheet workbook carrying the whole
  tree: `groups` (only the groups the exported racks reference), `racks`
  (the flat set above), `devices` (the device export column set — rack,
  site and carrier all by **name**), plus `interfaces` and `cables` when
  the devices have any (cable endpoints addressed by device + interface
  names — ids are meaningless across installs).

The rack detail header's **Export .xlsx** downloads a single-rack bundle
(including its group row so it re-imports cleanly); a group page's
**Export group** downloads the whole row — group, member racks in
position order, every device and its wiring — as `{group}.xlsx`.

**Import** (write permission) reuses the smart-import dialog: pick a flat
racks CSV or a bundle workbook — sheets are detected by their header
signature (unknown sheets warn and are ignored; English/Hebrew aliases
map on every sheet). **Run preview** shows each row's action grouped per
sheet — sites referenced by the bundle are created when missing, groups
match/create by name, racks by `name`+`site` (name alone when
unambiguous), devices per the device importer's rules with names scoped
to the target rack, interfaces by device+name, cables by resolved
endpoint pair. Placement conflicts, ambiguous names and unresolvable
endpoints are error rows — never silently resolved. **When a rack
matches**: `skip` touches nothing in its subtree, `update` patches rack
fields then applies the device rows, `merge` keeps occupants and only
adds devices into free U slots. Matched *devices* follow the same mode —
`update` re-places them per the file (unracked inventory included), while
`skip`/`merge` leave them where they are; a carrier child whose tray
isn't racked then reports skip rather than an error. **Replace devices** unracks a matched
rack's current occupants first — they survive as unracked inventory,
never deleted. Commit is one transaction; `force` commits the valid rows
despite error rows. A group page's **Import into this group** posts the
same dialog with `?group_id=` — every imported rack joins that group
regardless of the file's group column. A group export re-imported into an
empty install rebuilds the identical tree.

## API sketch

```
GET    /api/v1/racks?q=&site_id=&group_id=&ungrouped=&room=&height_u=
       &occupancy=&min_free_u=&max_free_u=
                                   # every page facet is a param; CSV sets
                                   # (height_u=42,24), AND semantics, 422 on
                                   # bad values; occupancy/free-U facet after
                                   # the used_u aggregate so total stays honest
GET    /api/v1/racks/export.csv     # same params + columns= whitelist
GET    /api/v1/racks/export.xlsx    # same params -> groups/racks/devices
                                    #   (+interfaces/cables) bundle
GET    /api/v1/racks/{id}/export.xlsx          # single-rack bundle
GET    /api/v1/rack-groups/{id}/export.xlsx    # the group file
POST   /api/v1/racks/import         # raw file + filename=; dry_run=1 (default),
                                    # on_existing=skip|update|merge,
                                    # replace_devices, group_id=, mapping=,
                                    # force, detect
```

## Placement rules

- `u_position` is the device's **bottom** U, counted from 1.
- Front + rear in the same U is fine; front + front (or rear + rear) in the
  same U is rejected with a conflict error. A `both`-face device conflicts
  with anything overlapping its span.
- Devices can't extend above `height_u`.
- Carrier children skip the rack-level checks entirely — their carrier
  already occupies that U and face. They only conflict with a sibling
  sharing the same slot.
- A device may link to an [asset](/docs/inventory) and any number of IP
  addresses — see [Devices](/docs/devices). Deleting a rack unracks its
  devices (they survive); deleting a *device* is done from its page.

## Rackula round-trip

For heavy layout editing, IpamBox round-trips with
[Rackula](https://github.com/RackulaLives/Rackula) instead of re-implementing
a drag-and-drop editor:

- **Open in Rackula** — appears on the rack page once an admin sets the
  *Rackula instance URL* under [Settings → Features](/docs/settings). It
  opens your layout in that instance via a share URL.
- **.Rackula.zip** — downloads the rack as a Rackula layout archive (import
  it in Rackula's UI the same way).
- **Import from Rackula** — paste a Rackula share URL or upload a
  `.Rackula.zip`; a preview shows which devices will be added, which conflict
  with existing placements, and which are skipped (sub-U gear has no
  IpamBox equivalent). Rackula carriers import as carrier trays and their
  container children mount into slots — Rackula's auto-created trays arrive
  as a "shelf"-layout carrier named **Shelf**. Choose **merge** (keep
  existing, skip conflicts) or **replace** (unrack current devices first —
  they survive as unracked inventory, never deleted). Imported devices
  carry a `rackula` source badge.

## Printing and labels

- **Print** opens `/racks/[id]/print`: a paper-friendly report with rack
  metadata, the **front and rear elevations side by side**, and a full device
  table (U range, face, type, linked asset and IP + status). Save as PDF via
  the browser's print dialog.
- **QR** opens a dialog with a QR code pointing at the rack's live elevation
  URL. **Print label** opens a minimal sticker card (QR + name + URL) sized
  for a physical label — stick it on the rack and scan to open the live view.
  The same QR appears in the print report footer.

## Fields

| Field | Notes |
|---|---|
| **Name** | Searchable from the palette |
| **Site / Room** | Where the rack lives (room is free text) |
| **Rack group / Position** | Bayed-row membership; position orders left-to-right (blank appends) |
| **Height (U)** | 1–100, default 42 |
| **Rail width** | 19″ or 10″ |
| **Description / Notes** | Free text |

Devices: name, device type (free text or library slug), U position, height,
face, colour, category, manufacturer/model, linked asset/IP(s), **Power (W)**,
**Weight (kg)**, notes — plus **Mounted in**/**Slot** for carrier children
and **Carrier layout** to make the device itself a carrier. The single
**Linked IP** field on this form replaces the device's whole IP set; multi-IP
management lives on the [device page](/docs/devices). The **device
library** in the add dialog pre-fills common gear (servers, switches, PDUs,
blanks, carrier trays) — including power/weight where upstream publishes it.

## Device image library

The library behind the picker is a bundled subset of the NetBox
[devicetype-library](https://github.com/netbox-community/devicetype-library)
(~1,600 device types — every upstream device that ships an elevation image,
the complete Check Point / Aruba / HPE-storage families even where no image
exists, plus a curated set of generic rack gear; CC0 — see
`/rack-library/ATTRIBUTION.md` in the shipped files). Entries carry real
dimensions (`u_height`, `is_full_depth`), product photos, and where
upstream publishes them, typical power draw and weight — picking an entry
pre-fills the form's Power/Weight fields, which persist on the device and
feed the rack/group capacity rollups.

- Picking a library entry sets the *device type* slug; the elevation then
  draws the product's front/rear photo instead of a colour block. Rear view
  uses the rear photo, falling back to the front one; entries without
  images keep their colour block. Health dots, selection and editing work
  the same on photo blocks.
- Everything is served from `/rack-library/` inside the app — nothing is
  fetched from the internet at runtime, so it works air-gapped.
- **Refreshing** (maintainers): `cd frontend && npm run build:rack-library`
  re-pulls the curated slug list, every upstream device with an elevation
  image, and the FULL_IMPORT vendor families (Check Point, Aruba, HPE
  storage — image or not) from the upstream repo, re-encodes images as
  ≤400px WebP and rewrites the manifest (`--curated-only` skips the wide
  sweeps); `npm run check:rack-library` verifies the bundle. The generated
  files are committed — refresh them per release, like the OUI database.
