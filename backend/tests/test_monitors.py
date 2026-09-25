"""V7 monitoring + notification channels.

Covers target CRUD/RBAC, the exactly-one-ref rule, the check state machine
(up->down->up with down_after hysteresis, silent steady state, changelog
bypass), channel CRUD + the v6 secrets contract, webhook dispatch via a
monkeypatched transport, the tick's one-job batching, and the emit wiring
for cert/scan/mac_mismatch events.
"""
from datetime import date, datetime, timedelta, timezone

import pytest
from sqlalchemy import func, select

from app.core.config import get_settings
from app.core.security import hash_password
from app.models.certificate import Certificate
from app.models.change_log import ChangeLog
from app.models.monitoring import (
    ChannelKind,
    MonitorState,
    MonitorTarget,
    NotificationChannel,
    NotificationLog,
)
from app.models.scan_job import ScanJob, ScanStatus
from app.models.user import User, UserRole
from app.services import notify
from app.services.secrets import decrypt_str, encrypt_str

PASSWORD = "mon-test-pw1"


@pytest.fixture
def key(monkeypatch):
    """Provision the master key so channel secrets can encrypt."""
    s = get_settings()
    monkeypatch.setattr(s, "ipambox_secret_key", "test-master-key")
    monkeypatch.setattr(s, "ipambox_secret_key_file", "")
    return s


@pytest.fixture
async def auth_on():
    """Turn auth on for a test; restore insecure mode + flush session keys."""
    from app.core.redis import get_redis

    settings = get_settings()
    settings.ipambox_allow_insecure = False
    r = get_redis()
    try:
        yield
    finally:
        settings.ipambox_allow_insecure = True
        for pattern in ("ipam:session:*", "ipam:loginfails:*", "ipam:lockout:*"):
            async for k in r.scan_iter(pattern):
                await r.delete(k)
        await r.aclose()


async def _mkuser(session, username, role):
    u = User(username=username, password_hash=hash_password(PASSWORD), role=role)
    session.add(u)
    await session.commit()
    return u


async def _login(client, username):
    r = await client.post(
        "/api/v1/auth/login", json={"username": username, "password": PASSWORD}
    )
    assert r.status_code == 200, r.text


class _FakeRedis:
    """In-memory get/set/publish stand-in for the worker's redis client."""

    def __init__(self):
        self.store: dict[str, str] = {}

    async def get(self, k):
        return self.store.get(k)

    async def set(self, k, v, ex=None):
        self.store[k] = v

    async def publish(self, *a):
        return 1

    async def aclose(self):
        pass


class _FakeArqPool:
    """Records enqueue_job calls — never dispatches."""

    def __init__(self):
        self.calls = []

    async def enqueue_job(self, fn, *args, **kw):
        self.calls.append((fn, args, kw))
        return _Job()


class _Job:
    job_id = "fake-arq-job"


async def _mk_prefix_and_addr(client, addr="10.60.0.5", cidr="10.60.0.0/24"):
    vrfs = (await client.get("/api/v1/vrfs")).json()
    vrf_id = vrfs[0]["id"]
    p = (
        await client.post(
            "/api/v1/prefixes", json={"prefix": cidr, "vrf_id": vrf_id}
        )
    ).json()
    a = await client.post(
        "/api/v1/addresses",
        json={
            "prefix_id": p["id"],
            "vrf_id": vrf_id,
            "address": addr,
            "status": "active",
        },
    )
    assert a.status_code == 201, a.text
    return p["id"], a.json()["id"]


async def _mk_device(client, name="web-01") -> int:
    r = await client.post("/api/v1/devices", json={"name": name})
    assert r.status_code == 201, r.text
    return r.json()["id"]


# -------------------------------------------------------------------- CRUD


