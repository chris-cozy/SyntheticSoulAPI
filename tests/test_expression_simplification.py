"""Routine subjective choices stay bounded without a second model judgment."""
import unittest
from unittest.mock import AsyncMock, patch

from app.services import decision_tasks, decisions


def weak_batch(questions, selections):
    answers = []
    for question in questions:
        choice = selections[question["name"]]
        answers.append({"name": question["name"], "type": "choice", "choice": choice,
                        "confidence": .01,
                        "probabilities": [{"value": item["value"], "probability": 1 / len(question["choices"])}
                                          for item in question["choices"]]})
    return decisions.DecisionBatch.from_response(questions, {"answers": answers})


class ExpressionSimplificationTests(unittest.IsolatedAsyncioTestCase):
    async def test_valid_low_confidence_expression_is_accepted_without_writer(self):
        async def evaluate(_evidence, questions, **_kwargs):
            return weak_batch(questions, {"expression": "joy"})

        with patch.object(decision_tasks, "get_available_expressions", return_value=["calm", "joy"]), \
             patch.object(decision_tasks, "enabled", return_value=True), \
             patch.object(decision_tasks.decisions, "evaluate", AsyncMock(side_effect=evaluate)) as evaluate_mock, \
             patch.object(decision_tasks, "structured_query", AsyncMock()) as writer:
            expression = await decision_tasks.select_expression({"global_expression": "calm"}, {"reply": "Thank you"})
            self.assertEqual(expression, "joy")
            evaluate_mock.assert_awaited_once()
            writer.assert_not_awaited()

    async def test_invalid_answer_retains_installed_asset_without_writer(self):
        async def evaluate(_evidence, questions, **_kwargs):
            # An invented asset never survives the adapter's schema checks.
            return weak_batch(questions, {"expression": "invented"})

        for current, legacy, expected in (("calm", "no", "calm"), ("calm", "joy", "joy"),
                                          ("missing", "invented", "calm")):
            with self.subTest(current=current, legacy=legacy), \
                 patch.object(decision_tasks, "get_available_expressions", return_value=["calm", "joy"]), \
                 patch.object(decision_tasks, "enabled", return_value=True), \
                 patch.object(decision_tasks.decisions, "evaluate", AsyncMock(side_effect=evaluate)), \
                 patch.object(decision_tasks, "structured_query", AsyncMock()) as writer:
                self.assertEqual(await decision_tasks.select_expression({"global_expression": current}, {}, legacy), expected)
                writer.assert_not_awaited()

    async def test_one_installed_asset_needs_no_provider_call(self):
        with patch.object(decision_tasks, "get_available_expressions", return_value=["calm"]), \
             patch.object(decision_tasks, "enabled", return_value=True), \
             patch.object(decision_tasks.decisions, "evaluate", AsyncMock()) as evaluate, \
             patch.object(decision_tasks, "structured_query", AsyncMock()) as writer:
            self.assertEqual(await decision_tasks.select_expression({"global_expression": "missing"}, {}), "calm")
            evaluate.assert_not_awaited()
            writer.assert_not_awaited()

    async def test_disabled_expression_keeps_legacy_behavior(self):
        with patch.object(decision_tasks, "get_available_expressions", return_value=["calm", "joy"]), \
             patch.object(decision_tasks, "enabled", return_value=False), \
             patch.object(decision_tasks.decisions, "evaluate", AsyncMock()) as evaluate:
            self.assertEqual(await decision_tasks.select_expression({"global_expression": "calm"}, {}, "joy"), "joy")
            self.assertEqual(await decision_tasks.select_expression({"global_expression": "calm"}, {}, "invalid"), "calm")
            evaluate.assert_not_awaited()

    async def test_participation_and_outreach_accept_valid_weak_choices(self):
        async def evaluate(_evidence, questions, **_kwargs):
            return weak_batch(questions, {questions[0]["name"]: questions[0]["choices"][0]["value"]})

        with patch.object(decision_tasks.decisions, "evaluate", AsyncMock(side_effect=evaluate)):
            participation = await decision_tasks.select("participation", "Choose freely", ["ignore", "respond"], {}, "participation")
            outreach = await decision_tasks.select("outreach_action", "Respect recipient boundaries", ["keep", "suppress", "revise"], {}, "autonomy")
        self.assertEqual(participation, "ignore")
        self.assertEqual(outreach, "keep")

    async def test_perception_and_commitment_directive_accept_valid_weak_choices(self):
        questions = [decisions.choice_question("purpose", "Purpose", ["other", "question"]),
                     decisions.choice_question("tone", "Tone", ["other", "friendly"]),
                     decisions.choice_question("directive", "Durable commitment", ["unchanged", "fulfilled", "cancelled"])]
        batch = weak_batch(questions, {"purpose": "other", "tone": "other", "directive": "fulfilled"})
        with patch.object(decision_tasks.decisions, "evaluate", AsyncMock(return_value=batch)):
            resolved = await decision_tasks.evaluate_categories(questions, {}, "perception")
        self.assertEqual(resolved, {"purpose": "other", "tone": "other", "directive": "fulfilled"})

    async def test_identity_choice_accepts_valid_weak_selection(self):
        questions = [decisions.choice_question("identity", "Identity continuity", ["unchanged", "revised"])]
        with patch.object(decision_tasks.decisions, "evaluate", AsyncMock(return_value=weak_batch(questions, {"identity": "revised"}))):
            self.assertEqual(await decision_tasks.evaluate_categories(questions, {}, "identity"), {"identity": "revised"})


if __name__ == "__main__":
    unittest.main()
