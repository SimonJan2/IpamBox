# Discovery Inbox

The reconciliation queue. When a [scan](/docs/scans) finds a host that isn't
documented — or contradicts what is — it lands here instead of silently
mutating your data.

## What lands in the inbox

- **New hosts** — seen live, matching no documented address. They arrive as
  `discovered` addresses with whatever the scan learned (MAC, vendor, open
  ports, device type, PTR name).
- **MAC mismatches** — a scan saw a different MAC than the stored one. The
  live value wins, but the address is flagged `mac_mismatch` and counted on
  the dashboard until you review it.

## Confirming

**Confirm** promotes a discovered host into your documentation — it becomes a
normal `active` address you can edit like any other. Confirm selectively, or
bulk-confirm a whole inbox page at once.

**Delete** rejects the finding — the row goes away and the changelog records
the decision.

## The other direction: going quiet

Reconciliation works both ways. A documented `active` host that stops
answering scans flips to `offline`; when it comes back it returns to
`active` automatically — no inbox round-trip needed. Only genuinely *new*
things require a human decision.

## Workflow tips

- Run a scan, then work the inbox top-down: bulk-confirm the expected,
  investigate the weird.
- A MAC mismatch usually means a NIC swap or a spoof — check `mac_was` vs
  `mac_seen` on the dashboard's mismatch list.
- Purge stale discoveries in bulk from **Settings → Data & Maintenance**.
