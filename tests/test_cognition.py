import copy
import unittest
from types import SimpleNamespace

from app.services.cognition import commit_snapshot, evaluate_and_commit


class Collection:
    def __init__(self, doc):
        self.doc = copy.deepcopy(doc)
        self.conflicts = 0
        self.raise_after = False
        self.raise_before = False
        self.read_error = False
        self.writes = 0

    async def find_one(self, query):
        if self.read_error:
            raise ConnectionError("unavailable")
        return copy.deepcopy(self.doc)

    async def update_one(self, query, update):
        self.writes += 1
        if self.raise_before:
            raise ConnectionError("lost")
        if self.conflicts:
            self.conflicts -= 1
            self.doc["cognition_revision"] = self.doc.get("cognition_revision", 0) + 1
            self.doc["value"] = self.doc.get("value", 0) + 10
            return SimpleNamespace(matched_count=0)
        revision = self.doc.get("cognition_revision", 0)
        matches = (revision == query.get("cognition_revision")) if "$or" not in query else revision == 0
        if not matches:
            return SimpleNamespace(matched_count=0)
        self.doc.update(update["$set"])
        self.doc["cognition_revision"] = revision + 1
        if self.raise_after:
            raise ConnectionError("lost acknowledgement")
        return SimpleNamespace(matched_count=1)


class CognitionTests(unittest.IsolatedAsyncioTestCase):
    async def test_revisionless_document_lazily_increments_only_intended_fields(self):
        snapshot = {"_id": "agent", "value": 1, "identity": "unchanged"}
        collection = Collection(snapshot)
        result = await commit_snapshot(collection, snapshot, {"value": 2})
        self.assertTrue(result)
        self.assertEqual(collection.doc, {"_id": "agent", "value": 2, "identity": "unchanged", "cognition_revision": 1})

    async def test_stale_delta_cannot_overwrite_winner(self):
        snapshot = {"_id": "agent", "value": 1, "cognition_revision": 1}
        collection = Collection({**snapshot, "cognition_revision": 2, "value": 10})
        result = await commit_snapshot(collection, snapshot, {"value": 2})
        self.assertEqual(result.status, "conflict")
        self.assertEqual(collection.doc["value"], 10)

    async def test_definite_conflict_reevaluates_against_fresh_state(self):
        collection = Collection({"_id": "agent", "value": 1})
        collection.conflicts = 1
        observed = []
        async def evaluate(snapshot):
            observed.append(snapshot["value"])
            return {"value": snapshot["value"] + 1}, "audit"
        result = await evaluate_and_commit(collection, {"_id": "agent"}, evaluate)
        self.assertEqual(observed, [1, 11])
        self.assertEqual(collection.doc["value"], 12)
        self.assertEqual(result.attempts, 2)

    async def test_exhausted_conflicts_leave_winner_unchanged(self):
        collection = Collection({"_id": "agent", "value": 1})
        collection.conflicts = 4
        async def evaluate(snapshot):
            return {"value": snapshot["value"] + 1}, None
        result = await evaluate_and_commit(collection, {"_id": "agent"}, evaluate)
        self.assertEqual(result.status, "conflict")
        self.assertEqual(collection.writes, 3)
        self.assertEqual(collection.doc["value"], 31)
        self.assertEqual(result.snapshot["value"], 31)

    async def test_uncertain_applied_write_readback_prevents_double_delta(self):
        collection = Collection({"_id": "agent", "value": 1})
        collection.raise_after = True
        async def evaluate(snapshot):
            return {"value": snapshot["value"] + 1}, None
        result = await evaluate_and_commit(collection, {"_id": "agent"}, evaluate)
        self.assertEqual(result.status, "committed")
        self.assertEqual(collection.writes, 1)
        self.assertEqual(collection.doc["value"], 2)

    async def test_uncertain_unapplied_write_does_not_blindly_repeat(self):
        collection = Collection({"_id": "agent", "value": 1})
        collection.raise_before = True
        async def evaluate(snapshot):
            return {"value": snapshot["value"] + 1}, None
        result = await evaluate_and_commit(collection, {"_id": "agent"}, evaluate)
        self.assertEqual(result.status, "unknown")
        self.assertEqual(collection.writes, 1)
        self.assertEqual(collection.doc["value"], 1)

    async def test_rejects_reserved_field_mutations(self):
        collection = Collection({"_id": "agent"})
        with self.assertRaises(ValueError):
            await commit_snapshot(collection, collection.doc, {"cognition_revision": 100})

    async def test_unchanged_interaction_local_result_reevaluates_after_state_drift(self):
        collection = Collection({"_id": "agent", "value": 1})
        observed = []
        async def evaluate(snapshot):
            observed.append(snapshot["value"])
            if len(observed) == 1:
                collection.doc["value"] = 9
                collection.doc["cognition_revision"] = 1
            return {}, snapshot["value"]
        result = await evaluate_and_commit(collection, {"_id": "agent"}, evaluate)
        self.assertEqual(result.status, "unchanged")
        self.assertEqual(result.value, 9)
        self.assertEqual(observed, [1, 9])
        self.assertEqual(collection.writes, 0)


if __name__ == "__main__":
    unittest.main()
