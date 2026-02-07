import ssl
import json
import redis

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
