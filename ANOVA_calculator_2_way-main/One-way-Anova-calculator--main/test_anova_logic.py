import unittest
import numpy as np
from scipy import stats
from anova_logic import ANOVA

class TestANOVA(unittest.TestCase):
    def test_balanced_design(self):
        # Data from the user's notebook
        data = [
            [12.5, 13.1, 11.8, 12.9, 12.2, 13.5, 12.0],
            [15.2, 16.0, 14.8, 15.5, 16.2, 15.9, 14.5],
            [18.1, 17.9, 19.2, 18.5, 17.6, 18.8, 19.0]
        ]
        anova = ANOVA(data)
        results = anova.calculate()
        
        # Scipy calculation
        f_scipy, p_scipy = stats.f_oneway(*data)
        
        self.assertAlmostEqual(results['F'], f_scipy, places=5)
        self.assertAlmostEqual(results['p_value'], p_scipy, places=5)

    def test_unbalanced_design(self):
        # Unequal group sizes
        data = [
            [10, 12, 11, 13],    # n=4
            [15, 16, 14],        # n=3
            [20, 21, 19, 22, 20] # n=5
        ]
        anova = ANOVA(data)
        results = anova.calculate()
        
        # Scipy calculation
        f_scipy, p_scipy = stats.f_oneway(*data)
        
        self.assertAlmostEqual(results['F'], f_scipy, places=5)
        self.assertAlmostEqual(results['p_value'], p_scipy, places=5)

    def test_input_formats(self):
        # Dictionary input
        data_dict = {
            "A": [1, 2, 3],
            "B": [4, 5, 6]
        }
        anova = ANOVA(data_dict)
        results = anova.calculate()
        f_scipy, p_scipy = stats.f_oneway(data_dict["A"], data_dict["B"])
        
        self.assertAlmostEqual(results['F'], f_scipy, places=5)

if __name__ == '__main__':
    unittest.main()
