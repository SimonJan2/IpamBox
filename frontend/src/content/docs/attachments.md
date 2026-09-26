# Pages & Attachments

Two additions for day-to-day ops: **Pages** — user-authored markdown
documents that live beside this help — and **Attachments** — files
stored directly on devices, racks, sites, IPs, certificates, circuits,
and assets.

## Pages

The built-in help (what you're reading now) is written by developers and
ships with the app. **Pages** are yours: runbooks, procedures, notes —
anything you'd otherwise keep in a wiki or a README on a share.

- Open [Docs](/docs) — the **Pages** section sits below the built-in
  guides, on a dashed-border list so the two never blur together.
- **New page** needs the `data:write` role. The editor is split-screen:
  markdown on the left, live preview on the right.
- The **slug** auto-suggests from the title (`My Runbook` →
  `my-runbook`); the server owns the final slug and appends `-2`, `-3`…
  on collisions.
- Pages render with the same GitHub-flavored markdown as these guides —
  tables, task lists, code blocks, links. Raw HTML is not rendered.
- Hebrew and other RTL text works: titles and paragraphs render with
  `dir="auto"`.
- Deleting a page requires `data:delete` and is permanent — there is no
  trash.

Every create/edit/delete lands in the **Changelog** like any other
object, and pages ride along in **Backup**.

## Attachments

Anything with a detail surface can carry files — a photo of a rack, a
certificate export, a signed circuit contract, a switch config dump.

- On **device** and **rack** detail pages the *Attachments* card sits
  with the other metadata cards. On **sites**, **certificates**,
  **circuits**, and **inventory** click the paperclip in the row's
  actions. On an **IP address** open the drawer — attachments are below
  the monitor section.
- Click **Attach** (or drop a file onto the card) → pick a file →
  optional label → Upload.
- Limits and rules:
  - **6 MB per file**, enforced at upload.
  - Allowed types: images, PDF, plain text, ZIP. The server stores the
    bytes honestly — it doesn't try to preview what it can't render.
  - Filenames may repeat; use the label to distinguish.
  - **No versioning**: to replace a file, delete the attachment and
    upload the new one — the history stays honest.
- Click a chip to download (byte-identical to what was uploaded). Image
  attachments open a lightbox preview instead.
- Uploading needs `data:write`; deleting needs `data:delete`.

Files live as rows in Postgres — no shared filesystem, so a backup
restore brings them back with the rest of the database. Deleting an
entity sweeps its attachments in the same transaction: nothing is left
dangling, and the changelog records the file's name — never its bytes.

> **Note:** this is a trusted-LAN tool. Uploaded files are stored as-is
> and are **not virus-scanned** — attach files you trust, from machines
> you trust.

## What's not here (yet)

- Embedding an attachment *inside* a page's markdown (`![](attachment:…)`
  or data URLs) — the natural follow-on.
- Full-text search across page bodies, non-image file previews,
  attachment versioning, and bulk zip export (backups already cover
  everything).
