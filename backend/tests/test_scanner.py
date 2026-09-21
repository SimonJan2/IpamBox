import ipaddress

import pytest
from sqlalchemy import select

from app.models.scan_job import ScanJob, ScanStatus
from app.worker.reconcile import reconcile
from app.worker.scanner import HostResult, infer_device_type
from app.worker.worker import _infer_scan_vrf, _scan_vrf


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


async def test_scan_rejects_oversized_and_ipv6(client, fake_arq):
    """Enqueue-time bounds: a /8 (~16.7M usable) blows past scan_max_hosts
    (default 4096); IPv6 CIDRs are refused outright — no worker OOM, no
    int4 total_hosts overflow."""
    r = await client.post("/api/v1/scans", json={"cidr": "10.0.0.0/8"})
    assert r.status_code == 422
    assert "scan_max_hosts" in r.json()["detail"]

    r = await client.post("/api/v1/scans", json={"cidr": "fd00::/64"})
    assert r.status_code == 422
    assert "IPv6" in r.text

    # boundary: a /20 (4094 usable) is under the cap and accepted
    r = await client.post("/api/v1/scans", json={"cidr": "10.235.0.0/20"})
    assert r.status_code == 201, r.text


async def test_scan_max_hosts_runtime_editable(client, fake_arq):
    """The cap is a runtime setting: lowering it to 2 rejects a /24."""
    r = await client.patch("/api/v1/settings", json={"scan_max_hosts": 2})
    assert r.status_code == 200, r.text
    r = await client.post("/api/v1/scans", json={"cidr": "10.236.0.0/24"})
    assert r.status_code == 422
    assert "scan_max_hosts" in r.json()["detail"]


async def test_watchdog_reaps_stale_jobs(client, session):
    """A worker killed mid-scan leaves RUNNING rows that would wedge the
    single-live-job rule forever — the watchdog fails them once they pass
    started_at + job_timeout."""
    from datetime import datetime, timezone, timedelta

    from app.worker.worker import WorkerSettings, reap_stale_scan_jobs

    old = datetime.now(timezone.utc) - timedelta(seconds=WorkerSettings.job_timeout + 60)
    stale_run = ScanJob(cidr="10.220.0.0/24", status=ScanStatus.RUNNING,
                        started_at=old)
    stale_q = ScanJob(cidr="10.221.0.0/24", status=ScanStatus.QUEUED,
                      created_at=old)
    fresh = ScanJob(cidr="10.222.0.0/24", status=ScanStatus.RUNNING,
                    started_at=datetime.now(timezone.utc))
    session.add_all([stale_run, stale_q, fresh])
    await session.commit()

    assert await reap_stale_scan_jobs(session) == 2
    await session.refresh(stale_run)
    await session.refresh(stale_q)
    await session.refresh(fresh)
    assert stale_run.status == ScanStatus.FAILED
    assert "job_timeout" in stale_run.error
    assert stale_q.status == ScanStatus.FAILED
    assert fresh.status == ScanStatus.RUNNING


async def _extra_vrf(client, name="HomeLab") -> int:
    r = await client.post("/api/v1/vrfs", json={"name": name})
    assert r.status_code == 201, r.text
    return r.json()["id"]


async def _global_id(client) -> int:
    vrfs = (await client.get("/api/v1/vrfs")).json()
    return next(v["id"] for v in vrfs if v["name"] == "Global")


async def _mk_prefix(client, cidr: str, vrf_id: int) -> dict:
    r = await client.post("/api/v1/prefixes", json={"prefix": cidr, "vrf_id": vrf_id})
    assert r.status_code == 201, r.text
    return r.json()


async def test_scan_create_leaves_vrf_unresolved(client, fake_arq):
    r = await client.post("/api/v1/scans", json={"cidr": "10.245.0.0/24"})
    assert r.status_code == 201, r.text
    assert r.json()["vrf_id"] is None


async def test_infer_scan_vrf_uses_unique_matching_prefix(client, session):
    hl = await _extra_vrf(client)
    await _mk_prefix(client, "10.230.0.0/24", hl)
    assert await _infer_scan_vrf(session, ipaddress.ip_network("10.230.0.0/24")) == hl


