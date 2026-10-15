"""Regressions found by the live Decisions comparison, without paid API calls."""
from contextlib import ExitStack
from datetime import datetime
import unittest
from unittest.mock import AsyncMock, Mock, patch

from app.constants.schemas import get_memory_schema_lite, get_thought_schema
from app.services import decision_tasks, decisions, thinking
from app.services.memory import EMOTION_KEYS
from app.services.openai import _validate_structured_payload
from scripts.local_validation import fixture_value


def assert_strict_objects(test, node):
    kinds = node.get("type")
    if kinds == "object" or isinstance(kinds, list) and "object" in kinds:
        test.assertFalse(node["additionalProperties"])
        test.assertEqual(set(node["required"]), set(node.get("properties", {})))
        for child in node.get("properties", {}).values():
            assert_strict_objects(test, child)
    if isinstance(node.get("items"), dict):
        assert_strict_objects(test, node["items"])


class NativeMemorySchemaTests(unittest.IsolatedAsyncioTestCase):
    def test_score_question_enforces_provider_maximum_and_memory_rubric(self):
        for count in (1, 11):
            with self.subTest(count=count), self.assertRaises(ValueError):
                decisions.score_question("impact", "Rate impact", [str(i) for i in range(count)])
        self.assertEqual(len(decisions.score_question("impact", "Rate impact", [str(i) for i in range(10)])["levels"]), 10)
        self.assertEqual([level["label"] for level in decision_tasks.MEMORY_IMPACT_LEVELS], ["0", "20", "40", "60", "80", "100"])

    async def test_valid_subjective_memory_scores_ignore_confidence_without_rescaling(self):
        for confidence in (.7, .69, 0):
            async def metadata(_evidence, questions, **_kwargs):
                answers = []
                for question in questions:
                    if question["type"] == "predicate":
                        answers.append({"name": question["name"], "type": "predicate", "probability": 1})
                    elif question["type"] == "choice":
                        answers.append({"name": question["name"], "type": "choice", "choice": "high", "confidence": 1,
                                        "probabilities": [{"value": c["value"], "probability": float(c["value"] == "high")} for c in question["choices"]]})
                    else:
                        is_joy = question["name"] == "impact_joy"
                        answers.append({"name": question["name"], "type": "score", "confidence": confidence if is_joy else 1,
                                        "score": 2.75 if is_joy else 0,
                                        "probabilities": [{"value": i, "label": level["label"],
                                                           "probability": (.25 if i == 2 else .75 if i == 3 else 0) if is_joy else float(i == 0)}
                                                          for i, level in enumerate(question["levels"])]})
                return decisions.DecisionBatch.from_response(questions, {"answers": answers})
            with self.subTest(confidence=confidence), \
                 patch.object(decision_tasks, "enabled", return_value=True), \
                 patch.object(decision_tasks.decisions, "evaluate", AsyncMock(side_effect=metadata)), \
                 patch.object(decision_tasks, "structured_query", AsyncMock(return_value={"event": "Lee finished an interview.", "thoughts": "I will follow up.",
                                                                                         "significance": "low",
                                                                                         "emotional_impact": {"joy": {"value": 11}}})) as writer:
                result = await decision_tasks.create_memory({"memory_tags": []}, [])
                self.assertEqual(result["emotional_impact"]["joy"]["value"], 55)
                self.assertEqual(result["significance"], "high")
                self.assertEqual(set(result["emotional_impact"]), set(EMOTION_KEYS))
                writer.assert_awaited_once()
                self.assertFalse(writer.await_args.kwargs["fallback"])
                properties = writer.await_args.args[1]["json_schema"]["schema"]["properties"]
                self.assertNotIn("emotional_impact", properties)
                self.assertNotIn("significance", properties)

    async def test_native_memory_writers_preserve_original_user_actor_evidence(self):
        queries = [{"role": "user", "content": "I finished the interview!"}, {"role": "assistant", "content": "Congratulations!"}]
        evidence = {"user": {"user_id": "lee-id", "username": "Lee"}, "interaction": queries}
        metadata = Mock()
        metadata.choice.return_value = "high"
        metadata.score.return_value = 0
        for worthy in (None, True):
            metadata.predicate.return_value = worthy
            with self.subTest(worthy=worthy), \
                 patch.object(decision_tasks, "enabled", return_value=True), \
                 patch.object(decision_tasks.decisions, "evaluate", AsyncMock(return_value=metadata)), \
                 patch.object(decision_tasks, "structured_query", AsyncMock(return_value=None)) as writer:
                await decision_tasks.create_memory({"name": "Kaede", "memory_tags": []}, queries, evidence)
                prompt = writer.await_args.args[0][-1]["content"]
                self.assertIn('"username": "Lee"', prompt)
                self.assertIn('"role": "user", "content": "I finished the interview!"', prompt)
                self.assertIn("Lee completed Lee's interview", prompt)
                self.assertIn("Kaede is a bodyless agent", prompt)
                self.assertIn("first-person 'I' is Kaede's subjective reflection", prompt)
                self.assertNotIn("Jasmine", str(writer.await_args.args[0]))

    def test_partial_memory_schema_closes_nullable_emotion_objects(self):
        schema = decision_tasks._memory_writer_schema({"significance": "high", "emotional_impact": {"love": {"value": 80}}})
        self.assertTrue(schema["json_schema"]["strict"])
        root = schema["json_schema"]["schema"]
        assert_strict_objects(self, root)
        self.assertNotIn("significance", root["properties"])
        self.assertNotIn("love", root["properties"]["emotional_impact"]["properties"])
        self.assertEqual(set(root["properties"]["emotional_impact"]["required"]), set(EMOTION_KEYS) - {"love"})
        self.assertNotIn("uniqueItems", root["properties"]["tags"])
        # The baseline schema remains untouched, including its optional metadata.
        baseline = get_memory_schema_lite()["json_schema"]["schema"]
        self.assertIn("significance", baseline["properties"])
        self.assertIn("love", baseline["properties"]["emotional_impact"]["properties"])
        self.assertNotIn("required", baseline["properties"]["emotional_impact"])

    def test_unresolved_metadata_cannot_invent_sentiment_emotion_keys(self):
        schema = decision_tasks._memory_writer_schema({})
        payload = fixture_value(schema["json_schema"]["schema"])
        self.assertEqual(_validate_structured_payload(payload, schema), [])
        payload["emotional_impact"]["trust"] = {"value": 70}
        errors = _validate_structured_payload(payload, schema)
        self.assertTrue(any("trust" in error for error in errors))

    def test_fully_accepted_metadata_is_excluded_from_writer(self):
        schema = decision_tasks._memory_writer_schema({"significance": "high", "emotional_impact": {
            emotion: {"value": 0} for emotion in EMOTION_KEYS}})
        root = schema["json_schema"]["schema"]
        assert_strict_objects(self, root)
        self.assertNotIn("significance", root["properties"])
        self.assertNotIn("emotional_impact", root["properties"])
        self.assertIn("event", root["required"])
        self.assertIn("thoughts", root["required"])

    async def test_uncertain_native_gate_uses_one_strict_combined_writer(self):
        batch = Mock()
        batch.predicate.return_value = None
        batch.choice.return_value = None
        batch.score.return_value = None
        with patch.object(decision_tasks, "enabled", return_value=True), \
             patch.object(decision_tasks.decisions, "evaluate", AsyncMock(return_value=batch)), \
             patch.object(decision_tasks, "structured_query", AsyncMock(return_value=None)) as writer:
            await decision_tasks.create_memory({"memory_tags": []}, [])
        writer.assert_awaited_once()
        schema = writer.await_args.args[1]
        self.assertTrue(schema["json_schema"]["strict"])
        assert_strict_objects(self, schema["json_schema"]["schema"])

    async def test_disabled_memory_preserves_baseline_writer_schema(self):
        with patch.object(decision_tasks, "enabled", return_value=False), \
             patch.object(decision_tasks, "structured_query", AsyncMock(return_value=None)) as writer:
            await decision_tasks.create_memory({"memory_tags": []}, [])
        self.assertEqual(writer.await_args.args[1], get_memory_schema_lite())


