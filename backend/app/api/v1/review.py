"""Review center (V7.1) — one queue for every flag the system raises.

GET /review is pure reads: each section is a live query (no worker, no
cron). Actions go through the normal write paths — the mac accept/keep
endpoints mutate the address row directly so the changelog records them,
and resolve-switch-fields delegates to the v4a legacy-text matcher.
Dismissal is data, not deletion: dismissed items persist in
review_dismissals and stay recallable from the UI.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import DATA_READ, DATA_WRITE, require_perm
from app.models.ip_address import IPAddress
from app.schemas.cabling import MatchFreeTextOut
from app.schemas.ip_address import IPAddressOut
from app.schemas.review import DismissBody, ReviewDismissalOut, ReviewOut
from app.services import review as review_svc
from app.services.cabling import match_free_text
from app.services.ipam import IPAMError, get_or_404

router = APIRouter(prefix="/review", tags=["review"])


@router.get(
    "",
    response_model=ReviewOut,
    dependencies=[Depends(require_perm(DATA_READ))],
)
async def get_review(session: AsyncSession = Depends(get_session)):
    """Every section, each split into open items and recallable dismissals."""
    return await review_svc.build_review(session)


@router.post(
    "/dismiss",
    response_model=ReviewDismissalOut,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def dismiss_item(
    body: DismissBody, session: AsyncSession = Depends(get_session)
):
    """Suppress one finding — idempotent on its (kind, entity, fingerprint)."""
    row = await review_svc.dismiss(
        session,
        kind=body.kind,
        entity_type=body.entity_type,
        entity_id=body.entity_id,
        fingerprint=body.fingerprint,
        notes=body.notes,
    )
    await session.commit()
    return row


@router.post(
    "/undismiss",
    status_code=204,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def undismiss_item(
    body: DismissBody, session: AsyncSession = Depends(get_session)
):
    """Recall a dismissal — the finding rejoins its section's open items."""
    found = await review_svc.undismiss(
        session,
        kind=body.kind,
        entity_type=body.entity_type,
        entity_id=body.entity_id,
        fingerprint=body.fingerprint,
    )
    if not found:
        raise HTTPException(404, "no matching dismissal")
    await session.commit()


async def _flagged_address(
    session: AsyncSession, address_id: int
) -> IPAddress:
    try:
        return await get_or_404(session, IPAddress, address_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))


@router.post(
    "/mac_mismatch/{address_id}/accept",
    response_model=IPAddressOut,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def mac_mismatch_accept(
    address_id: int, session: AsyncSession = Depends(get_session)
):
    """Accept the scanned MAC: write it to mac_address, clear the flag."""
    row = await _flagged_address(session, address_id)
    try:
        await review_svc.accept_scanned_mac(session, row)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    await session.commit()
    await session.refresh(row)
    return row


@router.post(
    "/mac_mismatch/{address_id}/keep",
    response_model=IPAddressOut,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def mac_mismatch_keep(
    address_id: int, session: AsyncSession = Depends(get_session)
):
    """Keep the documented MAC: restore it, clear the flag, dismiss the pair
    so the next scan's re-flag stays out of the queue."""
    row = await _flagged_address(session, address_id)
    try:
        await review_svc.keep_stored_mac(session, row)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    await session.commit()
    await session.refresh(row)
    return row


@router.post(
    "/resolve-switch-fields",
    response_model=MatchFreeTextOut,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def resolve_switch_fields(
    session: AsyncSession = Depends(get_session),
):
    """Run the legacy switch_name/switch_port matcher over the remaining
    unlinked addresses and return its matched/ambiguous/unmatched report —
    same service call as POST /interfaces/match-free-text."""
    report = await match_free_text(session)
    await session.commit()
    return MatchFreeTextOut(
        matched=len(report["matched"]),
        ambiguous=len(report["ambiguous"]),
        unmatched=len(report["unmatched"]),
        matched_ids=report["matched"],
        ambiguous_ids=report["ambiguous"],
        unmatched_ids=report["unmatched"],
    )
