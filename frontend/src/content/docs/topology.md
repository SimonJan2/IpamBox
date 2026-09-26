# Topology Map

**Topology** (`/topology`) draws the network as a canvas: every device is a
node, and edges are *documented cables* — the map shows measured adjacency,
not a diagram guessed from hierarchy.

It complements the [Hierarchy tree](/docs/hierarchy): `/tree` answers "where
does this subnet live?", `/topology` answers "what is physically patched to
what?".

## What an edge means

An edge between two devices means one or more [cables](/docs/devices)
directly join their interfaces. Parallel cables collapse into a single edge
with a `×N` count badge; click an edge to list its member cables and jump to
the cable trace on either device.

Edges are deliberately *direct cables only* — a device → patch panel → device
run renders as two edges ending at the panel, not a synthesized hop. The L1
trace already resolves panel pass-through; the map keeps documented fact and
derived path separate.

## Groups and lanes

Nodes nest inside compound containers — **site → rack group → rack** — laid
out automatically. Devices with no rack sit in a dashed *No rack* lane inside
their site; devices with no site land in *No site*.

## Health overlay

Each node carries a colored dot rolled up from its linked addresses' worst
status (same worst-of rule as the device list): offline → discovered → dhcp →
reserved → active. Devices with no addresses show a hollow "unmonitored" dot.
Toggle **Health** in the toolbar to hide the overlay — the choice persists
per browser.

Edges flagged by cable validation (interface speed/type mismatches) draw in
red with a `⚠`.

## Unlinked hosts

Discovered addresses that belong to a prefix but to no device appear in a
dimmed *Unlinked hosts* lane — the map stays honest about what isn't
documented. Toggle them with **Unlinked hosts** (off by default — on real
inventories they can outnumber devices many times over); the filter is part
of the URL, so a filtered view is bookmarkable.

## Layouts

The initial layout is computed automatically. You can drag nodes (and whole
groups) to rearrange, but nothing persists until you hit **Save layout** —
positions save per node under the shared `main` key (`data:write` required).
**Auto-layout** resets the canvas to the computed arrangement. Saved
positions apply only to nodes that still exist; new nodes fall back to the
computed spot.

The canvas is a lens, not an editor — rack placement and cabling still happen
in their own UIs.

## Getting around

- `g t` jumps straight to the map; it's also in the IPAM nav group and the
  command palette.
- Minimap + zoom controls are built in; click a node for a summary panel,
  double-click to open the device.