async def test_target_crud_address(client):
    _, addr_id = await _mk_prefix_and_addr(client)
    r = await client.post(
        "/api/v1/monitor-targets",
        json={"address_id": addr_id, "kind": "tcp", "port": 443},
    )
    assert r.status_code == 201, r.text
    t = r.json()
    assert t["kind"] == "tcp" and t["port"] == 443
    assert t["state"] == "unknown"
    assert t["resolved_ip"] == "10.60.0.5"
    assert "10.60.0.5" in t["target_label"]

    tid = t["id"]
    assert (await client.get(f"/api/v1/monitor-targets/{tid}")).status_code == 200
    r = await client.patch(f"/api/v1/monitor-targets/{tid}", json={"notes": "keep"})
    assert r.status_code == 200 and r.json()["notes"] == "keep"
    r = await client.get("/api/v1/monitor-targets", params={"address_id": addr_id})
    assert r.json()["total"] == 1
    assert (await client.delete(f"/api/v1/monitor-targets/{tid}")).status_code == 204
    assert (await client.get(f"/api/v1/monitor-targets/{tid}")).status_code == 404


async def test_target_exactly_one_ref(client):
    _, addr_id = await _mk_prefix_and_addr(client)
    dev_id = await _mk_device(client)
    assert (
        await client.post("/api/v1/monitor-targets", json={"kind": "ping"})
    ).status_code == 422
    assert (
        await client.post(
            "/api/v1/monitor-targets",
            json={"device_id": dev_id, "address_id": addr_id, "kind": "ping"},
        )
    ).status_code == 422


async def test_target_kind_field_rules(client):
    _, addr_id = await _mk_prefix_and_addr(client)
    # tcp/http need a port; ping carries neither port nor http_* fields
    assert (
        await client.post(
            "/api/v1/monitor-targets",
            json={"address_id": addr_id, "kind": "tcp"},
        )
    ).status_code == 422
    assert (
        await client.post(
            "/api/v1/monitor-targets",
            json={"address_id": addr_id, "kind": "ping", "port": 22},
        )
    ).status_code == 422
    assert (
        await client.post(
            "/api/v1/monitor-targets",
            json={"address_id": addr_id, "kind": "ping", "http_expect": "ok"},
        )
    ).status_code == 422
    # status: must be a 3-digit 1xx-5xx
    assert (
        await client.post(
            "/api/v1/monitor-targets",
            json={
                "address_id": addr_id, "kind": "http", "port": 80,
                "http_expect": "status:9999",
            },
        )
    ).status_code == 422
    for expect in ("status:200", "ok"):
        r = await client.post(
            "/api/v1/monitor-targets",
            json={
                "address_id": addr_id, "kind": "http", "port": 80,
                "http_expect": expect,
            },
        )
        assert r.status_code == 201, r.text


async def test_target_bad_refs_404(client):
    r = await client.post(
        "/api/v1/monitor-targets", json={"device_id": 999999, "kind": "ping"}
    )
    assert r.status_code == 404


async def test_target_summary_counts(client):
    _, addr_id = await _mk_prefix_and_addr(client)
    await client.post(
        "/api/v1/monitor-targets", json={"address_id": addr_id, "kind": "ping"}
    )
    r = await client.get("/api/v1/monitor-targets/summary")
    assert r.status_code == 200
    body = r.json()
    assert body["unknown"] == 1 and body["up"] == 0 and body["down"] == 0
    assert body["due"] == 1  # never checked -> due


async def test_targets_rbac(client, session, auth_on):
    """Viewer reads targets but can't write/check/delete them."""
    await _mkuser(session, "a", UserRole.ADMIN)
    await _login(client, "a")
    _, addr_id = await _mk_prefix_and_addr(client)
    tid = (
        await client.post(
            "/api/v1/monitor-targets",
            json={"address_id": addr_id, "kind": "ping"},
        )
    ).json()["id"]

    await _mkuser(session, "v", UserRole.VIEWER)
    await _login(client, "v")
    assert (await client.get("/api/v1/monitor-targets")).status_code == 200
    assert (
        await client.post(
            "/api/v1/monitor-targets",
            json={"address_id": addr_id, "kind": "ping"},
        )
    ).status_code == 403
    assert (
        await client.patch(f"/api/v1/monitor-targets/{tid}", json={"enabled": False})
    ).status_code == 403
    assert (
        await client.post(f"/api/v1/monitor-targets/{tid}/check")
    ).status_code == 403
    assert (await client.delete(f"/api/v1/monitor-targets/{tid}")).status_code == 403


# -------------------------------------------------------------- state machine


