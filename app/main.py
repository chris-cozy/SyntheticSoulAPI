from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from app.constants.schemas import get_thought_schema
from app.domain.models import MessageRequest
from app.services.thinking import periodic_thinking
from app.services.openai_service import get_structured_response
from app.services.data_service import get_all_agents, grab_self, init_db, db_client
from bson.json_util import dumps
from dotenv import load_dotenv
import os
import asyncio
import redis
import ssl
from rq import Queue
from rq.job import Job

from app.services.util_service import start_emotion_decay

load_dotenv()

agent = os.getenv("BOT_NAME")

REDIS_URL = os.getenv("REDIS_TLS_URL") or os.getenv("REDIS_URL", "redis://localhost:6379/0")
if REDIS_URL.startswith("rediss://"):
    rconn = redis.from_url(REDIS_URL, ssl_cert_reqs=ssl.CERT_NONE)
else:
    rconn = redis.from_url(REDIS_URL)

q = Queue("default", connection=rconn)

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
    
@app.post("/messages/submit")
async def submit_message(request: MessageRequest):
    try:
        # enqueue the job into RQ; pass the request body as a dict
        job = q.enqueue(
            "app.tasks.send_message_task",   # dotted path to the function we created
            request.model_dump(),            # pydantic -> dict
            job_timeout=600                  # safety cap
        )
        
        # return 202 + Location header so clients can poll
        response =  Response(
            content=dumps({"job_id": job.id, "status": job.get_status()}),
            status_code=202,
            headers={
                "Location": f"/jobs/{job.id}",
                "Retry-After": "3"
            },
            media_type="application/json"
        )
        
        print(response)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# --- NEW: status endpoint for polling ---
@app.get("/jobs/{job_id}")
async def job_status(job_id: str):
    try:
        job = Job.fetch(job_id, connection=rconn)
    except Exception:
        raise HTTPException(status_code=404, detail="not_found")

    # Normalize RQ statuses to a small set
    rq_status = job.get_status(refresh=True)
    if rq_status in ("queued", "deferred"):
        status = "queued"
    elif rq_status in ("started",):
        status = "running"
    elif rq_status in ("finished",):
        status = "succeeded"
    elif rq_status in ("failed",):
        status = "failed"
    else:
        status = rq_status

    payload = {
        "job_id": job.id,
        "status": status,
        "progress": (job.meta or {}).get("progress"),
    }

    if status == "succeeded":
        payload["result"] = job.result  # whatever send_message_task returned
    if status == "failed":
        payload["error"] = str(job.exc_info) if job.exc_info else "Job failed"

    return payload
    
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
    
    
@app.get("/active_agent")
async def get_active_agent():
    try:
        response = await grab_self(agent)
        serialized_response = dumps(response)  # Serialize the response
        print(serialized_response)
        return {'agent': serialized_response}
    except Exception as e:
        print(f"Error in agent endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))