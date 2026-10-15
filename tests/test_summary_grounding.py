"""Native summaries retain durable facts without absorbing subjective agent prose."""
import copy
from datetime import datetime, timezone
import json
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

from app.services import accounting, decision_tasks, interaction_decisions as stages
from app.services.decisions import DecisionBatch


def user_doc():
    return {"user_id": "lee", "username": "Lee", "agent_perspective": "jasmine",
        "summary": "Lee has an interview tomorrow, prefers tea to coffee, and values privacy about family.",
        "extrinsic_relationship": "friend", "sentiment_status": {"sentiments": {
            "positive": {"value": 50, "min": 0, "max": 100}}, "reason": None}}


def agent_doc():
    return {"name": "jasmine", "identity": "An independent bodyless individual.",
        "personality": {"personality_matrix": {}},
        "emotional_status": {"emotions": {}, "reason": None}}


class SummaryGroundingTests(unittest.IsolatedAsyncioTestCase):
    async def run_refresh(self, payload, *, revise=True, unresolved=False, event_failure=False, native=True):
        user, agent = user_doc(), agent_doc()
        queries = [{"role": "system", "content": "Agent context"},
            {"role": "user", "content": "I finished the interview! I think it went well."},
            {"role": "assistant", "content": "I feel drawn to Lee; they might be romantic and outgoing."}]

        async def mutate(doc, collection, identity, evaluate):
            fields, value = await evaluate(copy.deepcopy(doc))
            doc.update(copy.deepcopy(fields))
            return SimpleNamespace(status="committed" if fields else "unchanged", fields=fields, value=value)

        def evaluate(evidence, questions, **kwargs):
            answers = []
            for question in questions:
                name = question["name"]
                if name == "revise_summary":
                    answers.append({"name": name, "type": "predicate", "probability": .999 if revise else .001})
                elif name == "revise_identity":
                    answers.append({"name": name, "type": "predicate", "probability": .001})
                elif unresolved:
                    answers.append({"name": name, "type": "refusal"})
                else:
                    chosen = "friend" if name == "relationship" else "0"
                    answers.append({"name": name, "type": "choice", "choice": chosen, "confidence": .999,
                        "probabilities": [{"value": choice["value"], "probability": 1 if choice["value"] == chosen else 0}
                            for choice in question["choices"]]})
            return DecisionBatch.from_response(questions, {"answers": answers})

        writer = AsyncMock(return_value=payload)
        evaluator = AsyncMock(side_effect=evaluate)
        event = AsyncMock(side_effect=ConnectionError("ledger unavailable") if event_failure else None)
        with patch.object(stages, "_mutate", side_effect=mutate), \
             patch.object(stages.database, "grab_self", AsyncMock(return_value=agent)), \
             patch.object(stages, "_audit", AsyncMock()), \
             patch.object(stages.decisions, "enabled", return_value=native), \
             patch.object(stages.decisions, "evaluate", evaluator), \
             patch.object(stages, "structured_query", writer), \
             patch.object(stages, "build_post_processing_prompt") as legacy_prompt, \
             patch.object(stages, "_system_message", return_value={"role": "system", "content": "Individual"}), \
             patch.object(decision_tasks, "predicate", AsyncMock(return_value=False)), \
             patch.object(accounting, "record_event", event), \
             accounting.scope(run_id="summary-test", owner_id="lee"):
            await stages.refresh_user_and_identity(user, agent, queries)
        return user, writer, evaluator, event, legacy_prompt

    async def test_completed_interview_replaces_status_and_preserves_unrelated_facts(self):
        completed = "Lee finished the interview and believes it went well. Lee prefers tea to coffee and values privacy about family."
        user, writer, evaluator, event, legacy_prompt = await self.run_refresh(
            {"summary": completed, "summary_supported": True})
        self.assertEqual(user["summary"], completed)
        self.assertNotIn("tomorrow", user["summary"])
        self.assertIn("tea", user["summary"])
        self.assertIn("privacy", user["summary"])
        writer.assert_awaited_once()
        legacy_prompt.assert_not_called()
        evidence, questions = evaluator.await_args.args
        facts = evidence["summary_facts"]
        self.assertEqual(facts["original_user_messages"], ["I finished the interview! I think it went well."])
        self.assertNotIn("romantic", json.dumps(facts))
        self.assertIn("as_of", facts)
        instruction = next(question["instructions"] for question in questions if question["name"] == "revise_summary")
        self.assertIn("complete, cancel", instruction)
        self.assertIn("already known", instruction)
        event.assert_not_awaited()

    async def test_summary_writer_has_bounded_grounded_task_without_identity_directives(self):
        _, writer, _, _, _ = await self.run_refresh({"summary": None, "summary_supported": False})
        messages, schema = writer.await_args.args
        self.assertEqual(messages[0]["role"], "system")
        self.assertIn("For summary and summary_supported use ONLY summary_facts", messages[0]["content"])
        self.assertIn("Copy unchanged stored facts verbatim", messages[0]["content"])
        self.assertIn("assistant interpretations are not user facts", messages[0]["content"])
        self.assertIn("Do not guess dates or gender", messages[0]["content"])
        self.assertIn("invent unprovided future follow-ups", messages[0]["content"])
        properties = schema["json_schema"]["schema"]["properties"]
        self.assertEqual(set(properties), {"summary", "summary_supported"})
        self.assertEqual(properties["summary"]["maxLength"], 1800)
        self.assertIn("null", properties["summary"]["type"])
        task = messages[-1]["content"].split("\nEvidence:\n")[0]
        self.assertIn("120 words", task)
        self.assertIn("ONLY summary_facts", task)
        self.assertIn("Preserve explicit boundaries", task)
        self.assertIn("Copy unchanged stored facts verbatim", task)
        self.assertEqual(list(json.loads(messages[-1]["content"].split("\nEvidence:\n")[1]))[-1], "summary_facts")
        self.assertNotIn("Your updated identity", task)
        self.assertNotIn("Decision rule for identity", task)
        self.assertFalse(writer.await_args.kwargs["quality"])

    async def test_unchanged_summary_skips_writer_even_with_subjective_assistant_prose(self):
        stable = user_doc()
        stable["sentiment_status"]["sentiments"]["positive"]["description"] = "Positive sentiment"
        stable["sentiment_status"]["reason"] = "Decisions: positive +0."
        stable["last_interaction"] = datetime(2000, 1, 1, tzinfo=timezone.utc)
        for native in (True, False):
            with self.subTest(native=native), patch(__name__ + ".user_doc", side_effect=lambda: copy.deepcopy(stable)):
                user, writer, _, event, _ = await self.run_refresh({}, revise=False, native=native)
            self.assertEqual(user["summary"], stable["summary"])
            self.assertEqual(user["sentiment_status"], stable["sentiment_status"])
            self.assertGreater(user["last_interaction"], stable["last_interaction"])
            if native:
                writer.assert_not_awaited()
            event.assert_not_awaited()

    async def test_completed_event_instruction_replaces_status_and_spent_return_promise(self):
        _, writer, _, _, _ = await self.run_refresh({
            "summary": "Lee completed the interview and feels it went well. Lee prefers tea and values family privacy.",
            "summary_supported": True})
        task = writer.await_args.args[0][-1]["content"].split("\nEvidence:\n")[0]
        self.assertIn("chronological order", task)
        self.assertIn("newest explicit update supersedes earlier status for the same event", task)
        self.assertIn("Replace rather than append", task)
        self.assertIn("remove obsolete upcoming/preparing status", task)
        self.assertIn("earlier promise to return with results once the user reports those results", task)
        self.assertIn("Do not infer a second interview or another future follow-up", task)

    async def test_partial_state_and_relationship_share_one_grounded_summary_writer(self):
        payload = {"summary": "Lee finished the interview. Lee prefers tea and values family privacy.",
            "summary_supported": True, "extrinsic_relationship": "friend",
            "sentiment_deltas": {"deltas": {"positive": 1}, "confidence": .8, "reason": "User shared progress."}}
        user, writer, _, _, legacy_prompt = await self.run_refresh(payload, unresolved=True)
        writer.assert_awaited_once()
        properties = writer.await_args.args[1]["json_schema"]["schema"]["properties"]
        self.assertEqual(set(properties), {"summary", "summary_supported", "sentiment_deltas", "extrinsic_relationship"})
        self.assertEqual(user["summary"], payload["summary"])
        self.assertEqual(user["extrinsic_relationship"], "friend")
        legacy_prompt.assert_not_called()

    async def test_invalid_unsupported_and_repetitive_summaries_keep_prior_and_report(self):
        cases = [("unsupported", {"summary": "Lee is secretly in love with Jasmine.", "summary_supported": False}),
            ("invalid", {"summary": None, "summary_supported": True}),
            ("too_long", {"summary": "x" * 1801, "summary_supported": True}),
            ("repetitive", {"summary": "Lee values privacy about family. " * 3, "summary_supported": True})]
        for reason, payload in cases:
            with self.subTest(reason=reason):
                user, _, _, event, _ = await self.run_refresh(payload)
                self.assertEqual(user["summary"], user_doc()["summary"])
                self.assertEqual(event.await_args.args, ("summary-test", "summary_rejected_" + reason))
                self.assertNotIn("summary", event.await_args.kwargs)

    async def test_summary_decline_with_ledger_outage_does_not_fail_state_refresh(self):
        user, _, _, _, _ = await self.run_refresh({"summary": None, "summary_supported": False}, event_failure=True)
        self.assertEqual(user["summary"], user_doc()["summary"])


if __name__ == "__main__":
    unittest.main()
