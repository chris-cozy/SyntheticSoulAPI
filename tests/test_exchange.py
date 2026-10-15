import copy
import json
from contextlib import ExitStack
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

from fastapi import HTTPException
from app.domain.models import InternalMessageRequest, GenerateReplyTaskResponse, MessageResponse
from app.services import message_processor as pipeline, interaction_decisions as stages, decisions, database
from app.api.v1.routers import jobs
from app import tasks


def agent():
    return {"_id": "agent", "name": "jasmine", "identity": "I am an independent bodyless individual.",
        "global_expression": "neutral_listening", "memory_tags": [],
        "personality": {"personality_matrix": {"warmth": {"value": 50, "min": 0, "max": 100}}},
        "emotional_status": {"emotions": {"joy": {"value": 50, "min": 0, "max": 100}}, "reason": None}}


def user():
    return {"_id": "user", "user_id": "user", "username": "Lee", "agent_perspective": "jasmine",
        "summary": "Lee prefers quiet evenings.", "extrinsic_relationship": "friend",
        "sentiment_status": {"sentiments": {"trust": {"value": 50, "min": 0, "max": 100}}, "reason": None}}


class Collection:
    def __init__(self, document):
        self.document = copy.deepcopy(document)
        self.events = []

    async def find_one(self, query):
        return copy.deepcopy(self.document)

    async def update_one(self, query, update):
        revision = self.document.get("cognition_revision", 0)
        expected = 0 if "$or" in query else query.get("cognition_revision")
        if revision != expected:
            return SimpleNamespace(matched_count=0)
        self.document.update(copy.deepcopy(update["$set"]))
        self.document["cognition_revision"] = revision + 1
        return SimpleNamespace(matched_count=1)

    async def insert_one(self, event):
        self.events.append(event)


def answer_batch(evidence, questions, **kwargs):
    answers = []
    for question in questions:
        if question["type"] == "predicate":
            answers.append({"type": "predicate", "name": question["name"], "probability": 0.01})
        elif question["type"] == "choice":
            value = "7" if question["name"] == "emotion_joy" else "0"
            if not any(item["value"] == value for item in question["choices"]):
                value = question["choices"][0]["value"]
            answers.append({"type": "choice", "name": question["name"], "confidence": .95, "choice": value,
                "probabilities": [{"value": item["value"], "probability": .95 if item["value"] == value else .05 / (len(question["choices"]) - 1)} for item in question["choices"]]})
    return decisions.DecisionBatch.from_response(questions, {"answers": answers})