async def test_infer_scan_vrf_ambiguous_prefix_falls_back_to_global(client, session):
    g = await _global_id(client)
    hl = await _extra_vrf(client)
    await _mk_prefix(client, "10.231.0.0/24", g)
    await _mk_prefix(client, "10.231.0.0/24", hl)
    assert await _infer_scan_vrf(session, ipaddress.ip_network("10.231.0.0/24")) == g


async def test_infer_scan_vrf_covering_prefix(client, session):
    hl = await _extra_vrf(client)
    await _mk_prefix(client, "10.232.0.0/24", hl)
    assert await _infer_scan_vrf(session, ipaddress.ip_network("10.232.0.9/32")) == hl


async def test_infer_scan_vrf_no_match_uses_global(client, session):
    g = await _global_id(client)
    assert await _infer_scan_vrf(session, ipaddress.ip_network("10.233.0.0/24")) == g


async def test_scan_vrf_resolution_order(client, session):
    g = await _global_id(client)
    hl = await _extra_vrf(client)
    p = await _mk_prefix(client, "10.234.0.0/24", hl)
    net = ipaddress.ip_network("10.234.0.0/24")
    assert await _scan_vrf(session, ScanJob(cidr=str(net), vrf_id=g), net) == g
    assert await _scan_vrf(session, ScanJob(cidr=str(net), prefix_id=p["id"]), net) == hl
    assert await _scan_vrf(session, ScanJob(cidr=str(net)), net) == hl


async def test_scan_cidr_emits_found_deltas(monkeypatch):
    """on_hosts fires once per detection step with that chunk's new IPs —
    ARP batch first, then per-chunk ICMP — so the worker publishes bounded
    `found` deltas on the SSE channel, never one event per IP."""
    from app.worker import scanner

    monkeypatch.setattr(scanner, "detect_interface", lambda explicit="": None)
    monkeypatch.setattr(
        scanner,
        "_arp_scan",
        lambda cidr, dev, timeout: {"10.99.0.2": "AA:BB:CC:DD:EE:02"},
    )

    async def fake_icmp(ips, timeout):
        return {ip for ip in ips if ip.endswith(".5")}

    async def fake_probe(ip, ports, timeout, sem):
        return [80]

    async def fake_ptr(ip, sem):
        return None

    monkeypatch.setattr(scanner, "_icmp_sweep", fake_icmp)
    monkeypatch.setattr(scanner, "_tcp_probe", fake_probe)
    monkeypatch.setattr(scanner, "_ptr_lookup", fake_ptr)

    deltas: list[tuple[list[str], str]] = []

    async def on_hosts(ips, phase):
        deltas.append((ips, phase))

    # /29 -> 6 usable hosts, a single ICMP chunk; TCP fallback skipped
    # because hosts were found.
    hosts = await scanner.scan_cidr("10.99.0.0/29", on_hosts=on_hosts)

    assert [h.ip for h in hosts] == ["10.99.0.2", "10.99.0.5"]
    assert deltas == [(["10.99.0.2"], "arp"), (["10.99.0.5"], "icmp")]


async def test_scan_cidr_tcp_fallback_reports_found(monkeypatch):
    """When L2+L3 find nothing, the TCP fallback publishes its batch too."""
    from app.worker import scanner

    monkeypatch.setattr(scanner, "detect_interface", lambda explicit="": None)
    monkeypatch.setattr(scanner, "_arp_scan", lambda cidr, dev, timeout: {})

    async def fake_icmp(ips, timeout):
        return set()

    async def fake_probe(ip, ports, timeout, sem):
        return [443] if ip.endswith(".5") else []

    async def fake_ptr(ip, sem):
        return None

    monkeypatch.setattr(scanner, "_icmp_sweep", fake_icmp)
    monkeypatch.setattr(scanner, "_tcp_probe", fake_probe)
    monkeypatch.setattr(scanner, "_ptr_lookup", fake_ptr)

    deltas: list[tuple[list[str], str]] = []

    async def on_hosts(ips, phase):
        deltas.append((ips, phase))

    hosts = await scanner.scan_cidr(
        "10.99.1.0/29", tcp_ports=[443], on_hosts=on_hosts
    )

    assert [h.ip for h in hosts] == ["10.99.1.5"]
    assert deltas == [(["10.99.1.5"], "tcp")]


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
    net = ipaddress.ip_network("10.240.0.0/24")
    n, new = await reconcile(session, p["id"], vrf_id, hosts, net)
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


