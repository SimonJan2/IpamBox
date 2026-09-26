"""V13 — user-authored docs pages + entity attachments."""
import gzip
import json

import pytest
from httpx import AsyncClient, Response
from sqlalchemy import select, text

from app.core.config import get_settings
from app.core.redis import get_redis
from app.core.security import hash_password
from app.models.change_log import ChangeLog
from app.models.user import User, UserRole
from app.services.backup import BACKUP_TABLES

PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
    "1f15c4890000000d49444154789c626001000000ffff03000006000557"
    "bfabd40000000049454e44ae426082"
)


async def _mk_page(client: AsyncClient, title="Runbook", **kw) -> dict:
    r = await client.post(
        "/api/v1/docs-pages", json={"title": title, **kw}
    )
    assert r.status_code == 201, r.text
    return r.json()


async def _mk_site(client: AsyncClient) -> dict:
    r = await client.post("/api/v1/sites", json={"name": "Attach Site"})
    assert r.status_code == 201, r.text
    return r.json()


async def _upload(
    client: AsyncClient,
    entity_type: str,
    entity_id: int,
    payload: bytes = PNG,
    filename: str = "rack.png",
    content_type: str = "image/png",
    **params,
) -> Response:
    return await client.post(
        "/api/v1/attachments",
        params={
            "entity_type": entity_type,
            "entity_id": entity_id,
            "filename": filename,
            **params,
        },
        content=payload,
        headers={"content-type": content_type},
    )


# ---------------------------------------------------------------- docs pages


async def test_docs_pages_crud(client: AsyncClient):
    page = await _mk_page(
        client, "Rack rebuild", body="# Steps\n\n1. pull the PDU", category="runbook"
    )
    assert page["slug"] == "rack-rebuild"
    assert page["category"] == "runbook"
    assert page["created_by"] == "system"
    assert page["created_at"] and page["updated_at"]

    r = await client.get("/api/v1/docs-pages")
    assert r.status_code == 200
    assert any(p["id"] == page["id"] for p in r.json()["items"])

    # slug lookup is the public route's data source
    r = await client.get(f"/api/v1/docs-pages/slug/{page['slug']}")
    assert r.status_code == 200 and r.json()["id"] == page["id"]
    assert (await client.get("/api/v1/docs-pages/slug/nope")).status_code == 404

    # title search (incl. hebrew-final-letter folding path)
    r = await client.get("/api/v1/docs-pages", params={"q": "rebuild"})
    assert any(p["id"] == page["id"] for p in r.json()["items"])

    r = await client.patch(
        f"/api/v1/docs-pages/{page['id']}", json={"body": "v2", "category": "ops"}
    )
    assert r.status_code == 200
    assert r.json()["body"] == "v2" and r.json()["category"] == "ops"
    # slug is a permalink — title/body edits don't move it
    assert r.json()["slug"] == "rack-rebuild"

    r = await client.delete(f"/api/v1/docs-pages/{page['id']}")
    assert r.status_code == 204
    assert (await client.get(f"/api/v1/docs-pages/{page['id']}")).status_code == 404


async def test_docs_pages_slug_uniqueness(client: AsyncClient):
    a = await _mk_page(client, "Overlap")
    b = await _mk_page(client, "Overlap")
    assert a["slug"] == "overlap"
    assert b["slug"] == "overlap-2"

    # explicit slugs are slugified and deduped the same way
    c = await _mk_page(client, "Third", slug="Overlap")
    assert c["slug"] == "overlap-3"
    d = await _mk_page(client, "Fourth", slug="My Custom Slug!")
    assert d["slug"] == "my-custom-slug"

    # "new" is the frontend's editor route — a page can't take it
    e = await _mk_page(client, "New")
    assert e["slug"] == "new-2"


async def test_docs_pages_slug_rename_collision(client: AsyncClient):
    a = await _mk_page(client, "First")
    b = await _mk_page(client, "Second")
    r = await client.patch(
        f"/api/v1/docs-pages/{b['id']}", json={"slug": a["slug"]}
    )
    assert r.status_code == 409
    # renaming to your own slug is a no-op, not a conflict
    r = await client.patch(
        f"/api/v1/docs-pages/{a['id']}", json={"slug": "first"}
    )
    assert r.status_code == 200 and r.json()["slug"] == "first"


