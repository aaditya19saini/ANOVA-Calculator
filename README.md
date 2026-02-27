# ANOVA Calculator

A unified **ANOVA Calculator** supporting both **One-Way** and **Two-Way** analyses. Built with Python, PySide6, NumPy, SciPy, and Matplotlib.

---

## Features

- 🖥️ **Tabbed GUI** — Switch between One-Way and Two-Way ANOVA in a single app
- 🧮 **Core Engines** — Clean `OneWayANOVA` and `TwoWayANOVA` classes for programmatic use
- 🔬 **Post-Hoc Tests** — Tukey HSD, Bonferroni, and Scheffé pairwise comparisons
- 📊 **Embedded Visualizations** — Box plots, bar charts (±SE), interaction plots, and residual diagnostics (Q-Q + histogram)
- 📋 **Formatted Output** — ANOVA summary tables with significance stars (`*`, `**`, `***`)
- 💾 **CSV Export** — Save ANOVA results to CSV
- 🏷️ **Custom Names** — Name your groups/factors for readable output
- ✅ **23 Unit Tests** — Comprehensive test coverage

## Project Structure

```
ANOVA_CALC_final/
├── one_way_logic.py     # One-Way ANOVA computation class
├── two_way_logic.py     # Two-Way ANOVA computation class
├── post_hoc.py          # Tukey HSD, Bonferroni, Scheffé
├── visualizations.py    # Box plots, bar charts, interaction & residual plots
├── anova_gui.py         # Unified PySide6 tabbed GUI
├── tests/
│   ├── test_one_way.py  # 7 tests — one-way logic
│   ├── test_two_way.py  # 9 tests — two-way logic
│   └── test_post_hoc.py # 7 tests — post-hoc functions
└── README.md
```

## Requirements

- Python 3.9+
- NumPy
- SciPy
- Matplotlib
- PySide6

## Installation

```bash
pip install numpy scipy matplotlib PySide6
```

## Usage

### GUI Application

```bash
python anova_gui.py
```

**One-Way tab:** Enter data in columns (one per group). Configure group count, names, and rows. Click Calculate → Run Post-Hoc → Visualize.

**Two-Way tab:** Set factor names, levels, and replicates. Generate the table, fill data, then Calculate → Run Post-Hoc → Visualize.

Both tabs support **Reset** and **Save Results (CSV)**.

### Programmatic Usage

```python
from one_way_logic import OneWayANOVA

data = [[12.5, 13.1, 11.8], [15.2, 16.0, 14.8], [18.1, 17.9, 19.2]]
anova = OneWayANOVA(data, group_names=["Low", "Medium", "High"])
results = anova.calculate()
print(results["summary"])
```

```python
from two_way_logic import TwoWayANOVA

data = [
    [[12, 14, 13], [15, 16, 14]],
    [[10, 11, 12], [13, 14, 12]],
]
anova = TwoWayANOVA(data, factor_a_name="Fertilizer", factor_b_name="Watering")
results = anova.calculate()
print(results["summary"])
```

## Running Tests

```bash
python -m pytest tests/ -v
```

---

_Built with Python, NumPy, SciPy, Matplotlib, and PySide6._
