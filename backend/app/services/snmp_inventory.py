"""SNMP inventory sync (V8.3) — the network's own truth, previewed.

A managed switch knows its VLANs (Q-BRIDGE dot1qVlanStatic*), its routed
interfaces/SVIs (IP-MIB ipAddressTable + ipAddressPrefixTable), and its
ARP cache (ipNetToPhysical / ipNetToMedia) better than a scan ever will —
it sees every VLAN, not just the routable one. This module turns a live
read of those tables into the importer's preview → review → apply grammar:

    collect_inventory — probe + the three walks, read-only (never SET).
    build_plan        — classify every observation against the operator's
                        chosen VRF/site into create|update|exists|conflict|
                        skip rows — the same grammar the device workbook
                        importer speaks.
    apply_plan        — write the selected rows inside the caller's one
                        transaction; the caller commits, or rolls back —
                        a partial sync is worse than none.

Provenance: ip_addresses stamp source='snmp' and every created address
links the kind='snmp' import_batches row — GET /imports/{id} shows what
the switch reported (stats.snapshot) and what we did with it
(commit_rows). VLANs/prefixes carry no source column; their provenance
is the batch plus the 'SNMP <device>' description stamped on created
prefixes — honest, and never mistaken for hand-curated rows.

Precedence: services.ipam.may_write is the field-ownership rule — scan
data may be refreshed by an observation, manual/import rows never are.
Contradictions are reported as conflict rows, never silently applied,
and the subnet's managed gateway/DNS marker rows (custom_fields.
technical) are skipped — the ranges sync owns them.
"""
import hashlib
import ipaddress
import json
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device
from app.models.import_batch import ImportBatch, ImportBatchStatus
from app.models.ip_address import IPAddress, IPStatus
from app.models.prefix import Prefix, PrefixStatus
from app.models.vlan import VLAN
from app.models.vrf import VRF
from app.schemas.common import ip_display
from app.services import prefix_math, ranges
from app.services import snmp as snmp_svc
from app.services.devices import ips_by_device
from app.services.ipam import IPAMError, check_overlap, may_write
from app.services.monitors import device_check_ip
from app.services.workbook.normalize import fold_hebrew

# One sync must stay bounded even against a monster ARP cache — the walk
# itself is capped per-column; this caps the plan's address section.
MAX_ARP_ROWS = 4096

SECTIONS = ("vlans", "subnets", "addresses")
_ACTIONS = ("create", "update", "exists", "conflict", "skip", "error")

# SVI names that give away their VLAN id — 'Vlan10', 'Vl10', 'vlan 10'.
_SVI_VID = re.compile(r"(?i)^vl(?:an)?\s*(\d{1,4})$")


@dataclass
class PlanRow:
    """One observation's verdict + everything apply needs for it."""

    section: str  # vlans | subnets | addresses
    key: str      # stable per-section selector: 'vlan:10', 'sub:10.0.0.0/24'
    action: str   # create|update|exists|conflict|skip|error
    detail: str
    diff: dict | None = None      # field -> [stored, observed]
    ref: dict | None = None       # matched existing row: {kind,id,label}
    data: dict | None = None      # apply payload — never serialized
    result: dict | None = None    # apply fills: {kind,id,label}

    @property
    def ok(self) -> bool:
        return self.action not in ("conflict", "error")

    def out(self) -> dict:
        d = {
            "section": self.section,
            "key": self.key,
            "action": self.action,
            "detail": self.detail,
            "ok": self.ok,
        }
        if self.diff:
            d["diff"] = self.diff
        if self.ref:
            d["ref"] = self.ref
        if self.result:
            d["result"] = self.result
        return d


@dataclass
class Plan:
    vrf_id: int
    vrf_name: str
    site_id: int | None
    rows: list[PlanRow] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def counts(self) -> dict[str, int]:
        c = Counter(r.action for r in self.rows)
        return {a: c.get(a, 0) for a in _ACTIONS}

    def out(self) -> dict:
        return {
            "counts": self.counts(),
            "rows": [r.out() for r in self.rows],
            "errors": self.errors,
        }