async def test_check_now_transitions_and_emits(client, session, monkeypatch):
    """check-now drives the same state machine the sweep does; failures
    accrue until down_after, then the flip emits exactly once."""
    from app.worker import monitors as wmon

    _, addr_id = await _mk_prefix_and_addr(client)
    tid = (
        await client.post(
            "/api/v1/monitor-targets",
            json={
                "address_id": addr_id, "kind": "tcp", "port": 443,
                "down_after": 2,
            },
        )
    ).json()["id"]

    result = {"ok": True, "err": None}

    async def fake_check(t, ip, **kw):
        return result["ok"], result["err"]

    emitted = []

    async def fake_emit(et, summary, payload=None):
        emitted.append(et)
        return 0

    monkeypatch.setattr(wmon, "check_target", fake_check)
    monkeypatch.setattr(notify, "emit", fake_emit)

    # first success: unknown -> up (silent — not a recovery)
    r = await client.post(f"/api/v1/monitor-targets/{tid}/check")
    assert r.status_code == 200, r.text
    assert r.json()["state"] == "up"
    assert emitted == []

    # one failure under down_after=2: still up, no event
    result.update(ok=False, err="refused")
    r = await client.post(f"/api/v1/monitor-targets/{tid}/check")
    assert r.json()["state"] == "up"
    assert r.json()["consecutive_failures"] == 1
    assert emitted == []

    # second failure hits the threshold -> down + exactly one event
    r = await client.post(f"/api/v1/monitor-targets/{tid}/check")
    body = r.json()
    assert body["state"] == "down"
    assert body["consecutive_failures"] == 2
    assert body["last_error"] == "refused"
    assert emitted == ["monitor.down"]

    # recovery: down -> up, one event
    result.update(ok=True, err=None)
    r = await client.post(f"/api/v1/monitor-targets/{tid}/check")
    assert r.json()["state"] == "up"
    assert r.json()["consecutive_failures"] == 0
    assert emitted == ["monitor.down", "monitor.up"]


async def test_state_writes_bypass_changelog(client, session, monkeypatch):
    """Observed churn (state/failures/last_*) must not touch the audit log."""
    from app.worker import monitors as wmon

    _, addr_id = await _mk_prefix_and_addr(client)
    tid = (
        await client.post(
            "/api/v1/monitor-targets",
            json={"address_id": addr_id, "kind": "tcp", "port": 443},
        )
    ).json()["id"]

    async def fake_check(t, ip, **kw):
        return False, "down"

    async def fake_emit(*a, **k):
        return 0

    monkeypatch.setattr(wmon, "check_target", fake_check)
    monkeypatch.setattr(notify, "emit", fake_emit)

    # clear the create entry so only check-driven writes are counted
    await session.execute(
        ChangeLog.__table__.delete().where(
            ChangeLog.object_type == "MonitorTarget"
        )
    )
    await session.commit()

    for _ in range(3):
        await client.post(f"/api/v1/monitor-targets/{tid}/check")
    n = await session.scalar(
        select(func.count(ChangeLog.id)).where(
            ChangeLog.object_type == "MonitorTarget"
        )
    )
    assert n == 0


# ----------------------------------------------------------------- the tick


async def test_tick_batches_one_job(client, session, sf, monkeypatch):
    """All due targets ride a single run_monitor_sweep enqueue — the
    max_jobs=4 budget stays for scans."""
    from app.worker import monitors as wmon

    _, addr_id = await _mk_prefix_and_addr(client)
    _, addr2 = await _mk_prefix_and_addr(client, "10.61.0.6", "10.61.0.0/24")
    for aid in (addr_id, addr2):
        await client.post(
            "/api/v1/monitor-targets", json={"address_id": aid, "kind": "ping"}
        )
    pool = _FakeArqPool()
    monkeypatch.setattr(wmon, "SessionLocal", sf)

    async def _pool():
        return pool

    monkeypatch.setattr(wmon, "get_arq_pool", _pool)

    out = await wmon.monitor_tick({})
    assert out["due"] == 2 and out["enqueued"] is True
    assert len(pool.calls) == 1
    fn, args, kw = pool.calls[0]
    assert fn == "run_monitor_sweep"
    assert len(args[0]) == 2
    assert kw.get("_job_id") == wmon.SWEEP_JOB_ID


