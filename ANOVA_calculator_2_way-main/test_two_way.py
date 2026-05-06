import unittest
import numpy as np
from two_way_logic import TwoWayANOVA


class TestTwoWayANOVA(unittest.TestCase):
    """Comprehensive tests for the TwoWayANOVA class."""

    def setUp(self):
        """Standard 2x3 balanced dataset with r=3 replicates."""
        self.data_2x3 = [
            [[12, 14, 13], [15, 16, 14], [18, 17, 19]],  # A1
            [[10, 11, 12], [13, 14, 12], [16, 15, 17]],   # A2
        ]

    # ── Test 1: Balanced 2x3 design ──
    def test_balanced_2x3(self):
        """Verify basic 2x3 calculation produces correct structure and reasonable values."""
        anova = TwoWayANOVA(self.data_2x3)
        results = anova.calculate()

        # Check all keys exist
        for key in ["SS", "df", "MS", "F", "p_value", "summary"]:
            self.assertIn(key, results)

        # Check sub-keys
        for key in ["A", "B", "AB", "error", "total"]:
            self.assertIn(key, results["SS"])
        for key in ["A", "B", "AB"]:
            self.assertIn(key, results["F"])
            self.assertIn(key, results["p_value"])

        # F-values should be positive
        self.assertGreater(results["F"]["A"], 0)
        self.assertGreater(results["F"]["B"], 0)

        # p-values must be in [0, 1]
        for src in ["A", "B", "AB"]:
            self.assertGreaterEqual(results["p_value"][src], 0)
            self.assertLessEqual(results["p_value"][src], 1)

    # ── Test 2: Balanced 3x2 design ──
    def test_balanced_3x2(self):
        """Verify 3 levels of A, 2 levels of B, r=3."""
        data = [
            [[5, 6, 7], [10, 11, 12]],     # A1
            [[8, 9, 10], [13, 14, 15]],     # A2
            [[11, 12, 13], [16, 17, 18]],   # A3
        ]
        anova = TwoWayANOVA(data)
        results = anova.calculate()

        self.assertEqual(results["df"]["A"], 2)   # a-1
        self.assertEqual(results["df"]["B"], 1)   # b-1
        self.assertEqual(results["df"]["AB"], 2)  # (a-1)(b-1)
        self.assertEqual(results["df"]["error"], 12)  # N - a*b
        self.assertEqual(results["df"]["total"], 17)  # N - 1

    # ── Test 3: No interaction effect ──
    def test_no_interaction(self):
        """Data designed so interaction effect is zero (perfectly additive)."""
        # Additive model: cell_ij = base + A_effect_i + B_effect_j
        # A effects: [0, 5], B effects: [0, 3, 6]
        data = [
            [[10, 10, 10], [13, 13, 13], [16, 16, 16]],  # A1
            [[15, 15, 15], [18, 18, 18], [21, 21, 21]],   # A2
        ]
        anova = TwoWayANOVA(data)
        results = anova.calculate()

        # SS_AB should be 0 (no interaction)
        self.assertAlmostEqual(results["SS"]["AB"], 0.0, places=5)
        # p_AB should be 1.0 or very high (F_AB ≈ 0)
        # F_AB will be 0/0 or nan when SS_error is also 0, so handle carefully
        # Since all replicates are identical, SS_error = 0 too → F is undefined.
        # This is an edge case. Let's just verify SS_AB = 0.

    # ── Test 4: Strong interaction effect ──
    def test_strong_interaction(self):
        """Data where interaction dominates."""
        data = [
            [[10, 10, 10], [20, 20, 20]],  # A1: big difference between B1 and B2
            [[20, 20, 20], [10, 10, 10]],   # A2: reversed! B1 high, B2 low
        ]
        anova = TwoWayANOVA(data)
        results = anova.calculate()

        # Main effects should be near zero (means are balanced)
        self.assertAlmostEqual(results["SS"]["A"], 0.0, places=5)
        self.assertAlmostEqual(results["SS"]["B"], 0.0, places=5)
        # Interaction should be large
        self.assertGreater(results["SS"]["AB"], 0)

    # ── Test 5: Single replicate rejected ──
    def test_single_replicate_rejected(self):
        """r=1 should raise ValueError."""
        data = [
            [[10], [20]],
            [[15], [25]],
        ]
        with self.assertRaises(ValueError) as ctx:
            TwoWayANOVA(data)
        self.assertIn("at least 2 replicates", str(ctx.exception))

    # ── Test 6: Unbalanced design rejected ──
    def test_unbalanced_rejected(self):
        """Different number of replicates per cell should raise ValueError."""
        data = [
            [[10, 11], [20, 21, 22]],   # 2 vs 3 replicates
            [[15, 16], [25, 26, 27]],
        ]
        with self.assertRaises(ValueError) as ctx:
            TwoWayANOVA(data)
        self.assertIn("replicates", str(ctx.exception).lower())

    # ── Test 7: SS decomposition identity ──
    def test_ss_decomposition(self):
        """Verify SS_A + SS_B + SS_AB + SS_error == SS_total."""
        anova = TwoWayANOVA(self.data_2x3)
        results = anova.calculate()
        ss = results["SS"]

        ss_sum = ss["A"] + ss["B"] + ss["AB"] + ss["error"]
        self.assertAlmostEqual(ss_sum, ss["total"], places=8)

    # ── Test 8: df decomposition identity ──
    def test_df_decomposition(self):
        """Verify df_A + df_B + df_AB + df_error == df_total."""
        anova = TwoWayANOVA(self.data_2x3)
        results = anova.calculate()
        df = results["df"]

        df_sum = df["A"] + df["B"] + df["AB"] + df["error"]
        self.assertEqual(df_sum, df["total"])

    # ── Extra: CSV export ──
    def test_csv_export(self):
        """Verify CSV string has correct structure."""
        anova = TwoWayANOVA(self.data_2x3, factor_a_name="Fert", factor_b_name="Water")
        csv = anova.to_csv_string()
        lines = csv.strip().split("\n")

        self.assertEqual(lines[0], "Source,SS,df,MS,F,p-value")
        self.assertEqual(len(lines), 6)  # header + 5 rows
        self.assertTrue(lines[1].startswith("Fert,"))
        self.assertTrue(lines[2].startswith("Water,"))

    # ── Extra: Custom factor names appear in summary ──
    def test_custom_names_in_summary(self):
        """Verify custom factor names appear in the formatted summary."""
        anova = TwoWayANOVA(self.data_2x3, factor_a_name="Fertilizer", factor_b_name="Watering")
        results = anova.calculate()
        self.assertIn("Fertilizer", results["summary"])
        self.assertIn("Watering", results["summary"])


if __name__ == "__main__":
    unittest.main()
