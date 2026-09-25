"""SNMP trap receiver (V8.1) — near-realtime link state.

The poll lane (worker/snmp.py) runs on a schedule; a `linkDown` shouldn't
wait for the next interval. This module opens a UDP listener inside the
scanner worker — the container is already host-networked and privileged —
and turns traps into interface state in seconds.

Ingestion is read-only in spirit: traps only ever *set observed state*
(``device_interfaces.oper_status``/``snmp_seen_at``, the
``devices.snmp_last_*`` stamps — all bulk ``update()`` writes that skip
the changelog) or raise a review flag. Nothing here creates devices or
interfaces, mutates desired config, or writes SETs.

Decode: pysnmp's ``ntfrcv.NotificationReceiver`` does the BER work and
the v1→v2 trap conversion, so every version arrives as a v2-style PDU
keyed on ``snmpTrapOID.0``. The community gate is a single sentinel
``add_v1_system`` row: an observer at the ``rfc2576.processIncomingMsg:
writable`` execpoint captures the real community + source address per
datagram, then rewrites the community to the sentinel — unknown-community
senders reach the handler instead of dying silently at the security
layer, because *they're* the auto-learn case (review queue, not a drop
counter). Our own resolution re-checks community → credentialed devices,
narrowed by source IP ↔ the device's linked IPs when ambiguous.

v3 traps are NOT handled: USM keys are localized to the sender's
engineID (carried in the packet), but we never learn or persist it —
no localized keys exist, so v3 packets fail honestly at the security
layer. Malformed datagrams die inside pysnmp's decode; anything our
handler raises is logged per-trap and never propagates — a bad packet
must not cost the listener.
"""
import asyncio
import ipaddress
import logging
import socket
from datetime import datetime, timedelta, timezone

from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.entity import config as snmp_config
from pysnmp.entity.engine import SnmpEngine
from pysnmp.entity.rfc3413 import ntfrcv
from pysnmp.hlapi.v3arch.asyncio import OctetString
from sqlalchemy import func, select, update

from app.core.db import SessionLocal
from app.core.redis import get_arq_pool
from app.core.security import set_actor
from app.models.cabling import DeviceInterface
from app.models.device import Device
from app.models.ip_address import IPAddress
from app.schemas.common import ip_display
from app.services import notify, runtime_settings
from app.services import snmp as svc
from app.services.devices import ips_by_device
from app.services.secrets import SecretsNotConfigured
from app.worker.snmp import POLL_JOB_ID

log = logging.getLogger("ipambox.snmp.traps")

# Trap identity: the VALUE of snmpTrapOID.0 (v1 traps arrive converted —
# genericTrap maps onto these same OIDs by pysnmp's rfc2576 module).
OID_TRAP_ID = "1.3.6.1.6.3.1.1.4.1.0"
# The link-trap interface: an ifIndex varbind (name is the column's row
# instance, value is the ifIndex).
OID_IF_INDEX = "1.3.6.1.2.1.2.2.1.1"

TRAP_COLD_START = "1.3.6.1.6.3.1.1.5.1"
TRAP_WARM_START = "1.3.6.1.6.3.1.1.5.2"
TRAP_LINK_DOWN = "1.3.6.1.6.3.1.1.5.3"
TRAP_LINK_UP = "1.3.6.1.6.3.1.1.5.4"
TRAP_AUTH_FAILURE = "1.3.6.1.6.3.1.1.5.5"

_TRAP_NAMES = {
    TRAP_COLD_START: "cold_start",
    TRAP_WARM_START: "warm_start",
    TRAP_LINK_DOWN: "link_down",
    TRAP_LINK_UP: "link_up",
    TRAP_AUTH_FAILURE: "authentication_failure",
}

# Sentinel community: the one registered com2sec row. Every datagram's
# real community is rewritten to this at the writable execpoint so the
# message always resolves and reaches the handler.
_SENTINEL = "ipambox-traps-in"

