# Overview

IpamBox is a self-hosted IP address manager (IPAM) with a built-in LAN
scanner. It keeps your **documented** network and your **real** network in
sync: you model the address space, the scanner verifies it, and drift shows
up as data instead of surprises.

## The data model

Everything hangs off one hierarchy:

```
Site → VRF → Prefix → IP address
```

- **Sites** are physical or logical locations (branches, DCs, floors).
- **VRFs** are routing instances inside a site — overlapping CIDRs are
  allowed *across* VRFs but rejected *within* one.
- **Prefixes** are subnets. A `container` prefix holds child subnets and is
  exempt from overlap checks.
- **IP addresses** live inside prefixes and carry status, role, MAC,
  hostname, and discovery metadata.

Around that core sit **VLANs**, **IP ranges** (dhcp/pool/reserved blocks
excluded from allocation), **tags**, and **row colors**.

## A tour of the UI

The sidebar is grouped like the data:

| Group | What's inside |
|---|---|
| *(top)* | Dashboard — fleet stats, expiring certs, MAC mismatches, last scan |
| **IPAM** | Sites, VRFs, VLANs, Subnets, Hierarchy tree |
| **Inventory** | Circuits, Certificates, Inventory (assets), Services |
| **Operations** | Discovery Inbox, Scans, Import, Changelog |
| **System** | Tags, Settings, Docs (this guide) |

The header holds the **Search** button (⌘K / Ctrl+K), the **keyboard
shortcuts** button, and **Quick scan**. The sidebar footer shows the signed-in
user and collapses to an icon rail.

## Documentation vs. API docs

This Docs section is the user guide. The machine-readable API reference
(Swagger) lives on the API service at `http://<host>:8001/docs` — same path,
different port. The UI talks to it for you; open it directly for scripting.

## Where to go next

- New install? Start with [Accounts & Roles](/docs/accounts-and-roles).
- Modeling a network? [Sites](/docs/sites) → [VRFs](/docs/vrfs) →
  [Subnets](/docs/subnets) → [IP Addresses](/docs/addresses).
- Have a spreadsheet? Jump to [Import](/docs/import).
- Want the network to check itself? [Scans](/docs/scans) and the
  [Discovery Inbox](/docs/discovery).
