import unittest
from unittest.mock import AsyncMock, patch

from app.services import accounting, openai


class FallbackContextTests(unittest.IsolatedAsyncioTestCase):
    async def test_unspecified_fallback_preserves_enclosing_stage_flag(self):
        contexts = []
        async def query(*args):
            with accounting.scope() as context:
                contexts.append(dict(context))
            return {}
        with accounting.scope("exchange", "owner", stage="expression", fallback=True), \
             patch.object(openai, "_structured_query", new=AsyncMock(side_effect=query)):
            await openai.structured_query([], {"json_schema": {"name": "expression_fallback"}})
            await openai.structured_query([], {}, fallback=False)
        self.assertTrue(contexts[0]["fallback"])
        self.assertFalse(contexts[1]["fallback"])
        self.assertEqual(contexts[0]["run_id"], "exchange")
        self.assertEqual(contexts[0]["stage"], "expression_fallback")
