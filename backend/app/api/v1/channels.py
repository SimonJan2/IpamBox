"""Notification channels + the append-only delivery log — V7.

Every route is SYSTEM_ADMIN: channel rows carry the encrypted secret blob
and their config is close-adjacent. Responses expose `config` (non-secret
fields only) + `secret_set`; `secret_enc` never leaves the server.
"""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import SYSTEM_ADMIN, require_perm
from app.models.monitoring import (
    ChannelKind,
    NotificationChannel,
    NotificationLog,
)
from app.schemas.common import Page
from app.schemas.monitor import (
    ChannelCreate,
    ChannelOut,
    ChannelTestOut,
    ChannelUpdate,
    NotificationLogOut,
    validate_channel_fields,
)
from app.services import notify
from app.services.ipam import IPAMError, get_or_404
from app.services.secrets import encrypt_str

router = APIRouter(
    prefix="/notification-channels",
    tags=["notifications"],
    dependencies=[Depends(require_perm(SYSTEM_ADMIN))],
)
log_router = APIRouter(
    prefix="/notification-log",
    tags=["notifications"],
    dependencies=[Depends(require_perm(SYSTEM_ADMIN))],
)


async def _get(session: AsyncSession, channel_id: int) -> NotificationChannel:
    try:
        return await get_or_404(session, NotificationChannel, channel_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))


def _out(ch: NotificationChannel) -> ChannelOut:
    o = ChannelOut.model_validate(ch)
    o.secret_set = bool(ch.secret_enc)
    return o


def _config_fields(kind: ChannelKind, data: dict[str, Any]) -> dict:
    """Map the schema's flat per-kind fields onto the config JSONB."""
    if kind == ChannelKind.WEBHOOK:
        return {"method": (data.get("webhook_method") or "POST").upper()}
    if kind == ChannelKind.DISCORD:
        return {}
    if kind == ChannelKind.TELEGRAM:
        return {"chat_id": data.get("telegram_chat_id")}
    if kind == ChannelKind.SMTP:
        return {
            "host": data.get("smtp_host"),
            "port": data.get("smtp_port") or 587,
            "from": data.get("smtp_from"),
            "to": data.get("smtp_to") or [],
            "starttls": data.get("smtp_starttls", True),
            "username": data.get("smtp_username"),
        }
    return {}


def _set_secret(ch: NotificationChannel, secret: str | None) -> None:
    """None/"" clears; otherwise encrypt (503 via handler when no key)."""
    ch.secret_enc = encrypt_str(secret) if secret else None


