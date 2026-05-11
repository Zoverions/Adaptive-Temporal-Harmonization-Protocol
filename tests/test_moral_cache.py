
import unittest
import math
from gca_moral import MoralCalculator, Action, EntropyClass

class TestMoralCaching(unittest.TestCase):
    def test_caching_correctness(self):
        calc = MoralCalculator()
        action1 = Action("type1", "desc1", 0.1, 0.9, 0.05, 0.5, 10, EntropyClass.REVERSIBLE)
        action2 = Action("type1", "desc1", 0.1, 0.9, 0.05, 0.5, 10, EntropyClass.REVERSIBLE)

        # They are different instances but equal
        self.assertIsNot(action1, action2)
        self.assertEqual(action1, action2)
        self.assertEqual(hash(action1), hash(action2))

        # Calculate for both
        res1 = calc.calculate_moral_vector(action1)
        res2 = calc.calculate_moral_vector(action2)

        self.assertEqual(res1, res2)

        # Verify cache info (internal check)
        self.assertEqual(calc.calculate_moral_vector.cache_info().hits, 1)

    def test_different_actions(self):
        calc = MoralCalculator()
        calc.calculate_moral_vector.cache_clear()
        action1 = Action("type1", "desc1", 0.1, 0.9, 0.05, 0.5, 10, EntropyClass.REVERSIBLE)
        action2 = Action("type2", "desc2", 0.2, 0.8, 0.1, 0.6, 20, EntropyClass.IRREVERSIBLE)

        res1 = calc.calculate_moral_vector(action1)
        res2 = calc.calculate_moral_vector(action2)

        self.assertNotEqual(res1, res2)
        self.assertEqual(calc.calculate_moral_vector.cache_info().hits, 0)
        self.assertEqual(calc.calculate_moral_vector.cache_info().misses, 2)

if __name__ == '__main__':
    unittest.main()
