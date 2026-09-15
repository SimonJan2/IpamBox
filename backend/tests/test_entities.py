"""CRUD smoke tests for the workbook-entity routers (M4)."""


async def test_circuit_crud(client):
    r = await client.post(
        "/api/v1/circuits",
        json={
            "site_name": "Alenbi",
            "site_code": "ALNB",
            "bezeq_circuit_id": "828328469",
            "line_type": "ipvpn",
            "status": "פעיל",
        },
    )
    assert r.status_code == 201, r.text
    cid = r.json()["id"]

    r = await client.get("/api/v1/circuits", params={"q": "828328"})
    assert r.status_code == 200 and len(r.json()) == 1

    r = await client.get("/api/v1/circuits", params={"q": "פעיל"})
    assert any(c["id"] == cid for c in r.json())

    r = await client.patch(f"/api/v1/circuits/{cid}", json={"node": "N5"})
    assert r.json()["node"] == "N5"

    r = await client.delete(f"/api/v1/circuits/{cid}")
    assert r.status_code == 204
    assert (await client.get(f"/api/v1/circuits/{cid}")).status_code == 404


async def test_certificate_crud_and_expiry(client):
    r = await client.post(
        "/api/v1/certificates",
        json={
            "platform": "F5",
            "server_name": "vs-web",
            "cert_name": "*.example.com",
            "expires_on": "2027-01-31",
        },
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["expires_on"] == "2027-01-31"
    cid = body["id"]

    r = await client.get("/api/v1/certificates", params={"q": "example.com"})
    assert any(c["id"] == cid for c in r.json())


async def test_asset_and_service_crud(client):
    r = await client.post(
        "/api/v1/assets",
        json={
            "kind": "hardware",
            "vendor": "Cisco",
            "model": "ISR4331",
            "serial_number": "FTX1234ABCD",
        },
    )
    assert r.status_code == 201, r.text
    aid = r.json()["id"]

    r = await client.get("/api/v1/assets", params={"q": "FTX1234"})
    assert any(a["id"] == aid for a in r.json())

    r = await client.post(
        "/api/v1/services",
        json={"name": "DNS", "beneficiary": "infra", "site_code": "ALNB"},
    )
    assert r.status_code == 201, r.text
    sid = r.json()["id"]

    r = await client.get("/api/v1/services", params={"q": "dns"})
    assert any(s["id"] == sid for s in r.json())


async def test_site_extended_fields(client):
    r = await client.post(
        "/api/v1/sites",
        json={
            "name": "נתב״ג מרכזי",
            "code": "NTBG",
            "site_number": 77,
            "size": "גדול",
            "is_active": False,
            "address": "רחוב הדוגמה 1",
        },
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["code"] == "NTBG"
    assert body["site_number"] == 77
    assert body["is_active"] is False
    # hebrew name -> non-empty, hebrew-preserving slug
    assert body["slug"] and body["slug"] != "site"

    r = await client.patch(
        f"/api/v1/sites/{body['id']}", json={"is_active": True}
    )
    assert r.json()["is_active"] is True
