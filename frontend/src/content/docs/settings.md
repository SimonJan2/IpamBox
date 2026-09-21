# Settings

The settings area (`/settings`) is a sidebar of sections — each mirrors a
deployment concern. Sections you lack permission for are hidden.

## The hybrid settings model

Operational settings follow **`.env` default → database override**:

- `.env` provides the deployment default.
- Saving in the UI writes an `app_settings` row that takes effect without a
  restart (scanner changes reach the worker within a minute).
- Each field shows its **source** (db / env / default) and a reset button
  that deletes the override and falls back to the env value.

## The sections

| Section | What it does |
|---|---|
| **General** | System info — app version, alembic revision, detected LAN interface/CIDR, env summary |
| **Features** | Behavior toggles — currently *Site codes follow site changes* |
| **Scanning** | Runtime scanner config: networks, exclusions, schedule, rate limits, timeouts, ports |
| **Backup & Restore** | Download a `.json.gz` snapshot, restore on any install, schedule recurring backups |
| **Account & Security** | Your password and active sessions (revoke others remotely) |
| **Users & Roles** | Admin console — create users, set [roles](/docs/accounts-and-roles) |
| **Appearance** | Theme (IpamBox Tokyo Night is the default; also IpamBox Dark/Light, LocalSend Mint/Dark, NetBox Light/Dark, system), density, list preferences |
| **Color Rules** | Admin-managed conditional row coloring — see [Row Colors](/docs/row-colors) |
| **Data & Maintenance** | Purge scans/changelog/discovery, trigger a backup now, factory reset |

## Backup & Restore notes

- Snapshots cover every data table; **user accounts are excluded by
  default** (admins always are) with an admin opt-in for non-admin accounts.
- Restores are **atomic**, preserve IDs, work on a fresh install, and keep
  you logged in.
- Scheduled snapshots go to a Docker volume (`BACKUP_DIR`), retained per
  `backup_keep`; `backup_interval_minutes=0` means manual only.
- Before a restore you get a **preview**: format version, source app version,
  per-table row counts, and warnings.

## Danger zone

**Data & Maintenance** holds the irreversible tools — factory reset wipes
data tables (users survive), purges truncate history. These are audited and
permission-gated; treat them as such.