async def test_tick_skips_disabled_and_respects_kill_switch(
    client, session, sf, monkeypatch
):
    from app.worker import monitors as wmon

    _, addr_id = await _mk_prefix_and_addr(client)
    r = await client.post(
        "/api/v1/monitor-targets",
        json={"address_id": addr_id, "kind": "ping", "enabled": False},
    )
    tid = r.json()["id"]
    pool = _FakeArqPool()
    monkeypatch.setattr(wmon, "SessionLocal", sf)

    async def _pool():
        return pool

    monkeypatch.setattr(wmon, "get_arq_pool", _pool)
    out = await wmon.monitor_tick({})
    assert out["due"] == 0 and pool.calls == []

    # monitoring_enabled=0 -> the tick is a no-op even with due targets
    await client.patch(f"/api/v1/monitor-targets/{tid}", json={"enabled": True})
    r = await client.patch("/api/v1/settings", json={"monitoring_enabled": False})
    assert r.status_code == 200
    out = await wmon.monitor_tick({})
    assert out["skipped"] == "monitoring disabled"
    assert pool.calls == []


async def test_sweep_writes_state_and_emits(client, session, sf, monkeypatch):
    """run_monitor_sweep checks each id, writes via bulk update, emits on
    transitions only."""
    from app.worker import monitors as wmon

    _, addr_id = await _mk_prefix_and_addr(client)
    tid = (
        await client.post(
            "/api/v1/monitor-targets",
            json={
                "address_id": addr_id, "kind": "tcp", "port": 443,
                "down_after": 1,
            },
        )
    ).json()["id"]
    monkeypatch.setattr(wmon, "SessionLocal", sf)
    emitted = []

    async def fake_emit(et, summary, payload=None):
        emitted.append(et)
        return 0

    async def down_check(t, ip, **kw):
        return False, "conn refused"

    monkeypatch.setattr(wmon, "check_target", down_check)
    monkeypatch.setattr(wmon.notify, "emit", fake_emit)

    out = await wmon.run_monitor_sweep({}, [tid])
    assert out == {"checked": 1, "events": 1}
    assert emitted == ["monitor.down"]
    session.expire_all()
    t = await session.get(MonitorTarget, tid)
    assert t.state == MonitorState.DOWN and t.consecutive_failures == 1


# ------------------------------------------------------------------ channels


async def test_channel_crud_secret_contract(client, session, key):
    """secret_enc never leaves the API; config carries non-secret fields;
    secret_set reflects the stored blob."""
    r = await client.post(
        "/api/v1/notification-channels",
        json={
            "name": "hook",
            "kind": "webhook",
            "secret": "https://example.com/hook?token=abc123",
        },
    )
    assert r.status_code == 201, r.text
    ch = r.json()
    assert ch["secret_set"] is True
    assert ch["config"] == {"method": "POST"}
    assert "abc123" not in r.text
    assert "secret_enc" not in r.text

    cid = ch["id"]
    # stored blob decrypts to exactly what was submitted
    row = await session.get(NotificationChannel, cid)
    assert row.secret_enc.startswith("v1:")
    assert decrypt_str(row.secret_enc) == "https://example.com/hook?token=abc123"

    # GET never carries the blob either
    r = await client.get(f"/api/v1/notification-channels/{cid}")
    assert "abc123" not in r.text and "secret_enc" not in r.text

    # patch: rename without touching the secret
    r = await client.patch(
        f"/api/v1/notification-channels/{cid}", json={"name": "hook2"}
    )
    assert r.status_code == 200 and r.json()["secret_set"] is True


async def test_channel_kind_validation(client, key):
    # webhook without URL -> 422
    assert (
        await client.post(
            "/api/v1/notification-channels",
            json={"name": "x", "kind": "webhook"},
        )
    ).status_code == 422
    # telegram without chat_id -> 422
    assert (
        await client.post(
            "/api/v1/notification-channels",
            json={"name": "x", "kind": "telegram", "secret": "tok"},
        )
    ).status_code == 422
    # smtp needs host/from/to
    assert (
        await client.post(
            "/api/v1/notification-channels",
            json={"name": "x", "kind": "smtp", "smtp_host": "mail"},
        )
    ).status_code == 422


