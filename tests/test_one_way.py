"""Tests for OneWayANOVA logic."""

import unittest
import numpy as np
from scipy import stats

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from one_way_logic import OneWayANOVA


class TestOneWayANOVA(unittest.TestCase):

    # ── Test 1: balanced design matches scipy ──
    def test_balanced_design(self):
        data = [
            [12.5, 13.1, 11.8, 12.9, 12.2, 13.5, 12.0],
            [15.2, 16.0, 14.8, 15.5, 16.2, 15.9, 14.5],
            [18.1, 17.9, 19.2, 18.5, 17.6, 18.8, 19.0],
        ]
        anova = OneWayANOVA(data)
        results = anova.calculate()

        f_scipy, p_scipy = stats.f_oneway(*data)
        self.assertAlmostEqual(results["F"], f_scipy, places=5)
        self.assertAlmostEqual(results["p_value"], p_scipy, places=5)

    # ── Test 2: unbalanced design matches scipy ──
    def test_unbalanced_design(self):
        data = [
            [10, 12, 11, 13],
            [15, 16, 14],
            [20, 21, 19, 22, 20],
        ]
        anova = OneWayANOVA(data)
        results = anova.calculate()

        f_scipy, p_scipy = stats.f_oneway(*data)
        self.assertAlmostEqual(results["F"], f_scipy, places=5)
        self.assertAlmostEqual(results["p_value"], p_scipy, places=5)

    # ── Test 3: dictionary input ──
    def test_dict_input(self):
        data = {"Control": [1, 2, 3], "Treatment": [4, 5, 6]}
        anova = OneWayANOVA(data)
        results = anova.calculate()

        f_scipy, p_scipy = stats.f_oneway([1, 2, 3], [4, 5, 6])
        self.assertAlmostEqual(results["F"], f_scipy, places=5)
        self.assertIn("Control", results["group_names"])

    # ── Test 4: CSV export structure ──
    def test_csv_export(self):
        data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        anova = OneWayANOVA(data)
        csv = anova.to_csv_string()
        lines = csv.strip().split("\n")

        self.assertEqual(lines[0], "Source,SS,df,MS,F,p-value")
        self.assertEqual(len(lines), 4)  # header + 3 rows
        self.assertTrue(lines[1].startswith("Between Groups,"))

    # ── Test 5: custom group names ──
    def test_custom_group_names(self):
        data = [[1, 2], [3, 4], [5, 6]]
        anova = OneWayANOVA(data, group_names=["Low", "Mid", "High"])
        results = anova.calculate()
        self.assertEqual(results["group_names"], ["Low", "Mid", "High"])

    # ── Test 6: residuals sum to ~0 ──
    def test_residuals_sum_zero(self):
        data = [[10, 12, 11], [15, 16, 14], [20, 21, 19]]
        results = OneWayANOVA(data).calculate()
        self.assertAlmostEqual(np.sum(results["residuals"]), 0.0, places=10)

    # ── Test 7: too few groups rejected ──
    def test_too_few_groups(self):
        with self.assertRaises(ValueError):
            OneWayANOVA([[1, 2, 3]])


if __name__ == "__main__":
    unittest.main()
