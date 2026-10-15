"""Compatible profile decisions share context without weakening revision checks."""
import copy
import json
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

from app.services import interaction_decisions as stages
from app.services.decisions import DecisionBatch
from tests.test_summary_grounding import user_doc, agent_doc


class BatchedRefreshTests(unittest.IsolatedAsyncioTestCase):
    async def refresh(self, *, revise_summary=False, revise_identity=False, conflict=False,
                      user_conflict=False, user_failure=False, features=None):
        user, agent = user_doc(), agent_doc()
        user["cognition_revision"] = agent["cognition_revision"] = 0
        stored_agent, stored_user = copy.deepcopy(agent), copy.deepcopy(user)
        evidence_seen = []

        def evaluate(evidence, questions, **kwargs):
            evidence_seen.append(copy.deepcopy(evidence))
            answers = []
            for question in questions:
                name = question["name"]
                if question["type"] == "predicate":
                    revise = revise_summary if name == "revise_summary" else revise_identity
                    # The concurrent winner no longer warrants the earlier identity revision.
                    if conflict and len(evidence_seen) > 1:
                        revise = False
                    answers.append({"name": name, "type": "predicate", "probability": .6 if revise else .4})
                else:
                    choice = "friend" if name == "relationship" else "2"
                    answers.append({"name": name, "type": "choice", "choice": choice,
                        "confidence": .01,
                        "probabilities": [{"value": item["value"], "probability": int(item["value"] == choice)}
                            for item in question["choices"]]})
            return DecisionBatch.from_response(questions, {"answers": answers})

        async def mutate(doc, collection, identity, callback):
            if collection == stages.database.USER_COLLECTION and user_failure:
                await callback(copy.deepcopy(doc))
                return SimpleNamespace(status="conflict", value=None)
            if collection == stages.database.USER_COLLECTION and user_conflict:
                await callback(copy.deepcopy(doc))
                stored_agent.update(identity="Fresh personality winner.", cognition_revision=1)
                stored_user.update(summary="A concurrent user fact.", cognition_revision=1)
                doc.update(copy.deepcopy(stored_user))
            if collection == stages.database.AGENT_COLLECTION and conflict:
                stored_agent.update(identity="The winning durable identity.", cognition_revision=1)
            if collection == stages.database.AGENT_COLLECTION:
                doc.update(copy.deepcopy(stored_agent))
            fields, value = await callback(copy.deepcopy(doc))
            doc.update(copy.deepcopy(fields))
            return SimpleNamespace(status="committed" if fields else "unchanged", value=value)

        writer = AsyncMock(return_value={"summary": "Lee completed the interview and still prefers tea.",
            "summary_supported": True, "identity": "A new durable identity.", "extrinsic_relationship": "friend"})
        evaluator = AsyncMock(side_effect=evaluate)
        with patch.object(stages, "_mutate", side_effect=mutate), \
             patch.object(stages, "_audit", AsyncMock()), \
             patch.object(stages.database, "grab_self", AsyncMock(side_effect=lambda: copy.deepcopy(stored_agent))), \
             patch.object(stages.database, "grab_user", AsyncMock(side_effect=lambda _: copy.deepcopy(stored_user))), \
             patch.object(stages.decisions, "enabled", side_effect=lambda feature=None: features is None or feature in features), \
             patch.object(stages.decisions, "evaluate", evaluator), \
             patch.object(stages, "structured_query", writer):
            await stages.refresh_user_and_identity(user, agent, [
                {"role": "system", "content": "Huge repeated prompt should never appear."},
                {"role": "user", "content": "I finished the interview."},
                {"role": "assistant", "content": "Congratulations."}], sequence=1)
        return user, agent, evaluator, writer, evidence_seen

    async def test_joint_refresh_is_one_decision_and_one_combined_writer(self):
        user, agent, evaluator, writer, evidence = await self.refresh(revise_summary=True, revise_identity=True)
        evaluator.assert_awaited_once()
        writer.assert_awaited_once()
        names = {question["name"] for question in evaluator.await_args.args[1]}
        self.assertEqual(names, {"sentiment_positive", "relationship", "revise_summary", "revise_identity"})
        self.assertEqual(evaluator.await_args.kwargs["stage"], "post_refresh")
        self.assertEqual(set(writer.await_args.args[1]["json_schema"]["schema"]["properties"]),
                         {"summary", "summary_supported", "identity"})
        # Native sentiment changes remain direct even when provider confidence is low.
        self.assertEqual(user["sentiment_status"]["sentiments"]["positive"]["value"], 52)
        self.assertEqual(agent["identity"], "A new durable identity.")
        self.assertEqual(user["last_refreshed_sequence"], 1)
        serialized = json.dumps(evidence[0])
        self.assertEqual(serialized.count("I finished the interview."), 1)
        self.assertEqual(serialized.count(user_doc()["summary"]), 1)
        self.assertNotIn("Huge repeated prompt", serialized)
        self.assertNotIn("cognition_revision", serialized)

    async def test_stable_identity_and_summary_do_not_invoke_prose(self):
        _, agent, evaluator, writer, _ = await self.refresh()
        evaluator.assert_awaited_once()
        writer.assert_not_awaited()
        self.assertEqual(agent["identity"], agent_doc()["identity"])

    async def test_identity_conflict_rechecks_only_identity_and_discards_stale_candidate(self):
        _, agent, evaluator, writer, evidence = await self.refresh(revise_identity=True, conflict=True)
        self.assertEqual(evaluator.await_count, 2)
        self.assertEqual([question["name"] for question in evaluator.await_args.args[1]], ["revise_identity"])
        writer.assert_awaited_once()
        self.assertEqual(agent["identity"], "The winning durable identity.")
        self.assertEqual(evidence[-1]["agent"]["identity"], "The winning durable identity.")

    async def test_user_conflict_refreshes_both_captured_documents(self):
        _, agent, evaluator, writer, evidence = await self.refresh(user_conflict=True)
        self.assertEqual(evaluator.await_count, 2)
        writer.assert_not_awaited()
        self.assertEqual(evidence[-1]["agent"]["identity"], "Fresh personality winner.")
        self.assertEqual(evidence[-1]["summary_facts"]["stored_summary"], "A concurrent user fact.")
        self.assertEqual(agent["identity"], "Fresh personality winner.")

    async def test_failed_user_commit_does_not_apply_candidate_identity(self):
        _, agent, _, writer, _ = await self.refresh(revise_identity=True, user_failure=True)
        writer.assert_awaited_once()
        self.assertEqual(agent["identity"], agent_doc()["identity"])

    async def test_feature_flags_leave_disabled_fields_to_one_regular_writer(self):
        _, _, evaluator, writer, _ = await self.refresh(features={"state"})
        evaluator.assert_awaited_once()
        self.assertEqual([question["name"] for question in evaluator.await_args.args[1]], ["sentiment_positive"])
        writer.assert_awaited_once()
        self.assertFalse(writer.await_args.kwargs["fallback"])


if __name__ == "__main__":
    unittest.main()
