"""Queue ordering uses real RQ/Redis when an isolated test URL is supplied."""
import asyncio
from contextlib import ExitStack
import os
import unittest
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

from redis import Redis
from redis.exceptions import LockNotOwnedError
from rq import Queue, SimpleWorker
from rq.job import Job
from rq.timeouts import TimerDeathPenalty

from app import tasks
from app.domain.models import InternalMessageRequest, GenerateReplyTaskResponse, MessageResponse
from app.services import background_queue as ordering


class ReservedBackgroundTests(unittest.TestCase):
    def test_reply_fills_reserved_job_without_enqueueing_again(self):
        job = Mock(id='reply', meta={'background_job_id': 'background'})
        background = Mock()
        background.args = ('lee', None, 'reply', 1)
        result = GenerateReplyTaskResponse(user_id='lee', queries=[{'role': 'user', 'content': 'Keep family private'}],
            message_response=MessageResponse(response='Understood', expression='neutral', time=1))
        with patch.object(tasks, 'get_current_job', return_value=job), \
             patch.object(tasks.Job, 'fetch', return_value=background), \
             patch.object(tasks, 'generate_response', AsyncMock(return_value=result)), \
             patch.object(tasks, 'get_queue') as queue, \
             patch.object(tasks, 'publish_progress'), patch.object(tasks, 'publish_job_event'), \
             patch.object(tasks.accounting, 'begin_run', AsyncMock()), \
             patch.object(tasks.accounting, 'mark_phase', AsyncMock()):
            tasks.generate_reply_task(InternalMessageRequest(message='Hi', type='dm', user_id='lee', sequence=1))
        self.assertEqual(background.args, ('lee', result.queries, 'reply', 1))
        background.save.assert_called_once_with(include_meta=False)
        queue.assert_not_called()

    def test_missing_reply_payload_cancels_slot_without_model_work(self):
        with patch.object(tasks, 'get_current_job', return_value=None), \
             patch.object(tasks.accounting, 'mark_phase', AsyncMock()) as phase, \
             patch.object(tasks, 'post_processing', AsyncMock()) as process:
            tasks.post_processing_task('lee', None, 'reply', 1)
        process.assert_not_awaited()
        self.assertEqual(phase.await_args.args, ('reply', 'background', 'cancelled'))


