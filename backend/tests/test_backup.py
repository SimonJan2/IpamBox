import gzip
import json

from sqlalchemy import text

from app.models.base import Base
from app.models.user import User, UserRole
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
    # `users` is valid in an envelope ONLY via the includes_users flag — it
    # must never join the registry, whose TRUNCATE would wipe admin accounts.
    assert "users" in EXCLUDED_TABLES and "users" not in _registry_names()


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
    # a racked device owning both addresses — the V3 link under test
    rack = (
        await client.post("/api/v1/racks", json={"name": "B-01", "height_u": 24})
    ).json()
    device = (
        await client.post(
            "/api/v1/devices",
            json={
                "name": "core-sw",
                "rack_id": rack["id"],
                "u_position": 10,
                "u_height": 1,
                "serial_number": "SN-BKP-1",
            },
        )
    ).json()
    for a in (a1, a2):
        r = await client.patch(
            f"/api/v1/addresses/{a['id']}", json={"device_id": device["id"]}
        )
        assert r.status_code == 200, r.text
    # a plain Date column — certificates.expires_on exercises the
    # non-DateTime date decode path in restore
    cert = (
        await client.post(
            "/api/v1/certificates",
            json={"cert_name": "edge-lb", "expires_on": "2030-06-30"},
        )
    ).json()
    return {
        "site": site, "vlan": vlan, "prefix": prefix, "a1": a1, "a2": a2,
        "tag": tag, "rack": rack, "device": device, "cert": cert,
    }


async def _wipe(session):
    await session.execute(
        text(
            "TRUNCATE scan_jobs, ip_addresses, ip_ranges, prefixes, vrfs, "
            "sites, users, change_log, tag_assignments, tags, vlans, "
            "vlan_groups, devices, racks, rack_groups RESTART IDENTITY CASCADE"
        )
    )
    await session.commit()


async def _backup_bytes(client, **params) -> bytes:
    r = await client.get("/api/v1/backup", params=params)
    assert r.status_code == 200, r.text
    assert r.headers["content-type"] == "application/gzip"
    return r.content


def _envelope_bytes(tables: dict, **extra) -> bytes:
    """Hand-craft a backup envelope (e.g. with a forged users table)."""
    env = {
        "format": "ipambox-backup",
        "format_version": 1,
        "tables": tables,
        **extra,
    }
    return gzip.compress(json.dumps(env).encode())


async def _mkusers(session) -> dict[str, User]:
    users = {}
    for name, role in [
        ("admin1", UserRole.ADMIN),
        ("op1", UserRole.OPERATOR),
        ("c1", UserRole.CONTRIBUTOR),
        ("v1", UserRole.VIEWER),
    ]:
        u = User(username=name, password_hash="x", role=role)
        session.add(u)
        users[name] = u
    await session.commit()
    for u in users.values():
        await session.refresh(u)
    return users


async def _usernames(session) -> set[str]:
    rows = await session.execute(text("SELECT username FROM users"))
    return set(rows.scalars().all())


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
    log = (await client.get("/api/v1/changelog")).json()["items"]
    assert any(e["object_type"] == "Site" for e in log)

    # device + rack + device↔IP links survived the wipe (V3: devices restore
    # before ip_addresses, original ids preserved so links stay valid)
    assert report["restored"]["devices"] == 1
    assert report["restored"]["racks"] == 1
    dev = (await client.get(f"/api/v1/devices/{ids['device']['id']}")).json()
    assert dev["name"] == "core-sw"
    assert dev["rack_id"] == ids["rack"]["id"]
    assert dev["u_position"] == 10 and dev["serial_number"] == "SN-BKP-1"
    assert {i["id"] for i in dev["ips"]} == {ids["a1"]["id"], ids["a2"]["id"]}
    assert {a["device_id"] for a in addrs} == {ids["device"]["id"]}

    # plain-Date columns round-trip (certificates.expires_on regressed once)
    certs = (await client.get("/api/v1/certificates")).json()["items"]
    assert certs[0]["expires_on"] == "2030-06-30"


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


# --------------------------------------------------------------------- users


async def test_backup_include_users_excludes_admins(client, session):
    await _mkusers(session)
    payload = await _backup_bytes(client, include_users=1)
    envelope = json.loads(gzip.decompress(payload))
    assert envelope["includes_users"] is True
    rows = envelope["tables"]["users"]
    assert {u["username"] for u in rows} == {"op1", "c1", "v1"}
    assert all(u["role"] != "admin" for u in rows)
    assert all("password_hash" in u for u in rows)

    # default export: no users table, no flag
    envelope = json.loads(gzip.decompress(await _backup_bytes(client)))
    assert "users" not in envelope["tables"]
    assert "includes_users" not in envelope


