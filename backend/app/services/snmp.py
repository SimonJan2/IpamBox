"""SNMP enrichment (V8) — read-only polls of our own devices.

Devices report themselves: IF-MIB gives the real port table (names, live
oper/admin state, negotiated speed, port MACs) and BRIDGE-MIB's forwarding
table says which learned MAC sits behind which port — which lets the poll
fill ``ip_addresses.connected_interface_id`` with structured far-end
links. All polls are GET/GETNEXT/GETBULK only — no SET, ever.

Transport: pysnmp's asyncio hlapi (``pysnmp.hlapi.v3arch.asyncio``) — the
only flavour pysnmp>=7 ships (the sync API was removed upstream), and its
datagram endpoint works on the worker's loop and on uvloop in the API, so
no ``asyncio.to_thread`` wrapper is needed. OIDs are numeric-only; no MIB
files and no net-snmp dependency.

Bounds: every request uses ``snmp_timeout`` + one retry and every walk is
capped at ``max_calls`` round-trips — a dead device costs its timeout,
never the lane. Credentials arrive decrypted inside a ``SnmpTarget`` and
are never logged or returned; a missing/corrupt blob is a ``SnmpError``
(a device problem), while ``SecretsNotConfigured`` propagates (a platform
problem — 503 on the API, stamped per-device by the worker).
"""
import ipaddress
import json
import logging
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta, timezone

from sqlalchemy import bindparam, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from pysnmp.hlapi.v3arch.asyncio import (
    CommunityData,
    ContextData,
    EndOfMibView,
    NoSuchInstance,
    NoSuchObject,
    ObjectIdentifier,
    ObjectIdentity,
    ObjectType,
    OctetString,
    SnmpEngine,
    Udp6TransportTarget,
    UdpTransportTarget,
    UsmUserData,
    bulk_walk_cmd,
    get_cmd,
    usm3DESEDEPrivProtocol,
    usmAesCfb128Protocol,
    usmAesCfb192Protocol,
    usmAesCfb256Protocol,
    usmDESPrivProtocol,
    usmHMAC128SHA224AuthProtocol,
    usmHMAC192SHA256AuthProtocol,
    usmHMAC256SHA384AuthProtocol,
    usmHMAC384SHA512AuthProtocol,
    usmHMACMD5AuthProtocol,
    usmHMACSHAAuthProtocol,
    usmNoAuthProtocol,
    usmNoPrivProtocol,
    walk_cmd,
)

from app.models.cabling import DeviceInterface
from app.models.device import Device
from app.models.ip_address import IPAddress
from app.schemas.common import ip_display
from app.services import cable_validation
from app.services.devices import ips_by_device
from app.services.ipam import may_write
from app.services.monitors import device_check_ip
from app.services.secrets import SecretsDecryptError, decrypt_str

log = logging.getLogger("ipambox.snmp")


class SnmpError(Exception):
    """Config/protocol failure — safe messages only, never credentials."""


class SnmpUnreachable(SnmpError):
    """No answer within timeout*retries — lands in snmp_last_error."""


# --- numeric OIDs -----------------------------------------------------------
# SNMPv2-MIB system group (scalar GETs)
OID_SYS_DESCR = "1.3.6.1.2.1.1.1.0"
OID_SYS_NAME = "1.3.6.1.2.1.1.5.0"

# IF-MIB — ifTable + ifXTable columns; the row suffix IS the ifIndex.
OID_IF_DESCR = "1.3.6.1.2.1.2.2.1.2"
OID_IF_SPEED = "1.3.6.1.2.1.2.2.1.5"  # bps, saturates at 2^32-1
OID_IF_PHYS = "1.3.6.1.2.1.2.2.1.6"
OID_IF_ADMIN = "1.3.6.1.2.1.2.2.1.7"
OID_IF_OPER = "1.3.6.1.2.1.2.2.1.8"
OID_IF_NAME = "1.3.6.1.2.1.31.1.1.1.1"  # preferred over ifDescr
OID_IF_HSPEED = "1.3.6.1.2.1.31.1.1.1.15"  # Mbps

# BRIDGE-MIB / Q-BRIDGE-MIB — basePort -> ifIndex + learned MAC -> basePort.
OID_DOT1D_BASE_IF = "1.3.6.1.2.1.17.1.4.1.2"
OID_DOT1D_FDB_PORT = "1.3.6.1.2.1.17.4.3.1.2"  # index = 6 MAC arcs
OID_DOT1Q_FDB_PORT = "1.3.6.1.2.1.17.7.1.2.2.1.2"  # index = vlan + 6 MAC arcs
OID_DOT1Q_VLAN_NAME = "1.3.6.1.2.1.17.7.1.4.3.1.1"  # index = VLAN id

