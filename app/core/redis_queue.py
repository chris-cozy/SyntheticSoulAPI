from typing import Optional
import ssl
import redis
from rq import Queue
from .config import REDIS_URL


_rconn: Optional["redis.Redis"] = None
_queue: Optional[Queue] = None




def get_redis() -> "redis.Redis":
    global _rconn
    if _rconn is None:
        if REDIS_URL.startswith("rediss://"):
            _rconn = redis.from_url(REDIS_URL, ssl_cert_reqs=ssl.CERT_NONE)
        else:
            _rconn = redis.from_url(REDIS_URL)
    return _rconn




def get_queue(name: str = "default") -> Queue:
    global _queue
    if _queue is None:
        _queue = Queue(name, connection=get_redis())
    return _queue