# Unmanaged-flag churn guard: a flapping sender must not rewrite its
# ip_addresses.custom_fields flag on every trap.
_FLAG_DEBOUNCE = timedelta(hours=1)
_FLAGGED: dict[str, datetime] = {}
# authenticationFailure traps debounce per device — a device under a
# credential-guessing scan shouldn't flood the notification channels.
_AUTH_NOTIFY_GAP = timedelta(minutes=5)
_AUTH_NOTIFIED: dict[int, datetime] = {}

_listener: "TrapListener | None" = None
_bind_error: str | None = None  # dedupes the once-per-change error log
_secrets_warned = False  # SecretsNotConfigured -> warn once, then debug


def _source_ip(transport_information) -> str | None:
    """(transportDomain, transportAddress) -> the sender's IP string.

    asyncio's UDP carrier passes the peer as a ('ip', port) tuple; other
    transports may hand a TransportAddress — fall back to its str form."""
    info = transport_information
    try:
        addr = info[1] if isinstance(info, (tuple, list)) and len(info) == 2 else info
        host = addr[0] if isinstance(addr, (tuple, list)) else str(addr)
        return str(ipaddress.ip_address(host))
    except (IndexError, TypeError, ValueError):
        return str(info) or None


def _decode(varbinds) -> tuple[str | None, int | None]:
    """[(oid, value), ...] -> (trap_oid, if_index). Tolerant: accepts
    pysnmp objects and plain str/int (tests feed canned pairs)."""
    trap_oid = None
    if_index = None
    for name, val in varbinds or []:
        oid = svc._oid_str(name)
        if oid == OID_TRAP_ID:
            trap_oid = svc._oid_str(val)
        elif oid == OID_IF_INDEX or oid.startswith(OID_IF_INDEX + "."):
            v = svc._ival(val)
            if v is None:
                v = svc._idx_int(oid, OID_IF_INDEX)  # index-in-suffix form
            if v is not None and if_index is None:
                if_index = v
    return trap_oid, if_index


async def _resolve_device(
    session, source_ip: str | None, community: str | None
) -> Device | None:
    """Trap -> the device that sent it.

    Community names the candidate set (devices with v1/v2c creds whose
    decrypted community matches — never logged); when more than one
    device shares the community the source IP narrows it to the one whose
    linked IPs contain the sender. A unique community resolves alone —
    agents that trap from an undocumented mgmt address still attribute.
    """
    rows = (
        (
            await session.execute(
                select(Device).where(
                    Device.snmp_enabled.is_(True),
                    Device.snmp_version.in_(("v1", "v2c")),
                    Device.snmp_cred_enc.is_not(None),
                )
            )
        )
        .scalars()
        .all()
    )
    cands: list[Device] = []
    for d in rows:
        try:
            cred = svc._cred(d)
        except svc.SnmpError:
            continue
        except SecretsNotConfigured:
            raise
        # "" must never match "" — a trap whose community couldn't be
        # captured (or is genuinely empty) has no claim on any device.
        if community and cred.get("community") == community:
            cands.append(d)
    if not cands:
        return None
    if len(cands) == 1:
        return cands[0]
    if not source_ip:
        return None
    linked = await ips_by_device(session, [d.id for d in cands])
    try:
        want = ipaddress.ip_address(source_ip)
    except ValueError:
        return None
    for d in cands:
        for a in linked[d.id]:
            try:
                if ipaddress.ip_address(ip_display(a.address) or "") == want:
                    return d
            except ValueError:
                continue
    return None


