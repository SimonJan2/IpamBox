"""W8: no N+1 stats queries, filters run in SQL before LIMIT, the
existing-address import probe is scoped to the file's prefixes, and the
previously unbounded list routes answer with {items, total, limit, offset}.
"""
import ipaddress

from sqlalchemy import event

from app.models.ip_address import IPAddress, IPStatus
from app.models.prefix import Prefix


async def test_prefix_list_stats_is_one_grouped_query(client, session, engine):
    """The old _with_stats ran one COUNT(ip_addresses) per row — N prefixes
    meant N+1 queries. The list now joins a single grouped count."""
    for i in range(5):
        session.add(Prefix(prefix=f"10.6{i}.0.0/24", vrf_id=1))
    await session.commit()

    stmts = []

    def capture(conn, cursor, statement, parameters, context, executemany):
        stmts.append(statement)

    event.listen(engine.sync_engine, "before_cursor_execute", capture)
    try:
        r = await client.get("/api/v1/prefixes")
    finally:
        event.remove(engine.sync_engine, "before_cursor_execute", capture)
    assert r.status_code == 200 and len(r.json()) == 5
    hits = [s for s in stmts if "ip_addresses" in s]
    assert len(hits) == 1, f"expected 1 grouped count, got {len(hits)}: {hits}"
    assert "GROUP BY" in hits[0].upper()


async def test_addresses_q_filters_before_limit(client, session):
    """?q= used to filter in Python on an already-LIMITed page — matches
    past the window were invisible. The predicate lives in SQL now."""
    p = Prefix(prefix="10.7.0.0/24", vrf_id=1)
    session.add(p)
    await session.flush()
    for i in range(3):  # 'web' rows sort first by address_int
        session.add(
            IPAddress(
                address=f"10.7.0.{i + 1}",
                address_int=int(ipaddress.ip_address(f"10.7.0.{i + 1}")),
                prefix_id=p.id,
                vrf_id=1,
                status=IPStatus.ACTIVE,
                hostname="web",
            )
        )
    for i in range(3):  # 'db' rows sort last — a limit-first filter misses them
        session.add(
            IPAddress(
                address=f"10.7.0.{i + 10}",
                address_int=int(ipaddress.ip_address(f"10.7.0.{i + 10}")),
                prefix_id=p.id,
                vrf_id=1,
                status=IPStatus.ACTIVE,
                hostname="db",
            )
        )
    await session.commit()

    r = await client.get("/api/v1/addresses", params={"q": "db", "limit": 2})
    assert [a["hostname"] for a in r.json()] == ["db", "db"]
    r = await client.get(
        "/api/v1/addresses", params={"q": "db", "limit": 2, "offset": 2}
    )
    assert [a["hostname"] for a in r.json()] == ["db"]

    # export shares the same predicate — the filtered CSV shows db rows only
    r = await client.get("/api/v1/addresses/export.csv", params={"q": "db"})
    assert "10.7.0.10" in r.text and ",web" not in r.text


async def test_list_envelopes(client, session):
    """The unbounded list routes now answer {items, total, limit, offset};
    no limit -> the full set (items == total)."""
    session.add(Prefix(prefix="10.8.0.0/24", vrf_id=1))
    await session.commit()

    for route in (
        "/api/v1/sites",
        "/api/v1/vlans",
        "/api/v1/ranges",
        "/api/v1/discovery",
        "/api/v1/imports",
        "/api/v1/circuits",
        "/api/v1/certificates",
        "/api/v1/assets",
        "/api/v1/services",
    ):
        body = (await client.get(route)).json()
        assert set(body) >= {"items", "total", "limit", "offset"}, route
        assert body["total"] == len(body["items"]), route
        assert body["limit"] is None and body["offset"] == 0, route

    await client.post("/api/v1/sites", json={"name": "env"})
    await client.post("/api/v1/sites", json={"name": "env2"})
    body = (await client.get("/api/v1/sites", params={"limit": 1})).json()
    assert len(body["items"]) == 1 and body["total"] == 2 and body["limit"] == 1
    body = (
        await client.get("/api/v1/sites", params={"limit": 1, "offset": 1})
    ).json()
    assert body["offset"] == 1 and body["items"][0]["name"] != "env"

    # changelog stays bounded by default but now reports the honest total
    body = (await client.get("/api/v1/changelog")).json()
    assert body["limit"] == 200 and body["total"] >= 2


async def test_import_existing_probe_scoped_to_file_prefixes(
    client, session, engine
):
    """import_addresses used to SELECT every ip_addresses row into a set.
    The probe must only touch prefixes named in the uploaded file."""
    p_used = Prefix(prefix="10.9.0.0/24", vrf_id=1)
    p_other = Prefix(prefix="10.10.0.0/24", vrf_id=1)
    session.add_all([p_used, p_other])
    await session.flush()
    session.add(
        IPAddress(
            address="10.10.0.9",
            address_int=int(ipaddress.ip_address("10.10.0.9")),
            prefix_id=p_other.id,
            vrf_id=1,
            status=IPStatus.ACTIVE,
        )
    )
    await session.commit()

    captured = []

    def capture(conn, cursor, statement, parameters, context, executemany):
        captured.append((statement, parameters))

    event.listen(engine.sync_engine, "before_cursor_execute", capture)
    try:
        r = await client.post(
            "/api/v1/addresses/import",
            content="address,prefix\n10.9.0.5,10.9.0.0/24\n",
            headers={"content-type": "text/csv"},
        )
    finally:
        event.remove(engine.sync_engine, "before_cursor_execute", capture)
    assert r.status_code == 200, r.text
    assert r.json()[0]["ok"] is True

    probes = [
        (s, p)
        for s, p in captured
        if s.lstrip().upper().startswith("SELECT") and "ip_addresses" in s
    ]
    assert len(probes) == 1, f"expected one scoped probe: {probes}"
    flat_params = str(probes[0][1])
    assert str(p_used.id) in flat_params
    assert str(p_other.id) not in flat_params