# LLDP-MIB — lldpRemTable columns (index = timeMark.localPort.remIndex).
OID_LLDP_REM_CHASSIS = "1.0.8802.1.1.2.1.4.1.1.5"
OID_LLDP_REM_PORTID = "1.0.8802.1.1.2.1.4.1.1.7"
OID_LLDP_REM_PORTDESC = "1.0.8802.1.1.2.1.4.1.1.8"
OID_LLDP_REM_SYSNAME = "1.0.8802.1.1.2.1.4.1.1.9"
# lldpLocPortTable — the agent's own port identifier per lldpLocPortNum
# (ifName on most agents; a MAC under the macAddress subtype). It is how
# a received neighbor maps back onto OUR port — without it the rem
# table's bare localPortNum can't be attributed honestly.
OID_LLDP_LOC_PORTID = "1.0.8802.1.1.2.1.3.7.1.3"

OPER_MAP = {
    1: "up",
    2: "down",
    3: "testing",
    4: "unknown",
    5: "dormant",
    6: "notPresent",
    7: "lowerLayerDown",
}

_USM_AUTH = {
    "sha": usmHMACSHAAuthProtocol,
    "md5": usmHMACMD5AuthProtocol,
    "sha224": usmHMAC128SHA224AuthProtocol,
    "sha256": usmHMAC192SHA256AuthProtocol,
    "sha384": usmHMAC256SHA384AuthProtocol,
    "sha512": usmHMAC384SHA512AuthProtocol,
}
_USM_PRIV = {
    "aes128": usmAesCfb128Protocol,
    "aes192": usmAesCfb192Protocol,
    "aes256": usmAesCfb256Protocol,
    "des": usmDESPrivProtocol,
    "3des": usm3DESEDEPrivProtocol,
}
_USM_AUTH_DEFAULT = "sha"
_USM_PRIV_DEFAULT = "aes128"

# Hard caps — a poll must stay bounded no matter what the agent answers.
DEFAULT_TIMEOUT = 2.0
DEFAULT_RETRIES = 1
MAX_WALK_CALLS = 400  # request round-trips per column walk
MAX_VLAN_PASSES = 64  # community@vlan / v3-context FDB passes per device
MAX_LINKED_MACS = 4096  # FDB macs resolved against ip_addresses per poll


@dataclass(frozen=True)
class SnmpTarget:
    """Everything one device poll needs — incl. the decrypted credential.

    ``cred`` stays inside this object: it is never logged, never written
    to error text, never returned. ``vlan`` marks a per-VLAN pass — for
    v1/v2c it mangles the community (``community@vid``, Cisco-style), for
    v3 it becomes the contextName (``vlan-<vid>``).
    """

    host: str
    port: int
    version: str  # v1 | v2c | v3
    cred: dict = field(repr=False, compare=False)
    timeout: float = DEFAULT_TIMEOUT
    retries: int = DEFAULT_RETRIES
    max_calls: int = MAX_WALK_CALLS
    vlan: int | None = None


def _cred(dev: Device) -> dict:
    """Decrypt ``snmp_cred_enc`` -> dict. SecretsNotConfigured propagates
    (503 on the API); a corrupt/undecryptable blob is a device-level
    SnmpError so the poll records it as ``snmp_last_error``."""
    if not dev.snmp_cred_enc:
        raise SnmpError("no SNMP credential stored")
    try:
        data = json.loads(decrypt_str(dev.snmp_cred_enc))
    except (SecretsDecryptError, ValueError) as e:
        raise SnmpError("stored credential cannot be decrypted") from e
    if not isinstance(data, dict):
        raise SnmpError("stored credential is malformed")
    return data


def _target(dev: Device, host: str, *, timeout: float) -> SnmpTarget:
    if dev.snmp_version not in ("v1", "v2c", "v3"):
        raise SnmpError("snmp_version not set")
    return SnmpTarget(
        host=host,
        port=dev.snmp_port or 161,
        version=dev.snmp_version,
        cred=_cred(dev),
        timeout=timeout,
    )