# --- collection ---------------------------------------------------------------


async def collect_inventory(
    session: AsyncSession, dev: Device, *, timeout: float
) -> dict:
    """Probe + the three inventory walks -> the raw observed truth.

    {up, host, sys_name, sys_descr, error, vlans, ip_ifs, arp,
    walk_errors}. Read-only — preview and apply both call this so the
    committed plan always reflects what the device says right now, never
    a cached answer. Writes nothing, stamps nothing.
    """
    out = {
        "up": False,
        "host": None,
        "sys_name": None,
        "sys_descr": None,
        "error": None,
        "vlans": [],
        "ip_ifs": [],
        "arp": [],
        "walk_errors": [],
    }
    ips = (await ips_by_device(session, [dev.id]))[dev.id]
    ip = device_check_ip(ips)
    if ip is None:
        out["error"] = "device has no linked IP address to poll"
        return out
    out["host"] = ip_display(ip.address)
    probe = await snmp_svc.test_device(dev, out["host"], timeout=timeout)
    out["sys_name"] = probe["sys_name"]
    out["sys_descr"] = probe["sys_descr"]
    if not probe["up"]:
        out["error"] = probe["error"]
        return out
    out["up"] = True
    for name, fn in (
        ("vlans", snmp_svc.walk_vlans),
        ("ip_ifs", snmp_svc.walk_ip_interfaces),
        ("arp", snmp_svc.walk_arp),
    ):
        try:
            out[name] = await fn(dev, out["host"], timeout=timeout)
        except snmp_svc.SnmpError as e:
            # A missing table isn't fatal — the agent may not implement
            # it; the honest answer is the error plus an empty section.
            out["walk_errors"].append(f"{name}: {e}")
    return out


