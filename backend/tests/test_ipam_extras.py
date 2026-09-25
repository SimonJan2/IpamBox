import ipaddress
from datetime import date, timedelta

from app.worker.reconcile import reconcile
from app.worker.scanner import HostResult


async def _vrf(client) -> int:
    vrfs = (await client.get("/api/v1/vrfs")).json()
    return next(v["id"] for v in vrfs if v["name"] == "Global")


async def _prefix(client, cidr="10.90.0.0/24") -> dict:
    vrf_id = await _vrf(client)
    r = await client.post("/api/v1/prefixes", json={"prefix": cidr, "vrf_id": vrf_id})
    assert r.status_code == 201, r.text
    return r.json()


async def test_tags_crud_and_assignment(client):
    r = await client.post("/api/v1/tags", json={"name": "Production", "color": "#3B82F6"})
    assert r.status_code == 201, r.text
    tag = r.json()
    assert tag["slug"] == "production"

    p = await _prefix(client, "10.91.0.0/24")
    r = await client.post(
        f"/api/v1/tags/{tag['id']}/assignments",
        json={"object_type": "Prefix", "object_id": p["id"]},
    )
    assert r.status_code == 201, r.text

    rows = (
        await client.get("/api/v1/tags/assignments", params={"object_type": "Prefix"})
    ).json()
    assert any(a["object_id"] == p["id"] for a in rows)

    # filtering prefixes by tag
    got = (await client.get("/api/v1/prefixes", params={"tag_id": tag["id"]})).json()
    assert [x["id"] for x in got] == [p["id"]]

    r = await client.delete(f"/api/v1/tags/{tag['id']}/assignments/Prefix/{p['id']}")
    assert r.status_code == 204
    got = (await client.get("/api/v1/prefixes", params={"tag_id": tag["id"]})).json()
    assert got == []


async def test_vlan_group_and_prefix_link(client):
    g = (await client.post("/api/v1/vlan-groups", json={"name": "Access"})).json()
    v = (
        await client.post(
            "/api/v1/vlans", json={"vid": 100, "name": "users", "group_id": g["id"]}
        )
    ).json()
    assert v["vid"] == 100

    # duplicate VID in the same group rejected
    r = await client.post(
        "/api/v1/vlans", json={"vid": 100, "name": "dup", "group_id": g["id"]}
    )
    assert r.status_code == 409

    p = await _prefix(client, "10.92.0.0/24")
    r = await client.patch(f"/api/v1/prefixes/{p['id']}", json={"vlan_id": v["id"]})
    assert r.status_code == 200, r.text
    assert r.json()["vlan"]["vid"] == 100


async def test_ip_ranges_exclude_allocator(client):
    p = await _prefix(client, "10.93.0.0/24")
    r = await client.post(
        "/api/v1/ranges",
        json={
            "prefix_id": p["id"],
            "start_address": "10.93.0.1",
            "end_address": "10.93.0.10",
            "role": "dhcp",
        },
    )
    assert r.status_code == 201, r.text

    # overlapping range rejected
    r = await client.post(
        "/api/v1/ranges",
        json={
            "prefix_id": p["id"],
            "start_address": "10.93.0.5",
            "end_address": "10.93.0.20",
        },
    )
    assert r.status_code == 409

    # allocator skips the DHCP range entirely
    r = await client.post(f"/api/v1/prefixes/{p['id']}/available-ips", json={})
    assert r.status_code == 201
    assert r.json()["address"] == "10.93.0.11"


async def test_address_role_nat_and_bulk(client):
    p = await _prefix(client, "10.94.0.0/24")
    inside = (
        await client.post(
            "/api/v1/addresses",
            json={"address": "10.94.0.5", "prefix_id": p["id"], "status": "active"},
        )
    ).json()
    outside = (
        await client.post(
            "/api/v1/addresses",
            json={
                "address": "10.94.0.6",
                "prefix_id": p["id"],
                "role": "vip",
                "nat_inside_id": inside["id"],
            },
        )
    ).json()
    assert outside["role"] == "vip"
    assert outside["nat_inside_id"] == inside["id"]

    # bulk set_status
    r = await client.post(
        "/api/v1/addresses/bulk",
        json={"ids": [inside["id"], outside["id"]], "action": "set_status", "status": "reserved"},
    )
    assert r.status_code == 200 and r.json()["affected"] == 2
    rows = (await client.get("/api/v1/addresses", params={"prefix_id": p["id"]})).json()
    assert {x["status"] for x in rows} == {"reserved"}

    # bulk delete
    r = await client.post(
        "/api/v1/addresses/bulk",
        json={"ids": [inside["id"], outside["id"]], "action": "delete"},
    )
    assert r.json()["affected"] == 2
    rows = (await client.get("/api/v1/addresses", params={"prefix_id": p["id"]})).json()
    assert rows == []


