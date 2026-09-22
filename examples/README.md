# Demo import data — ALL FICTIONAL

Every value in these files is **invented**: site names, IPs, serials, MACs,
circuit IDs, contacts and paths are synthetic and do not describe any real
network. The files mirror the *shape* of a real-world `Network_Address.xlsx`
so the import pipeline can be exercised end-to-end with zero production data.

## Files

| File | Use it with | What it exercises |
|---|---|---|
| `Network_Address_DEMO.xlsx` | Import wizard (`/import`) | The clean flagship, 63 sheets, Hebrew+English. Every family present: sites master, circuits (incl. a retired `ישן` sheet), servers, assets, certificates, services, serial inventory, 54 site sheets. Every site has a name, code and number; every sheet title matches its site; every address is unique. The import preview is **all creates — zero conflicts, skips, errors or warnings**. |
| `Network_Address_DEMO_EN.xlsx` | Import wizard (`/import`) | Compact international version, 44 sheets, English only — and deliberately messier. Carries all the parser edge cases (headerless sheets, blank IP headers, duplicated column blocks, preamble junk, unknown sheets → custom-list suggestions, an empty sheet). Use this one to see how the wizard handles imperfect files. |
| `demo-site-utf8.csv` | Import wizard or `/lists` import | Single site sheet, UTF-8-BOM, Hebrew cell content. |
| `demo-site-cp1255.csv` | Import wizard or `/lists` import | Same sheet encoded as ANSI cp1255 — exercises the decoder fallback. |
| `demo-addresses.csv` | `/addresses` → CSV import | Flat bulk format (`address,prefix,hostname,mac_address,status,role,notes`). Uses the `10.130/131/132.0.0/24` prefixes the demo workbook's master list creates — **import `Network_Address_DEMO.xlsx` first**. |
| `demo-contacts-list.csv` | `/lists` → Import file | Vendor/contact table that becomes a custom list. |
| `demo-vlans.csv` | `/lists` → Import file | The VLAN scheme reference (vid, name, group, scope, description) — becomes a custom list documenting what the workbooks deploy. |
| `demo-servers-list.csv` | `/lists` → Import a file | Servers table mirroring a real servers-sheet export — classifies as `servers` so the wizard also offers "import to IPAM" (rows land on the `Demo Server Farm` site). Exercises every inferred column type: `text` key, `select` (Guest OS / Cert / License), `ip` with multi-value cells, `date` (Cert Expiry — expiry badges), `url` (Mgmt URL), `number` (vCPUs), `owner` (Owner). |
| `generate_demo_data.py` | `python3 generate_demo_data.py` | Regenerates everything deterministically (fixed seed). Requires `openpyxl`. |

## `Network_Address_DEMO.xlsx` — the clean flagship

Designed to import perfectly. A realistic workbook that still shows off the
main features:

- `רשימת אתרים` — sites master, ~55 fictional sites with names, codes,
  types and `10.N.0.0/24` blocks; two `לא פעיל` (inactive) sites
- `INTEGRATION Demo` — a non-10.x site (172.31.x) declared in the master
- `קוי-SDH-IPVPN` + `קוי בזק ישן` — active + retired (`ישן`) circuits sheets
- `שרתים בייצור` — servers with multi-IP cells (incl. 169.254.x link-local)
  and an unnamed owner column
- `תוכנות וחומרות`, `תוקף תעודות` (Excel serial dates), `שירותים`
- `Switches S.N` / `Routers S.N` — serial-number inventory
- 54 site sheets including two large ones (~450 / ~300 rows): a designed
  VLAN scheme (see below), MACs (all three valid formats), `101-200`-style
  ranges in the .201-.250 band, subnet-declaration rows, Hebrew status
  words (`פעיל`, `בהקמה`, `לא פעיל`), `מוגדר תחת אתר` cross-site
  reassignment on a few rows

## VLAN scheme (both workbooks + `demo-vlans.csv`)

Every site sheet maps its subnets onto a consistent enterprise VLAN plan —
subnet ↔ VLAN is stable inside each sheet, and commit auto-creates the VLAN
records (vid + name, scoped per site):

| Group | VLANs |
|---|---|
| Infrastructure | `VLAN5-MGMT`, `VLAN6-OOB` |
| Corporate | `VLAN10-USERS`, `VLAN20-VOICE`, `VLAN30-PRINTERS`, `VLAN40-GUEST`, `VLAN50-WIFI-CORP` |
| Data Center | `VLAN100-SERVERS`, `VLAN110-STORAGE`, `VLAN120-BACKUP` |
| OT & IoT | `VLAN200-IOT`, `VLAN210-CAMERAS`, `VLAN220-ACCESS-CTRL` |
| Security | `VLAN999-QUARANTINE` (documented, not deployed in the sheets) |

Site size decides which VLANs a site runs: small → users/printers/guest,
medium → + voice/wifi/iot/access-ctrl, large → + mgmt/server/storage/
backup/cameras. VLAN *groups* aren't part of the workbook import — create
them on the VLANs page and drag the imported VLANs in; `demo-vlans.csv` is
the matching reference.
- `Quarry Annex` / `Telemetry Hut` — sheets with no master row → sites
  created from the sheet itself (`octet-new`)

## `Network_Address_DEMO_EN.xlsx` — the edge-case workbook

Everything that can go wrong, in one file — each maps to a code path in
`backend/app/services/workbook/`:

- junk/note rows above the real header, and repeated header rows mid-sheet
- `Headerless Demo` — no header at all → positional column mapping
- `Blank Header Demo` — blank IP header cell, recognized via neighbors
- `Dup Blocks Demo` — two duplicated column groups, both parsed
- `Full IP Demo` — full dotted IPs instead of the split base+end layout
- `Orphan Range` — undeclared 172.33.x block → *Imported (unmatched)*
- `Reclaimed Segment` — octet block of an inactive site → retired-anchor rule
- `Beacon Annex` — claims a nameless master row → synthetic site name
- `README — DEMO DATA` + `Vendor Contacts` + `Training Classes` +
  `WAN Circuits`/`Hw-Sw Assets`/`Services` — no English header signature →
  `unknown`, suggested as Custom lists
- `Empty Sheet` — classified `empty`
- `yes`/`no ping` junk markers, continuation rows (empty IP cell), invalid
  MACs → `mac_raw`, unnamed trailing columns → `custom_fields.extra`

## Regenerating

```bash
python3 examples/generate_demo_data.py
```

Deterministic: a fixed RNG seed and fixed workbook timestamps produce
identical output on every run.
