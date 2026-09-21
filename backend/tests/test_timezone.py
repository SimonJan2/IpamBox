"""W7: every serialized timestamp carries an explicit UTC offset.

Before timestamptz, Pydantic emitted '2026-09-19T12:00:00' — browsers parse
offset-less ISO as LOCAL time, so a scan finished 10 s ago rendered as
'hours ago' in UTC+3. Columns are timestamptz now and every write is aware
UTC. The cert-expiry boundary also uses UTC 'today', not the server's
local date.
"""
from datetime import datetime, timedelta, timezone

from app.models.certificate import Certificate
from app.models.scan_job import ScanJob, ScanStatus


async def test_serialized_timestamps_carry_utc_offset(client, session):
    r = await client.post("/api/v1/sites", json={"name": "tz"})
    assert r.status_code == 201
    created = r.json()["created_at"]
    # an offset-less stamp would parse naive; timestamptz round-trips aware
    assert datetime.fromisoformat(created).tzinfo is not None

    session.add(
        ScanJob(
            cidr="10.99.0.0/30",
            status=ScanStatus.COMPLETED,
            finished_at=datetime.now(timezone.utc),
        )
    )
    await session.commit()
    rows = (await client.get("/api/v1/scans")).json()
    fin = next(x for x in rows if x["cidr"] == "10.99.0.0/30")["finished_at"]
    assert datetime.fromisoformat(fin).tzinfo is not None


async def test_cert_expiring_boundary_uses_utc_today(client, session):
    """expires_on <= UTC today+30 counts; +31 doesn't — regardless of the
    server's local timezone (previously date.today() shifted the boundary)."""
    today_utc = datetime.now(timezone.utc).date()
    session.add(Certificate(cert_name="in30", expires_on=today_utc + timedelta(days=30)))
    session.add(Certificate(cert_name="in31", expires_on=today_utc + timedelta(days=31)))
    session.add(Certificate(cert_name="past", expires_on=today_utc - timedelta(days=1)))
    await session.commit()
    stats = (await client.get("/api/v1/dashboard/stats")).json()
    assert stats["certs_expiring_30d"] == 2  # in30 + past, not in31


async def test_aware_write_roundtrips_through_timestamptz(session):
    """A datetime written aware comes back aware — no naive/aware mixing."""
    from app.models.ip_address import IPAddress, IPStatus
    from app.models.prefix import Prefix
    from sqlalchemy import select

    p = Prefix(prefix="10.98.0.0/24", vrf_id=1)  # conftest seeds Global vrf
    session.add(p)
    await session.flush()
    a = IPAddress(
        address="10.98.0.5",
        address_int=10 * 2**24 + 5,
        prefix_id=p.id,
        vrf_id=1,
        status=IPStatus.ACTIVE,
        last_seen=datetime.now(timezone.utc),
    )
    session.add(a)
    await session.commit()
    got = (
        await session.execute(select(IPAddress).where(IPAddress.id == a.id))
    ).scalar_one()
    assert got.last_seen.tzinfo is not None