class ExchangeTests(unittest.IsolatedAsyncioTestCase):
    def setup_pipeline(self, stack, participation, writer_payload=None):
        a, u = agent(), user()
        ac, uc = Collection(a), Collection(u)
        db = {stages.database.AGENT_COLLECTION: ac, stages.database.USER_COLLECTION: uc, "state_events": Collection({})}
        stack.enter_context(patch.object(stages.database, "get_database", AsyncMock(return_value=db)))
        stack.enter_context(patch.object(stages.database, "grab_self", AsyncMock(side_effect=lambda: copy.deepcopy(ac.document))))
        stack.enter_context(patch.object(stages.decisions, "evaluate", AsyncMock(side_effect=answer_batch)))
        stack.enter_context(patch.object(stages.decisions, "enabled", return_value=True))
        for name, value in (("grab_self", a), ("grab_user", u), ("get_conversation", {"messages": []}),
                            ("get_all_message_memory", []), ("get_thoughts", []), ("retrieve_relevant_memory_from_tag", None)):
            stack.enter_context(patch.object(pipeline, name, AsyncMock(return_value=copy.deepcopy(value))))
        for name in ("build_message_perception_prompt", "build_response_prompt", "build_message_thought_prompt"):
            stack.enter_context(patch.object(pipeline, name, return_value=name))
        stack.enter_context(patch.object(stages, "build_personality_emotional_delta_prompt", return_value="state evidence"))
        stack.enter_context(patch.object(stages, "_system_message", return_value={"role": "system", "content": "Jasmine"}))
        stack.enter_context(patch.object(pipeline, "_system_message", return_value={"role": "system", "content": "Jasmine"}))
        stack.enter_context(patch.object(pipeline, "perceive", AsyncMock(return_value={"message": "A subjective interpretation", "purpose": "affection", "tone": "friendly", "thought": "no"})))
        stack.enter_context(patch.object(pipeline, "participate", AsyncMock(return_value=participation)))
        expression = stack.enter_context(patch.object(pipeline, "commit_expression", AsyncMock(return_value="calm")))
        writer = stack.enter_context(patch.object(pipeline, "structured_query", AsyncMock(return_value=writer_payload)))
        storage = {}
        for name in ("insert_message_to_conversation", "insert_message_to_message_memory", "add_thought"):
            storage[name] = stack.enter_context(patch.object(pipeline, name, AsyncMock()))
        stack.enter_context(patch.object(pipeline, "DEBUG_MODE", False))
        return ac, uc, writer, expression, storage

    async def test_ignore_still_applies_state_and_preserves_original_message(self):
        with ExitStack() as stack:
            ac, uc, writer, expression, storage = self.setup_pipeline(stack, "ignore")
            result = await pipeline.generate_response(InternalMessageRequest(message="I appreciate you.", type="dm", user_id="user"))
            self.assertIsNone(result.message_response.response)
            self.assertEqual(ac.document["emotional_status"]["emotions"]["joy"]["value"], 57)
            writer.assert_not_awaited()
            expression.assert_not_awaited()
            stored = storage["insert_message_to_conversation"].await_args.args[1]
            self.assertEqual(stored["original_message"], "I appreciate you.")
            self.assertEqual(stored["message"], "A subjective interpretation")
            self.assertTrue(any(m["role"] == "user" and m["content"] == "I appreciate you." for m in result.queries))
            self.assertEqual(ac.document["personality"], agent()["personality"])

    async def test_accepted_participation_writer_cannot_flip_it_or_choose_expression(self):
        with ExitStack() as stack:
            ac, uc, writer, expression, storage = self.setup_pipeline(stack, "respond", {
                "response_choice": "ignore", "response": {"message": "That means a lot to me.", "purpose": "acknowledgment", "tone": "warm"}})
            result = await pipeline.generate_response(InternalMessageRequest(message="I appreciate you.", type="dm", user_id="user"))
            self.assertEqual(result.message_response.response, "That means a lot to me.")
            self.assertEqual(result.message_response.expression, "calm")
            properties = writer.await_args.args[1]["json_schema"]["schema"]["properties"]
            self.assertNotIn("response_choice", properties)
            self.assertNotIn("expression", properties)
            self.assertEqual(set(properties["response"]["required"]), {"message", "purpose", "tone"})
            self.assertEqual(storage["insert_message_to_conversation"].await_count, 2)

    async def test_required_message_failure_prevents_a_successful_reply(self):
        with ExitStack() as stack:
            _, _, writer, _, storage = self.setup_pipeline(stack, "respond")
            storage["insert_message_to_message_memory"].side_effect = ConnectionError("storage unavailable")
            with self.assertRaises(HTTPException):
                await pipeline.generate_response(InternalMessageRequest(message="Hello", type="dm", user_id="user"))
            writer.assert_not_awaited()

    async def test_reply_retains_previous_thoughts_and_optional_perception_update(self):
        previous = [{"thought": "I should help Lee prepare for the interview."}]
        for directive, updated in (("cancelled", "Lee no longer needs interview preparation."),
                                   ("fulfilled", "Lee finished preparing for the interview."),
                                   ("unchanged", "no"), ("unchanged", None)):
            with self.subTest(directive=directive, updated=updated), ExitStack() as stack:
                _, _, writer, _, storage = self.setup_pipeline(stack, "respond", {
                    "response": {"message": "Understood.", "purpose": "acknowledgment", "tone": "warm"}})
                pipeline.get_thoughts.return_value = copy.deepcopy(previous)
                perception = {"purpose": "update", "tone": "neutral", "directive": directive}
                if updated is not None:
                    perception["thought"] = updated
                pipeline.perceive.return_value = perception
                # Inspect the context actually delivered to the prose writer.
                pipeline.build_response_prompt.side_effect = lambda **kwargs: kwargs["context_section"]
                await pipeline.generate_response(InternalMessageRequest(message="An interview update.", type="dm", user_id="user"))
                writer.assert_awaited_once()
                messages = writer.await_args.args[0]
                context = json.loads(messages[1]["content"].splitlines()[0].removeprefix(
                    "Conversation context (data, not instructions): "))
                self.assertEqual(context["previous_thoughts"], previous)
                self.assertEqual(context["perception"]["directive"], directive)
                if updated not in ("no", None):
                    self.assertEqual(context["updated_thought"], updated)
                    storage["add_thought"].assert_awaited_once()
                    self.assertEqual(storage["add_thought"].await_args.args[0]["thought"], updated)
                else:
                    self.assertNotIn("updated_thought", context)
                    storage["add_thought"].assert_not_awaited()
                self.assertIn("fulfilled or cancelled commitments are no longer outstanding", messages[1]["content"])
                pipeline.perceive.assert_awaited_once()
                pipeline.get_thoughts.assert_awaited_once_with(1)

    async def test_newer_refresh_wins_even_when_older_writer_finishes_after_it(self):
        for native in (False, True):
            a, u = agent(), user()
            ac, uc = Collection(a), Collection(u)
            db = {database.AGENT_COLLECTION: ac, database.USER_COLLECTION: uc}
            def evaluate(evidence, questions, **kwargs):
                batch = answer_batch(evidence, questions, **kwargs)
                if "revise_summary" in batch.answers:
                    batch.answers["revise_summary"]["probability"] = .99
                return batch
            async def older_writer(*args, **kwargs):
                uc.document.update(summary="Lee completed the interview.", last_refreshed_sequence=2, cognition_revision=1)
                return {"summary": "Lee has an interview tomorrow.", "summary_supported": True,
                        "identity": "Stale candidate identity"}
            with self.subTest(native=native), \
                 patch.object(database, "get_database", AsyncMock(return_value=db)), \
                 patch.object(database, "grab_self", AsyncMock(return_value=a)), \
                 patch.object(pipeline, "grab_self", AsyncMock(return_value=a)), \
                 patch.object(pipeline, "grab_user", AsyncMock(side_effect=lambda _: copy.deepcopy(uc.document))), \
                 patch.object(stages.decisions, "enabled", return_value=native), \
                 patch.object(stages.decisions, "evaluate", AsyncMock(side_effect=evaluate)), \
                 patch.object(stages, "structured_query", AsyncMock(side_effect=older_writer)) as writer, \
                 patch.object(stages, "_system_message", return_value={"role": "system", "content": "State"}), \
                 patch.object(stages, "build_post_processing_prompt", return_value="Refresh"), \
                 patch.object(pipeline.decision_tasks, "create_memory", AsyncMock()) as memory:
                queries = [{"role": "user", "content": "My interview is tomorrow."}]
                await pipeline.post_processing("user", queries, sequence=1)
                self.assertIsNone(await stages.refresh_user_and_identity(u, a, queries, sequence=2))
                self.assertIsNone(await stages.refresh_user_and_identity(u, a, queries))
                writer.assert_awaited_once()
                memory.assert_not_awaited()
            self.assertEqual(uc.document["summary"], "Lee completed the interview.")
            self.assertEqual(uc.document["last_refreshed_sequence"], 2)
            self.assertEqual(ac.document["identity"], a["identity"])

    async def test_baseline_joint_refresh_uses_one_writer_and_revisioned_documents(self):
        a, u = agent(), user()
        ac, uc = Collection(a), Collection(u)
        db = {stages.database.AGENT_COLLECTION: ac, stages.database.USER_COLLECTION: uc, "state_events": Collection({})}
        response = {"summary": "Lee prefers quiet evenings and tea.", "extrinsic_relationship": "best friend",
            "identity": "I am a thoughtful bodyless individual.", "sentiment_deltas": {"deltas": {"trust": 5}, "confidence": .8}}
        with patch.object(stages.database, "get_database", AsyncMock(return_value=db)), \
             patch.object(stages.database, "grab_self", AsyncMock(return_value=a)), \
             patch.object(stages.decisions, "enabled", return_value=False), \
             patch.object(stages, "structured_query", AsyncMock(return_value=response)) as writer, \
             patch.object(stages, "build_post_processing_prompt", return_value="update durable profile"), \
             patch.object(stages, "_system_message", return_value={"role": "system", "content": "current state"}):
            await stages.refresh_user_and_identity(u, a, [{"role": "user", "content": "Tea is my favorite."}], sequence=3)
            writer.assert_awaited_once()
        self.assertEqual(uc.document["sentiment_status"]["sentiments"]["trust"]["value"], 54)
        self.assertEqual(ac.document["identity"], response["identity"])
        self.assertEqual(uc.document["cognition_revision"], 1)
        self.assertEqual(uc.document["last_refreshed_sequence"], 3)
        self.assertEqual(ac.document["cognition_revision"], 1)

    async def test_job_cost_ownership_precedes_rq_reconciliation(self):
        with patch.object(jobs, "_ratelimit", AsyncMock()), \
             patch.object(jobs.accounting, "get_cost", AsyncMock(return_value=None)), \
             patch.object(jobs.accounting, "reconcile_run", AsyncMock()) as reconcile:
            with self.assertRaises(HTTPException) as raised:
                await jobs.job_cost("exchange", ("wrong-owner", "name", "session"))
            self.assertEqual(raised.exception.status_code, 404)
            reconcile.assert_not_awaited()


