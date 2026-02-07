from typing import Optional
import ssl
import redis
from rq import Queue
from .config import APP_ENV, REDIS_CA_CERT, REDIS_TLS_INSECURE_SKIP_VERIFY, REDIS_URL


_rconn: Optional["redis.Redis"] = None
_queue: Optional[Queue] = None




def get_redis() -> "redis.Redis":
    global _rconn
    if _rconn is None:
        if REDIS_URL.startswith("rediss://"):
            ssl_cert_reqs = ssl.CERT_REQUIRED
            if REDIS_TLS_INSECURE_SKIP_VERIFY and APP_ENV in {"dev", "development", "local", "test"}:
                ssl_cert_reqs = ssl.CERT_NONE
            kwargs = {"ssl_cert_reqs": ssl_cert_reqs}
            if REDIS_CA_CERT:
                kwargs["ssl_ca_certs"] = REDIS_CA_CERT
            _rconn = redis.from_url(REDIS_URL, **kwargs)
        else:
            _rconn = redis.from_url(REDIS_URL)
    return _rconn




def get_queue(name: str = "default") -> Queue:
    global _queue
    if _queue is None:
        _queue = Queue(name, connection=get_redis())
    return _queue
