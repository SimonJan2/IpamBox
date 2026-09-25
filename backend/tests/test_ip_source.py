"""V6 provenance — ip_addresses.source: stamping, ownership, filtering.

Every writer stamps its tag; the scanner owns only rows it created, so a
manual or imported row keeps its provenance when reconcile touches it.
"""
import ipaddress
import os
import subprocess

import asyncpg

from app.services.ipam import SOURCE_RANK, may_write
from app.worker.reconcile import reconcile
from app.worker.scanner import HostResult
from tests.conftest import _base_dsn, _split_dsn

MIGRATION_DB = "ipam_test_migrate"


async def _vrf_id(client) -> int:
    vrfs = (await client.get("/api/v1/vrfs")).json()
    return next(v["id"] for v in vrfs if v["name"] == "Global")


async def _mk_prefix(client, cidr: str, vrf_id: int) -> dict:
    r = await client.post("/api/v1/prefixes", json={"prefix": cidr, "vrf_id": vrf_id})
    assert r.status_code == 201, r.text
    return r.json()


# ---------------------------------------------------------------- helpers

def test_may_write_ranking():
    # scan observations never overwrite anything curated
    assert may_write("scan", "manual")
    assert may_write("scan", "import")
    assert may_write("scan", "scan")      # a scan rewrites its own rows
    assert not may_write("manual", "scan")
    assert not may_write("import", "scan")
    # snmp/integration sit between scan and import in the rank table
    assert may_write("scan", "snmp")
    assert not may_write("snmp", "scan")
    assert may_write("integration", "import")
    assert not may_write("import", "integration")
    assert may_write("snmp", "manual")
    # fail closed both ways: unknown stored -> protected; unknown
    # incoming -> never wins; NULL stored behaves as pre-v6 manual
    assert not may_write(None, "scan")
    assert not may_write("controller", "scan")
    assert not may_write("scan", "bogus")
    assert SOURCE_RANK["scan"] < SOURCE_RANK["import"] < SOURCE_RANK["manual"]


async def test_manual_create_stamps_manual(client):
    vrf_id = await _vrf_id(client)
    p = await _mk_prefix(client, "10.70.0.0/24", vrf_id)
    r = await client.post(
        "/api/v1/addresses",
        json={"address": "10.70.0.9", "prefix_id": p["id"]},
    )
    assert r.status_code == 201, r.text
    assert r.json()["source"] == "manual"


async def test_reserve_next_available_stamps_manual(client):
    vrf_id = await _vrf_id(client)
    p = await _mk_prefix(client, "10.70.1.0/24", vrf_id)
    r = await client.post(f"/api/v1/prefixes/{p['id']}/available-ips", json={})
    assert r.status_code == 201, r.text
    row = (await client.get(f"/api/v1/addresses/{r.json()['id']}")).json()
    assert row["source"] == "manual"


async def test_csv_import_stamps_import(client):
    vrf_id = await _vrf_id(client)
    p = await _mk_prefix(client, "10.71.0.0/24", vrf_id)
    r = await client.post(
        "/api/v1/addresses/import",
        content="address,prefix,hostname\n10.71.0.5,10.71.0.0/24,imported.lan\n",
    )
    assert r.status_code == 200, r.text
    rows = (
        await client.get("/api/v1/addresses", params={"prefix_id": p["id"]})
    ).json()
    assert [a["source"] for a in rows] == ["import"]


async def test_scanner_create_stamps_scan(client, session):
    vrf_id = await _vrf_id(client)
    p = await _mk_prefix(client, "10.72.0.0/24", vrf_id)
    net = ipaddress.ip_network("10.72.0.0/24")
    n, new = await reconcile(
        session,
        p["id"],
        vrf_id,
        [HostResult(ip="10.72.0.7", mac="AA:BB:CC:DD:EE:07")],
        net,
    )
    await session.commit()
    assert (n, new) == (1, 1)
    rows = (
        await client.get("/api/v1/addresses", params={"prefix_id": p["id"]})
    ).json()
    assert rows[0]["source"] == "scan"


