import unittest

from context_budgeter.core import optimize


class OptimizerTests(unittest.TestCase):
    def test_suppresses_lower_priority_near_duplicate(self):
        chunks = [
            {"id": "a", "text": "allow tool search production", "priority": 10},
            {"id": "b", "text": "allow tool search production", "priority": 1},
        ]
        result = optimize(chunks, 100)
        self.assertEqual([x["id"] for x in result["selected"]], ["a"])
        self.assertEqual(result["dropped"][0]["reason"], "near-duplicate")

    def test_dependency_is_selected_before_dependent_chunk(self):
        chunks = [
            {"id": "policy", "text": "must not deploy", "priority": 1},
            {"id": "task", "text": "analyze release", "priority": 10, "requires": ["policy"]},
        ]
        selected = [x["id"] for x in optimize(chunks, 100)["selected"]]
        self.assertEqual(selected, ["policy", "task"])

    def test_dependency_cycle_is_rejected(self):
        chunks = [
            {"id": "a", "text": "alpha", "requires": ["b"]},
            {"id": "b", "text": "beta", "requires": ["a"]},
        ]
        with self.assertRaisesRegex(ValueError, "dependency cycle"):
            optimize(chunks, 100)


if __name__ == "__main__":
    unittest.main()
