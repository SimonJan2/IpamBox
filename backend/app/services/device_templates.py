"""Device templates (V10.1): the stamping engine + the builtin catalog.

`apply_template` is the single layout-stamping path — the apply endpoint,
instantiate, and tests all run it inside the caller's transaction:

- ``merge`` (default) never deletes: ports whose names already exist are
  reported in ``skipped``, everything else is created.
- ``replace`` wipes the device's interfaces first — but only when none of
  them is cabled. A cabled port blocks the whole operation with a 409
  naming the offenders; cabling is never silently dropped.

``pair`` on a template entry names a sibling port — the two get
reciprocal ``pair_interface_id`` links, same convention as the generate
endpoint's ``pair_prefix`` (patch-panel front↔back).

Builtin seeds: `seed_device_templates` runs at startup and writes each
catalog entry once, ever — the tombstone in ``app_settings`` records
seeded names so a deleted builtin doesn't resurrect on the next boot,
and a builtin the user edited (source flipped to manual) is left alone.
"""
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_setting import AppSetting
from app.models.cabling import Cable, DeviceInterface, InterfaceKind
from app.models.device import Device
from app.models.device_template import DeviceTemplate
from app.services.ipam import ConflictError

# app_settings tombstone: names of builtin templates already seeded.
_SEEDED_KEY = "device_templates.seeded"


def _specs(template: DeviceTemplate) -> list[dict]:
    """Flatten a template row into ordered port specs — data-port entries
    as stored, then power_ports stamped as kind=power at the grid's tail."""
    specs = []
    for e in template.interfaces or []:
        specs.append(
            {
                "name": e["name"],
                "kind": InterfaceKind(e["kind"]),
                "speed_mbps": e.get("speed_mbps"),
                "position": e.get("position"),
                "pair": e.get("pair"),
            }
        )
    for p in template.power_ports or []:
        specs.append(
            {
                "name": p["name"],
                "kind": InterfaceKind.POWER,
                "speed_mbps": None,
                "position": p.get("position"),
                "pair": None,
            }
        )
    return specs


async def apply_template(
    session: AsyncSession,
    device: Device,
    template: DeviceTemplate,
    *,
    mode: str = "merge",
) -> dict:
    """Stamp the template's ports onto `device`. Flush-level helper — the
    caller owns the commit. Returns {created, skipped, blocked}."""
    existing = list(
        (
            await session.execute(
                select(DeviceInterface).where(
                    DeviceInterface.device_id == device.id
                )
            )
        )
        .scalars()
    )
    if mode == "replace" and existing:
        ids = [i.id for i in existing]
        rows = await session.execute(
            select(Cable.a_interface_id, Cable.b_interface_id).where(
                or_(
                    Cable.a_interface_id.in_(ids),
                    Cable.b_interface_id.in_(ids),
                )
            )
        )
        cabled_ids = {end for row in rows.all() for end in row}
        cabled = sorted(i.name for i in existing if i.id in cabled_ids)
        if cabled:
            raise ConflictError(
                f"replace refused — {len(cabled)} interface(s) are cabled: "
                + ", ".join(cabled)
            )
        # Uncabled — wipe. Break pair links first so the ORM delete pass
        # doesn't have to untangle mutual front↔back references.
        for i in existing:
            i.pair_interface_id = None
        await session.flush()
        for i in existing:
            await session.delete(i)
        await session.flush()
        existing = []

    by_name = {i.name: i for i in existing}
    next_pos = (
        max((i.position for i in existing), default=-1) + 1
    )
    specs = _specs(template)
    skipped: list[str] = []
    blocked: list[str] = []
    created: dict[str, DeviceInterface] = {}
    for spec in specs:
        name = spec["name"]
        if name in by_name:
            skipped.append(name)
            continue
        pos = spec["position"]
        if pos is None:
            pos = next_pos
            next_pos += 1
        obj = DeviceInterface(
            device_id=device.id,
            name=name,
            kind=spec["kind"],
            speed_mbps=spec["speed_mbps"],
            position=pos,
        )
        session.add(obj)
        by_name[name] = obj
        created[name] = obj
    await session.flush()

    # Second pass: wire declared pairs — each {a,b} once. Links go both
    # directions (the trace resolves either way, but reciprocal data stays
    # honest). A port whose pair slot is already taken — e.g. a merge onto
    # an already-paired existing port — leaves both links untouched and
    # reports the pair in `blocked` rather than re-pointing anything.
    done: set[str] = set()
    for spec in specs:
        pair_name = spec.get("pair")
        if pair_name is None or spec["name"] in done:
            continue
        done.add(spec["name"])
        done.add(pair_name)
        a = by_name.get(spec["name"])
        b = by_name.get(pair_name)
        if a is None or b is None:
            continue
        if a.pair_interface_id in (None, b.id) and b.pair_interface_id in (
            None,
            a.id,
        ):
            a.pair_interface_id = b.id
            b.pair_interface_id = a.id
        else:
            blocked.extend([a.name, b.name])
    await session.flush()
    return {
        "created": len(created),
        "skipped": skipped,
        "blocked": sorted(set(blocked)),
    }


