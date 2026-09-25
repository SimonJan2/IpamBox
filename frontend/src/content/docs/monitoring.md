# Monitoring

Scans answer "what is out there" in sweeps. Monitoring answers "is it alive
right now": continuous per-target health checks on a dedicated worker lane,
plus **notification channels** that carry state transitions, certificate
warnings, scan failures and MAC mismatches to webhook, SMTP, Discord or
Telegram.

## Targets

A monitor target anchors to **exactly one** object:

- a **device** — the check probes the device's first active IP (falling back
  to its lowest-id address), so renumbering doesn't break the monitor;
- an **IP address** — the check probes that address directly.

Deleting the device or address deletes its monitors — a monitor without a
target has nothing to check. Create targets from **Monitoring**, the
**Monitor** section on a device page, or the IP drawer.

## Check kinds

| Kind | Up means | Fields |
|---|---|---|
| `ping` | ICMP echo reply | — |
| `tcp` | TCP connect succeeds | `port` |
| `http` | GET matches the expectation | `port`, `http_path`, `http_expect` |

HTTP requests go to `http://{ip}:{port}{http_path}` (plain HTTP — HTTPS/TLS
validation is not performed). `http_expect` grammar:

- *empty* — any `2xx`/`3xx` status is up;
- `status:NNN` — the status code must match exactly (`status:401` is a neat
  trick for "service is up but auth-gated");
- anything else — a case-sensitive substring matched against the response
  body (e.g. `"status":"ok"`).

## Hysteresis and states

Every target carries `state` (`unknown` → `up` / `down`) and a
`consecutive_failures` counter:

- A **down** transition fires only when failures reach `down_after`
  (default 2) — one dropped packet won't page anyone.
- A **up** transition fires on the first success while `down`.
- `unknown → up` on first contact is silent; `unknown → down` after
  `down_after` failures does alert.

`interval_seconds` (min 5s) controls check cadence per target. The worker
tick runs every minute, picks targets whose interval has elapsed (capped at
200 per tick), and runs them in **one** batched sweep job — monitoring never
starves scans; they share the `max_jobs` pool.

State columns (`state`, `consecutive_failures`, `last_*`) are written via
bulk updates that bypass the changelog — steady-state probing produces no
audit noise. Only create/edit/delete of the target itself is audited.

## Notification channels

Every state transition fans out to **all enabled channels** (per-target
routing is deliberately out of scope). Delivery failures are recorded in the
notification log — a broken channel never breaks a check.

| Kind | Config (plain `config`) | Secret (`secret_enc`, write-only) |
|---|---|---|
| `webhook` | HTTP method (`POST`/`PUT`) | Webhook URL — tokens in the path are why it's encrypted |
| `discord` | — | Discord webhook URL |
| `telegram` | `chat_id` | Bot token |
| `smtp` | host, port, from, to\[], starttls, username | Password (optional) |

Payload shapes:

- **webhook**: `{"event": "monitor.down", "summary": "…", "payload": {…}, "ts": "…"}`
- **discord**: same event rendered as `content` text
- **telegram**: `sendMessage` to `chat_id`
- **smtp**: plain-text mail with the event as subject

Secrets follow the [secrets contract](secrets) — AES-256-GCM under the
master key (`IPAMBOX_SECRET_KEY`/`_FILE`), write-only in the API (`secret_set`
is all a client sees). Without a configured master key, channel create/test
returns `503`.

The **test** button sends a canned event through the stored credentials and
reports ok/err — it exercises the real secret end-to-end.

## Event sources

One service emits every event:

- `monitor.down` / `monitor.up` — target state transitions only;
- `cert.expiring` — certificates within `cert_warn_days`, once per cert per
  day;
- `scan.failed` — watchdog-reaped and worker-restart-failed scan jobs;
- `mac_mismatch` — a stored-vs-seen MAC disagreement, once per flag.

## Settings

**Settings → Monitoring** (admin): channel CRUD + test, the runtime toggles,
and the notification log viewer. The same toggles also appear under
**Settings → Features → Monitoring**:

- `monitoring_enabled` — master switch; off makes the tick a no-op;
- `monitor_concurrency` — parallel probes inside one sweep (default 64);
- `monitor_http_timeout` — per-request HTTP timeout (default 5s);
- `notify_retention_days` — auto-purge for the notification log (0 = keep).

## Limits (by design)

No SNMP monitors, no dependency/rollup trees ("site down when…"), no
maintenance windows, no alert acknowledgement, no per-target routing, no
uptime-percentage history — the notification log is the audit trail.
