import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models.app_setting import AppSetting
from app.models.change_log import ChangeLog


class _FakeArqJob:
    job_id = "fake-arq-job"


class _FakePool:
    async def enqueue_job(self, *a, **k):
        return _FakeArqJob()

    async def close(self):
        pass


@pytest.fixture
def fake_arq(monkeypatch):
    async def _pool():
        return _FakePool()

    monkeypatch.setattr("app.api.v1.scans.get_arq_pool", _pool)


async def test_settings_get(client: AsyncClient):
    r = await client.get("/api/v1/settings")
    assert r.status_code == 200
    body = r.json()
    assert body["values"]["scan_interval_minutes"] == 0
    assert body["sources"]["scan_interval_minutes"] == "default"
    assert body["values"]["backup_keep"] == 14
    # secrets are masked in the env display
    assert "•••" in body["env"]["database_url"]
    assert body["system"]["app_version"]
    assert "lan" in body["system"]


async def test_settings_patch_and_reset(client: AsyncClient):
    r = await client.patch(
        "/api/v1/settings", json={"scan_interval_minutes": 60}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["values"]["scan_interval_minutes"] == 60
    assert body["sources"]["scan_interval_minutes"] == "db"

    # the effective value flows into the scans config view
    cfg = (await client.get("/api/v1/scans/config")).json()
    assert cfg["interval_minutes"] == 60

    # null resets to env/default
    r = await client.patch(
        "/api/v1/settings", json={"scan_interval_minutes": None}
    )
    assert r.json()["values"]["scan_interval_minutes"] == 0
    assert r.json()["sources"]["scan_interval_minutes"] == "default"


async def test_settings_validation(client: AsyncClient):
    r = await client.patch(
        "/api/v1/settings", json={"scan_networks": ["not-a-cidr"]}
    )
    assert r.status_code == 422
    assert "scan_networks" in r.json()["detail"]

    r = await client.patch("/api/v1/settings", json={"bogus_key": 1})
    assert r.status_code == 422

    r = await client.patch("/api/v1/settings", json={"backup_keep": 0})
    assert r.status_code == 422

    r = await client.patch(
        "/api/v1/settings", json={"scan_tcp_ports": [22, 70000]}
    )
    assert r.status_code == 422

    # nothing was persisted from the failed patches
    assert (await client.get("/api/v1/settings")).json()["values"][
        "scan_networks"
    ] == []


async def test_scan_guards_use_db_settings(client: AsyncClient, fake_arq):
    r = await client.patch(
        "/api/v1/settings",
        json={
            "scan_networks": ["10.90.0.0/16"],
            "scan_only_configured": True,
            "scan_exclude_networks": ["10.90.99.0/24"],
        },
    )
    assert r.status_code == 200

    # outside configured list -> refused
    r = await client.post("/api/v1/scans", json={"cidr": "10.91.0.0/24"})
    assert r.status_code == 422
    # inside but excluded -> refused
    r = await client.post("/api/v1/scans", json={"cidr": "10.90.99.0/25"})
    assert r.status_code == 422
    # inside -> allowed
    r = await client.post("/api/v1/scans", json={"cidr": "10.90.1.0/24"})
    assert r.status_code == 201, r.text


async def test_settings_changes_audited(client: AsyncClient, session):
    await client.patch("/api/v1/settings", json={"backup_keep": 7})
    rows = (
        (
            await session.execute(
                select(ChangeLog).where(ChangeLog.object_type == "AppSetting")
            )
        )
        .scalars()
        .all()
    )
    assert any(r.object_repr == "backup_keep" for r in rows)


async def test_backup_files_report_effective_schedule(client: AsyncClient):
    await client.patch(
        "/api/v1/settings",
        json={"backup_interval_minutes": 120, "backup_keep": 5},
    )
    body = (await client.get("/api/v1/backup/files")).json()
    assert body["interval_minutes"] == 120
    assert body["keep"] == 5


async def test_internal_keys_hidden(client: AsyncClient, session):
    session.add(AppSetting(key="_last_scan_at", value="2026-01-01T00:00:00"))
    await session.commit()
    body = (await client.get("/api/v1/settings")).json()
    assert "_last_scan_at" not in body["values"]
    # and internal keys are not settable via PATCH
    r = await client.patch("/api/v1/settings", json={"_last_scan_at": "x"})
    assert r.status_code == 422