async def test_restore_users_replaces_non_admins_keeps_admins(client, session):
    """Fresh-server scenario: the target's admins survive; its non-admin set
    is fully replaced by the file's non-admin rows (original ids kept)."""
    users = await _mkusers(session)
    payload = await _backup_bytes(client, include_users=1)

    await _wipe(session)
    session.add(
        User(username="bootstrap", password_hash="x", role=UserRole.ADMIN)
    )
    session.add(User(username="stale", password_hash="x", role=UserRole.VIEWER))
    await session.commit()

    r = await _restore(client, payload)
    assert r.status_code == 200, r.text
    assert r.json()["restored"]["users"] == 3

    rows = (
        await session.execute(text("SELECT id, username FROM users"))
    ).all()
    by_name = {u.username: u.id for u in rows}
    assert "bootstrap" in by_name  # admin created on the target survives
    assert "stale" not in by_name  # non-admin set was replaced
    assert "admin1" not in by_name  # admins are never exported
    assert by_name["op1"] == users["op1"].id  # original ids preserved

    # users sequence resynced — a new account can't collide with restored ids
    session.add(User(username="after", password_hash="x", role=UserRole.VIEWER))
    await session.commit()


async def test_restore_ignores_admin_rows_in_file(client, session):
    session.add(User(username="keeper", password_hash="x", role=UserRole.ADMIN))
    await session.commit()
    payload = _envelope_bytes(
        {
            "users": [
                {"id": 5, "username": "sneaky", "password_hash": "h", "role": "admin"},
                {"id": 6, "username": "op", "password_hash": "h", "role": "operator"},
            ]
        },
        includes_users=True,
    )
    r = await _restore(client, payload)
    assert r.status_code == 200, r.text
    report = r.json()
    assert (
        "1 admin account(s) ignored — admins are never restored"
        in report["warnings"]
    )
    assert await _usernames(session) == {"keeper", "op"}


async def test_restore_user_pk_collision_with_admin(client, session):
    admin = User(username="boss", password_hash="x", role=UserRole.ADMIN)
    session.add(admin)
    await session.commit()
    await session.refresh(admin)
    payload = _envelope_bytes(
        {
            "users": [
                {
                    "id": admin.id,
                    "username": "impostor",
                    "password_hash": "h",
                    "role": "viewer",
                },
                {
                    "id": admin.id + 100,
                    "username": "fine",
                    "password_hash": "h",
                    "role": "viewer",
                },
            ]
        },
        includes_users=True,
    )
    r = await _restore(client, payload)
    assert r.status_code == 200, r.text
    assert (
        f"user 'impostor' skipped: id {admin.id} in use by an admin account"
        in r.json()["warnings"]
    )
    assert await _usernames(session) == {"boss", "fine"}


async def test_restore_users_invalid_role_skipped(client, session):
    session.add(User(username="keeper", password_hash="x", role=UserRole.ADMIN))
    await session.commit()
    payload = _envelope_bytes(
        {
            "users": [
                {"id": 2, "username": "bad", "password_hash": "h", "role": "superuser"},
                {"id": 3, "username": "good", "password_hash": "h", "role": "viewer"},
            ]
        },
        includes_users=True,
    )
    r = await _restore(client, payload)
    assert r.status_code == 200, r.text
    assert "user 'bad' skipped: unknown role 'superuser'" in r.json()["warnings"]
    assert await _usernames(session) == {"keeper", "good"}


async def test_restore_users_empty_set_clears_non_admins(client, session):
    session.add(User(username="keeper", password_hash="x", role=UserRole.ADMIN))
    session.add(User(username="gone", password_hash="x", role=UserRole.VIEWER))
    await session.commit()
    payload = _envelope_bytes({"users": []}, includes_users=True)
    r = await _restore(client, payload)
    assert r.status_code == 200, r.text
    assert await _usernames(session) == {"keeper"}


async def test_dry_run_reports_users(client, session):
    await _mkusers(session)
    payload = await _backup_bytes(client, include_users=1)

    r = await _restore(client, payload, dry_run=1)
    assert r.status_code == 200, r.text
    preview = r.json()
    assert preview["includes_users"] is True
    assert preview["tables"]["users"] == 3

    n = await session.execute(text("SELECT COUNT(*) FROM users"))
    assert n.scalar() == 4  # preview wrote nothing


async def test_restore_drops_orphaned_tag_assignments(client, session):
    """A backup carrying an assignment for a missing object (e.g. taken while
    orphans still existed) must not resurrect it — raw inserts bypass the
    flush hooks, so restore sweeps them before committing."""
    payload = _envelope_bytes(
        {
            "tags": [{"id": 1, "name": "core", "slug": "core"}],
            "tag_assignments": [
                {"id": 1, "tag_id": 1, "object_type": "IPAddress", "object_id": 99999},
                {"id": 2, "tag_id": 1, "object_type": "Nonsense", "object_id": 1},
            ],
        }
    )
    r = await _restore(client, payload)
    assert r.status_code == 200, r.text
    report = r.json()
    assert "2 orphaned tag assignment(s) dropped on restore" in report["warnings"]
    assert (await client.get("/api/v1/tags/assignments")).json() == []


async def test_users_table_without_flag_is_skipped(client, session):
    """A forged users table without the includes_users flag is treated as
    unknown and the real users table is left untouched."""
    session.add(User(username="keeper", password_hash="x", role=UserRole.ADMIN))
    await session.commit()
    payload = _envelope_bytes(
        {"users": [{"id": 9, "username": "x", "password_hash": "h", "role": "viewer"}]}
    )
    r = await _restore(client, payload)
    assert r.status_code == 200, r.text
    assert "unknown table 'users' skipped" in r.json()["warnings"]
    assert await _usernames(session) == {"keeper"}