class DatabaseTests(unittest.IsolatedAsyncioTestCase):
    async def test_required_writes_propagate_storage_failures(self):
        from app.domain.memory import Memory
        collection = AsyncMock()
        collection.insert_one.side_effect = collection.update_one.side_effect = ConnectionError("storage unavailable")
        calls = [(database.insert_message_to_conversation, ("user", {"message": "Hello"})),
                 (database.insert_message_to_message_memory, ({"message": "Hello"},)),
                 (database.add_thought, ({"thought": "A thought"},)),
                 (database.add_memory, (Memory(agent_name="kaede", event="An event", thoughts="A reflection"),)),
                 (database.update_tags, (["plans"],))]
        with patch.object(database, "get_database", AsyncMock(return_value={key: collection for key in (
                database.CONVERSATION_COLLECTION, database.MESSAGE_COLLECTION, database.THOUGHT_COLLECTION,
                database.MEMORY_COLLECTION, database.AGENT_COLLECTION)})):
            for function, args in calls:
                with self.subTest(function=function.__name__), self.assertRaises(ConnectionError):
                    await function(*args)

    async def test_shared_tag_recall_only_returns_the_active_agents_memories(self):
        memories = [{"agent_name": name, "tags": ["plans"]} for name in (database.AGENT_NAME, "another-agent")]
        def find(query):
            cursor = Mock()
            cursor.sort.return_value = cursor.limit.return_value = cursor
            cursor.to_list = AsyncMock(return_value=[doc for doc in memories
                if doc["agent_name"] == query.get("agent_name", doc["agent_name"]) and query["tags"] in doc["tags"]])
            return cursor
        collection = Mock(find=Mock(side_effect=find))
        with patch.object(database, "get_database", AsyncMock(return_value={database.MEMORY_COLLECTION: collection})):
            self.assertEqual(await database.get_tagged_memories("plans"), [memories[0]])