def _auth(t: SnmpTarget):
    """Build pysnmp auth data — never logged. v1/v2c use a community
    string (``community@vid`` for per-VLAN passes); v3 a USM user with
    SHA-family auth + AES-family priv (authPriv basics only)."""
    c = t.cred
    if t.version == "v3":
        user = (c.get("user") or "").strip()
        if not user:
            raise SnmpError("v3 credential requires a user")
        auth_key = c.get("auth_key") or None
        priv_key = c.get("priv_key") or None
        auth_proto = usmNoAuthProtocol
        if auth_key:
            proto = (c.get("auth_proto") or _USM_AUTH_DEFAULT).lower()
            auth_proto = _USM_AUTH.get(proto)
            if auth_proto is None:
                raise SnmpError(f"unsupported auth_proto {proto!r}")
        priv_proto = usmNoPrivProtocol
        if priv_key:
            proto = (c.get("priv_proto") or _USM_PRIV_DEFAULT).lower()
            priv_proto = _USM_PRIV.get(proto)
            if priv_proto is None:
                raise SnmpError(f"unsupported priv_proto {proto!r}")
        return UsmUserData(
            user,
            authKey=auth_key,
            privKey=priv_key,
            authProtocol=auth_proto,
            privProtocol=priv_proto,
        )
    community = (c.get("community") or "").strip()
    if not community:
        raise SnmpError("v1/v2c credential requires a community")
    if t.vlan is not None:
        community = f"{community}@{t.vlan}"
    return CommunityData(community, mpModel=0 if t.version == "v1" else 1)


def _context(t: SnmpTarget) -> ContextData:
    """Per-VLAN context for v3 polls (v1/v2c index by community instead);
    else the cred's optional `context` — some agents (snmpsim, appliances)
    only answer a named context instead of the default."""
    if t.version != "v3":
        return ContextData()
    if t.vlan is not None:
        return ContextData(contextName=f"vlan-{t.vlan}")
    return ContextData(contextName=(t.cred.get("context") or "").strip())


async def _transport(t: SnmpTarget):
    cls = UdpTransportTarget
    try:
        if ipaddress.ip_address(t.host).version == 6:
            cls = Udp6TransportTarget
    except ValueError:
        pass  # hostname — the target's resolver handles it
    try:
        return await cls.create(
            (t.host, t.port), timeout=t.timeout, retries=t.retries
        )
    except SnmpError:
        raise
    except Exception as e:
        # DNS/UDP setup failures are 'unreachable' — data, not exceptions.
        raise SnmpUnreachable(f"{e.__class__.__name__}: {e}"[:300]) from e


def _raise_for(err_ind, err_stat, err_idx, binds) -> None:
    """Map pysnmp's error triple onto our exceptions. Transport failures
    are 'unreachable' (data); protocol errors are SnmpError. Error text
    comes from pysnmp — it never contains credentials. In pysnmp 7 the
    status tuple is (errorIndication, errorStatus:int, errorIndex:int) —
    status 0/noError is success, anything else maps to a clean message."""
    if err_ind is not None:
        raise SnmpUnreachable(str(err_ind)[:300])
    if err_stat is not None and int(err_stat) != 0:
        where = ""
        if err_idx and binds:
            try:
                where = f" at {binds[int(err_idx) - 1][0].prettyPrint()}"
            except (IndexError, TypeError, AttributeError):
                where = ""
        pretty = (
            err_stat.prettyPrint()
            if hasattr(err_stat, "prettyPrint")
            else f"errorStatus {err_stat}"
        )
        raise SnmpError(f"{pretty}{where}")


async def _get(t: SnmpTarget, oids: list[str]) -> dict[str, object]:
    """One GET for a few scalar OIDs -> {dotted-oid: value}.

    The low-level boundary tests monkeypatch — callers above this line
    only ever see plain (oid, value) pairs."""
    engine = SnmpEngine()
    try:
        transport = await _transport(t)
        err_ind, err_stat, err_idx, binds = await get_cmd(
            engine,
            _auth(t),
            transport,
            _context(t),
            *[ObjectType(ObjectIdentity(o)) for o in oids],
            lookupMib=False,
        )
        _raise_for(err_ind, err_stat, err_idx, binds)
        return {_oid_str(b[0]): b[1] for b in binds}
    finally:
        engine.close_dispatcher()


async def _walk(t: SnmpTarget, oid_prefix: str) -> list[tuple[str, object]]:
    """Bounded column walk -> [(dotted-oid, value)] under ``oid_prefix``.

    GETBULK on v2c/v3 (maxRepetitions=25 rows per request), GETNEXT on
    v1. ``lexicographicMode=False`` stops the walk at the subtree edge;
    ``max_calls`` caps round-trips so a huge or looping table can't burn
    the lane. Rows carry no implied order."""
    engine = SnmpEngine()
    try:
        transport = await _transport(t)
        vb = ObjectType(ObjectIdentity(oid_prefix))
        common = dict(lookupMib=False, lexicographicMode=False,
                      maxCalls=t.max_calls)
        if t.version == "v1":
            it = walk_cmd(engine, _auth(t), transport, _context(t), vb,
                          **common)
        else:
            it = bulk_walk_cmd(engine, _auth(t), transport, _context(t),
                               0, 25, vb, **common)
        out: list[tuple[str, object]] = []
        async for err_ind, err_stat, err_idx, binds in it:
            _raise_for(err_ind, err_stat, err_idx, binds)
            for b in binds:
                name = _oid_str(b[0])
                if name.startswith(oid_prefix + "."):
                    out.append((name, b[1]))
        return out
    finally:
        engine.close_dispatcher()


