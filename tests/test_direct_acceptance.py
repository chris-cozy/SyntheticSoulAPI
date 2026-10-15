"""Valid low-certainty decisions reach pipeline actions without recovery."""
import unittest
from unittest.mock import AsyncMock, patch

from app.services import decision_tasks, decisions, interaction_decisions, thinking


def valid_batch(questions, *, probability=.6, choices=None, omit=()):
    answers = []
    for question in questions:
        name = question['name']
        if name in omit:
            continue
        kind = question['type']
        answer = {'name': name, 'type': kind}
        if kind == 'predicate':
            answer['probability'] = probability
        elif kind == 'choice':
            answer.update(choice=(choices or {}).get(name, question['choices'][0]['value']), confidence=0,
                          probabilities=[{'value': c['value'], 'probability': 1 / len(question['choices'])}
                                         for c in question['choices']])
        else:
            answer.update(score=0, confidence=0, probabilities=[
                {'value': i, 'label': level['label'], 'probability': float(i == 0)}
                for i, level in enumerate(question['levels'])])
        answers.append(answer)
    return decisions.DecisionBatch.from_response(questions, {'answers': answers})


class DirectAcceptanceTests(unittest.IsolatedAsyncioTestCase):
    async def test_memory_middle_probability_writes_or_declines_without_recovery(self):
        for probability in (.4, .5, .6):
            async def evaluate(_evidence, questions, **_kwargs):
                return valid_batch(questions, probability=probability, choices={'significance': 'high'})
            with self.subTest(probability=probability), \
                 patch.object(decision_tasks, 'enabled', return_value=True), \
                 patch.object(decision_tasks.decisions, 'evaluate', AsyncMock(side_effect=evaluate)), \
                 patch.object(decision_tasks, 'structured_query', AsyncMock(return_value={
                     'event': 'Lee completed the interview.', 'thoughts': 'I am glad.', 'tags': []})) as writer:
                result = await decision_tasks.create_memory({}, [])
                if probability > .5:
                    writer.assert_awaited_once()
                    self.assertFalse(writer.await_args.kwargs['fallback'])
                    self.assertEqual(result['significance'], 'high')
                    self.assertTrue(all(v['value'] == 0 for v in result['emotional_impact'].values()))
                    properties = writer.await_args.args[1]['json_schema']['schema']['properties']
                    self.assertNotIn('significance', properties)
                    self.assertNotIn('emotional_impact', properties)
                else:
                    writer.assert_not_awaited()
                    self.assertIsNone(result)

    async def test_missing_memory_predicate_still_recovers_with_valid_metadata_fixed(self):
        async def evaluate(_evidence, questions, **_kwargs):
            return valid_batch(questions, choices={'significance': 'high'}, omit={'memory_worthy'})
        with patch.object(decision_tasks, 'enabled', return_value=True), \
             patch.object(decision_tasks.decisions, 'evaluate', AsyncMock(side_effect=evaluate)), \
             patch.object(decision_tasks, 'structured_query', AsyncMock(return_value={
                 'event': 'Lee completed the interview.', 'thoughts': 'I am glad.', 'tags': []})) as writer:
            result = await decision_tasks.create_memory({}, [])
        writer.assert_awaited_once()
        self.assertTrue(writer.await_args.kwargs['fallback'])
        self.assertEqual(result['significance'], 'high')

    async def test_weak_fulfilled_directive_needs_only_regular_thought_prose(self):
        async def evaluate(_evidence, questions, **_kwargs):
            return valid_batch(questions, choices={'purpose': 'follow_up', 'tone': 'friendly', 'directive': 'fulfilled'})
        with patch.object(decisions, 'evaluate', AsyncMock(side_effect=evaluate)), \
             patch.object(interaction_decisions, 'structured_query', AsyncMock(return_value={
                 'thought': 'Lee completed the interview.'})) as writer:
            result = await interaction_decisions.perceive({}, {}, 'I finished the interview.', [], [],
                                                         '2026-10-11', [], {'role': 'user', 'content': 'Perceive.'})
        self.assertEqual(result['directive'], 'fulfilled')
        self.assertEqual(result['purpose'], 'follow_up')
        writer.assert_awaited_once()
        self.assertEqual(writer.await_args.kwargs['stage'], 'perception_writer')
        self.assertFalse(writer.await_args.kwargs['fallback'])
        self.assertEqual(set(writer.await_args.args[1]['json_schema']['schema']['properties']), {'thought'})

    async def test_weak_keep_or_suppress_outreach_action_does_not_rewrite(self):
        message = {'user_id': 'alex', 'message': 'How did the thesis go?', 'purpose': 'follow_up', 'tone': 'friendly'}
        for action in ('keep', 'suppress'):
            async def evaluate(_evidence, questions, **_kwargs):
                return valid_batch(questions, choices={'outreach_action': action})
            with self.subTest(action=action), \
                 patch.object(thinking.decision_tasks, 'enabled', return_value=True), \
                 patch.object(decisions, 'evaluate', AsyncMock(side_effect=evaluate)), \
                 patch.object(thinking, 'grab_self', AsyncMock(return_value={})), \
                 patch.object(thinking, 'grab_user', AsyncMock(return_value={'user_id': 'alex'})), \
                 patch.object(thinking, 'get_conversation', AsyncMock(return_value={'messages': []})), \
                 patch.object(thinking, 'structured_query', AsyncMock()) as writer, \
                 patch.object(thinking, 'insert_message_to_conversation', AsyncMock()) as persist, \
                 patch.object(thinking, 'insert_message_to_message_memory', AsyncMock()):
                sent = await thinking.handle_initiating_messages([message])
                writer.assert_not_awaited()
                if action == 'keep':
                    self.assertEqual(sent, [message])
                    persist.assert_awaited_once()
                else:
                    self.assertEqual(sent, [])
                    persist.assert_not_awaited()
