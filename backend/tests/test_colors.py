"""Global row colors: manual row_color + rule-computed display_color.

Covers the shared behaviors on both router styles (circuits ride the
_crud_router factory; sites/certificates are representative) plus the
admin-only color_rules CRUD, rule priority, within_days boundaries and the
backup registry round-trip for the new table.
"""
import gzip
import json
from datetime import date, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.redis import get_redis
from app.core.security import hash_password
from app.models.change_log import ChangeLog
from app.models.color_rule import ColorRule
from app.models.user import User, UserRole

PASSWORD = "color-test-pw1"
RED = "#f43f5e"
BLUE = "#3b82f6"


@pytest.fixture
async def auth_on():
    """Same pattern as test_ordering: flip auth on, restore + flush keys."""
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


async def _mk_site(client: AsyncClient, name: str) -> dict:
    r = await client.post("/api/v1/sites", json={"name": name})
    assert r.status_code == 201, r.text
    return r.json()


async def _mk_rule(
    client: AsyncClient,
    entity_type="sites",
    field="name",
    operator="contains",
    value="hq",
    color=RED,
) -> dict:
    r = await client.post(
        "/api/v1/color-rules",
        json={
            "entity_type": entity_type,
            "field": field,
            "operator": operator,
            "value": value,
            "color": color,
        },
    )
    assert r.status_code == 201, r.text
    return r.json()


# --- manual row_color -------------------------------------------------------


async def test_row_color_set_clear_and_validated(client: AsyncClient):
    site = await _mk_site(client, "DC-East")

    r = await client.patch(
        f"/api/v1/sites/{site['id']}", json={"row_color": RED}
    )
    assert r.status_code == 200, r.text
    assert r.json()["row_color"] == RED
    assert r.json()["display_color"] == RED

    # lowercase normalization + rejection of non-hex
    r = await client.patch(
        f"/api/v1/sites/{site['id']}", json={"row_color": "#FF00AA"}
    )
    assert r.json()["row_color"] == "#ff00aa"
    r = await client.patch(
        f"/api/v1/sites/{site['id']}", json={"row_color": "red"}
    )
    assert r.status_code == 422

    # explicit null clears
    r = await client.patch(
        f"/api/v1/sites/{site['id']}", json={"row_color": None}
    )
    assert r.json()["row_color"] is None
    assert r.json()["display_color"] is None


async def test_row_color_requires_write_perm(
    client: AsyncClient, session: AsyncSession, auth_on
):
    await _mkuser(session, "v", UserRole.VIEWER)
    await _login(client, "v")
    r = await client.patch("/api/v1/sites/1", json={"row_color": RED})
    assert r.status_code == 403


# --- rules CRUD + gating ----------------------------------------------------


async def test_rule_crud_cycle(client: AsyncClient):
    rule = await _mk_rule(client)
    assert rule["position"] == 1

    r = await client.get("/api/v1/color-rules", params={"entity_type": "sites"})
    assert [x["id"] for x in r.json()] == [rule["id"]]

    r = await client.patch(
        f"/api/v1/color-rules/{rule['id']}", json={"value": "dc", "color": BLUE}
    )
    assert r.status_code == 200 and r.json()["color"] == BLUE

    r = await client.delete(f"/api/v1/color-rules/{rule['id']}")
    assert r.status_code == 204
    assert (await client.get("/api/v1/color-rules")).json() == []


async def test_rule_validation_errors(client: AsyncClient):
    for body, why in [
        ({"entity_type": "prefixes"}, "uncolorable entity"),
        ({"entity_type": "sites", "field": "nope"}, "unknown field"),
        ({"entity_type": "sites", "operator": "regex"}, "bad operator"),
        ({"entity_type": "sites", "color": "red"}, "non-hex color"),
        (
            {"entity_type": "sites", "field": "name", "operator": "within_days"},
            "within_days on a text field",
        ),
    ]:
        payload = {
            "entity_type": "sites",
            "field": "name",
            "operator": "eq",
            "value": "x",
            "color": RED,
            **body,
        }
        r = await client.post("/api/v1/color-rules", json=payload)
        assert r.status_code == 422, f"{why}: {r.status_code} {r.text}"


async def test_rules_require_admin(
    client: AsyncClient, session: AsyncSession, auth_on
):
    for name, role in [
        ("v", UserRole.VIEWER),
        ("c", UserRole.CONTRIBUTOR),
        ("o", UserRole.OPERATOR),
    ]:
        await _mkuser(session, name, role)
        await _login(client, name)
        assert (
            await client.get("/api/v1/color-rules")
        ).status_code == 403, name
        assert (
            await client.post(
                "/api/v1/color-rules",
                json={
                    "entity_type": "sites",
                    "field": "name",
                    "operator": "eq",
                    "value": "x",
                    "color": RED,
                },
            )
        ).status_code == 403, name

    await _mkuser(session, "a", UserRole.ADMIN)
    await _login(client, "a")
    assert (await client.get("/api/v1/color-rules")).status_code == 200
    rule = await _mk_rule(client)
    assert rule["entity_type"] == "sites"


# --- evaluation: priority, manual-beats-rule, within_days -------------------