async def _flag_unmanaged(
    session, source_ip: str | None, trap: str, now: datetime
) -> bool:
    """Mark a documented-but-uncredentialed sender for the review queue.

    The flag is a silent custom_fields stamp (Core update — no changelog
    churn), debounced per source IP so a trap storm can't rewrite it per
    packet. It never carries the community — secrets stay out of row
    data. Sources with no ip_addresses row just get logged upstream.
    """
    if not source_ip:
        return False
    row = (
        await session.execute(
            select(IPAddress)
            .where(func.host(IPAddress.address) == source_ip)
            .order_by(IPAddress.id)
        )
    ).scalars().first()
    if row is None:
        log.debug(
            "snmp %s trap from undocumented source %s — nothing to flag",
            trap,
            source_ip,
        )
        return False
    if row.device_id is not None:
        dev = await session.get(Device, row.device_id)
        if dev is not None and dev.snmp_enabled and dev.snmp_cred_enc:
            # credentialed device whose community didn't match — a config
            # fix on the sender, not an unmanaged host.
            log.debug(
                "trap from %s belongs to credentialed device %s but the "
                "community didn't match",
                source_ip,
                dev.id,
            )
            return False
    last = _FLAGGED.get(source_ip)
    if last is not None and now - last < _FLAG_DEBOUNCE:
        return True  # already flagged recently — the row still carries it
    cf = dict(row.custom_fields or {})
    cf["snmp_unmanaged"] = {"at": now.isoformat(), "trap": trap}
    await session.execute(
        update(IPAddress)
        .where(IPAddress.id == row.id)
        .values(custom_fields=cf)
    )
    _FLAGGED[source_ip] = now
    log.info(
        "snmp %s trap from unmanaged source %s — flagged for review",
        trap,
        source_ip,
    )
    return True


async def _clear_unmanaged_flag(session, source_ip: str | None) -> None:
    """A resolved trap retires the flag — the sender turned out managed."""
    if not source_ip:
        return
    row = (
        await session.execute(
            select(IPAddress.id, IPAddress.custom_fields).where(
                func.host(IPAddress.address) == source_ip,
                IPAddress.custom_fields.has_key("snmp_unmanaged"),  # noqa: W601
            )
        )
    ).first()
    if row is None:
        return
    cf = dict(row.custom_fields or {})
    cf.pop("snmp_unmanaged", None)
    await session.execute(
        update(IPAddress).where(IPAddress.id == row.id).values(custom_fields=cf)
    )
    _FLAGGED.pop(source_ip, None)


async def _apply_link_state(
    session, dev: Device, if_index: int | None, oper: str, now: datetime
) -> tuple[int | None, str | None, str | None]:
    """linkDown/linkUp -> observed state on the modeled interface.

    Returns (prev_oper, interface_id, interface_name). Never creates a
    row — an unlearned ifIndex just means the next poll discovers it."""
    if if_index is None:
        log.debug("link trap from device %s carried no ifIndex", dev.id)
        return None, None, None
    row = (
        await session.execute(
            select(
                DeviceInterface.id,
                DeviceInterface.name,
                DeviceInterface.oper_status,
            ).where(
                DeviceInterface.device_id == dev.id,
                DeviceInterface.if_index == if_index,
            )
        )
    ).first()
    if row is None:
        log.debug(
            "ifIndex %s on device %s not modeled — trap ignored",
            if_index,
            dev.id,
        )
        return None, None, None
    await session.execute(
        update(DeviceInterface)
        .where(DeviceInterface.id == row.id)
        .values(oper_status=oper, snmp_seen_at=now)
    )
    return row.oper_status, row.id, row.name


