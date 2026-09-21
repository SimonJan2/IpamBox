# Scans

The scanner container runs Scapy with raw sockets (`network_mode: host`,
`NET_ADMIN`/`NET_RAW`, Linux only) and reconciles what it finds against your
documentation.

## The pipeline

Each target CIDR goes through five stages:

1. **ARP sweep** — L2 discovery on the local segment.
2. **ICMP sweep** — ping-socket for hosts that don't answer ARP.
3. **TCP probe** — connection attempts on the configured port list
   (default `22,80,443,445,8080`) for hosts silent on L2+L3.
4. **PTR lookups** — reverse-DNS hostnames.
5. **OUI resolution** — vendor from the bundled 58k-entry IEEE database.

Per host it persists `open_ports` and a best-effort `device_type`.

## Running a scan

- **Quick scan** — the header button (needs *data:write*). Enter a CIDR and
  watch live progress.
- **Scans page** — full history: status (`queued → running →
  completed/failed/cancelled`), progress bar with ETA, per-CIDR rate limit
  (`scan_min_interval_seconds`), cancel button, and a live SSE stream of
  found-host deltas as chunks complete.
- **Scheduled** — `scan_interval_minutes` > 0 runs recurring scans of the
  configured networks from the worker.

## Targeting policy

| Setting | Effect |
|---|---|
| `scan_networks` | CIDRs the scanner may touch (empty = auto-detect local LAN) |
| `scan_exclude_networks` | Never scanned — wins in both directions over any target |
| `scan_only_configured` | Refuse targets outside `scan_networks` |
| `scan_max_hosts` | Refuse targets above this usable-host count |
| `scan_interface` | Pin a specific interface (empty = default route) |

Exclusions are enforced identically by the API route, the scheduler, and the
worker — a job that slips through one layer is stopped by the next.

## Runtime-tunable

Everything above — plus timeouts, concurrency, and TCP ports — is editable
live in **Settings → Scanning**. Changes persist in the `app_settings` table,
fall back to `.env` defaults, and reach the worker within a minute. No
restart needed.

## Reconciliation

What scans do to your data is covered in [Discovery Inbox](/docs/discovery)
and [IP Addresses](/docs/addresses) (status flips, `mac_mismatch`).
