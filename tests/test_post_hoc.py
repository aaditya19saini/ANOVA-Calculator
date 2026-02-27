"""Tests for post-hoc analysis functions."""

import unittest
import numpy as np

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from post_hoc import tukey_hsd, bonferroni, scheffe


class TestPostHoc(unittest.TestCase):

    def setUp(self):
        # Three clearly separated groups
        self.groups = [
            np.array([10, 11, 12, 10, 11]),
            np.array([20, 21, 22, 20, 21]),
            np.array([30, 31, 32, 30, 31]),
        ]
        self.names = ["Low", "Medium", "High"]

    # ── Test 1: Tukey detects significant differences ──
    def test_tukey_significant(self):
        result = tukey_hsd(self.groups, self.names)
        self.assertIn("table", result)
        self.assertIn("summary", result)
        # All pairs should be significant
        for row in result["table"]:
            self.assertTrue(row["significant"],
                            f"{row['group1']} vs {row['group2']} should be sig.")

    # ── Test 2: Tukey on identical groups → not significant ──
    def test_tukey_not_significant(self):
        groups = [np.array([10, 11, 12]), np.array([10, 11, 12])]
        result = tukey_hsd(groups, ["A", "B"])
        self.assertFalse(result["table"][0]["significant"])

    # ── Test 3: Bonferroni adjusted p ≥ raw p ──
    def test_bonferroni_pvalues(self):
        result = bonferroni(self.groups, self.names)
        for row in result["table"]:
            self.assertGreaterEqual(row["p_adjusted"], row["p_raw"])
            self.assertLessEqual(row["p_adjusted"], 1.0)

    # ── Test 4: Bonferroni detects significant differences ──
    def test_bonferroni_significant(self):
        result = bonferroni(self.groups, self.names)
        for row in result["table"]:
            self.assertTrue(row["significant"])

    # ── Test 5: Scheffé consistent with known differences ──
    def test_scheffe_consistent(self):
        result = scheffe(self.groups, self.names)
        for row in result["table"]:
            self.assertTrue(row["significant"])
            self.assertGreater(abs(row["mean_diff"]), 0)

    # ── Test 6: Scheffé with provided MSE ──
    def test_scheffe_with_mse(self):
        ms_w = 1.0  # very small error → everything significant
        df_w = 12
        result = scheffe(self.groups, self.names,
                         ms_within=ms_w, df_within=df_w)
        for row in result["table"]:
            self.assertTrue(row["significant"])

    # ── Test 7: correct number of comparisons ──
    def test_num_comparisons(self):
        # k=3 → C(3,2) = 3 pairwise comparisons
        result = tukey_hsd(self.groups, self.names)
        self.assertEqual(len(result["table"]), 3)

        # k=4 → C(4,2) = 6
        groups4 = self.groups + [np.array([40, 41, 42, 40, 41])]
        result4 = tukey_hsd(groups4, self.names + ["Very High"])
        self.assertEqual(len(result4["table"]), 6)


if __name__ == "__main__":
    unittest.main()