async def handle_trap(
    source_ip: str | None, community: str | None, varbinds
) -> dict:
    """One trap end-to-end: resolve → apply → notify.

    The listener callback hands every decoded datagram here (in a task);
    tests feed canned varbind pairs directly. Never raises — a bad trap
    is a dropped packet + a debug log, never a worker crash."""
    set_actor("snmp-traps")
    try:
        trap_oid, if_index = _decode(varbinds)
    except Exception:
        log.debug("trap decode failed from %s", source_ip, exc_info=True)
        return {"drop": "decode"}
    name = _TRAP_NAMES.get(trap_oid)
    if name is None:
        log.debug("unhandled trap oid %s from %s — dropped", trap_oid, source_ip)
        return {"drop": "unknown", "trap": trap_oid}
    now = datetime.now(timezone.utc)
    notify_ev: tuple[str, str, dict] | None = None
    enqueue_poll_for: int | None = None
    try:
        async with SessionLocal() as session:
            dev = await _resolve_device(session, source_ip, community)
            if dev is None:
                flagged = await _flag_unmanaged(session, source_ip, name, now)
                await session.commit()
                if not flagged:
                    # covers: no inventory row, credentialed-mismatch, and
                    # unparseable source — none of which own a log line yet
                    log.debug(
                        "snmp %s trap from %s unresolved — dropped",
                        name,
                        source_ip or "?",
                    )
                return {"resolved": False, "trap": name, "flagged": flagged}
            await _clear_unmanaged_flag(session, source_ip)

            # Due-ness for a refresh enqueue is judged on the value BEFORE
            # this trap's own stamp — the Core update() below syncs the
            # identity-mapped row, so capture it first.
            prev_ok_at = dev.snmp_last_ok_at
            stamps: dict = {
                "snmp_last_trap_at": now,
                "snmp_last_ok_at": now,
            }
            if name in ("cold_start", "warm_start"):
                stamps["snmp_last_error"] = None
            await session.execute(
                update(Device).where(Device.id == dev.id).values(**stamps)
            )

            if name in ("link_down", "link_up"):
                oper = "down" if name == "link_down" else "up"
                prev, iface_id, iface_name = await _apply_link_state(
                    session, dev, if_index, oper, now
                )
                label = iface_name or (
                    f"ifIndex {if_index}" if if_index is not None else "?"
                )
                payload = {
                    "device_id": dev.id,
                    "device": dev.name,
                    "interface_id": iface_id,
                    "interface": iface_name,
                    "if_index": if_index,
                    "source_ip": source_ip,
                }
                # Transition-only, same rule as the monitor lane: down on
                # any change into 'down', up only on recovery FROM 'down'.
                # iface_id None = the ifIndex isn't modeled — nothing to
                # point the notification at, so stay quiet.
                if (
                    name == "link_down"
                    and iface_id is not None
                    and prev != "down"
                ):
                    notify_ev = (
                        "link.down",
                        f"{dev.name} {label} — link down (trap)",
                        payload,
                    )
                elif name == "link_up" and prev == "down":
                    notify_ev = (
                        "link.up",
                        f"{dev.name} {label} — link up (trap)",
                        payload,
                    )
            elif name == "authentication_failure":
                last = _AUTH_NOTIFIED.get(dev.id)
                if last is None or now - last >= _AUTH_NOTIFY_GAP:
                    _AUTH_NOTIFIED[dev.id] = now
                    notify_ev = (
                        "snmp.auth_failure",
                        f"{dev.name} reported an SNMP authenticationFailure "
                        "trap — someone failed auth against its agent",
                        {
                            "device_id": dev.id,
                            "device": dev.name,
                            "source_ip": source_ip,
                        },
                    )
            else:  # cold_start / warm_start
                eff = await runtime_settings.get_effective(session)
                interval = int(eff.values["snmp_interval_minutes"])
                if prev_ok_at is None or prev_ok_at <= now - timedelta(
                    minutes=interval
                ):
                    enqueue_poll_for = dev.id
            await session.commit()
    except SecretsNotConfigured:
        global _secrets_warned
        if not _secrets_warned:
            _secrets_warned = True
            log.warning(
                "snmp trap dropped — secrets not configured "
                "(suppressing repeats)"
            )
        else:
            log.debug("snmp trap dropped — secrets not configured")
        return {"drop": "secrets"}
    except Exception:
        log.exception("trap handling failed (%s from %s)", name, source_ip)
        return {"drop": "error", "trap": name}

    if enqueue_poll_for is not None:
        try:
            pool = await get_arq_pool()
            job = await pool.enqueue_job(
                "run_snmp_poll", [enqueue_poll_for], _job_id=POLL_JOB_ID
            )
            log.debug(
                "%s from device %s — refresh poll %s",
                name,
                enqueue_poll_for,
                "enqueued" if job is not None else "already queued",
            )
        except Exception:
            log.warning("trap-triggered poll enqueue failed", exc_info=True)
    if notify_ev is not None:
        try:
            await notify.emit(*notify_ev)
        except Exception:
            log.warning("trap notify emit failed", exc_info=True)
    return {"resolved": True, "trap": name}


def _task_done(t: asyncio.Task) -> None:
    try:
        t.result()
    except asyncio.CancelledError:
        pass
    except Exception:
        log.exception("trap handler task failed")


