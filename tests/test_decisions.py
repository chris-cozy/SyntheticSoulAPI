import copy
import json
import math
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.domain.decision_state import (StateProposal, apply_proposals, decay_proposals,
                                      fallback_proposals, proposals_from_batch, state_questions)
from app.domain.state import BoundedTrait, EmotionalState, PersonalityMatrix, SentimentMatrix
from app.services.decisions import DecisionBatch, choice_question, enabled, evaluate, predicate_question, score_question


def choice_answer(question, value, *, confidence=0.9, probability=0.95):
    others = len(question["choices"]) - 1
    return {"name": question["name"], "type": "choice", "choice": value, "confidence": confidence,
            "probabilities": [{"value": item["value"], "probability": probability if item["value"] == value else (1 - probability) / others}
                              for item in question["choices"]]}


class DecisionsValidationTests(unittest.TestCase):
    def test_partial_batch_retains_valid_answer_and_refusal_is_unresolved(self):
        questions = [predicate_question("addressed", "Addressed?"), choice_question("purpose", "Purpose?", ["question", "other"])]
        batch = DecisionBatch.from_response(questions, {"answers": [
            {"name": "addressed", "type": "predicate", "probability": 0.96},
            {"name": "purpose", "type": "refusal"},
        ]})
        self.assertTrue(batch.predicate("addressed"))
        self.assertIsNone(batch.choice("purpose"))
        self.assertEqual(batch.unresolved, {"purpose"})

    def test_predicates_resolve_middle_probabilities_and_ties_decline(self):
        question = predicate_question("gate", "Gate?")
        for probability, expected in [(1, True), (0.9, True), (0.51, True),
                                      (0.5, False), (0.49, False), (0.1, False), (0, False)]:
            batch = DecisionBatch.from_response([question], {"answers": [{"name": "gate", "type": "predicate", "probability": probability}]})
            self.assertIs(batch.predicate("gate"), expected)

    def test_duplicate_answer_is_unresolved(self):
        question = predicate_question("gate", "Gate?")
        answer = {"name": "gate", "type": "predicate", "probability": 0.99}
        batch = DecisionBatch.from_response([question], {"answers": [answer, answer]})
        self.assertEqual(batch.answers, {})

    def test_malformed_probabilities_and_out_of_vocabulary_rejected(self):
        question = choice_question("tone", "Tone?", ["neutral", "friendly"])
        mutations = [
            lambda answer: answer.update(choice="hostile"),
            lambda answer: answer["probabilities"].pop(),
            lambda answer: answer["probabilities"][0].update(probability=float("nan")),
            lambda answer: answer["probabilities"][0].update(value="friendly"),
            lambda answer: answer.update(confidence=True),
        ]
        for mutate in mutations:
            answer = choice_answer(question, "neutral")
            mutate(answer)
            self.assertEqual(DecisionBatch.from_response([question], {"answers": [answer]}).answers, {})

    def test_valid_choice_ignores_confidence_and_selected_probability(self):
        question = choice_question("tone", "Tone?", ["neutral", "friendly"])
        for confidence, probability in [(0, 0.01), (0.8, 0.99), (0.99, 0.8)]:
            batch = DecisionBatch.from_response([question], {"answers": [choice_answer(question, "neutral", confidence=confidence, probability=probability)]})
            self.assertEqual(batch.choice("tone"), "neutral")
            self.assertEqual(batch.answers["tone"]["confidence"], confidence)
            self.assertFalse(batch.unresolved)

    def test_score_is_weighted_level_index(self):
        question = score_question("impact", "Impact?", ["0", "10", "20"])
        answer = {"name": "impact", "type": "score", "confidence": 0, "score": 1.3,
                  "probabilities": [{"value": 0, "label": "0", "probability": 0.2},
                                    {"value": 1, "label": "10", "probability": 0.3},
                                    {"value": 2, "label": "20", "probability": 0.5}]}
        batch = DecisionBatch.from_response([question], {"answers": [answer]})
        self.assertAlmostEqual(batch.score("impact"), 1.3)
        answer["score"] = 2
        self.assertIsNone(DecisionBatch.from_response([question], {"answers": [answer]}).score("impact"))

    def test_typed_boolean_choice_and_string_are_distinct(self):
        question = choice_question("typed", "Typed?", [True, "true"])
        answer = choice_answer(question, True)
        self.assertIs(DecisionBatch.from_response([question], {"answers": [answer]}).choice("typed"), True)

    def test_local_and_disabled_never_enable_decisions(self):
        from app.core import config
        with patch.object(config, "DECISIONS_ENABLED", True, create=True), patch.object(config, "LLM_MODE", "local"):
            self.assertFalse(enabled("state"))
        with patch.object(config, "DECISIONS_ENABLED", False, create=True), patch.object(config, "LLM_MODE", "hosted"):
            self.assertFalse(enabled("state"))


