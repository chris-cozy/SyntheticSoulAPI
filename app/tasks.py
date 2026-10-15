import asyncio
from uuid import uuid4
from rq import get_current_job
from rq.job import Job
from typing import Dict, Any
from app.core.redis_queue import get_queue
from app.domain.models import InternalMessageRequest
from app.services.message_processor import generate_response, post_processing
from app.services.progress import publish_job_event, publish_progress
from app.services import accounting
from app.core import config

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
        
    run_id = str(job.id) if job else str(uuid4())
    _run_async(accounting.begin_run(run_id, request.user_id, metadata={"agent_name": config.AGENT_NAME,
        "variant": "decisions" if config.DECISIONS_ENABLED and config.LLM_MODE == "hosted" else "baseline",
        "flags": {"decisions": config.DECISIONS_ENABLED, "features": ",".join(sorted(config.DECISIONS_FEATURES))}}))
    _run_async(accounting.mark_phase(run_id, "reply", "running", job_id=run_id))
    try:
        # Run async stage on persistent loop for worker process.
        with accounting.scope(run_id, request.user_id, phase="reply", flags={"decisions": config.DECISIONS_ENABLED, "features": ",".join(sorted(config.DECISIONS_FEATURES))}):
            result = _run_async(generate_response(request))
        _run_async(accounting.mark_phase(run_id, "reply", "completed"))
        
        user_id = result.user_id
        queries = result.queries
        
        # Post-processing is best-effort and should not fail the primary reply job.
        try:
            background_id = job.meta.get("background_job_id") if job else None
            if background_id:
                # Store the payload on the deferred job, not the expiring reply
                # result. Its dependencies keep it from running until we finish.
                background = Job.fetch(background_id, connection=job.connection)
                arguments = list(background.args)  # Load RQ's lazy function/argument data before replacing it.
                arguments[1] = queries
                background.args = tuple(arguments)
                background.save(include_meta=False)
            else:
                # Compatibility for jobs submitted before ordered reservation.
                q = get_queue()
                background_id = str(uuid4())
                _run_async(accounting.mark_phase(run_id, "background", "pending", job_id=background_id))
                q.enqueue(post_processing_task, user_id, queries, run_id, request.sequence,
                    job_id=background_id, depends_on=job, job_timeout=600)
        except Exception as e:
            _run_async(accounting.mark_phase(run_id, "background", "failed", error="background_enqueue_failed"))
            print(f"Warning - failed to enqueue post_processing_task: {e}")

        if job:
            job.meta["progress"] = 0.6
            job.save_meta()
            publish_progress(job.id, 0.6)
            publish_job_event(job.id, progress=1.0, status="succeeded")

        # Return plain dict to keep job result serialization simple for API/UI clients.
        return result.message_response.model_dump()
    except Exception:
        _run_async(accounting.mark_phase(run_id, "reply", "failed", error="reply_failed"))
        _run_async(accounting.mark_phase(run_id, "background", "cancelled", error="reply_failed"))
        if job:
            publish_job_event(job.id, status="failed", error="job_failed")
        raise


def post_processing_task(user_id: str, queries: list | None, exchange_id: str | None = None, sequence: int | None = None):
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

    run_id = exchange_id or str(job.id if job else uuid4())
    if exchange_id is None:
        _run_async(accounting.begin_run(run_id, user_id, kind="background", metadata={"variant": "legacy_queued_background"}))
    if queries is None:
        # A failed reply never filled its reserved payload. Finish this queue
        # slot without model calls so the next exchange can proceed.
        _run_async(accounting.mark_phase(run_id, "background", "cancelled", error="background_payload_unavailable"))
        return
    _run_async(accounting.mark_phase(run_id, "background", "running", job_id=job.id if job else None))
    try:
        with accounting.scope(run_id, user_id, phase="background", flags={"decisions": config.DECISIONS_ENABLED, "features": ",".join(sorted(config.DECISIONS_FEATURES))}):
            _run_async(post_processing(user_id, queries, sequence=sequence))
        _run_async(accounting.mark_phase(run_id, "background", "completed"))
    except Exception:
        _run_async(accounting.mark_phase(run_id, "background", "failed", error="post_processing_failed"))
        raise

    if job:
        job.meta["progress"] = 1.0
        job.save_meta()
