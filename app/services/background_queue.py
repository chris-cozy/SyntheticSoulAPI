"""Reserve per-user background dependencies before replies can finish out of order."""
import asyncio
import hashlib
import json
import logging

from redis.exceptions import LockNotOwnedError, RedisError, WatchError
from rq.job import Dependency, Job, JobStatus

from app.core import config
from app.services import accounting, database


def _order_key(user_id):
    identity = json.dumps([config.DATABASE_NAME, config.AGENT_NAME, user_id])
    return 'ss:background:' + hashlib.sha256(identity.encode()).hexdigest()


def _enqueue(queue, request, job_id, background_id, key, lock):
    from app.tasks import generate_reply_task, post_processing_task

    # Saving both jobs, their dependencies and the tail in one transaction keeps
    # a failed submission from leaving a partial chain. WATCH also guards a
    # predecessor finishing/failing and the submission lock expiring.
    with queue.connection.pipeline() as pipe:
        while True:
            try:
                pipe.watch(key, lock.name)
                if pipe.get(lock.name) != lock.local.token:
                    raise LockNotOwnedError('Submission lock expired')
                previous = pipe.get(key)
                dependencies = [job_id]
                if previous:
                    previous = previous.decode()
                    previous_key = Job.key_for(previous)
                    pipe.watch(previous_key)
                    status = pipe.hget(previous_key, 'status')
                    # RQ 1.16's setup_dependencies defers even already-failed
                    # parents. Only active predecessors need a dependency.
                    if status and status.decode() not in {'finished', 'failed', 'stopped', 'canceled'}:
                        dependencies.append(previous)
                reply = queue.create_job(generate_reply_task, args=(request,), job_id=job_id,
                    timeout=600, meta={'owner_user_id': request.user_id, 'background_job_id': background_id})
                background = queue.create_job(post_processing_task,
                    args=(request.user_id, None, job_id, request.sequence), job_id=background_id,
                    timeout=600, status=JobStatus.DEFERRED,
                    depends_on=Dependency(dependencies, allow_failure=True))
                pipe.multi()
                # The reply has no dependencies. Bypass RQ's dependency setup
                # because this transaction explicitly registers the background.
                queue._enqueue_job(reply, pipeline=pipe)
                background.save(pipeline=pipe)
                background.register_dependency(pipeline=pipe)
                pipe.set(key, background_id)
                pipe.execute()
                return reply
            except WatchError:
                continue


async def enqueue_exchange(queue, request, job_id):
    key = _order_key(request.user_id)
    # Serialize only sequence allocation and enqueueing, never model calls or
    # waiting jobs. Different users/agents have independent submission locks.
    lock = queue.connection.lock(key + ':submit', timeout=60, blocking_timeout=5, thread_local=False)
    if not await asyncio.to_thread(lock.acquire):
        raise TimeoutError('Another submission for this user is still being queued')
    try:
        sequence = await database.next_interaction_sequence(request.user_id)
        ordered = request.model_copy(update={'sequence': sequence})
        background_id = job_id + ':background'
        await accounting.mark_phase(job_id, 'background', 'pending', job_id=background_id)
        return await asyncio.to_thread(_enqueue, queue, ordered, job_id, background_id, key, lock)
    finally:
        try:
            await asyncio.to_thread(lock.release)
        except LockNotOwnedError:
            pass  # An expired lock cannot delete another submitter's lock.
        except RedisError:
            logging.getLogger(__name__).warning('Background submission lock release failed; lease will expire')
