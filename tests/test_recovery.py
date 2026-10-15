import asyncio
import copy
import unittest
from unittest.mock import AsyncMock, patch

import httpx2
import openai as sdk
from app.services import accounting, recovery, openai as generation, interaction_decisions
from tests.test_interaction_state import StateCollection, agent_doc, partial_answers


class RecoveryTests(unittest.IsolatedAsyncioTestCase):
    async def test_failed_native_prose_uses_single_recovery_with_same_fixed_schema(self):
        schema = {"type": "json_schema", "json_schema": {"name": "accepted_reply", "schema": {"properties": {"response": {"type": "object"}}}}}
        writer = AsyncMock(side_effect=[None, {"response": {"message": "Thanks"}}, None])
        @recovery.phase("reply")
        async def run():
            result = await recovery.query([], schema, stage="reply_writer", fallback=False, recover_generation=True, writer=writer)
            self.assertEqual(result["response"]["message"], "Thanks")
            return await recovery.query([], schema, stage="later_writer", fallback=False, recover_generation=True, writer=writer)
        self.assertIsNone(await run())
        self.assertEqual(writer.await_count, 3)
        self.assertEqual([call.kwargs["fallback"] for call in writer.await_args_list], [False, True, False])
        self.assertEqual(writer.await_args_list[1].args[1], schema)
        self.assertEqual(writer.await_args_list[1].kwargs["stage"], "reply_writer_recovery")

    async def test_one_attempt_including_failed_recovery_and_event(self):
        writer = AsyncMock(return_value=None)
        @recovery.phase("reply")
        async def run():
            await recovery.query([], {}, stage="state", writer=writer)
            return await recovery.query([], {}, stage="perception", writer=writer)
        with accounting.scope("run", "owner"), patch.object(accounting, "record_event", AsyncMock()) as event:
            self.assertIsNone(await run())
        writer.assert_awaited_once()
        self.assertEqual(event.await_args.args, ("run", "recovery_exhausted"))
        self.assertEqual(event.await_args.kwargs, {"stage": "perception"})
        self.assertFalse(recovery.active())

    async def test_normal_prose_and_baseline_do_not_consume_recovery(self):
        writer = AsyncMock(return_value={"thought": "A thought."})
        @recovery.phase("background")
        async def run():
            await recovery.query([], {}, fallback=False, writer=writer)
            await recovery.query([], {}, fallback=True, writer=writer)
            await recovery.query([], {}, fallback=False, writer=writer)
            await recovery.query([], {}, fallback=True, writer=writer)
        await run()
        self.assertEqual(writer.await_count, 3)
        self.assertEqual([c.kwargs["fallback"] for c in writer.await_args_list], [False, True, False])

    async def test_parallel_calls_share_one_budget_but_distinct_phases_reset(self):
        writer = AsyncMock(return_value={})
        @recovery.phase("reply")
        async def run():
            return await asyncio.gather(*(recovery.query([], {}, writer=writer) for _ in range(3)))
        self.assertEqual(sum(x is not None for x in await run()), 1)
        self.assertEqual(sum(x is not None for x in await run()), 1)
        self.assertEqual(writer.await_count, 2)

    async def test_distinct_jobs_do_not_share_recovery_budget(self):
        writer = AsyncMock(return_value={})
        @recovery.phase("background")
        async def run():
            return await recovery.query([], {}, writer=writer)
        results = await asyncio.gather(run(), run())
        self.assertEqual(results, [{}, {}])
        self.assertEqual(writer.await_count, 2)

    async def test_exception_restores_phase_and_active_context(self):
        @recovery.phase("autonomy")
        async def run(writer):
            return await recovery.query([], {}, writer=writer)
        with self.assertRaises(RuntimeError):
            await run(AsyncMock(side_effect=RuntimeError("synthetic failure")))
        self.assertFalse(recovery.active())
        self.assertEqual(await run(AsyncMock(return_value={})), {})

    async def test_mongo_conflict_does_not_reuse_stale_recovery_or_repeat_it(self):
        collection = StateCollection(agent_doc())
        collection.conflicts = 1
        events = AsyncMock()
        writer = AsyncMock(return_value={"emotion_deltas": {"deltas": {"sadness": 7}, "confidence": .9}})
        @recovery.phase("reply")
        async def run():
            return await interaction_decisions.evaluate_reply_state(agent_doc(), {}, [], [], "2026-10-11", "Thanks", {})
        with patch.object(interaction_decisions.database, "get_database", AsyncMock(return_value={interaction_decisions.database.AGENT_COLLECTION: collection, "state_events": events})), \
             patch.object(interaction_decisions.decisions, "evaluate", AsyncMock(side_effect=partial_answers)), \
             patch.object(interaction_decisions.decisions, "enabled", return_value=True), \
             patch.object(interaction_decisions, "structured_query", writer), \
             patch.object(interaction_decisions, "build_personality_emotional_delta_prompt", return_value="synthetic state"), \
             patch.object(interaction_decisions, "_system_message", return_value={"role": "system", "content": "synthetic"}):
            await run()
        writer.assert_awaited_once()
        self.assertEqual(collection.doc["emotional_status"]["emotions"]["joy"]["value"], 67)
        self.assertEqual(collection.doc["emotional_status"]["emotions"]["sadness"]["value"], 50)
        self.assertEqual(collection.doc["cognition_revision"], 2)

    async def test_sdk_http_500_recovery_has_exactly_one_physical_request(self):
        calls = []
        def respond(request):
            calls.append(request)
            return httpx2.Response(500, json={"error": {"message": "synthetic failure", "type": "server_error"}})
        constructor = sdk.OpenAI
        def client_factory(**kwargs):
            self.assertEqual(kwargs["max_retries"], 0)
            kwargs["http_client"].close()
            kwargs["http_client"] = httpx2.Client(transport=httpx2.MockTransport(respond))
            return constructor(**kwargs)
        @recovery.phase("reply")
        async def run():
            return await recovery.query([{"role": "user", "content": "synthetic"}], {"type": "json_object"}, quality=False)
        with patch.object(generation, "OPENAI_KEY", "test-unused-key"), \
             patch.object(generation.openai, "OpenAI", side_effect=client_factory), \
             patch.object(generation, "LLM_MODE", "hosted"), \
             patch.object(generation, "GPT_FAST", "gpt-4o-mini"), \
             patch.object(generation, "flush", AsyncMock()):
            self.assertIsNone(await run())
        self.assertEqual(len(calls), 1)

    async def test_subjective_thought_gate_uses_valid_probability_without_recovery(self):
        from app.services import decisions, decision_tasks
        for name in ("post_thought", "contextual_thought"):
            question = decisions.predicate_question(name, "Think?")
            batch = decisions.DecisionBatch.from_response([question], {"answers": [{"name": name, "type": "predicate", "probability": .6}]})
            with patch.object(decision_tasks.decisions, "evaluate", AsyncMock(return_value=batch)):
                self.assertIs(await decision_tasks.predicate(name, "Think?", {}, "autonomy"), True)

    async def test_known_contact_keeps_final_boundary_recovery_despite_uncertain_extra_contact(self):
        from app.services import thinking, decisions
        class Cursor:
            def __init__(self, values): self.values = values
            def sort(self, *args): return self
            def limit(self, count): self.values = self.values[:count]; return self
            async def to_list(self, length=None): return self.values[:length]
        class Collection:
            def __init__(self, values): self.values = values
            def find(self, query, *args):
                values = self.values
                if "$or" in query:
                    ids = query["$or"][0]["user_id"]["$in"]
                    names = query["$or"][1]["username"]["$in"]
                    values = [doc for doc in values if doc["user_id"] in ids or
                              any(name.fullmatch(doc["username"]) for name in names)]
                elif isinstance(query.get("user_id"), dict):
                    ids = query["user_id"]
                    values = [doc for doc in values if doc["user_id"] in ids["$in"] and doc["user_id"] not in ids.get("$nin", [])]
                return Cursor(values)
        old = {"user_id": "old", "username": "Alex"}
        db = {thinking.USER_COLLECTION: Collection([old, {"user_id": "extra", "username": "Lee"}]),
              thinking.MEMORY_COLLECTION: Collection([]),
              thinking.THOUGHT_COLLECTION: Collection([{"thought": "I promised Alex to check the draft."}])}
        written = {"user_id": "old", "message": "How is the draft?", "purpose": "follow_up", "tone": "friendly"}
        actions = []
        async def writer(_messages, _schema, **kwargs):
            actions.append((kwargs["fallback"], recovery.active()))
            return {"message": "How is your draft going?"} if kwargs["fallback"] else {"initiate_messages": [written]}
        async def selection(evidence, questions, **kwargs):
            return decisions.DecisionBatch.from_response(questions, {"answers": [
                {"type": "predicate", "name": q["name"], "probability": .6} for q in questions]})
        @recovery.phase("autonomy")
        async def run():
            candidates = await thinking._grounded_candidates([], "Alex's draft")
            self.assertEqual([c["profile"]["user_id"] for c in candidates], ["old"])
            self.assertEqual(actions, [])
            messages = await thinking._compose_outreach({}, [], [], "Alex's draft")
            return await thinking.handle_initiating_messages(messages)
        with patch.object(thinking, "get_database", AsyncMock(return_value=db)), \
             patch.object(thinking.decision_tasks, "predicate", AsyncMock(return_value=None)), \
             patch.object(thinking.decision_tasks, "enabled", return_value=True), \
             patch.object(thinking.decisions, "evaluate", AsyncMock(side_effect=selection)), \
             patch.object(thinking.decision_tasks, "select", AsyncMock(return_value=None)) as check, \
             patch.object(thinking, "structured_query", AsyncMock(side_effect=writer)), \
             patch.object(thinking, "grab_user", AsyncMock(return_value=old)), \
             patch.object(thinking, "grab_self", AsyncMock(return_value={})), \
             patch.object(thinking, "get_conversation", AsyncMock(return_value={"messages": [{"message": "latest privacy boundary"}]})), \
             patch.object(thinking, "build_message_appropriate_prompt", return_value="Respect the latest boundary."), \
             patch.object(thinking, "insert_message_to_conversation", AsyncMock()), \
             patch.object(thinking, "insert_message_to_message_memory", AsyncMock()):
            sent = await run()
        self.assertEqual(actions, [(False, False), (True, True)])
        self.assertEqual([message["user_id"] for message in sent], ["old"])
        self.assertEqual(check.await_args.args[3]["recent_messages"], [{"message": "latest privacy boundary"}])
