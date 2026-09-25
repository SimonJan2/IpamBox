"""The SNMP poll lane — per-device enrichment on the minute cron.

Same budget discipline as the monitor lane: `snmp_tick` batches every due
device into ONE `run_snmp_poll` job (fixed `_job_id`, so a second poll can
never queue behind a still-running one), and the job walks its due set
through a small semaphore (`snmp_concurrency`, default 4). Each device
gets its own session so one dead agent can't take the batch down — and
each probe is bounded by `snmp_timeout` + max walk calls, so a dead
device costs its timeout, never the lane.

Due-ness has two halves: `snmp_last_ok_at` (a column — successful polls)
and a per-device attempt stamp in the `ipam:snmp:attempts` Redis hash —
a device that keeps failing never gets a fresh last_ok, so without the
stamp it would re-poll every minute instead of every interval. Stamps
live in Redis (not app_settings, not a column) — scheduler state, not
audited data.
"""
import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select, update

from app.core.db import SessionLocal
from app.core.redis import get_arq_pool, get_redis
from app.core.security import set_actor
from app.models.device import Device
from app.services import cable_validation, runtime_settings
from app.services import snmp as svc
from app.services.secrets import SecretsNotConfigured

log = logging.getLogger("ipambox.snmp")

# Fixed arq job id — enqueue_job returns None while a job with this id is
# queued/running, so at most one poll can ever be in flight.
POLL_JOB_ID = "snmp-poll"
# Redis hash: device_id -> iso8601 of the last poll attempt (any outcome).
ATTEMPT_HASH = "ipam:snmp:attempts"


async def _attempt_fresh(device_ids: list[int], interval_minutes: int, now: datetime) -> list[int]:
    """Drop devices attempted inside the interval — the Redis half of
    due-ness (covers devices that never reach last_ok)."""
    try:
        stamps = await get_redis().hgetall(ATTEMPT_HASH)
    except Exception:
        return device_ids  # Redis down -> fall back to column-based due
    cutoff = interval_minutes * 60
    due: list[int] = []
    for did in device_ids:
        raw = stamps.get(str(did).encode()) or stamps.get(str(did))
        if not raw:
            due.append(did)
            continue
        try:
            last = datetime.fromisoformat(
                raw.decode() if isinstance(raw, bytes) else raw
            )
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)
        except ValueError:
            due.append(did)
            continue
        if (now - last).total_seconds() >= cutoff:
            due.append(did)
    return due


async def run_snmp_poll(ctx: dict, device_ids: list[int]) -> dict:
    """ARQ job: poll each due device through a small semaphore.

    Every device gets its own session + commit: one poll's writes can
    never be rolled back by another device's failure, and AsyncSession
    stays single-tasked."""
    set_actor("snmp")
    async with SessionLocal() as session:
        eff = await runtime_settings.get_effective(session)
    timeout = float(eff.values["snmp_timeout"])
    learns = bool(eff.values.get("snmp_learns_interfaces", True))
    fills = bool(eff.values.get("snmp_fills_connected", True))
    sem = asyncio.Semaphore(int(eff.values["snmp_concurrency"]))
    r = get_redis()

    async def one(did: int) -> dict | None:
        async with sem:
            now = datetime.now(timezone.utc)
            try:
                await r.hset(ATTEMPT_HASH, str(did), now.isoformat())
            except Exception:
                pass  # pacing stamp is best-effort, never fatal
            try:
                async with SessionLocal() as session:
                    dev = await session.get(Device, did)
                    # Re-check on the far side of the queue — the toggle
                    # may have flipped while the job waited.
                    if (
                        dev is None
                        or not dev.snmp_enabled
                        or not dev.snmp_version
                        or not dev.snmp_cred_enc
                    ):
                        return None
                    res = await svc.poll_device(
                        session,
                        dev,
                        timeout=timeout,
                        learns_interfaces=learns,
                        fills_connected=fills,
                    )
                    await session.commit()
                    # New cable mismatches page once; cleared/recurrent
                    # flags stay silent (fingerprint dedup lives in
                    # validate_device's raised/new split).
                    await cable_validation.emit_new_flags(
                        did, dev.name, res.get("cable_flags_new") or []
                    )
                    return res
            except SecretsNotConfigured:
                # Platform fault, not a device fault — stamp it so the
                # device page shows why polls can't run.
                try:
                    async with SessionLocal() as session:
                        await session.execute(
                            update(Device)
                            .where(Device.id == did)
                            .values(snmp_last_error="secrets not configured")
                        )
                        await session.commit()
                except Exception:
                    log.exception("snmp error-stamp failed for device %s", did)
                return None
            except Exception as e:
                log.exception("snmp poll failed for device %s", did)
                try:
                    async with SessionLocal() as session:
                        await session.execute(
                            update(Device)
                            .where(Device.id == did)
                            .values(
                                snmp_last_error=(
                                    f"poll error: {e.__class__.__name__}"
                                )[:2000]
                            )
                        )
                        await session.commit()
                except Exception:
                    log.exception("snmp error-stamp failed for device %s", did)
                return None

    results = await asyncio.gather(*(one(d) for d in device_ids))
    done = [r for r in results if r]
    ok = sum(1 for r in done if r.get("up"))
    log.info("snmp poll: %d due, %d up", len(device_ids), ok)
    return {
        "polled": len(device_ids),
        "up": ok,
        "down": len(device_ids) - ok,
    }


async def snmp_tick(ctx: dict) -> dict:
    """Every-minute cron beside monitor_tick: batch due devices into a
    single poll job. `snmp_enabled` off -> the whole lane idles."""
    set_actor("scheduler")
    now = datetime.now(timezone.utc)
    async with SessionLocal() as session:
        eff = await runtime_settings.get_effective(session)
        if not eff.values.get("snmp_enabled", False):
            return {"skipped": "snmp disabled"}
        interval = int(eff.values["snmp_interval_minutes"])
        ids = await svc.due_device_ids(session, now, interval)
    due = await _attempt_fresh(ids, interval, now)
    if not due:
        return {"due": 0}
    pool = await get_arq_pool()
    job = await pool.enqueue_job("run_snmp_poll", due, _job_id=POLL_JOB_ID)
    return {"due": len(due), "enqueued": job is not None}
