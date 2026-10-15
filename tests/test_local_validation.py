import unittest

from scripts.local_validation import fixture_decisions, fixture_provider, fixture_value, validate_services


class LocalValidationTests(unittest.TestCase):
    def test_only_isolated_loopback_services_allowed(self):
        validate_services("mongodb://127.0.0.1:27028", "redis://127.0.0.1:16379/15", "syntheticsoul_replay_test")
        for mongo, redis, database in [
            ("mongodb://production:27028", "redis://127.0.0.1:16379/15", "syntheticsoul_replay_test"),
            ("mongodb://127.0.0.1:27017", "redis://127.0.0.1:16379/15", "syntheticsoul_replay_test"),
            ("mongodb://127.0.0.1:27028", "redis://127.0.0.1:16379/0", "syntheticsoul_replay_test"),
            ("mongodb://127.0.0.1:27028", "redis://127.0.0.1:16379/15", "production"),
            ("mongodb://secret@127.0.0.1:27028", "redis://127.0.0.1:16379/15", "syntheticsoul_replay_test"),
        ]:
            with self.subTest(mongo=mongo, redis=redis, database=database), self.assertRaises(ValueError):
                validate_services(mongo, redis, database)

    def test_fixture_choice_probabilities_form_complete_distribution(self):
        questions = [{"name": "emotion_joy", "type": "choice", "choices": [{"value": str(i)} for i in range(-7, 8)]},
                     {"name": "contextual_thought", "type": "predicate"},
                     {"name": "impact", "type": "score", "levels": [{"label": "low"}, {"label": "high"}]}]
        answers = fixture_decisions(questions)
        self.assertEqual(answers[0]["choice"], "7")
        self.assertEqual(sum(p["probability"] for p in answers[0]["probabilities"]), 1)
        self.assertEqual(len(answers[0]["probabilities"]), 15)
        self.assertEqual(answers[1]["probability"], .01)
        self.assertEqual(answers[2]["score"], 0)

    def test_fixture_generates_legacy_and_fixed_key_state_shapes(self):
        loose = {"type": "object", "properties": {"emotion_deltas": {"type": "object", "properties": {
            "deltas": {"type": "object", "additionalProperties": {"type": "number"}}, "confidence": {"type": "number"}}}}}
        payload = fixture_value(loose)
        self.assertEqual(payload["emotion_deltas"], {"deltas": {"joy": 7}, "confidence": .7})
        fixed = {"type": "object", "properties": {"deltas": {"type": "object", "properties": {"joy": {"type": "integer"}}}}}
        self.assertEqual(fixture_value(fixed)["deltas"]["joy"], 7)

    def test_real_sdk_parses_http_fixture_both_endpoints(self):
        import json
        import openai
        with fixture_provider() as url, openai.OpenAI(api_key="fixture-no-secret", base_url=url, max_retries=0) as client:
            response = client.decisions.with_raw_response.create(model="gpt-6-luna", input="Synthetic evidence", questions=[
                {"name": "participation", "type": "choice", "instructions": "Choose participation", "choices": [{"value": "respond"}, {"value": "ignore"}]}])
            self.assertEqual(json.loads(response.content)["answers"][0]["choice"], "respond")
            response = client.beta.chat.completions.parse(model="gpt-4o-mini", messages=[{"role": "user", "content": "Synthetic evidence"}],
                response_format={"type": "json_schema", "json_schema": {"name": "fixture", "schema": {"type": "object", "properties": {"thought": {"type": "string"}}}}})
            self.assertEqual(json.loads(response.choices[0].message.content), {"thought": "no"})


if __name__ == "__main__":
    unittest.main()
