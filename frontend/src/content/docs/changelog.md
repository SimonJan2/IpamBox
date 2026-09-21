# Changelog

Every create, update, and delete is recorded with **actor, timestamp, and
field-level before/after diffs**. Nothing changes silently.

## The global log

`/changelog` lists every change in the system, newest first:

| Column | Meaning |
|---|---|
| **Timestamp** | When it happened |
| **Actor** | Who did it (username, or the worker for scan-driven changes) |
| **Action** | `create` / `update` / `delete` |
| **Object** | Type + a readable repr (`Tag "core"`, `10.0.0.5`…) |
| **Changes** | Per-field before → after |

Bulk operations write one entry per affected row — a 50-address bulk delete
produces 50 traceable entries, not one opaque event.

## Per-object history

The same data scoped to one object:

- **History button** in row actions on entity lists.
- **IP drawer** — an address's own audit trail alongside its fields.

## Coverage

Changelog captures UI edits, API writes, bulk actions, deletes that cascade
to tag assignments, settings overrides, and scanner-driven status changes
(active ↔ offline, discovery confirms).

## Retention

Admins can purge the log from **Settings → Data & Maintenance** — itself a
logged action.