async def test_reconcile_never_rewrites_source(client, session):
    """Manual and imported rows keep their provenance when a scan sees them —
    observed fields still refresh; source does not move."""
    vrf_id = await _vrf_id(client)
    p = await _mk_prefix(client, "10.73.0.0/24", vrf_id)
    r = await client.post(
        "/api/v1/addresses",
        json={"address": "10.73.0.10", "prefix_id": p["id"], "status": "active"},
    )
    assert r.status_code == 201, r.text
    r = await client.post(
        "/api/v1/addresses/import",
        content="address,prefix\n10.73.0.11,10.73.0.0/24\n",
    )
    assert r.status_code == 200, r.text

    net = ipaddress.ip_network("10.73.0.0/24")
    await reconcile(
        session,
        p["id"],
        vrf_id,
        [
            HostResult(ip="10.73.0.10", hostname="seen.lan"),
            HostResult(ip="10.73.0.11", mac="AA:BB:CC:DD:EE:11"),
        ],
        net,
    )
    await session.commit()

    rows = {
        r["address"]: r
        for r in (
            await client.get("/api/v1/addresses", params={"prefix_id": p["id"]})
        ).json()
    }
    assert rows["10.73.0.10"]["source"] == "manual"
    assert rows["10.73.0.11"]["source"] == "import"
    # observed fields still refreshed — provenance is the only frozen field
    assert rows["10.73.0.10"]["hostname"] == "seen.lan"
    assert rows["10.73.0.11"]["mac_address"] == "AA:BB:CC:DD:EE:11"


async def test_source_filter(client):
    vrf_id = await _vrf_id(client)
    p = await _mk_prefix(client, "10.74.0.0/24", vrf_id)
    await client.post(
        "/api/v1/addresses",
        json={"address": "10.74.0.5", "prefix_id": p["id"]},
    )
    await client.post(
        "/api/v1/addresses/import",
        content="address,prefix\n10.74.0.6,10.74.0.0/24\n",
    )

    r = await client.get(
        "/api/v1/addresses", params={"prefix_id": p["id"], "source": "manual"}
    )
    assert [a["address"] for a in r.json()] == ["10.74.0.5"]
    r = await client.get(
        "/api/v1/addresses",
        params={"prefix_id": p["id"], "source": "manual,import"},
    )
    assert len(r.json()) == 2
    r = await client.get(
        "/api/v1/addresses", params={"prefix_id": p["id"], "source": "scan"}
    )
    assert r.json() == []


async def test_export_filters_and_carries_source(client):
    vrf_id = await _vrf_id(client)
    p = await _mk_prefix(client, "10.75.0.0/24", vrf_id)
    await client.post(
        "/api/v1/addresses",
        json={"address": "10.75.0.5", "prefix_id": p["id"]},
    )
    await client.post(
        "/api/v1/addresses/import",
        content="address,prefix\n10.75.0.6,10.75.0.0/24\n",
    )
    r = await client.get(
        "/api/v1/addresses/export.csv",
        params={"prefix_id": p["id"], "source": "import"},
    )
    assert r.status_code == 200
    lines = r.text.splitlines()
    assert "source" in lines[0].split(",")
    body = "\n".join(lines[1:])
    assert "10.75.0.6" in body and "10.75.0.5" not in body
    assert ",import," in body


async def test_no_secret_columns_leak(client):
    """Response bodies carry `source` but never any *_enc-style field."""
    vrf_id = await _vrf_id(client)
    p = await _mk_prefix(client, "10.76.0.0/24", vrf_id)
    r = await client.post(
        "/api/v1/addresses",
        json={"address": "10.76.0.9", "prefix_id": p["id"]},
    )
    assert r.status_code == 201, r.text
    for body in (r.json(), (await client.get("/api/v1/addresses")).json()[0]):
        assert body["source"] == "manual"
        assert not any(k.endswith("_enc") for k in body)


# ------------------------------------------------------- migration 0024


