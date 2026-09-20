async def _global_vrf_id(client) -> int:
    vrfs = (await client.get("/api/v1/vrfs")).json()
    return next(v["id"] for v in vrfs if v["name"] == "Global")


async def test_overlap_same_vrf_rejected(client):
    vrf_id = await _global_vrf_id(client)
    r = await client.post("/api/v1/prefixes", json={"prefix": "10.50.0.0/24", "vrf_id": vrf_id})
    assert r.status_code == 201, r.text

    r = await client.post("/api/v1/prefixes", json={"prefix": "10.50.0.0/25", "vrf_id": vrf_id})
    assert r.status_code == 409
    r = await client.post("/api/v1/prefixes", json={"prefix": "10.50.0.128/25", "vrf_id": vrf_id})
    assert r.status_code == 409
    r = await client.post("/api/v1/prefixes", json={"prefix": "10.50.0.0/16", "vrf_id": vrf_id})
    assert r.status_code == 409


async def test_same_cidr_allowed_across_vrfs(client):
    vrf_id = await _global_vrf_id(client)
    r = await client.post("/api/v1/vrfs", json={"name": "Tenant-A", "rd": "65000:1"})
    assert r.status_code == 201, r.text
    tenant = r.json()["id"]

    assert (
        await client.post("/api/v1/prefixes", json={"prefix": "192.168.77.0/24", "vrf_id": vrf_id})
    ).status_code == 201
    # identical CIDR in a different VRF is legal
    assert (
        await client.post("/api/v1/prefixes", json={"prefix": "192.168.77.0/24", "vrf_id": tenant})
    ).status_code == 201
    # but still not within the same VRF
    assert (
        await client.post("/api/v1/prefixes", json={"prefix": "192.168.77.0/24", "vrf_id": tenant})
    ).status_code == 409


async def test_prefix_stats_fields(client):
    vrf_id = await _global_vrf_id(client)
    r = await client.post("/api/v1/prefixes", json={"prefix": "172.30.0.0/24", "vrf_id": vrf_id})
    assert r.status_code == 201
    body = r.json()
    assert body["total_ips"] == 256
    assert body["usable_ips"] == 254
    assert body["used_ips"] == 0
    assert body["utilization_pct"] == 0.0


async def test_prefixes_order_by_utilization_and_limit(client):
    vrf_id = await _global_vrf_id(client)
    p1 = (
        await client.post("/api/v1/prefixes", json={"prefix": "10.61.0.0/24", "vrf_id": vrf_id})
    ).json()
    p2 = (
        await client.post("/api/v1/prefixes", json={"prefix": "10.62.0.0/24", "vrf_id": vrf_id})
    ).json()
    p3 = (
        await client.post("/api/v1/prefixes", json={"prefix": "10.63.0.0/24", "vrf_id": vrf_id})
    ).json()
    for i in (5, 6):
        await client.post(
            "/api/v1/addresses",
            json={"address": f"10.62.0.{i}", "prefix_id": p2["id"]},
        )
    await client.post(
        "/api/v1/addresses",
        json={"address": "10.63.0.5", "prefix_id": p3["id"]},
    )

    # utilization desc: p2 (2 used) -> p3 (1 used) -> p1 (empty); limit trims
    rows = (
        await client.get(
            "/api/v1/prefixes", params={"order_by": "utilization", "limit": 2}
        )
    ).json()
    assert [r["id"] for r in rows] == [p2["id"], p3["id"]]

    rows = (
        await client.get("/api/v1/prefixes", params={"order_by": "utilization"})
    ).json()
    assert [r["id"] for r in rows] == [p2["id"], p3["id"], p1["id"]]

    # default ordering is still by network address, and limit applies after it
    rows = (await client.get("/api/v1/prefixes", params={"limit": 1})).json()
    assert [r["id"] for r in rows] == [p1["id"]]

    r = await client.get("/api/v1/prefixes", params={"order_by": "bogus"})
    assert r.status_code == 422


async def test_unknown_vlan_rejected(client):
    vrf_id = await _global_vrf_id(client)
    r = await client.post(
        "/api/v1/prefixes", json={"prefix": "10.60.0.0/24", "vrf_id": vrf_id, "vlan_id": 5000}
    )
    assert r.status_code == 404

    # and an out-of-range VID is rejected when creating the VLAN itself
    r = await client.post("/api/v1/vlans", json={"vid": 5000, "name": "bad"})
    assert r.status_code == 422