async def test_channels_viewer_cannot_manage(client, session, auth_on, key):
    """Channels are SYSTEM_ADMIN — a viewer can't even list them."""
    await _mkuser(session, "a", UserRole.ADMIN)
    await _mkuser(session, "v", UserRole.VIEWER)
    await _login(client, "v")
    assert (await client.get("/api/v1/notification-channels")).status_code == 403
    assert (
        await client.post(
            "/api/v1/notification-channels",
            json={"name": "x", "kind": "webhook", "secret": "https://x.test/"},
        )
    ).status_code == 403
    assert (await client.get("/api/v1/notification-log")).status_code == 403
    # operator (backup+delete) still isn't admin
    await _mkuser(session, "op", UserRole.OPERATOR)
    await _login(client, "op")
    assert (await client.get("/api/v1/notification-channels")).status_code == 403
    # admin can
    await _login(client, "a")
    assert (await client.get("/api/v1/notification-channels")).status_code == 200


async def test_webhook_dispatch_posts_expected_json(
    client, session, sf, key, monkeypatch
):
    """emit() posts {event, summary, payload, ts} to the decrypted URL and
    writes one notification_log row per attempt."""
    ch = NotificationChannel(
        name="hook",
        kind=ChannelKind.WEBHOOK,
        config={"method": "POST"},
        secret_enc=encrypt_str("https://hook.test/x"),
        enabled=True,
    )
    session.add(ch)
    await session.commit()

    posted = {}

    async def fake_post(url, json, method="POST"):
        posted["url"] = url
        posted["json"] = json
        posted["method"] = method

    monkeypatch.setattr(notify, "_post_json", fake_post)
    monkeypatch.setattr(notify, "SessionLocal", sf)
    n = await notify.emit("monitor.down", "web-01 is DOWN", {"x": 1})
    assert n == 1
    assert posted["url"] == "https://hook.test/x"
    assert posted["json"]["event"] == "monitor.down"
    assert posted["json"]["payload"] == {"x": 1}
    assert "ts" in posted["json"]
    assert posted["method"] == "POST"

    logs = (
        await session.execute(
            select(NotificationLog).where(NotificationLog.channel_id == ch.id)
        )
    ).scalars().all()
    assert len(logs) == 1 and logs[0].ok is True


async def test_webhook_honors_configured_method(session, sf, key, monkeypatch):
    """A channel created with webhook_method=PUT must actually deliver
    via PUT, not silently fall back to POST (config.method was ignored
    until this regression was caught)."""
    ch = NotificationChannel(
        name="hook-put",
        kind=ChannelKind.WEBHOOK,
        config={"method": "PUT"},
        secret_enc=encrypt_str("https://hook.test/put"),
        enabled=True,
    )
    session.add(ch)
    await session.commit()

    seen = {}

    async def fake_post(url, json, method="POST"):
        seen["method"] = method

    monkeypatch.setattr(notify, "_post_json", fake_post)
    monkeypatch.setattr(notify, "SessionLocal", sf)
    await notify.emit("monitor.down", "x is DOWN")
    assert seen["method"] == "PUT"


class _FakeSMTP:
    """Records how it was constructed/used; smtplib.SMTP/SMTP_SSL stand-in."""

    instances: list = []

    def __init__(self, host, port, timeout=None):
        self.host, self.port, self.started_tls, self.logged_in = (
            host, port, False, None,
        )
        _FakeSMTP.instances.append(self)

    def starttls(self):
        self.started_tls = True

    def login(self, user, password):
        self.logged_in = (user, password)

    def send_message(self, msg):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_smtp_uses_implicit_tls_on_465(monkeypatch):
    """Port 465 is implicit TLS — plain smtplib.SMTP can't complete a
    handshake against it (proven live: it just times out), so 465 must
    route through SMTP_SSL, not SMTP+starttls()."""
    import smtplib

    from app.services import notify as notify_mod

    _FakeSMTP.instances = []
    monkeypatch.setattr(smtplib, "SMTP_SSL", _FakeSMTP)
    monkeypatch.setattr(smtplib, "SMTP", _FakeSMTP)
    monkeypatch.setattr(notify_mod, "_secret", lambda ch: "pw")

    ch = NotificationChannel(
        name="smtp-465", kind=ChannelKind.SMTP,
        config={
            "host": "mail.test", "port": 465, "from": "a@test",
            "to": ["b@test"], "starttls": False, "username": "a@test",
        },
    )
    notify_mod._smtp_send(ch, "subj", "body")
    assert len(_FakeSMTP.instances) == 1
    inst = _FakeSMTP.instances[0]
    assert inst.port == 465
    assert inst.started_tls is False  # SMTP_SSL is already encrypted
    assert inst.logged_in == ("a@test", "pw")


