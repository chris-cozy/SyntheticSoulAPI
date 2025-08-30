from fastapi import APIRouter, HTTPException
from rq.job import Job

from app.core.redis_queue import get_redis
from app.domain.models import JobStatusResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("/{job_id}", response_model=JobStatusResponse)
async def job_status(job_id: str):
    try:
        job = Job.fetch(job_id, connection=get_redis())
    except Exception:
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
        payload["error"] = str(job.exc_info) if job.exc_info else "Job failed"

    return payload