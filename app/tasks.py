import os
import asyncio
import json
import redis
from rq import get_current_job
from typing import Dict, Any
from app.core.redis_queue import get_queue
from app.domain.models import InternalMessageRequest
from app.services.message_processor import generate_response, post_processing
from app.services.progress import publish_progress

def generate_reply_task(request: InternalMessageRequest) -> Dict[str, Any]:
    """
    RQ job entrypoint. Runs your async handle_message() and returns its result.
    RQ persists the return value as job.result; we also write simple progress meta.
    """
    try:
        job = get_current_job()
        if job:
            job.meta["progress"] = 0.1
            job.save_meta()
            publish_progress(job.id, 0.1)
    except Exception:
        job = None
        
    # Run the async first stage in a private event loop
    result = asyncio.run(generate_response(request))
    
    user_id = result.user_id
    queries = result.queries
    
    q = get_queue()
    q.enqueue(
        post_processing_task,
        user_id,
        queries,
        depends_on=job,     # ensures it runs after this job finishes
        job_timeout=600,
    )

    if job:
        job.meta["progress"] = 0.6
        job.save_meta()
        publish_progress(job.id, 0.6)

    # IMPORTANT: return ONLY the MessageResponse so client contracts remain unchanged
    # Use model.dump() for Pydantic object → plain dict (if needed)
    return result.message_response


def post_processing_task(user_id: str, queries: list):
    """
    RQ worker entrypoint for the background post-processing stage.
    """
    try:
        job = get_current_job()
        if job:
            job.meta["progress"] = 0.8
            job.save_meta()
    except Exception:
        job = None

    asyncio.run(post_processing(user_id, queries))

    if job:
        job.meta["progress"] = 1.0
        job.save_meta()