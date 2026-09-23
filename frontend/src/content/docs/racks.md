# Racks

Physical rack elevations — which devices sit in which U slots, on which face.

## The list

[Racks](/racks) works like the other entity pages: search, column sort, pin,
drag to reorder, row colors, history. Each row shows the device count and a
used-U bar (`used_u / height_u` — front and rear gear sharing a U counts once).

## Rack detail

Open a rack to see its **elevation**: an SVG drawing of the rack, U1 at the
bottom, devices as colour blocks. The **Front / Rear** toggle picks which
face is drawn — front and rear devices legitimately share U slots, so each
view shows only its own face (plus `both`-face gear like shelves).

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

### Health overlay

The **Health** toggle (on by default, remembered per browser) draws a status
dot on every device block — the live scan status of its linked IP address,
using the same colors as the address table:

| Dot | Meaning |
|---|---|
| green | `active` |
| amber | `reserved` |
| cyan | `dhcp` |
| violet | `discovered` |
| zinc | `offline` |
| grey | unmonitored — no linked IP |

Click a device block (or a table row) for a detail card: name, U range, face,
linked [asset](/docs/inventory) and IP address — with the IP's status badge
and relative *last seen* ("2h ago"). The device table below lists every
placement top-down, including a Status column for the linked IP.

### Finding free space

The header shows a **next free U** hint for a 1U front device. In the
add/edit device dialog, **Find free U** next to the U position field asks the
API for the *lowest* or *highest* contiguous span that fits the entered
height on the chosen face — face-aware, so a front device may legally sit
opposite rear gear in the same U.

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
| **Height (U)** | 1–100, default 42 |
| **Rail width** | 19″ or 10″ |
| **Description / Notes** | Free text |

Devices: name, device type (free text or library slug), U position, height,
face, colour, category, manufacturer/model, linked asset/IP, notes. The
**device library** in the add dialog pre-fills common gear (servers,
switches, PDUs, blanks).
