# Secrets at Rest

Features that talk to other systems need credentials — monitoring SMTP
passwords, SNMP communities, controller API tokens, the OIDC client secret.
IpamBox stores them encrypted under **one master key**, so a database dump
or backup never yields plaintext.

## The master key

Two env vars, file wins — the same convention as `IPAMBOX_PASSWORD_FILE`:

| Var | What |
|---|---|
| `IPAMBOX_SECRET_KEY` | The passphrase, inline in `.env` |
| `IPAMBOX_SECRET_KEY_FILE` | Path to a file holding the passphrase — wins when set |

Set either one in `.env`, restart `api` (and `scanner` — the worker needs it
to decrypt credentials it uses). **Settings → General** shows a read-only
`secret_key_configured` indicator, as does **Settings → Account & Security**
under *Secrets at rest*. There is no UI for entering the key — it comes from
the environment only.

Under the hood the passphrase feeds `HKDF(SHA-256, salt="ipambox-secrets",
info="v1")` to derive a 32-byte data key, and each secret is sealed with
AES-256-GCM under a random nonce — stored as `v1:<base64>` text. Two
identical secrets encrypt to different blobs, and decrypting with the wrong
key fails closed.

## Rotating the key

**Rotating `IPAMBOX_SECRET_KEY` invalidates every stored credential** —
decryption fails and the values must be re-entered. There is no re-wrap
tooling; rotate deliberately, and expect to re-enter secrets afterwards.
The status indicator only tells you a key is *set*, not that it's the right
one — keep the passphrase in your password manager.

## What features store

The convention every credential feature follows:

- A secret field is a `<name>_enc` column holding the `v1:…` blob.
- API responses never carry the blob or the plaintext — they report
  `<name>_set: true/false` and the `updated_at` timestamp.
- Editing a secret writes the encrypted column; a separate *test* action
  proves the stored secret actually works server-side.

Without a configured key, credential endpoints answer a clean
`503 — set IPAMBOX_SECRET_KEY` rather than an error trace.
