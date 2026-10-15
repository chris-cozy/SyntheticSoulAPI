from copy import deepcopy
from datetime import timezone
import json
from pathlib import Path
import random
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

from scripts.replay import check_bounds, fixed_datetime, safe_database_name, validate_snapshot, worker


class ReplayTests(unittest.TestCase):
    def test_production_database_rejected(self):
        for name in ("production", "syntheticsoul", "syntheticsoul_replay_../prod", "syntheticsoul_replay_prod.$cmd", "syntheticsoul_replay_a" * 8):
            with self.assertRaises(ValueError): safe_database_name(name)
        self.assertEqual(safe_database_name("syntheticsoul_replay_test_baseline"), "syntheticsoul_replay_test_baseline")

    def snapshot(self):
        return {"owner_id": "owner", "agent_name": "jasmine", "mode": "lite", "collections": {
            "agent_lite": [{"_id": "agentid", "name": "jasmine"}],
            "user_lite": [{"_id": "userid", "user_id": "owner", "agent_perspective": "jasmine"}]}}

    def test_snapshot_identity_and_authentication_exclusion(self):
        self.assertEqual(validate_snapshot(self.snapshot())["owner_id"], "owner")
        for change in ("auth", "wrong_agent", "missing_id"):
            snapshot = self.snapshot()
            if change == "auth": snapshot["collections"]["auth"] = []
            elif change == "wrong_agent": snapshot["agent_name"] = "someone_else"
            else: snapshot["collections"]["agent_lite"][0].pop("_id")
            with self.assertRaises(ValueError): validate_snapshot(snapshot)

    def test_fixed_clock_timezone_semantics(self):
        fixed = fixed_datetime("2026-10-11T12:00:00Z")
        self.assertEqual(fixed.now(timezone.utc).isoformat(), "2026-10-11T12:00:00+00:00")
        self.assertIsNone(fixed.now().tzinfo)
        self.assertEqual(fixed.utcnow(), fixed.now())

    def test_bound_violation_reports_dimension(self):
        self.assertEqual(check_bounds({"emotional_status": {"emotions": {"joy": {"value": 100, "min": 0, "max": 100}}}}), [])
        self.assertEqual(check_bounds({"emotional_status": {"emotions": {"joy": {"value": 101, "min": 0, "max": 100}}}}), ["emotional_status.joy:out_of_bounds"])


class ReplayPipelineTests(unittest.IsolatedAsyncioTestCase):
    async def test_identical_snapshot_seed_clock_and_background_per_repetition(self):
        from app.domain.models import GenerateReplyTaskResponse, MessageResponse
        from app.services import accounting, database, message_processor
        class Collection:
            def __init__(self): self.docs = []
            async def delete_many(self, query): self.docs.clear()
            async def insert_many(self, docs): self.docs.extend(deepcopy(docs))
            def find(self, query): return self
            async def find_one(self, query): return None
            async def to_list(self, length=None): return []
        class Database(dict):
            name = "syntheticsoul_replay_unit"
            def __missing__(self, key): self[key] = Collection(); return self[key]
        db = Database()
        client = Mock(drop_database=AsyncMock())
        snapshot = ReplayTests().snapshot()
        calls = []
        async def generate(request):
            self.assertEqual(db["agent_lite"].docs, snapshot["collections"]["agent_lite"])
            calls.append((random.random(), message_processor.datetime.now(timezone.utc).isoformat()))
            db["agent_lite"].docs.append({"_id": "changed"})
            return GenerateReplyTaskResponse(message_response=MessageResponse(response="fixture", time=1, expression="neutral"), user_id="owner", queries=[])
        async def cost(run_id, owner):
            return {"run_id": run_id, "kind": "exchange", "accounting_complete": True, "total_cost_usd": ".01", "known_cost_usd": ".01", "stages": {}, "metadata": {"variant": "baseline"}}
        with tempfile.TemporaryDirectory() as directory:
            cases = Path(directory) / "cases.json"
            cases.write_text(json.dumps([{"id": "case", "message": "Hello."}]), encoding="utf-8")
            output = Path(directory) / "output.json"
            args = SimpleNamespace(clock="2026-10-11T12:00:00Z", cases=str(cases), seed=12, session="test", variant="baseline", warm_repetitions=2, autonomy=False, keep_db=False, output=str(output))
            original_clock = message_processor.datetime
            with patch("app.core.config.validate_llm_configuration"), \
                 patch.object(database, "init_db", AsyncMock()), \
                 patch.object(database, "get_database", AsyncMock(return_value=db)), \
                 patch.object(database, "_db_client", client), \
                 patch.object(database, "grab_self", AsyncMock(return_value=snapshot["collections"]["agent_lite"][0])), \
                 patch.object(database, "grab_user", AsyncMock(return_value=snapshot["collections"]["user_lite"][0])), \
                 patch.object(database, "next_interaction_sequence", AsyncMock(return_value=1)), \
                 patch.object(message_processor, "generate_response", AsyncMock(side_effect=generate)), \
                 patch.object(message_processor, "post_processing", AsyncMock()) as background, \
                 patch.object(accounting, "begin_run", AsyncMock()), \
                 patch.object(accounting, "mark_phase", AsyncMock()), \
                 patch.object(accounting, "get_cost", AsyncMock(side_effect=cost)):
                await worker(args, snapshot)
            self.assertEqual(background.await_count, 3)
            self.assertEqual(len(calls), 3)
            self.assertEqual(len(set(calls)), 1)
            self.assertEqual(calls[0][1], "2026-10-11T12:00:00+00:00")
            self.assertIs(message_processor.datetime, original_clock)
            self.assertEqual(len(json.loads(output.read_text(encoding="utf-8"))["outcomes"]), 3)
            client.drop_database.assert_awaited_once_with("syntheticsoul_replay_unit")


if __name__ == "__main__": unittest.main()
