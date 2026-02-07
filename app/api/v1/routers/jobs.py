from fastapi import APIRouter, Depends, HTTPException
from rq.job import Job

from app.core.redis_queue import get_redis
from app.domain.models import JobStatusResponse
from app.services.auth import _ratelimit, auth_guard, identity

router = APIRouter(prefix="/jobs", tags=["jobs"], dependencies=[Depends(auth_guard)])

@router.get("/{job_id}", response_model=JobStatusResponse)
async def job_status(job_id: str, ident=Depends(identity)):
    user_id, _username, _sid = ident
    await _ratelimit(f"rl:job_poll:{user_id}", limit=120, window_sec=60)
    try:
        job = Job.fetch(job_id, connection=get_redis())
    except Exception:
        raise HTTPException(status_code=404, detail="not_found")

    if (job.meta or {}).get("owner_user_id") != user_id:
        raise HTTPException(status_code=404, detail="not_found")

    # Normalize RQ statuses to a small set
    rq_status = job.get_status(refresh=True)
    if rq_status in ("queued", "deferred"):
        status = "queued"
    elif rq_status in ("started",):
        status = "running"
    elif rq_status in ("finished",):
        status = "succeeded"
    elif rq_status in ("failed",):
        status = "failed"
    else:
        status = rq_status

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
