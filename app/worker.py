import os
import asyncio
import redis
import ssl
from rq import Worker, Queue, Connection
from dotenv import load_dotenv

load_dotenv()

listen = ['high', 'default', 'low']

REDIS_URL = os.getenv("REDIS_TLS_URL") or os.getenv("REDIS_URL", "redis://localhost:6379/0")

def main():
    if REDIS_URL.startswith("rediss://"):
        conn = redis.from_url(REDIS_URL, ssl_cert_reqs=ssl.CERT_NONE)
    else:
        conn = redis.from_url(REDIS_URL)
        
    with Connection(conn):
        worker = Worker([Queue(name) for name in listen])
        worker.work(with_scheduler=True)

if __name__ == '__main__':
    main()