import gzip
import json

from sqlalchemy import text

from app.models.base import Base
from app.models.user import User
from app.services import backup as svc
from app.services.backup import BACKUP_TABLES, EXCLUDED_TABLES


def _registry_names() -> set[str]:
    return {spec.name for spec in BACKUP_TABLES}


def test_registry_covers_all_tables():
    """Guard: every ORM table must be backed up (or explicitly excluded).

    Adding a new model without a BackupTable entry fails this test loudly.
    """
    all_tables = set(Base.metadata.tables)
    expected = all_tables - EXCLUDED_TABLES
    assert _registry_names() == expected


async def _vrf(client) -> int:
    vrfs = (await client.get("/api/v1/vrfs")).json()
    return next(v["id"] for v in vrfs if v["name"] == "Global")


async def _seed(client) -> dict:
    site = (
        await client.post("/api/v1/sites", json={"name": "HQ", "slug": "hq"})
    ).json()
    vrf_id = await _vrf(client)
    group = (
        await client.post("/api/v1/vlan-groups", json={"name": "Access"})
    ).json()
    vlan = (
        await client.post(
            "/api/v1/vlans",
            json={"vid": 100, "name": "users", "group_id": group["id"]},
        )
    ).json()
    prefix = (
        await client.post(
            "/api/v1/prefixes",
            json={
                "prefix": "10.80.0.0/24",
                "vrf_id": vrf_id,
                "site_id": site["id"],
                "vlan_id": vlan["id"],
            },
        )
    ).json()
    a1 = (
        await client.post(
            "/api/v1/addresses",
            json={"prefix_id": prefix["id"], "address": "10.80.0.10", "status": "active"},
        )
    ).json()
    a2 = (
        await client.post(
            "/api/v1/addresses",
            json={
                "prefix_id": prefix["id"],
                "address": "10.80.0.11",
                "status": "active",
                "nat_inside_id": a1["id"],
            },
        )
    ).json()
    tag = (
        await client.post("/api/v1/tags", json={"name": "Critical", "color": "#ff0000"})
    ).json()
    await client.post(
        f"/api/v1/tags/{tag['id']}/assignments",
        json={"object_type": "IPAddress", "object_id": a2["id"]},
    )
    return {"site": site, "vlan": vlan, "prefix": prefix, "a1": a1, "a2": a2, "tag": tag}


async def _wipe(session):
    await session.execute(
        text(
            "TRUNCATE scan_jobs, ip_addresses, ip_ranges, prefixes, vrfs, "
            "sites, users, change_log, tag_assignments, tags, vlans, "
            "vlan_groups RESTART IDENTITY CASCADE"
        )
    )
    await session.commit()


async def _backup_bytes(client) -> bytes:
    r = await client.get("/api/v1/backup")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"] == "application/gzip"
    return r.content


async def _restore(client, payload: bytes, name="backup.json.gz", **params):
    return await client.post(
        "/api/v1/backup/restore",
        content=payload,
        headers={"content-type": "application/gzip"},
        params={"name": name, **params},
    )


async def test_backup_roundtrip(client, session):
    ids = await _seed(client)
    payload = await _backup_bytes(client)
    envelope = json.loads(gzip.decompress(payload))
    assert envelope["format"] == "ipambox-backup"
    assert "users" not in envelope["tables"]

    await _wipe(session)
    assert (await client.get("/api/v1/prefixes")).json() == []

    r = await _restore(client, payload)
    assert r.status_code == 200, r.text
    report = r.json()
    assert report["restored"]["sites"] == 1
    assert report["restored"]["ip_addresses"] == 2

    # rows come back with their ORIGINAL ids — polymorphic refs still valid
    prefix = (await client.get("/api/v1/prefixes")).json()
    assert [p["id"] for p in prefix] == [ids["prefix"]["id"]]
    assert prefix[0]["site_id"] == ids["site"]["id"]
    assert prefix[0]["vlan"]["vid"] == 100

    addrs = (await client.get("/api/v1/addresses")).json()
    by_addr = {a["address"]: a for a in addrs}
    assert by_addr["10.80.0.11"]["nat_inside_id"] == by_addr["10.80.0.10"]["id"]

    # tag assignment survived (polymorphic object_id preserved)
    assigns = (
        await client.get(
            "/api/v1/tags/assignments", params={"object_type": "IPAddress"}
        )
    ).json()
    assert any(a["object_id"] == by_addr["10.80.0.11"]["id"] for a in assigns)

    # changelog history was backed up and restored
    log = (await client.get("/api/v1/changelog")).json()
    assert any(e["object_type"] == "Site" for e in log)