async def test_bulk_reports_real_counts(client):
    p = await _prefix(client, "10.99.0.0/24")
    ids = []
    for i in (5, 6):
        r = await client.post(
            "/api/v1/addresses",
            json={"address": f"10.99.0.{i}", "prefix_id": p["id"]},
        )
        ids.append(r.json()["id"])
    stale = 999999

    # set_status with a stale id — affected counts rows actually changed
    r = await client.post(
        "/api/v1/addresses/bulk",
        json={
            "ids": [ids[0], ids[1], stale],
            "action": "set_status",
            "status": "reserved",
        },
    )
    body = r.json()
    assert body["affected"] == 2
    assert body["not_found"] == [stale]

    # delete reports the real rowcount, not the requested count
    r = await client.post(
        "/api/v1/addresses/bulk",
        json={"ids": [ids[0], stale], "action": "delete"},
    )
    body = r.json()
    assert body["affected"] == 1
    assert body["not_found"] == [stale]
    rows = (
        await client.get("/api/v1/addresses", params={"prefix_id": p["id"]})
    ).json()
    assert [x["id"] for x in rows] == [ids[1]]

    # tag actions skip ghosts and count only real assignments
    tag = (
        await client.post("/api/v1/tags", json={"name": "t1", "color": "#3B82F6"})
    ).json()
    r = await client.post(
        "/api/v1/addresses/bulk",
        json={"ids": [ids[1], stale], "action": "add_tag", "tag_id": tag["id"]},
    )
    body = r.json()
    assert body["affected"] == 1
    assert body["not_found"] == [stale]
    # re-adding the same tag is a no-op, not another "affected"
    r = await client.post(
        "/api/v1/addresses/bulk",
        json={"ids": [ids[1]], "action": "add_tag", "tag_id": tag["id"]},
    )
    assert r.json()["affected"] == 0
    r = await client.post(
        "/api/v1/addresses/bulk",
        json={"ids": [ids[1]], "action": "remove_tag", "tag_id": tag["id"]},
    )
    assert r.json()["affected"] == 1


async def test_prefix_move_vrf(client):
    g = await _vrf(client)
    v2 = (
        await client.post("/api/v1/vrfs", json={"name": "DMZ"})
    ).json()["id"]

    p = await _prefix(client, "10.96.0.0/24")
    await client.post(
        "/api/v1/addresses",
        json={"address": "10.96.0.5", "prefix_id": p["id"], "status": "active"},
    )

    # move to the DMZ vrf — the address follows
    r = await client.patch(f"/api/v1/prefixes/{p['id']}", json={"vrf_id": v2})
    assert r.status_code == 200, r.text
    assert r.json()["vrf_id"] == v2
    rows = (await client.get("/api/v1/addresses", params={"prefix_id": p["id"]})).json()
    assert rows[0]["vrf_id"] == v2

    # same CIDR can now exist in Global again (no conflict there anymore)
    r = await client.post("/api/v1/prefixes", json={"prefix": "10.96.0.0/24", "vrf_id": g})
    assert r.status_code == 201, r.text

    # moving it back now collides with the copy in Global
    r = await client.patch(f"/api/v1/prefixes/{p['id']}", json={"vrf_id": g})
    assert r.status_code == 409

    # nonexistent VRF
    r = await client.patch(f"/api/v1/prefixes/{p['id']}", json={"vrf_id": 9999})
    assert r.status_code == 404


