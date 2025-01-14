from contextlib import asynccontextmanager
import os
from fastapi import FastAPI, HTTPException
from app.constants.schemas import get_thought_schema
from app.models.request import MessageRequest, MessageResponse
from app.services.mental_service import process_message
from app.services.openai_service import get_structured_query_response
from app.services.data_service import grab_self, init_db, db_client
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing database...")
    await init_db()
    try:
        yield
    finally:
        if db_client:
            db_client.close()
            print("Database connection closed.")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    try:
        response = await get_structured_query_response([{"role": "user", "content": "Please give me a random thought."}], get_thought_schema())
        return {'message': response["thought"]}
    except Exception as e:
        print(f"Error in root endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/messages/submit", response_model=MessageResponse)
async def submit_message(request: MessageRequest):
    try:
        response = await process_message(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))