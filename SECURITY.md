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
  cookie is marked `Secure`.
- **Network exposure**: PostgreSQL and Redis publish on `127.0.0.1` only.
  The scanner container runs `network_mode: host` with `NET_ADMIN`/`NET_RAW`
  capabilities — required for ARP discovery; keep the host trusted.
- **Audit trail**: all object writes are recorded in the change log with
  the acting username (or `scanner`/`scheduler` for automated writes).