async def test_container_move_with_children_rejected(client):
    g = await _vrf(client)
    v2 = (await client.post("/api/v1/vrfs", json={"name": "Staging"})).json()["id"]

    r = await client.post(
        "/api/v1/prefixes",
        json={"prefix": "10.97.0.0/16", "vrf_id": g, "status": "container"},
    )
    assert r.status_code == 201, r.text
    parent = r.json()
    child = await _prefix(client, "10.97.1.0/24")

    r = await client.patch(f"/api/v1/prefixes/{parent['id']}", json={"vrf_id": v2})
    assert r.status_code == 409, r.text
    assert "child prefixes" in r.json()["detail"]

    # a childless container moves freely
    r = await client.delete(f"/api/v1/prefixes/{child['id']}")
    assert r.status_code == 204
    r = await client.patch(f"/api/v1/prefixes/{parent['id']}", json={"vrf_id": v2})
    assert r.status_code == 200, r.text


async def test_csv_export_import(client):
    p = await _prefix(client, "10.95.0.0/24")
    await client.post(
        "/api/v1/addresses",
        json={"address": "10.95.0.7", "prefix_id": p["id"], "hostname": "h1"},
    )
    r = await client.get("/api/v1/addresses/export.csv", params={"prefix_id": p["id"]})
    assert r.status_code == 200
    assert "10.95.0.7" in r.text

    csv_body = "address,prefix,hostname,status\n10.95.0.20,10.95.0.0/24,h2,active\n10.95.0.99,10.0.0.0/8,missing,active\n"
    r = await client.post(
        "/api/v1/addresses/import",
        content=csv_body,
        headers={"content-type": "text/csv"},
    )
    assert r.status_code == 200, r.text
    rows = r.json()
    assert rows[0]["ok"] is True
    assert rows[1]["ok"] is False
    # failed rows abort the whole import (all-or-nothing)
    got = (await client.get("/api/v1/addresses", params={"prefix_id": p["id"]})).json()
    assert {x["address"] for x in got} == {"10.95.0.7"}


async def test_addresses_export_respects_filters(client):
    """export.csv takes the same filters as the list endpoint — a filtered
    view downloads only the rows it shows (F8)."""
    p = await _prefix(client, "10.85.0.0/24")
    other = await _prefix(client, "10.86.0.0/24")
    tag = (
        await client.post("/api/v1/tags", json={"name": "core", "color": "#3B82F6"})
    ).json()
    made = {}
    for addr, pid, kw in [
        ("10.85.0.5", p["id"], {"status": "active", "hostname": "core-sw"}),
        ("10.85.0.6", p["id"], {"status": "reserved"}),
        ("10.85.0.7", p["id"], {"status": "discovered"}),
        ("10.86.0.5", other["id"], {"status": "active"}),
    ]:
        r = await client.post(
            "/api/v1/addresses",
            json={"address": addr, "prefix_id": pid, **kw},
        )
        assert r.status_code == 201, r.text
        made[addr] = r.json()
    r = await client.post(
        f"/api/v1/tags/{tag['id']}/assignments",
        json={"object_type": "IPAddress", "object_id": made["10.85.0.5"]["id"]},
    )
    assert r.status_code == 201, r.text

    # no params -> every address; unchanged default behaviour + filename
    r = await client.get("/api/v1/addresses/export.csv")
    assert all(ip in r.text for ip in made)
    assert 'filename="addresses.csv"' in r.headers["content-disposition"]

    # status accepts the panel's CSV multi-select; prefix_id still scopes
    r = await client.get(
        "/api/v1/addresses/export.csv",
        params={"prefix_id": p["id"], "status": "reserved,discovered"},
    )
    assert "10.85.0.6" in r.text and "10.85.0.7" in r.text
    assert "10.85.0.5" not in r.text and "10.86.0.5" not in r.text
    assert 'filename="addresses-filtered.csv"' in r.headers["content-disposition"]

    # tags CSV — the address must carry at least one selected tag
    r = await client.get(
        "/api/v1/addresses/export.csv", params={"tags": str(tag["id"])}
    )
    assert "10.85.0.5" in r.text and "10.85.0.6" not in r.text

    # untagged -> the complement set
    r = await client.get("/api/v1/addresses/export.csv", params={"untagged": 1})
    assert "10.85.0.5" not in r.text and "10.86.0.5" in r.text

    # q shares the list predicate (hostname hit, prefix sibling excluded)
    r = await client.get(
        "/api/v1/addresses/export.csv",
        params={"prefix_id": p["id"], "q": "core-sw"},
    )
    assert "10.85.0.5" in r.text and "10.85.0.6" not in r.text

    # bad values -> 422, not 500
    for params in ({"status": "bogus"}, {"tags": "x"}, {"tags": "1,x"}):
        r = await client.get("/api/v1/addresses/export.csv", params=params)
        assert r.status_code == 422, (params, r.status_code)


