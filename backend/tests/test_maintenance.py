import pytest
from httpx import AsyncClient

from app.models.change_log import ChangeLog
from app.models.ip_address import IPAddress, IPStatus
from app.models.scan_job import ScanJob, ScanStatus
from app.models.site import Site


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

    monkeypatch.setattr("app.api.v1.maintenance.get_arq_pool", _pool)


async def test_purge_scans_keeps_live(client: AsyncClient, session):
    session.add(ScanJob(cidr="10.30.0.0/24", status=ScanStatus.COMPLETED))
    session.add(ScanJob(cidr="10.30.1.0/24", status=ScanStatus.FAILED))
    session.add(ScanJob(cidr="10.30.2.0/24", status=ScanStatus.RUNNING))
    await session.commit()

    r = await client.post("/api/v1/maintenance/purge-scans", json={})
    assert r.status_code == 200
    assert r.json()["deleted"] == 2

    remaining = (await client.get("/api/v1/scans")).json()
    assert len(remaining) == 1 and remaining[0]["status"] == "running"


async def test_purge_changelog(client: AsyncClient, session):
    session.add(Site(name="S1", slug="s1"))
    await session.commit()  # creates a changelog entry via the hook

    r = await client.post("/api/v1/maintenance/purge-changelog", json={})
    assert r.status_code == 200
    assert r.json()["deleted"] >= 1


async def test_clear_discovery(client: AsyncClient, session):
    vrf_id = (await client.get("/api/v1/vrfs")).json()[0]["id"]
    p = (
        await client.post(
            "/api/v1/prefixes", json={"prefix": "10.31.0.0/24", "vrf_id": vrf_id}
        )
    ).json()
    session.add(
        IPAddress(
            address="10.31.0.5",
            address_int=10 * 2**24 + 31 * 2**16 + 5,
            prefix_id=p["id"],
            vrf_id=vrf_id,
            status=IPStatus.DISCOVERED,
        )
    )
    session.add(
        IPAddress(
            address="10.31.0.6",
            address_int=10 * 2**24 + 31 * 2**16 + 6,
            prefix_id=p["id"],
            vrf_id=vrf_id,
            status=IPStatus.ACTIVE,
        )
    )
    await session.commit()

    r = await client.post("/api/v1/maintenance/clear-discovery")
    assert r.status_code == 200
    assert r.json()["deleted"] == 1
    assert (await client.get("/api/v1/discovery")).json()["items"] == []
    rows = (await client.get("/api/v1/addresses")).json()
    assert len(rows) == 1


async def test_factory_reset(client: AsyncClient, session):
    session.add(Site(name="HQ", slug="hq"))
    await session.commit()
    await client.patch("/api/v1/settings", json={"backup_keep": 42})

    r = await client.post("/api/v1/maintenance/reset", json={"confirm": "NOPE"})
    assert r.status_code == 422  # pydantic literal gate

    r = await client.post("/api/v1/maintenance/reset", json={"confirm": "RESET"})
    assert r.status_code == 200

    assert (await client.get("/api/v1/sites")).json()["items"] == []
    # settings reverted to env/default
    body = (await client.get("/api/v1/settings")).json()
    assert body["values"]["backup_keep"] == 14
    assert body["sources"]["backup_keep"] == "default"


async def test_backup_now_enqueues(client: AsyncClient, fake_arq):
    r = await client.post("/api/v1/maintenance/backup-now")
    assert r.status_code == 202
    assert r.json()["queued"] is True
