"""tag_assignments garbage collection.

TagAssignment references its target polymorphically (object_type/object_id,
no real FK), so deleting a tagged row leaves dangling assignments — and a
later ``TRUNCATE RESTART IDENTITY`` (factory reset, backup restore) can
resurrect them onto unrelated rows when ids are reused.

The flush hooks below delete a doomed object's assignments in the same
transaction and record one changelog row per removed assignment — the same
audit contract as an explicit unassign. ``sweep_orphans`` covers rows
created outside the ORM (backup restore inserts raw rows); the 0015
migration sweeps existing databases once.
"""
from sqlalchemy import delete as sa_delete
from sqlalchemy import event, select, tuple_
from sqlalchemy.orm import Session as SyncSession

from app.core.security import get_actor
from app.models.change_log import ChangeLog
from app.models.ip_address import IPAddress
from app.models.prefix import Prefix
from app.models.site import Site
from app.models.tag import TagAssignment
from app.models.vrf import VRF

# object_type -> model. Must stay in sync with schemas.tag.TAGGABLE.
TAGGABLE_MODELS = {
    "Site": Site,
    "VRF": VRF,
    "Prefix": Prefix,
    "IPAddress": IPAddress,
}

_DOOMED_KEY = "_tag_refs_doomed"


def before_flush(session: SyncSession, _flush_context, _instances=None) -> None:
    # drop leftovers from a failed flush, mirroring changelog.py — stale
    # entries must not delete assignments for objects that rolled back
    session.info.pop(_DOOMED_KEY, None)
    doomed: list[tuple[str, int]] = []
    for obj in session.deleted:
        object_type = type(obj).__name__
        if object_type in TAGGABLE_MODELS and getattr(obj, "id", None) is not None:
            doomed.append((object_type, obj.id))
    if doomed:
        session.info[_DOOMED_KEY] = doomed


def after_flush(session: SyncSession, _flush_context) -> None:
    doomed = session.info.pop(_DOOMED_KEY, [])
    if not doomed:
        return
    conn = session.connection()
    rows = conn.execute(
        sa_delete(TagAssignment)
        .where(
            tuple_(TagAssignment.object_type, TagAssignment.object_id).in_(doomed)
        )
        .returning(
            TagAssignment.id,
            TagAssignment.tag_id,
            TagAssignment.object_type,
            TagAssignment.object_id,
        )
    ).all()
    if not rows:
        return
    # record each cascaded unassign — same entry shape as an explicit delete
    conn.execute(
        ChangeLog.__table__.insert(),
        [
            {
                "actor": get_actor(),
                "action": "delete",
                "object_type": "TagAssignment",
                "object_id": rid,
                "object_repr": f"tag#{tag} on {otype}#{oid} (cascade)",
                "changes": [
                    {"field": "object_id", "before": oid, "after": None}
                ],
            }
            for rid, tag, otype, oid in rows
        ],
    )


async def sweep_orphans(session) -> int:
    """Delete assignments whose target no longer exists. For non-ORM write
    paths (backup restore) — the flush hook can't see raw row inserts."""
    removed = 0
    for object_type, model in TAGGABLE_MODELS.items():
        res = await session.execute(
            sa_delete(TagAssignment).where(
                TagAssignment.object_type == object_type,
                ~TagAssignment.object_id.in_(select(model.id)),
            )
        )
        removed += res.rowcount or 0
    res = await session.execute(
        sa_delete(TagAssignment).where(
            ~TagAssignment.object_type.in_(TAGGABLE_MODELS)
        )
    )
    removed += res.rowcount or 0
    return removed


def register() -> None:
    event.listen(SyncSession, "before_flush", before_flush)
    event.listen(SyncSession, "after_flush", after_flush)