def inventory_fingerprint(inv: dict) -> str:
    """Stable SHA-256 over the observed walks — the snmp batch's 'file
    hash': proof of exactly what the switch reported."""
    payload = json.dumps(
        {
            "vlans": inv.get("vlans", []),
            "ip_ifs": inv.get("ip_ifs", []),
            "arp": inv.get("arp", []),
        },
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(payload.encode()).hexdigest()


# --- plan ----------------------------------------------------------------------


def _fold(s: str | None) -> str:
    return fold_hebrew((s or "").strip()).casefold()


def _vlan_pref(v: VLAN, site_id: int | None) -> tuple[int, int]:
    """Among same-vid rows prefer the chosen site's, then unscoped."""
    return (
        0
        if site_id is not None and v.site_id == site_id
        else (1 if v.site_id is None else 2),
        0 if v.group_id is None else 1,
    )


def _pristine_technical(row: IPAddress) -> bool:
    """The subnet sync's managed gateway/DNS marker — we never touch it."""
    return ranges._pristine_technical(row)


async def _plan_vlans(
    session: AsyncSession, plan: Plan, vlans: list[dict]
) -> None:
    existing = list((await session.execute(select(VLAN))).scalars())
    by_vid: dict[int, list[VLAN]] = {}
    by_name: dict[str, list[VLAN]] = {}
    for v in existing:
        by_vid.setdefault(v.vid, []).append(v)
        by_name.setdefault(_fold(v.name), []).append(v)

    seen: set[int] = set()
    for obs in sorted(vlans, key=lambda r: r.get("vid") or 0):
        vid = obs.get("vid")
        name = (obs.get("name") or "").strip() or None
        key = f"vlan:{vid}"
        if not isinstance(vid, int) or not (1 <= vid <= 4094):
            plan.rows.append(
                PlanRow(key=key, section="vlans", action="error",
                        detail=f"VLAN id {vid!r} is out of range")
            )
            continue
        if vid in seen:
            continue  # merged tables can't double-report a vid
        seen.add(vid)
        cands = sorted(
            by_vid.get(vid, []), key=lambda v: _vlan_pref(v, plan.site_id)
        )
        if cands:
            stored = cands[0]
            ref = {"kind": "vlan", "id": stored.id,
                   "label": f"VLAN {stored.vid} ({stored.name})"}
            if name is None or _fold(stored.name) == _fold(name):
                detail = (
                    f"exists — VLAN {vid} '{stored.name}'"
                    if name is not None
                    else f"exists — VLAN {vid} '{stored.name}' (unnamed on the switch)"
                )
                plan.rows.append(PlanRow(
                    key=key, section="vlans", action="exists",
                    detail=detail, ref=ref,
                    data={"vid": vid, "vlan_id": stored.id}))
            else:
                plan.rows.append(PlanRow(
                    key=key, section="vlans", action="conflict",
                    detail=(f"VLAN {vid} is '{stored.name}' here, "
                            f"the switch calls it '{name}'"),
                    diff={"name": [stored.name, name]}, ref=ref,
                    data={"vid": vid, "vlan_id": stored.id}))
            continue
        if name is None:
            plan.rows.append(PlanRow(
                key=key, section="vlans", action="skip",
                detail=f"VLAN {vid} has no name on the switch — "
                       "nothing to match or create"))
            continue
        name_hits = by_name.get(_fold(name), [])
        if name_hits:
            other = name_hits[0]
            plan.rows.append(PlanRow(
                key=key, section="vlans", action="conflict",
                detail=(f"name '{name}' already belongs to VLAN "
                        f"{other.vid} — the switch assigns it to {vid}"),
                diff={"vid": [other.vid, vid]},
                ref={"kind": "vlan", "id": other.id,
                     "label": f"VLAN {other.vid} ({other.name})"},
                data={"vid": vid}))
            continue
        plan.rows.append(PlanRow(
            key=key, section="vlans", action="create",
            detail=f"create VLAN {vid} '{name}'"
                   + (f" — {len(obs.get('ports') or [])} member ports"
                      if obs.get("ports") else ""),
            data={"vid": vid, "name": name}))


async def _plan_subnets(
    session: AsyncSession,
    plan: Plan,
    dev: Device,
    ip_ifs: list[dict],
    known_vids: set[int],
) -> dict[str, list[str]]:
    """SVI/L3 interfaces -> subnet rows. Returns {net_str: [extra own addrs]}
    so the addresses section can report secondary addresses honestly."""
    prefixes = list(
        (await session.execute(
            select(Prefix).where(Prefix.vrf_id == plan.vrf_id)
        )).scalars()
    )
    by_cidr = {str(prefix_math.to_network(p.prefix)): p for p in prefixes}

    nets: dict[str, list[dict]] = {}
    extras: dict[str, list[str]] = {}
    for i in ip_ifs:
        addr, plen = i.get("address"), i.get("prefix_len")
        if not addr or plen is None:
            continue
        try:
            net = ipaddress.ip_network(f"{addr}/{plen}", strict=False)
        except ValueError:
            continue
        nets.setdefault(str(net), []).append(i)

    # deterministic: family, then network address
    def net_key(s: str):
        n = ipaddress.ip_network(s)
        return (n.version, int(n.network_address))

    for net_str in sorted(nets, key=net_key):
        net = ipaddress.ip_network(net_str)
        ifaces = sorted(nets[net_str], key=lambda i: int(
            ipaddress.ip_address(i["address"])))
        primary = ifaces[0]
        extras[net_str] = [i["address"] for i in ifaces[1:]]
        gateway = primary["address"]
        if_name = primary.get("name")
        key = f"sub:{net_str}"

        # vlan link — only when the SVI name parses to a vid the switch
        # actually reports (or we already track); digits alone aren't proof.
        vlan_vid = None
        m = _SVI_VID.match(if_name or "")
        if m:
            cand = int(m.group(1))
            if cand in known_vids:
                vlan_vid = cand

        p = by_cidr.get(net_str)
        if p is None:
            conflict = await check_overlap(session, net, plan.vrf_id)
            if conflict is not None:
                plan.rows.append(PlanRow(
                    key=key, section="subnets", action="conflict",
                    detail=(f"{net_str} overlaps {conflict.prefix} in "
                            f"'{plan.vrf_name}' — can't create"),
                    diff={"prefix": [str(conflict.prefix), net_str]},
                    ref={"kind": "prefix", "id": conflict.id,
                         "label": str(conflict.prefix)}))
                continue
            detail = f"create {net_str} — gateway {gateway}"
            if vlan_vid:
                detail += f", VLAN {vlan_vid}"
            plan.rows.append(PlanRow(
                key=key, section="subnets", action="create",
                detail=detail,
                data={
                    "cidr": net_str,
                    "gateway": gateway,
                    "vlan_vid": vlan_vid,
                    "description": (
                        f"SNMP {dev.name}"
                        + (f" SVI {if_name}" if if_name else "")
                    ),
                }))
            continue
        ref = {"kind": "prefix", "id": p.id, "label": str(p.prefix)}
        stored_gw = ip_display(p.gateway)
        if stored_gw == gateway:
            plan.rows.append(PlanRow(
                key=key, section="subnets", action="exists",
                detail=f"exists — {net_str} (gateway {gateway})"
                       if stored_gw else f"exists — {net_str}",
                ref=ref, data={"prefix_id": p.id}))
        elif stored_gw is None:
            plan.rows.append(PlanRow(
                key=key, section="subnets", action="update",
                detail=f"{net_str} — fill gateway {gateway} "
                       f"(the device's {if_name or 'interface'})",
                diff={"gateway": [None, gateway]}, ref=ref,
                data={"prefix_id": p.id, "gateway": gateway}))
        else:
            plan.rows.append(PlanRow(
                key=key, section="subnets", action="conflict",
                detail=(f"{net_str} gateway is {stored_gw} here, "
                        f"the device answers on {gateway}"),
                diff={"gateway": [stored_gw, gateway]}, ref=ref,
                data={"prefix_id": p.id}))
    return extras


async def _plan_addresses(
    session: AsyncSession,
    plan: Plan,
    arp: list[dict],
    extras: dict[str, list[str]],
    dev: Device,
    ifaces_by_if: dict[int, dict],
    net_to_key: dict[str, str],
) -> None:
    """ARP neighbors + the device's own secondary SVI addresses ->
    ip_addresses rows, matched per VRF by normalized address."""
    rows = list(
        (await session.execute(
            select(IPAddress).where(IPAddress.vrf_id == plan.vrf_id)
        )).scalars()
    )
    ip_map = {ip_display(r.address): r for r in rows}
    prefixes = list(
        (await session.execute(
            select(Prefix).where(
                Prefix.vrf_id == plan.vrf_id,
                Prefix.status != PrefixStatus.CONTAINER,
            )
        )).scalars()
    )
    containers = list(
        (await session.execute(
            select(Prefix).where(
                Prefix.vrf_id == plan.vrf_id,
                Prefix.status == PrefixStatus.CONTAINER,
            )
        )).scalars()
    )
    # Longest-prefix containment among existing leaf prefixes; planned
    # subnet creates are candidates too (resolved at apply). The two sets
    # can't overlap — check_overlap already conflicted any create that
    # would sit inside an existing non-container prefix.
    leaf_nets = sorted(
        ((prefix_math.to_network(p.prefix), p) for p in prefixes),
        key=lambda t: -t[0].prefixlen,
    )
    container_nets = [prefix_math.to_network(p.prefix) for p in containers]

    def holder(ip) -> dict | None:
        for net_str, key in net_to_key.items():
            if ip in ipaddress.ip_network(net_str):
                return {"prefix_key": key}
        for net, p in leaf_nets:
            if ip in net:
                return {"prefix_id": p.id}
        return None

    def classify(addr: str, mac: str | None, note: str, own: bool) -> None:
        key = f"addr:{addr}"
        existing = ip_map.get(addr)
        if existing is None:
            ref_data = holder(ipaddress.ip_address(addr))
            if ref_data is None:
                inside = next(
                    (str(n) for n in container_nets
                     if ipaddress.ip_address(addr) in n),
                    None,
                )
                detail = (
                    f"inside container {inside} — no leaf subnet in "
                    f"'{plan.vrf_name}'"
                    if inside
                    else f"no prefix in '{plan.vrf_name}' covers {addr} — "
                         "its SVI wasn't observed"
                )
                plan.rows.append(PlanRow(
                    key=key, section="addresses", action="skip",
                    detail=detail))
                return
            plan.rows.append(PlanRow(
                key=key, section="addresses", action="create",
                detail=f"discover {addr}" + (f" ({mac})" if mac else "")
                       + note,
                data={
                    "address": addr,
                    "mac": mac,
                    "own": own,
                    **ref_data,
                }))
            return
        ref = {"kind": "address", "id": existing.id, "label": addr}
        stored_mac = (existing.mac_address or "").upper() or None
        obs_mac = mac.upper() if mac else None
        if _pristine_technical(existing):
            plan.rows.append(PlanRow(
                key=key, section="addresses", action="skip",
                detail=(f"{addr} is the subnet's managed gateway/DNS "
                        "row — the ranges sync owns it"), ref=ref))
            return
        if stored_mac == obs_mac or obs_mac is None:
            plan.rows.append(PlanRow(
                key=key, section="addresses", action="exists",
                detail=f"exists — {addr}" + (f" ({stored_mac})"
                                           if stored_mac else ""),
                ref=ref, data={"address_id": existing.id}))
            return
        if stored_mac is None:
            if may_write(existing.source, "snmp"):
                plan.rows.append(PlanRow(
                    key=key, section="addresses", action="update",
                    detail=f"{addr} — fill MAC {obs_mac}",
                    diff={"mac_address": [None, obs_mac]}, ref=ref,
                    data={"address_id": existing.id, "mac": obs_mac}))
            else:
                plan.rows.append(PlanRow(
                    key=key, section="addresses", action="conflict",
                    detail=(f"{addr} is {existing.source}-owned — the "
                            f"observed MAC {obs_mac} can't be applied"),
                    diff={"mac_address": [None, obs_mac]}, ref=ref))
            return
        plan.rows.append(PlanRow(
            key=key, section="addresses", action="conflict",
            detail=(f"{addr} is documented at MAC {stored_mac}, "
                    f"the switch's ARP says {obs_mac}"),
            diff={"mac_address": [stored_mac, obs_mac]}, ref=ref))

    own_addrs = {i["address"] for i in ifaces_by_if.values()}
    seen: set[str] = set()
    for e in arp[:MAX_ARP_ROWS]:
        addr = e.get("ip")
        if not addr:
            continue
        try:
            addr = str(ipaddress.ip_address(addr))
        except ValueError:
            continue
        if addr in own_addrs:
            continue  # the device's own SVI addresses aren't neighbors
        if addr in seen:
            continue
        seen.add(addr)
        classify(addr, e.get("mac"),
                 f" — ARP via if{e.get('if_index')}"
                 if e.get("if_index") else " — ARP", False)
    # Secondary addresses on an SVI — the same net already claimed a
    # primary; these are real device-owned addresses worth documenting.
    for net_str, addrs in extras.items():
        for addr in addrs:
            try:
                addr = str(ipaddress.ip_address(addr))
            except ValueError:
                continue
            if addr in seen:
                continue
            seen.add(addr)
            iface = next(
                (i for i in ifaces_by_if.values()
                 if i.get("address") == addr),
                None,
            )
            classify(addr, (iface or {}).get("mac"),
                     f" — the device's secondary address on {net_str}",
                     True)
    if len(arp) > MAX_ARP_ROWS:
        plan.errors.append(
            f"arp: table capped at {MAX_ARP_ROWS} rows "
            f"({len(arp)} reported)"
        )


async def build_plan(
    session: AsyncSession,
    dev: Device,
    *,
    vrf_id: int,
    site_id: int | None,
    vlans: list[dict],
    ip_ifs: list[dict],
    arp: list[dict],
    walk_errors: list[str] | None = None,
) -> Plan:
    """Observed walks + chosen VRF/site -> the classified plan. Read-only —
    a preview must write nothing, so this never touches the session for
    writes."""
    vrf = await session.get(VRF, vrf_id)
    plan = Plan(
        vrf_id=vrf_id,
        vrf_name=vrf.name if vrf else f"vrf:{vrf_id}",
        site_id=site_id,
        errors=list(walk_errors or []),
    )
    await _plan_vlans(session, plan, vlans)
    # VIDs the device actually reports — bounds the SVI-name → VLAN guess.
    known_vids = {
        r.data["vid"]
        for r in plan.rows
        if r.section == "vlans" and r.data and "vid" in r.data
    }
    ifaces_by_if = {
        i.get("if_index"): i for i in ip_ifs if i.get("if_index") is not None
    }
    extras = await _plan_subnets(session, plan, dev, ip_ifs, known_vids)
    net_to_key = {
        r.data["cidr"]: r.key
        for r in plan.rows
        if r.section == "subnets" and r.action == "create" and r.data
    }
    await _plan_addresses(
        session, plan, arp, extras, dev, ifaces_by_if, net_to_key
    )
    return plan


# --- apply ----------------------------------------------------------------------


def _selected(row: PlanRow, selections: dict[str, set[str]] | None) -> bool:
    """selections=None → every applicable row; a section present but not
    listing the key → deselected (the user unchecked it)."""
    if selections is None:
        return True
    return row.key in selections.get(row.section, set())


async def apply_plan(
    session: AsyncSession,
    dev: Device,
    plan: Plan,
    *,
    selections: dict[str, set[str]] | None,
    batch: ImportBatch,
) -> list[dict]:
    """Write the selected plan rows in the caller's transaction.

    vlans → subnets → addresses, so subnet rows can link freshly-created
    VLANs and address rows resolve freshly-created prefixes. Runs ORM
    writes only — the changelog records each one. The caller owns
    commit/rollback: any exception here must roll the whole thing back —
    a half-imported switch view is worse than none.
    """
    now = datetime.now(timezone.utc)
    vlan_id_by_vid: dict[int, int] = {}
    prefix_id_by_key: dict[str, int] = {}

    def deselect(r: PlanRow) -> None:
        r.action = "skip"
        r.detail += " — deselected"

    # -- VLANs ------------------------------------------------------------------
    for r in (r for r in plan.rows if r.section == "vlans"):
        if r.action != "create":
            vid = (r.data or {}).get("vid")
            if vid is not None and (r.data or {}).get("vlan_id"):
                vlan_id_by_vid[vid] = r.data["vlan_id"]
            continue
        if not _selected(r, selections):
            deselect(r)
            continue
        v = VLAN(
            vid=r.data["vid"],
            name=r.data["name"],
            site_id=plan.site_id,
        )
        session.add(v)
        await session.flush()
        vlan_id_by_vid[v.vid] = v.id
        r.result = {"kind": "vlan", "id": v.id,
                    "label": f"VLAN {v.vid} ({v.name})"}

    # -- subnets -----------------------------------------------------------------
    for r in (r for r in plan.rows if r.section == "subnets"):
        if r.action == "exists":
            if r.data and r.data.get("prefix_id"):
                prefix_id_by_key[r.key] = r.data["prefix_id"]
            continue
        if r.action == "conflict" and r.data and r.data.get("prefix_id"):
            prefix_id_by_key[r.key] = r.data["prefix_id"]
            continue
        if not _selected(r, selections):
            if r.action in ("create", "update"):
                deselect(r)
            continue
        if r.action == "create":
            net = ipaddress.ip_network(r.data["cidr"])
            gw = ipaddress.ip_address(r.data["gateway"])
            if gw.version != net.version or gw not in net:
                raise IPAMError(
                    f"gateway {gw} is not inside {net} — aborting sync"
                )
            vid = r.data.get("vlan_vid")
            prefix = Prefix(
                prefix=str(net),
                vrf_id=plan.vrf_id,
                site_id=plan.site_id,
                vlan_id=vlan_id_by_vid.get(vid) if vid else None,
                status=PrefixStatus.ACTIVE,
                description=(r.data.get("description") or None),
                gateway=str(gw),
            )
            session.add(prefix)
            await session.flush()
            await ranges.sync_technical_addresses(session, prefix)
            prefix_id_by_key[r.key] = prefix.id
            r.result = {"kind": "prefix", "id": prefix.id,
                        "label": str(net)}
        elif r.action == "update":
            prefix = await session.get(Prefix, r.data["prefix_id"])
            if prefix is None:
                r.action = "error"
                r.detail += " — the prefix disappeared before apply"
                continue
            prefix.gateway = r.data["gateway"]
            await session.flush()
            await ranges.sync_technical_addresses(session, prefix)
            r.result = {"kind": "prefix", "id": prefix.id,
                        "label": str(prefix.prefix)}

    # -- addresses ---------------------------------------------------------------
    for r in (r for r in plan.rows if r.section == "addresses"):
        if r.action == "create":
            if not _selected(r, selections):
                deselect(r)
                continue
            prefix_id = r.data.get("prefix_id") or prefix_id_by_key.get(
                r.data.get("prefix_key") or ""
            )
            if prefix_id is None:
                r.action = "skip"
                r.detail = (f"{r.data['address']} — its subnet wasn't "
                            "applied, so there's no prefix to hold it")
                continue
            ip = ipaddress.ip_address(r.data["address"])
            prefix_ranges = await ranges.ranges_for_prefix(session, prefix_id)
            rng = ranges.containing_range(prefix_ranges, int(ip))
            addr_row = IPAddress(
                address=str(ip),
                address_int=int(ip),
                prefix_id=prefix_id,
                vrf_id=plan.vrf_id,
                ip_range_id=rng.id if rng else None,
                mac_address=r.data.get("mac"),
                status=IPStatus.DISCOVERED,
                source="snmp",
                import_batch_id=batch.id,
                device_id=dev.id if r.data.get("own") else None,
                last_seen=now,
            )
            session.add(addr_row)
            await session.flush()
            r.result = {"kind": "address", "id": addr_row.id,
                        "label": str(ip), "prefix_id": prefix_id}
        elif r.action == "update":
            if not _selected(r, selections):
                deselect(r)
                continue
            row = await session.get(IPAddress, r.data["address_id"])
            if row is None:
                r.action = "error"
                r.detail += " — the row disappeared before apply"
                continue
            if not may_write(row.source, "snmp"):
                # provenance changed between preview and apply — the
                # safer answer is to report, not write.
                r.action = "conflict"
                r.detail = (
                    f"{r.data['address_id']} is now {row.source}-owned "
                    "— not writing"
                )
                continue
            row.mac_address = r.data["mac"]
            await session.flush()
            r.result = {"kind": "address", "id": row.id,
                        "label": r.key.removeprefix("addr:"),
                        "prefix_id": row.prefix_id}

    return [r.out() for r in plan.rows]


def new_batch(
    dev: Device,
    plan: Plan,
    inv: dict,
    *,
    actor: str | None,
    selections: dict[str, list[str]] | None,
) -> ImportBatch:
    """The kind='snmp' import_batches row — provenance for one sync.

    filename/stored_path keep the file-import shape: 'snmp:<device>' and a
    snmp:// sentinel — there is no file; the observed walk lives in
    stats['snapshot'] instead. DRAFT until the transaction commits."""
    return ImportBatch(
        kind="snmp",
        filename=f"snmp:{dev.name}"[:255],
        stored_path=f"snmp://device/{dev.id}",
        sha256=inventory_fingerprint(inv),
        status=ImportBatchStatus.DRAFT,
        actor=actor,
        stats={
            "device_id": dev.id,
            "vrf_id": plan.vrf_id,
            "site_id": plan.site_id,
            "counts": plan.counts(),
            "rows": [r.out() for r in plan.rows][:5000],
            "options": {"selections": selections},
            "snapshot": {
                "vlans": inv.get("vlans", [])[:4096],
                "ip_ifs": inv.get("ip_ifs", [])[:4096],
                "arp": inv.get("arp", [])[:4096],
            },
        },
    )