# --- varbind coercion --------------------------------------------------------


def _oid_str(name) -> str:
    """Varbind name -> dotted numeric string, MIB-independent."""
    try:
        return ".".join(str(int(a)) for a in tuple(name))
    except (TypeError, ValueError):
        s = name.prettyPrint() if hasattr(name, "prettyPrint") else str(name)
        if "::" in s:
            s = s.rsplit("::", 1)[1]
        if s.startswith("iso."):
            s = s[4:]
        return s


def _is_exc(v) -> bool:
    """RFC1905 exception values — 'no answer for this varbind', not data."""
    return isinstance(v, (NoSuchObject, NoSuchInstance, EndOfMibView))


def _index_suffix(oid: str, prefix: str) -> str | None:
    """The row index of a walked column OID, or None when out of scope."""
    if not oid.startswith(prefix + "."):
        return None
    return oid[len(prefix) + 1 :]


def _idx_int(oid: str, prefix: str) -> int | None:
    """Single-int row index (ifIndex, basePort, VLAN id)."""
    suffix = _index_suffix(oid, prefix)
    if suffix is None:
        return None
    try:
        return int(suffix)
    except ValueError:
        return None


def _idx_tail_ints(oid: str, prefix: str, count: int) -> list[int] | None:
    """The trailing `count` arcs of a row index (e.g. 6 MAC bytes)."""
    suffix = _index_suffix(oid, prefix)
    if suffix is None:
        return None
    try:
        arcs = [int(a) for a in suffix.split(".")]
    except ValueError:
        return None
    if len(arcs) < count or any(not 0 <= a <= 255 for a in arcs[-count:]):
        return None
    return arcs


def _mac_from_index(oid: str, prefix: str, arcs: int = 6) -> str | None:
    """EUI-48 from the last 6 OID arcs -> 'AA:BB:CC:DD:EE:FF'."""
    tail = _idx_tail_ints(oid, prefix, arcs)
    if tail is None:
        return None
    return ":".join(f"{b:02X}" for b in tail[-arcs:])


def _ival(v) -> int | None:
    if v is None or _is_exc(v):
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _sval(v) -> str | None:
    if v is None or _is_exc(v):
        return None
    if isinstance(v, str):
        s = v.strip("\x00").strip()
        return s or None
    try:
        raw = bytes(v.asOctets())
    except (AttributeError, TypeError):
        s = str(v).strip("\x00").strip()
        return s or None
    s = raw.decode("utf-8", "replace").strip("\x00").strip()
    return s or None


def _macval(v) -> str | None:
    """ifPhysAddress/lldpRemChassisId -> 'AA:BB:..' when it's really an
    EUI-48 — empty strings and non-6-byte blobs don't count as MACs."""
    if v is None or _is_exc(v):
        return None
    if isinstance(v, str):
        hexed = v.replace(":", "").replace("-", "").replace(".", "")
        if len(hexed) == 12:
            try:
                int(hexed, 16)
            except ValueError:
                return None
            return ":".join(
                hexed[i : i + 2].upper() for i in range(0, 12, 2)
            )
        return None
    try:
        raw = bytes(v.asOctets())
    except (AttributeError, TypeError):
        return None
    if len(raw) != 6:
        return None
    return ":".join(f"{b:02X}" for b in raw)


# --- the four poll primitives -------------------------------------------------


async def test_device(
    dev: Device, host: str, *, timeout: float = DEFAULT_TIMEOUT
) -> dict:
    """GET sysName + sysDescr -> {up, sys_name, sys_descr, error}.

    Unreachable/auth-failed is DATA (the caller stamps snmp_last_error),
    never an exception. SecretsNotConfigured still propagates — that's a
    platform fault, not a device fault."""
    try:
        t = _target(dev, host, timeout=timeout)
        got = await _get(t, [OID_SYS_NAME, OID_SYS_DESCR])
    except SnmpError as e:
        return {
            "up": False,
            "sys_name": None,
            "sys_descr": None,
            "error": str(e)[:500],
        }
    except Exception as e:
        # A pysnmp/pyasn1 bug or DNS failure degrades to the same honest
        # answer — the endpoint stays a clean {up:false,error}.
        log.debug("snmp test raised for device %s", dev.id, exc_info=True)
        return {
            "up": False,
            "sys_name": None,
            "sys_descr": None,
            "error": f"{e.__class__.__name__}: {e}"[:500],
        }
    return {
        "up": True,
        "sys_name": _sval(got.get(OID_SYS_NAME)),
        "sys_descr": _sval(got.get(OID_SYS_DESCR)),
        "error": None,
    }


