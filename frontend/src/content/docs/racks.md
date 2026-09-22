# Racks

Physical rack elevations — which devices sit in which U slots, on which face.

## The list

[Racks](/racks) works like the other entity pages: search, column sort, pin,
drag to reorder, row colors, history. Each row shows the device count and a
used-U bar (`used_u / height_u` — front and rear gear sharing a U counts once).

## Rack detail

Open a rack to see its **elevation**: a read-only SVG drawing of the rack,
U1 at the bottom, devices as colour blocks. The **Front / Rear** toggle picks
which face is drawn — front and rear devices legitimately share U slots, so
each view shows only its own face (plus `both`-face gear like shelves).

Click a device block (or a table row) for a detail card: name, U range, face,
linked [asset](/docs/inventory) and IP address. The device table below lists
every placement top-down.

## Placement rules

- `u_position` is the device's **bottom** U, counted from 1.
- Front + rear in the same U is fine; front + front (or rear + rear) in the
  same U is rejected with a conflict error. A `both`-face device conflicts
  with anything overlapping its span.
- Devices can't extend above `height_u`.
- A device may link to an [asset](/docs/inventory) and an IP address.

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
  with existing placements, and which are skipped (carrier-mounted or sub-U
  gear has no IpamBox equivalent). Choose **merge** (keep existing, skip
  conflicts) or **replace** (wipe current devices first). Imported devices
  carry a `rackula` source badge.

## Fields

| Field | Notes |
|---|---|
| **Name** | Searchable from the palette |
| **Site / Room** | Where the rack lives (room is free text) |
| **Height (U)** | 1–100, default 42 |
| **Rail width** | 19″ or 10″ |
| **Description / Notes** | Free text |

Devices: name, device type (free text or library slug), U position, height,
face, colour, category, manufacturer/model, linked asset/IP, notes. The
**device library** in the add dialog pre-fills common gear (servers,
switches, PDUs, blanks).
