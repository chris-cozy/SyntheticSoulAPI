import os
import sys
from rq import Worker, SimpleWorker, Queue, Connection
from dotenv import load_dotenv

from app.core.redis_queue import get_redis

load_dotenv()

listen = ['high', 'default', 'low']

def main():        
    with Connection(get_redis()):
        # macOS + forked workers can crash with ObjC runtime fork-safety checks.
        # Default to SimpleWorker (no fork) on darwin for local/dev stability.
        use_simple = sys.platform == "darwin" and os.getenv("RQ_USE_FORK_WORKER", "false").lower() not in {"1", "true", "yes"}
        worker_cls = SimpleWorker if use_simple else Worker
        worker = worker_cls([Queue(name) for name in listen])
    
        worker.work(with_scheduler=True)

if __name__ == '__main__':
    main()
