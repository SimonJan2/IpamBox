"""Global manual row order for entity list pages (shared by all users).

Rows carry two columns:

- ``pinned`` — pinned rows float to the top of every list.
- ``sort_order`` — 1-based position. NULL means "never positioned"; NULLs
  sort to the end of their pin group (NULLS LAST), so rows created outside
  the reorder flow (imports, restores, fresh creates) simply append in id
  order without anyone having to assign them a position.

``reorder()`` is slot-preserving: the submitted ids keep the positions they
already occupy and permute among them. Reordering a scoped view (a circuits
tab, a VLAN group) therefore can't displace rows outside that scope, and a
full-list reorder compacts positions to 1..n.
"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ipam import IPAMError, NotFoundError


def ordered(stmt, model, *tiebreak):
    """Default list ordering: pinned first, then manual position, then the
    entity's own tiebreak (name/vid/id)."""
    return stmt.order_by(
        model.pinned.desc(),
        model.sort_order.asc().nulls_last(),
        *tiebreak,
    )


async def reorder(session: AsyncSession, model, ids: list[int]) -> int:
    """Set positions for ``ids`` by array order, in this transaction.

    The listed rows permute among their own existing sort_order slots; when
    some listed rows are unpositioned (or all of them), fresh slots are
    allocated above the table's current max. Returns the row count.
    """
    if len(set(ids)) != len(ids):
        raise IPAMError("duplicate ids in reorder")
    if not ids:
        return 0
    rows = (
        await session.execute(select(model).where(model.id.in_(ids)))
    ).scalars().all()
    by_id = {r.id: r for r in rows}
    missing = [i for i in ids if i not in by_id]
    if missing:
        raise NotFoundError(f"unknown {model.__name__} ids: {missing[:5]}")

    slots = sorted(r.sort_order for r in rows if r.sort_order is not None)
    if len(slots) < len(ids):
        top = await session.scalar(
            select(func.coalesce(func.max(model.sort_order), 0))
        )
        slots.extend(range(top + 1, top + 1 + len(ids) - len(slots)))
    for row_id, pos in zip(ids, slots):
        by_id[row_id].sort_order = pos
    await session.commit()
    return len(ids)
