import numpy as np
from scipy import stats


class TwoWayANOVA:
    """
    Two-Way ANOVA calculator (with replication, balanced design).

    Args:
        data: 3D structure — data[i][j] is a list of replicates for
              level i of Factor A and level j of Factor B.
              Example: [[[12,14,13], [15,16,14]],
                        [[10,11,12], [13,14,12]]]
        factor_a_name: Display name for Factor A (default "Factor A").
        factor_b_name: Display name for Factor B (default "Factor B").
    """

    def __init__(self, data, factor_a_name="Factor A", factor_b_name="Factor B"):
        self.factor_a_name = factor_a_name
        self.factor_b_name = factor_b_name

        # Convert to 3D numpy array of lists
        self.cells = []
        for i, row in enumerate(data):
            cell_row = []
            for j, cell in enumerate(row):
                cell_row.append(np.array(cell, dtype=float))
            self.cells.append(cell_row)

        self.a = len(self.cells)        # levels of Factor A
        self.b = len(self.cells[0])     # levels of Factor B

        # Validate
        self._validate()

        self.r = len(self.cells[0][0])  # replicates per cell
        self.N = self.a * self.b * self.r  # total observations

    def _validate(self):
        """Validate that the data is a balanced design with r >= 2."""
        # Check all rows have the same number of columns
        for i, row in enumerate(self.cells):
            if len(row) != self.b:
                raise ValueError(
                    f"Row {i+1} has {len(row)} columns, expected {self.b}. "
                    "All rows must have the same number of columns."
                )

        # Check all cells have the same number of replicates
        r = len(self.cells[0][0])
        if r < 2:
            raise ValueError(
                "Each cell must have at least 2 replicates to compute the error term. "
                "Without-replication mode is not supported yet."
            )
        for i in range(self.a):
            for j in range(self.b):
                if len(self.cells[i][j]) != r:
                    raise ValueError(
                        f"Cell ({i+1}, {j+1}) has {len(self.cells[i][j])} replicates, "
                        f"expected {r}. All cells must have equal replicates (balanced design)."
                    )

    def calculate(self):
        """
        Perform two-way ANOVA calculations.

        Returns:
            dict with SS, df, MS, F, p-values for Factor A, Factor B,
            Interaction, Error, and Total. Also includes a formatted summary.
        """
        # 1. Compute means
        # Grand mean
        all_values = []
        for i in range(self.a):
            for j in range(self.b):
                all_values.extend(self.cells[i][j])
        grand_mean = np.mean(all_values)

        # Row means (Factor A level means)
        row_means = []
        for i in range(self.a):
            row_vals = []
            for j in range(self.b):
                row_vals.extend(self.cells[i][j])
            row_means.append(np.mean(row_vals))

        # Column means (Factor B level means)
        col_means = []
        for j in range(self.b):
            col_vals = []
            for i in range(self.a):
                col_vals.extend(self.cells[i][j])
            col_means.append(np.mean(col_vals))

        # Cell means
        cell_means = []
        for i in range(self.a):
            row = []
            for j in range(self.b):
                row.append(np.mean(self.cells[i][j]))
            cell_means.append(row)

        # 2. Sum of Squares
        # SS_A = b * r * Σ(row_mean_i - grand_mean)^2
        ss_a = self.b * self.r * sum(
            (rm - grand_mean) ** 2 for rm in row_means
        )

        # SS_B = a * r * Σ(col_mean_j - grand_mean)^2
        ss_b = self.a * self.r * sum(
            (cm - grand_mean) ** 2 for cm in col_means
        )

        # SS_AB = r * Σ(cell_mean_ij - row_mean_i - col_mean_j + grand_mean)^2
        ss_ab = 0.0
        for i in range(self.a):
            for j in range(self.b):
                ss_ab += (cell_means[i][j] - row_means[i] - col_means[j] + grand_mean) ** 2
        ss_ab *= self.r

        # SS_Error = Σ(x_ijk - cell_mean_ij)^2
        ss_error = 0.0
        for i in range(self.a):
            for j in range(self.b):
                ss_error += np.sum((self.cells[i][j] - cell_means[i][j]) ** 2)

        # SS_Total = Σ(x_ijk - grand_mean)^2
        ss_total = sum(
            (x - grand_mean) ** 2
            for i in range(self.a)
            for j in range(self.b)
            for x in self.cells[i][j]
        )

        # 3. Degrees of Freedom
        df_a = self.a - 1
        df_b = self.b - 1
        df_ab = df_a * df_b
        df_error = self.N - self.a * self.b
        df_total = self.N - 1

        # 4. Mean Squares
        ms_a = ss_a / df_a
        ms_b = ss_b / df_b
        ms_ab = ss_ab / df_ab
        ms_error = ss_error / df_error

        # 5. F-statistics
        f_a = ms_a / ms_error
        f_b = ms_b / ms_error
        f_ab = ms_ab / ms_error

        # 6. P-values
        p_a = stats.f.sf(f_a, df_a, df_error)
        p_b = stats.f.sf(f_b, df_b, df_error)
        p_ab = stats.f.sf(f_ab, df_ab, df_error)

        results = {
            "SS": {"A": ss_a, "B": ss_b, "AB": ss_ab, "error": ss_error, "total": ss_total},
            "df": {"A": df_a, "B": df_b, "AB": df_ab, "error": df_error, "total": df_total},
            "MS": {"A": ms_a, "B": ms_b, "AB": ms_ab, "error": ms_error},
            "F": {"A": f_a, "B": f_b, "AB": f_ab},
            "p_value": {"A": p_a, "B": p_b, "AB": p_ab},
            "summary": self._format_summary(
                ss_a, ss_b, ss_ab, ss_error, ss_total,
                df_a, df_b, df_ab, df_error, df_total,
                ms_a, ms_b, ms_ab, ms_error,
                f_a, f_b, f_ab,
                p_a, p_b, p_ab
            ),
        }
        return results

    def _format_summary(self, ss_a, ss_b, ss_ab, ss_e, ss_t,
                        df_a, df_b, df_ab, df_e, df_t,
                        ms_a, ms_b, ms_ab, ms_e,
                        f_a, f_b, f_ab,
                        p_a, p_b, p_ab):
        """Format the ANOVA table as a readable string."""
        w = {"src": 20, "ss": 12, "df": 5, "ms": 12, "f": 10, "p": 10}
        sep = "-" * (w["src"] + w["ss"] + w["df"] + w["ms"] + w["f"] + w["p"] + 15)

        header = (
            f"{'Source':<{w['src']}} | {'SS':<{w['ss']}} | {'df':<{w['df']}} | "
            f"{'MS':<{w['ms']}} | {'F':<{w['f']}} | {'p-value':<{w['p']}}"
        )

        def sig(p):
            if p < 0.001: return "***"
            if p < 0.01:  return "**"
            if p < 0.05:  return "*"
            return ""

        row_a = (
            f"{self.factor_a_name:<{w['src']}} | {ss_a:<{w['ss']}.4f} | {df_a:<{w['df']}} | "
            f"{ms_a:<{w['ms']}.4f} | {f_a:<{w['f']}.4f} | {p_a:<{w['p']}.6f} {sig(p_a)}"
        )
        row_b = (
            f"{self.factor_b_name:<{w['src']}} | {ss_b:<{w['ss']}.4f} | {df_b:<{w['df']}} | "
            f"{ms_b:<{w['ms']}.4f} | {f_b:<{w['f']}.4f} | {p_b:<{w['p']}.6f} {sig(p_b)}"
        )
        row_ab = (
            f"{'Interaction':<{w['src']}} | {ss_ab:<{w['ss']}.4f} | {df_ab:<{w['df']}} | "
            f"{ms_ab:<{w['ms']}.4f} | {f_ab:<{w['f']}.4f} | {p_ab:<{w['p']}.6f} {sig(p_ab)}"
        )
        row_e = (
            f"{'Error':<{w['src']}} | {ss_e:<{w['ss']}.4f} | {df_e:<{w['df']}} | "
            f"{ms_e:<{w['ms']}.4f} | {'-':<{w['f']}} | {'-':<{w['p']}}"
        )
        row_t = (
            f"{'Total':<{w['src']}} | {ss_t:<{w['ss']}.4f} | {df_t:<{w['df']}} | "
            f"{'-':<{w['ms']}} | {'-':<{w['f']}} | {'-':<{w['p']}}"
        )

        legend = "\nSignificance: * p<0.05, ** p<0.01, *** p<0.001"

        return f"{header}\n{sep}\n{row_a}\n{row_b}\n{row_ab}\n{row_e}\n{row_t}\n{legend}"

    def to_csv_string(self):
        """Return the ANOVA table as a CSV-formatted string for saving."""
        results = self.calculate()
        lines = ["Source,SS,df,MS,F,p-value"]

        ss, df, ms, f, p = results["SS"], results["df"], results["MS"], results["F"], results["p_value"]

        lines.append(f"{self.factor_a_name},{ss['A']:.6f},{df['A']},{ms['A']:.6f},{f['A']:.6f},{p['A']:.6f}")
        lines.append(f"{self.factor_b_name},{ss['B']:.6f},{df['B']},{ms['B']:.6f},{f['B']:.6f},{p['B']:.6f}")
        lines.append(f"Interaction,{ss['AB']:.6f},{df['AB']},{ms['AB']:.6f},{f['AB']:.6f},{p['AB']:.6f}")
        lines.append(f"Error,{ss['error']:.6f},{df['error']},{ms['error']:.6f},,")
        lines.append(f"Total,{ss['total']:.6f},{df['total']},,, ")

        return "\n".join(lines)


if __name__ == "__main__":
    # Quick test with sample data
    data = [
        [[12, 14, 13], [15, 16, 14], [18, 17, 19]],  # Factor A level 1
        [[10, 11, 12], [13, 14, 12], [16, 15, 17]],   # Factor A level 2
    ]
    anova = TwoWayANOVA(data, factor_a_name="Fertilizer", factor_b_name="Watering")
    results = anova.calculate()
    print(results["summary"])
