"""
Visualization helpers for ANOVA results.

Every function returns a ``matplotlib.figure.Figure`` so the GUI can embed
it in a ``FigureCanvasQTAgg`` widget without calling ``plt.show()``.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")  # non-interactive backend; GUI will use Qt backend
import matplotlib.pyplot as plt
from scipy import stats


# ======================================================================
# Box Plot
# ======================================================================
def box_plot(groups, group_names, title="Box Plot by Group"):
    """
    Create a box plot for each group.

    Args:
        groups: list of array-like.
        group_names: list of str.
        title: plot title.

    Returns:
        matplotlib.figure.Figure
    """
    fig, ax = plt.subplots(figsize=(7, 4))
    bp = ax.boxplot(
        [np.asarray(g) for g in groups],
        patch_artist=True,
        labels=group_names,
    )
    colors = plt.cm.Set2(np.linspace(0, 1, len(groups)))
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)

    ax.set_title(title, fontweight="bold")
    ax.set_ylabel("Value")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


# ======================================================================
# Bar Chart with Error Bars
# ======================================================================
def bar_chart_with_error(group_means, group_se, group_names,
                         title="Group Means ± SE"):
    """
    Bar chart of group means with standard-error whiskers.

    Args:
        group_means: list of float.
        group_se: list of float (standard errors).
        group_names: list of str.
        title: plot title.

    Returns:
        matplotlib.figure.Figure
    """
    fig, ax = plt.subplots(figsize=(7, 4))
    x = np.arange(len(group_means))
    colors = plt.cm.Set2(np.linspace(0, 1, len(group_means)))

    ax.bar(x, group_means, yerr=group_se, capsize=5, color=colors, edgecolor="black")
    ax.set_xticks(x)
    ax.set_xticklabels(group_names)
    ax.set_title(title, fontweight="bold")
    ax.set_ylabel("Mean")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


# ======================================================================
# Interaction Plot  (Two-Way only)
# ======================================================================
def interaction_plot(cell_means, factor_a_names, factor_b_names,
                     factor_a_label="Factor A", factor_b_label="Factor B",
                     title="Interaction Plot"):
    """
    Line plot of cell means: one line per Factor A level, x-axis = Factor B.

    Args:
        cell_means: 2D list/array, shape (a, b).
        factor_a_names: labels for Factor A levels.
        factor_b_names: labels for Factor B levels.
        factor_a_label: axis label for legend.
        factor_b_label: axis label for x-axis.
        title: plot title.

    Returns:
        matplotlib.figure.Figure
    """
    cell_means = np.asarray(cell_means)
    fig, ax = plt.subplots(figsize=(7, 4))
    x = np.arange(cell_means.shape[1])
    markers = ["o", "s", "^", "D", "v", "p", "*", "h"]
    colors = plt.cm.tab10(np.linspace(0, 1, cell_means.shape[0]))

    for i in range(cell_means.shape[0]):
        marker = markers[i % len(markers)]
        ax.plot(x, cell_means[i], marker=marker, label=factor_a_names[i],
                color=colors[i], linewidth=2, markersize=8)

    ax.set_xticks(x)
    ax.set_xticklabels(factor_b_names)
    ax.set_xlabel(factor_b_label)
    ax.set_ylabel("Cell Mean")
    ax.set_title(title, fontweight="bold")
    ax.legend(title=factor_a_label)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


# ======================================================================
# Residual Plots (Q-Q + histogram)
# ======================================================================
def residual_plots(residuals, title_prefix="Residuals"):
    """
    Side-by-side Q-Q plot and histogram of residuals.

    Args:
        residuals: 1D array of residuals.
        title_prefix: prefix for subplot titles.

    Returns:
        matplotlib.figure.Figure
    """
    residuals = np.asarray(residuals)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    # Q-Q plot
    stats.probplot(residuals, dist="norm", plot=ax1)
    ax1.set_title(f"{title_prefix} — Q-Q Plot", fontweight="bold")
    ax1.grid(alpha=0.3)

    # Histogram
    ax2.hist(residuals, bins="auto", color="#5DA5DA", edgecolor="black", alpha=0.8)
    ax2.set_title(f"{title_prefix} — Histogram", fontweight="bold")
    ax2.set_xlabel("Residual")
    ax2.set_ylabel("Frequency")
    ax2.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    return fig
