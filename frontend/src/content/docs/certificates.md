# Certificates

Track certificate expiry across your estate so nothing silently lapses.

## Fields

| Field | Notes |
|---|---|
| **Platform** | Where the cert lives (LB, web server, appliance…) |
| **Target** | The protected endpoint |
| **Server name** | Host the cert is installed on |
| **Cert name** | Friendly certificate name |
| **Expires on** | The tracked date — drives the countdown |
| **Serial** | Raw serial string |
| **Notes** | Free text |

## Expiry tracking

- Rows show an **expiry badge** with a live countdown.
- The **dashboard** surfaces certificates expiring within **30 days**
  (`certs_expiring_30d`) so renewals are visible the moment you log in.
- Pair with a [color rule](/docs/row-colors) like *"expires_on within 7 days
  → red"* to make urgent renewals impossible to miss.

## Working with the list

Full list affordances: reorder, pin, tag, row color, inline edits, per-row
history. Certificates are searchable from the command palette and covered by
backup + changelog like every other entity.
