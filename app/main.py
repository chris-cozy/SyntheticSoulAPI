from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.constants.schemas import get_thought_schema
from app.models.request import MessageRequest, MessageResponse
from app.services.brain_service import periodic_thinking, handle_message
from app.services.openai_service import get_structured_response
from app.services.data_service import get_all_agents, init_db, db_client
from bson.json_util import dumps
from dotenv import load_dotenv
import os
import asyncio

from app.services.util_service import start_emotion_decay

load_dotenv()

API_VERSION = "1.0.0"

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing database...")
    await init_db()
    print('Starting emotional decay...')
    decay_task = asyncio.create_task(start_emotion_decay())
    print('Starting to think...')
    asyncio.create_task(periodic_thinking())
    try:
        yield
    finally:
        if db_client:
            db_client.close()
            print("Database connection closed.")
        decay_task.cancel()
        print("Emotion decay loop stopped.")

app = FastAPI(lifespan=lifespan)

# --- CORS config ---
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    os.getenv('WEB_UI_DOMAIN'),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,                  # set to True only if you send cookies/Authorization
    allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"],
    allow_headers=["Content-Type","Authorization"],  # add any custom headers you use
    expose_headers=[],                       # optional
)

@app.get("/")
async def root():
    try:
        response = await get_structured_response([{"role": "user", "content": "Please give me a random thought."}], get_thought_schema())
        return {'message': response["thought"]}
    except Exception as e:
        print(f"Error in root endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/messages/submit", response_model=MessageResponse)
async def submit_message(request: MessageRequest):
    try:
        response = await handle_message(request)
        print(response)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/agents")
async def get_agents():
    try:
        response = await get_all_agents()
        serialized_response = dumps(response)  # Serialize the response
        print(serialized_response)
        return {'agents': serialized_response}
    except Exception as e:
        print(f"Error in agents endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))