async def walk_if_mib(
    dev: Device, host: str, *, timeout: float = DEFAULT_TIMEOUT
) -> list[dict]:
    """IF-MIB -> [{if_index, name, oper, admin, speed_mbps, mac}].

    Columns are walked independently (an agent that lacks ifXTable still
    yields ifTable); ifName wins over ifDescr for the port name."""
    t = _target(dev, host, timeout=timeout)
    names, descrs, opers, admins, speeds, hspeeds, macs = (
        await _walk(t, OID_IF_NAME),
        await _walk(t, OID_IF_DESCR),
        await _walk(t, OID_IF_OPER),
        await _walk(t, OID_IF_ADMIN),
        await _walk(t, OID_IF_SPEED),
        await _walk(t, OID_IF_HSPEED),
        await _walk(t, OID_IF_PHYS),
    )

    def col(rows, prefix, conv):
        out = {}
        for oid, v in rows:
            idx = _idx_int(oid, prefix)
            if idx is not None:
                val = conv(v)
                if val is not None:
                    out[idx] = val
        return out

    name_by = col(descrs, OID_IF_DESCR, _sval) | col(
        names, OID_IF_NAME, _sval
    )
    oper_by = col(opers, OID_IF_OPER, lambda v: OPER_MAP.get(_ival(v)))
    admin_by = col(admins, OID_IF_ADMIN, lambda v: OPER_MAP.get(_ival(v)))
    hspeed_by = col(hspeeds, OID_IF_HSPEED, _ival)  # already Mbps
    speed_by = col(speeds, OID_IF_SPEED, _ival)  # bps
    mac_by = col(macs, OID_IF_PHYS, _macval)

    def speed_mbps(idx: int) -> int | None:
        high = hspeed_by.get(idx)
        if high:
            return high
        bps = speed_by.get(idx)
        if bps is None or bps >= 0xFFFFFFFF:
            return None
        return round(bps / 1_000_000)

    out = []
    for idx, name in sorted(name_by.items()):
        if not name:
            continue
        out.append(
            {
                "if_index": idx,
                "name": name[:64],
                "oper": oper_by.get(idx),
                "admin": admin_by.get(idx),
                "speed_mbps": speed_mbps(idx),
                "mac": mac_by.get(idx),
            }
        )
    return out


async def walk_bridge_macs(
    dev: Device, host: str, *, timeout: float = DEFAULT_TIMEOUT
) -> dict[int, list[str]]:
    """BRIDGE/Q-BRIDGE forwarding table -> {port_ifindex: [MAC, ...]}.

    Three passes: the base-context FDB (dot1dTpFdbPort), the unified
    per-VLAN table (dot1qTpFdbPort — index carries the VLAN), and a
    per-VLAN pass over dot1dTpFdbPort for every VID in
    dot1qVlanStaticName — ``community@vid`` on v1/v2c, contextName
    ``vlan-<vid>`` on v3. Every learned MAC resolves through
    dot1dBasePortIfIndex to a real ifIndex."""
    t = _target(dev, host, timeout=timeout)
    base_map: dict[int, int] = {}
    for oid, v in await _walk(t, OID_DOT1D_BASE_IF):
        port = _idx_int(oid, OID_DOT1D_BASE_IF)
        ifidx = _ival(v)
        if port is not None and ifidx is not None:
            base_map[port] = ifidx

    out: dict[int, set[str]] = {}

    def merge_fdb(rows, prefix: str, arcs: int = 6) -> None:
        for oid, v in rows:
            mac = _mac_from_index(oid, prefix, arcs)
            base_port = _ival(v)
            ifidx = base_map.get(base_port) if base_port is not None else None
            if mac and ifidx is not None:
                out.setdefault(ifidx, set()).add(mac)

    merge_fdb(await _walk(t, OID_DOT1D_FDB_PORT), OID_DOT1D_FDB_PORT)
    merge_fdb(await _walk(t, OID_DOT1Q_FDB_PORT), OID_DOT1Q_FDB_PORT, 6)

    vids: list[int] = []
    try:
        for oid, _v in await _walk(t, OID_DOT1Q_VLAN_NAME):
            vid = _idx_int(oid, OID_DOT1Q_VLAN_NAME)
            if vid is not None:
                vids.append(vid)
    except SnmpError:
        vids = []  # no Q-BRIDGE — per-VLAN passes would be identical anyway
    for vid in vids[:MAX_VLAN_PASSES]:
        try:
            merge_fdb(
                await _walk(replace(t, vlan=vid), OID_DOT1D_FDB_PORT),
                OID_DOT1D_FDB_PORT,
            )
        except SnmpUnreachable:
            # community@vid/contextName indexing unsupported — every VLAN
            # pass hits the same agent, so don't burn 64 timeouts.
            break
        except SnmpError:
            continue  # a missing/failed VLAN context isn't fatal

    return {k: sorted(v) for k, v in out.items() if v}


