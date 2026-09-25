"""V7.1 review center: every computed flag on one queue — section queries
with honest counts, auditable+reversible dismissals, the mac_mismatch
accept/keep write paths, resolver delegation, RBAC, backup coverage."""
from datetime import date, datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.changelog import AUDITED_MODELS
from app.core.config import get_settings
from app.core.redis import get_redis
from app.core.security import hash_password
from app.models.certificate import Certificate
from app.models.ip_address import IPAddress
from app.models.review import ReviewDismissal
from app.models.user import User, UserRole
from app.services.backup import BACKUP_TABLES

PASSWORD = "review-test-pw1"


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


async def _prefix(client: AsyncClient, cidr: str = "10.71.0.0/24") -> int:
    vrfs = (await client.get("/api/v1/vrfs")).json()
    vrf = (vrfs["items"] if isinstance(vrfs, dict) else vrfs)[0]
    r = await client.post(
        "/api/v1/prefixes", json={"prefix": cidr, "vrf_id": vrf["id"]}
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


async def _ip(client: AsyncClient, prefix_id: int, addr: str, **kw) -> dict:
    r = await client.post(
        "/api/v1/addresses", json={"address": addr, "prefix_id": prefix_id, **kw}
    )
    assert r.status_code == 201, r.text
    return r.json()


async def _device(client: AsyncClient, **kw) -> dict:
    r = await client.post("/api/v1/devices", json={"name": "srv", **kw})
    assert r.status_code == 201, r.text
    return r.json()


async def _iface(client: AsyncClient, device_id: int, **kw) -> dict:
    r = await client.post(
        f"/api/v1/devices/{device_id}/interfaces", json={"name": "p1", **kw}
    )
    assert r.status_code == 201, r.text
    return r.json()


async def _flag_mismatch(
    session: AsyncSession, ip_id: int, was: str, seen: str
) -> None:
    """Simulate the scanner's flag write (reconcile sets custom_fields)."""
    row = await session.get(IPAddress, ip_id)
    cf = dict(row.custom_fields or {})
    cf["mac_mismatch"] = {
        "was": was,
        "seen": seen,
        "at": datetime.now(timezone.utc).isoformat(),
    }
    row.custom_fields = cf
    await session.commit()


async def _review(client: AsyncClient) -> dict:
    r = await client.get("/api/v1/review")
    assert r.status_code == 200, r.text
    return r.json()


def _section(review: dict, key: str) -> dict:
    return next(s for s in review["sections"] if s["key"] == key)


ALL_KEYS = {
    "mac_mismatch",
    "dup_mac",
    "aging_discovery",
    "offline",
    "cert_expiry",
    "unmatched_switch",
    "uncabled",
    "unracked",
}


# --------------------------------------------------------------- sections


async def test_empty_state(client: AsyncClient):
    """Empty inventory → eight zero-count sections, no errors."""
    secs = {s["key"]: s for s in (await _review(client))["sections"]}
    assert set(secs) == ALL_KEYS
    for s in secs.values():
        assert s["count"] == 0 and s["items"] == [] and s["dismissed"] == []
    # aging is disabled at discovery_expire_days=0 — noted, not an error
    assert secs["aging_discovery"]["note"]


async def test_mac_mismatch_section(client: AsyncClient, session: AsyncSession):
    pid = await _prefix(client)
    ip = await _ip(
        client, pid, "10.71.0.10", mac_address="66:77:88:99:AA:BB"
    )
    await _flag_mismatch(session, ip["id"], "00:11:22:33:44:55", "66:77:88:99:AA:BB")

    sec = _section(await _review(client), "mac_mismatch")
    assert sec["count"] == 1
    it = sec["items"][0]
    assert it["entity_type"] == "ip_address" and it["entity_id"] == ip["id"]
    assert it["label"] == "10.71.0.10"
    assert it["detail"]["mac_was"] == "00:11:22:33:44:55"
    assert it["detail"]["mac_seen"] == "66:77:88:99:AA:BB"
    assert it["fingerprint"] == "00:11:22:33:44:55->66:77:88:99:aa:bb"
    assert it["flagged_at"]


async def test_dup_mac_section(client: AsyncClient):
    pid = await _prefix(client)
    a = await _ip(client, pid, "10.71.0.20", mac_address="00:AA:BB:CC:DD:EE")
    b = await _ip(client, pid, "10.71.0.21", mac_address="00:AA:BB:CC:DD:EE")
    await _ip(client, pid, "10.71.0.22", mac_address="11:22:33:44:55:66")

    sec = _section(await _review(client), "dup_mac")
    assert sec["count"] == 1
    it = sec["items"][0]
    assert it["entity_type"] == "mac_group"
    assert it["label"] == "00:aa:bb:cc:dd:ee"
    assert it["fingerprint"] == "mac:00:aa:bb:cc:dd:ee"
    member_ids = {m["id"] for m in it["detail"]["members"]}
    assert member_ids == {a["id"], b["id"]}


async def test_aging_discovery_section(client: AsyncClient, session: AsyncSession):
    await client.patch("/api/v1/settings", json={"discovery_expire_days": 30})
    pid = await _prefix(client)
    stale = await _ip(client, pid, "10.71.0.30", status="discovered")
    fresh = await _ip(client, pid, "10.71.0.31", status="discovered")
    row = await session.get(IPAddress, stale["id"])
    row.last_seen = datetime.now(timezone.utc) - timedelta(days=40)
    row = await session.get(IPAddress, fresh["id"])
    row.last_seen = datetime.now(timezone.utc) - timedelta(days=5)
    await session.commit()

    sec = _section(await _review(client), "aging_discovery")
    assert sec["count"] == 1
    assert sec["items"][0]["entity_id"] == stale["id"]

    # setting back to 0 disables the section (noted, not an error)
    await client.patch("/api/v1/settings", json={"discovery_expire_days": 0})
    sec = _section(await _review(client), "aging_discovery")
    assert sec["count"] == 0 and sec["note"]


async def test_offline_section(client: AsyncClient, session: AsyncSession):
    pid = await _prefix(client)
    dead = await _ip(client, pid, "10.71.0.40", status="offline")
    flapping = await _ip(client, pid, "10.71.0.41", status="offline")
    (await session.get(IPAddress, dead["id"])).missed_scans = 5
    # grace defaults to 1 — an offline row with missed_scans=0 doesn't count
    (await session.get(IPAddress, flapping["id"])).missed_scans = 0
    await session.commit()

    sec = _section(await _review(client), "offline")
    assert sec["count"] == 1
    it = sec["items"][0]
    assert it["entity_id"] == dead["id"]
    assert it["detail"]["missed_scans"] == 5


async def test_cert_expiry_section(client: AsyncClient, session: AsyncSession):
    today = date.today()
    session.add_all(
        [
            Certificate(cert_name="soon", expires_on=today + timedelta(days=10)),
            Certificate(cert_name="gone", expires_on=today - timedelta(days=2)),
            Certificate(cert_name="fine", expires_on=today + timedelta(days=300)),
        ]
    )
    await session.commit()

    sec = _section(await _review(client), "cert_expiry")
    assert sec["count"] == 2  # expiring-soon + already-expired
    labels = [i["label"] for i in sec["items"]]
    assert labels == ["gone", "soon"]  # earliest expiry first
    assert sec["items"][1]["detail"]["days"] == 10


async def test_unmatched_switch_section(client: AsyncClient):
    pid = await _prefix(client)
    legacy = await _ip(
        client, pid, "10.71.0.50", switch_name="sw1", switch_port="Gi0/1"
    )
    await _ip(client, pid, "10.71.0.51")  # no switch text → not flagged

    sec = _section(await _review(client), "unmatched_switch")
    assert sec["count"] == 1
    it = sec["items"][0]
    assert it["entity_id"] == legacy["id"]
    assert it["detail"]["switch_name"] == "sw1"
    assert it["fingerprint"] == "sw1|Gi0/1"


async def test_uncabled_and_unracked_sections(client: AsyncClient):
    bare = await _device(client, name="bare")  # no interfaces at all
    wired_no_cable = await _device(client, name="uncabled-srv")
    await _iface(client, wired_no_cable["id"], name="eth0")

    secs = {s["key"]: s for s in (await _review(client))["sections"]}
    # has interfaces, zero cables → uncabled; `bare` has no ports → excluded
    assert secs["uncabled"]["count"] == 1
    assert secs["uncabled"]["items"][0]["entity_id"] == wired_no_cable["id"]
    assert secs["uncabled"]["items"][0]["detail"]["interface_count"] == 1
    # neither device is racked
    assert secs["unracked"]["count"] == 2
    assert {i["entity_id"] for i in secs["unracked"]["items"]} == {
        bare["id"],
        wired_no_cable["id"],
    }


# ------------------------------------------------------------- dismissals


async def test_dismiss_undismiss_roundtrip(client: AsyncClient, session: AsyncSession):
    pid = await _prefix(client)
    ip = await _ip(client, pid, "10.71.0.60", mac_address="66:77:88:99:AA:BB")
    await _flag_mismatch(session, ip["id"], "00:11:22:33:44:55", "66:77:88:99:AA:BB")

    sec = _section(await _review(client), "mac_mismatch")
    it = sec["items"][0]
    body = {
        "kind": "mac_mismatch",
        "entity_type": it["entity_type"],
        "entity_id": it["entity_id"],
        "fingerprint": it["fingerprint"],
        "notes": "known laptop dock",
    }
    r = await client.post("/api/v1/review/dismiss", json=body)
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["kind"] == "mac_mismatch" and d["notes"] == "known laptop dock"
    assert d["actor"]

    sec = _section(await _review(client), "mac_mismatch")
    assert sec["count"] == 0 and sec["items"] == []
    assert len(sec["dismissed"]) == 1
    gone = sec["dismissed"][0]
    assert gone["entity_id"] == ip["id"]
    assert gone["dismiss_notes"] == "known laptop dock"
    assert gone["dismissed_by"]

    # re-dismissing the same tuple is idempotent — still one row
    r = await client.post("/api/v1/review/dismiss", json=body)
    assert r.status_code == 200
    rows = (await session.execute(select(ReviewDismissal))).scalars().all()
    assert len(rows) == 1

    # undismiss restores the item to the open list
    r = await client.post("/api/v1/review/undismiss", json=body)
    assert r.status_code == 204
    sec = _section(await _review(client), "mac_mismatch")
    assert sec["count"] == 1 and sec["dismissed"] == []
    assert (await client.post("/api/v1/review/undismiss", json=body)).status_code == 404


async def test_dismissal_survives_reflag(client: AsyncClient, session: AsyncSession):
    """The fingerprint pins the was→seen pair: a scanner re-flag of the same
    pair stays dismissed; a DIFFERENT seen MAC is a fresh finding."""
    pid = await _prefix(client)
    ip = await _ip(client, pid, "10.71.0.61", mac_address="66:77:88:99:AA:BB")
    was, seen = "00:11:22:33:44:55", "66:77:88:99:AA:BB"
    await _flag_mismatch(session, ip["id"], was, seen)
    body = {
        "kind": "mac_mismatch",
        "entity_type": "ip_address",
        "entity_id": ip["id"],
        "fingerprint": "00:11:22:33:44:55->66:77:88:99:aa:bb",
    }
    assert (await client.post("/api/v1/review/dismiss", json=body)).status_code == 200

    # scanner writes the same flag again → still dismissed
    await _flag_mismatch(session, ip["id"], was, seen)
    sec = _section(await _review(client), "mac_mismatch")
    assert sec["count"] == 0 and len(sec["dismissed"]) == 1

    # a new observed MAC → new fingerprint → resurfaces as open
    await _flag_mismatch(session, ip["id"], was, "DE:AD:BE:EF:00:01")
    sec = _section(await _review(client), "mac_mismatch")
    assert sec["count"] == 1


async def test_dismissals_are_audited(client: AsyncClient, session: AsyncSession):
    pid = await _prefix(client)
    ip = await _ip(client, pid, "10.71.0.62", mac_address="66:77:88:99:AA:BB")
    await _flag_mismatch(session, ip["id"], "00:11:22:33:44:55", "66:77:88:99:AA:BB")
    it = _section(await _review(client), "mac_mismatch")["items"][0]
    await client.post(
        "/api/v1/review/dismiss",
        json={
            "kind": "mac_mismatch",
            "entity_type": "ip_address",
            "entity_id": ip["id"],
            "fingerprint": it["fingerprint"],
        },
    )
    log = (
        await client.get(
            "/api/v1/changelog", params={"object_type": "ReviewDismissal"}
        )
    ).json()["items"]
    assert any(e["action"] == "create" for e in log)


# ----------------------------------------------------------- mac actions


async def test_mac_accept_writes_scanned_mac(
    client: AsyncClient, session: AsyncSession
):
    pid = await _prefix(client)
    ip = await _ip(client, pid, "10.71.0.70", mac_address="00:11:22:33:44:55")
    await _flag_mismatch(session, ip["id"], "00:11:22:33:44:55", "66:77:88:99:AA:BB")

    r = await client.post(f"/api/v1/review/mac_mismatch/{ip['id']}/accept")
    assert r.status_code == 200, r.text
    got = (await client.get(f"/api/v1/addresses/{ip['id']}")).json()
    assert got["mac_address"] == "66:77:88:99:AA:BB"
    assert "mac_mismatch" not in (got["custom_fields"] or {})
    # the flag's gone → nothing left in the section
    assert _section(await _review(client), "mac_mismatch")["count"] == 0
    # normal write path → changelog row
    log = (
        await client.get("/api/v1/changelog", params={"object_type": "IPAddress"})
    ).json()["items"]
    assert any(
        "mac_address" in str(e["changes"]) and e["object_id"] == ip["id"]
        for e in log
    )


async def test_mac_keep_restores_stored_and_dismisses(
    client: AsyncClient, session: AsyncSession
):
    """Scanner overwrote the stored MAC (default policy); keep puts it back
    and dismisses the pair so the next re-flag stays out of the queue."""
    pid = await _prefix(client)
    ip = await _ip(client, pid, "10.71.0.71", mac_address="66:77:88:99:AA:BB")
    await _flag_mismatch(session, ip["id"], "00:11:22:33:44:55", "66:77:88:99:AA:BB")

    r = await client.post(f"/api/v1/review/mac_mismatch/{ip['id']}/keep")
    assert r.status_code == 200, r.text
    got = (await client.get(f"/api/v1/addresses/{ip['id']}")).json()
    assert got["mac_address"] == "00:11:22:33:44:55"
    assert "mac_mismatch" not in (got["custom_fields"] or {})

    rows = (await session.execute(select(ReviewDismissal))).scalars().all()
    assert len(rows) == 1
    d = rows[0]
    assert d.kind == "mac_mismatch" and d.entity_id == ip["id"]
    assert d.fingerprint == "00:11:22:33:44:55->66:77:88:99:aa:bb"

    # re-flagged by the scanner → lands in dismissed, not open items
    await _flag_mismatch(session, ip["id"], "00:11:22:33:44:55", "66:77:88:99:AA:BB")
    sec = _section(await _review(client), "mac_mismatch")
    assert sec["count"] == 0 and len(sec["dismissed"]) == 1


async def test_mac_actions_require_flag(client: AsyncClient):
    pid = await _prefix(client)
    ip = await _ip(client, pid, "10.71.0.72")
    for verb in ("accept", "keep"):
        r = await client.post(f"/api/v1/review/mac_mismatch/{ip['id']}/{verb}")
        assert r.status_code == 404
    assert (
        await client.post("/api/v1/review/mac_mismatch/99999/accept")
    ).status_code == 404


# -------------------------------------------------------------- resolver


async def test_resolve_switch_fields(client: AsyncClient):
    """Review resolver delegates to the real match_free_text — same report
    shape, same changelog-covered writes."""
    pid = await _prefix(client)
    sw = await _device(client, name="sw1")
    await _iface(client, sw["id"], name="Gi1/0/1")
    good = await _ip(
        client, pid, "10.71.0.80", switch_name="sw1", switch_port="Gi1/0/1"
    )
    ghost = await _ip(
        client, pid, "10.71.0.81", switch_name="nowhere", switch_port="x"
    )

    r = await client.post("/api/v1/review/resolve-switch-fields")
    assert r.status_code == 200, r.text
    rep = r.json()
    assert rep["matched"] == 1 and rep["matched_ids"] == [good["id"]]
    assert rep["unmatched"] == 1 and rep["unmatched_ids"] == [ghost["id"]]
    assert rep["ambiguous"] == 0

    got = (await client.get(f"/api/v1/addresses/{good['id']}")).json()
    assert got["connected_interface_id"] is not None
    # linked row leaves the unmatched_switch section; the ghost stays
    sec = _section(await _review(client), "unmatched_switch")
    assert sec["count"] == 1
    assert sec["items"][0]["entity_id"] == ghost["id"]


# ------------------------------------------------------------------ misc


async def test_rbac_review(client: AsyncClient, session: AsyncSession, auth_on):
    await _mkuser(session, "v", UserRole.VIEWER)
    await _login(client, "v")
    assert (await client.get("/api/v1/review")).status_code == 200
    body = {
        "kind": "offline",
        "entity_type": "ip_address",
        "entity_id": 1,
        "fingerprint": "x",
    }
    for r in (
        await client.post("/api/v1/review/dismiss", json=body),
        await client.post("/api/v1/review/undismiss", json=body),
        await client.post("/api/v1/review/mac_mismatch/1/accept"),
        await client.post("/api/v1/review/mac_mismatch/1/keep"),
        await client.post("/api/v1/review/resolve-switch-fields"),
    ):
        assert r.status_code == 403

    await _mkuser(session, "c", UserRole.CONTRIBUTOR)
    await _login(client, "c")
    r = await client.post("/api/v1/review/dismiss", json=body)
    assert r.status_code == 200
    r = await client.post("/api/v1/review/undismiss", json=body)
    assert r.status_code == 204


def test_review_dismissals_backed_up_and_audited():
    names = [t.name for t in BACKUP_TABLES]
    assert "review_dismissals" in names
    assert ReviewDismissal in AUDITED_MODELS
