import random
import unittest
from app.services.prompting import build_thought_prompt, build_message_thought_prompt


class NativeThoughtPromptTests(unittest.TestCase):
    def test_expression_tasks_are_absent_from_native_inner_prose_prompt(self):
        for branch in (True, False):
            prompt = build_thought_prompt({"name": "jasmine"}, [], None, random_branch=branch,
                rng=random.Random(1), now="2026-10-11", include_expression=False)
            self.assertNotIn("new_expression", prompt)
            self.assertNotIn("expression is selected separately", prompt)
            self.assertNotIn("Possible expressions", prompt)
            self.assertIn("personal inner aside", prompt)

    def test_post_interaction_native_prompt_has_no_expression_task(self):
        prompt = build_message_thought_prompt({"name": "jasmine"}, "A previous thought", include_expression=False)
        self.assertNotIn("new_expression", prompt)
        self.assertIn("A previous thought", prompt)

    def test_baseline_keeps_existing_expression_task(self):
        prompt = build_thought_prompt({"name": "jasmine"}, [], None, rng=random.Random(1))
        self.assertIn("new_expression", prompt)