async def test_docs_pages_changelog(client: AsyncClient, session):
    page = await _mk_page(client, "Audited", body="v1")
    await client.patch(f"/api/v1/docs-pages/{page['id']}", json={"title": "Audited 2"})
    await client.delete(f"/api/v1/docs-pages/{page['id']}")

    rows = (
        await session.execute(
            select(ChangeLog).where(
                ChangeLog.object_type == "DocsPage",
                ChangeLog.object_id == page["id"],
            )
        )
    ).scalars().all()
    assert [r.action for r in rows] == ["create", "update", "delete"]
    assert all(r.object_repr.startswith("Audited") for r in rows)
    upd = rows[1]
    assert any(c["field"] == "title" for c in upd.changes)


# ---------------------------------------------------------------- attachments


async def test_attachment_upload_list_download(client: AsyncClient):
    site = await _mk_site(client)
    r = await _upload(
        client, "site", site["id"], label="photo of the rack", filename="../evil/../rack.png"
    )
    assert r.status_code == 201, r.text
    att = r.json()
    # filename is path-sanitized, size measured server-side, no blob in metadata
    assert att["filename"] == "rack.png"
    assert att["size"] == len(PNG)
    assert att["label"] == "photo of the rack"
    assert att["uploaded_by"] == "system"
    assert "blob" not in att

    r = await client.get(
        "/api/v1/attachments",
        params={"entity_type": "site", "entity_id": site["id"]},
    )
    assert r.status_code == 200
    assert [a["id"] for a in r.json()] == [att["id"]]
    assert "blob" not in r.json()[0]

    r = await client.get(f"/api/v1/attachments/{att['id']}/download")
    assert r.status_code == 200
    assert r.content == PNG  # byte-identical
    assert r.headers["content-type"] == "image/png"
    assert "attachment" in r.headers["content-disposition"]
    assert "rack.png" in r.headers["content-disposition"]

    # same-name re-upload is allowed (label distinguishes), not upserted
    r = await _upload(client, "site", site["id"], filename="rack.png", label="v2")
    assert r.status_code == 201 and r.json()["id"] != att["id"]


async def test_attachment_validation(client: AsyncClient):
    site = await _mk_site(client)

    # unknown entity_type -> 422
    r = await _upload(client, "nonsense", site["id"])
    assert r.status_code == 422
    r = await client.get(
        "/api/v1/attachments", params={"entity_type": "nonsense", "entity_id": 1}
    )
    assert r.status_code == 422

    # nonexistent target -> 404 (no attachments on ghosts)
    r = await _upload(client, "site", 999999)
    assert r.status_code == 404

    # over the 6 MB cap -> 413
    r = await _upload(client, "site", site["id"], payload=b"x" * (6 * 1024 * 1024 + 1))
    assert r.status_code == 413

    # disallowed type -> 422
    r = await client.post(
        "/api/v1/attachments",
        params={"entity_type": "site", "entity_id": site["id"], "filename": "x.bin"},
        content=b"MZ90",
        headers={"content-type": "application/x-msdownload"},
    )
    assert r.status_code == 422

    # empty file -> 422
    r = await client.post(
        "/api/v1/attachments",
        params={"entity_type": "site", "entity_id": site["id"]},
        content=b"",
        headers={"content-type": "image/png"},
    )
    assert r.status_code == 422

    r = await client.get("/api/v1/attachments/999999/download")
    assert r.status_code == 404


async def test_attachment_delete_and_changelog(client: AsyncClient, session):
    site = await _mk_site(client)
    att = (await _upload(client, "site", site["id"])).json()
    assert att["uploaded_by"] == "system"

    rows = (
        await session.execute(
            select(ChangeLog).where(ChangeLog.object_type == "Attachment")
        )
    ).scalars().all()
    create = [r for r in rows if r.action == "create"][0]
    # metadata is audited; the blob field never reaches a diff
    assert create.object_repr == f"rack.png on site#{site['id']}"
    assert all(c["field"] != "blob" for c in create.changes)
    assert any(c["field"] == "size" and c["after"] == len(PNG) for c in create.changes)

    r = await client.delete(f"/api/v1/attachments/{att['id']}")
    assert r.status_code == 204
    assert (
        await client.get(f"/api/v1/attachments/{att['id']}/download")
    ).status_code == 404


async def test_attachment_cascades_on_entity_delete(client: AsyncClient, session):
    site = await _mk_site(client)
    att = (await _upload(client, "site", site["id"])).json()

    r = await client.delete(f"/api/v1/sites/{site['id']}")
    assert r.status_code == 204

    # swept in the same transaction — the row is gone, not orphaned
    assert (await session.execute(text("SELECT count(*) FROM attachments"))).scalar() == 0
    # and the sweep is audited like an explicit delete
    rows = (
        await session.execute(
            select(ChangeLog).where(
                ChangeLog.object_type == "Attachment",
                ChangeLog.object_id == att["id"],
            )
        )
    ).scalars().all()
    assert any(r.action == "delete" and "(cascade)" in r.object_repr for r in rows)


