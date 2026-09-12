import asyncio

import pytest

from app.services.ipam import reserve_next_available


async def _mk_prefix(client, cidr="10.90.0.0/24") -> int:
    vrf_id = next(v["id"] for v in (await client.get("/api/v1/vrfs")).json() if v["name"] == "Global")
    r = await client.post("/api/v1/prefixes", json={"prefix": cidr, "vrf_id": vrf_id})
    assert r.status_code == 201, r.text
    return r.json()["id"]


async def test_sequential_allocation_skips_boundaries(client):
    pid = await _mk_prefix(client)
    for expected in ("10.90.0.1", "10.90.0.2"):
        r = await client.post(f"/api/v1/prefixes/{pid}/available-ips", json={})
        assert r.status_code == 201, r.text
        assert r.json()["address"] == expected
        assert r.json()["status"] == "reserved"

    # stats reflect the two reservations
    stats = (await client.get(f"/api/v1/prefixes/{pid}")).json()
    assert stats["used_ips"] == 2


async def test_allocation_skips_existing(client):
    pid = await _mk_prefix(client, "10.91.0.0/24")
    r = await client.post(
        "/api/v1/addresses", json={"address": "10.91.0.1", "prefix_id": pid}
    )
    assert r.status_code == 201
    r = await client.post(f"/api/v1/prefixes/{pid}/available-ips", json={})
    assert r.json()["address"] == "10.91.0.2"


async def test_exhausted_prefix_conflicts(client):
    pid = await _mk_prefix(client, "10.92.0.0/30")  # usable: .1, .2
    assert (await client.post(f"/api/v1/prefixes/{pid}/available-ips", json={})).status_code == 201
    assert (await client.post(f"/api/v1/prefixes/{pid}/available-ips", json={})).status_code == 201
    r = await client.post(f"/api/v1/prefixes/{pid}/available-ips", json={})
    assert r.status_code == 409


async def test_concurrent_allocation_unique(client, sf):
    pid = await _mk_prefix(client, "10.93.0.0/24")

    async def alloc():
        async with sf() as s:
            row = await reserve_next_available(s, pid)
            await s.commit()
            return int(row.address_int)

    results = await asyncio.gather(*(alloc() for _ in range(8)))
    lo = min(results)
    assert set(results) == set(range(lo, lo + 8))


async def test_address_crud_and_dup_guard(client):
    pid = await _mk_prefix(client, "10.94.0.0/24")
    r = await client.post(
        "/api/v1/addresses",
        json={"address": "10.94.0.10", "prefix_id": pid, "mac_address": "aa-bb-cc-00-11-22"},
    )
    assert r.status_code == 201, r.text
    addr = r.json()
    assert addr["mac_address"] == "AA:BB:CC:00:11:22"
    assert addr["status"] == "active"

    # duplicate in same VRF -> 409
    r = await client.post("/api/v1/addresses", json={"address": "10.94.0.10", "prefix_id": pid})
    assert r.status_code == 409

    # update
    r = await client.patch(f"/api/v1/addresses/{addr['id']}", json={"hostname": "printer.lan"})
    assert r.status_code == 200 and r.json()["hostname"] == "printer.lan"

    # out-of-prefix rejected
    other = (
        await client.post(
            "/api/v1/addresses", json={"address": "10.95.9.9", "prefix_id": pid}
        )
    )
    assert other.status_code == 422