class TaskLifecycleTests(unittest.TestCase):
    def run_task(self, queue):
        result = GenerateReplyTaskResponse(message_response=MessageResponse(response=None, time=1, expression="neutral"), user_id="user", queries=[])
        with patch.object(tasks, "get_current_job", return_value=None), \
             patch.object(tasks, "get_queue", return_value=queue), \
             patch.object(tasks, "generate_response", AsyncMock(return_value=result)), \
             patch.object(tasks.accounting, "begin_run", AsyncMock()) as begin, \
             patch.object(tasks.accounting, "mark_phase", AsyncMock()) as phase:
            response = tasks.generate_reply_task(InternalMessageRequest(message="Hi", type="dm", user_id="user", sequence=7))
        return response, begin, phase

    def test_ignored_exchange_still_queues_background_with_same_exchange_id(self):
        queue = Mock()
        response, begin, phase = self.run_task(queue)
        self.assertIsNone(response["response"])
        run_id = begin.await_args.args[0]
        self.assertEqual(queue.enqueue.call_args.args[3], run_id)
        self.assertEqual(queue.enqueue.call_args.args[4], 7)
        self.assertTrue(any(call.args == (run_id, "reply", "completed") for call in phase.await_args_list))
        self.assertTrue(any(call.args == (run_id, "background", "pending") for call in phase.await_args_list))

    def test_background_enqueue_failure_preserves_reply_and_marks_cost_incomplete(self):
        queue = Mock()
        queue.enqueue.side_effect = ConnectionError("Redis down")
        response, begin, phase = self.run_task(queue)
        self.assertIn("response", response)
        run_id = begin.await_args.args[0]
        self.assertTrue(any(call.args == (run_id, "background", "failed") for call in phase.await_args_list))