async def test_restore_preserves_users(client, session):
    await _seed(client)
    payload = await _backup_bytes(client)
    session.add(User(username="restored-admin", password_hash="x"))
    await session.commit()

    r = await _restore(client, payload)
    assert r.status_code == 200, r.text
    n = await session.execute(text("SELECT COUNT(*) FROM users"))
    assert n.scalar() == 1  # untouched, even though the backup has no users


async def test_scan_jobs_sanitized_on_restore(client, session):
    from app.models.scan_job import ScanJob, ScanStatus

    await _seed(client)
    session.add(ScanJob(cidr="10.80.0.0/24", status=ScanStatus.RUNNING, progress=42.0))
    await session.commit()

    payload = await _backup_bytes(client)
    r = await _restore(client, payload)
    assert r.status_code == 200, r.text

    jobs = (await client.get("/api/v1/scans")).json()
    assert jobs[0]["status"] == "failed"
    assert "interrupted by restore" in jobs[0]["error"]


async def test_restore_replaces_seeded_global_vrf(client, session):
    """Fresh-server scenario: the migration-seeded Global VRF is replaced by
    the backup's own copy — not duplicated."""
    # give the backup's Global a non-1 id so the fresh-install seed differs:
    # delete the seeded Global first (while empty), recreate it, then seed.
    backup_vrf_id = await _vrf(client)
    await client.delete(f"/api/v1/vrfs/{backup_vrf_id}")
    recreated = (
        await client.post("/api/v1/vrfs", json={"name": "Global"})
    ).json()
    assert recreated["id"] != backup_vrf_id
    await _seed(client)
    payload = await _backup_bytes(client)

    # simulate a brand-new install: wipe, then re-seed Global (gets id 1 again)
    await _wipe(session)
    await session.execute(
        text("INSERT INTO vrfs (name, description) VALUES ('Global', 'seed')")
    )
    await session.commit()
    assert (await _vrf(client)) == 1

    r = await _restore(client, payload)
    assert r.status_code == 200, r.text
    vrfs = (await client.get("/api/v1/vrfs")).json()
    globals_ = [v for v in vrfs if v["name"] == "Global"]
    assert len(globals_) == 1
    assert globals_[0]["id"] == recreated["id"]


async def test_sequences_resynced_after_restore(client, session):
    await _seed(client)
    payload = await _backup_bytes(client)
    r = await _restore(client, payload)
    assert r.status_code == 200, r.text

    # creating after a restore must not collide with restored primary keys
    r = await client.post("/api/v1/sites", json={"name": "New", "slug": "new"})
    assert r.status_code == 201, r.text


async def test_dry_run_does_not_write(client, session):
    await _seed(client)
    payload = await _backup_bytes(client)
    before = (await client.get("/api/v1/prefixes")).json()

    r = await _restore(client, payload, dry_run=1)
    assert r.status_code == 200, r.text
    preview = r.json()
    assert preview["format"] == "ipambox-backup"
    assert preview["tables"]["sites"] == 1

    after = (await client.get("/api/v1/prefixes")).json()
    assert after == before


async def test_restore_rejects_bad_file(client):
    r = await _restore(client, b"not a backup at all")
    assert r.status_code == 422

    # a newer format_version is refused cleanly
    fake = gzip.compress(
        json.dumps({"format": "ipambox-backup", "format_version": 99, "tables": {}}).encode()
    )
    r = await _restore(client, fake)
    assert r.status_code == 422


async def test_backup_file_store(client, tmp_path, monkeypatch):
    monkeypatch.setattr(svc.settings, "backup_dir", str(tmp_path))

    path = svc.write_backup_file(b"\x1f\x8bfake")
    assert path.name.startswith("ipambox-backup-")
    files = svc.list_backup_files()
    assert [f["name"] for f in files] == [path.name]

    r = await client.get("/api/v1/backup/files")
    assert r.status_code == 200
    assert r.json()["files"][0]["name"] == path.name

    r = await client.get(f"/api/v1/backup/files/{path.name}")
    assert r.status_code == 200
    assert r.content == b"\x1f\x8bfake"

    # traversal is refused
    assert svc.read_backup_file("../secrets") is None
    r = await client.get("/api/v1/backup/files/..%2F..%2Fetc%2Fpasswd")
    assert r.status_code in (404, 422)

    # retention prunes oldest beyond keep
    for i in range(3):
        svc.write_backup_file(b"x", name=f"ipambox-backup-2026010{i}-000000.json.gz")
    removed = svc.prune_backups(keep=2)
    assert removed == 2
    assert len(svc.list_backup_files()) == 2