async def test_prefixes_export_respects_filters(client):
    """Same filtered-export treatment on the prefixes CSV (F8)."""
    v2 = (await client.post("/api/v1/vrfs", json={"name": "Filtered"})).json()["id"]
    await _prefix(client, "10.87.0.0/24")
    r = await client.post(
        "/api/v1/prefixes", json={"prefix": "10.88.0.0/24", "vrf_id": v2}
    )
    assert r.status_code == 201, r.text

    csv_all = (await client.get("/api/v1/prefixes/export.csv")).text
    assert "10.87.0.0/24" in csv_all and "10.88.0.0/24" in csv_all

    csv_v = (
        await client.get("/api/v1/prefixes/export.csv", params={"vrf_id": v2})
    ).text
    assert "10.88.0.0/24" in csv_v and "10.87.0.0/24" not in csv_v

    csv_q = (
        await client.get("/api/v1/prefixes/export.csv", params={"q": "10.87"})
    ).text
    assert "10.87.0.0/24" in csv_q and "10.88.0.0/24" not in csv_q

    r = await client.get("/api/v1/prefixes/export.csv", params={"status": "bogus"})
    assert r.status_code == 422


async def test_ipv6_prefix_does_not_poison_totals(client):
    """A documented v6 /64's 2^64 host count must not reach dashboard sums
    (~1.8e19 > Number.MAX_SAFE_INTEGER). Capacity fields report null while
    the documented-address count stays real."""
    vrf_id = await _vrf(client)
    await _prefix(client, "10.80.0.0/24")  # one v4 /24: 254 usable
    r = await client.post(
        "/api/v1/prefixes", json={"prefix": "fd00::/64", "vrf_id": vrf_id}
    )
    assert r.status_code == 201, r.text
    v6_id = r.json()["id"]

    stats = (await client.get("/api/v1/dashboard/stats")).json()
    assert stats["ips_total"] == 254  # just the /24 — not 2^64
    assert stats["prefixes_total"] == 2

    # v6 stays listed with null capacity
    rows = (await client.get("/api/v1/prefixes")).json()
    v6 = next(p for p in rows if p["id"] == v6_id)
    assert v6["usable_ips"] is None
    assert v6["total_ips"] is None
    assert v6["utilization_pct"] is None

    # a documented v6 address is counted per-prefix but consumes no v4
    # capacity — ips_used/ips_total share the same IPv4 lens
    await client.post(
        "/api/v1/addresses", json={"address": "fd00::5", "prefix_id": v6_id}
    )
    rows = (await client.get("/api/v1/prefixes")).json()
    v6 = next(p for p in rows if p["id"] == v6_id)
    assert v6["used_ips"] == 1
    stats = (await client.get("/api/v1/dashboard/stats")).json()
    assert stats["ips_total"] == 254 and stats["ips_used"] == 0

    # utilization sort tolerates the null (v6 sinks last)
    rows = (
        await client.get("/api/v1/prefixes", params={"order_by": "utilization"})
    ).json()
    assert rows[-1]["prefix"] == "fd00::/64"


async def test_dashboard_attention_fields(client, session):
    today = date.today()
    for name, days in [("expired-cert", -10), ("soon-cert", 10), ("far-cert", 300)]:
        r = await client.post(
            "/api/v1/certificates",
            json={"cert_name": name, "expires_on": str(today + timedelta(days=days))},
        )
        assert r.status_code == 201, r.text

    vrf_id = await _vrf(client)
    p = await _prefix(client, "10.98.0.0/24")
    await client.post(
        "/api/v1/addresses",
        json={
            "prefix_id": p["id"],
            "address": "10.98.0.10",
            "status": "active",
            "mac_address": "00:11:22:33:44:55",
        },
    )
    await reconcile(
        session, p["id"], vrf_id, [HostResult(ip="10.98.0.10", mac="66:77:88:99:AA:BB")],
        ipaddress.ip_network("10.98.0.0/24"),
    )
    await session.commit()

    stats = (await client.get("/api/v1/dashboard/stats")).json()
    assert stats["certs_expiring_30d"] == 2
    # expired first, far-future cert excluded
    assert [c["cert_name"] for c in stats["certs_expiring"]] == [
        "expired-cert",
        "soon-cert",
    ]
    assert stats["mac_mismatches"] == 1
    item = stats["mac_mismatch_items"][0]
    assert item["address"] == "10.98.0.10"
    assert item["prefix_id"] == p["id"]
    assert item["mac_was"] == "00:11:22:33:44:55"
    assert item["mac_seen"] == "66:77:88:99:AA:BB"


