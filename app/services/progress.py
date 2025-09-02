import ssl
import json
import redis

from app.core.config import REDIS_URL

def _redis_from_env():
    url = REDIS_URL
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