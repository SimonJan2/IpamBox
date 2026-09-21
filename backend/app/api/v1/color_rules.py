"""Color rules — global auto-coloring config (admin-managed).

Rules live at /color-rules and are all gated on system:admin — they change
what every user's tables look like, which is global config, not data edit.
Row-level manual colors stay ordinary PATCHes on each entity router
(data:write), untouched here.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import SYSTEM_ADMIN, require_perm
from app.models.color_rule import ColorRule
from app.schemas.color_rule import (
    ColorRuleCreate,
    ColorRuleOut,
    ColorRuleUpdate,
    RulePreviewOut,
    RuleReorderBody,
)
from app.services.colors import (
    COLORABLE,
    count_matches,
    fields_for,
    rules_for,
    validate_rule,
)
from app.services.ipam import IPAMError, get_or_404

router = APIRouter(
    prefix="/color-rules",
    tags=["color-rules"],
    dependencies=[Depends(require_perm(SYSTEM_ADMIN))],
)


# Literal routes declared before /{rule_id} so they can't be shadowed.
@router.get("/fields", response_model=list[dict])
async def rule_fields(entity_type: str = Query(...)):
    """Rule-targetable columns of an entity (drives the editor dropdowns)."""
    if entity_type not in COLORABLE:
        raise HTTPException(
            422, f"entity_type must be one of {sorted(COLORABLE)}"
        )
    return fields_for(entity_type)


@router.get("/preview", response_model=RulePreviewOut)
async def preview_rule(
    entity_type: str = Query(...),
    field: str = Query(...),
    operator: str = Query(...),
    value: str = Query(...),
    session: AsyncSession = Depends(get_session),
):
    """How many rows of `entity_type` a candidate rule would color."""
    err = validate_rule(entity_type, field, operator, value)
    if err:
        raise HTTPException(422, err)
    probe = ColorRule(
        entity_type=entity_type,
        field=field,
        operator=operator,
        value=value,
        color="#000000",
        position=0,
    )
    return RulePreviewOut(
        count=await count_matches(session, entity_type, probe)
    )


@router.post("/reorder", status_code=204)
async def reorder_rules(
    body: RuleReorderBody, session: AsyncSession = Depends(get_session)
):
    """Permute rules within one entity_type — first match wins, so position
    is priority. Slot-preserving like reorder() in services/ordering: the
    submitted ids keep the positions they occupy and permute among them."""
    if body.entity_type not in COLORABLE:
        raise HTTPException(
            422, f"entity_type must be one of {sorted(COLORABLE)}"
        )
    rules = await rules_for(session, body.entity_type)
    by_id = {r.id: r for r in rules}
    missing = [i for i in body.ids if i not in by_id]
    if missing:
        raise HTTPException(404, f"unknown {body.entity_type} rule ids: {missing[:5]}")
    if len(set(body.ids)) != len(body.ids):
        raise HTTPException(400, "duplicate ids in reorder")
    slots = sorted(r.position for r in rules if r.id in set(body.ids))
    for rid, pos in zip(body.ids, slots):
        by_id[rid].position = pos
    await session.commit()


@router.get("", response_model=list[ColorRuleOut])
async def list_rules(
    entity_type: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(ColorRule).order_by(
        ColorRule.entity_type, ColorRule.position, ColorRule.id
    )
    if entity_type is not None:
        stmt = stmt.where(ColorRule.entity_type == entity_type)
    return (await session.execute(stmt)).scalars().all()


@router.post("", response_model=ColorRuleOut, status_code=201)
async def create_rule(
    body: ColorRuleCreate, session: AsyncSession = Depends(get_session)
):
    top = await session.scalar(
        select(func.coalesce(func.max(ColorRule.position), 0)).where(
            ColorRule.entity_type == body.entity_type
        )
    )
    rule = ColorRule(**body.model_dump(), position=top + 1)
    session.add(rule)
    await session.commit()
    await session.refresh(rule)
    return rule


@router.get("/{rule_id}", response_model=ColorRuleOut)
async def get_rule(rule_id: int, session: AsyncSession = Depends(get_session)):
    try:
        return await get_or_404(session, ColorRule, rule_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))


@router.patch("/{rule_id}", response_model=ColorRuleOut)
async def update_rule(
    rule_id: int,
    body: ColorRuleUpdate,
    session: AsyncSession = Depends(get_session),
):
    try:
        rule = await get_or_404(session, ColorRule, rule_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    data = body.model_dump(exclude_unset=True)
    err = validate_rule(
        rule.entity_type,
        data.get("field", rule.field),
        data.get("operator", rule.operator),
        data.get("value", rule.value),
    )
    if err:
        raise HTTPException(422, err)
    for field, value in data.items():
        setattr(rule, field, value)
    await session.commit()
    await session.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=204)
async def delete_rule(rule_id: int, session: AsyncSession = Depends(get_session)):
    try:
        rule = await get_or_404(session, ColorRule, rule_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    await session.delete(rule)
    await session.commit()