# --- V6.1: pool membership + the /networks wizard ---------------------------

async def _range(client, prefix_id, start, end, role="dhcp", description=None):
    body = {
        "prefix_id": prefix_id,
        "start_address": start,
        "end_address": end,
        "role": role,
    }
    if description:
        body["description"] = description
    r = await client.post("/api/v1/ranges", json=body)
    assert r.status_code == 201, r.text
    return r.json()


async def test_static_inside_dhcp_range_conflicts_and_force_overrides(client):
    p = await _prefix(client, "10.40.0.0/24")
    rng = await _range(
        client, p["id"], "10.40.0.100", "10.40.0.199", description="LAN dhcp"
    )

    r = await client.post(
        "/api/v1/addresses",
        json={"address": "10.40.0.150", "prefix_id": p["id"], "status": "active"},
    )
    assert r.status_code == 409, r.text
    detail = r.json()["detail"]
    assert "10.40.0.100" in detail and "10.40.0.199" in detail

    r = await client.post(
        "/api/v1/addresses?force=1",
        json={"address": "10.40.0.150", "prefix_id": p["id"], "status": "active"},
    )
    assert r.status_code == 201, r.text
    row = r.json()
    assert row["ip_range_id"] == rng["id"]
    assert row["range_role"] == "dhcp"
    assert row["custom_fields"]["pool_override"] is True

    # dhcp-status rows inside a dhcp range are always fine
    r = await client.post(
        "/api/v1/addresses",
        json={"address": "10.40.0.151", "prefix_id": p["id"], "status": "dhcp"},
    )
    assert r.status_code == 201, r.text
    assert r.json()["ip_range_id"] == rng["id"]


async def test_membership_any_role_and_range_delete_nulls_link(client):
    p = await _prefix(client, "10.41.0.0/24")
    rng = await _range(client, p["id"], "10.41.0.200", "10.41.0.210", role="reserved")
    r = await client.post(
        "/api/v1/addresses",
        json={"address": "10.41.0.205", "prefix_id": p["id"], "status": "active"},
    )
    # reserved ranges inform but never block
    assert r.status_code == 201, r.text
    addr = r.json()
    assert addr["ip_range_id"] == rng["id"]

    rows = (
        await client.get("/api/v1/addresses", params={"ip_range_id": rng["id"]})
    ).json()
    assert [a["id"] for a in rows] == [addr["id"]]
    assert rows[0]["range_role"] == "reserved"

    r = await client.delete(f"/api/v1/ranges/{rng['id']}")
    assert r.status_code == 204
    got = (await client.get(f"/api/v1/addresses/{addr['id']}")).json()
    assert got["ip_range_id"] is None
    assert got["range_role"] is None


async def test_patch_status_into_pool_conflicts_unless_forced(client):
    p = await _prefix(client, "10.42.0.0/24")
    rng = await _range(client, p["id"], "10.42.0.100", "10.42.0.199")
    r = await client.post(
        "/api/v1/addresses",
        json={"address": "10.42.0.150", "prefix_id": p["id"], "status": "discovered"},
    )
    assert r.status_code == 201, r.text
    addr = r.json()
    assert addr["ip_range_id"] == rng["id"]  # membership is informational

    r = await client.patch(
        f"/api/v1/addresses/{addr['id']}", json={"status": "active"}
    )
    assert r.status_code == 409, r.text

    r = await client.patch(
        f"/api/v1/addresses/{addr['id']}?force=1", json={"status": "active"}
    )
    assert r.status_code == 200, r.text
    assert r.json()["custom_fields"]["pool_override"] is True

    # acknowledged override stays editable without force
    r = await client.patch(
        f"/api/v1/addresses/{addr['id']}", json={"hostname": "printer"}
    )
    assert r.status_code == 200, r.text


