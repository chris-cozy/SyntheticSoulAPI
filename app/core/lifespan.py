from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI

from app.services.data_service import init_db, db_client
from app.services.util_service import start_emotion_decay
from app.services.thinking import periodic_thinking

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing database...")
    await init_db()

    print("Starting emotional decay...")
    decay_task = asyncio.create_task(start_emotion_decay())

    print("Starting to think...")
    asyncio.create_task(periodic_thinking())

    try:
        yield
    finally:
        if db_client:
            db_client.close()
            print("Database connection closed.")
        decay_task.cancel()
        print("Emotion decay loop stopped.")