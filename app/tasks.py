import os
import asyncio
import json
import redis
from rq import get_current_job
from typing import Dict, Any
from app.domain.models import InternalMessageRequest
from app.services.message_processor import process_message
from app.services.progress import publish_progress

def send_message_task(request_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    RQ job entrypoint. Runs your async handle_message() and returns its result.
    RQ persists the return value as job.result; we also write simple progress meta.
    """
    job = get_current_job()
    # --- progress 0% ---
    job.meta["progress"] = 0
    job.save_meta()
    publish_progress(job.id, 0)

    # Build your Pydantic input from dict (mirrors your current endpoint)
    message_req = InternalMessageRequest(**request_payload)
    
    async def _run():
        return await process_message(message_req)

    # Run the async function in a private event loop
    result = asyncio.run(_run())

    # --- progress 100% ---
    job.meta["progress"] = 100
    job.save_meta()
    publish_progress(job.id, 100)

    # Whatever your handle_message() returns should be JSON-serializable (e.g., {"response": "..."}).
    # RQ stores this in job.result for retrieval by the status endpoint.
    return result