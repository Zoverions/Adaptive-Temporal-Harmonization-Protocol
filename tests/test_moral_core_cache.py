
import unittest
import math
from gca_core.moral import MoralKernel, Action, EntropyClass

class TestMoralCoreCaching(unittest.TestCase):
    def test_caching_correctness(self):
        calc = MoralKernel()
        action1 = Action("type1", "desc1", 0.1, 0.9, 0.05, 0.5, 10, EntropyClass.REVERSIBLE)
        action2 = Action("type1", "desc1", 0.1, 0.9, 0.05, 0.5, 10, EntropyClass.REVERSIBLE)

        self.assertEqual(action1, action2)

        res1 = calc.calculate_moral_vector(action1)
        res2 = calc.calculate_moral_vector(action2)

        self.assertEqual(res1, res2)
        self.assertEqual(calc.calculate_moral_vector.cache_info().hits, 1)

if __name__ == '__main__':
    unittest.main()
