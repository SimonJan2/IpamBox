from httpx import AsyncClient


async def test_changelog_records_crud(client: AsyncClient):
    r = await client.post("/api/v1/sites", json={"name": "HQ"})
    site = r.json()
    await client.patch(f"/api/v1/sites/{site['id']}", json={"description": "main"})
    await client.delete(f"/api/v1/sites/{site['id']}")

    log = (
        await client.get("/api/v1/changelog?object_type=Site")
    ).json()["items"]
    assert [e["action"] for e in log] == ["delete", "update", "create"]

    create = log[2]
    assert create["object_repr"] == "HQ"
    assert create["actor"] == "system"  # allow_insecure test mode
    assert create["object_id"] == site["id"]

    update = log[1]
    changed = {c["field"]: c for c in update["changes"]}
    assert changed["description"]["before"] is None
    assert changed["description"]["after"] == "main"


async def test_changelog_scoped_filters(client: AsyncClient):
    r = await client.post("/api/v1/sites", json={"name": "Branch"})
    site = r.json()

    log = (
        await client.get(
            f"/api/v1/changelog?object_type=Site&object_id={site['id']}"
        )
    ).json()["items"]
    assert len(log) == 1
    assert log[0]["object_id"] == site["id"]

    # nonexistent object id -> empty
    assert (
        await client.get("/api/v1/changelog?object_type=Site&object_id=99999")
    ).json()["items"] == []


async def test_changelog_captures_ip_status_change(client: AsyncClient):
    vrf_id = next(
        v["id"]
        for v in (await client.get("/api/v1/vrfs")).json()
        if v["name"] == "Global"
    )
    p = (
        await client.post("/api/v1/prefixes", json={"prefix": "10.9.0.0/24", "vrf_id": vrf_id})
    ).json()
    r = await client.post(
        "/api/v1/addresses",
        json={"address": "10.9.0.10", "prefix_id": p["id"], "status": "reserved"},
    )
    addr = r.json()
    await client.patch(f"/api/v1/addresses/{addr['id']}", json={"status": "active"})

    log = (
        await client.get(
            f"/api/v1/changelog?object_type=IPAddress&object_id={addr['id']}"
        )
    ).json()["items"]
    update = next(e for e in log if e["action"] == "update")
    status_change = next(c for c in update["changes"] if c["field"] == "status")
    assert status_change["before"] == "reserved"
    assert status_change["after"] == "active"


async def test_bulk_delete_writes_changelog_entries(client: AsyncClient):
    """/addresses/bulk action=delete used to issue one Core DELETE — invisible
    to the flush-hook audit. Rows now delete through the ORM, one entry each."""
    vrf_id = next(
        v["id"]
        for v in (await client.get("/api/v1/vrfs")).json()
        if v["name"] == "Global"
    )
    p = (
        await client.post(
            "/api/v1/prefixes",
            json={"prefix": "10.20.0.0/24", "vrf_id": vrf_id},
        )
    ).json()
    ids = []
    for i in (5, 6):
        r = await client.post(
            "/api/v1/addresses",
            json={"address": f"10.20.0.{i}", "prefix_id": p["id"]},
        )
        ids.append(r.json()["id"])

    r = await client.post(
        "/api/v1/addresses/bulk", json={"ids": ids, "action": "delete"}
    )
    assert r.status_code == 200 and r.json()["affected"] == 2

    log = (
        await client.get(
            "/api/v1/changelog",
            params={"object_type": "IPAddress", "action": "delete"},
        )
    ).json()["items"]
    assert sorted(e["object_id"] for e in log) == sorted(ids)


async def test_tagged_entity_delete_sweeps_assignments(client: AsyncClient):
    """tag_assignments.object_id has no FK — deleting a tagged object must
    drop its rows in the same transaction, or they dangle and can re-attach
    to an unrelated row when RESTART IDENTITY reuses ids."""
    tag = (
        await client.post("/api/v1/tags", json={"name": "core", "color": "#ff0000"})
    ).json()
    site = (await client.post("/api/v1/sites", json={"name": "Tagged"})).json()
    vrf_id = next(
        v["id"]
        for v in (await client.get("/api/v1/vrfs")).json()
        if v["name"] == "Global"
    )
    prefix = (
        await client.post(
            "/api/v1/prefixes", json={"prefix": "10.21.0.0/24", "vrf_id": vrf_id}
        )
    ).json()
    addr = (
        await client.post(
            "/api/v1/addresses",
            json={"address": "10.21.0.7", "prefix_id": prefix["id"]},
        )
    ).json()
    for otype, oid in (
        ("Site", site["id"]),
        ("VRF", vrf_id),
        ("Prefix", prefix["id"]),
        ("IPAddress", addr["id"]),
    ):
        r = await client.post(
            f"/api/v1/tags/{tag['id']}/assignments",
            json={"object_type": otype, "object_id": oid},
        )
        assert r.status_code == 201, r.text

    # site delete sweeps its own assignment
    r = await client.delete(f"/api/v1/sites/{site['id']}")
    assert r.status_code == 204
    # VRF delete ORM-cascades to the prefix (and its address) — every level's
    # assignments die with it, not just the VRF's own
    r = await client.delete(f"/api/v1/vrfs/{vrf_id}")
    assert r.status_code == 204

    assert (await client.get("/api/v1/tags/assignments")).json() == []

    # cascaded unassigns are audit-logged like explicit deletes
    log = (
        await client.get(
            "/api/v1/changelog",
            params={"object_type": "TagAssignment", "action": "delete"},
        )
    ).json()["items"]
    assert len(log) == 4


async def test_tag_delete_audit_via_orm_cascade(client: AsyncClient):
    """Tag.assignments is already ORM delete-orphan — each removed assignment
    lands in the changelog when its tag is deleted."""
    tag = (
        await client.post("/api/v1/tags", json={"name": "gone", "color": "#ff0000"})
    ).json()
    site = (await client.post("/api/v1/sites", json={"name": "S"})).json()
    await client.post(
        f"/api/v1/tags/{tag['id']}/assignments",
        json={"object_type": "Site", "object_id": site["id"]},
    )
    r = await client.delete(f"/api/v1/tags/{tag['id']}")
    assert r.status_code == 204
    log = (
        await client.get(
            "/api/v1/changelog",
            params={"object_type": "TagAssignment", "action": "delete"},
        )
    ).json()["items"]
    assert len(log) == 1


async def test_settings_reset_to_default_is_audited(client: AsyncClient):
    """PATCH settings with a null value deletes the app_settings row — that
    delete used to run at Core level and skip the changelog."""
    await client.patch("/api/v1/settings", json={"backup_keep": 42})
    await client.patch("/api/v1/settings", json={"backup_keep": None})

    log = (
        await client.get(
            "/api/v1/changelog",
            params={"object_type": "AppSetting", "action": "delete"},
        )
    ).json()["items"]
    assert len(log) == 1
    assert "backup_keep" in str(log[0]["changes"])
