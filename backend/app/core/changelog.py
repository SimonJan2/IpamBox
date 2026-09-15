"""Audit trail via session flush hooks.

before_flush collects (object, action, field-diff) specs for allowlisted
models; after_flush writes them with a direct Core INSERT on the flush's own
connection — by then new objects have their PKs assigned, and the writes land
in the same transaction without needing a second ORM flush.
"""
import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import event, inspect
from sqlalchemy.orm import Session as SyncSession

from app.core.security import get_actor
from app.models.app_setting import AppSetting
from app.models.asset import Asset
from app.models.certificate import Certificate
from app.models.change_log import ChangeLog
from app.models.circuit import Circuit
from app.models.import_batch import ImportBatch
from app.models.ip_address import IPAddress
from app.models.ip_range import IPRange
from app.models.prefix import Prefix
from app.models.service import Service
from app.models.site import Site
from app.models.tag import Tag, TagAssignment
from app.models.user import User
from app.models.vlan import VLAN, VLANGroup
from app.models.vrf import VRF

AUDITED_MODELS: tuple = (
    Site,
    VRF,
    Prefix,
    IPAddress,
    IPRange,
    Tag,
    TagAssignment,
    VLAN,
    VLANGroup,
    AppSetting,
    User,
    ImportBatch,
    Circuit,
    Certificate,
    Asset,
    Service,
)
# churn-only columns that produce noise, never signal
SKIP_FIELDS = {"updated_at", "last_seen", "password_hash"}
_SPECS_KEY = "_changelog_specs"
_REPR_ATTRS = ("name", "prefix", "address", "cidr", "username")


def _ser(v):
    if v is None or isinstance(v, (str, int, float, bool)):
        return v
    if isinstance(v, (dict, list)):
        return v  # JSONB-native values (e.g. AppSetting.value)
    if isinstance(v, enum.Enum):
        return v.value
    if isinstance(v, datetime):
        return v.isoformat()
    if isinstance(v, Decimal):
        return int(v)
    return str(v)


def _repr(obj) -> str:
    custom = getattr(obj, "__changelog_repr__", None)
    if custom is not None:
        return custom()
    for attr in _REPR_ATTRS:
        v = getattr(obj, attr, None)
        if v:
            return str(v)
    return f"{obj.__tablename__}#{getattr(obj, 'id', '?')}"


def _columns(obj) -> list[str]:
    return [a.key for a in inspect(obj).mapper.column_attrs if a.key != "id"]


def _create_changes(obj) -> list[dict]:
    return [
        {"field": f, "before": None, "after": _ser(getattr(obj, f, None))}
        for f in _columns(obj)
        if f not in SKIP_FIELDS and getattr(obj, f, None) is not None
    ]


def _update_changes(obj) -> list[dict]:
    insp = inspect(obj)
    out = []
    for attr in insp.mapper.column_attrs:
        f = attr.key
        if f in SKIP_FIELDS:
            continue
        hist = getattr(insp.attrs, f).history
        if not hist.has_changes():
            continue
        out.append(
            {
                "field": f,
                "before": _ser(hist.deleted[0] if hist.deleted else None),
                "after": _ser(hist.added[0] if hist.added else None),
            }
        )
    return out


def _delete_changes(obj) -> list[dict]:
    return [
        {"field": f, "before": _ser(getattr(obj, f, None)), "after": None}
        for f in _columns(obj)
        if f not in SKIP_FIELDS
    ]


def before_flush(session: SyncSession, _flush_context, _instances=None) -> None:
    # Drop specs left behind by a failed flush — rolled-back changes must
    # never be logged. A completed flush always pops its own specs, so
    # anything still here is stale.
    session.info.pop(_SPECS_KEY, None)
    specs: list = []
    session.info[_SPECS_KEY] = specs
    for obj in session.new:
        if isinstance(obj, AUDITED_MODELS):
            specs.append((obj, "create", _create_changes(obj)))
    for obj in session.dirty:
        if isinstance(obj, AUDITED_MODELS) and session.is_modified(
            obj, include_collections=False
        ):
            changes = _update_changes(obj)
            if changes:
                specs.append((obj, "update", changes))
    for obj in session.deleted:
        if isinstance(obj, AUDITED_MODELS):
            specs.append((obj, "delete", _delete_changes(obj)))


def after_flush(session: SyncSession, _flush_context) -> None:
    specs = session.info.pop(_SPECS_KEY, [])
    if not specs:
        return
    session.connection().execute(
        ChangeLog.__table__.insert(),
        [
            {
                "actor": get_actor(),
                "action": action,
                "object_type": type(obj).__name__,
                "object_id": getattr(obj, "id", None),
                "object_repr": _repr(obj),
                "changes": changes,
            }
            for obj, action, changes in specs
        ],
    )


def register() -> None:
    event.listen(SyncSession, "before_flush", before_flush)
    event.listen(SyncSession, "after_flush", after_flush)