async def test_csv_import_marks_statics_inside_pool(client):
    """A deliberate bulk import documents existing reality — statics inside
    pools land with an auditable pool_override marker rather than sinking
    the whole file."""
    p = await _prefix(client, "10.43.0.0/24")
    await _range(client, p["id"], "10.43.0.100", "10.43.0.199")
    csv_body = (
        "address,prefix,hostname,status\n"
        "10.43.0.50,10.43.0.0/24,ok-host,active\n"
        "10.43.0.150,10.43.0.0/24,pooled,active\n"
    )
    r = await client.post(
        "/api/v1/addresses/import",
        content=csv_body,
        headers={"content-type": "text/csv"},
    )
    assert r.status_code == 200, r.text
    rows = r.json()
    assert rows[0]["ok"] is True
    assert rows[1]["ok"] is True and "override" in rows[1]["detail"]

    got = (
        await client.get("/api/v1/addresses", params={"prefix_id": p["id"]})
    ).json()
    by_addr = {a["address"]: a for a in got}
    assert by_addr["10.43.0.50"]["ip_range_id"] is None
    pooled = by_addr["10.43.0.150"]
    assert pooled["ip_range_id"] is not None
    assert pooled["custom_fields"]["pool_override"] is True


async def test_networks_wizard_happy_path(client):
    vrf_id = await _vrf(client)
    r = await client.post(
        "/api/v1/networks",
        json={
            "vlan": {"vid": 10, "name": "LAN-10"},
            "prefix": {"cidr": "10.10.0.0/24", "vrf_id": vrf_id},
            "gateway": "10.10.0.1",
            "dns_servers": ["10.10.0.2"],
            "dhcp_range": {"start": "10.10.0.100", "end": "10.10.0.199"},
        },
    )
    assert r.status_code == 201, r.text
    out = r.json()
    assert out["vlan_id"] and out["prefix_id"] and out["ip_range_id"]
    assert len(out["address_ids"]) == 2  # gateway + in-prefix resolver

    p = (await client.get(f"/api/v1/prefixes/{out['prefix_id']}")).json()
    assert p["gateway"] == "10.10.0.1"
    assert p["dns_servers"] == ["10.10.0.2"]
    assert p["vlan_id"] == out["vlan_id"]

    addrs = (
        await client.get("/api/v1/addresses", params={"prefix_id": p["id"]})
    ).json()
    gw = next(a for a in addrs if a["address"] == "10.10.0.1")
    assert gw["custom_fields"]["technical"] == "gateway"

    ranges = (
        await client.get("/api/v1/ranges", params={"prefix_id": p["id"]})
    ).json()["items"]
    assert ranges[0]["id"] == out["ip_range_id"]
    assert ranges[0]["role"] == "dhcp"
    assert ranges[0]["start_address"] == "10.10.0.100"
    assert ranges[0]["end_address"] == "10.10.0.199"


async def test_networks_wizard_rolls_back_everything(client):
    vrf_id = await _vrf(client)
    vlans_before = (await client.get("/api/v1/vlans")).json()["total"]

    # bad CIDR -> request rejected before anything is created
    r = await client.post(
        "/api/v1/networks",
        json={
            "vlan": {"vid": 77, "name": "GONE-77"},
            "prefix": {"cidr": "not-a-cidr", "vrf_id": vrf_id},
        },
    )
    assert r.status_code == 422
    assert (await client.get("/api/v1/vlans")).json()["total"] == vlans_before

    # mid-transaction failure (overlapping prefix) -> the new VLAN rolls back too
    await _prefix(client, "10.20.0.0/24")
    r = await client.post(
        "/api/v1/networks",
        json={
            "vlan": {"vid": 78, "name": "GONE-78"},
            "prefix": {"cidr": "10.20.0.0/24", "vrf_id": vrf_id},
            "gateway": "10.20.0.1",
        },
    )
    assert r.status_code == 409, r.text
    assert (await client.get("/api/v1/vlans")).json()["total"] == vlans_before
    vlans = (await client.get("/api/v1/vlans")).json()["items"]
    assert not any(v["vid"] == 78 for v in vlans)


