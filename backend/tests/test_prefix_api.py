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


# --- V6.1: subnet semantics — gateway/DNS technical addresses ---------------

async def _mkprefix(client, cidr="10.10.0.0/24"):
    vrf_id = await _global_vrf_id(client)
    r = await client.post("/api/v1/prefixes", json={"prefix": cidr, "vrf_id": vrf_id})
    assert r.status_code == 201, r.text
    return r.json()


async def _addrs(client, prefix_id):
    rows = (
        await client.get("/api/v1/addresses", params={"prefix_id": prefix_id})
    ).json()
    return {a["address"]: a for a in rows}


async def test_prefix_gateway_creates_reserved_technical_row(client):
    p = await _mkprefix(client)
    r = await client.patch(
        f"/api/v1/prefixes/{p['id']}",
        json={"gateway": "10.10.0.1", "dns_servers": ["10.10.0.2", "8.8.8.8"]},
    )
    assert r.status_code == 200, r.text
    assert r.json()["gateway"] == "10.10.0.1"
    assert r.json()["dns_servers"] == ["10.10.0.2", "8.8.8.8"]

    by_addr = await _addrs(client, p["id"])
    gw = by_addr["10.10.0.1"]
    assert gw["status"] == "reserved"
    assert gw["custom_fields"]["technical"] == "gateway"
    dns = by_addr["10.10.0.2"]
    assert dns["status"] == "reserved"
    assert dns["custom_fields"]["technical"] == "dns"
    # resolvers outside the prefix stay a prefix attribute — no fake member row
    assert "8.8.8.8" not in by_addr


async def test_gateway_clear_removes_only_pristine_row(client):
    p = await _mkprefix(client)
    await client.patch(f"/api/v1/prefixes/{p['id']}", json={"gateway": "10.10.0.1"})
    gw_id = (await _addrs(client, p["id"]))["10.10.0.1"]["id"]

    # a touched technical row is user data — clearing the field must keep it
    r = await client.patch(
        f"/api/v1/addresses/{gw_id}", json={"hostname": "core-gw"}
    )
    assert r.status_code == 200, r.text
    r = await client.patch(f"/api/v1/prefixes/{p['id']}", json={"gateway": None})
    assert r.status_code == 200 and r.json()["gateway"] is None
    assert "10.10.0.1" in await _addrs(client, p["id"])

    # …while a still-pristine row is removed cleanly
    await client.patch(f"/api/v1/prefixes/{p['id']}", json={"gateway": "10.10.0.3"})
    assert "10.10.0.3" in await _addrs(client, p["id"])
    r = await client.patch(f"/api/v1/prefixes/{p['id']}", json={"gateway": None})
    assert r.status_code == 200
    assert "10.10.0.3" not in await _addrs(client, p["id"])


async def test_gateway_never_clobbers_manual_row(client):
    p = await _mkprefix(client)
    r = await client.post(
        "/api/v1/addresses",
        json={
            "address": "10.10.0.1",
            "prefix_id": p["id"],
            "status": "active",
            "hostname": "core-gw",
        },
    )
    assert r.status_code == 201, r.text

    r = await client.patch(f"/api/v1/prefixes/{p['id']}", json={"gateway": "10.10.0.1"})
    assert r.status_code == 200, r.text
    rows = await _addrs(client, p["id"])
    assert rows["10.10.0.1"]["hostname"] == "core-gw"
    assert "technical" not in (rows["10.10.0.1"]["custom_fields"] or {})


async def test_gateway_validation(client):
    p = await _mkprefix(client)
    r = await client.patch(f"/api/v1/prefixes/{p['id']}", json={"gateway": "10.9.9.1"})
    assert r.status_code == 422
    r = await client.patch(f"/api/v1/prefixes/{p['id']}", json={"gateway": "nope"})
    assert r.status_code == 422
    r = await client.patch(
        f"/api/v1/prefixes/{p['id']}",
        json={"dns_servers": ["1.1.1.1", "8.8.8.8", "8.8.4.4", "9.9.9.9", "10.0.0.1"]},
    )
    assert r.status_code == 422
    r = await client.patch(
        f"/api/v1/prefixes/{p['id']}", json={"dns_servers": ["not-an-ip"]}
    )
    assert r.status_code == 422


async def test_next_ip_never_hands_out_gateway(client):
    p = await _mkprefix(client)
    await client.patch(f"/api/v1/prefixes/{p['id']}", json={"gateway": "10.10.0.1"})
    r = await client.post(f"/api/v1/prefixes/{p['id']}/available-ips", json={})
    assert r.status_code == 201, r.text
    assert r.json()["address"] == "10.10.0.2"


async def test_technical_address_rows_are_audited(client):
    p = await _mkprefix(client)
    await client.patch(f"/api/v1/prefixes/{p['id']}", json={"gateway": "10.10.0.1"})
    gw_id = (await _addrs(client, p["id"]))["10.10.0.1"]["id"]
    log = (
        await client.get(
            f"/api/v1/changelog?object_type=IPAddress&object_id={gw_id}"
        )
    ).json()
    actions = {e["action"] for e in log["items"]}
    assert "create" in actions
    # clearing the field deletes the pristine row — also audited
    await client.patch(f"/api/v1/prefixes/{p['id']}", json={"gateway": None})
    log = (
        await client.get(
            f"/api/v1/changelog?object_type=IPAddress&object_id={gw_id}"
        )
    ).json()
    actions = {e["action"] for e in log["items"]}
    assert {"create", "delete"} <= actions