async def walk_lldp(
    dev: Device, host: str, *, timeout: float = DEFAULT_TIMEOUT
) -> list[dict]:
    """LLDP-MIB lldpRemTable -> [{local_port, local_port_id, remote_name,
    remote_port, remote_mac}].

    ``local_port`` is the agent's lldpRemLocalPortNum; ``local_port_id``
    is the matching lldpLocPortTable port identifier — the string the
    agent itself calls that port (ifName on most agents, a MAC under the
    macAddress subtype). v8.2's cable validation resolves it onto our
    interfaces by name/MAC; a missing loc table degrades to
    ``local_port_id=None``, never a guessed mapping."""
    t = _target(dev, host, timeout=timeout)
    sys_names, port_ids, chassis = (
        await _walk(t, OID_LLDP_REM_SYSNAME),
        await _walk(t, OID_LLDP_REM_PORTID),
        await _walk(t, OID_LLDP_REM_CHASSIS),
    )
    try:
        loc_rows = await _walk(t, OID_LLDP_LOC_PORTID)
    except SnmpError:
        loc_rows = []  # no loc table — neighbors stay unattributed
    loc_by: dict[int, str] = {}
    for oid, v in loc_rows:
        pnum = _idx_int(oid, OID_LLDP_LOC_PORTID)
        s = _sval(v)
        if pnum is not None and s is not None:
            loc_by[pnum] = s

    def col(rows, prefix, conv):
        out = {}
        for oid, v in rows:
            suffix = _index_suffix(oid, prefix)
            if suffix is None:
                continue
            try:
                parts = [int(a) for a in suffix.split(".")]
            except ValueError:
                continue
            if len(parts) < 2:
                continue
            key = (parts[-2], parts[-1])  # (localPortNum, remIndex)
            val = conv(v)
            if val is not None:
                out[key] = val
        return out

    name_by = col(sys_names, OID_LLDP_REM_SYSNAME, _sval)
    port_by = col(port_ids, OID_LLDP_REM_PORTID, _sval)
    chassis_by = col(chassis, OID_LLDP_REM_CHASSIS, _macval) | col(
        chassis, OID_LLDP_REM_CHASSIS, _sval
    )
    out = []
    for key in sorted(name_by):
        out.append(
            {
                "local_port": key[0],
                "local_port_id": loc_by.get(key[0]),
                "remote_name": name_by[key],
                "remote_port": port_by.get(key),
                "remote_mac": chassis_by.get(key),
            }
        )
    return out


# --- the enrichment poll ------------------------------------------------------


def _poll_ip(ips: list[IPAddress]) -> str | None:
    """The address a device answers SNMP on: same rule monitors use —
    first ACTIVE linked address, else the lowest-id row."""
    ip = device_check_ip(ips)
    return ip_display(ip.address) if ip is not None else None


async def due_device_ids(
    session: AsyncSession, now: datetime, interval_minutes: int
) -> list[int]:
    """Devices the lane should poll: enabled + version + cred, and last
    success older than the interval (or never). Failed-attempt pacing
    lives in the worker's Redis stamp hash — a dead device must not be
    re-polled every tick while its snmp_last_ok_at stays stale."""
    cutoff = now - timedelta(minutes=interval_minutes)
    stmt = (
        select(Device.id)
        .where(
            Device.snmp_enabled.is_(True),
            Device.snmp_version.is_not(None),
            Device.snmp_cred_enc.is_not(None),
            or_(
                Device.snmp_last_ok_at.is_(None),
                Device.snmp_last_ok_at <= cutoff,
            ),
        )
        .order_by(Device.id)
    )
    return list((await session.execute(stmt)).scalars().all())


async def _stamp_device(
    session: AsyncSession,
    device_id: int,
    *,
    now: datetime,
    ok: bool,
    error: str | None,
    sys_name: str | None = None,
    sys_descr: str | None = None,
) -> None:
    """Observed device fields via Core update — never the changelog."""
    values: dict = {"snmp_last_error": (error or None)}
    if ok:
        values["snmp_last_ok_at"] = now
        values["snmp_sys_name"] = sys_name
        values["snmp_sys_descr"] = sys_descr
    await session.execute(
        update(Device).where(Device.id == device_id).values(**values)
    )


