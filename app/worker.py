import os
import asyncio
import redis
import ssl
from rq import SimpleWorker, Worker, Queue, Connection
from dotenv import load_dotenv

from app.core.config import WINDOWS_ENV
from app.core.redis_queue import get_redis

load_dotenv()

listen = ['high', 'default', 'low']

def main():        
    with Connection(get_redis()):
        worker = Worker([Queue(name) for name in listen])
        if WINDOWS_ENV:
            worker = SimpleWorker([Queue(name) for name in listen])
            
        worker.work(with_scheduler=True)

if __name__ == '__main__':
    main()