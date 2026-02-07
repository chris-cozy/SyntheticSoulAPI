import asyncio
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from rq import Queue, Worker

from app.core.redis_queue import get_redis
from app.core.config import API_BASE_PATH, API_MAJOR_VERSION, API_MINOR_VERSION, API_PATCH_VERSION, API_VERSION

router = APIRouter(prefix="/meta", tags=["meta"])

@router.get("/version")
async def version():
    return {
        "version": API_VERSION,
        "api_base_path": API_BASE_PATH,
        "semver": {
            "major": API_MAJOR_VERSION,
            "minor": API_MINOR_VERSION,
            "patch": API_PATCH_VERSION,
        },
        "versioning_policy": {
            "url_versioning": "major",
            "breaking_changes": "major-only",
            "non_breaking_changes": "minor-or-patch",
        },
    }

@router.get("/ping")
async def ping():
    return {"status": "ok"}


def _queue_snapshot() -> dict:
    conn = get_redis()
    queue_names = ("high", "default", "low")
    queue_sizes: dict[str, int] = {}

    for name in queue_names:
        queue_sizes[name] = len(Queue(name, connection=conn))

    workers = Worker.all(connection=conn)
    worker_states = [
        {
            "name": w.name,
            "state": w.get_state(),
            "queues": [q.name for q in w.queues],
        }
        for w in workers
    ]

    return {
        "redis_ok": bool(conn.ping()),
        "worker_count": len(workers),
        "workers": worker_states,
        "queues": queue_sizes,
        "total_backlog": sum(queue_sizes.values()),
    }


@router.get("/queue")
async def queue_health():
    """
    Lightweight queue diagnostics for local/dev troubleshooting.
    """
    try:
        snapshot = await asyncio.to_thread(_queue_snapshot)
    except Exception:
        raise HTTPException(status_code=503, detail="queue_unavailable")

    status = "ok" if snapshot["worker_count"] > 0 else "degraded"
    return {
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **snapshot,
    }
