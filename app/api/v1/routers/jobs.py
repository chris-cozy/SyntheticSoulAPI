import asyncio
import json
from datetime import datetime

import jwt
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from rq.job import Job

from app.constants.constants import JWT_AUD, JWT_ISS, SESSIONS_COLLECTION
from app.core.config import JWT_SECRET_ENV
from app.core.redis_queue import get_redis
from app.domain.models import JobStatusResponse
from app.services.database import get_database
from app.services.auth import _ratelimit, auth_guard, identity

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _normalize_rq_status(rq_status: str) -> str:
    if rq_status in ("queued", "deferred"):
        return "queued"
    if rq_status in ("started",):
        return "running"
    if rq_status in ("finished",):
        return "succeeded"
    if rq_status in ("failed",):
        return "failed"
    return rq_status


def _read_job_payload(job_id: str, user_id: str) -> dict:
    try:
        job = Job.fetch(job_id, connection=get_redis())
    except Exception as exc:
        raise KeyError("not_found") from exc

    if (job.meta or {}).get("owner_user_id") != user_id:
        raise PermissionError("not_found")

    status = _normalize_rq_status(job.get_status(refresh=True))
    payload = {
        "job_id": job.id,
        "status": status,
        "progress": (job.meta or {}).get("progress"),
    }

    if status == "succeeded":
        payload["result"] = job.result
    if status == "failed":
        payload["error"] = "job_failed"
    return payload


async def _authenticate_sse_token(access_token: str) -> tuple[str, str, str]:
    try:
        payload = jwt.decode(
            access_token,
            JWT_SECRET_ENV,
            algorithms=["HS256"],
            audience=JWT_AUD,
            issuer=JWT_ISS,
        )
        user_id = payload["sub"]
        username = payload["username"]
        sid = payload["sid"]
    except Exception:
        raise HTTPException(status_code=401, detail="invalid_token")

    db = await get_database()
    sess = await db[SESSIONS_COLLECTION].find_one({"_id": sid})
    if not sess or sess.get("revoked"):
        raise HTTPException(status_code=401, detail="session_revoked")
    if sess.get("expires_at") and sess["expires_at"] <= datetime.now():
        raise HTTPException(status_code=401, detail="session_expired")

    return (user_id, username, sid)


def _format_sse(event: str, payload: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(payload)}\n\n"


def _decode_pubsub_event(raw_data, job_id: str) -> dict:
    if isinstance(raw_data, bytes):
        raw_text = raw_data.decode("utf-8", errors="ignore")
    else:
        raw_text = str(raw_data)

    try:
        payload = json.loads(raw_text)
        if isinstance(payload, dict):
            return payload
    except Exception:
        pass

    return {"job_id": job_id}


async def _job_events_stream(request: Request, job_id: str, user_id: str):
    channel = f"job:{job_id}"
    pubsub = get_redis().pubsub()
    await asyncio.to_thread(pubsub.subscribe, channel)

    last_status = None
    last_progress = None
    heartbeat_ticks = 0

    try:
        initial = await asyncio.to_thread(_read_job_payload, job_id, user_id)
        last_status = initial.get("status")
        last_progress = initial.get("progress")
        yield _format_sse("status", initial)

        if last_status in {"succeeded", "failed"}:
            yield _format_sse("done", initial)
            return

        while True:
            if await request.is_disconnected():
                break

            message = await asyncio.to_thread(
                lambda: pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            )
            if message and message.get("type") == "message":
                payload = _decode_pubsub_event(message.get("data"), job_id)
                yield _format_sse("progress", payload)

            snapshot = await asyncio.to_thread(_read_job_payload, job_id, user_id)
            status = snapshot.get("status")
            progress = snapshot.get("progress")
            if status != last_status or progress != last_progress:
                yield _format_sse("status", snapshot)
                last_status = status
                last_progress = progress

            if status in {"succeeded", "failed"}:
                yield _format_sse("done", snapshot)
                break

            heartbeat_ticks += 1
            if heartbeat_ticks >= 15:
                heartbeat_ticks = 0
                # Comment heartbeat to keep idle SSE connections alive.
                yield ": keep-alive\n\n"
    finally:
        await asyncio.to_thread(pubsub.unsubscribe, channel)
        await asyncio.to_thread(pubsub.close)


@router.get("/{job_id}", response_model=JobStatusResponse, dependencies=[Depends(auth_guard)])
async def job_status(job_id: str, ident=Depends(identity)):
    user_id, _username, _sid = ident
    await _ratelimit(f"rl:job_poll:{user_id}", limit=120, window_sec=60)

    try:
        payload = await asyncio.to_thread(_read_job_payload, job_id, user_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="not_found")
    except PermissionError:
        raise HTTPException(status_code=404, detail="not_found")

    return payload


@router.get("/{job_id}/events")
async def job_events(
    job_id: str,
    request: Request,
    access_token: str = Query(..., min_length=1),
):
    user_id, _username, _sid = await _authenticate_sse_token(access_token)
    await _ratelimit(f"rl:job_events:{user_id}", limit=120, window_sec=60)

    try:
        await asyncio.to_thread(_read_job_payload, job_id, user_id)
    except (KeyError, PermissionError):
        raise HTTPException(status_code=404, detail="not_found")

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(
        _job_events_stream(request, job_id, user_id),
        media_type="text/event-stream",
        headers=headers,
    )