def test_smtp_uses_starttls_on_587(monkeypatch):
    import smtplib

    from app.services import notify as notify_mod

    _FakeSMTP.instances = []
    monkeypatch.setattr(smtplib, "SMTP_SSL", _FakeSMTP)
    monkeypatch.setattr(smtplib, "SMTP", _FakeSMTP)
    monkeypatch.setattr(notify_mod, "_secret", lambda ch: "pw")

    ch = NotificationChannel(
        name="smtp-587", kind=ChannelKind.SMTP,
        config={
            "host": "mail.test", "from": "a@test", "to": ["b@test"],
            "starttls": True, "username": "a@test",
        },
    )
    notify_mod._smtp_send(ch, "subj", "body")
    inst = _FakeSMTP.instances[0]
    assert inst.port == 587
    assert inst.started_tls is True


async def test_notify_failure_is_log_row_not_raise(
    client, session, sf, key, monkeypatch
):
    ch = NotificationChannel(
        name="bad",
        kind=ChannelKind.WEBHOOK,
        config={},
        secret_enc=encrypt_str("https://down.test/"),
        enabled=True,
    )
    session.add(ch)
    await session.commit()

    async def boom(url, json, method="POST"):
        raise RuntimeError("connection refused")

    monkeypatch.setattr(notify, "_post_json", boom)
    monkeypatch.setattr(notify, "SessionLocal", sf)
    n = await notify.emit("monitor.down", "x is DOWN")
    assert n == 1  # attempted even though it failed
    log = (await session.execute(select(NotificationLog))).scalars().all()
    assert len(log) == 1 and log[0].ok is False
    assert "connection refused" in log[0].error


async def test_channel_test_endpoint(client, session, sf, key, monkeypatch):
    """POST /{id}/test exercises the stored secret and reports ok/err —
    it never propagates delivery failures."""
    r = await client.post(
        "/api/v1/notification-channels",
        json={
            "name": "t", "kind": "webhook",
            "secret": "https://t.test/hook",
        },
    )
    cid = r.json()["id"]

    async def ok_post(url, json, method="POST"):
        return None

    monkeypatch.setattr(notify, "_post_json", ok_post)
    r = await client.post(f"/api/v1/notification-channels/{cid}/test")
    assert r.status_code == 200 and r.json() == {"ok": True, "error": None}

    async def bad_post(url, json, method="POST"):
        raise RuntimeError("nope")

    monkeypatch.setattr(notify, "_post_json", bad_post)
    r = await client.post(f"/api/v1/notification-channels/{cid}/test")
    assert r.status_code == 200
    assert r.json()["ok"] is False and "nope" in r.json()["error"]


async def test_channels_require_secret_key(client, monkeypatch):
    """Without the master key, a secret-bearing channel create 503s through
    the SecretsNotConfigured handler — no traceback, no secret."""
    s = get_settings()
    monkeypatch.setattr(s, "ipambox_secret_key", "")
    monkeypatch.setattr(s, "ipambox_secret_key_file", "")
    r = await client.post(
        "/api/v1/notification-channels",
        json={"name": "x", "kind": "webhook", "secret": "https://x.test/"},
    )
    assert r.status_code == 503
    assert "IPAMBOX_SECRET_KEY" in r.json()["detail"]
    assert "x.test" not in r.text


# --------------------------------------------------------------- emit points


async def test_cert_warning_emits_once_per_day(client, session, sf, monkeypatch):
    """_cert_warnings emits cert.expiring once per cert per day — the
    Redis day-stamp suppresses re-fires on later ticks."""
    from app.worker import worker

    cert = Certificate(
        cert_name="ca.crt", expires_on=date.today() + timedelta(days=10)
    )
    session.add(cert)
    await session.commit()

    emitted = []

    async def fake_emit(et, summary, payload=None):
        emitted.append((et, summary))
        return 0

    monkeypatch.setattr(worker.notify, "emit", fake_emit)
    monkeypatch.setattr(worker, "SessionLocal", sf)
    fake = _FakeRedis()
    monkeypatch.setattr(worker, "get_redis", lambda: fake)

    now = datetime.now(timezone.utc)
    assert await worker._cert_warnings(now) == 1
    assert await worker._cert_warnings(now) == 0  # stamped — no re-fire
    assert emitted[0][0] == "cert.expiring"
    assert "ca.crt" in emitted[0][1]


