"""Regression for uncertain native participation and ignored reply prose."""
import unittest
from contextlib import ExitStack
from unittest.mock import patch

from app.constants.schemas import get_response_schema
from app.services import message_processor
from app.services.openai import _validate_structured_payload
from app.domain.models import InternalMessageRequest


class NativeReplySchemaTests(unittest.TestCase):
    def test_native_writer_excludes_diagnostic_envelopes_and_ends_with_actual_user_text(self):
        queries = [{"role": "system", "content": "Jasmine's personality and emotions"},
                   {"role": "user", "content": "Got it, thanks."},
                   {"role": "assistant", "content": "Internal perception JSON envelope"}]
        prompt = {"role": "user", "content": "Context and public reply task"}
        messages = message_processor._reply_writer_messages(queries, prompt, "Got it, thanks.", True)
        self.assertEqual(messages[0]["role"], "system")
        self.assertIn(queries[0]["content"], messages[0]["content"])
        self.assertIn("persists conversations", messages[0]["content"])
        self.assertIn("without reopening unrelated background topics", messages[0]["content"])
        self.assertEqual(messages[1:], [prompt, {"role": "user", "content": "Got it, thanks."}])
        self.assertEqual(message_processor._reply_writer_messages(queries, prompt, "Got it, thanks.", False), queries + [prompt])

    def test_native_prompt_has_no_legacy_envelope_examples_or_second_participation_task(self):
        from app.services.prompting import build_response_prompt
        values = dict(user_id="lee", username="Lee", personality="thoughtful", current_emotions="joy=23",
                      personality_language_guide="natural", latest_thought="Reflecting", recent_messages=[],
                      recent_all_messages=[], memory=[], expressions=["calm"], message="Thanks")
        accepted = build_response_prompt(**values, response_mode="accepted", include_expression=False)
        self.assertIn("Participation is already fixed", accepted)
        self.assertIn("public conversational reply only", accepted)
        self.assertIn("joy=23", accepted)
        self.assertNotIn("Examples (for shape only", accepted)
        self.assertNotIn('"response_choice":', accepted)
        self.assertNotIn("Decide whether to respond or ignore", accepted)
        self.assertNotIn("Allowed expressions", accepted)
        legacy = build_response_prompt(**values)
        self.assertIn("Examples (for shape only", legacy)
        self.assertIn('"response_choice":', legacy)

    def configure(self, features, participation=None):
        prompt = {"role": "user", "content": "Reply in character or ignore."}
        with patch.object(message_processor.decisions, "enabled", side_effect=lambda feature: feature in features):
            return message_processor._reply_writer_configuration(participation, prompt)

    def test_uncertain_native_ignore_accepts_null_without_inner_prose(self):
        for features in ({"participation"}, {"expressions"}, {"participation", "expressions"}):
            with self.subTest(features=features):
                schema, prompt = self.configure(features)
                root = schema["json_schema"]["schema"]
                self.assertTrue(schema["json_schema"]["strict"])
                self.assertEqual(root["properties"]["response"]["type"], ["object", "null"])
                self.assertEqual(set(root["required"]), set(root["properties"]))
                self.assertFalse(root["additionalProperties"])
                inner = root["properties"]["response"]
                self.assertEqual(set(inner["required"]), {"message", "purpose", "tone"})
                self.assertFalse(inner["additionalProperties"])
                ignored = {"response_choice": "ignore", "reason": "This does not need a reply.", "response": None}
                if "expressions" not in features:
                    ignored["expression"] = "neutral_listening"
                self.assertEqual(_validate_structured_payload(ignored, schema), [])
                self.assertIn("If response_choice is ignore, response must be null", prompt["content"])

    def test_uncertain_native_writer_rejects_removed_expression_and_missing_reply_fields(self):
        schema, _prompt = self.configure({"participation", "expressions"})
        responded = {"response_choice": "respond", "reason": "I want to respond.",
                     "response": {"message": "I appreciate you.", "purpose": "affection", "tone": "friendly"}}
        self.assertEqual(_validate_structured_payload(responded, schema), [])
        responded["expression"] = "invented_expression"
        self.assertTrue(any("expression" in error for error in _validate_structured_payload(responded, schema)))
        responded.pop("expression")
        responded["response"].pop("message")
        self.assertTrue(any("message" in error for error in _validate_structured_payload(responded, schema)))

    def test_accepted_response_has_prose_only_and_cannot_choose_ignore(self):
        schema, prompt = self.configure({"participation", "expressions"}, "respond")
        root = schema["json_schema"]["schema"]
        self.assertEqual(set(root["properties"]), {"response"})
        self.assertEqual(root["properties"]["response"]["type"], "object")
        self.assertTrue(_validate_structured_payload({"response": None}, schema))
        self.assertIn("Participation is fixed: respond", prompt["content"])
        self.assertIn("omit the expression field", prompt["content"])

    def test_disabled_features_preserve_baseline_schema_and_prompt(self):
        schema, prompt = self.configure(set())
        self.assertEqual(schema, get_response_schema())
        self.assertEqual(prompt, {"role": "user", "content": "Reply in character or ignore."})


class NativeIgnoredReplyTests(unittest.IsolatedAsyncioTestCase):
    async def test_uncertain_participation_ignore_does_not_create_error_reply(self):
        from tests import test_exchange
        fixture = test_exchange.ExchangeTests()
        ignored = {"response_choice": "ignore", "reason": "A reply is not needed.", "response": None}
        with ExitStack() as stack:
            agent, _user, writer, expression, storage = fixture.setup_pipeline(stack, None, ignored)
            async def validated_writer(_messages, schema, **_kwargs):
                self.assertEqual(_validate_structured_payload(ignored, schema), [])
                return ignored
            writer.side_effect = validated_writer
            result = await message_processor.generate_response(InternalMessageRequest(message="I appreciate you.", type="dm", user_id="user"))
            self.assertIsNone(result.message_response.response)
            self.assertEqual(agent.document["emotional_status"]["emotions"]["joy"]["value"], 57)
            writer.assert_awaited_once()
            self.assertTrue(writer.await_args.kwargs["fallback"])
            expression.assert_not_awaited()
            self.assertEqual(storage["insert_message_to_conversation"].await_count, 1)
            self.assertFalse(storage["insert_message_to_conversation"].await_args.args[1]["from_agent"])


if __name__ == "__main__":
    unittest.main()
