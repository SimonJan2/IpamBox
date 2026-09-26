"""V10.1 device templates: CRUD + RBAC + JSONB layout validation, the
apply merge/replace semantics (cabled ports block replace, never silently
dropped), atomic instantiate through the placement path, and the builtin
seed catalog (idempotent, deletes stick)."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.redis import get_redis
from app.core.security import hash_password
from app.models.device_template import DeviceTemplate
from app.models.user import User, UserRole
from app.services.backup import BACKUP_TABLES
from app.services.device_templates import (
    BUILTIN_TEMPLATES,
    seed_device_templates,
)

PASSWORD = "tmpl-test-pw1"


@pytest.fixture
async def auth_on():
    settings = get_settings()
    settings.ipambox_allow_insecure = False
    cookie_secure = settings.ipambox_cookie_secure
    settings.ipambox_cookie_secure = False
    r = get_redis()
    try:
        yield
    finally:
        settings.ipambox_allow_insecure = True
        settings.ipambox_cookie_secure = cookie_secure
        for pattern in ("ipam:session:*", "ipam:loginfails:*", "ipam:lockout:*"):
            async for key in r.scan_iter(pattern):
                await r.delete(key)
        await r.aclose()


async def _mkuser(session: AsyncSession, username: str, role: UserRole) -> User:
    u = User(username=username, password_hash=hash_password(PASSWORD), role=role)
    session.add(u)
    await session.commit()
    return u


async def _login(client: AsyncClient, username: str) -> None:
    r = await client.post(
        "/api/v1/auth/login", json={"username": username, "password": PASSWORD}
    )
    assert r.status_code == 200, r.text


async def _template(client: AsyncClient, **kw) -> dict:
    body = {
        "name": "tpl",
        "interfaces": [
            {"name": "Gi1/0/1", "kind": "rj45", "speed_mbps": 1000},
            {"name": "Gi1/0/2", "kind": "rj45", "speed_mbps": 1000},
            {"name": "Te1/1/1", "kind": "sfp28", "speed_mbps": 25000},
        ],
        **kw,
    }
    r = await client.post("/api/v1/device-templates", json=body)
    assert r.status_code == 201, r.text
    return r.json()


async def _device(client: AsyncClient, **kw) -> dict:
    r = await client.post("/api/v1/devices", json={"name": "srv", **kw})
    assert r.status_code == 201, r.text
    return r.json()


async def _interfaces(client: AsyncClient, device_id: int) -> list[dict]:
    r = await client.get(f"/api/v1/devices/{device_id}/interfaces")
    assert r.status_code == 200
    return r.json()


# ------------------------------------------------------------------- CRUD


async def test_template_crud_and_search(client: AsyncClient):
    t = await _template(
        client,
        name="Cisco 9300-48",
        manufacturer="Cisco",
        model="C9300-48P",
        device_type="cisco-c9300-48p",
        u_height=1,
        colour="#1e90ff",
        category="network",
        watts=350,
        weight_kg=7.4,
        notes="access switch",
    )
    assert t["source"] == "manual"
    assert len(t["interfaces"]) == 3

    # list + q search across name/manufacturer/model
    for q in ("9300", "cisco", "C9300"):
        r = await client.get("/api/v1/device-templates", params={"q": q})
        assert any(i["id"] == t["id"] for i in r.json()["items"]), q

    r = await client.get(f"/api/v1/device-templates/{t['id']}")
    assert r.json()["model"] == "C9300-48P"

    r = await client.patch(
        f"/api/v1/device-templates/{t['id']}", json={"watts": 400}
    )
    assert r.status_code == 200 and r.json()["watts"] == 400

    r = await client.delete(f"/api/v1/device-templates/{t['id']}")
    assert r.status_code == 204
    assert (
        await client.get(f"/api/v1/device-templates/{t['id']}")
    ).status_code == 404


async def test_layout_validation_rejects_bad_input(client: AsyncClient):
    # bad kind -> 422 before the JSONB blob is stored
    r = await client.post(
        "/api/v1/device-templates",
        json={
            "name": "bad",
            "interfaces": [{"name": "x1", "kind": "usb"}],
        },
    )
    assert r.status_code == 422

    # duplicate names
    r = await client.post(
        "/api/v1/device-templates",
        json={
            "name": "dup",
            "interfaces": [
                {"name": "p1", "kind": "rj45"},
                {"name": "p1", "kind": "rj45"},
            ],
        },
    )
    assert r.status_code == 422

    # pair target not in the layout
    r = await client.post(
        "/api/v1/device-templates",
        json={
            "name": "dangling",
            "interfaces": [{"name": "p1", "kind": "patch", "pair": "b1"}],
        },
    )
    assert r.status_code == 422

    # pair declared on only one side
    r = await client.post(
        "/api/v1/device-templates",
        json={
            "name": "asym",
            "interfaces": [
                {"name": "p1", "kind": "patch", "pair": "b1"},
                {"name": "b1", "kind": "patch"},
            ],
        },
    )
    assert r.status_code == 422

    # power port collides with an interface name (same stamp namespace)
    r = await client.post(
        "/api/v1/device-templates",
        json={
            "name": "clash",
            "interfaces": [{"name": "out1", "kind": "rj45"}],
            "power_ports": [{"name": "out1"}],
        },
    )
    assert r.status_code == 422

    # PATCH re-validates too
    t = await _template(client, name="ok")
    r = await client.patch(
        f"/api/v1/device-templates/{t['id']}",
        json={"interfaces": [{"name": "x", "kind": "nope"}]},
    )
    assert r.status_code == 422


# -------------------------------------------------------------------- RBAC


async def test_template_rbac(
    client: AsyncClient, session: AsyncSession, auth_on
):
    await _mkuser(session, "v", UserRole.VIEWER)
    await _mkuser(session, "c", UserRole.CONTRIBUTOR)
    # fixture row via the session — the API is already gated by auth_on
    session.add(DeviceTemplate(name="seeded", interfaces=[]))
    await session.commit()

    await _login(client, "v")
    # viewer reads
    assert (await client.get("/api/v1/device-templates")).status_code == 200
    tid = (
        await client.get("/api/v1/device-templates")
    ).json()["items"][0]["id"]
    assert (
        await client.get(f"/api/v1/device-templates/{tid}")
    ).status_code == 200
    # viewer cannot write/delete/apply
    assert (
        await client.post("/api/v1/device-templates", json={"name": "x"})
    ).status_code == 403
    assert (
        await client.patch(
            f"/api/v1/device-templates/{tid}", json={"name": "y"}
        )
    ).status_code == 403
    assert (
        await client.delete(f"/api/v1/device-templates/{tid}")
    ).status_code == 403
    assert (
        await client.post(
            "/api/v1/devices/1/apply-template",
            json={"template_id": tid},
        )
    ).status_code == 403
    assert (
        await client.post(
            f"/api/v1/device-templates/{tid}/instantiate",
            json={"name": "d"},
        )
    ).status_code == 403

    await _login(client, "c")
    # contributor writes + applies but cannot delete
    r = await client.post("/api/v1/device-templates", json={"name": "mine"})
    assert r.status_code == 201
    assert (
        await client.delete(f"/api/v1/device-templates/{tid}")
    ).status_code == 403


# ------------------------------------------------------------------- apply


async def test_apply_merge_and_reapply_skips(client: AsyncClient):
    t = await _template(client, name="sw3")
    d = await _device(client)

    r = await client.post(
        f"/api/v1/devices/{d['id']}/apply-template",
        json={"template_id": t["id"]},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["created"] == 3 and body["skipped"] == [] and body["blocked"] == []

    names = [i["name"] for i in await _interfaces(client, d["id"])]
    assert names == ["Gi1/0/1", "Gi1/0/2", "Te1/1/1"]

    # second apply: every name exists -> all skipped, nothing duplicated
    r = await client.post(
        f"/api/v1/devices/{d['id']}/apply-template",
        json={"template_id": t["id"], "mode": "merge"},
    )
    assert r.json()["created"] == 0
    assert sorted(r.json()["skipped"]) == names
    assert len(await _interfaces(client, d["id"])) == 3

    # partial merge: one hand-made port + the template's rest
    d2 = await _device(client, name="half")
    await client.post(
        f"/api/v1/devices/{d2['id']}/interfaces",
        json={"name": "Gi1/0/1", "kind": "rj45"},
    )
    r = await client.post(
        f"/api/v1/devices/{d2['id']}/apply-template",
        json={"template_id": t["id"]},
    )
    assert r.json()["created"] == 2 and r.json()["skipped"] == ["Gi1/0/1"]


async def test_apply_pairs_and_power_ports(client: AsyncClient):
    t = await _template(
        client,
        name="panel",
        interfaces=[
            {"name": "p1", "kind": "patch", "pair": "b1", "position": 0},
            {"name": "b1", "kind": "patch", "pair": "p1", "position": 0},
            {"name": "p2", "kind": "patch", "pair": "b2", "position": 1},
            {"name": "b2", "kind": "patch", "pair": "p2", "position": 1},
        ],
        power_ports=[{"name": "inlet"}],
    )
    d = await _device(client)
    r = await client.post(
        f"/api/v1/devices/{d['id']}/apply-template",
        json={"template_id": t["id"]},
    )
    assert r.json()["created"] == 5
    ifaces = {i["name"]: i for i in await _interfaces(client, d["id"])}
    assert ifaces["inlet"]["kind"] == "power"
    # reciprocal pair links, same convention as generate's pair_prefix
    assert ifaces["p1"]["pair_interface_id"] == ifaces["b1"]["id"]
    assert ifaces["b1"]["pair_interface_id"] == ifaces["p1"]["id"]
    assert ifaces["p2"]["pair_interface_id"] == ifaces["b2"]["id"]


async def test_apply_replace_refuses_cabled_ports(client: AsyncClient):
    t = await _template(client, name="newset")
    a = await _device(client, name="a")
    b = await _device(client, name="b")
    fa = (
        await client.post(
            f"/api/v1/devices/{a['id']}/interfaces",
            json={"name": "eth0", "kind": "rj45"},
        )
    ).json()
    fb = (
        await client.post(
            f"/api/v1/devices/{b['id']}/interfaces",
            json={"name": "swp1", "kind": "rj45"},
        )
    ).json()
    await client.post(
        "/api/v1/cables",
        json={
            "a_interface_id": fa["id"],
            "b_interface_id": fb["id"],
            "kind": "cat6",
        },
    )

    # replace must refuse and name the cabled port — never drop the cable
    r = await client.post(
        f"/api/v1/devices/{a['id']}/apply-template",
        json={"template_id": t["id"], "mode": "replace"},
    )
    assert r.status_code == 409
    assert "eth0" in r.json()["detail"]

    # nothing changed: cable + interface intact
    assert (await _interfaces(client, a["id"]))[0]["name"] == "eth0"

    # a third, genuinely uncabled device: replace wipes + stamps cleanly
    c = await _device(client, name="c")
    r = await client.post(
        f"/api/v1/devices/{c['id']}/apply-template",
        json={"template_id": t["id"], "mode": "replace"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["created"] == 3 and r.json()["skipped"] == []
    assert [i["name"] for i in await _interfaces(client, c["id"])] == [
        "Gi1/0/1",
        "Gi1/0/2",
        "Te1/1/1",
    ]


async def test_apply_unknown_ids_404(client: AsyncClient):
    d = await _device(client)
    t = await _template(client)
    assert (
        await client.post(
            f"/api/v1/devices/{d['id']}/apply-template",
            json={"template_id": 99999},
        )
    ).status_code == 404
    assert (
        await client.post(
            "/api/v1/devices/99999/apply-template",
            json={"template_id": t["id"]},
        )
    ).status_code == 404


# -------------------------------------------------------------- instantiate


async def test_instantiate_device_plus_layout_atomic(client: AsyncClient):
    site = (
        await client.post("/api/v1/sites", json={"name": "HQ"})
    ).json()
    rack = (
        await client.post(
            "/api/v1/racks", json={"name": "R1", "site_id": site["id"], "height_u": 12}
        )
    ).json()
    t = await _template(
        client,
        name="sw48",
        manufacturer="Cisco",
        model="C9300-48P",
        u_height=1,
        colour="#1e90ff",
        watts=350,
        weight_kg=7.4,
    )

    r = await client.post(
        f"/api/v1/device-templates/{t['id']}/instantiate",
        json={
            "name": "sw-core",
            "site_id": site["id"],
            "rack_id": rack["id"],
            "u_position": 10,
        },
    )
    assert r.status_code == 201, r.text
    out = r.json()
    dev = out["device"]
    assert dev["name"] == "sw-core"
    # template defaults landed on the row
    assert dev["manufacturer"] == "Cisco"
    assert dev["u_height"] == 1 and dev["watts"] == 350
    assert dev["rack_id"] == rack["id"] and dev["u_position"] == 10
    assert float(dev["weight_kg"]) == 7.4
    assert out["created"] == 3
    assert len(await _interfaces(client, dev["id"])) == 3

    # changelog covers the created device AND its stamped interfaces
    log = (
        await client.get(
            "/api/v1/changelog",
            params={"object_type": "Device", "object_id": dev["id"]},
        )
    ).json()
    assert any(e["action"] == "create" for e in log["items"])
    ifaces = await _interfaces(client, dev["id"])
    log = (
        await client.get(
            "/api/v1/changelog",
            params={
                "object_type": "DeviceInterface",
                "object_id": ifaces[0]["id"],
            },
        )
    ).json()
    assert any(e["action"] == "create" for e in log["items"])

    # placement conflict: U10 is taken — instantiate refuses atomically,
    # no device row and no interfaces survive
    r = await client.post(
        f"/api/v1/device-templates/{t['id']}/instantiate",
        json={
            "name": "sw-blocked",
            "rack_id": rack["id"],
            "u_position": 10,
        },
    )
    assert r.status_code == 409
    remaining = (await client.get("/api/v1/devices?q=sw-blocked")).json()
    assert remaining["items"] == []


async def test_instantiate_unracked_and_overrides(client: AsyncClient):
    t = await _template(client, name="mini", u_height=2, manufacturer="OEM")
    r = await client.post(
        f"/api/v1/device-templates/{t['id']}/instantiate",
        json={"name": "spare", "manufacturer": "Acme"},
    )
    assert r.status_code == 201
    dev = r.json()["device"]
    assert dev["rack_id"] is None and dev["manufacturer"] == "Acme"
    assert dev["u_height"] == 2  # template value inherited
    assert r.json()["created"] == 3


async def test_builtin_edit_forks_to_manual(client: AsyncClient):
    t = await _template(client, name="stock", source="builtin")
    assert t["source"] == "builtin"
    r = await client.patch(
        f"/api/v1/device-templates/{t['id']}", json={"notes": "tweaked"}
    )
    assert r.status_code == 200
    assert r.json()["source"] == "manual"
    assert r.json()["notes"] == "tweaked"


# -------------------------------------------------------------------- seeds


async def test_builtin_seeds_exist_and_idempotent(
    client: AsyncClient, session: AsyncSession
):
    created = await seed_device_templates(session)
    await session.commit()
    assert created == len(BUILTIN_TEMPLATES)

    items = (
        await client.get("/api/v1/device-templates?limit=200")
    ).json()["items"]
    names = {i["name"] for i in items}
    for spec in BUILTIN_TEMPLATES:
        assert spec["name"] in names
    sw48 = await session.scalar(
        select(DeviceTemplate).where(DeviceTemplate.name == "switch-48")
    )
    assert sw48 is not None and sw48.source == "builtin"
    assert len(sw48.interfaces) == 52  # 48 rj45 + 4 sfp28

    # second run — the whole catalog is seeded, nothing to do
    assert await seed_device_templates(session) == 0
    await session.commit()
    rows = (await session.execute(select(DeviceTemplate.id))).scalars().all()
    assert len(rows) == len(BUILTIN_TEMPLATES)

    # a deleted builtin stays deleted — the tombstone prevents resurrection
    await session.delete(sw48)
    await session.commit()
    assert await seed_device_templates(session) == 0
    await session.commit()
    assert (
        await session.scalar(
            select(DeviceTemplate).where(DeviceTemplate.name == "switch-48")
        )
    ) is None

    # a cleared tombstone (fresh install / restored backup) re-seeds
    # missing names — the name key is the identity
    await session.execute(
        text("DELETE FROM app_settings WHERE key='device_templates.seeded'")
    )
    await session.commit()
    assert await seed_device_templates(session) == 1
    await session.commit()


def test_backup_registry_covers_device_templates():
    assert "device_templates" in {s.name for s in BACKUP_TABLES}
