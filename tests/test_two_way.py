"""Tests for TwoWayANOVA logic."""

import unittest
import numpy as np

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from two_way_logic import TwoWayANOVA


class TestTwoWayANOVA(unittest.TestCase):

    def setUp(self):
        self.data_2x3 = [
            [[12, 14, 13], [15, 16, 14], [18, 17, 19]],
            [[10, 11, 12], [13, 14, 12], [16, 15, 17]],
        ]

    # ── Test 1: balanced 2x3 structure ──
    def test_balanced_2x3(self):
        results = TwoWayANOVA(self.data_2x3).calculate()
        for key in ["SS", "df", "MS", "F", "p_value", "summary"]:
            self.assertIn(key, results)
        for src in ["A", "B", "AB"]:
            self.assertGreaterEqual(results["p_value"][src], 0)
            self.assertLessEqual(results["p_value"][src], 1)

    # ── Test 2: no interaction (additive data) ──
    def test_no_interaction(self):
        data = [
            [[10, 10, 10], [13, 13, 13], [16, 16, 16]],
            [[15, 15, 15], [18, 18, 18], [21, 21, 21]],
        ]
        results = TwoWayANOVA(data).calculate()
        self.assertAlmostEqual(results["SS"]["AB"], 0.0, places=5)

    # ── Test 3: strong interaction ──
    def test_strong_interaction(self):
        data = [
            [[10, 10, 10], [20, 20, 20]],
            [[20, 20, 20], [10, 10, 10]],
        ]
        results = TwoWayANOVA(data).calculate()
        self.assertAlmostEqual(results["SS"]["A"], 0.0, places=5)
        self.assertAlmostEqual(results["SS"]["B"], 0.0, places=5)
        self.assertGreater(results["SS"]["AB"], 0)

    # ── Test 4: SS decomposition ──
    def test_ss_decomposition(self):
        results = TwoWayANOVA(self.data_2x3).calculate()
        ss = results["SS"]
        self.assertAlmostEqual(
            ss["A"] + ss["B"] + ss["AB"] + ss["error"],
            ss["total"], places=8,
        )

    # ── Test 5: df decomposition ──
    def test_df_decomposition(self):
        results = TwoWayANOVA(self.data_2x3).calculate()
        df = results["df"]
        self.assertEqual(
            df["A"] + df["B"] + df["AB"] + df["error"],
            df["total"],
        )

    # ── Test 6: single replicate rejected ──
    def test_single_replicate_rejected(self):
        data = [[[10], [20]], [[15], [25]]]
        with self.assertRaises(ValueError) as ctx:
            TwoWayANOVA(data)
        self.assertIn("at least 2 replicates", str(ctx.exception))

    # ── Test 7: CSV export ──
    def test_csv_export(self):
        anova = TwoWayANOVA(self.data_2x3, "Fert", "Water")
        csv = anova.to_csv_string()
        lines = csv.strip().split("\n")
        self.assertEqual(lines[0], "Source,SS,df,MS,F,p-value")
        self.assertEqual(len(lines), 6)
        self.assertTrue(lines[1].startswith("Fert,"))

    # ── Test 8: custom names in summary ──
    def test_custom_names_in_summary(self):
        results = TwoWayANOVA(
            self.data_2x3, "Fertilizer", "Watering"
        ).calculate()
        self.assertIn("Fertilizer", results["summary"])
        self.assertIn("Watering", results["summary"])

    # ── Test 9: extra viz fields present ──
    def test_extra_fields(self):
        results = TwoWayANOVA(self.data_2x3).calculate()
        for key in ["cell_means", "row_means", "col_means",
                     "residuals", "groups_by_a", "groups_by_b"]:
            self.assertIn(key, results)


if __name__ == "__main__":
    unittest.main()