async def test_split_endpoint(client):
    vrf_id = await _global_vrf_id(client)
    pid = (
        await client.post("/api/v1/prefixes", json={"prefix": "10.70.0.0/24", "vrf_id": vrf_id})
    ).json()["id"]
    r = await client.get(f"/api/v1/prefixes/{pid}/split", params={"mask": 25})
    assert r.status_code == 200
    assert r.json()["children"] == ["10.70.0.0/25", "10.70.0.128/25"]
    assert r.json()["existing"] == []


async def test_split_cardinality_cap(client):
    """Splits are counted arithmetically before materializing: anything over
    IPAMBOX_MAX_SPLIT_CHILDREN (default 4096) is a 422, not an allocation."""
    vrf_id = await _global_vrf_id(client)
    pid = (
        await client.post(
            "/api/v1/prefixes",
            json={"prefix": "10.71.0.0/16", "vrf_id": vrf_id, "status": "container"},
        )
    ).json()["id"]

    # /16 -> /25 = 2^9 = 512 children: under the cap, succeeds
    r = await client.get(f"/api/v1/prefixes/{pid}/split", params={"mask": 25})
    assert r.status_code == 200
    assert len(r.json()["children"]) == 512

    # /16 -> /28 = 2^12 = 4096 children: exactly at the cap, still succeeds
    r = await client.get(f"/api/v1/prefixes/{pid}/split", params={"mask": 28})
    assert r.status_code == 200
    assert len(r.json()["children"]) == 4096

    # /16 -> /29 = 8192 children: over the cap -> 422 naming the cap
    r = await client.get(f"/api/v1/prefixes/{pid}/split", params={"mask": 29})
    assert r.status_code == 422
    assert "4096" in r.json()["detail"]

    # invalid masks still report the bounds error, not the cap
    r = await client.get(f"/api/v1/prefixes/{pid}/split", params={"mask": 15})
    assert r.status_code == 422
    assert "longer than current" in r.json()["detail"]


async def test_tree_endpoint(client):
    vrf_id = await _global_vrf_id(client)
    site = (await client.post("/api/v1/sites", json={"name": "HQ"})).json()
    await client.patch(f"/api/v1/vrfs/{vrf_id}", json={"site_id": site["id"]})
    vlan = (
        await client.post("/api/v1/vlans", json={"vid": 210, "name": "users"})
    ).json()
    await client.post("/api/v1/prefixes", json={"prefix": "10.80.0.0/16", "vrf_id": vrf_id, "status": "container"})
    await client.post("/api/v1/prefixes", json={"prefix": "10.80.1.0/24", "vrf_id": vrf_id, "status": "container"})
    leaf = (
        await client.post(
            "/api/v1/prefixes",
            json={"prefix": "10.80.1.0/26", "vrf_id": vrf_id, "vlan_id": vlan["id"]},
        )
    ).json()
    for i in (1, 2, 3):
        await client.post(
            "/api/v1/addresses",
            json={"address": f"10.80.1.{i}", "prefix_id": leaf["id"]},
        )

    tree = (await client.get("/api/v1/prefixes/tree")).json()
    hq = next(n for n in tree if n["name"] == "HQ")
    global_vrf = next(v for v in hq["vrfs"] if v["name"] == "Global")
    root = global_vrf["prefixes"][0]
    assert root["prefix"] == "10.80.0.0/16"
    mid = root["children"][0]
    assert mid["prefix"] == "10.80.1.0/24"
    leaf_node = mid["children"][0]
    assert leaf_node["prefix"] == "10.80.1.0/26"

    # rollup fields on the /16 container
    assert root["descendant_count"] == 2
    assert root["agg_used_ips"] == 3
    assert root["allocated_pct"] == round(100.0 * 256 / 65536, 1)
    assert mid["descendant_count"] == 1
    assert mid["allocated_pct"] == 25.0

    # leaf stats + vlan vid (not the DB row id)
    assert leaf_node["vlan_vid"] == 210
    assert leaf_node["vlan_name"] == "users"
    assert leaf_node["used_ips"] == 3
    assert leaf_node["usable_ips"] == 62
    assert leaf_node["utilization_pct"] == round(100.0 * 3 / 62, 1)
    assert leaf_node["children"] == []
