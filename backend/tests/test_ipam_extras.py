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
