"""Global row coloring: manual ``row_color`` + rule-computed ``display_color``.

``row_color`` is a nullable #rrggbb column on the entity/address tables —
a manual per-row accent shared by all users. ``display_color`` is computed
server-side on every list/get response:

    display_color = row.color            if set (manual wins)
                  = first matching rule's color   (lowest position)
                  = None

Stamping is deliberately explicit: each list/get endpoint calls
``stamp_colors`` so exports and every client agree on the same value, and
no rule logic leaks into per-row serialization or the changelog (the
attribute isn't a mapped column, so it's never persisted or audited).
"""
import enum
from datetime import date, datetime, timedelta, timezone
from typing import Any, Iterable

from sqlalchemy import Boolean, Date, DateTime, Integer, Numeric, select
from sqlalchemy import Enum as SAEnum
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset
from app.models.base import Base
from app.models.certificate import Certificate
from app.models.circuit import Circuit
from app.models.color_rule import ColorRule
from app.models.custom_list import CustomListRow
from app.models.ip_address import IPAddress
from app.models.rack import Rack
from app.models.service import Service
from app.models.site import Site
from app.models.tag import Tag
from app.models.vlan import VLAN
from app.models.vrf import VRF

# entity_type -> model, keyed by the API resource name (what the UI calls
# the list). ip_addresses is "addresses" after its router prefix.
COLORABLE: dict[str, type[Base]] = {
    "sites": Site,
    "vrfs": VRF,
    "vlans": VLAN,
    "circuits": Circuit,
    "certificates": Certificate,
    "assets": Asset,
    "services": Service,
    "tags": Tag,
    "addresses": IPAddress,
    "custom_list_rows": CustomListRow,
    "racks": Rack,
}

OPERATORS = ("eq", "neq", "contains", "lt", "gt", "within_days")

# field "type" reported to the rules editor, which gates operator choices.
_DATE_TYPES = (Date, DateTime)
_NUM_TYPES = (Integer, Numeric)


def fields_for(entity_type: str) -> list[dict]:
    """Rule-targetable columns of an entity, for the editor's field picker.

    Every real column is fair game except row_color itself (a rule tinting
    on the manual override column would be circular). `values` is populated
    for native enums so the UI can offer a dropdown instead of free text.
    """
    out: list[dict] = []
    for col in COLORABLE[entity_type].__table__.columns:
        if col.key == "row_color":
            continue
        t = col.type
        kind = "text"
        values: list[str] | None = None
        if isinstance(t, _DATE_TYPES):
            kind = "date"
        elif isinstance(t, Boolean):
            kind = "bool"
        elif isinstance(t, _NUM_TYPES):
            kind = "number"
        elif isinstance(t, SAEnum) and t.enum_class is not None:
            kind = "enum"
            values = [m.value for m in t.enum_class]
        out.append({"name": col.key, "type": kind, "values": values})
    return out


def _as_str(v: Any) -> str:
    if isinstance(v, enum.Enum):
        return str(v.value)
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (date, datetime)):
        return v.isoformat()
    return str(v)


def _as_date(v: Any) -> date | None:
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    if isinstance(v, str):
        try:
            return date.fromisoformat(v.strip())
        except ValueError:
            return None
    return None


def _ordered_cmp(raw: Any, val: str) -> int | None:
    """-1/0/1 comparing a column value to a rule's value string.

    Tries date first when the column value is date-like, then numeric, then
    falls back to a case-insensitive string compare — so `lt`/`gt` work on
    expiry dates, VIDs and free text alike.
    """
    da = _as_date(raw)
    if da is not None:
        db = _as_date(val)
        return None if db is None else (da > db) - (da < db)
    try:
        fa, fb = float(raw), float(val)  # noqa: INT001 — bool compares as 0/1
        return (fa > fb) - (fa < fb)
    except (TypeError, ValueError):
        pass
    sa, sb = _as_str(raw).lower(), val.lower()
    return (sa > sb) - (sa < sb)


def rule_matches(rule: ColorRule, obj: Any) -> bool:
    """Does ``rule`` fire on this row? NULL fields never match."""
    raw = getattr(obj, rule.field, None)
    if raw is None:
        return False
    op = rule.operator
    if op == "within_days":
        # "expires within the next N days" — a past-due date still counts
        # (an expired cert is at least as urgent as one expiring soon).
        d = _as_date(raw)
        if d is None:
            return False
        try:
            n = int(rule.value)
        except ValueError:
            return False
        return d <= datetime.now(timezone.utc).date() + timedelta(days=n)
    if op in ("lt", "gt"):
        c = _ordered_cmp(raw, rule.value)
        if c is None:
            return False
        return c < 0 if op == "lt" else c > 0
    s, v = _as_str(raw).lower(), rule.value.lower()
    if op == "eq":
        return s == v
    if op == "neq":
        return s != v
    if op == "contains":
        return v in s
    return False


def display_color_for(obj: Any, rules: Iterable[ColorRule]) -> str | None:
    """Effective row color: manual row_color beats every rule."""
    manual = getattr(obj, "row_color", None)
    if manual:
        return manual
    for r in rules:
        if rule_matches(r, obj):
            return r.color
    return None


async def rules_for(session: AsyncSession, entity_type: str) -> list[ColorRule]:
    """An entity's rules in evaluation order (position, then id)."""
    return (
        (
            await session.execute(
                select(ColorRule)
                .where(ColorRule.entity_type == entity_type)
                .order_by(ColorRule.position, ColorRule.id)
            )
        )
        .scalars()
        .all()
    )


async def stamp_colors(
    session: AsyncSession, entity_type: str, objs: Iterable[Any]
) -> list[Any]:
    """Set the transient ``display_color`` attr on each row for serialization."""
    objs = list(objs)
    if not objs:
        return objs
    rules = await rules_for(session, entity_type)
    for o in objs:
        o.display_color = display_color_for(o, rules)
    return objs


async def count_matches(
    session: AsyncSession, entity_type: str, rule: ColorRule
) -> int:
    """Rows of ``entity_type`` the rule would color — editor preview."""
    model = COLORABLE[entity_type]
    rows = (await session.execute(select(model))).scalars().all()
    return sum(1 for r in rows if rule_matches(rule, r))


def validate_rule(
    entity_type: str, field: str, operator: str, value: str
) -> str | None:
    """Cross-field rule validation -> error string or None.

    Schemas can only check each field in isolation; whether ``field`` exists
    on the entity (and whether within_days targets a date) needs the model,
    so it lives here next to the registry.
    """
    model = COLORABLE.get(entity_type)
    if model is None:
        return f"entity_type must be one of {sorted(COLORABLE)}"
    col = model.__table__.columns.get(field)
    if col is None or field == "row_color":
        return f"{field!r} is not a field of {entity_type}"
    if operator == "within_days":
        if not isinstance(col.type, _DATE_TYPES):
            return f"within_days needs a date field — {field!r} isn't one"
        try:
            if int(value) < 0:
                return "within_days value must be >= 0"
        except ValueError:
            return "within_days value must be a day count like 7"
    return None