async def test_attachment_cascade_via_bulk_delete(client: AsyncClient, session):
    """Bulk ORM deletes (addresses bulk action) sweep attachments too."""
    vrf_id = next(
        v["id"] for v in (await client.get("/api/v1/vrfs")).json() if v["name"] == "Global"
    )
    prefix = (
        await client.post(
            "/api/v1/prefixes", json={"prefix": "10.99.0.0/24", "vrf_id": vrf_id}
        )
    ).json()
    addr = (
        await client.post(
            "/api/v1/addresses",
            json={"address": "10.99.0.5", "prefix_id": prefix["id"]},
        )
    ).json()
    await _upload(client, "ip_address", addr["id"])

    r = await client.post(
        "/api/v1/addresses/bulk", json={"action": "delete", "ids": [addr["id"]]}
    )
    assert r.status_code == 200
    assert (await session.execute(text("SELECT count(*) FROM attachments"))).scalar() == 0


# ------------------------------------------------------------------ RBAC


@pytest.fixture
async def auth_on():
    """Turn auth on for a test, restore insecure mode after."""
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


async def test_rbac_docs_pages_and_attachments(client: AsyncClient, auth_on, session):
    admin = User(
        username="admin", password_hash=hash_password("pw-strong-1"), role=UserRole.ADMIN
    )
    viewer = User(
        username="v", password_hash=hash_password("pw-strong-1"), role=UserRole.VIEWER
    )
    contrib = User(
        username="c", password_hash=hash_password("pw-strong-1"), role=UserRole.CONTRIBUTOR
    )
    session.add_all([admin, viewer, contrib])
    await session.commit()

    await client.post(
        "/api/v1/auth/login", json={"username": "v", "password": "pw-strong-1"}
    )
    site = await client.post("/api/v1/sites", json={"name": "x"})
    assert site.status_code == 403
    assert (await client.post("/api/v1/docs-pages", json={"title": "t"})).status_code == 403
    assert (await _upload(client, "site", 1)).status_code == 403
    # reads still work for viewers
    assert (await client.get("/api/v1/docs-pages")).status_code == 200
    assert (
        await client.get(
            "/api/v1/attachments", params={"entity_type": "site", "entity_id": 1}
        )
    ).status_code == 200

    await client.post(
        "/api/v1/auth/login", json={"username": "c", "password": "pw-strong-1"}
    )
    page = await _mk_page(client, "contrib page")
    att = (
        await _upload(client, "site", 1)
    )  # 404s (no such site) — perm gate precedes lookup
    assert att.status_code in (404,)
    # contributor can write but not delete
    assert (await client.delete(f"/api/v1/docs-pages/{page['id']}")).status_code == 403

    await client.post(
        "/api/v1/auth/login", json={"username": "admin", "password": "pw-strong-1"}
    )
    site = await _mk_site(client)
    att = (await _upload(client, "site", site["id"])).json()
    assert (await client.delete(f"/api/v1/attachments/{att['id']}")).status_code == 204
    assert (await client.delete(f"/api/v1/docs-pages/{page['id']}")).status_code == 204


# ------------------------------------------------------------------ backup


async def test_backup_restore_roundtrip(client: AsyncClient, session):
    site = await _mk_site(client)
    page = await _mk_page(client, "Restore me", body="**bold** body", category="ops")
    att = (await _upload(client, "site", site["id"], label="pic")).json()

    payload = (
        await client.get("/api/v1/backup", params={"include_users": False})
    ).content
    envelope = json.loads(gzip.decompress(payload))
    assert envelope["tables"]["docs_pages"][0]["title"] == "Restore me"
    assert envelope["tables"]["attachments"][0]["filename"] == "rack.png"

    # wipe everything and restore — the same path the restore endpoint takes
    names = ", ".join(spec.name for spec in BACKUP_TABLES)
    await session.execute(text(f"TRUNCATE {names} RESTART IDENTITY CASCADE"))
    await session.commit()

    r = await client.post(
        "/api/v1/backup/restore",
        content=payload,
        headers={"content-type": "application/gzip"},
        params={"name": "t.json.gz"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["restored"]["docs_pages"] == 1
    assert r.json()["restored"]["attachments"] == 1

    p = (await client.get(f"/api/v1/docs-pages/slug/{page['slug']}")).json()
    assert p["body"] == "**bold** body" and p["category"] == "ops"
    assert p["id"] == page["id"]  # ids are preserved — refs still valid

    # blob survived the json.gz round-trip byte-identical
    r = await client.get(f"/api/v1/attachments/{att['id']}/download")
    assert r.status_code == 200 and r.content == PNG
