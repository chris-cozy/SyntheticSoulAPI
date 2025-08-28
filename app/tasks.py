import os
import asyncio
import json
import redis
from rq import get_current_job
from typing import Dict, Any
from app.models.request import MessageRequest
from app.services.message_processor_lite import process_message

def _publish_progress(job_id: str, progress: int) -> None:
    """
    Optional: publish progress events to Redis pub/sub (handy if you later add SSE/WS).
    Safe to no-op if you don't use it.
    """
    try:
        r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
        r.publish(f"job:{job_id}", json.dumps({"job_id": job_id, "progress": progress}))
    except Exception:
        pass

def send_message_task(request_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    RQ job entrypoint. Runs your async handle_message() and returns its result.
    RQ persists the return value as job.result; we also write simple progress meta.
    """
    job = get_current_job()
    # --- progress 0% ---
    job.meta["progress"] = 0
    job.save_meta()
    _publish_progress(job.id, 0)

    # Build your Pydantic input from dict (mirrors your current endpoint)
    message_req = MessageRequest(**request_payload)
    
    async def _run():
        return await process_message(message_req)

    # Run the async function in a private event loop
    result = asyncio.run(_run())

    # --- progress 100% ---
    job.meta["progress"] = 100
    job.save_meta()
    _publish_progress(job.id, 100)

    # Whatever your handle_message() returns should be JSON-serializable (e.g., {"response": "..."}).
    # RQ stores this in job.result for retrieval by the status endpoint.
    return result