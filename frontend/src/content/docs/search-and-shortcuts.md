# Search & Shortcuts

IpamBox is keyboard-first. Every shortcut is listed in the overlay opened by
`?` or the **keyboard button** next to Search in the header.

## Command palette

Open with **⌘K / Ctrl+K**, the `/` key, or the Search button in the header.
Type to search across the whole IPAM:

- IP addresses, subnets, sites, VRFs, VLANs
- Circuits, certificates, inventory assets, services
- Matching **Docs** guides (they appear as a "Docs" group)

Paste a bare IP address and the palette offers a **Jump** result that lands
directly on the owning prefix with the address highlighted — preferring the
address's documented owner, then the deepest containing prefix.

With no query, the palette shows your five most recent destinations. Results
respect Hebrew final-letter folding, so `רשת` also matches `רשתו`.

## Go-to chords

Press `g`, then one of:

| Keys | Destination |
|---|---|
| `g d` | Dashboard |
| `g p` | Subnets |
| `g s` | Scans |
| `g i` | Discovery inbox |
| `g c` | Changelog |
| `g h` | Docs (this section) |

## Table navigation

| Key | Action |
|---|---|
| `j` / `↓` | Next row |
| `k` / `↑` | Previous row |
| `Enter` | Open the focused row |
| `Home` / `End` | First / last row |
| `Alt+↑` / `Alt+↓` | Move the focused row (orderable lists) |

## Subnet grid

Inside a prefix's [subnet matrix](/docs/subnets):

| Key / gesture | Action |
|---|---|
| `← ↑ ↓ →` | Move between addresses |
| `Enter` | Open the address |
| Drag | Select a span of addresses |
| `Esc` | Clear the span selection |

## Scope rules

Single-key shortcuts never fire while you're typing in a field or while a
dialog/menu is open — so `j`, `k`, `/` and `?` are safe to use as text.
**⌘K / Ctrl+K** is the exception: it toggles the palette from anywhere,
including inside dialogs.
