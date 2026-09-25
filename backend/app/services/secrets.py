"""Secrets at rest — the credential contract v7/v8/v12/v14 build on.

A single master key — `IPAMBOX_SECRET_KEY`, or `IPAMBOX_SECRET_KEY_FILE`
(the file wins, same convention as `IPAMBOX_PASSWORD_FILE`) — encrypts
every third-party credential IpamBox stores. The key is a passphrase; the
32-byte data key is derived with `HKDF(SHA-256, salt=b"ipambox-secrets",
info=b"v1")` and values are sealed with AES-256-GCM under a random 12-byte
nonce.

Stored format: `"v1:" + b64(nonce || ciphertext||tag)`. The `v1` prefix and
the HKDF `info` move together, so a future format can version the key
derivation without ambiguity.

CONSUMER CONTRACT — what later features must follow:
- A secret field is a `Text` column named `<field>_enc` holding the `v1:…`
  blob.
- Schemas never expose `<field>_enc`; responses carry `<field>_set: bool`
  plus `updated_at`, never the value.
- The PATCH endpoint accepts the plaintext `<field>` and writes
  `<field>_enc`; a separate `POST …/test` endpoint proves the stored
  secret works server-side.
- Secrets are write-only: no log line, error message, or response body may
  contain a decrypted value. `SecretsNotConfigured` maps to a clean 503
  (see the handler in app.main) — never a traceback.

Rotation: changing `IPAMBOX_SECRET_KEY` invalidates every stored blob —
`decrypt_str` raises `SecretsDecryptError` and the credential must be
re-entered. There is no re-wrap tooling (the same policy RackPad ships).
"""
import base64
import os
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from app.core.config import get_settings

_FORMAT = "v1"
_PREFIX = "v1:"
_SALT = b"ipambox-secrets"
_NONCE_BYTES = 12


class SecretsError(Exception):
    """Base for secrets-service failures — never carries secret material."""


class SecretsNotConfigured(SecretsError):
    """IPAMBOX_SECRET_KEY(_FILE) is not set — encrypt/decrypt can't run."""

    def __init__(self) -> None:
        super().__init__(
            "secrets not configured — set IPAMBOX_SECRET_KEY "
            "(or IPAMBOX_SECRET_KEY_FILE) and restart"
        )


class SecretsDecryptError(SecretsError):
    """Malformed blob or wrong master key — the stored value stays sealed."""


def _master_key() -> str:
    """Resolve the passphrase — the *_FILE path wins over the env var."""
    settings = get_settings()
    if settings.ipambox_secret_key_file:
        try:
            key = Path(settings.ipambox_secret_key_file).read_text().strip()
            if key:
                return key
        except OSError:
            pass
    return settings.ipambox_secret_key


def secrets_configured() -> bool:
    """True when a master key is provisioned (env or file)."""
    return bool(_master_key())


def _data_key() -> bytes:
    key = _master_key()
    if not key:
        raise SecretsNotConfigured()
    return HKDF(
        algorithm=hashes.SHA256(), length=32, salt=_SALT, info=_FORMAT.encode()
    ).derive(key.encode())


def encrypt_str(plain: str) -> str:
    """Seal a string -> "v1:" + b64(nonce || ciphertext+tag).

    Raises SecretsNotConfigured when no master key is set — callers surface
    that as a clean 503/422, not a traceback.
    """
    nonce = os.urandom(_NONCE_BYTES)
    ct = AESGCM(_data_key()).encrypt(nonce, plain.encode(), None)
    return _PREFIX + base64.b64encode(nonce + ct).decode()


def decrypt_str(blob: str) -> str:
    """Unseal a "v1:…" blob.

    Strict prefix check — unknown formats, malformed payloads and wrong
    keys all fail closed (SecretsDecryptError); a missing master key raises
    SecretsNotConfigured. No error carries the value.
    """
    if not blob.startswith(_PREFIX):
        raise SecretsDecryptError("not an encrypted value")
    try:
        raw = base64.b64decode(blob[len(_PREFIX):], validate=True)
    except ValueError as e:
        raise SecretsDecryptError("malformed encrypted value") from e
    if len(raw) <= _NONCE_BYTES:
        raise SecretsDecryptError("malformed encrypted value")
    key = _data_key()
    nonce, ct = raw[:_NONCE_BYTES], raw[_NONCE_BYTES:]
    try:
        return AESGCM(key).decrypt(nonce, ct, None).decode()
    except InvalidTag as e:
        raise SecretsDecryptError("cannot decrypt value") from e
