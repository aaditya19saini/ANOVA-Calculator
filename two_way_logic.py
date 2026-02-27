import numpy as np
from scipy import stats


class TwoWayANOVA:
    """
    Two-Way ANOVA calculator (with replication, balanced design).

    Args:
        data: 3D structure — data[i][j] is a list of replicates for
              level i of Factor A and level j of Factor B.
        factor_a_name: Display name for Factor A (row factor).
        factor_b_name: Display name for Factor B (column factor).
    """

    def __init__(self, data, factor_a_name="Factor A", factor_b_name="Factor B"):
        self.data = data
        self.factor_a_name = factor_a_name
        self.factor_b_name = factor_b_name

        self.a = len(data)                # levels of Factor A
        self.b = len(data[0])             # levels of Factor B
        self.r = len(data[0][0])          # replicates per cell
        self.N = self.a * self.b * self.r  # total observations

        self._validate()

   
    def _validate(self):
        """Validate that the data is a balanced design with r >= 2."""
        if self.a < 2:
            raise ValueError("Factor A must have at least 2 levels.")
        if self.b < 2:
            raise ValueError("Factor B must have at least 2 levels.")
        if self.r < 2:
            raise ValueError(
                "Two-way ANOVA with replication requires at least 2 replicates "
                "per cell."
            )
        for i in range(self.a):
            if len(self.data[i]) != self.b:
                raise ValueError(
                    f"Row {i} has {len(self.data[i])} columns, expected {self.b}. "
                    "Design must be balanced."
                )
            for j in range(self.b):
                if len(self.data[i][j]) != self.r:
                    raise ValueError(
                        f"Cell ({i},{j}) has {len(self.data[i][j])} replicates, "
                        f"expected {self.r}. All cells must have equal replicates."
                    )

    
    def calculate(self):
        """
        Perform two-way ANOVA calculations.

        Returns:
            dict with SS, df, MS, F, p-values for Factor A, Factor B,
            Interaction, Error, and Total.  Also includes formatted summary
            and extra fields for visualizations.
        """
        a, b, r = self.a, self.b, self.r
        arr = np.array(self.data, dtype=float)  # shape (a, b, r)

        # Means
        grand_mean = arr.mean()
        row_means = arr.mean(axis=(1, 2))          # shape (a,)
        col_means = arr.mean(axis=(0, 2))           # shape (b,)
        cell_means = arr.mean(axis=2)               # shape (a, b)

        # Sum of Squares
        ss_a = b * r * np.sum((row_means - grand_mean) ** 2)
        ss_b = a * r * np.sum((col_means - grand_mean) ** 2)
        ss_ab = r * np.sum(
            (cell_means - row_means[:, None] - col_means[None, :] + grand_mean) ** 2
        )
        ss_e = np.sum((arr - cell_means[:, :, None]) ** 2)
        ss_t = np.sum((arr - grand_mean) ** 2)

        # Degrees of Freedom
        df_a = a - 1
        df_b = b - 1
        df_ab = (a - 1) * (b - 1)
        df_e = a * b * (r - 1)
        df_t = self.N - 1

        # Mean Squares
        ms_a = ss_a / df_a
        ms_b = ss_b / df_b
        ms_ab = ss_ab / df_ab
        ms_e = ss_e / df_e if df_e > 0 else 0.0

        # F-statistics
        f_a = ms_a / ms_e if ms_e > 0 else float("inf")
        f_b = ms_b / ms_e if ms_e > 0 else float("inf")
        f_ab = ms_ab / ms_e if ms_e > 0 else float("inf")

        # p-values
        p_a = stats.f.sf(f_a, df_a, df_e)
        p_b = stats.f.sf(f_b, df_b, df_e)
        p_ab = stats.f.sf(f_ab, df_ab, df_e)

        # Residuals
        residuals = (arr - cell_means[:, :, None]).flatten()

        # Groups collapsed by Factor A and Factor B (for post-hoc)
        groups_by_a = [arr[i, :, :].flatten() for i in range(a)]
        groups_by_b = [arr[:, j, :].flatten() for j in range(b)]
        a_names = [f"{self.factor_a_name} {i + 1}" for i in range(a)]
        b_names = [f"{self.factor_b_name} {j + 1}" for j in range(b)]

        # Standard errors per factor level
        se_a = [np.std(g, ddof=1) / np.sqrt(len(g)) for g in groups_by_a]
        se_b = [np.std(g, ddof=1) / np.sqrt(len(g)) for g in groups_by_b]

        return {
            "SS": {"A": ss_a, "B": ss_b, "AB": ss_ab, "error": ss_e, "total": ss_t},
            "df": {"A": df_a, "B": df_b, "AB": df_ab, "error": df_e, "total": df_t},
            "MS": {"A": ms_a, "B": ms_b, "AB": ms_ab, "error": ms_e},
            "F": {"A": f_a, "B": f_b, "AB": f_ab},
            "p_value": {"A": p_a, "B": p_b, "AB": p_ab},
            "summary": self._format_summary(
                ss_a, ss_b, ss_ab, ss_e, ss_t,
                df_a, df_b, df_ab, df_e, df_t,
                ms_a, ms_b, ms_ab, ms_e,
                f_a, f_b, f_ab,
                p_a, p_b, p_ab,
            ),
            # Extra fields for visualizations / post-hoc
            "cell_means": cell_means.tolist(),
            "row_means": row_means.tolist(),
            "col_means": col_means.tolist(),
            "grand_mean": float(grand_mean),
            "residuals": residuals,
            "groups_by_a": groups_by_a,
            "groups_by_b": groups_by_b,
            "a_names": a_names,
            "b_names": b_names,
            "se_a": se_a,
            "se_b": se_b,
        }

    def to_csv_string(self):
        """Return the ANOVA table as a CSV-formatted string for saving."""
        results = self.calculate()
        ss = results["SS"]
        df = results["df"]
        ms = results["MS"]
        f = results["F"]
        p = results["p_value"]

        lines = ["Source,SS,df,MS,F,p-value"]
        lines.append(f"{self.factor_a_name},{ss['A']:.6f},{df['A']},{ms['A']:.6f},{f['A']:.6f},{p['A']:.6f}")
        lines.append(f"{self.factor_b_name},{ss['B']:.6f},{df['B']},{ms['B']:.6f},{f['B']:.6f},{p['B']:.6f}")
        lines.append(f"Interaction,{ss['AB']:.6f},{df['AB']},{ms['AB']:.6f},{f['AB']:.6f},{p['AB']:.6f}")
        lines.append(f"Error,{ss['error']:.6f},{df['error']},{ms['error']:.6f},-,-")
        lines.append(f"Total,{ss['total']:.6f},{df['total']},-,-,-")
        return "\n".join(lines)

    def _format_summary(self, ss_a, ss_b, ss_ab, ss_e, ss_t,
                        df_a, df_b, df_ab, df_e, df_t,
                        ms_a, ms_b, ms_ab, ms_e,
                        f_a, f_b, f_ab,
                        p_a, p_b, p_ab):
        """Format the ANOVA table as a readable string."""

        def sig(p):
            if p < 0.001:
                return " ***"
            elif p < 0.01:
                return " **"
            elif p < 0.05:
                return " *"
            return ""

        header = (
            f"{'Source':<20} | {'SS':<12} | {'df':<5} | "
            f"{'MS':<12} | {'F':<10} | {'p-value'}"
        )
        sep = "-" * 82

        rows = [
            f"{self.factor_a_name:<20} | {ss_a:<12.4f} | {df_a:<5} | "
            f"{ms_a:<12.4f} | {f_a:<10.4f} | {p_a:.6f}{sig(p_a)}",

            f"{self.factor_b_name:<20} | {ss_b:<12.4f} | {df_b:<5} | "
            f"{ms_b:<12.4f} | {f_b:<10.4f} | {p_b:.6f}{sig(p_b)}",

            f"{'Interaction':<20} | {ss_ab:<12.4f} | {df_ab:<5} | "
            f"{ms_ab:<12.4f} | {f_ab:<10.4f} | {p_ab:.6f}{sig(p_ab)}",

            f"{'Error':<20} | {ss_e:<12.4f} | {df_e:<5} | "
            f"{ms_e:<12.4f} | {'-':<10} | -",

            f"{'Total':<20} | {ss_t:<12.4f} | {df_t:<5} | "
            f"{'-':<12} | {'-':<10} | -",
        ]

        footer = "\nSignificance: * p<0.05, ** p<0.01, *** p<0.001"
        return f"{header}\n{sep}\n" + "\n".join(rows) + footer


if __name__ == "__main__":
    data = [
        [[12, 14, 13], [15, 16, 14], [18, 17, 19]],
        [[10, 11, 12], [13, 14, 12], [16, 15, 17]],
    ]
    anova = TwoWayANOVA(data, factor_a_name="Fertilizer", factor_b_name="Watering")
    results = anova.calculate()
    print(results["summary"])