@unittest.skipUnless(os.getenv('ORDERING_TEST_REDIS_URL'), 'Requires isolated Redis; see contribution guide')
class RedisBackgroundOrderingTests(unittest.TestCase):
    def setUp(self):
        from scripts.local_validation import validate_services
        url = os.environ['ORDERING_TEST_REDIS_URL']
        validate_services('mongodb://127.0.0.1:27028', url, 'syntheticsoul_replay_ordering')
        self.redis = Redis.from_url(url)
        self.redis.flushdb()
        self.queue = Queue('ordering-' + uuid4().hex, connection=self.redis)
        self.worker = SimpleWorker([self.queue], connection=self.redis, log_job_description=False)
        self.worker.death_penalty_class = TimerDeathPenalty
        self.sequences, self.seen, self.facts = {}, [], {}
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.addCleanup(self.redis.close)
        self.addCleanup(self.redis.flushdb)

        async def reserve(user):
            self.sequences[user] = self.sequences.get(user, 0) + 1
            return self.sequences[user]
        async def reply(request):
            if request.message == 'fail-reply':
                raise RuntimeError('synthetic reply failure')
            return GenerateReplyTaskResponse(user_id=request.user_id,
                queries=[{'role': 'user', 'content': request.message}],
                message_response=MessageResponse(response='Understood', expression='neutral', time=1))
        async def background(user, queries, *, sequence):
            self.seen.append((user, sequence))
            if queries[0]['content'] == 'fail-background':
                raise RuntimeError('synthetic background failure')
            if queries[0]['content'] == 'Keep family private':
                self.facts[user] = 'family private'
            elif queries[0]['content'] == 'Thanks':
                self.assertEqual(self.facts.get(user), 'family private')
        self.stack.enter_context(patch.object(ordering.database, 'next_interaction_sequence', AsyncMock(side_effect=reserve)))
        self.stack.enter_context(patch.object(tasks, 'generate_response', AsyncMock(side_effect=reply)))
        self.stack.enter_context(patch.object(tasks, 'post_processing', AsyncMock(side_effect=background)))
        self.stack.enter_context(patch.object(tasks, 'publish_progress'))
        self.stack.enter_context(patch.object(tasks, 'publish_job_event'))
        for name in ('begin_run', 'mark_phase'):
            self.stack.enter_context(patch.object(tasks.accounting, name, AsyncMock()))

    def submit(self, message, user='lee'):
        return asyncio.run(ordering.enqueue_exchange(self.queue,
            InternalMessageRequest(user_id=user, message=message, type='dm'), uuid4().hex))

    def execute(self, job):
        self.queue.remove(job.id)
        self.worker.execute_job(Job.fetch(job.id, connection=self.redis), self.queue)

    def drain(self):
        worker = SimpleWorker([self.queue], connection=self.redis, log_job_description=False)
        worker.death_penalty_class = TimerDeathPenalty
        worker.work(burst=True, logging_level='CRITICAL')

    def test_faster_second_reply_cannot_skip_first_boundary_and_payload_survives_reply_expiry(self):
        first, second = self.submit('Keep family private'), self.submit('Thanks')
        self.execute(second)
        self.assertEqual(Job.fetch(second.id + ':background', connection=self.redis).get_status(), 'deferred')
        # A deferred background owns its input even after the reply disappears.
        Job.fetch(second.id, connection=self.redis).delete()
        self.drain()
        self.assertEqual(self.seen, [('lee', 1), ('lee', 2)])
        self.assertEqual(self.facts['lee'], 'family private')
        self.assertEqual(Job.fetch(first.id + ':background', connection=self.redis).get_status(), 'finished')

    def test_other_user_can_finish_while_first_user_reply_is_pending(self):
        self.submit('Keep family private')
        other = self.submit('Hello', user='alex')
        self.execute(other)
        self.execute(Job.fetch(other.id + ':background', connection=self.redis))
        self.assertEqual(self.seen, [('alex', 1)])

    def test_failed_reply_or_background_releases_later_exchange(self):
        for failure in ('fail-reply', 'fail-background'):
            with self.subTest(failure=failure):
                user = failure
                first, second = self.submit(failure, user), self.submit('Hello', user)
                self.execute(second)
                self.drain()
                self.assertEqual(Job.fetch(second.id + ':background', connection=self.redis).get_status(), 'finished')
                self.assertIn((user, 2), self.seen)

    def test_already_failed_predecessor_does_not_leave_new_job_deferred(self):
        self.submit('fail-background')
        self.drain()
        second = self.submit('Hello')
        self.drain()
        self.assertEqual(Job.fetch(second.id + ':background', connection=self.redis).get_status(), 'finished')

    def test_transaction_failure_leaves_no_partial_chain_and_sequence_gap_is_harmless(self):
        # Fail after both job saves have been added to the transaction.
        with patch.object(Job, 'register_dependency', side_effect=RuntimeError('synthetic enqueue failure')):
            with self.assertRaises(RuntimeError):
                self.submit('Unqueued')
        self.assertIsNone(self.redis.get(ordering._order_key('lee')))
        self.assertFalse(self.redis.keys('rq:job:*'))
        job = self.submit('Hello')
        self.drain()
        self.assertEqual(self.seen, [('lee', 2)])
        self.assertEqual(Job.fetch(job.id + ':background', connection=self.redis).get_status(), 'finished')

    def test_lost_submission_lease_cannot_commit_partial_jobs(self):
        key = ordering._order_key('lee')
        lock = self.redis.lock(key + ':submit', timeout=60, thread_local=False)
        self.assertTrue(lock.acquire())
        original = self.queue._enqueue_job
        def expire_lock(*args, **kwargs):
            result = original(*args, **kwargs)
            self.redis.delete(lock.name)
            return result
        with patch.object(self.queue, '_enqueue_job', side_effect=expire_lock), self.assertRaises(LockNotOwnedError):
            ordering._enqueue(self.queue, InternalMessageRequest(user_id='lee', message='Hello', type='dm', sequence=1),
                              'reply', 'reply:background', key, lock)
        self.assertIsNone(self.redis.get(key))
        self.assertFalse(self.redis.keys('rq:job:*'))

    def test_concurrent_submissions_chain_in_reserved_sequence_order(self):
        async def submit_all():
            return await asyncio.gather(*(ordering.enqueue_exchange(self.queue,
                InternalMessageRequest(user_id='lee', message='Hello', type='dm'), uuid4().hex) for _ in range(5)))
        jobs = asyncio.run(submit_all())
        for job in sorted(jobs, key=lambda j:j.args[0].sequence, reverse=True):
            self.execute(job)
        self.drain()
        self.assertEqual(self.seen, [('lee', i) for i in range(1, 6)])