async def test_networks_wizard_reuses_vlan_by_id(client):
    vrf_id = await _vrf(client)
    vlan = (
        await client.post("/api/v1/vlans", json={"vid": 55, "name": "voice"})
    ).json()
    r = await client.post(
        "/api/v1/networks",
        json={
            "vlan_id": vlan["id"],
            "prefix": {"cidr": "10.55.0.0/24", "vrf_id": vrf_id},
        },
    )
    assert r.status_code == 201, r.text
    assert r.json()["vlan_id"] == vlan["id"]
    assert r.json()["ip_range_id"] is None


# --- V6.1: migration 0025 scratch-DB check ---------------------------------

async def test_migration_0025_columns_backfill_rollback():
    """Scratch DB: seed a range + member address at 0024, upgrade to head —
    gateway/dns columns appear and the member's ip_range_id backfills;
    downgrade to 0024 drops them; re-upgrade re-links (idempotent)."""
    import os
    import subprocess

    import asyncpg

    from tests.conftest import _base_dsn, _split_dsn

    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    root, query = _split_dsn(_base_dsn())
    db = "ipam_test_migrate"
    pg_url = f"{root}/{db}{query}"
    env = dict(
        os.environ,
        DATABASE_URL=pg_url.replace("postgresql://", "postgresql+asyncpg://"),
    )

    def alembic(*args: str) -> None:
        subprocess.run(["alembic", *args], check=True, env=env, cwd=backend_dir)

    conn = await asyncpg.connect(f"{root}/postgres{query}")
    try:
        await conn.execute(f'DROP DATABASE IF EXISTS "{db}" WITH (FORCE)')
        await conn.execute(f'CREATE DATABASE "{db}"')
    finally:
        await conn.close()

    try:
        alembic("upgrade", "0024_ip_source")
        conn = await asyncpg.connect(pg_url)
        try:
            cols = {
                r["column_name"]
                for r in await conn.fetch(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'prefixes'"
                )
            }
            assert "gateway" not in cols and "dns_servers" not in cols

            await conn.execute("INSERT INTO vrfs (name) VALUES ('Mig')")
            await conn.execute(
                "INSERT INTO prefixes (prefix, vrf_id) VALUES ('10.81.0.0/24', 1)"
            )
            await conn.execute(
                "INSERT INTO ip_ranges "
                "(prefix_id, vrf_id, start_address, start_int, end_address, "
                " end_int, role) VALUES "
                "(1, 1, '10.81.0.100', 173025380, '10.81.0.199', 173025479, 'dhcp')"
            )
            # one member + one outsider
            await conn.execute(
                "INSERT INTO ip_addresses "
                "(address, address_int, prefix_id, vrf_id) VALUES "
                "('10.81.0.150', 173025430, 1, 1), "
                "('10.81.0.50', 173025330, 1, 1)"
            )
        finally:
            await conn.close()

        alembic("upgrade", "head")
        conn = await asyncpg.connect(pg_url)
        try:
            cols = {
                r["column_name"]
                for r in await conn.fetch(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'prefixes'"
                )
            }
            assert {"gateway", "dns_servers"} <= cols
            rows = {
                r["address"]: r["ip_range_id"]
                for r in await conn.fetch(
                    "SELECT host(address) AS address, ip_range_id FROM ip_addresses"
                )
            }
            assert rows == {"10.81.0.150": 1, "10.81.0.50": None}
        finally:
            await conn.close()

        alembic("downgrade", "0024_ip_source")
        conn = await asyncpg.connect(pg_url)
        try:
            cols = {
                r["column_name"]
                for r in await conn.fetch(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'prefixes'"
                )
            }
            assert "gateway" not in cols
            acols = {
                r["column_name"]
                for r in await conn.fetch(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'ip_addresses'"
                )
            }
            assert "ip_range_id" not in acols
        finally:
            await conn.close()

        # re-upgrade re-links — the backfill UPDATE is idempotent
        alembic("upgrade", "head")
        conn = await asyncpg.connect(pg_url)
        try:
            rows = {
                r["address"]: r["ip_range_id"]
                for r in await conn.fetch(
                    "SELECT host(address) AS address, ip_range_id FROM ip_addresses"
                )
            }
            assert rows == {"10.81.0.150": 1, "10.81.0.50": None}
        finally:
            await conn.close()
    finally:
        conn = await asyncpg.connect(f"{root}/postgres{query}")
        try:
            await conn.execute(f'DROP DATABASE IF EXISTS "{db}" WITH (FORCE)')
        finally:
            await conn.close()