async def test_reconcile_flags_mac_mismatch(client, session):
    """A stored (e.g. imported) MAC that differs from the scan is flagged in
    custom_fields; a matching re-scan clears the flag."""
    vrf_id = (await client.get("/api/v1/vrfs")).json()[0]["id"]
    p = (
        await client.post(
            "/api/v1/prefixes", json={"prefix": "10.241.0.0/24", "vrf_id": vrf_id}
        )
    ).json()
    a = (
        await client.post(
            "/api/v1/addresses",
            json={
                "prefix_id": p["id"],
                "vrf_id": vrf_id,
                "address": "10.241.0.10",
                "status": "active",
                "mac_address": "00:11:22:33:44:55",
            },
        )
    ).json()

    hosts = [HostResult(ip="10.241.0.10", mac="66:77:88:99:AA:BB")]
    net = ipaddress.ip_network("10.241.0.0/24")
    await reconcile(session, p["id"], vrf_id, hosts, net)
    await session.commit()

    row = (
        await client.get("/api/v1/addresses", params={"q": "10.241.0.10"})
    ).json()[0]
    assert row["mac_address"] == "66:77:88:99:AA:BB"
    assert row["custom_fields"]["mac_mismatch"]["was"] == "00:11:22:33:44:55"

    # re-scan with the matching MAC clears the flag
    await reconcile(session, p["id"], vrf_id,
                    [HostResult(ip="10.241.0.10", mac="66:77:88:99:AA:BB")], net)
    await session.commit()
    row = (
        await client.get("/api/v1/addresses", params={"q": "10.241.0.10"})
    ).json()[0]
    assert "mac_mismatch" not in (row["custom_fields"] or {})


async def test_reconcile_offline_sweep_scoped_to_scanned_net(client, session):
    """Scanning a /24 under a documented /16 must not mark the other 255
    subnets' addresses offline — the sweep is bounded to the scanned range."""
    from sqlalchemy import select

    from app.models.change_log import ChangeLog
    from app.models.ip_address import IPAddress

    vrf_id = (await client.get("/api/v1/vrfs")).json()[0]["id"]
    p = (
        await client.post(
            "/api/v1/prefixes", json={"prefix": "10.242.0.0/16", "vrf_id": vrf_id}
        )
    ).json()
    # two ACTIVE rows inside the scanned /24, one ACTIVE row outside it
    addr_ids = {}
    for addr in ("10.242.1.5", "10.242.1.9", "10.242.2.5"):
        r = await client.post(
            "/api/v1/addresses",
            json={
                "prefix_id": p["id"],
                "vrf_id": vrf_id,
                "address": addr,
                "status": "active",
            },
        )
        assert r.status_code == 201, r.text
        addr_ids[addr] = r.json()["id"]
    # clear the create-changelog rows so only reconcile's writes are counted
    await session.execute(
        ChangeLog.__table__.delete().where(ChangeLog.object_type == "IPAddress")
    )
    await session.commit()

    scanned = ipaddress.ip_network("10.242.1.0/24")
    # scan sees .5 alive but not .9; .2.5 is outside the scanned range.
    # (no MAC on the seen host: last_seen is a skipped changelog field, so the
    # only logged update is .9's status flip)
    hosts = [HostResult(ip="10.242.1.5")]
    await reconcile(session, p["id"], vrf_id, hosts, scanned)
    await session.commit()

    rows = (
        await client.get("/api/v1/addresses", params={"prefix_id": p["id"]})
    ).json()
    by_ip = {r["address"]: r["status"] for r in rows}
    assert by_ip["10.242.1.5"] == "active"    # seen -> stays active
    assert by_ip["10.242.1.9"] == "offline"   # in-range unseen -> offline
    assert by_ip["10.242.2.5"] == "active"    # out-of-range -> untouched

    # changelog only records the in-range transition
    logged = (
        await session.execute(
            select(ChangeLog.object_id).where(
                ChangeLog.object_type == "IPAddress",
                ChangeLog.action == "update",
            )
        )
    ).scalars().all()
    assert logged == [addr_ids["10.242.1.9"]]


# --------------------------------------------------------------------------
# cancel/complete race — the worker's stale row copy must never overwrite a
# terminal status written by the API on another connection
# --------------------------------------------------------------------------


