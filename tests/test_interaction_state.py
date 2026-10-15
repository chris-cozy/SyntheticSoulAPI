import copy
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.services import interaction_decisions
from app.services.decisions import DecisionBatch
from app.services.emotion_decay import decay_once


def agent_doc():
    return {"_id": "agent", "name": "jasmine", "identity": "An independent bodyless individual.",
            "personality": {"personality_matrix": {"warmth": {"value": 50, "min": 0, "max": 100}}},
            "emotional_status": {"emotions": {
                "joy": {"value": 50, "min": 0, "max": 100},
                "sadness": {"value": 50, "min": 0, "max": 100}}, "reason": None}}


class StateCollection:
    def __init__(self, doc):
        self.doc = copy.deepcopy(doc)
        self.conflicts = 0
        self.writes = 0
        self.raise_after = False

    async def find_one(self, query):
        return copy.deepcopy(self.doc)

    async def update_one(self, query, update):
        self.writes += 1
        revision = self.doc.get("cognition_revision", 0)
        if self.conflicts:
            self.conflicts -= 1
            self.doc["emotional_status"]["emotions"]["joy"]["value"] += 10
            self.doc["cognition_revision"] = revision + 1
            return SimpleNamespace(matched_count=0)
        matches = revision == 0 if "$or" in query else revision == query.get("cognition_revision")
        if not matches:
            return SimpleNamespace(matched_count=0)
        self.doc.update(copy.deepcopy(update["$set"]))
        self.doc["cognition_revision"] = revision + 1
        if self.raise_after:
            raise ConnectionError("write acknowledged late")
        return SimpleNamespace(matched_count=1)


class Events:
    def __init__(self):
        self.events = []

    async def insert_one(self, event):
        self.events.append(copy.deepcopy(event))


def partial_answers(evidence, questions, **kwargs):
    answers = []
    for question in questions:
        name = question["name"]
        if name == "emotion_sadness":
            answers.append({"name": name, "type": "refusal"})
            continue
        chosen = "7" if name == "emotion_joy" else "0"
        answers.append({"name": name, "type": "choice", "choice": chosen, "confidence": 0.75,
            "probabilities": [{"value": item["value"], "probability": 0.75 if item["value"] == chosen else 0.25 / (len(question["choices"]) - 1)}
                              for item in question["choices"]]})
    return DecisionBatch.from_response(questions, {"answers": answers})


class InteractionStateTests(unittest.IsolatedAsyncioTestCase):
    async def run_reply(self, collection):
        agent = agent_doc()
        events = Events()
        db = {interaction_decisions.database.AGENT_COLLECTION: collection, "state_events": events}
        fallback = AsyncMock(return_value={"emotion_deltas": {"deltas": {"joy": -7, "sadness": 7}, "confidence": 0, "reason": "Legacy evidence"}})
        evaluator = AsyncMock(side_effect=partial_answers)
        with patch.object(interaction_decisions.database, "get_database", new=AsyncMock(return_value=db)), \
             patch.object(interaction_decisions.decisions, "evaluate", new=evaluator), \
             patch.object(interaction_decisions.decisions, "enabled", return_value=True), \
             patch.object(interaction_decisions, "structured_query", new=fallback), \
             patch.object(interaction_decisions, "build_personality_emotional_delta_prompt", return_value="State task"), \
             patch.object(interaction_decisions, "_system_message", return_value={"role": "system", "content": "Individual"}):
            result = await interaction_decisions.evaluate_reply_state(agent, {}, [], [], "2026-10-11", "I appreciate you", {})
        return agent, result, fallback, evaluator, events

    async def test_partial_batch_single_fallback_cannot_replace_accepted_dimension(self):
        collection = StateCollection(agent_doc())
        agent, result, fallback, evaluator, events = await self.run_reply(collection)
        self.assertEqual(collection.doc["emotional_status"]["emotions"]["joy"]["value"], 57)
        self.assertEqual(collection.doc["emotional_status"]["emotions"]["sadness"]["value"], 52)
        self.assertEqual(fallback.await_count, 1)
        schema = fallback.call_args.args[1]["json_schema"]["schema"]
        self.assertEqual(set(schema["properties"]), {"emotion_deltas"})
        self.assertEqual(set(schema["properties"]["emotion_deltas"]["properties"]["deltas"]["properties"]), {"sadness"})
        self.assertEqual(agent["cognition_revision"], 1)
        self.assertEqual(collection.doc["personality"]["personality_matrix"]["warmth"]["value"], 50)
        self.assertEqual(events.events[0]["dimensions"][0]["source"], "decisions")

    async def test_conflict_reevaluates_latest_emotions_without_double_application(self):
        collection = StateCollection(agent_doc())
        collection.conflicts = 1
        agent, result, fallback, evaluator, events = await self.run_reply(collection)
        self.assertEqual(collection.doc["emotional_status"]["emotions"]["joy"]["value"], 67)
        self.assertEqual(collection.doc["emotional_status"]["emotions"]["sadness"]["value"], 52)
        self.assertEqual(evaluator.await_count, 2)
        self.assertEqual(fallback.await_count, 2)
        self.assertEqual(collection.writes, 2)
        self.assertEqual(len(events.events), 2)  # One committed emotional audit and one interaction-local personality audit.
        self.assertEqual(agent["cognition_revision"], 2)

    async def test_lost_write_ack_readback_does_not_repeat_state_model_call(self):
        collection = StateCollection(agent_doc())
        collection.raise_after = True
        agent, result, fallback, evaluator, events = await self.run_reply(collection)
        self.assertEqual(evaluator.await_count, 1)
        self.assertEqual(collection.writes, 1)
        self.assertEqual(collection.doc["emotional_status"]["emotions"]["joy"]["value"], 57)

    async def test_decay_reloads_after_conflict_and_audits_only_committed_change(self):
        collection = StateCollection(agent_doc())
        collection.conflicts = 1
        events = Events()
        db = {interaction_decisions.database.AGENT_COLLECTION: collection, "state_events": events}
        with patch.object(interaction_decisions.database, "grab_self", new=AsyncMock(return_value=agent_doc())), \
             patch.object(interaction_decisions.database, "get_database", new=AsyncMock(return_value=db)):
            result = await decay_once()
        self.assertEqual(result.status, "committed")
        self.assertEqual(collection.doc["emotional_status"]["emotions"]["joy"]["value"], 59)
        self.assertEqual(collection.doc["emotional_status"]["emotions"]["sadness"]["value"], 49)
        self.assertEqual(len(events.events), 1)
        self.assertTrue(all(item["source"] == "decay" for item in events.events[0]["dimensions"]))

    async def test_decay_at_minimum_does_not_increment_revision(self):
        doc = agent_doc()
        for trait in doc["emotional_status"]["emotions"].values():
            trait["value"] = trait["min"]
        collection = StateCollection(doc)
        db = {interaction_decisions.database.AGENT_COLLECTION: collection, "state_events": Events()}
        with patch.object(interaction_decisions.database, "grab_self", new=AsyncMock(return_value=doc)), \
             patch.object(interaction_decisions.database, "get_database", new=AsyncMock(return_value=db)):
            result = await decay_once()
        self.assertEqual(result.status, "unchanged")
        self.assertEqual(collection.writes, 0)


if __name__ == "__main__":
    unittest.main()
