import asyncio
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal
import json
import unittest
from unittest.mock import Mock, patch

import httpx

from app.services import accounting as ledger
from app.services.pricing import estimate_cost, normalize_usage
from scripts.cost_report import build_report


class PricingTests(unittest.TestCase):
    def test_chat_cache_writes_are_not_additive_or_reasoning_double_billed(self):
        usage = normalize_usage({"input_tokens": 1000, "output_tokens": 100,
                                 "input_tokens_details": {"cached_tokens": 200, "cache_write_tokens": 300},
                                 "output_tokens_details": {"reasoning_tokens": 70}})
        result = estimate_cost("openai", "chat.completions", "gpt-6-luna", usage)
        expected = (Decimal(500)*Decimal(".10")+Decimal(200)*Decimal(".01")+
                    Decimal(300)*Decimal(".125")+Decimal(100)*Decimal(".50"))/Decimal(1_000_000)
        self.assertEqual(Decimal(result["cost_usd"]), expected)

    def test_decisions_bills_all_input_once(self):
        usage = normalize_usage({"input_tokens": 1000, "input_tokens_details": {
            "cached_tokens": 400, "cache_write_tokens": 600}}, decisions=True)
        result = estimate_cost("openai", "decisions", "gpt-6-luna", usage)
        self.assertEqual(Decimal(result["cost_usd"]), Decimal(".0001"))
        self.assertEqual(result["pricing"]["input_basis"], "total_input_tokens")

    def test_long_context_and_region(self):
        usage = normalize_usage({"input_tokens": 272001, "output_tokens": 100})
        cost = estimate_cost("openai", "decisions", "gpt-6-luna", usage, regional=True)
        self.assertEqual(Decimal(cost["cost_usd"]), Decimal(272001)*Decimal(".22")/Decimal(1_000_000))
        self.assertEqual(cost["pricing"]["context_band"], "long")

    def test_unknown_never_means_zero(self):
        usage = normalize_usage({"prompt_tokens": 1, "completion_tokens": 1})
        for kwargs in ({"model": "made-up", "usage": usage}, {"model": "gpt-6-luna", "usage": None},
                       {"model": "gpt-6-luna", "usage": usage, "tier": "made-up"}):
            result = estimate_cost("openai", "chat.completions", **kwargs)
            self.assertFalse(result["known"])
            self.assertIsNone(result["cost_usd"])
        self.assertEqual(estimate_cost("ollama", "chat.completions", "any", None)["cost_usd"], "0")

    def test_usage_validation(self):
        self.assertIsNone(normalize_usage({"input_tokens": True, "output_tokens": 1}))
        self.assertIsNone(normalize_usage({"input_tokens": 3, "output_tokens": 1,
                                           "input_tokens_details": {"cached_tokens": 4}}))


class Cursor:
    def __init__(self, docs): self.docs = docs
    async def to_list(self, length=None): return deepcopy(self.docs)


class Collection:
    def __init__(self): self.docs = []; self.fail = False
    async def create_index(self, *args, **kwargs): pass
    def _match(self, doc, query):
        for key, expected in query.items():
            value = doc
            for part in key.split("."):
                value = value.get(part) if isinstance(value, dict) else None
            if value != expected:
                return False
        return True
    def find(self, query): return Cursor([d for d in self.docs if self._match(d, query)])
    async def find_one(self, query):
        return deepcopy(next((d for d in self.docs if self._match(d, query)), None))
    async def update_one(self, query, update, upsert=False):
        if self.fail: raise RuntimeError("Ledger offline")
        doc = next((d for d in self.docs if self._match(d, query)), None)
        if doc is None:
            if not upsert: return
            doc = deepcopy(query)
            doc.update(deepcopy(update.get("$setOnInsert", {})))
            self.docs.append(doc)
        for field, value in update.get("$set", {}).items():
            target = doc
            parts = field.split(".")
            for part in parts[:-1]: target = target.setdefault(part, {})
            target[parts[-1]] = deepcopy(value)
        for field, value in update.get("$push", {}).items():
            doc.setdefault(field, []).append(deepcopy(value))


class Database(dict):
    def __missing__(self, key): self[key] = Collection(); return self[key]


class LedgerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.db = Database()
        ledger._pending.clear()
        ledger._recording_failures.clear()
        self.env = patch.dict("os.environ", {"COST_TRACKING_ENABLED": "true"})
        self.env.start()
        await ledger.initialize_accounting(self.db)
        await ledger.begin_run("exchange", "alice", metadata={"flags": {"decisions_enabled": True}})

    async def asyncTearDown(self): self.env.stop(); ledger._db = None

    def _request(self, body, retry=0, status=200):
        client = httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(status, json=body)), event_hooks=ledger.httpx_hooks())
        try:
            return client.post("https://api.openai.com/v1/chat/completions", headers={"x-stainless-retry-count": str(retry)},
                               json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "PRIVATE MESSAGE"}]})
        finally:
            client.close()

    async def test_physical_attempts_thread_context_and_parse_failure_usage(self):
        with ledger.scope("exchange", "alice", stage="state", phase="reply", fallback=True):
            await asyncio.to_thread(self._request, {"error": {"message": "PRIVATE ERROR"}}, 0, 500)
            await asyncio.to_thread(self._request, {"model": "gpt-4o-mini", "id": "response-id",
                "usage": {"prompt_tokens": 1000, "completion_tokens": 200},
                "choices": [{"message": {"content": "MALFORMED JSON PRIVATE RESPONSE"}}]}, 1)
        await ledger.flush()
        records = self.db[ledger.ATTEMPT_COLLECTION].docs
        self.assertEqual(len(records), 2)
        self.assertEqual(sum(bool(r["known"]) for r in records), 1)
        self.assertEqual(records[1]["sdk_retry_count"], 1)
        self.assertEqual(records[1]["stage"], "state")
        self.assertNotIn("PRIVATE", json.dumps(records, default=str))
        await ledger.flush()
        self.assertEqual(len(records), 2)

    async def test_owner_and_background_attribution(self):
        with ledger.scope("exchange", "alice", stage="memory", phase="background"):
            self._request({"model": "gpt-4o-mini", "usage": {"prompt_tokens": 1000, "completion_tokens": 100}})
        await ledger.mark_phase("exchange", "reply", "completed")
        provisional = await ledger.get_cost("exchange", "alice")
        self.assertTrue(provisional["provisional"])
        self.assertIsNone(provisional["total_cost_usd"])
        self.assertEqual(provisional["background_known_cost_usd"], "0.00021")
        lookup = Mock()
        self.assertIsNone(await ledger.get_cost("exchange", "bob", rq_status_lookup=lookup))
        lookup.assert_not_called()
        await ledger.mark_phase("exchange", "background", "completed")
        result = await ledger.get_cost("exchange", "alice")
        self.assertTrue(result["accounting_complete"])
        self.assertEqual(result["total_cost_usd"], "0.00021")
        self.assertNotIn("summary", self.db[ledger.RUN_COLLECTION].docs[0])

    async def test_reconciliation_preserves_concurrent_completion_and_background_registration(self):
        async def lookup(job_id):
            await ledger.mark_phase("exchange", "reply", "completed")
            await ledger.mark_phase("exchange", "background", "running", job_id="new-background")
            return "finished"
        result = await ledger.get_cost("exchange", "alice", rq_status_lookup=lookup)
        self.assertEqual(result["phases"]["reply"]["status"], "completed")
        self.assertEqual(result["phases"]["background"]["status"], "running")
        self.assertEqual(result["phases"]["background"]["job_id"], "new-background")

    async def test_crash_and_expired_jobs_remain_incomplete(self):
        await ledger.mark_phase("exchange", "background", "pending", job_id="background-id")
        await ledger.reconcile_run("exchange", lambda job: "failed" if job == "exchange" else None)
        result = await ledger.get_cost("exchange", "alice")
        self.assertFalse(result["accounting_complete"])
        self.assertEqual(result["execution_status"], "failed")
        self.assertEqual(result["phases"]["background"]["status"], "unknown")

    async def test_crash_before_background_registration(self):
        await ledger.mark_phase("exchange", "reply", "completed")
        await ledger.reconcile_run("exchange", lambda job: "finished")
        result = await ledger.get_cost("exchange", "alice")
        self.assertEqual(result["phases"]["background"]["status"], "unknown")
        self.assertFalse(result["accounting_complete"])

    async def test_sdk_transport_retry_and_decisions_use_httpx2(self):
        import openai
        try:
            import httpx2 as sdk_httpx
        except ImportError:
            sdk_httpx = httpx
        counter = {"calls": 0}
        def handler(request):
            counter["calls"] += 1
            if request.url.path.endswith("/decisions"):
                return sdk_httpx.Response(200, json={"model": "gpt-6-luna", "answers": [
                    {"name": "gate", "type": "predicate", "probability": .99}],
                    "usage": {"input_tokens": 250, "input_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 0},
                              "output_tokens": 0, "output_tokens_details": {"reasoning_tokens": 0}, "total_tokens": 250}})
            if counter["calls"] == 1:
                return sdk_httpx.Response(500, headers={"retry-after-ms": "1"}, json={"error": {"message": "retry", "type": "server_error"}})
            return sdk_httpx.Response(200, json={"id": "test", "object": "chat.completion", "created": 1,
                "model": "gpt-4o-mini", "choices": [{"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": "malformed json"}}],
                "usage": {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120}})
        client = openai.OpenAI(api_key="test-unused", max_retries=1,
            http_client=sdk_httpx.Client(transport=sdk_httpx.MockTransport(handler), event_hooks=ledger.httpx_hooks()))
        try:
            with ledger.scope("exchange", "alice", stage="reply"):
                response = await asyncio.to_thread(client.chat.completions.create, model="gpt-4o-mini", messages=[{"role": "user", "content": "test"}])
                with self.assertRaises(json.JSONDecodeError):
                    json.loads(response.choices[0].message.content)
            if hasattr(client, "decisions"):
                with ledger.scope("exchange", "alice", stage="state"):
                    await asyncio.to_thread(client.decisions.create, model="gpt-6-luna", input="test", questions=[{"type": "predicate", "name": "gate", "instructions": "test"}])
            await ledger.flush()
            records = self.db[ledger.ATTEMPT_COLLECTION].docs
            self.assertEqual(len(records), 3 if hasattr(client, "decisions") else 2)
            self.assertEqual(records[1]["sdk_retry_count"], 1)
            self.assertTrue(records[1]["known"])
            if hasattr(client, "decisions"):
                self.assertEqual(records[2]["endpoint"], "decisions")
                self.assertEqual(Decimal(records[2]["cost_usd"]), Decimal(".000025"))
        finally:
            client.close()

    async def test_failed_recording_never_breaks_reply_or_claims_complete(self):
        with ledger.scope("exchange", "alice", stage="reply"):
            self._request({"usage": {"prompt_tokens": 10, "completion_tokens": 10}})
        self.db[ledger.ATTEMPT_COLLECTION].fail = True
        await ledger.flush()
        self.db[ledger.ATTEMPT_COLLECTION].fail = False
        await ledger.mark_phase("exchange", "reply", "completed")
        await ledger.mark_phase("exchange", "background", "completed")
        result = await ledger.get_cost("exchange", "alice")
        self.assertEqual(result["attempt_count"], 1)
        self.assertFalse(result["accounting_complete"])
        self.assertEqual(result["recording_errors"], 1)

    async def test_transport_failure_captured_unknown(self):
        def fail(request): raise httpx.ConnectError("connection failed")
        with ledger.scope("exchange", "alice", stage="reply"):
            with httpx.Client(transport=httpx.MockTransport(fail), event_hooks=ledger.httpx_hooks()) as client:
                with self.assertRaises(httpx.ConnectError):
                    client.post("https://api.openai.com/v1/chat/completions", json={"model": "gpt-4o-mini"})
        await ledger.flush()
        result = await ledger.get_cost("exchange", "alice")
        self.assertEqual(result["unknown_attempts"], 1)


class ReportTests(unittest.TestCase):
    def test_incomplete_excluded_and_autonomy_separate_no_cost_gate(self):
        rows = [{"kind": kind, "metadata": {"variant": variant}, "accounting_complete": complete,
                 "total_cost_usd": cost if complete else None, "known_cost_usd": cost,
                 "stages": {"s": {"latency_ms": 10}}, "attempt_count": 1}
                for kind, variant, complete, cost in [("exchange", "baseline", True, ".01"),
                    ("exchange", "decisions", True, ".02"), ("exchange", "decisions", False, ".9"),
                    ("autonomy", "decisions", True, ".5")]]
        report = build_report(rows)
        self.assertEqual(report["groups"]["exchange:decisions"]["average_complete_exchange_cost_usd"], "0.02")
        self.assertEqual(report["comparisons"]["exchange"]["average_cost_delta_percent"], "100")
        self.assertEqual(report["groups"]["autonomy:decisions"]["complete_runs"], 1)


if __name__ == "__main__": unittest.main()