class _FakeRedis:
    """In-memory stand-in for the worker's redis client (get/set/publish)."""

    def __init__(self):
        self.store: dict[str, str] = {}

    async def get(self, key):
        return self.store.get(key)

    async def set(self, key, value, ex=None):
        self.store[key] = value

    async def publish(self, *args):
        return 1

    async def aclose(self):
        pass


def _wire_worker(monkeypatch, sf, fake):
    """Point the worker at the test DB (sf) and the fake redis client."""
    from app.worker import worker

    monkeypatch.setattr(worker, "SessionLocal", sf)
    monkeypatch.setattr(worker, "get_redis", lambda: fake)
    return worker


async def _mk_job(session, cidr="10.60.0.0/24"):
    job = ScanJob(cidr=cidr, status=ScanStatus.QUEUED)
    session.add(job)
    await session.commit()
    return job


async def _api_cancel(sf, job_id):
    """Simulate the API-side cancel: terminal status on a fresh connection."""
    from datetime import datetime, timezone

    async with sf() as other:
        j = await other.get(ScanJob, job_id)
        j.status = ScanStatus.CANCELLED
        j.finished_at = datetime.now(timezone.utc)
        await other.commit()


async def test_run_scan_cancel_flag_mid_scan(client, session, sf, monkeypatch):
    """Cancel flag polled between phases -> ScanCancelled -> CANCELLED, and
    no reconcile writes commit."""
    from app.worker import worker
    from app.worker.scanner import ScanCancelled

    fake = _FakeRedis()
    _wire_worker(monkeypatch, sf, fake)
    job = await _mk_job(session)

    async def fake_scan(cidr, *, should_stop=None, **kw):
        assert should_stop is not None
        if await should_stop():
            raise ScanCancelled()
        return [HostResult(ip="10.60.0.9")]

    monkeypatch.setattr(worker, "scan_cidr", fake_scan)
    await fake.set(worker.cancel_key(job.id), "1")

    out = await worker.run_scan({}, job.id)
    assert out == {"cancelled": True}
    await session.refresh(job)
    assert job.status == ScanStatus.CANCELLED
    assert (await client.get("/api/v1/addresses")).json() == []


async def test_run_scan_does_not_clobber_api_cancel(
    client, session, sf, monkeypatch
):
    """Audit race: API writes CANCELLED mid-scan while the redis flag is
    lost (expired/restart). The stale worker copy must not overwrite it with
    COMPLETED, and reconciled rows must roll back."""
    from app.worker import worker

    fake = _FakeRedis()  # flag never set — only the DB row carries the cancel
    _wire_worker(monkeypatch, sf, fake)
    job = await _mk_job(session, "10.61.0.0/24")

    async def fake_scan(cidr, **kw):
        await _api_cancel(sf, job.id)
        return [HostResult(ip="10.61.0.9")]

    monkeypatch.setattr(worker, "scan_cidr", fake_scan)
    out = await worker.run_scan({}, job.id)
    assert out == {"cancelled": True}
    await session.refresh(job)
    assert job.status == ScanStatus.CANCELLED
    assert (await client.get("/api/v1/addresses")).json() == []


async def test_run_scan_cancel_during_reconcile_rolls_back(
    client, session, sf, monkeypatch
):
    """Cancel landing while reconcile writes rows: the flag + row re-check
    right before the completion commit catches it and rolls back."""
    from app.worker import worker

    fake = _FakeRedis()
    _wire_worker(monkeypatch, sf, fake)
    job = await _mk_job(session, "10.62.0.0/24")

    async def fake_scan(cidr, **kw):
        return [HostResult(ip="10.62.0.9")]

    real_reconcile = worker.reconcile

    async def cancelling_reconcile(sess, prefix_id, vrf_id, hosts, net):
        out = await real_reconcile(sess, prefix_id, vrf_id, hosts, net)
        await fake.set(worker.cancel_key(job.id), "1")
        await _api_cancel(sf, job.id)
        return out

    monkeypatch.setattr(worker, "scan_cidr", fake_scan)
    monkeypatch.setattr(worker, "reconcile", cancelling_reconcile)

    out = await worker.run_scan({}, job.id)
    assert out == {"cancelled": True}
    await session.refresh(job)
    assert job.status == ScanStatus.CANCELLED
    # reconcile's insert rode the same transaction and rolled back with it
    assert (await client.get("/api/v1/addresses")).json() == []