class NativeThoughtSchemaTests(unittest.IsolatedAsyncioTestCase):
    async def test_native_thought_fields_are_required_with_partial_feature_flags(self):
        agent = {"personality": {}, "emotional_status": {}, "identity": "Jasmine", "memory_tags": []}
        for features in ({"autonomy"}, {"expressions"}, {"autonomy", "expressions"}, set()):
            with self.subTest(features=features), ExitStack() as stack:
                stack.enter_context(patch.object(thinking.decision_tasks, "enabled", side_effect=lambda feature: feature in features))
                for name, value in (("grab_self", agent), ("get_all_message_memory", []), ("get_thoughts", []),
                                    ("retrieve_relevant_memory_from_tag", None)):
                    stack.enter_context(patch.object(thinking, name, AsyncMock(return_value=value)))
                stack.enter_context(patch.object(thinking, "build_thought_prompt", return_value="Write a thought."))
                writer = stack.enter_context(patch.object(thinking, "structured_query", AsyncMock(return_value={"thought": "no"})))
                rng = Mock()
                rng.random.return_value = .2
                await thinking._generate_thought(rng=rng, now=datetime(2026, 10, 11))
                writer.assert_awaited_once()
                schema = writer.await_args.args[1]
                if features:
                    self.assertTrue(schema["json_schema"]["strict"])
                    root = schema["json_schema"]["schema"]
                    assert_strict_objects(self, root)
                    self.assertIn("thought", root["required"])
                    self.assertEqual("new_expression" in root["properties"], "expressions" not in features)
                    self.assertTrue(_validate_structured_payload({}, schema))
                else:
                    self.assertEqual(schema, get_thought_schema())


if __name__ == "__main__":
    unittest.main()