async def test_rule_priority_and_reorder(client: AsyncClient):
    await _mk_site(client, "HQ-East")
    r1 = await _mk_rule(client, color=RED)  # pos 1 — first match
    r2 = await _mk_rule(client, color=BLUE)  # pos 2

    site = (await client.get("/api/v1/sites")).json()["items"][0]
    assert site["display_color"] == RED

    # flip priority: r2 now wins the same match
    r = await client.post(
        "/api/v1/color-rules/reorder",
        json={"entity_type": "sites", "ids": [r2["id"], r1["id"]]},
    )
    assert r.status_code == 204, r.text
    site = (await client.get("/api/v1/sites")).json()["items"][0]
    assert site["display_color"] == BLUE


async def test_manual_color_beats_rule(client: AsyncClient):
    site = await _mk_site(client, "HQ-East")
    await _mk_rule(client, color=RED)

    # rule fires when no manual color
    got = (await client.get(f"/api/v1/sites/{site['id']}")).json()
    assert got["display_color"] == RED

    # manual wins over the matching rule …
    r = await client.patch(
        f"/api/v1/sites/{site['id']}", json={"row_color": BLUE}
    )
    assert r.json()["display_color"] == BLUE

    # … and clearing falls back to the rule
    r = await client.patch(
        f"/api/v1/sites/{site['id']}", json={"row_color": None}
    )
    assert r.json()["display_color"] == RED


async def test_within_days_boundary(client: AsyncClient):
    today = date.today()
    iso = lambda d: d.isoformat()
    for days, name in [(-3, "past"), (0, "today"), (7, "edge"), (8, "out")]:
        r = await client.post(
            "/api/v1/certificates",
            json={"cert_name": name, "expires_on": iso(today + timedelta(days=days))},
        )
        assert r.status_code == 201, r.text
    await _mk_rule(
        client,
        entity_type="certificates",
        field="expires_on",
        operator="within_days",
        value="7",
        color=RED,
    )
    certs = {c["cert_name"]: c for c in (await client.get("/api/v1/certificates")).json()["items"]}
    assert certs["past"]["display_color"] == RED  # past-due counts as within
    assert certs["today"]["display_color"] == RED
    assert certs["edge"]["display_color"] == RED
    assert certs["out"]["display_color"] is None


async def test_rule_operators_on_addresses(client: AsyncClient):
    vrf_id = next(
        v["id"] for v in (await client.get("/api/v1/vrfs")).json() if v["name"] == "Global"
    )
    prefix = (
        await client.post(
            "/api/v1/prefixes", json={"prefix": "10.99.0.0/24", "vrf_id": vrf_id}
        )
    ).json()
    for ip, status in [("10.99.0.5", "active"), ("10.99.0.6", "discovered")]:
        r = await client.post(
            "/api/v1/addresses",
            json={"prefix_id": prefix["id"], "address": ip, "status": status},
        )
        assert r.status_code == 201, r.text
    await _mk_rule(
        client,
        entity_type="addresses",
        field="status",
        operator="eq",
        value="discovered",
        color=BLUE,
    )
    rows = {
        a["address"]: a
        for a in (await client.get("/api/v1/addresses")).json()
    }
    assert rows["10.99.0.5"]["display_color"] is None
    assert rows["10.99.0.6"]["display_color"] == BLUE

    # the prefix detail page (the address list view) agrees
    page = (await client.get(f"/api/v1/prefixes/{prefix['id']}/addresses")).json()
    by_ip = {a["address"]: a for a in page["items"]}
    assert by_ip["10.99.0.6"]["display_color"] == BLUE


async def test_rule_preview_counts_matches(client: AsyncClient):
    await _mk_site(client, "HQ-East")
    await _mk_site(client, "HQ-West")
    await _mk_site(client, "Branch")
    r = await client.get(
        "/api/v1/color-rules/preview",
        params={
            "entity_type": "sites",
            "field": "name",
            "operator": "contains",
            "value": "hq",
        },
    )
    assert r.status_code == 200 and r.json()["count"] == 2


# --- audit + backup ---------------------------------------------------------


async def test_rule_changes_are_audited(client: AsyncClient, session: AsyncSession):
    rule = await _mk_rule(client)
    entries = (
        await session.execute(
            select(ChangeLog).where(ChangeLog.object_type == "ColorRule")
        )
    ).scalars().all()
    assert entries and entries[0].action == "create"
    assert entries[0].object_id == rule["id"]


async def test_backup_roundtrips_color_rules(client: AsyncClient):
    rule = await _mk_rule(client, entity_type="circuits", field="status")
    payload = (await client.get("/api/v1/backup")).content
    env = json.loads(gzip.decompress(payload))
    assert env["tables"]["color_rules"][0]["id"] == rule["id"]

    await client.delete(f"/api/v1/color-rules/{rule['id']}")
    r = await client.post(
        "/api/v1/backup/restore",
        content=payload,
        headers={"content-type": "application/gzip"},
    )
    assert r.status_code == 200, r.text
    rules = (await client.get("/api/v1/color-rules")).json()
    assert len(rules) == 1
    assert rules[0]["entity_type"] == "circuits"
    assert rules[0]["position"] == rule["position"]
