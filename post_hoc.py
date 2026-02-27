"""
Post-hoc tests for ANOVA follow-up analysis.

Provides Tukey HSD, Bonferroni-corrected pairwise t-tests, and Scheffé
pairwise comparisons.  Each function takes a list of groups (arrays) and
their names, and returns a dict with a structured table and a formatted
summary string.
"""

import numpy as np
from scipy import stats
from itertools import combinations


# ======================================================================
# Tukey HSD
# ======================================================================
def tukey_hsd(groups, group_names):
    """
    Perform Tukey's Honestly Significant Difference test.

    Args:
        groups: list of array-like, one per group.
        group_names: list of str, same length as groups.

    Returns:
        dict with "table" (list of comparison dicts) and "summary" (str).
    """
    arrays = [np.asarray(g, dtype=float) for g in groups]
    result = stats.tukey_hsd(*arrays)

    table = []
    k = len(arrays)
    for i in range(k):
        for j in range(i + 1, k):
            pval = result.pvalue[i][j]
            diff = np.mean(arrays[i]) - np.mean(arrays[j])
            ci = result.confidence_interval(confidence_level=0.95)
            table.append({
                "group1": group_names[i],
                "group2": group_names[j],
                "mean_diff": float(diff),
                "p_value": float(pval),
                "ci_low": float(ci.low[i][j]),
                "ci_high": float(ci.high[i][j]),
                "significant": pval < 0.05,
            })

    summary = _format_posthoc_table("Tukey HSD", table)
    return {"table": table, "summary": summary}


# ======================================================================
# Bonferroni
# ======================================================================
def bonferroni(groups, group_names, alpha=0.05):
    """
    Perform pairwise t-tests with Bonferroni correction.

    Args:
        groups: list of array-like.
        group_names: list of str.
        alpha: family-wise significance level (default 0.05).

    Returns:
        dict with "table" and "summary".
    """
    arrays = [np.asarray(g, dtype=float) for g in groups]
    k = len(arrays)
    m = k * (k - 1) // 2  # number of comparisons
    corrected_alpha = alpha / m

    table = []
    for i, j in combinations(range(k), 2):
        t_stat, p_raw = stats.ttest_ind(arrays[i], arrays[j])
        p_adj = min(p_raw * m, 1.0)  # Bonferroni-adjusted p
        diff = float(np.mean(arrays[i]) - np.mean(arrays[j]))
        table.append({
            "group1": group_names[i],
            "group2": group_names[j],
            "mean_diff": diff,
            "t_stat": float(t_stat),
            "p_raw": float(p_raw),
            "p_adjusted": float(p_adj),
            "significant": p_adj < alpha,
        })

    summary = _format_bonferroni_table(table, alpha, corrected_alpha)
    return {"table": table, "summary": summary}


# ======================================================================
# Scheffé
# ======================================================================
def scheffe(groups, group_names, ms_within=None, df_within=None):
    """
    Perform Scheffé's test for pairwise comparisons.

    Args:
        groups: list of array-like.
        group_names: list of str.
        ms_within: Mean-square error from ANOVA.  If None, computed from
                   pooled within-group variance.
        df_within: Degrees of freedom for error.  If None, computed
                   automatically.

    Returns:
        dict with "table" and "summary".
    """
    arrays = [np.asarray(g, dtype=float) for g in groups]
    k = len(arrays)
    ns = [len(a) for a in arrays]
    N = sum(ns)

    if ms_within is None or df_within is None:
        # Compute pooled within-group MS
        df_within = N - k
        ss_within = sum(np.sum((a - np.mean(a)) ** 2) for a in arrays)
        ms_within = ss_within / df_within if df_within > 0 else 0.0

    table = []
    for i, j in combinations(range(k), 2):
        diff = float(np.mean(arrays[i]) - np.mean(arrays[j]))
        se = np.sqrt(ms_within * (1.0 / ns[i] + 1.0 / ns[j]))
        f_val = (diff ** 2) / ((k - 1) * ms_within * (1.0 / ns[i] + 1.0 / ns[j])) if se > 0 else 0.0
        # Scheffé critical value uses F(k-1, df_within)
        p_val = stats.f.sf(f_val, k - 1, df_within)
        table.append({
            "group1": group_names[i],
            "group2": group_names[j],
            "mean_diff": diff,
            "F_scheffe": float(f_val),
            "p_value": float(p_val),
            "significant": p_val < 0.05,
        })

    summary = _format_scheffe_table(table)
    return {"table": table, "summary": summary}


# ======================================================================
# Formatting helpers
# ======================================================================
def _format_posthoc_table(title, table):
    """Format Tukey HSD results."""
    lines = [
        f"=== {title} ===",
        f"{'Comparison':<30} | {'Mean Diff':>10} | {'p-value':>10} | "
        f"{'95% CI':>20} | {'Sig.'}",
        "-" * 88,
    ]
    for row in table:
        ci = f"[{row['ci_low']:.4f}, {row['ci_high']:.4f}]"
        sig = "Yes *" if row["significant"] else "No"
        lines.append(
            f"{row['group1']} vs {row['group2']:<20} | "
            f"{row['mean_diff']:>10.4f} | {row['p_value']:>10.4f} | "
            f"{ci:>20} | {sig}"
        )
    return "\n".join(lines)


def _format_bonferroni_table(table, alpha, corrected_alpha):
    """Format Bonferroni results."""
    lines = [
        f"=== Bonferroni Pairwise Comparisons (α={alpha}) ===",
        f"Corrected α per comparison: {corrected_alpha:.6f}",
        "",
        f"{'Comparison':<30} | {'Mean Diff':>10} | {'t':>8} | "
        f"{'p(raw)':>10} | {'p(adj)':>10} | {'Sig.'}",
        "-" * 95,
    ]
    for row in table:
        sig = "Yes *" if row["significant"] else "No"
        lines.append(
            f"{row['group1']} vs {row['group2']:<20} | "
            f"{row['mean_diff']:>10.4f} | {row['t_stat']:>8.4f} | "
            f"{row['p_raw']:>10.6f} | {row['p_adjusted']:>10.6f} | {sig}"
        )
    return "\n".join(lines)


def _format_scheffe_table(table):
    """Format Scheffé results."""
    lines = [
        "=== Scheffé Pairwise Comparisons ===",
        f"{'Comparison':<30} | {'Mean Diff':>10} | {'F(Scheffé)':>12} | "
        f"{'p-value':>10} | {'Sig.'}",
        "-" * 82,
    ]
    for row in table:
        sig = "Yes *" if row["significant"] else "No"
        lines.append(
            f"{row['group1']} vs {row['group2']:<20} | "
            f"{row['mean_diff']:>10.4f} | {row['F_scheffe']:>12.4f} | "
            f"{row['p_value']:>10.4f} | {sig}"
        )
    return "\n".join(lines)
