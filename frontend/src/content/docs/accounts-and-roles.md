# Accounts & Roles

IpamBox uses session-cookie login with role-based access control (RBAC)
enforced on every API route — the UI only *hides* what you can't do; the
backend is the authority.

## First run

On a fresh install the UI redirects to `/setup`, where you create the first
administrator account. Alternatively, pre-provision a password with
`IPAMBOX_PASSWORD` (or `IPAMBOX_PASSWORD_FILE` for Docker secrets) before
first launch.

## Signing in

Log in at `/login`. Sessions are cookie-based and expire after
`IPAMBOX_SESSION_HOURS` (default: 168 — one week). Two brute-force
protections apply:

- **5-strike lockout** per (user, IP) pair after repeated failures.
- A per-IP **credential-stuffing backstop** independent of username.

## The four roles

| Role | Tier | Can do |
|---|---|---|
| **Administrator** | Admin | Everything: users & roles, system settings, backups, all data including deletes |
| **Operator** | Tier-1 | Add, edit and delete data; trigger and download backups. No user management or system settings |
| **Contributor** | Tier-2 | View, add and edit data. Cannot delete, trigger backups, or manage users |
| **Viewer** | Tier-3 | Read-only access to data and reports |

Your tier is shown in the sidebar footer next to your username.

## Managing accounts

Admins use **Settings → Users & Roles** to create accounts, change roles, and
reset passwords. An admin can step their own account down once a second admin
exists — you can never lock the last administrator out of adminship.

## Your own account

**Settings → Account & Security** lets you change your password and review
active sessions (created time, IP, user agent, expiry). From there you can
also sign out every *other* session while keeping the current one.

## Insecure mode

`IPAMBOX_ALLOW_INSECURE=true` disables authentication entirely — every request
is treated as an admin. Only use it behind a trusted reverse proxy that does
its own auth; the server logs a loud warning on startup when it's on.
