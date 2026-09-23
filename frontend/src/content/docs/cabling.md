# Cabling

The L1 layer — devices own **interfaces**, interfaces get **cables**, and
"what's patched into switch X port 12" becomes a query instead of a memory.
A patch panel needs no special entity: it's just a device whose interfaces
have kind `patch`, with each front port paired to a back port.

## Interfaces

Every [device](/docs/devices) detail page has an **Interfaces** section: a
port grid showing name, kind (`rj45`, `sfp`, `sfp28`, `qsfp`, `console`,
`patch`, `power`, `other`), speed and MAC. Cabled ports are tinted and show
their peer (`device · port`) — click one to open the **trace** drawer.

- **Generate** creates a whole port set in one call: pick a kind, a name
  prefix and a count — `Gi1/0/` × 48 yields `Gi1/0/1…48`. Setting a **pair
  prefix** (`b` for `p`) additionally creates same-indexed back ports and
  links each `p_i ↔ b_i` pair — a 24-port patch panel's front+back in one
  click.
- **Add port** creates a single interface; the edit dialog can rename,
  re-kind, set speed/MAC, and change the pair partner (pairs must live on
  the same device — the two sides of a panel position).
- `connected_ip` is the host-side binding — "this NIC serves this IP" — a
  different link from the device's IP ownership and from the address's
  far-end switch port.

## Cables

A cable joins exactly two interfaces. Each interface terminates **at most
one** cable — trying to cable a busy port returns the existing cable's id.
Cables carry `kind` (`cat5e`/`cat6`/`cat6a`/`dac`/`fiber_sm`/`fiber_mm`/
`power`/`console`/`other`), a physical `color`/`label`, `length_m` and
notes. Cable labels are searchable — global search resolves a label hit to
**both** ends' devices.

Cable a port from its card: pick the peer device (search), then one of its
**free** ports, then kind/color/label. Deleting a port or device takes its
cable with it.

## Trace

Clicking a cabled port opens the trace drawer: the ordered L1 path through
the interface — `device · interface` per hop, with the cable kind/label on
each cable edge. At a `patch` port the walk continues through the panel's
front↔back pair (shown as *panel pass-through* — not a cable) and keeps
going, so `host → panel-front → panel-back → switch` renders as one path.
Traces launched mid-chain still surface the whole path, and loops
terminate at 10 hops.

## IP → interface link

The [IP drawer](/docs/addresses) has a **Connected interface** field — the
far-end port (usually a switch's) the address is patched into. It lives
alongside the legacy `switch_name`/`switch_port` free text, which stays as
the import record and shows as fallback when no link is set.

### Transitioning legacy text

`POST /api/v1/interfaces/match-free-text` is the one-shot matcher: for
every address still lacking a link, a device whose name exactly equals
`switch_name` **and** owns an interface named exactly `switch_port` gets
linked; multiple candidates are reported `ambiguous` (never guessed) and
zero are `unmatched`. Text columns are never touched and every link lands
in the [changelog](/docs/changelog) for review.

## API sketch

```
GET    /api/v1/devices/{id}/interfaces
POST   /api/v1/devices/{id}/interfaces
POST   /api/v1/devices/{id}/interfaces/generate   # {kind, prefix, count,
                                                  #  start_index?, speed_mbps?,
                                                  #  pair_prefix?}
PATCH  /api/v1/devices/{id}/interfaces/{iface}
DELETE /api/v1/devices/{id}/interfaces/{iface}
GET    /api/v1/interfaces/{id}                    # resolved peer + bound IP
POST   /api/v1/interfaces/match-free-text         # {matched, ambiguous, unmatched}

GET    /api/v1/cables?device_id=&site_id=&q=
POST   /api/v1/cables            # 409 when either end is already cabled
PATCH  /api/v1/cables/{id}
DELETE /api/v1/cables/{id}
GET    /api/v1/cables/trace?interface_id=         # ordered hop list

GET    /api/v1/devices/{id}      # gains interface_count + cabled_count
PATCH  /api/v1/addresses/{id}    # connected_interface_id — the structured link
```
