import unittest
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

from app.services import decision_tasks, thinking
from app.services.memory import EMOTION_KEYS


class SharedDecisionTaskTests(unittest.IsolatedAsyncioTestCase):
    async def test_rejected_memory_batches_gate_and_metadata_without_narrative(self):
        batch = Mock()
        batch.predicate.return_value = False
        with patch.object(decision_tasks, "enabled", return_value=True), \
             patch.object(decision_tasks, "structured_query", AsyncMock()) as writer, \
             patch.object(decision_tasks.decisions, "evaluate", AsyncMock(return_value=batch)) as metadata:
            self.assertIsNone(await decision_tasks.create_memory({"memory_tags": []}, []))
            writer.assert_not_awaited()
            metadata.assert_awaited_once()
            names = {question["name"] for question in metadata.await_args.args[1]}
            self.assertEqual(names, {"memory_worthy", "significance"} | {f"impact_{emotion}" for emotion in EMOTION_KEYS})

    async def test_unresolved_memory_gate_uses_combined_legacy_fallback_once(self):
        expected = {"event": "lasting boundary", "thoughts": "Remember it.", "significance": "high"}
        batch = Mock()
        batch.predicate.return_value = None
        batch.choice.return_value = None
        batch.score.return_value = None
        with patch.object(decision_tasks, "enabled", return_value=True), \
             patch.object(decision_tasks, "structured_query", AsyncMock(return_value=expected)) as writer, \
             patch.object(decision_tasks.decisions, "evaluate", AsyncMock(return_value=batch)) as metadata:
            self.assertEqual(await decision_tasks.create_memory({"memory_tags": []}, []), expected)
            writer.assert_awaited_once()
            metadata.assert_awaited_once()

    async def test_memory_scores_map_level_indices_to_0_100_without_reweighting(self):
        batch = Mock()
        batch.predicate.return_value = True
        batch.choice.return_value = "high"
        batch.score.side_effect = lambda name, **kw: 2.75 if name == "impact_joy" else 0.0
        with patch.object(decision_tasks, "enabled", return_value=True), \
             patch.object(decision_tasks.decisions, "evaluate", AsyncMock(return_value=batch)), \
             patch.object(decision_tasks, "structured_query", AsyncMock(return_value={
                 "event": "A commitment", "thoughts": "Follow through", "tags": ["plans"]})) as writer:
            result = await decision_tasks.create_memory({"memory_tags": []}, [])
            self.assertEqual(result["significance"], "high")
            self.assertEqual(result["emotional_impact"]["joy"]["value"], 55)
            self.assertEqual(result["emotional_impact"]["fear"]["value"], 0)
            properties = writer.await_args.args[1]["json_schema"]["schema"]["properties"]
            self.assertNotIn("significance", properties)
            self.assertNotIn("emotional_impact", properties)

    async def test_partial_memory_metadata_requests_only_unresolved_fields(self):
        batch = Mock()
        batch.predicate.return_value = True
        batch.choice.return_value = None
        batch.score.side_effect = lambda name, **kw: 4 if name == "impact_love" else None
        with patch.object(decision_tasks, "enabled", return_value=True), \
             patch.object(decision_tasks.decisions, "evaluate", AsyncMock(return_value=batch)), \
             patch.object(decision_tasks, "structured_query", AsyncMock(return_value={
                 "event": "Love", "thoughts": "Meaningful", "significance": "medium",
                 "emotional_impact": {"love": {"value": 1}, "joy": {"value": 40}}})) as writer:
            result = await decision_tasks.create_memory({"memory_tags": []}, [])
            self.assertEqual(result["emotional_impact"]["love"]["value"], 80)
            self.assertEqual(result["emotional_impact"]["joy"]["value"], 40)
            schema = writer.await_args.args[1]["json_schema"]["schema"]
            self.assertIn("significance", schema["properties"])
            self.assertNotIn("love", schema["properties"]["emotional_impact"]["properties"])

    async def test_unresolved_gate_retains_accepted_metadata_in_recovery(self):
        batch = Mock()
        batch.predicate.return_value = None
        batch.choice.return_value = "high"
        batch.score.side_effect = lambda name, **kw: 4 if name == "impact_love" else 0
        with patch.object(decision_tasks, "enabled", return_value=True), \
             patch.object(decision_tasks.decisions, "evaluate", AsyncMock(return_value=batch)), \
             patch.object(decision_tasks, "structured_query", AsyncMock(return_value={
                 "event": "Lee set a lasting boundary", "thoughts": "I will respect it.",
                 "significance": "low", "emotional_impact": {"love": {"value": 1}}})) as writer:
            result = await decision_tasks.create_memory({"memory_tags": []}, [])
        self.assertEqual(result["significance"], "high")
        self.assertEqual(result["emotional_impact"]["love"]["value"], 80)
        self.assertTrue(writer.await_args.kwargs["fallback"])
        properties = writer.await_args.args[1]["json_schema"]["schema"]["properties"]
        self.assertNotIn("significance", properties)
        self.assertNotIn("emotional_impact", properties)

    async def test_native_memory_writer_receives_dialogue_once_without_prompt_replay(self):
        agent = {"name": "Jasmine", "identity": "A bodyless person", "personality": {"kindness": 50},
                 "emotional_status": {"joy": {"value": 50}}, "memory_tags": [], "_id": "storage-id"}
        queries = [{"role": "system", "content": "Huge repeated state system prompt"},
                   {"role": "user", "content": "I finished the interview!"},
                   {"role": "assistant", "content": "Congratulations!"},
                   {"role": "assistant", "content": 'This is Jasmine\'s refreshed summary: {"summary": "Lee completed the interview."}'}]
        evidence = {"agent": agent, "user": {"user_id": "lee", "username": "Lee"}, "interaction": queries}
        batch = Mock()
        batch.predicate.return_value = True
        batch.choice.return_value = "high"
        batch.score.return_value = 0
        with patch.object(decision_tasks, "enabled", return_value=True), \
             patch.object(decision_tasks.decisions, "evaluate", AsyncMock(return_value=batch)) as evaluate, \
             patch.object(decision_tasks, "structured_query", AsyncMock(return_value=None)) as writer:
            await decision_tasks.create_memory(agent, queries, evidence)
        evaluate.assert_awaited_once()
        messages = writer.await_args.args[0]
        self.assertEqual(sum(message["role"] == "user" for message in messages), 1)
        self.assertEqual(messages[0]["role"], "system")
        self.assertIn("persists conversations", messages[0]["content"])
        prompt = next(message["content"] for message in messages if message["role"] == "user")
        self.assertEqual(prompt.count("I finished the interview!"), 1)
        self.assertIn('"username": "Lee"', prompt)
        self.assertIn('"outcome": "user_refresh"', prompt)
        self.assertNotIn("Huge repeated state system prompt", prompt)
        self.assertNotIn("storage-id", prompt)

    async def test_missing_expression_assets_retain_current_without_api_call(self):
        with patch.object(decision_tasks, "get_available_expressions", return_value=[]), \
             patch.object(decision_tasks, "select", AsyncMock()) as select:
            self.assertEqual(await decision_tasks.select_expression({"global_expression": "calm"}, {}, "invented"), "calm")
            select.assert_not_awaited()

    async def test_failed_expression_retains_current_without_generative_fallback(self):
        with patch.object(decision_tasks, "get_available_expressions", return_value=["calm", "joy"]), \
             patch.object(decision_tasks, "enabled", return_value=True), \
             patch.object(decision_tasks, "select", AsyncMock(return_value=None)), \
             patch.object(decision_tasks, "structured_query", AsyncMock(return_value={"expression": "joy"})) as writer:
            self.assertEqual(await decision_tasks.select_expression({"global_expression": "calm"}, {}), "calm")
            writer.assert_not_awaited()

    async def test_accepted_expression_does_not_request_prose_fallback(self):
        with patch.object(decision_tasks, "get_available_expressions", return_value=["calm", "joy"]), \
             patch.object(decision_tasks, "enabled", return_value=True), \
             patch.object(decision_tasks, "select", AsyncMock(return_value="joy")), \
             patch.object(decision_tasks, "structured_query", AsyncMock()) as writer:
            self.assertEqual(await decision_tasks.select_expression({"global_expression": "calm"}, {}), "joy")
            writer.assert_not_awaited()


