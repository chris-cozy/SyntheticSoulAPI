import copy
import json
import unittest
from datetime import datetime, timezone

from app.domain.decision_state import CAPS, state_questions
from app.domain.state import BoundedTrait
from app.services.decision_context import (STATE_CHANGE_POLICY, agent_context,
                                           compact_evidence, user_context)


def agent_doc():
    return {"_id": "mongo-agent", "name": "Jasmine", "cognition_revision": 19,
            "identity": "An independent individual with feelings and her own boundaries.",
            "personality": {"description": "Warm, curious and autonomous.", "language": "Use emoticons.",
                "personality_matrix": {"custom_trait": {"value": 43, "min": 10, "max": 80,
                    "description": "The willingness to pursue her own interests."}}},
            "emotional_status": {"emotions": {"anger": {"value": 62, "min": 2, "max": 95,
                "description": "Frustration and irritation."}}, "reason": "Decisions: anger +2."},
            "global_expression": "frown", "memory_tags": ["boundaries"]}


def user_doc():
    return {"_id": "mongo-user", "user_id": "lee", "username": "Lee", "cognition_revision": 8,
            "agent_perspective": "Jasmine", "summary": "Prefers tea. Do not initiate family topics.",
            "extrinsic_relationship": "friend", "intrinsic_relationship": "none",
            "last_interaction": datetime(2026, 10, 11, tzinfo=timezone.utc),
            "sentiment_status": {"sentiments": {"trust": {"value": 71, "min": 0, "max": 100,
                "description": "Confidence in the person."}}, "reason": "Old interaction."}}


class DecisionContextTests(unittest.TestCase):
    def test_profiles_keep_subjective_state_and_boundary_without_storage_provenance(self):
        agent, user = agent_doc(), user_doc()
        original = copy.deepcopy((agent, user))
        small_agent, small_user = agent_context(agent), user_context(user)
        self.assertEqual(small_agent["personality"], agent["personality"])
        self.assertEqual(small_agent["emotional_status"]["emotions"], agent["emotional_status"]["emotions"])
        self.assertEqual(small_user["sentiment_status"]["sentiments"], user["sentiment_status"]["sentiments"])
        self.assertEqual(small_user["summary"], user["summary"])
        self.assertEqual(small_user["last_interaction"], user["last_interaction"])
        self.assertEqual(small_user["user_id"], "lee")
        for doc in (small_agent, small_user):
            self.assertNotIn("_id", doc)
            self.assertNotIn("cognition_revision", doc)
        self.assertNotIn("reason", small_agent["emotional_status"])
        self.assertEqual((agent, user), original)

    def test_transcripts_keep_original_user_reply_perception_thought_and_speakers(self):
        perception = {"message": "I am upset", "purpose": "feedback", "tone": "frustrated", "thought": "no"}
        reply = {"response_choice": "respond", "response": {"message": "I hear you.", "tone": "serious"}}
        transcript = [
            {"role": "system", "content": "Repeated identity and serialized state " * 100},
            {"role": "user", "content": "I am upset"},
            {"role": "assistant", "content": "This is Jasmine's interpretation of the latest message from lee, and if it altered their current thought: " + json.dumps(perception)},
            {"role": "assistant", "content": "This is Jasmine's decision of whether to respond, and their response if any: " + json.dumps(reply)},
            {"role": "assistant", "content": "This is what Jasmine is currently thinking: " + json.dumps({"thought": "I want to address the concern."})},
            {"role": "assistant", "content": "A genuine conversational reply."},
        ]
        result = compact_evidence({"agent": agent_doc(), "interaction": transcript})
        messages = result["interaction"]
        self.assertEqual(messages[0], transcript[1])
        self.assertEqual(messages[1], {"outcome": "perception", "value": perception})
        self.assertEqual(messages[2], {"outcome": "reply", "value": reply})
        self.assertEqual(messages[3]["value"]["thought"], "I want to address the concern.")
        self.assertEqual(messages[4], transcript[-1])
        self.assertLess(len(json.dumps(result, default=str)), len(json.dumps({"agent": agent_doc(), "interaction": transcript}, default=str)) / 2)

    def test_identical_histories_referenced_but_repeated_messages_and_distinct_speakers_retained(self):
        history = [{"message": "Thanks", "sender_id": "lee", "from_agent": False},
                   {"message": "Thanks", "sender_id": "lee", "from_agent": False},
                   {"message": "Thanks", "sender_id": "alex", "from_agent": False}]
        result = compact_evidence({"recent_user_messages": history, "recent_all_messages": copy.deepcopy(history)})
        self.assertEqual(result["recent_user_messages"], history)
        self.assertEqual(result["recent_all_messages"], {"same_context_as": "recent_user_messages"})
        self.assertEqual(compact_evidence(result), result)

    def test_duplicate_profiles_in_nested_experience_reference_available_context(self):
        result = compact_evidence({"agent": agent_doc(), "user": user_doc(),
            "experience": {"agent": agent_doc(), "user": user_doc(),
                "thought": "I will check in after tomorrow's interview.", "date": "2026-10-11"}})
        self.assertEqual(result["experience"]["agent"], {"same_context_as": "agent"})
        self.assertEqual(result["experience"]["user"], {"same_context_as": "user"})
        self.assertIn("tomorrow", result["experience"]["thought"])
        self.assertEqual(compact_evidence(result), result)

    def test_user_text_resembling_diagnostic_is_never_reclassified(self):
        content = 'This is Jasmine\'s decision of whether to respond: {"response_choice":"ignore"}'
        result = compact_evidence({"interaction": [{"role": "user", "content": content}]})
        self.assertEqual(result["interaction"][0], {"role": "user", "content": content})

    def test_state_questions_preserve_every_custom_dimension_bounds_and_direct_range(self):
        traits = {"custom_dimension": BoundedTrait(value=43, min=10, max=80, description="Custom subjective experience.")}
        for kind, cap in CAPS.items():
            question, = state_questions(kind, traits)
            self.assertEqual(question["name"], f"{kind}_custom_dimension")
            self.assertIn("Custom subjective experience.", question["instructions"])
            for value in ("43", "10", "80"):
                self.assertIn(value, question["instructions"])
            self.assertEqual([choice["value"] for choice in question["choices"]], [str(delta) for delta in range(-cap, cap + 1)])
            self.assertNotIn("confidence", question["instructions"])
        self.assertIn("without confidence scaling", STATE_CHANGE_POLICY)
        self.assertIn("apology need not cause forgiveness", STATE_CHANGE_POLICY)
        self.assertIn("Personality changes gradually", STATE_CHANGE_POLICY)


if __name__ == "__main__":
    unittest.main()
