"""Outbound notification fan-out — the watchdog's voice (V7).

``emit(event_type, summary, payload)`` loads every enabled channel once,
dispatches per kind, and appends one ``notification_log`` row per attempt.
It NEVER raises into the caller — a failing channel is a log row, not a
broken check — and decrypted secret material never enters logs, errors or
responses.

Kind -> secret/config contract (secrets contract: services/secrets.py):
- webhook / discord: secret = endpoint URL, config = {"method": "POST"}
- telegram:          secret = bot token,     config = {"chat_id": ...}
- smtp:              secret = password,      config = host/port/from/to/…
"""
import asyncio
import logging
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import SessionLocal
from app.models.monitoring import (
    ChannelKind,
    NotificationChannel,
    NotificationLog,
)
from app.services.secrets import SecretsError, decrypt_str

log = logging.getLogger(__name__)

_HTTP_TIMEOUT = 10.0


class _DeliveryFailed(Exception):
    """Internal carrier for per-channel failures -> notification_log row."""


def _secret(ch: NotificationChannel) -> str | None:
    """Decrypt the channel secret; failures surface as log rows."""
    if not ch.secret_enc:
        return None
    try:
        return decrypt_str(ch.secret_enc)
    except SecretsError as e:
        raise _DeliveryFailed(str(e)) from e


async def _post_json(url: str, body: dict, method: str = "POST") -> None:
    async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
        try:
            r = await client.request(method, url, json=body)
        except httpx.HTTPError as e:
            # sanitized — the URL (a secret, e.g. bot token for telegram)
            # must never land in a log row or error string
            raise _DeliveryFailed(
                f"{e.__class__.__name__}: {e}"
            ) from e
        if r.status_code >= 400:
            raise _DeliveryFailed(f"HTTP {r.status_code}: {r.text[:200]}")


def _smtp_send(ch: NotificationChannel, subject: str, text: str) -> None:
    """Blocking smtplib send — called via asyncio.to_thread.

    Port 465 is the well-known implicit-TLS convention (Gmail and most
    relays): the server expects a TLS handshake immediately, before any
    SMTP chatter, so it needs SMTP_SSL — plain SMTP (even with
    starttls() skipped) just times out against it. Anything else is
    plaintext SMTP with optional STARTTLS.
    """
    cfg = ch.config or {}
    secret = _secret(ch)
    msg = EmailMessage()
    msg["From"] = cfg["from"]
    msg["To"] = ", ".join(cfg.get("to") or [])
    msg["Subject"] = subject
    msg.set_content(text)
    port = int(cfg.get("port") or (587 if cfg.get("starttls") else 25))
    smtp_cls = smtplib.SMTP_SSL if port == 465 else smtplib.SMTP
    with smtp_cls(cfg["host"], port, timeout=_HTTP_TIMEOUT) as s:
        if cfg.get("starttls") and port != 465:
            s.starttls()
        if secret:
            s.login(cfg.get("username") or cfg["from"], secret)
        s.send_message(msg)


async def _deliver(
    ch: NotificationChannel, event_type: str, summary: str, payload: dict
) -> None:
    """Dispatch one channel; raises _DeliveryFailed for the caller to log."""
    cfg = ch.config or {}
    ts = datetime.now(timezone.utc).isoformat()
    if ch.kind in (ChannelKind.WEBHOOK, ChannelKind.DISCORD):
        url = _secret(ch)
        if not url:
            raise _DeliveryFailed("no webhook URL configured")
        if ch.kind == ChannelKind.DISCORD:
            # discord's own webhook shape — content only, no arbitrary JSON
            body = {"content": f"**{event_type}** — {summary}"}
            await _post_json(url, body)
        else:
            body = {
                "event": event_type,
                "summary": summary,
                "payload": payload,
                "ts": ts,
            }
            await _post_json(url, body, method=cfg.get("method", "POST"))
    elif ch.kind == ChannelKind.TELEGRAM:
        token = _secret(ch)
        if not token:
            raise _DeliveryFailed("no bot token configured")
        chat_id = cfg.get("chat_id")
        if not chat_id:
            raise _DeliveryFailed("no telegram chat_id configured")
        await _post_json(
            f"https://api.telegram.org/bot{token}/sendMessage",
            {"chat_id": chat_id, "text": f"{event_type} — {summary}"},
        )
    elif ch.kind == ChannelKind.SMTP:
        await asyncio.to_thread(
            _smtp_send, ch, f"[IpamBox] {event_type}: {summary}",
            summary + "\n\n" + str(payload),
        )
    else:  # pragma: no cover — enum guards this
        raise _DeliveryFailed(f"unknown channel kind {ch.kind}")


async def _log(
    session: AsyncSession,
    ch: NotificationChannel,
    event_type: str,
    summary: str,
    ok: bool,
    error: str | None,
) -> None:
    session.add(
        NotificationLog(
            channel_id=ch.id,
            event_type=event_type,
            summary=summary[:2000],
            ok=ok,
            error=(error or "")[:2000] or None,
        )
    )


async def emit(
    event_type: str, summary: str, payload: dict[str, Any] | None = None
) -> int:
    """Fan out to every enabled channel. Returns deliveries attempted."""
    payload = payload or {}
    try:
        async with SessionLocal() as session:
            channels = list(
                (
                    await session.execute(
                        select(NotificationChannel).where(
                            NotificationChannel.enabled.is_(True)
                        )
                    )
                )
                .scalars()
                .all()
            )
            for ch in channels:
                try:
                    await _deliver(ch, event_type, summary, payload)
                    await _log(session, ch, event_type, summary, True, None)
                except Exception as e:  # noqa: BLE001 — log row, not a raise
                    log.warning("notify %s via %s failed: %s", event_type, ch.id, e)
                    await _log(
                        session, ch, event_type, summary, False, str(e)[:500]
                    )
            await session.commit()
            return len(channels)
    except Exception:  # noqa: BLE001 — emit must never break its caller
        log.exception("notify.emit failed for %s", event_type)
        return 0


async def test_channel(
    ch: NotificationChannel, session: AsyncSession | None = None
) -> tuple[bool, str | None]:
    """Exercise one channel's stored credentials — used by POST
    /notification-channels/{id}/test. Logs the attempt like a real emit.
    Pass the request's own session to log on it directly; `async with`-ing
    a caller-owned AsyncSession would close it out from under the request
    (AsyncSession.__aexit__ calls close()), so an externally-owned session
    is used as-is and only a locally opened one is closed here."""
    summary = "IpamBox test notification"
    try:
        await _deliver(ch, "channel.test", summary, {"test": True})
        err = None
        ok = True
    except Exception as e:  # noqa: BLE001 — test endpoint reports, not raises
        err = str(e)[:500]
        ok = False
    try:
        if session is not None:
            await _log(session, ch, "channel.test", summary, ok, err)
            await session.commit()
        else:
            async with SessionLocal() as owned:
                await _log(owned, ch, "channel.test", summary, ok, err)
                await owned.commit()
    except Exception:
        log.exception("test_channel log write failed")
    return ok, err
