"""Independent transport regressions: validate provider JSON before SDK coercion."""
import unittest
from unittest.mock import AsyncMock, patch

import httpx2
import openai

from app.services import accounting, decisions, openai as chat_service
from app.services.interaction_decisions import writer_schema


class ProviderTypeValidationTests(unittest.IsolatedAsyncioTestCase):
    async def evaluate_answer(self, question, answer):
        real_constructor = openai.OpenAI
        transport = httpx2.MockTransport(lambda request: httpx2.Response(200, json={
            "model": "gpt-6-luna", "answers": answer if isinstance(answer, list) else [answer], "usage": {
                "input_tokens": 100, "output_tokens": 0, "total_tokens": 100,
                "input_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 0},
                "output_tokens_details": {"reasoning_tokens": 0}}}))

        def client_factory(**kwargs):
            # Replace the transport only; execute the installed SDK's real parsing.
            kwargs["http_client"].close()
            kwargs["api_key"] = "test-unused-key"
            kwargs["http_client"] = httpx2.Client(transport=transport)
            return real_constructor(**kwargs)

        with patch.object(decisions, "enabled", return_value=True), \
             patch.object(decisions.openai, "OpenAI", side_effect=client_factory), \
             patch("app.services.accounting.flush", new=AsyncMock()):
            return await decisions.evaluate({"experience": "synthetic evidence"},
                question if isinstance(question, list) else [question], feature="state")

    async def test_provider_boolean_probability_is_unresolved(self):
        question = decisions.predicate_question("gate", "Is this experience salient?")
        batch = await self.evaluate_answer(question, {"name": "gate", "type": "predicate", "probability": True})
        self.assertIsNone(batch.predicate("gate"))

    async def test_provider_numeric_string_confidence_is_unresolved(self):
        question = decisions.choice_question("delta", "Choose a direct change.", ["0", "1"])
        batch = await self.evaluate_answer(question, {
            "name": "delta", "type": "choice", "choice": "1", "confidence": "0.99",
            "probabilities": [{"value": "0", "probability": .01}, {"value": "1", "probability": .99}]})
        self.assertIsNone(batch.choice("delta"))

    async def test_provider_numeric_probability_is_accepted(self):
        question = decisions.predicate_question("gate", "Is this experience salient?")
        batch = await self.evaluate_answer(question, {"name": "gate", "type": "predicate", "probability": .99})
        self.assertTrue(batch.predicate("gate"))

    async def test_malformed_answer_does_not_discard_valid_sibling(self):
        questions = [decisions.predicate_question("valid", "Valid?"), decisions.predicate_question("bad", "Bad?")]
        batch = await self.evaluate_answer(questions, [
            {"name": "valid", "type": "predicate", "probability": .99},
            {"name": "bad", "type": "predicate", "probability": "0.99"}])
        self.assertTrue(batch.predicate("valid"))
        self.assertIsNone(batch.predicate("bad"))


class HostedWriterTransportTests(unittest.IsolatedAsyncioTestCase):
    async def test_upgraded_sdk_parse_preserves_usage_before_length_rejection(self):
        requests = []
        def respond(request):
            import json
            requests.append(json.loads(request.content))
            return httpx2.Response(200, json={
                "id": "synthetic-completion", "object": "chat.completion", "created": 1,
                "model": "gpt-4o-mini", "choices": [{"index": 0, "finish_reason": "length",
                    "message": {"role": "assistant", "content": '{"message":"unfinished'}}],
                "usage": {"prompt_tokens": 123, "completion_tokens": 17, "total_tokens": 140}})
        client = openai.OpenAI(api_key="test-unused-key", max_retries=0,
            http_client=httpx2.Client(transport=httpx2.MockTransport(respond), event_hooks=accounting.httpx_hooks()))
        schema = writer_schema("reply_writer_test", {"message": {"type": "string"}})
        with patch.dict("os.environ", {"COST_TRACKING_ENABLED": "true"}), \
             patch.object(accounting, "_pending", {}), \
             patch.object(chat_service, "_get_client", return_value=client), \
             patch.object(chat_service, "_get_model", return_value="gpt-4o-mini"), \
             patch.object(chat_service, "LLM_MODE", "hosted"), \
             patch.object(chat_service, "flush", new=AsyncMock()), \
             accounting.scope("review-exchange", "synthetic-owner", phase="reply"):
            result = await chat_service.structured_query([{"role": "user", "content": "Synthetic request"}], schema, stage="reply_writer")
            records = list(accounting._pending.values())
            self.assertIsNone(result)
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["usage"]["input_tokens"], 123)
            self.assertEqual(records[0]["usage"]["output_tokens"], 17)
            self.assertTrue(records[0]["known"])
            self.assertEqual(requests[0]["response_format"], schema)


if __name__ == "__main__":
    unittest.main()
