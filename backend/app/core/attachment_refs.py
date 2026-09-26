"""attachments garbage collection.

Attachment rows reference their owner polymorphically
(entity_type/entity_id, no real FK), so deleting an entity would leave
dangling blobs — and a later ``TRUNCATE RESTART IDENTITY`` (factory
reset, backup restore) could resurrect them onto unrelated rows when ids
are reused. The flush hooks below delete a doomed object's attachments in
the same transaction and record one changelog row per removed file — the
same audit contract as an explicit delete. ``sweep_orphans`` covers rows
created outside the ORM (backup restore inserts raw rows).

Mirrors tag_refs.py exactly.
"""
from sqlalchemy import delete as sa_delete
from sqlalchemy import event, select, tuple_
from sqlalchemy.orm import Session as SyncSession

from app.core.security import get_actor
from app.models.asset import Asset
from app.models.attachment import Attachment
from app.models.change_log import ChangeLog
from app.models.certificate import Certificate
from app.models.circuit import Circuit
from app.models.device import Device
from app.models.ip_address import IPAddress
from app.models.rack import Rack
from app.models.site import Site

# entity_type -> model. The upload vocabulary and the sweep map — must
# stay in sync with the frontend AttachmentEntityType union.
ATTACHABLE_MODELS = {
    "device": Device,
    "rack": Rack,
    "site": Site,
    "ip_address": IPAddress,
    "certificate": Certificate,
    "circuit": Circuit,
    "asset": Asset,
}
_MODEL_TO_ENTITY = {model: etype for etype, model in ATTACHABLE_MODELS.items()}

_DOOMED_KEY = "_attachment_refs_doomed"


def before_flush(session: SyncSession, _flush_context, _instances=None) -> None:
    # drop leftovers from a failed flush, mirroring tag_refs — stale
    # entries must not delete attachments for objects that rolled back
    session.info.pop(_DOOMED_KEY, None)
    doomed: list[tuple[str, int]] = []
    for obj in session.deleted:
        entity_type = _MODEL_TO_ENTITY.get(type(obj))
        if entity_type is not None and getattr(obj, "id", None) is not None:
            doomed.append((entity_type, obj.id))
    if doomed:
        session.info[_DOOMED_KEY] = doomed


def after_flush(session: SyncSession, _flush_context) -> None:
    doomed = session.info.pop(_DOOMED_KEY, [])
    if not doomed:
        return
    conn = session.connection()
    rows = conn.execute(
        sa_delete(Attachment)
        .where(
            tuple_(Attachment.entity_type, Attachment.entity_id).in_(doomed)
        )
        .returning(
            Attachment.id,
            Attachment.filename,
            Attachment.entity_type,
            Attachment.entity_id,
        )
    ).all()
    if not rows:
        return
    # record each cascaded removal — metadata only, blob is never logged
    conn.execute(
        ChangeLog.__table__.insert(),
        [
            {
                "actor": get_actor(),
                "action": "delete",
                "object_type": "Attachment",
                "object_id": rid,
                "object_repr": f"{filename} on {etype}#{eid} (cascade)",
                "changes": [
                    {"field": "entity_id", "before": eid, "after": None}
                ],
            }
            for rid, filename, etype, eid in rows
        ],
    )


async def sweep_orphans(session) -> int:
    """Delete attachments whose owner no longer exists. For non-ORM write
    paths (backup restore) — the flush hook can't see raw row inserts."""
    removed = 0
    for entity_type, model in ATTACHABLE_MODELS.items():
        res = await session.execute(
            sa_delete(Attachment).where(
                Attachment.entity_type == entity_type,
                ~Attachment.entity_id.in_(select(model.id)),
            )
        )
        removed += res.rowcount or 0
    res = await session.execute(
        sa_delete(Attachment).where(
            ~Attachment.entity_type.in_(ATTACHABLE_MODELS)
        )
    )
    removed += res.rowcount or 0
    return removed


def register() -> None:
    event.listen(SyncSession, "before_flush", before_flush)
    event.listen(SyncSession, "after_flush", after_flush)
