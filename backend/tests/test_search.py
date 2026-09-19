"""Global /api/v1/search endpoint (UX-3)."""

import pytest
from httpx import AsyncClient

from app.core.config import get_settings
from app.core.redis import get_redis


@pytest.fixture
async def auth_on():
    settings = get_settings()
    settings.ipambox_allow_insecure = False
    r = get_redis()
    try:
        yield
    finally:
        settings.ipambox_allow_insecure = True
        for pattern in ("ipam:session:*", "ipam:loginfails:*", "ipam:lockout:*"):
            async for key in r.scan_iter(pattern):
                await r.delete(key)
        await r.aclose()


async def _seed(client: AsyncClient) -> dict:
    """Site + VRF + prefix + address + one of each workbook entity."""
    site = (
        await client.post("/api/v1/sites", json={"name": "אתרים מרכזי", "code": "ATRM"})
    ).json()
    vrf = (
        await client.post(
            "/api/v1/vrfs", json={"name": "prod", "site_id": site["id"]}
        )
    ).json()
    prefix = (
        await client.post(
            "/api/v1/prefixes",
            json={"prefix": "10.20.0.0/16", "vrf_id": vrf["id"], "site_id": site["id"]},
        )
    ).json()
    addr = (
        await client.post(
            "/api/v1/addresses",
            json={
                "address": "10.20.3.44",
                "prefix_id": prefix["id"],
                "hostname": "sw-core-01",
            },
        )
    ).json()
    await client.post(
        "/api/v1/circuits",
        json={"site_name": "אתרים מרכזי", "bezeq_circuit_id": "828328469"},
    )
    await client.post(
        "/api/v1/certificates",
        json={"cert_name": "*.atrm.example.com", "server_name": "vs-atrm"},
    )
    await client.post(
        "/api/v1/assets",
        json={"kind": "hardware", "vendor": "Cisco", "serial_number": "SN-ATRM-1"},
    )
    await client.post(
        "/api/v1/services", json={"name": "ATRM DNS", "site_code": "ATRM"}
    )
    await client.post("/api/v1/vlans", json={"vid": 210, "name": "atrm-users"})
    return {"site": site, "vrf": vrf, "prefix": prefix, "addr": addr}


async def test_search_requires_auth(client: AsyncClient, auth_on):
    r = await client.get("/api/v1/search", params={"q": "x"})
    assert r.status_code == 401


async def test_search_empty_query(client: AsyncClient):
    r = await client.get("/api/v1/search")
    assert r.status_code == 200
    body = r.json()
    assert all(body[k] == [] for k in (
        "addresses", "prefixes", "sites", "vrfs", "vlans",
        "circuits", "certificates", "assets", "services",
    ))
    assert body["jump"] is None


async def test_search_grouped_results(client: AsyncClient):
    ids = await _seed(client)

    r = await client.get("/api/v1/search", params={"q": "sw-core"})
    assert r.status_code == 200
    assert [a["id"] for a in r.json()["addresses"]] == [ids["addr"]["id"]]

    # "ATRM" hits site code, cert name, asset serial, service name, vlan name
    body = (await client.get("/api/v1/search", params={"q": "atrm"})).json()
    assert body["sites"][0]["id"] == ids["site"]["id"]
    assert body["certificates"][0]["cert_name"] == "*.atrm.example.com"
    assert body["assets"][0]["serial_number"] == "SN-ATRM-1"
    assert body["services"][0]["name"] == "ATRM DNS"
    assert body["vlans"][0]["name"] == "atrm-users"

    # circuit via bezeq id
    body = (await client.get("/api/v1/search", params={"q": "828328"})).json()
    assert body["circuits"][0]["bezeq_circuit_id"] == "828328469"


async def test_search_hebrew_folding(client: AsyncClient):
    await _seed(client)
    # final letters fold both ways: query "אתרימ" (base) matches stored "אתרים"
    body = (await client.get("/api/v1/search", params={"q": "אתרימ"})).json()
    assert any(s["name"] == "אתרים מרכזי" for s in body["sites"])


async def test_search_ip_jump(client: AsyncClient):
    ids = await _seed(client)

    # existing address -> jump to its prefix, exists=True
    body = (await client.get("/api/v1/search", params={"q": "10.20.3.44"})).json()
    jump = body["jump"]
    assert jump == {
        "address": "10.20.3.44",
        "prefix_id": ids["prefix"]["id"],
        "prefix": "10.20.0.0/16",
        "exists": True,
    }
    # the address itself is also a group hit
    assert body["addresses"][0]["address"] == "10.20.3.44"

    # unused IP inside the prefix still resolves the containing prefix
    body = (await client.get("/api/v1/search", params={"q": "10.20.9.9"})).json()
    assert body["jump"]["prefix_id"] == ids["prefix"]["id"]
    assert body["jump"]["exists"] is False

    # IP outside every prefix -> no jump
    body = (await client.get("/api/v1/search", params={"q": "192.0.2.1"})).json()
    assert body["jump"] is None


async def test_search_ip_jump_prefers_owner_then_deepest(client: AsyncClient):
    ids = await _seed(client)
    container = (
        await client.post(
            "/api/v1/prefixes",
            json={
                "prefix": "10.20.3.0/24",
                "vrf_id": ids["vrf"]["id"],
                "status": "container",
            },
        )
    ).json()
    # address rows anchor the jump: /16 owns 10.20.3.44, beating the deeper /24
    body = (await client.get("/api/v1/search", params={"q": "10.20.3.44"})).json()
    assert body["jump"]["prefix_id"] == ids["prefix"]["id"]
    # a free IP inside both goes to the deepest containing prefix
    body = (await client.get("/api/v1/search", params={"q": "10.20.3.99"})).json()
    assert body["jump"]["prefix_id"] == container["id"]
    assert body["jump"]["exists"] is False


async def test_addresses_q_filter_not_broken(client: AsyncClient):
    """Regression: list_addresses ?q= used to crash on a missing column."""
    ids = await _seed(client)
    r = await client.get("/api/v1/addresses", params={"q": "sw-core"})
    assert r.status_code == 200
    assert [a["id"] for a in r.json()] == [ids["addr"]["id"]]
    # also matches the raw address and notes/vendor fields
    r = await client.get("/api/v1/addresses", params={"q": "10.20.3.4"})
    assert [a["id"] for a in r.json()] == [ids["addr"]["id"]]
