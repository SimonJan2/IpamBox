"""V6 secrets at rest — the master-key contract v7/v8/v12/v14 build on.

encrypt/decrypt round-trip, wrong-key/missing-key fail-closed, the v1 blob
format, file-over-env precedence, and the clean-503 API surface. No test may
ever observe a decrypted value in an error or response body.
"""
import base64
import os

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import get_settings
from app.services.secrets import (
    SecretsDecryptError,
    SecretsNotConfigured,
    decrypt_str,
    encrypt_str,
    secrets_configured,
)


@pytest.fixture
def key(monkeypatch):
    """Provision a master key on the cached settings object."""
    s = get_settings()
    monkeypatch.setattr(s, "ipambox_secret_key", "test-master-key")
    monkeypatch.setattr(s, "ipambox_secret_key_file", "")
    return s


@pytest.fixture
def no_key(monkeypatch):
    s = get_settings()
    monkeypatch.setattr(s, "ipambox_secret_key", "")
    monkeypatch.setattr(s, "ipambox_secret_key_file", "")
    return s


def test_round_trip(key):
    blob = encrypt_str("smtp-pa55w0rd-שלום")
    assert decrypt_str(blob) == "smtp-pa55w0rd-שלום"


def test_blob_format(key):
    blob = encrypt_str("x")
    assert blob.startswith("v1:")
    raw = base64.b64decode(blob[3:], validate=True)
    # 12-byte nonce + ciphertext + 16-byte GCM tag
    assert len(raw) > 12 + 16


def test_random_nonce(key):
    # Two encryptions of the same plaintext must differ (random nonce).
    assert encrypt_str("same plaintext") != encrypt_str("same plaintext")


def test_wrong_key_fails_closed(key, monkeypatch):
    blob = encrypt_str("controller-token")
    monkeypatch.setattr(key, "ipambox_secret_key", "a-different-key")
    with pytest.raises(SecretsDecryptError):
        decrypt_str(blob)


def test_missing_key_raises(no_key):
    assert secrets_configured() is False
    with pytest.raises(SecretsNotConfigured):
        encrypt_str("x")
    # a well-formed blob reaches the key-derivation step → NotConfigured
    blob = "v1:" + base64.b64encode(os.urandom(12) + b"x" * 16).decode()
    with pytest.raises(SecretsNotConfigured):
        decrypt_str(blob)


@pytest.mark.parametrize(
    "blob", ["", "plaintext", "v0:AAAA", "v2:AAAA", "v1:!!!", "v1:", "v1:AAAA"]
)
def test_malformed_blobs_fail_closed(key, blob):
    # strict "v1:" prefix check; "v1:AAAA" decodes to 3 bytes < a nonce.
    with pytest.raises(SecretsDecryptError):
        decrypt_str(blob)


def test_file_wins_over_env(no_key, tmp_path, monkeypatch):
    f = tmp_path / "secret_key"
    f.write_text("  file-key\n")
    s = get_settings()
    monkeypatch.setattr(s, "ipambox_secret_key", "env-key")
    monkeypatch.setattr(s, "ipambox_secret_key_file", str(f))
    blob = encrypt_str("tok")
    assert decrypt_str(blob) == "tok"
    # the env value alone can't open what the file key sealed
    monkeypatch.setattr(s, "ipambox_secret_key_file", "")
    with pytest.raises(SecretsDecryptError):
        decrypt_str(blob)


def test_secrets_configured(no_key, tmp_path, monkeypatch):
    assert secrets_configured() is False
    monkeypatch.setattr(no_key, "ipambox_secret_key", "k")
    assert secrets_configured() is True
    # file takes precedence for the check too
    monkeypatch.setattr(no_key, "ipambox_secret_key", "")
    f = tmp_path / "k"
    f.write_text("k")
    monkeypatch.setattr(no_key, "ipambox_secret_key_file", str(f))
    assert secrets_configured() is True


async def test_api_missing_key_is_clean_503(no_key):
    """SecretsNotConfigured surfaces as 503 + guidance — never a traceback,
    and never any secret material in the body."""
    from app.main import app

    @app.get("/__test_secrets_boom")
    def _boom():
        encrypt_str("hunter2")

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        r = await c.get("/__test_secrets_boom")
    assert r.status_code == 503
    body = r.json()["detail"]
    assert "IPAMBOX_SECRET_KEY" in body
    assert "hunter2" not in r.text
    assert "Traceback" not in r.text


async def test_settings_exposes_configured_flag(client, no_key):
    r = await client.get("/api/v1/settings")
    assert r.status_code == 200
    env = r.json()["env"]
    assert env["secret_key_configured"] is False
    # the key itself is never serialized
    assert "secret_key" not in env


async def test_settings_flag_flips_when_key_set(client, key):
    r = await client.get("/api/v1/settings")
    assert r.status_code == 200
    assert r.json()["env"]["secret_key_configured"] is True