async def test_scan_failed_emits(client, session, sf, monkeypatch):
    """A scan that raises mid-job flips to FAILED and emits scan.failed."""
    from app.worker import worker

    job = ScanJob(cidr="10.70.0.0/24", status=ScanStatus.QUEUED)
    session.add(job)
    await session.commit()

    fake = _FakeRedis()
    monkeypatch.setattr(worker, "SessionLocal", sf)
    monkeypatch.setattr(worker, "get_redis", lambda: fake)
    emitted = []

    async def fake_emit(et, summary, payload=None):
        emitted.append(et)
        return 0

    async def explode(*a, **k):
        raise RuntimeError("scanner blew up")

    monkeypatch.setattr(worker.notify, "emit", fake_emit)
    monkeypatch.setattr(worker, "scan_cidr", explode)
    out = await worker.run_scan({}, job.id)
    assert "error" in out
    await session.refresh(job)
    assert job.status == ScanStatus.FAILED
    assert emitted == ["scan.failed"]


async def test_mac_mismatch_emits_once(client, session, sf, monkeypatch):
    """reconcile raising a mac_mismatch flag emits once; a follow-up scan
    that leaves the flag untouched (or clears it) emits nothing new."""
    import ipaddress

    from app.worker import worker
    from app.worker.scanner import HostResult

    vrf_id = (await client.get("/api/v1/vrfs")).json()[0]["id"]
    p = (
        await client.post(
            "/api/v1/prefixes", json={"prefix": "10.71.0.0/24", "vrf_id": vrf_id}
        )
    ).json()
    await client.post(
        "/api/v1/addresses",
        json={
            "prefix_id": p["id"], "vrf_id": vrf_id,
            "address": "10.71.0.10", "status": "active",
            "mac_address": "00:11:22:33:44:55",
        },
    )

    fake = _FakeRedis()
    monkeypatch.setattr(worker, "SessionLocal", sf)
    monkeypatch.setattr(worker, "get_redis", lambda: fake)
    emitted = []

    async def fake_emit(et, summary, payload=None):
        emitted.append(et)
        return 0

    async def scan_with_mismatch(cidr, **kw):
        return [HostResult(ip="10.71.0.10", mac="AA:BB:CC:DD:EE:FF")]

    monkeypatch.setattr(worker.notify, "emit", fake_emit)
    monkeypatch.setattr(worker, "scan_cidr", scan_with_mismatch)
    job = ScanJob(cidr="10.71.0.0/24", status=ScanStatus.QUEUED)
    session.add(job)
    await session.commit()
    await worker.run_scan({}, job.id)
    assert emitted == ["mac_mismatch"]

    # scan 2: default live-wins already wrote the observed MAC, so this
    # scan agrees and clears the flag — no event either way
    emitted.clear()
    job2 = ScanJob(cidr="10.71.0.0/24", status=ScanStatus.QUEUED)
    session.add(job2)
    await session.commit()
    await worker.run_scan({}, job2.id)
    assert "mac_mismatch" not in emitted


# ------------------------------------------------------------- backup + sweep


async def test_backup_registry_covers_monitoring_tables():
    from app.services.backup import BACKUP_TABLES

    names = {t.name for t in BACKUP_TABLES}
    assert {
        "monitor_targets", "notification_channels", "notification_log"
    } <= names


async def test_retention_sweep_prunes_notification_log(client, session):
    from app.worker import worker

    session.add(
        NotificationLog(
            channel_id=None, event_type="x", summary="old", ok=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=40),
        )
    )
    session.add(
        NotificationLog(channel_id=None, event_type="x", summary="new", ok=True)
    )
    await session.commit()
    detail = await worker._retention_sweeps(
        session,
        {"notify_retention_days": 30},
        datetime.now(timezone.utc),
    )
    assert detail["notification_log"] == 1
    left = (
        await session.execute(select(NotificationLog.summary))
    ).scalars().all()
    assert left == ["new"]
