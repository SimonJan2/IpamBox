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


async def test_invalid_vlan_rejected(client):
    vrf_id = await _global_vrf_id(client)
    r = await client.post(
        "/api/v1/prefixes", json={"prefix": "10.60.0.0/24", "vrf_id": vrf_id, "vlan_id": 5000}
    )
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


async def test_tree_endpoint(client):
    vrf_id = await _global_vrf_id(client)
    site = (await client.post("/api/v1/sites", json={"name": "HQ"})).json()
    await client.patch(f"/api/v1/vrfs/{vrf_id}", json={"site_id": site["id"]})
    await client.post("/api/v1/prefixes", json={"prefix": "10.80.0.0/16", "vrf_id": vrf_id, "status": "container"})
    await client.post("/api/v1/prefixes", json={"prefix": "10.80.1.0/24", "vrf_id": vrf_id})

    tree = (await client.get("/api/v1/prefixes/tree")).json()
    hq = next(n for n in tree if n["name"] == "HQ")
    global_vrf = next(v for v in hq["vrfs"] if v["name"] == "Global")
    assert global_vrf["prefixes"][0]["prefix"] == "10.80.0.0/16"
    assert global_vrf["prefixes"][0]["children"][0]["prefix"] == "10.80.1.0/24"
