from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI

from app.services.database import init_db, _db_client
from app.services.emotion_decay import emotion_decay_loop
from app.services.thinking import periodic_thinking

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    print("Initializing database...")
    await init_db()

    print("Starting emotional decay...")
    decay_task = asyncio.create_task(emotion_decay_loop())

    print("Starting to think...")
    asyncio.create_task(periodic_thinking())

    try:
        yield
    finally:
        if _db_client:
            _db_client.close()
            print("Database connection closed.")
        decay_task.cancel()
        print("Emotion decay loop stopped.")