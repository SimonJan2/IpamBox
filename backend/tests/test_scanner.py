import pytest
from sqlalchemy import select

from app.models.scan_job import ScanJob, ScanStatus
from app.worker.reconcile import reconcile
from app.worker.scanner import HostResult, infer_device_type


class _FakeArqJob:
    job_id = "fake-arq-job"


class _FakePool:
    """Stands in for the arq Redis pool — never actually dispatches work."""

    async def enqueue_job(self, *a, **k):
        return _FakeArqJob()

    async def close(self):
        pass


@pytest.fixture
def fake_arq(monkeypatch):
    async def _pool():
        return _FakePool()

    monkeypatch.setattr("app.api.v1.scans.get_arq_pool", _pool)


def test_device_type_inference():
    assert infer_device_type(None, None, [631, 9100]) == "printer"
    assert infer_device_type("Hikvision Digital", None, []) == "camera"
    assert infer_device_type(None, "diskstation.lan", [5000]) == "nas"
    assert infer_device_type("Espressif Inc.", None, [80]) == "iot"
    assert infer_device_type(None, "openwrt.lan", [22, 53, 80]) == "server"  # >=3 ports
    assert infer_device_type(None, None, []) is None


async def test_scan_config_endpoint(client):
    r = await client.get("/api/v1/scans/config")
    assert r.status_code == 200
    body = r.json()
    assert body["only_configured"] is False
    assert body["interval_minutes"] == 0
    assert isinstance(body["tcp_ports"], list)


async def test_cancel_queued_scan(client, session):
    job = ScanJob(cidr="10.250.0.0/24", status=ScanStatus.QUEUED)
    session.add(job)
    await session.commit()

    r = await client.post(f"/api/v1/scans/{job.id}/cancel")
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "cancelled"

    # already terminal -> conflict
    r = await client.post(f"/api/v1/scans/{job.id}/cancel")
    assert r.status_code == 409


async def test_live_scan_blocks_new_scan(client, session):
    job = ScanJob(cidr="10.249.0.0/24", status=ScanStatus.RUNNING)
    session.add(job)
    await session.commit()

    r = await client.post("/api/v1/scans", json={"cidr": "10.248.0.0/24"})
    assert r.status_code == 429


async def test_scan_create_and_rate_limit(client, fake_arq):
    r = await client.post("/api/v1/scans", json={"cidr": "10.247.0.0/24"})
    assert r.status_code == 201, r.text
    # the queued job counts as live -> 429
    r = await client.post("/api/v1/scans", json={"cidr": "10.246.0.0/24"})
    assert r.status_code == 429


async def test_excluded_network_rejected(client, monkeypatch, fake_arq):
    from app.api.v1 import scans as scans_mod

    old = scans_mod.settings.scan_exclude_networks
    scans_mod.settings.scan_exclude_networks = "10.244.0.0/16"
    try:
        r = await client.post("/api/v1/scans", json={"cidr": "10.244.1.0/24"})
        assert r.status_code == 422
        r = await client.post("/api/v1/scans", json={"cidr": "10.243.0.0/24"})
        assert r.status_code == 201
    finally:
        scans_mod.settings.scan_exclude_networks = old


async def test_reconcile_persists_ports_and_type(client, session):
    vrf_id = (await client.get("/api/v1/vrfs")).json()[0]["id"]
    p = (
        await client.post(
            "/api/v1/prefixes", json={"prefix": "10.240.0.0/24", "vrf_id": vrf_id}
        )
    ).json()
    hosts = [
        HostResult(ip="10.240.0.5", mac="AA:BB:CC:DD:EE:01", vendor="Espressif Inc.",
                   hostname="esp-lamp", open_ports=[80], device_type="iot"),
        HostResult(ip="10.240.0.6", mac="AA:BB:CC:DD:EE:02",
                   hostname="printer.lan", open_ports=[631, 9100],
                   device_type="printer"),
    ]
    n, new = await reconcile(session, p["id"], vrf_id, hosts)
    await session.commit()
    assert (n, new) == (2, 2)

    rows = (
        await client.get("/api/v1/addresses", params={"prefix_id": p["id"]})
    ).json()
    by_ip = {r["address"]: r for r in rows}
    assert by_ip["10.240.0.5"]["device_type"] == "iot"
    assert by_ip["10.240.0.5"]["open_ports"] == [80]
    assert by_ip["10.240.0.6"]["device_type"] == "printer"
    assert by_ip["10.240.0.6"]["open_ports"] == [631, 9100]
