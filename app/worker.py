import os
import signal
import sys
from rq import Worker, SimpleWorker, Queue, Connection
from rq.timeouts import TimerDeathPenalty
from dotenv import load_dotenv

from app.core.redis_queue import get_redis

load_dotenv()

listen = ['high', 'default', 'low']

def main():        
    with Connection(get_redis()):
        # Platforms without os.fork (e.g., Windows) must use SimpleWorker.
        # macOS also defaults to SimpleWorker to avoid ObjC fork-safety crashes.
        force_fork = os.getenv("RQ_USE_FORK_WORKER", "false").lower() in {"1", "true", "yes"}
        can_fork = hasattr(os, "fork")
        if not can_fork:
            use_simple = True
        elif force_fork:
            use_simple = False
        else:
            use_simple = sys.platform == "darwin"
        worker_cls = SimpleWorker if use_simple else Worker
        worker = worker_cls([Queue(name) for name in listen])

        # Windows does not support SIGALRM; use thread-based timeout enforcement.
        if not hasattr(signal, "SIGALRM"):
            worker.death_penalty_class = TimerDeathPenalty
    
        worker.work(with_scheduler=True)

if __name__ == '__main__':
    main()