@router.get("", response_model=Page[ChannelOut])
async def list_channels(
    limit: int | None = Query(default=None, ge=1, le=20000),
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(NotificationChannel).order_by(NotificationChannel.id)
    total = await session.scalar(
        select(func.count()).select_from(NotificationChannel)
    )
    rows = (
        await session.execute(stmt.limit(limit).offset(offset))
    ).scalars().all()
    return Page(
        items=[_out(r) for r in rows], total=total or 0, limit=limit,
        offset=offset,
    )


@router.post("", response_model=ChannelOut, status_code=201)
async def create_channel(
    body: ChannelCreate, session: AsyncSession = Depends(get_session)
):
    ch = NotificationChannel(
        name=body.name,
        kind=body.kind,
        enabled=body.enabled,
        config=_config_fields(body.kind, body.model_dump()),
    )
    if body.secret:
        _set_secret(ch, body.secret)
    session.add(ch)
    await session.commit()
    await session.refresh(ch)
    return _out(ch)


@router.get("/{channel_id}", response_model=ChannelOut)
async def get_channel(
    channel_id: int, session: AsyncSession = Depends(get_session)
):
    return _out(await _get(session, channel_id))


@router.patch("/{channel_id}", response_model=ChannelOut)
async def update_channel(
    channel_id: int,
    body: ChannelUpdate,
    session: AsyncSession = Depends(get_session),
):
    ch = await _get(session, channel_id)
    data = body.model_dump(exclude_unset=True)
    kind = data.get("kind", ch.kind)
    cfg = dict(ch.config or {})
    if kind == ch.kind:
        # merge provided per-kind fields onto the stored config
        if kind == ChannelKind.WEBHOOK and data.get("webhook_method"):
            cfg["method"] = data["webhook_method"].upper()
        elif kind == ChannelKind.TELEGRAM and "telegram_chat_id" in data:
            cfg["chat_id"] = data["telegram_chat_id"]
        elif kind == ChannelKind.SMTP:
            for src_key, cfg_key in (
                ("smtp_host", "host"), ("smtp_port", "port"),
                ("smtp_from", "from"), ("smtp_to", "to"),
                ("smtp_starttls", "starttls"), ("smtp_username", "username"),
            ):
                if src_key in data:
                    cfg[cfg_key] = data[src_key]
    else:
        # kind changed — old-kind config doesn't carry over; the PATCH
        # must carry every field the new kind requires.
        cfg = _config_fields(kind, data)
    ch.config = cfg
    try:
        validate_channel_fields(
            kind,
            secret=data.get("secret"),
            has_stored_secret=bool(ch.secret_enc) or bool(data.get("secret")),
            smtp_host=cfg.get("host"),
            smtp_from=cfg.get("from"),
            smtp_to=cfg.get("to"),
            telegram_chat_id=cfg.get("chat_id"),
        )
    except ValueError as e:
        raise HTTPException(422, str(e))
    if "name" in data:
        ch.name = data["name"]
    if "kind" in data:
        ch.kind = kind
    if "enabled" in data:
        ch.enabled = data["enabled"]
    if "secret" in data:
        _set_secret(ch, data["secret"])
    await session.commit()
    await session.refresh(ch)
    return _out(ch)


@router.delete("/{channel_id}", status_code=204)
async def delete_channel(
    channel_id: int, session: AsyncSession = Depends(get_session)
):
    ch = await _get(session, channel_id)
    await session.delete(ch)
    await session.commit()


@router.post("/{channel_id}/test", response_model=ChannelTestOut)
async def test_channel(
    channel_id: int, session: AsyncSession = Depends(get_session)
):
    """Send a canned event through the channel's stored credentials —
    proves the secret works server-side. Failures come back as
    {ok:false,error}, never as raised exceptions."""
    ch = await _get(session, channel_id)
    ok, err = await notify.test_channel(ch, session=session)
    return ChannelTestOut(ok=ok, error=err)


@log_router.get("", response_model=Page[NotificationLogOut])
async def notification_log(
    channel_id: int | None = None,
    event_type: str | None = None,
    ok: bool | None = None,
    limit: int = Query(default=200, ge=1, le=1000),
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(NotificationLog).order_by(NotificationLog.id.desc())
    if channel_id is not None:
        stmt = stmt.where(NotificationLog.channel_id == channel_id)
    if event_type is not None:
        stmt = stmt.where(NotificationLog.event_type == event_type)
    if ok is not None:
        stmt = stmt.where(NotificationLog.ok == ok)
    total = await session.scalar(
        select(func.count()).select_from(stmt.order_by(None).subquery())
    )
    rows = list(
        (await session.execute(stmt.limit(limit).offset(offset)))
        .scalars()
        .all()
    )
    chan_ids = {r.channel_id for r in rows if r.channel_id is not None}
    names = (
        dict(
            (
                await session.execute(
                    select(NotificationChannel.id, NotificationChannel.name).where(
                        NotificationChannel.id.in_(chan_ids)
                    )
                )
            ).all()
        )
        if chan_ids
        else {}
    )
    items = []
    for r in rows:
        o = NotificationLogOut.model_validate(r)
        o.channel_name = names.get(r.channel_id)
        items.append(o)
    return Page(items=items, total=total or 0, limit=limit, offset=offset)
