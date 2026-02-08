import asyncio
from rq import get_current_job
from typing import Dict, Any
from app.core.redis_queue import get_queue
from app.domain.models import InternalMessageRequest
from app.services.message_processor import generate_response, post_processing
from app.services.progress import publish_job_event, publish_progress

_worker_loop: asyncio.AbstractEventLoop | None = None


def _get_worker_loop() -> asyncio.AbstractEventLoop:
    global _worker_loop
    if _worker_loop is None or _worker_loop.is_closed():
        _worker_loop = asyncio.new_event_loop()
    return _worker_loop


def _run_async(coro):
    """
    Run coroutine on a persistent per-process event loop.
    Avoids creating/closing loops per job, which can invalidate async clients
    (e.g., Motor) in SimpleWorker mode on macOS.
    """
    loop = _get_worker_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


def generate_reply_task(request: InternalMessageRequest) -> Dict[str, Any]:
    """
    RQ job entrypoint. Runs your async handle_message() and returns its result.
    RQ persists the return value as job.result; we also write simple progress meta.
    """
    job = None
    try:
        job = get_current_job()
        if job:
            job.meta["progress"] = 0.1
            job.save_meta()
            publish_progress(job.id, 0.1)
    except Exception:
        pass
        
    try:
        # Run async stage on persistent loop for worker process.
        result = _run_async(generate_response(request))
        
        user_id = result.user_id
        queries = result.queries
        
        # Post-processing is best-effort and should not fail the primary reply job.
        try:
            q = get_queue()
            q.enqueue(
                post_processing_task,
                user_id,
                queries,
                depends_on=job,     # ensures it runs after this job finishes
                job_timeout=600,
            )
        except Exception as e:
            print(f"Warning - failed to enqueue post_processing_task: {e}")

        if job:
            job.meta["progress"] = 0.6
            job.save_meta()
            publish_progress(job.id, 0.6)
            publish_job_event(job.id, progress=1.0, status="succeeded")

        # Return plain dict to keep job result serialization simple for API/UI clients.
        return result.message_response.model_dump()
    except Exception:
        if job:
            publish_job_event(job.id, status="failed", error="job_failed")
        raise


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

    _run_async(post_processing(user_id, queries))

    if job:
        job.meta["progress"] = 1.0
        job.save_meta()
