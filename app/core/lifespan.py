from contextlib import asynccontextmanager
from contextlib import suppress
import asyncio
from fastapi import FastAPI

import app.services.database as database_service
from app.core.config import validate_llm_configuration, validate_security_configuration
from app.services.emotion_decay import emotion_decay_loop
from app.services.expressions import refresh_expressions_cache
from app.services.thinking import periodic_thinking

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    validate_security_configuration()
    validate_llm_configuration()

    print("Initializing database...")
    await database_service.init_db()

    print("Starting emotional decay...")
    decay_task = asyncio.create_task(emotion_decay_loop())

    print("Starting to think...")
    thinking_task = asyncio.create_task(periodic_thinking())
    
    print("Refreshing expressions cache...") 
    refresh_expressions_cache()

    try:
        yield
    finally:
        if database_service._db_client:
            database_service._db_client.close()
            print("Database connection closed.")

        decay_task.cancel()
        thinking_task.cancel()
        with suppress(asyncio.CancelledError):
            await decay_task
        with suppress(asyncio.CancelledError):
            await thinking_task

        print("Emotion decay loop stopped.")
