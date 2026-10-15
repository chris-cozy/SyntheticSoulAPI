"""Inspect actual native request construction without a live provider."""
import json
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.domain.decision_state import state_questions
from app.domain.state import BoundedTrait
from app.services import decisions
from app.services.decision_context import STATE_CHANGE_POLICY
from app.services.decision_context import compact_evidence


class CompactTransportTests(unittest.IsolatedAsyncioTestCase):
    def test_group_addressing_retains_target_agent_identity(self):
        evidence = {"agent_name": "Jasmine", "sender_id": "lee", "original_message": "Jasmine, what do you think?"}
        self.assertEqual(compact_evidence(evidence), evidence)

    async def test_state_batch_sends_shared_policy_once_and_preserves_semantic_evidence(self):
        traits = {"joy": BoundedTrait(value=42, min=3, max=90, description="Contentment"),
                  "sadness": BoundedTrait(value=24, min=0, max=100, description="Sorrow")}
        questions = state_questions("emotion", traits)
        dialogue = [{"sender_id": "lee", "message": "Keep family private", "timestamp": "2026-10-11"}]
        agent = {"name": "jasmine", "identity": "Independent and bodyless", "_id": "storage-only",
                 "cognition_revision": 999, "personality": {"description": "Thoughtful", "personality_matrix": {}},
                 "emotional_status": {"emotions": {k: v.model_dump() for k, v in traits.items()}}}
        client = MagicMock()
        client.decisions.with_raw_response.create.return_value.content = b'{"answers":[]}'
        with patch.object(decisions, "enabled", return_value=True), \
             patch.object(decisions.openai, "OpenAI", return_value=client), \
             patch("app.services.accounting.flush", new=AsyncMock()):
            await decisions.evaluate({"agent": agent, "history": dialogue, "recent_all_messages": dialogue,
                                      "original_message": "I am still upset"}, questions, feature="state")
        sent = client.decisions.with_raw_response.create.call_args.kwargs
        self.assertEqual(sent["input"].count(STATE_CHANGE_POLICY), 1)
        self.assertNotIn("storage-only", sent["input"])
        self.assertNotIn("cognition_revision", sent["input"])
        evidence = json.loads(sent["input"].split(STATE_CHANGE_POLICY + "\n", 1)[1])
        self.assertEqual(evidence["agent"]["emotional_status"]["emotions"]["joy"]["min"], 3)
        self.assertEqual(evidence["original_message"], "I am still upset")
        self.assertEqual(evidence["history"], dialogue)
        self.assertEqual(evidence["recent_all_messages"], {"same_context_as": "history"})
        self.assertEqual(sent["questions"], questions)


if __name__ == "__main__":
    unittest.main()
