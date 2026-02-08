import ssl
import json
import redis
from typing import Optional

from app.core.config import APP_ENV, REDIS_CA_CERT, REDIS_TLS_INSECURE_SKIP_VERIFY, REDIS_URL

def _redis_from_env():
    url = REDIS_URL
    if url.startswith("rediss://"):
        ssl_cert_reqs = ssl.CERT_REQUIRED
        if REDIS_TLS_INSECURE_SKIP_VERIFY and APP_ENV in {"dev", "development", "local", "test"}:
            ssl_cert_reqs = ssl.CERT_NONE
        kwargs = {"ssl_cert_reqs": ssl_cert_reqs}
        if REDIS_CA_CERT:
            kwargs["ssl_ca_certs"] = REDIS_CA_CERT
        return redis.from_url(url, **kwargs)
    return redis.from_url(url)

def publish_job_event(
    job_id: str,
    *,
    progress: Optional[float] = None,
    status: Optional[str] = None,
    error: Optional[str] = None,
) -> None:
    """
    Publish a job event to Redis pub/sub.
    Channel: job:{job_id}
    Payload keys: job_id, progress?, status?, error?
    """
    payload = {"job_id": job_id}
    if progress is not None:
        payload["progress"] = float(progress)
    if status:
        payload["status"] = status
    if error:
        payload["error"] = error

    try:
        r = _redis_from_env()
        r.publish(f"job:{job_id}", json.dumps(payload))
    except Exception:
        # Swallow errors so jobs don’t crash if pub/sub is unavailable
        pass


def publish_progress(job_id: str, progress: int) -> None:
    """
    Publish progress events to Redis pub/sub. Safe to no-op on failure.
    Channel: job:{job_id}, message: {"job_id": ..., "progress": ...}
    """
    publish_job_event(job_id, progress=progress, status="running")
