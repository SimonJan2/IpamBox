# Security Policy

## Supported versions

Security fixes apply to the latest release tag and `main`.

## Reporting a vulnerability

Please do not open public issues for security problems. Report them via
GitHub's private vulnerability reporting ("Security" tab → "Report a
vulnerability") or by contacting the maintainer directly. We aim to
acknowledge reports within a few days.

## Deployment notes

- **Authentication**: the UI enforces a login after first-run setup. Provide
  the password via `IPAMBOX_PASSWORD` or `IPAMBOX_PASSWORD_FILE` (the file
  form keeps the secret out of environment listings). Sessions are signed
  cookies with a configurable lifetime (`IPAMBOX_SESSION_HOURS`).
- **`IPAMBOX_ALLOW_INSECURE=true`** disables all authentication. Only use it
  when IpamBox sits behind a trusted reverse proxy that enforces its own
  access control.
- **`IPAMBOX_COOKIE_SECURE=true`** when serving over HTTPS so the session
  cookie is marked `Secure`. It defaults to `false` so logins work over
  plain HTTP on a LAN (browsers reject `Secure` cookies on non-localhost
  http origins). Be aware: over plain HTTP the session cookie crosses the
  LAN in cleartext — anyone who can sniff the wire can hijack a session.
  Use HTTPS or restrict IpamBox to a trusted network.
- **Network exposure**: `web` (`:3010`) and `api` (`:8001`) are both
  published on all interfaces by default — direct `/docs`, `/metrics` and
  script access from the LAN is intentional. The API enforces auth on
  every route, but it is still a reachable attack surface. Set
  `API_BIND=127.0.0.1` to bind it to loopback when only the web UI should
  be reachable. PostgreSQL and Redis publish on `127.0.0.1` only. The
  scanner container runs `network_mode: host` with `NET_ADMIN`/`NET_RAW`
  capabilities — required for ARP discovery; keep the host trusted.
- **Login lockout / trusted proxies**: failed-login lockouts are keyed on
  `(username, client IP)` plus a per-IP aggregate. The real client IP comes
  from `X-Forwarded-For`, which is honored only when the socket peer is in
  `IPAMBOX_TRUSTED_PROXIES` — by default loopback plus the `web` proxy's
  pinned bridge address (`192.0.2.10` on the `ipam` network, see
  `docker-compose.yml`). The `web` container overwrites XFF with the real
  socket peer, so clients can't spoof it. If you change the pinned address
  or put another proxy in front of `web`, update that list.
- **Backups are credential-bearing when exported with users**: a default
  `GET /api/v1/backup` contains no accounts, but `?include_users=1`
  (admin-only) adds non-admin user rows including bcrypt password hashes.
  Treat such files as secrets: encrypt at rest, restrict access, and
  transmit only over trusted channels. Admin accounts are never exported,
  so a backup can never carry an admin credential.
- **Audit trail**: all object writes are recorded in the change log with
  the acting username (or `scanner`/`scheduler` for automated writes).