async def test_run_scan_terminal_job_not_picked_up(session, sf, monkeypatch):
    """A job already terminal when the worker picks it up is skipped — no
    RUNNING overwrite (duplicate delivery / cancel-before-pickup)."""
    from app.worker import worker

    fake = _FakeRedis()
    _wire_worker(monkeypatch, sf, fake)
    job = ScanJob(cidr="10.63.0.0/24", status=ScanStatus.CANCELLED)
    session.add(job)
    await session.commit()

    called = False

    async def fake_scan(cidr, **kw):
        nonlocal called
        called = True
        return []

    monkeypatch.setattr(worker, "scan_cidr", fake_scan)
    out = await worker.run_scan({}, job.id)
    assert out == {"cancelled": True}
    assert not called


# --------------------------------------------------------------------------
# shared exclusion guard — route, scheduler and worker must all treat
# scan_exclude_networks as an overlap check in EITHER direction
# --------------------------------------------------------------------------


def test_exclusion_hit_both_directions():
    from app.services.scan_policy import exclusion_hit

    net = ipaddress.ip_network("10.70.0.0/24")
    # supernet case: the exclusion is INSIDE the target — the scheduler's
    # old one-direction subnet_of check missed exactly this
    assert exclusion_hit(net, ["10.70.0.64/26"]) == "10.70.0.64/26"
    # subnet case: target inside an excluded block
    assert exclusion_hit(
        ipaddress.ip_network("10.70.0.64/26"), ["10.70.0.0/24"]
    ) == "10.70.0.0/24"
    assert exclusion_hit(net, ["10.70.0.0/24"]) == "10.70.0.0/24"  # equal
    # non-overlap / other family / junk entries are ignored, not fatal
    assert exclusion_hit(net, ["192.168.9.0/24"]) is None
    assert exclusion_hit(net, ["fd00::/64", "garbage"]) is None


async def test_scheduler_and_route_share_exclusion_guard(
    client, session, sf, monkeypatch
):
    """scan_exclude_networks=10.70.0.64/26 inside scan_networks=10.70.0.0/24:
    the route rejects it AND the scheduler skips it — same helper."""
    from app.worker import worker

    r = await client.patch(
        "/api/v1/settings",
        json={
            "scan_networks": ["10.70.0.0/24"],
            "scan_exclude_networks": ["10.70.0.64/26"],
        },
    )
    assert r.status_code == 200, r.text

    # route rejects the supernet target (same helper, raising variant)
    r = await client.post("/api/v1/scans", json={"cidr": "10.70.0.0/24"})
    assert r.status_code == 422, r.text
    assert "excluded" in r.json()["detail"]

    # scheduler logs-and-skips rather than raising
    monkeypatch.setattr(worker, "SessionLocal", sf)
    pool = _FakePool()

    async def _pool():
        return pool

    monkeypatch.setattr(worker, "get_arq_pool", _pool)
    out = await worker.run_scheduled_scans({})
    assert out["enqueued"] == []

    # sanity: remove the exclusion and the same target enqueues
    await client.patch("/api/v1/settings", json={"scan_exclude_networks": []})
    out = await worker.run_scheduled_scans({})
    assert out["enqueued"] == ["10.70.0.0/24"]


async def test_worker_rechecks_exclusion(client, session, sf, monkeypatch):
    """A job enqueued before an exclusion was added fails in run_scan
    instead of scanning (stale-job defence in depth)."""
    from app.worker import worker

    await client.patch(
        "/api/v1/settings",
        json={"scan_exclude_networks": ["10.64.0.0/24"]},
    )
    fake = _FakeRedis()
    _wire_worker(monkeypatch, sf, fake)
    job = await _mk_job(session, "10.64.0.0/24")

    called = False

    async def fake_scan(cidr, **kw):
        nonlocal called
        called = True
        return []

    monkeypatch.setattr(worker, "scan_cidr", fake_scan)
    out = await worker.run_scan({}, job.id)
    assert "excluded" in out["error"]
    assert not called
    await session.refresh(job)
    assert job.status == ScanStatus.FAILED
