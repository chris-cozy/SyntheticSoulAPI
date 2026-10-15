import copy
import unittest

from app.domain.decision_state import apply_proposals, proposals_from_batch, state_questions
from app.domain.state import BoundedTrait, EmotionalState, PersonalityMatrix, SentimentMatrix
from app.services.decisions import DecisionBatch, choice_question
from app.services.decision_context import STATE_CHANGE_POLICY


def uncertain_choice(question, value):
    count = len(question["choices"])
    return {
        "name": question["name"], "type": "choice", "choice": value,
        "confidence": 0.03,
        "probabilities": [{"value": choice["value"], "probability": 1 / count}
                          for choice in question["choices"]],
    }


class SubjectiveAcceptanceTests(unittest.TestCase):
    def test_state_questions_separate_current_event_from_already_reflected_history(self):
        for kind in ("emotion", "personality", "sentiment"):
            with self.subTest(kind=kind):
                question = state_questions(kind, {"custom": BoundedTrait(value=50)})[0]
                instructions = question["instructions"]
                self.assertIn(f"Direct {kind} delta for custom", instructions)
                self.assertIn("Current value: 50", instructions)
                self.assertIn("minimum: 0; maximum: 100", instructions)
                self.assertNotIn("past events", instructions)
                self.assertIn("latest original incoming message or newest thought", STATE_CHANGE_POLICY)
                self.assertIn("Do not count past events again", STATE_CHANGE_POLICY)
                self.assertIn("an apology need not cause forgiveness", STATE_CHANGE_POLICY)
                self.assertIn("Allow authentic changes in either direction", STATE_CHANGE_POLICY)

    def test_subjective_selection_preserves_uncertainty_without_veto(self):
        question = choice_question("tone", "Select the tone", ["friendly", "neutral", "other"])
        answer = uncertain_choice(question, "other")
        batch = DecisionBatch.from_response([question], {"answers": [answer]})
        self.assertEqual(batch.choice("tone"), "other")
        self.assertFalse(batch.unresolved)
        self.assertEqual(batch.answers["tone"], answer)

    def test_emotion_personality_and_sentiment_apply_low_confidence_deltas_directly(self):
        cases = [
            ("emotion", EmotionalState(emotions={"joy": BoundedTrait(value=50)}), "emotions", "joy", 7),
            ("personality", PersonalityMatrix(traits={"openness": BoundedTrait(value=50)}), "traits", "openness", -3),
            ("sentiment", SentimentMatrix(sentiments={"trust": BoundedTrait(value=50)}), "sentiments", "trust", 5),
        ]
        for kind, state, field, dimension, delta in cases:
            with self.subTest(kind=kind):
                traits = getattr(state, field)
                question = state_questions(kind, traits)[0]
                answer = uncertain_choice(question, str(delta))
                batch = DecisionBatch.from_response([question], {"answers": [answer]})
                proposals = proposals_from_batch(kind, traits, batch)
                result, audit = apply_proposals(kind, state, proposals)
                self.assertEqual(getattr(result, field)[dimension].value, 50 + delta)
                self.assertEqual(getattr(state, field)[dimension].value, 50)
                self.assertEqual(audit[0]["confidence"], 0.03)
                self.assertEqual(audit[0]["source"], "decisions")
                self.assertEqual(audit[0]["provenance"]["probabilities"], answer["probabilities"])

    def test_low_confidence_state_remains_bounded(self):
        state = EmotionalState(emotions={"joy": BoundedTrait(value=98, max=99)})
        question = state_questions("emotion", state.emotions)[0]
        batch = DecisionBatch.from_response([question], {"answers": [uncertain_choice(question, "7")]})
        result, audit = apply_proposals("emotion", state, proposals_from_batch("emotion", state.emotions, batch))
        self.assertEqual(result.emotions["joy"].value, 99)
        self.assertEqual(audit[0]["requested_delta"], 7)
        self.assertEqual(audit[0]["actual_delta"], 1)

    def test_invalid_missing_duplicate_and_refused_choices_still_require_recovery(self):
        question = choice_question("tone", "Select the tone", ["friendly", "neutral"])
        answer = uncertain_choice(question, "friendly")
        invalid = copy.deepcopy(answer)
        invalid["confidence"] = True
        foreign = copy.deepcopy(answer)
        foreign["choice"] = "invented"
        bad_distribution = copy.deepcopy(answer)
        bad_distribution["probabilities"][0]["probability"] = -0.5
        payloads = [[], [answer, answer], [invalid], [foreign], [bad_distribution],
                    [{"name": "tone", "type": "refusal"}]]
        for payload in payloads:
            with self.subTest(payload=payload):
                batch = DecisionBatch.from_response([question], {"answers": payload})
                self.assertIsNone(batch.choice("tone"))
                self.assertIn("tone", batch.unresolved)


if __name__ == "__main__":
    unittest.main()