async def _upsert_interfaces(
    session: AsyncSession, dev: Device, polled: list[dict], now: datetime
) -> tuple[dict[int, DeviceInterface], dict]:
    """Merge the polled IF-MIB table into device_interfaces.

    Match order: (device_id, if_index), then exact name — so a manually
    drawn 'Gi1/0/1' picks up observed state without losing its ownership.
    New ports become source='snmp' ORM writes (changelog-visible);
    matched rows get observed state via one bulk update() (no churn).
    Vanished ports keep their old snmp_seen_at — never deleted."""
    existing = list(
        (
            await session.execute(
                select(DeviceInterface).where(
                    DeviceInterface.device_id == dev.id
                )
            )
        ).scalars()
    )
    by_ifindex = {i.if_index: i for i in existing if i.if_index is not None}
    by_name = {i.name: i for i in existing}
    used_names = set(by_name)
    next_pos = max((i.position for i in existing), default=-1) + 1

    stats = {"seen": 0, "created": 0, "updated": 0}
    seen_indexes: set[int] = set()
    bulk: list[dict] = []
    for row in polled:
        idx = row.get("if_index")
        if idx is None or idx in seen_indexes:
            continue
        seen_indexes.add(idx)
        stats["seen"] += 1
        name = (row.get("name") or f"if{idx}")[:64]
        match = by_ifindex.get(idx) or by_name.get(name)
        values = {
            "if_index": idx,
            "oper_status": row.get("oper"),
            "admin_status": row.get("admin"),
            "snmp_seen_at": now,
            "speed_mbps": row.get("speed_mbps"),
            "mac_address": row.get("mac"),
        }
        if match is not None:
            bulk.append({"id": match.id, **values})
            stats["updated"] += 1
            continue
        if name in used_names:
            continue  # name taken by an unmatched row — can't double-book
        iface = DeviceInterface(
            device_id=dev.id,
            name=name,
            if_index=idx,
            position=next_pos,
            source="snmp",
            oper_status=row.get("oper"),
            admin_status=row.get("admin"),
            speed_mbps=row.get("speed_mbps"),
            mac_address=row.get("mac"),
            snmp_seen_at=now,
        )
        session.add(iface)
        await session.flush()  # ORM write — changelog "create" lands here
        by_ifindex[idx] = iface
        by_name[name] = iface
        used_names.add(name)
        next_pos += 1
        stats["created"] += 1
    if bulk:
        # ORM bulk-by-PK: one UPDATE per row, where id = :id implied.
        # NULL params keep the stored value — an absent ifPhysAddress or
        # ifHighSpeed must not wipe a documented MAC/speed. No session
        # sync: the populate_existing re-select below refreshes the
        # identity-mapped rows.
        await session.execute(
            update(DeviceInterface)
            .values(
                if_index=bindparam("if_index"),
                oper_status=bindparam("oper_status"),
                admin_status=bindparam("admin_status"),
                speed_mbps=func.coalesce(
                    bindparam("speed_mbps"), DeviceInterface.speed_mbps
                ),
                mac_address=func.coalesce(
                    bindparam("mac_address"), DeviceInterface.mac_address
                ),
                snmp_seen_at=bindparam("snmp_seen_at"),
            )
            .execution_options(synchronize_session=False),
            bulk,
        )
    # Re-read so the caller sees the post-upsert table (created rows got
    # ids at flush; matched rows updated by the Core statement above).
    # populate_existing forces the DB values over the identity map — the
    # bulk statement bypassed it.
    fresh = list(
        (
            await session.execute(
                select(DeviceInterface)
                .where(DeviceInterface.device_id == dev.id)
                .execution_options(populate_existing=True)
            )
        ).scalars()
    )
    return {i.if_index: i for i in fresh if i.if_index is not None}, stats


async def _apply_bridge_links(
    session: AsyncSession,
    dev: Device,
    bridge: dict[int, list[str]],
    ifindex_map: dict[int, DeviceInterface],
) -> dict:
    """Learned MAC -> ip_addresses.connected_interface_id.

    Only rows the poller may own: the field is NULL, or the row's source
    ranks below 'snmp' under may_write — manual links always win. Applied
    links are ORM writes so each one lands in the changelog."""
    mac_to_ifindex: dict[str, int] = {}
    for ifindex, macs in bridge.items():
        if ifindex not in ifindex_map or len(mac_to_ifindex) >= MAX_LINKED_MACS:
            continue
        room = MAX_LINKED_MACS - len(mac_to_ifindex)
        for mac in macs[:room]:
            mac_to_ifindex[mac] = ifindex
    stats = {"learned": len(mac_to_ifindex), "applied": 0, "skipped": 0}
    if not mac_to_ifindex:
        return stats
    rows = list(
        (
            await session.execute(
                select(IPAddress).where(
                    IPAddress.mac_address.in_(list(mac_to_ifindex))
                )
            )
        ).scalars()
    )
    for ip in rows:
        target = ifindex_map.get(mac_to_ifindex.get(ip.mac_address or ""))
        if target is None or ip.connected_interface_id == target.id:
            continue
        if ip.connected_interface_id is not None and not may_write(
            ip.source, "snmp"
        ):
            stats["skipped"] += 1  # manual (or higher-ranked) link wins
            continue
        ip.connected_interface_id = target.id
        await session.flush()  # ORM write — changelog "update"
        stats["applied"] += 1
    return stats