class TrapListener:
    """A pysnmp notification receiver on our own UDP socket.

    Binding the socket ourselves (rather than open_server_mode's implicit
    one) makes bind failures synchronous — EACCES/EADDRINUSE surface to
    the caller, not into a swallowed ensure_future.

    `_meta` is the per-datagram side channel: the writable-execpoint
    observer fills it immediately before pysnmp delivers the trap
    callback synchronously, so the community + source IP captured there
    belong to the trap being dispatched."""

    def __init__(self, port: int, host: str = "0.0.0.0"):
        self._meta: dict | None = None
        self._engine = SnmpEngine()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # No SO_REUSEADDR: on Linux it would let another socket that
            # also sets it bind this same UDP port and silently take the
            # trap stream — a sink must own its port loudly (EADDRINUSE).
            sock.bind((host, port))
            sock.setblocking(False)
        except OSError:
            sock.close()
            raise
        self._sock = sock
        self.port = sock.getsockname()[1]
        snmp_config.add_transport(
            self._engine,
            udp.SNMP_UDP_DOMAIN,
            udp.UdpTransport().open_server_mode(sock=sock),
        )
        snmp_config.add_v1_system(self._engine, "traps", _SENTINEL)
        self._engine.observer.register_observer(
            self._on_writable, "rfc2576.processIncomingMsg:writable"
        )
        ntfrcv.NotificationReceiver(self._engine, self._on_trap)
        self._engine.transport_dispatcher.job_started(1)
        self._engine.transport_dispatcher.run_dispatcher()

    def _on_writable(self, snmpEngine, execpoint, variables, cbCtx):
        """Capture per-datagram meta, then rewrite the community to the
        sentinel so every well-formed v1/v2c packet reaches the callback."""
        # Reset first: a hook exception must leave meta EMPTY — stale meta
        # from a previous datagram would mis-attribute this trap to the
        # wrong community/device.
        self._meta = None
        try:
            community = str(variables.get("communityName", ""))
            self._meta = {
                "community": community,
                "source_ip": _source_ip(
                    variables.get("transportInformation")
                ),
            }
            variables["communityName"] = OctetString(_SENTINEL)
        except Exception:
            log.debug("trap pre-gate failed", exc_info=True)

    def _on_trap(
        self,
        snmpEngine,
        stateReference,
        contextEngineId,
        contextName,
        varBinds,
        cbCtx,
    ):
        meta = self._meta
        self._meta = None
        try:
            task = asyncio.get_running_loop().create_task(
                handle_trap(
                    (meta or {}).get("source_ip"),
                    (meta or {}).get("community"),
                    varBinds,
                )
            )
            task.add_done_callback(_task_done)
        except Exception:
            log.debug("trap dispatch failed", exc_info=True)

    def close(self):
        for fn in (
            self._engine.transport_dispatcher.close_dispatcher,
            self._sock.close,
        ):
            try:
                fn()
            except Exception:
                pass


async def ensure(enabled: bool, port: int) -> bool:
    """Make the listener match the desired state — binds, rebinds and
    releases. Called at worker startup and on the scheduler minute tick
    so the runtime toggles take effect without a worker restart.

    A bind failure is logged once per distinct error — a stuck port must
    not spam the worker log every tick, but a freed port self-heals."""
    global _listener, _bind_error
    if _listener is not None and (not enabled or _listener.port != port):
        stop()
    if not enabled:
        _bind_error = None  # a later re-enable should log fresh
        return False
    if _listener is not None:
        return True
    try:
        _listener = TrapListener(port)
    except OSError as e:
        msg = f"udp/{port}: {e}"
        if msg != _bind_error:
            _bind_error = msg
            log.error(
                "snmp trap listener cannot bind %s — free the port or "
                "grant the container the privilege (traps stay off)",
                msg,
            )
        return False
    except Exception:
        log.exception("snmp trap listener failed to start")
        return False
    _bind_error = None
    log.info("snmp trap listener bound 0.0.0.0:udp/%d", _listener.port)
    return True


def stop() -> None:
    """Release the socket — worker shutdown and the disable/rebind path."""
    global _listener
    if _listener is not None:
        _listener.close()
        _listener = None
        log.info("snmp trap listener stopped")