def _mig_url() -> str:
    root, query = _split_dsn(_base_dsn())
    return f"{root}/{MIGRATION_DB}{query}"


async def test_migration_0024_backfill_and_rollback():
    """Scratch DB: rows seeded at 0023 upgrade to 'import'/'manual' at head;
    downgrade drops the column; re-upgrade re-backfills (idempotent)."""
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    root, query = _split_dsn(_base_dsn())
    pg_url = _mig_url()  # postgresql:// for asyncpg
    env = dict(os.environ, DATABASE_URL=pg_url.replace("postgresql://", "postgresql+asyncpg://"))

    def alembic(*args: str) -> None:
        subprocess.run(["alembic", *args], check=True, env=env, cwd=backend_dir)

    conn = await asyncpg.connect(f"{root}/postgres{query}")
    try:
        await conn.execute(f'DROP DATABASE IF EXISTS "{MIGRATION_DB}" WITH (FORCE)')
        await conn.execute(f'CREATE DATABASE "{MIGRATION_DB}"')
    finally:
        await conn.close()

    try:
        # schema at the parent revision — before `source` exists
        alembic("upgrade", "0023_interfaces_cables")

        conn = await asyncpg.connect(pg_url)
        try:
            cols = {
                r["column_name"]
                for r in await conn.fetch(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'ip_addresses'"
                )
            }
            assert "source" not in cols

            await conn.execute("INSERT INTO vrfs (name) VALUES ('Mig')")
            await conn.execute(
                "INSERT INTO prefixes (prefix, vrf_id) VALUES ('10.80.0.0/24', 1)"
            )
            await conn.execute(
                "INSERT INTO import_batches (filename, stored_path, sha256, status) "
                "VALUES ('w.xlsx', '/tmp/w.xlsx', 'deadbeef', 'committed')"
            )
            await conn.execute(
                "INSERT INTO ip_addresses "
                "(address, address_int, prefix_id, vrf_id, import_batch_id) "
                "VALUES ('10.80.0.1', 173015041, 1, 1, 1), "
                "       ('10.80.0.2', 173015042, 1, 1, NULL)"
            )
        finally:
            await conn.close()

        # 0024 adds the column and backfills honestly
        alembic("upgrade", "head")
        conn = await asyncpg.connect(pg_url)
        try:
            # host() strips the /32 inet display suffix
            rows = {
                r["address"]: r["source"]
                for r in await conn.fetch(
                    "SELECT host(address) AS address, source FROM ip_addresses"
                )
            }
            assert rows == {"10.80.0.1": "import", "10.80.0.2": "manual"}

            # the backfill UPDATE is idempotent — re-running changes nothing
            await conn.execute(
                "UPDATE ip_addresses SET source = 'import' "
                "WHERE import_batch_id IS NOT NULL AND source <> 'import'"
            )
            rows2 = {
                r["address"]: r["source"]
                for r in await conn.fetch(
                    "SELECT host(address) AS address, source FROM ip_addresses"
                )
            }
            assert rows2 == rows
        finally:
            await conn.close()

        # reversible: the column (and its index) drop cleanly
        alembic("downgrade", "-1")
        conn = await asyncpg.connect(pg_url)
        try:
            cols = {
                r["column_name"]
                for r in await conn.fetch(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'ip_addresses'"
                )
            }
            assert "source" not in cols
        finally:
            await conn.close()

        # and re-upgrade re-derives provenance from import_batch_id
        alembic("upgrade", "head")
        conn = await asyncpg.connect(pg_url)
        try:
            rows = {
                r["address"]: r["source"]
                for r in await conn.fetch(
                    "SELECT host(address) AS address, source FROM ip_addresses"
                )
            }
            assert rows == {"10.80.0.1": "import", "10.80.0.2": "manual"}
        finally:
            await conn.close()
    finally:
        conn = await asyncpg.connect(f"{root}/postgres{query}")
        try:
            await conn.execute(
                f'DROP DATABASE IF EXISTS "{MIGRATION_DB}" WITH (FORCE)'
            )
        finally:
            await conn.close()
