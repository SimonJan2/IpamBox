# Review Center

One queue for every flag the system raises. IpamBox already detects MAC
mismatches, cable mismatches, duplicate MACs, aging discoveries, offline
hosts, expiring certificates, unresolved switch references, unmanaged
SNMP senders, uncabled and unracked devices — they all land on
**Operations → Review** (`g v`) as live, computed sections.
Nothing here is a stored finding: each section is a query run on read, so
the queue is always current.

## Sections

| Section | What it catches |
|---|---|
| MAC mismatches | A scan saw a different MAC than inventory documented |
| Cable mismatches | SNMP evidence contradicts documented cabling — cabled-but-down, far-end MACs absent, or an LLDP neighbor on an uncabled port |
| Duplicate MACs | One MAC on multiple addresses — a multi-NIC host or bad data |
| Aging discoveries | `discovered` rows older than `discovery_expire_days` |
| Offline hosts | `offline` rows past the `scan_offline_grace_scans` hysteresis |
| Certificates expiring | `expires_on` within `cert_warn_days` (or already past) |
| Unmatched switch refs | Legacy `switch_name`/`switch_port` text with no linked interface |
| Uncabled devices | Devices with interfaces but zero cables |
| Unracked devices | Devices with no rack placement — inventory hygiene |

Counts are honest; each list caps at ~50 rows with a "showing N of M" note.

## Actions are real writes

Every button goes through the normal endpoint, so the
[changelog](/docs/changelog) stays honest:

- **Confirm** on aging discoveries uses the same call as the
  [discovery inbox](/docs/discovery).
- **Delete** calls the entity's own DELETE — it removes the underlying
  address/device/certificate row, not just the review entry.
- **Accept scanned MAC** writes the observed MAC to the address and clears
  the flag. **Keep stored** restores the documented MAC, clears the flag,
  *and* dismisses that was→seen pair — the scanner may re-flag it, but it
  stays out of the queue (the persistent, per-address form of
  `scan_stored_mac_wins`). This is the answer for shared dock/NIC MACs.
- **Run resolver** on the unmatched-switch section replays the legacy
  text matcher and reports matched / ambiguous / unmatched inline.
- **Open trace** on a cable mismatch jumps to that port's L1 trace
  drawer; **Edit cabling** lands on the device's interface panel. Cable
  flags self-heal when the next poll disproves them — dismissal is only
  for findings you accept as reality.

## Dismissal is data, not deletion

**Dismiss** records a `review_dismissals` row keyed on the finding's
fingerprint — the MAC pair, the switch/port text, the duplicate-MAC group.
Dismissed items collapse under each section with who/when/why, and
**Restore** brings them back. Because the fingerprint pins the *content*
of the finding, a scan that re-flags the same thing stays dismissed while
a genuinely new flag resurfaces.

## Tips

- Work top-down — sections are ordered worst-first, and the dashboard
  review card always names the current worst.
- Dismiss with a note when the reason isn't obvious to the next operator.
- The queue pairs with [monitoring](/docs/monitoring): a daily digest of
  open findings is a natural notification channel.
