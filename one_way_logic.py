import numpy as np
from scipy import stats


class OneWayANOVA:
    """
    One-Way ANOVA calculator.

    Args:
        data: Can be a list of lists, a dictionary of lists, or a numpy array.
              Represents groups of samples.  Supports unbalanced designs.
        group_names: Optional list of group names.  If data is a dict, keys
                     are used automatically.
    """

    def __init__(self, data, group_names=None):
        self.groups = []
        self._group_names = []

        # Standardize input to list of numpy arrays
        if isinstance(data, dict):
            for name, group in data.items():
                self.groups.append(np.array(group, dtype=float))
                self._group_names.append(str(name))
        elif isinstance(data, (list, tuple, np.ndarray)):
            for i, group in enumerate(data):
                self.groups.append(np.array(group, dtype=float))
                self._group_names.append(f"Group {i + 1}")
        else:
            raise ValueError(
                "Unsupported data format. Provide a list of lists, "
                "numpy array, or dictionary."
            )

        # Override auto-generated names if caller supplied them
        if group_names is not None:
            if len(group_names) != len(self.groups):
                raise ValueError(
                    f"group_names length ({len(group_names)}) must match "
                    f"number of groups ({len(self.groups)})."
                )
            self._group_names = [str(n) for n in group_names]

        if len(self.groups) < 2:
            raise ValueError("ANOVA requires at least 2 groups.")

        for i, g in enumerate(self.groups):
            if len(g) < 1:
                raise ValueError(f"Group {i + 1} is empty.")

        self.k = len(self.groups)
        self.n_total = sum(len(g) for g in self.groups)

    
    def calculate(self):
        """
        Perform one-way ANOVA calculations.

        Returns:
            dict with SS, df, MS, F, p_value, summary, group_means,
            group_names, grand_mean, and residuals.
        """
        group_means = [np.mean(g) for g in self.groups]
        grand_mean = np.sum([np.sum(g) for g in self.groups]) / self.n_total

        # Sum of Squares
        ss_between = sum(
            len(g) * (m - grand_mean) ** 2
            for g, m in zip(self.groups, group_means)
        )
        ss_within = sum(
            np.sum((g - m) ** 2)
            for g, m in zip(self.groups, group_means)
        )
        ss_total = sum(
            np.sum((g - grand_mean) ** 2) for g in self.groups
        )

        # Degrees of Freedom
        df_between = self.k - 1
        df_within = self.n_total - self.k
        df_total = self.n_total - 1

        # Mean Squares
        ms_between = ss_between / df_between
        ms_within = ss_within / df_within if df_within > 0 else 0.0

        # F-statistic & p-value
        f_stat = ms_between / ms_within if ms_within > 0 else float("inf")
        p_value = stats.f.sf(f_stat, df_between, df_within)

        # Residuals (for diagnostic plots)
        residuals = np.concatenate([
            g - m for g, m in zip(self.groups, group_means)
        ])

        # Standard errors per group
        group_se = [
            np.std(g, ddof=1) / np.sqrt(len(g)) if len(g) > 1 else 0.0
            for g in self.groups
        ]

        return {
            "SS": {"between": ss_between, "within": ss_within, "total": ss_total},
            "df": {"between": df_between, "within": df_within, "total": df_total},
            "MS": {"between": ms_between, "within": ms_within},
            "F": f_stat,
            "p_value": p_value,
            "summary": self._format_summary(
                ss_between, ss_within, ss_total,
                df_between, df_within, df_total,
                ms_between, ms_within, f_stat, p_value,
            ),
            "group_means": group_means,
            "group_se": group_se,
            "group_names": list(self._group_names),
            "grand_mean": grand_mean,
            "residuals": residuals,
        }

    def to_csv_string(self):
        """Return the ANOVA table as a CSV-formatted string."""
        results = self.calculate()
        ss = results["SS"]
        df = results["df"]
        ms = results["MS"]

        lines = ["Source,SS,df,MS,F,p-value"]
        lines.append(
            f"Between Groups,{ss['between']:.6f},{df['between']},"
            f"{ms['between']:.6f},{results['F']:.6f},{results['p_value']:.6f}"
        )
        lines.append(
            f"Within Groups,{ss['within']:.6f},{df['within']},"
            f"{ms['within']:.6f},-,-"
        )
        lines.append(
            f"Total,{ss['total']:.6f},{df['total']},-,-,-"
        )
        return "\n".join(lines)

  
    def _format_summary(self, ssb, ssw, sst, dfb, dfw, dft, msb, msw, f, p):
        """Format the ANOVA table as a readable string with significance."""

        def sig(pv):
            if pv < 0.001:
                return " ***"
            elif pv < 0.01:
                return " **"
            elif pv < 0.05:
                return " *"
            return ""

        header = (
            f"{'Source':<20} | {'SS':<12} | {'df':<5} | "
            f"{'MS':<12} | {'F':<10} | {'p-value'}"
        )
        sep = "-" * 82
        row1 = (
            f"{'Between Groups':<20} | {ssb:<12.4f} | {dfb:<5} | "
            f"{msb:<12.4f} | {f:<10.4f} | {p:.6f}{sig(p)}"
        )
        row2 = (
            f"{'Within Groups':<20} | {ssw:<12.4f} | {dfw:<5} | "
            f"{msw:<12.4f} | {'-':<10} | -"
        )
        row3 = (
            f"{'Total':<20} | {sst:<12.4f} | {dft:<5} | "
            f"{'-':<12} | {'-':<10} | -"
        )
        footer = "\nSignificance: * p<0.05, ** p<0.01, *** p<0.001"
        return f"{header}\n{sep}\n{row1}\n{row2}\n{row3}\n{footer}"


if __name__ == "__main__":
    data = [
        [12.5, 13.1, 11.8, 12.9, 12.2, 13.5, 12.0],
        [15.2, 16.0, 14.8, 15.5, 16.2, 15.9, 14.5],
        [18.1, 17.9, 19.2, 18.5, 17.6, 18.8, 19.0],
    ]
    anova = OneWayANOVA(data, group_names=["Low", "Medium", "High"])
    results = anova.calculate()
    print(results["summary"])