class DirectStateTests(unittest.TestCase):
    def test_direct_emotion_rises_and_recovers_without_friction(self):
        state = EmotionalState(emotions={"joy": BoundedTrait(value=90), "sadness": BoundedTrait(value=95)})
        result, audit = apply_proposals("emotion", state, [StateProposal("joy", 7, "decisions", 0.71), StateProposal("sadness", -7, "decisions", 0.71)])
        self.assertEqual(result.emotions["joy"].value, 97)
        self.assertEqual(result.emotions["sadness"].value, 88)
        self.assertEqual([item["actual_delta"] for item in audit], [7, -7])
        self.assertEqual(state.emotions["joy"].value, 90)

    def test_mixed_sources_retain_legacy_math_and_zero_bug_per_dimension(self):
        state = EmotionalState(emotions={"joy": BoundedTrait(value=50), "sadness": BoundedTrait(value=50)})
        fallback = fallback_proposals("emotion", {"deltas": {"joy": -7, "sadness": 7}, "confidence": 0}, ["sadness"])
        result, audit = apply_proposals("emotion", state, [StateProposal("joy", 7, "decisions", 0.7)] + fallback)
        self.assertEqual(result.emotions["joy"].value, 57)
        self.assertEqual(result.emotions["sadness"].value, 52)
        self.assertEqual([item["source"] for item in audit], ["decisions", "legacy"])

    def test_bounds_caps_zero_and_duplicate_rejection(self):
        state = EmotionalState(emotions={"joy": BoundedTrait(value=98, min=20, max=99)})
        result, audit = apply_proposals("emotion", state, [StateProposal("joy", 100, "decisions")])
        self.assertEqual(result.emotions["joy"].value, 99)
        self.assertEqual(audit[0]["requested_delta"], 100)
        self.assertEqual(audit[0]["actual_delta"], 1)
        result, audit = apply_proposals("emotion", state, [StateProposal("joy", 0, "decisions")])
        self.assertEqual(result.emotions["joy"].value, 98)
        self.assertEqual(audit[0]["actual_delta"], 0)
        with self.assertRaises(ValueError):
            apply_proposals("emotion", state, [StateProposal("joy", 1, "decisions"), StateProposal("joy", 1, "legacy")])

    def test_personality_sentiment_caps_and_custom_dimensions(self):
        personality = PersonalityMatrix(traits={"rich_custom": BoundedTrait(value=50)})
        sentiment = SentimentMatrix(sentiments={"trust": BoundedTrait(value=50)})
        self.assertEqual(apply_proposals("personality", personality, [StateProposal("rich_custom", 8, "decisions")])[0].traits["rich_custom"].value, 53)
        self.assertEqual(apply_proposals("sentiment", sentiment, [StateProposal("trust", -9, "decisions")])[0].sentiments["trust"].value, 45)
        self.assertEqual(len(state_questions("personality", personality.traits)[0]["choices"]), 7)
        self.assertIn("rich_custom", state_questions("personality", personality.traits)[0]["instructions"])

    def test_state_batch_keeps_resolved_zero_and_partial_unresolved(self):
        traits = {"joy": BoundedTrait(value=50), "sadness": BoundedTrait(value=50)}
        questions = state_questions("emotion", traits)
        batch = DecisionBatch.from_response(questions, {"answers": [choice_answer(questions[0], "0", confidence=0.7, probability=0.5)]})
        proposals = proposals_from_batch("emotion", traits, batch)
        self.assertEqual([(item.dimension, item.delta) for item in proposals], [("joy", 0)])

    def test_passive_decay_is_deterministic_at_custom_minimum(self):
        state = EmotionalState(emotions={"joy": BoundedTrait(value=21, min=20), "sadness": BoundedTrait(value=0)})
        result, _ = apply_proposals("emotion", state, decay_proposals(state.emotions))
        self.assertEqual(result.emotions["joy"].value, 20)
        self.assertEqual(result.emotions["sadness"].value, 0)


class AdapterTests(unittest.IsolatedAsyncioTestCase):
    async def test_call_disables_sdk_retries_and_preserves_answer_during_ledger_outage(self):
        question = predicate_question("gate", "Gate?")
        client = MagicMock()
        client.decisions.with_raw_response.create.return_value.content = json.dumps({"answers": [{"name": "gate", "type": "predicate", "probability": 0.99}]}).encode()
        with patch("app.services.decisions.enabled", return_value=True), \
             patch("app.services.decisions.openai.OpenAI", return_value=client) as factory, \
             patch("app.services.accounting.flush", new=AsyncMock(side_effect=ConnectionError)):
            result = await evaluate({"message": "private original message"}, [question], feature="autonomy", stage="thought_gate")
        self.assertTrue(result.predicate("gate"))
        self.assertEqual(factory.call_args.kwargs["max_retries"], 0)
        self.assertEqual(factory.call_args.kwargs["timeout"], 5.0)
        self.assertIn("private original message", client.decisions.with_raw_response.create.call_args.kwargs["input"])
        client.close.assert_called_once()

    async def test_constructor_failure_yields_unresolved_fallback(self):
        question = predicate_question("gate", "Gate?")
        with patch("app.services.decisions.enabled", return_value=True), \
             patch("app.services.decisions.openai.OpenAI", side_effect=RuntimeError), \
             patch("app.services.accounting.flush", new=AsyncMock()):
            result = await evaluate({}, [question])
        self.assertIsNone(result.predicate("gate"))
        self.assertEqual(result.error, "RuntimeError")

    async def test_disabled_adapter_does_not_create_client(self):
        with patch("app.services.decisions.enabled", return_value=False), \
             patch("app.services.decisions.openai.OpenAI") as factory:
            result = await evaluate({}, [predicate_question("gate", "Gate?")])
        factory.assert_not_called()
        self.assertIsNone(result.predicate("gate"))


if __name__ == "__main__":
    unittest.main()