async def poll_device(
    session: AsyncSession,
    dev: Device,
    *,
    timeout: float = DEFAULT_TIMEOUT,
    learns_interfaces: bool = True,
    fills_connected: bool = True,
) -> dict:
    """One full enrichment pass: test -> IF-MIB -> bridge-MAC -> LLDP.

    Network first, writes second — an unreachable device stamps
    snmp_last_error and nothing else (no partial writes). Per-part walk
    failures after a successful probe are soft: the device is up, the
    error lands in snmp_last_error and the summary's `errors` list.
    Callers own the commit."""
    now = datetime.now(timezone.utc)
    summary = {
        "device_id": dev.id,
        "up": False,
        "sys_name": None,
        "sys_descr": None,
        "interfaces_seen": 0,
        "interfaces_created": 0,
        "interfaces_updated": 0,
        "macs_learned": 0,
        "links_applied": 0,
        "links_skipped": 0,
        "lldp_neighbors": 0,
        "error": None,
        "errors": [],
    }
    ips = (await ips_by_device(session, [dev.id]))[dev.id]
    host = _poll_ip(ips)
    if host is None:
        summary["error"] = "no linked IP address to poll"
        await _stamp_device(
            session, dev.id, now=now, ok=False, error=summary["error"]
        )
        return summary

    probe = await test_device(dev, host, timeout=timeout)
    summary["sys_name"] = probe["sys_name"]
    summary["sys_descr"] = probe["sys_descr"]
    if not probe["up"]:
        summary["error"] = probe["error"]
        await _stamp_device(
            session, dev.id, now=now, ok=False, error=probe["error"]
        )
        return summary
    summary["up"] = True

    try:
        polled = await walk_if_mib(dev, host, timeout=timeout)
    except SnmpError as e:
        await _stamp_device(
            session,
            dev.id,
            now=now,
            ok=True,
            error=f"if-mib: {e}"[:2000],
            sys_name=probe["sys_name"],
            sys_descr=probe["sys_descr"],
        )
        summary["error"] = f"if-mib: {e}"
        return summary

    # None = "no evidence" (collection off or the walk failed) —
    # validation skips the check entirely; {} / [] = walked and empty.
    bridge: dict[int, list[str]] | None = None
    lldp: list[dict] | None = None
    if fills_connected:
        try:
            bridge = await walk_bridge_macs(dev, host, timeout=timeout)
        except SnmpError as e:
            summary["errors"].append(f"bridge-mib: {e}")
    try:
        lldp = await walk_lldp(dev, host, timeout=timeout)
        summary["lldp_neighbors"] = len(lldp)
    except SnmpError as e:
        summary["errors"].append(f"lldp-mib: {e}")

    if learns_interfaces:
        ifindex_map, istats = await _upsert_interfaces(
            session, dev, polled, now
        )
        summary["interfaces_seen"] = istats["seen"]
        summary["interfaces_created"] = istats["created"]
        summary["interfaces_updated"] = istats["updated"]
    else:
        # Learning off — bridge links can still resolve onto manually
        # modeled ports that already carry an if_index.
        existing = (
            await session.execute(
                select(DeviceInterface).where(
                    DeviceInterface.device_id == dev.id,
                    DeviceInterface.if_index.is_not(None),
                )
            )
        ).scalars()
        ifindex_map = {i.if_index: i for i in existing}
    if bridge:
        lstats = await _apply_bridge_links(session, dev, bridge, ifindex_map)
        summary["macs_learned"] = lstats["learned"]
        summary["links_applied"] = lstats["applied"]
        summary["links_skipped"] = lstats["skipped"]

    # V8.2 cable validation — the walks above are the evidence; flags
    # land in device_interfaces.validation (findings, never fixes).
    vstats = await cable_validation.validate_device(
        session, dev, polled=polled, bridge=bridge, lldp=lldp, now=now
    )
    summary["cable_checked"] = vstats["checked"]
    summary["cable_flags"] = vstats["flagged"]
    summary["cable_flags_raised"] = vstats["raised"]
    summary["cable_flags_cleared"] = vstats["cleared"]
    summary["cable_flags_new"] = vstats["new_flags"]

    error = "; ".join(summary["errors"])[:2000] or None
    summary["error"] = error
    await _stamp_device(
        session,
        dev.id,
        now=now,
        ok=True,
        error=error,
        sys_name=probe["sys_name"],
        sys_descr=probe["sys_descr"],
    )
    return summary
