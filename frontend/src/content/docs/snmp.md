# SNMP Enrichment

Scans learn what answers an ARP. SNMP enrichment makes your own devices
*report themselves*: a switch tells IpamBox which ports it has, whether
they're up, how fast they're running, and which MACs it has learned behind
each port. That data upserts real interfaces and fills the structured
`connected_interface_id` links between IP addresses and switch ports.

All polling is **read-only** — IpamBox only ever sends SNMP GET/WALK
requests to devices you configure. No SET operations, ever.

## Setting up a device

Open a device page and find the **SNMP** card:

1. Flip the toggle on. The card expands when enabled.
2. Pick the **version** — `v1`, `v2c`, or `v3` — and the **UDP port**
   (default 161).
3. Enter the credential:
   - v1/v2c: the read-only **community** string.
   - v3: **user**, **auth key** + protocol (SHA family or MD5), and
     optionally **priv key** + protocol (AES family, DES/3DES). Set only a
     user for authNoPriv; add auth key for authNoPriv→authPriv basics.
4. **Save**. The credential is encrypted at rest (AES-256-GCM under the
   server master key) and is *write-only* — the form always renders it
   empty, a "credential set" chip tells you one is stored, and it never
   appears in API responses, logs, or error messages.
5. Press **Test** — a live sysName/sysDescr probe. A reachable device
   answers with its identity; the response is shown inline.
6. **Poll now** runs a full enrichment pass immediately, without waiting
   for the scheduler.

Enabling SNMP without a stored (or freshly typed) credential is rejected —
a poll that can't authenticate would just burn timeouts.

## What a poll does

In order: `sysName`/`sysDescr` liveness check → IF-MIB interface walk →
bridge-MAC walk → LLDP neighbor walk.

**Interfaces** (`ifIndex`, `ifDescr`/`ifName`, `ifOperStatus`,
`ifAdminStatus`, `ifHighSpeed`, `ifPhysAddress`): every reported port is
upserted into the interface list, keyed by the device's `ifIndex` and
falling back to exact name match. Ports created by the poller carry
`source: snmp` and get their operational state, admin state, speed and
physical address refreshed every poll. Interfaces the device stops
reporting are **not deleted** — their `snmp_seen_at` just goes stale and
the tile dims (about two poll intervals), which is the difference between
"a renamed port" and "a documented truth".

**Bridge MACs** (`dot1dTpFdbPort` and `dot1qTpFdbPort`): each learned MAC
is looked up in `ip_addresses.mac_address`. On a match, the IP gains
`connected_interface_id` pointing at the port — visible as the green link
on the interface tile and in the IP drawer.

**LLDP** is collected for a future cable-validation feature; nothing is
written from it today.

## What enrichment writes — and what it never does

Writes:

- new `source: snmp` interfaces for ports the device reports and the
  inventory lacks;
- observed state on those ports (`oper_status`, `admin_status`,
  `speed_mbps`, `mac_address`, `snmp_seen_at`) — bulk-updated, no
  changelog noise;
- `connected_interface_id` on IPs whose MAC the bridge table places
  behind a port — ORM writes, so they appear in the changelog;
- device stamps: `snmp_sys_name`, `snmp_sys_descr`,
  `snmp_last_ok_at`, `snmp_last_error`.

Never:

- manual interfaces — a port you created by hand (or by generate)
  matched only by name keeps its `source: manual`, kind, speed and MAC;
- manual IP links — `may_write` provenance means `snmp` only fills a NULL
  `connected_interface_id` or replaces a *less* authoritative source
  (scan). A link you set yourself always wins;
- deletions — nothing is removed because a device stopped reporting it;
- SNMP SET — the poller is physically incapable of writing to a device.

## Runtime controls

Settings → **Features → SNMP enrichment**:

| Setting | Default | Effect |
|---|---|---|
| SNMP polling enabled | off | Global kill switch — the worker lane enqueues nothing. Test/Poll buttons still work. |
| Poll interval | 60 min | A device is due when its last poll is older than this. |
| Poll concurrency | 4 | Parallel device polls inside the single per-tick sweep. |
| Per-device timeout | 2 s | SNMP request timeout — a dead device costs only this. |
| Learn interfaces | on | Off = collect but don't create/update ports. |
| Fill connected IP | on | Off = collect MACs but don't write links. |

Polls run on the worker's own lane — one job per minute that iterates the
due set under a small semaphore, so a fleet of dead devices can't starve
scans or monitoring.

## Vendor notes

- **Per-VLAN bridge tables (Cisco and friends):** these devices keep one
  FDB per VLAN, reachable via *community indexing* — poll with community
  `public@vlan-id` (e.g. `public@10`). The poller tries the plain
  community first, then walks `community@1`…`community@N` for the VLANs
  the device reports. Store the plain community; VLAN expansion is
  automatic.
- **Q-BRIDGE (`dot1qTpFdbPort`):** devices that expose the Q-BRIDGE table
  directly don't need community indexing — the poller walks it in the
  same pass.
- **v1-only gear:** works, but `ifHighSpeed` doesn't exist on v1 — speed
  falls back to `ifSpeed`, which saturates at ~4 Gbps.
- **v3 authPriv:** SHA auth + AES privacy are supported (plus MD5/DES for
  legacy gear). Passwords must be at least 8 characters on most agents.
  Agents that scope data behind a non-default context (e.g. snmpsim,
  some appliances) need the credential's optional `context` field —
  empty means the default context.
- **Firewalls:** the poller needs UDP 161 (or your `snmp_port`) from the
  worker container to the device — same reachability as the scanner.

## Troubleshooting

- *Test shows nothing*: check community string, UDP/161 reachability, and
  that the device ACL allows the worker's IP. `snmp_last_error` on the
  card shows the last failure (credentials are never included).
- *Interfaces appear but no links*: the IPs must already have
  `mac_address` set (from ARP scans or manual entry) — the bridge table
  keys on MAC, not IP.
- *Port names doubled*: if a manual port's name doesn't match what the
  device reports (e.g. `Gi1/0/1` vs `GigabitEthernet1/0/1`), the poller
  creates a second `snmp` port rather than renaming yours. Delete or
  rename the manual one to merge.