class AutonomyTests(unittest.IsolatedAsyncioTestCase):
    async def test_outreach_writer_uses_grounded_candidates_without_replaying_queries(self):
        candidates = [{"profile": {"user_id": "alex", "username": "Alex", "summary": "Awaiting an interview follow-up.",
                                   "_id": "profile-storage-id"},
                       "recent_messages": [{"sender_id": "alex", "message": "Ask me about the interview tomorrow."}],
                       "memories": [], "outstanding_thoughts": ["I promised Alex a follow-up."]}]
        batch = Mock()
        batch.predicate.return_value = True
        batch.unresolved = set()
        with patch.object(thinking.decision_tasks, "enabled", return_value=True), \
             patch.object(thinking, "_grounded_candidates", AsyncMock(return_value=candidates)), \
             patch.object(thinking.decisions, "evaluate", AsyncMock(return_value=batch)), \
             patch.object(thinking, "structured_query", AsyncMock(return_value={"initiate_messages": []})) as writer:
            await thinking._compose_outreach({"identity": "Independent Jasmine", "personality": {}, "emotional_status": {}},
                [{"role": "system", "content": "Old full state replay"},
                 {"role": "assistant", "content": "Diagnostic replay that is not an experience"}],
                [], "I should ask Alex how the interview went.")
        messages = writer.await_args.args[0]
        self.assertEqual(len(messages), 2)
        serialized = str(messages)
        self.assertIn("Independent Jasmine", serialized)
        self.assertIn("Ask me about the interview tomorrow.", serialized)
        self.assertIn("I should ask Alex how the interview went.", serialized)
        self.assertNotIn("Old full state replay", serialized)
        self.assertNotIn("Diagnostic replay", serialized)
        self.assertNotIn("profile-storage-id", serialized)

    async def test_outreach_rewrite_uses_fresh_boundaries_and_recent_context(self):
        candidate = {"user_id": "alex", "message": "How is your family?", "purpose": "follow_up", "tone": "friendly"}
        user = {"user_id": "alex", "username": "Alex", "summary": "Do not initiate family discussions.", "_id": "profile-storage-id"}
        recent = [{"sender_id": "alex", "message": "Please keep family private."}]
        with patch.object(thinking, "grab_user", AsyncMock(return_value=user)), \
             patch.object(thinking, "grab_self", AsyncMock(return_value={"identity": "Fresh Jasmine", "personality": {}, "emotional_status": {}})), \
             patch.object(thinking, "get_conversation", AsyncMock(return_value={"messages": recent})), \
             patch.object(thinking.decision_tasks, "enabled", return_value=True), \
             patch.object(thinking.decision_tasks, "select", AsyncMock(return_value="rewrite")), \
             patch.object(thinking, "structured_query", AsyncMock(return_value={"message": "no"})) as writer, \
             patch.object(thinking, "insert_message_to_conversation", AsyncMock()) as persist:
            self.assertEqual(await thinking.handle_initiating_messages([candidate]), [])
        prompt = next(message["content"] for message in writer.await_args.args[0] if message["role"] == "user")
        self.assertIn("Fresh Jasmine", prompt)
        self.assertIn("Do not initiate family discussions.", prompt)
        self.assertIn("Please keep family private.", prompt)
        self.assertNotIn("profile-storage-id", prompt)
        persist.assert_not_awaited()

    async def test_random_branch_drawn_before_context_gate_and_never_rejected_by_it(self):
        rng = Mock()
        rng.random.return_value = 0.2
        agent = {"personality": {}, "emotional_status": {}, "identity": "Jasmine", "memory_tags": []}
        with patch.object(thinking, "grab_self", AsyncMock(return_value=agent)), \
             patch.object(thinking, "get_all_message_memory", AsyncMock(return_value=[])), \
             patch.object(thinking, "get_thoughts", AsyncMock(return_value=[])), \
             patch.object(thinking, "retrieve_relevant_memory_from_tag", AsyncMock(return_value=None)), \
             patch.object(thinking.decision_tasks, "enabled", return_value=True), \
             patch.object(thinking.decision_tasks, "predicate", AsyncMock(return_value=False)) as gate, \
             patch.object(thinking, "build_thought_prompt", return_value="random thought") as prompt, \
             patch.object(thinking, "structured_query", AsyncMock(return_value={"thought": "no"})) as writer:
            await thinking._generate_thought(rng=rng, now=datetime(2026, 10, 11))
            rng.random.assert_called_once()
            gate.assert_not_awaited()
            self.assertTrue(prompt.call_args.kwargs["random_branch"])
            writer.assert_awaited_once()
            self.assertNotIn("new_expression", writer.await_args.args[1]["json_schema"]["schema"]["properties"])

    async def test_context_rejection_has_no_writing_or_side_effects(self):
        rng = Mock()
        rng.random.return_value = .8
        agent = {"personality": {}, "emotional_status": {}, "identity": "Jasmine", "memory_tags": []}
        with patch.object(thinking, "grab_self", AsyncMock(return_value=agent)), \
             patch.object(thinking, "get_all_message_memory", AsyncMock(return_value=[])), \
             patch.object(thinking, "get_thoughts", AsyncMock(return_value=[])), \
             patch.object(thinking, "retrieve_relevant_memory_from_tag", AsyncMock(return_value=None)), \
             patch.object(thinking.decision_tasks, "enabled", return_value=True), \
             patch.object(thinking.decision_tasks, "predicate", AsyncMock(return_value=False)), \
             patch.object(thinking, "structured_query", AsyncMock()) as writer, \
             patch.object(thinking, "add_thought", AsyncMock()) as persist:
            await thinking._generate_thought(rng=rng)
            writer.assert_not_awaited()
            persist.assert_not_awaited()

    def test_candidate_messages_disallow_invented_duplicate_and_more_than_three_ids(self):
        def message(user_id):
            return {"user_id": user_id, "message": "Hi", "purpose": "greeting", "tone": "friendly"}
        payload = {"initiate_messages": [message("invented"), message("a"), message("a"), message("b"), message("c"), message("d")]}
        self.assertEqual([m["user_id"] for m in thinking._validated_messages(payload, {"a", "b", "c", "d"})], ["a", "b", "c"])

    async def test_keep_avoids_rewrite_and_suppress_avoids_persistence(self):
        messages = [{"user_id": "real", "message": "Follow-up", "purpose": "follow_up", "tone": "friendly"}]
        for action, count in [("keep", 1), ("suppress", 0)]:
            with patch.object(thinking, "grab_user", AsyncMock(return_value={"user_id": "real"})), \
                 patch.object(thinking, "grab_self", AsyncMock(return_value={})), \
                 patch.object(thinking, "get_conversation", AsyncMock(return_value=None)), \
                 patch.object(thinking.decision_tasks, "enabled", return_value=True), \
                 patch.object(thinking.decision_tasks, "select", AsyncMock(return_value=action)), \
                 patch.object(thinking, "structured_query", AsyncMock()) as writer, \
                 patch.object(thinking, "insert_message_to_conversation", AsyncMock()) as persist, \
                 patch.object(thinking, "insert_message_to_message_memory", AsyncMock()):
                sent = await thinking.handle_initiating_messages(messages)
                self.assertEqual(len(sent), count)
                self.assertEqual(persist.await_count, count)
                writer.assert_not_awaited()

    async def test_missing_recipient_is_skipped_before_accessing_conversation(self):
        messages = [{"user_id": "missing", "message": "Hi", "purpose": "greeting", "tone": "friendly"}]
        with patch.object(thinking, "grab_user", AsyncMock(return_value=None)), \
             patch.object(thinking, "get_conversation", AsyncMock()) as conversation:
            self.assertEqual(await thinking.handle_initiating_messages(messages), [])
            conversation.assert_not_awaited()

    async def test_old_contact_with_outstanding_thought_remains_a_candidate(self):
        class Cursor:
            def __init__(self, values):
                self.values = values
            def sort(self, key, direction):
                self.values = sorted(self.values, key=lambda doc: doc.get(key, 0), reverse=direction < 0)
                return self
            def limit(self, count):
                self.values = self.values[:count]
                return self
            async def to_list(self, length=None):
                assert length is not None
                return self.values[:length]
        class Collection:
            def __init__(self, values):
                self.values = values
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
        old = {"user_id": "old", "username": "Alice", "last_interaction": 0}
        recent = [{"user_id": f"new{i}", "username": f"Contact{i}", "last_interaction": i + 1} for i in range(30)]
        db = {
            thinking.USER_COLLECTION: Collection(recent + [old]),
            thinking.MEMORY_COLLECTION: Collection([{"user_id": p["user_id"], "ts_created": i} for i, p in enumerate(recent)]),
            thinking.THOUGHT_COLLECTION: Collection([{"thought": "I promised Alice to follow up next week."}]),
        }
        with patch.object(thinking, "get_database", AsyncMock(return_value=db)):
            candidates = await thinking._grounded_candidates(
                [{"sender_id": profile["user_id"]} for profile in recent], "A reminder")
        self.assertEqual(len(candidates), thinking.OUTREACH_CONTEXT_LIMIT)
        self.assertIn("old", {candidate["profile"]["user_id"] for candidate in candidates})
        older = next(candidate for candidate in candidates if candidate["profile"]["user_id"] == "old")
        self.assertEqual(older["recent_messages"], [])
        self.assertIn("I promised Alice", older["outstanding_thoughts"][0])


if __name__ == "__main__":
    unittest.main()
