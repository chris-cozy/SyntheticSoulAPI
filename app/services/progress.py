from typing import Optional
from rq.job import Job

import os
import ssl
import json
import redis

def _redis_from_env():
    url = os.getenv("REDIS_TLS_URL") or os.getenv("REDIS_URL", "redis://localhost:6379/0")
    if url.startswith("rediss://"):
        return redis.from_url(url, ssl_cert_reqs=ssl.CERT_NONE)
    return redis.from_url(url)

def publish_progress(job_id: str, progress: int) -> None:
    """
    Publish progress events to Redis pub/sub. Safe to no-op on failure.
    Channel: job:{job_id}, message: {"job_id": ..., "progress": ...}
    """
    try:
        r = _redis_from_env()
        r.publish(f"job:{job_id}", json.dumps({"job_id": job_id, "progress": progress}))
    except Exception:
        # Swallow errors so jobs don’t crash if pub/sub is unavailable
        pass