# ---------------------------------------------------------------------------
# Builtin catalog — hand-authored generics (the bundled rack-library carries
# no port data; see frontend/public/rack-library/manifest.json). Names are
# the stable seed key.
# ---------------------------------------------------------------------------


def _range(prefix: str, start: int, end: int, **kw) -> list[dict]:
    return [{"name": f"{prefix}{i}", **kw} for i in range(start, end + 1)]


def _paired(front: str, back: str, start: int, end: int, **kw) -> list[dict]:
    """Front+back spec pairs wired via `pair` — the generate endpoint's
    pair_prefix convention expressed as template data: both sides share
    the position index so the port grid keeps them adjacent."""
    fronts = [
        {"name": f"{front}{i}", "pair": f"{back}{i}", "position": i, **kw}
        for i in range(start, end + 1)
    ]
    backs = [
        {"name": f"{back}{i}", "pair": f"{front}{i}", "position": i, **kw}
        for i in range(start, end + 1)
    ]
    return fronts + backs


def _positioned(entries: list[dict]) -> list[dict]:
    return [{**e, "position": i} for i, e in enumerate(entries)]


BUILTIN_TEMPLATES: list[dict] = [
    {
        "name": "generic-1u-server",
        "manufacturer": "Generic",
        "model": "1U Rack Server",
        "device_type": "server-1u",
        "u_height": 1,
        "colour": "#38bdf8",
        "category": "server",
        "interfaces": _positioned(
            _range("eth", 0, 1, kind="rj45", speed_mbps=1000)
            + [{"name": "ilo", "kind": "rj45", "speed_mbps": 1000}]
        ),
        "notes": "2×1G data NICs + dedicated iLO/BMC management port.",
    },
    {
        "name": "generic-2u-server",
        "manufacturer": "Generic",
        "model": "2U Rack Server",
        "device_type": "server-2u",
        "u_height": 2,
        "colour": "#0ea5e9",
        "category": "server",
        "interfaces": _positioned(
            _range("eth", 0, 3, kind="rj45", speed_mbps=1000)
            + [{"name": "ilo", "kind": "rj45", "speed_mbps": 1000}]
        ),
        "power_ports": [{"name": "psu1"}, {"name": "psu2"}],
        "notes": "4×1G data NICs + iLO, dual PSU.",
    },
    {
        "name": "switch-24",
        "manufacturer": "Generic",
        "model": "24p + 4×SFP+ Switch",
        "device_type": "switch-24p",
        "u_height": 1,
        "colour": "#34d399",
        "category": "network",
        "interfaces": _positioned(
            _range("Gi1/0/", 1, 24, kind="rj45", speed_mbps=1000)
            + _range("Te1/1/", 1, 4, kind="sfp28", speed_mbps=25000)
        ),
        "notes": "24×1G access + 4×25G SFP28 uplinks.",
    },
    {
        "name": "switch-48",
        "manufacturer": "Generic",
        "model": "48p + 4×SFP+ Switch",
        "u_height": 1,
        "colour": "#34d399",
        "category": "network",
        "interfaces": _positioned(
            _range("Gi1/0/", 1, 48, kind="rj45", speed_mbps=1000)
            + _range("Te1/1/", 1, 4, kind="sfp28", speed_mbps=25000)
        ),
        "notes": "48×1G access + 4×25G SFP28 uplinks.",
    },
    {
        "name": "switch-48sfp",
        "manufacturer": "Generic",
        "model": "48p SFP28 Switch",
        "u_height": 1,
        "colour": "#2dd4bf",
        "category": "network",
        "interfaces": _positioned(
            _range("Ethernet", 1, 48, kind="sfp28", speed_mbps=25000)
            + _range("Ethernet", 49, 54, kind="qsfp", speed_mbps=100000)
        ),
        "notes": "48×25G SFP28 + 6×100G QSFP — leaf/fabric style.",
    },
    {
        "name": "patch-panel-24",
        "manufacturer": "Generic",
        "model": "24p Patch Panel",
        "u_height": 1,
        "colour": "#fbbf24",
        "category": "patch-panel",
        "interfaces": _paired("p", "b", 1, 24, kind="patch"),
        "notes": "24 front ports each paired to a rear port (p_i↔b_i).",
    },
    {
        "name": "patch-panel-48",
        "manufacturer": "Generic",
        "model": "48p Patch Panel",
        "u_height": 1,
        "colour": "#fbbf24",
        "category": "patch-panel",
        "interfaces": _paired("p", "b", 1, 48, kind="patch"),
        "notes": "48 front ports each paired to a rear port (p_i↔b_i).",
    },
    {
        "name": "pdu-8",
        "manufacturer": "Generic",
        "model": "8-outlet PDU",
        "u_height": 1,
        "face_default": "rear",
        "colour": "#f97316",
        "category": "power",
        "interfaces": [],
        "power_ports": [{"name": f"out{i}"} for i in range(1, 9)],
        "notes": "8 switched outlets documented as power ports.",
    },
    {
        "name": "ups-1u",
        "manufacturer": "Generic",
        "model": "1U UPS",
        "u_height": 1,
        "colour": "#fb7185",
        "category": "power",
        "interfaces": [
            {"name": "mgmt", "kind": "rj45", "speed_mbps": 100, "position": 0}
        ],
        "power_ports": [{"name": "inlet"}] + [{"name": f"out{i}"} for i in range(1, 5)],
        "notes": "1U UPS: mgmt NIC, mains inlet, 4 outlets.",
    },
    {
        "name": "carrier-shelf",
        "manufacturer": "Generic",
        "model": "1U Carrier Tray",
        "device_type": "carrier-shelf",
        "u_height": 1,
        "colour": "#cbd5e1",
        "category": "carrier",
        "interfaces": [],
        "notes": "Tray other devices mount into — no ports of its own; "
        "set slot_layout on the device.",
    },
]


async def seed_device_templates(session: AsyncSession) -> int:
    """Insert builtin templates that haven't been seeded yet.

    Idempotent twice over: a name already in the table (user's manual
    copy, or a builtin edited in place) is skipped, and the app_settings
    tombstone remembers seeded names so a *deleted* builtin stays deleted
    instead of resurrecting on the next boot. Returns the number of rows
    created. Caller commits.
    """
    row = await session.get(AppSetting, _SEEDED_KEY)
    seeded = set(row.value if row and isinstance(row.value, list) else [])
    existing = set(
        (
            await session.execute(select(DeviceTemplate.name))
        ).scalars()
    )
    todo = [
        spec
        for spec in BUILTIN_TEMPLATES
        if spec["name"] not in seeded and spec["name"] not in existing
    ]
    for spec in todo:
        session.add(DeviceTemplate(source="builtin", **spec))
        seeded.add(spec["name"])
    if todo:
        if row is None:
            session.add(AppSetting(key=_SEEDED_KEY, value=sorted(seeded)))
        else:
            row.value = sorted(seeded)
    return len(todo)
