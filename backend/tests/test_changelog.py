from httpx import AsyncClient


async def test_changelog_records_crud(client: AsyncClient):
    r = await client.post("/api/v1/sites", json={"name": "HQ"})
    site = r.json()
    await client.patch(f"/api/v1/sites/{site['id']}", json={"description": "main"})
    await client.delete(f"/api/v1/sites/{site['id']}")

    log = (
        await client.get("/api/v1/changelog?object_type=Site")
    ).json()
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
    ).json()
    assert len(log) == 1
    assert log[0]["object_id"] == site["id"]

    # nonexistent object id -> empty
    assert (
        await client.get("/api/v1/changelog?object_type=Site&object_id=99999")
    ).json() == []


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
    ).json()
    update = next(e for e in log if e["action"] == "update")
    status_change = next(c for c in update["changes"] if c["field"] == "status")
    assert status_change["before"] == "reserved"
    assert status_change["after"] == "active"
