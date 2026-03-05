# 📊 ANOVA Calculator
<<<<<<< HEAD

A unified **Analysis of Variance (ANOVA)** desktop application supporting both **One-Way** and **Two-Way** analyses. Features an interactive GUI, embedded visualizations, post-hoc testing, and CSV export — all in a single app.

Built with **Python · PySide6 · NumPy · SciPy · Matplotlib**

---

## ✨ Features

=======
A unified **Analysis of Variance (ANOVA)** desktop application supporting both **One-Way** and **Two-Way** analyses. Features an interactive GUI, embedded visualizations, post-hoc testing, and CSV export — all in a single app.
Built with **Python · PySide6 · NumPy · SciPy · Matplotlib**
---
## ✨ Features
>>>>>>> 68fa5c452f8df0417375b58be9004fcc3c47a108
| Category               | Details                                                                                    |
| ---------------------- | ------------------------------------------------------------------------------------------ |
| **Tabbed GUI**         | Switch between One-Way and Two-Way ANOVA in a single window                                |
| **Core Engines**       | Clean `OneWayANOVA` and `TwoWayANOVA` classes for both GUI and programmatic use            |
| **Post-Hoc Tests**     | Tukey HSD, Bonferroni correction, and Scheffé pairwise comparisons                         |
| **Visualizations**     | Box plots, bar charts (±SE), interaction plots, and residual diagnostics (Q-Q + histogram) |
| **Formatted Output**   | ANOVA summary tables with significance stars (`*`, `**`, `***`)                            |
| **CSV Export**         | Save full ANOVA results to `.csv` files                                                    |
| **Custom Naming**      | Name your groups and factors for readable, publication-ready output                        |
| **Unbalanced Designs** | One-Way ANOVA supports groups of different sizes                                           |
| **23 Unit Tests**      | Comprehensive coverage across logic, post-hoc, and edge cases                              |
<<<<<<< HEAD

---

## 🗂️ Project Structure

=======
---
## 🗂️ Project Structure
>>>>>>> 68fa5c452f8df0417375b58be9004fcc3c47a108
```
ANOVA_CALC_final/
├── anova_gui.py          # PySide6 tabbed GUI (entry point)
├── one_way_logic.py      # One-Way ANOVA computation engine
├── two_way_logic.py      # Two-Way ANOVA computation engine (balanced, with replication)
├── post_hoc.py           # Tukey HSD, Bonferroni, Scheffé post-hoc tests
├── visualizations.py     # Matplotlib chart generators (box, bar, interaction, residual)
├── tests/
│   ├── test_one_way.py   # 7 tests — one-way logic & edge cases
│   ├── test_two_way.py   # 9 tests — two-way logic, SS/df decomposition, validation
│   └── test_post_hoc.py  # 7 tests — Tukey, Bonferroni, Scheffé correctness
└── README.md
```
<<<<<<< HEAD

---

## 📋 Requirements

=======
---
## 📋 Requirements
>>>>>>> 68fa5c452f8df0417375b58be9004fcc3c47a108
- Python 3.9+
- [NumPy](https://numpy.org/)
- [SciPy](https://scipy.org/)
- [Matplotlib](https://matplotlib.org/)
- [PySide6](https://doc.qt.io/qtforpython-6/)
<<<<<<< HEAD

### Installation

```bash
pip install numpy scipy matplotlib PySide6
```

---

## 🚀 Usage

=======
### Installation
```bash
pip install numpy scipy matplotlib PySide6
```
---
## 🚀 Usage
>>>>>>> 68fa5c452f8df0417375b58be9004fcc3c47a108
### GUI Application
```bash
python anova_gui.py
```
<<<<<<< HEAD

#### One-Way ANOVA Tab

=======
#### One-Way ANOVA Tab
>>>>>>> 68fa5c452f8df0417375b58be9004fcc3c47a108
1. Set the number of **groups** and **observations per group**
2. Optionally enter custom **group names** (comma-separated)
3. Click **Generate Table** → fill in your data
4. **Calculate** → view the ANOVA table with F-statistic and p-value
5. **Run Post-Hoc** → select Tukey HSD, Bonferroni, or Scheffé
6. **Visualize** → view box plots, bar charts with error bars, and residual diagnostics
7. **Save Results** → export to CSV
<<<<<<< HEAD

#### Two-Way ANOVA Tab

=======
#### Two-Way ANOVA Tab
>>>>>>> 68fa5c452f8df0417375b58be9004fcc3c47a108
1. Set **Factor A name**, **Factor B name**, number of levels, and replicates per cell
2. Click **Generate Table** → fill in the data grid
3. **Calculate** → view the full ANOVA table (Factor A, Factor B, Interaction, Error)
4. **Run Post-Hoc** → pairwise comparisons for each factor
5. **Visualize** → interaction plots, bar charts, box plots, and residual diagnostics
6. **Save Results** → export to CSV
<<<<<<< HEAD

Both tabs include **Reset** to clear all data and start fresh.

---

### Programmatic Usage

Use the logic classes directly in your own scripts:

#### One-Way ANOVA

```python
from one_way_logic import OneWayANOVA

=======
Both tabs include **Reset** to clear all data and start fresh.
---
### Programmatic Usage
Use the logic classes directly in your own scripts:
#### One-Way ANOVA
```python
from one_way_logic import OneWayANOVA
>>>>>>> 68fa5c452f8df0417375b58be9004fcc3c47a108
data = [
    [12.5, 13.1, 11.8, 12.9, 12.2],
    [15.2, 16.0, 14.8, 15.5, 16.2],
    [18.1, 17.9, 19.2, 18.5, 17.6],
]
anova = OneWayANOVA(data, group_names=["Low", "Medium", "High"])
results = anova.calculate()
print(results["summary"])
print(f"F = {results['F']:.4f}, p = {results['p_value']:.6f}")
```
<<<<<<< HEAD

#### Two-Way ANOVA

```python
from two_way_logic import TwoWayANOVA

=======
#### Two-Way ANOVA
```python
from two_way_logic import TwoWayANOVA
>>>>>>> 68fa5c452f8df0417375b58be9004fcc3c47a108
# data[i][j] = list of replicates for level i of Factor A, level j of Factor B
data = [
    [[12, 14, 13], [15, 16, 14], [18, 17, 19]],
    [[10, 11, 12], [13, 14, 12], [16, 15, 17]],
]
anova = TwoWayANOVA(data, factor_a_name="Fertilizer", factor_b_name="Watering")
results = anova.calculate()
print(results["summary"])
```
<<<<<<< HEAD

#### Post-Hoc Tests

```python
from post_hoc import tukey_hsd, bonferroni, scheffe

groups = [[10, 11, 12], [20, 21, 22], [30, 31, 32]]
names = ["Low", "Medium", "High"]

tukey = tukey_hsd(groups, names)
print(tukey["summary"])

bonf = bonferroni(groups, names, alpha=0.05)
print(bonf["summary"])

sch = scheffe(groups, names)
print(sch["summary"])
```

---

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
```

All 23 tests cover:

- **One-Way**: balanced/unbalanced designs, dictionary input, CSV export, residual checks, input validation
- **Two-Way**: SS & df decomposition, interaction detection, custom naming, extra visualization fields
- **Post-Hoc**: significance detection, p-value adjustment, comparison counts, Scheffé with provided MSE

---

## 📐 Statistical Methods

### One-Way ANOVA

Compares means across **k ≥ 2** independent groups. Supports balanced and unbalanced designs. Computes SS<sub>between</sub>, SS<sub>within</sub>, F-statistic, and p-value using the F-distribution.

### Two-Way ANOVA

Analyzes the effect of **two factors** (with replication) on a dependent variable. Decomposes variance into Factor A, Factor B, Interaction (A×B), and Error components. Requires a balanced design with ≥ 2 replicates per cell.

### Post-Hoc Tests

- **Tukey HSD** — simultaneous pairwise comparisons with 95% confidence intervals
- **Bonferroni** — pairwise t-tests with family-wise error rate correction
- **Scheffé** — conservative pairwise comparisons using the Scheffé F-statistic

=======
#### Post-Hoc Tests
```python
from post_hoc import tukey_hsd, bonferroni, scheffe
groups = [[10, 11, 12], [20, 21, 22], [30, 31, 32]]
names = ["Low", "Medium", "High"]
tukey = tukey_hsd(groups, names)
print(tukey["summary"])
bonf = bonferroni(groups, names, alpha=0.05)
print(bonf["summary"])
sch = scheffe(groups, names)
print(sch["summary"])
```
---
## 🧪 Running Tests
```bash
python -m pytest tests/ -v
```
All 23 tests cover:
- **One-Way**: balanced/unbalanced designs, dictionary input, CSV export, residual checks, input validation
- **Two-Way**: SS & df decomposition, interaction detection, custom naming, extra visualization fields
- **Post-Hoc**: significance detection, p-value adjustment, comparison counts, Scheffé with provided MSE
---
## 📐 Statistical Methods
### One-Way ANOVA
Compares means across **k ≥ 2** independent groups. Supports balanced and unbalanced designs. Computes SS<sub>between</sub>, SS<sub>within</sub>, F-statistic, and p-value using the F-distribution.
### Two-Way ANOVA
Analyzes the effect of **two factors** (with replication) on a dependent variable. Decomposes variance into Factor A, Factor B, Interaction (A×B), and Error components. Requires a balanced design with ≥ 2 replicates per cell.
### Post-Hoc Tests
- **Tukey HSD** — simultaneous pairwise comparisons with 95% confidence intervals
- **Bonferroni** — pairwise t-tests with family-wise error rate correction
- **Scheffé** — conservative pairwise comparisons using the Scheffé F-statistic
>>>>>>> 68fa5c452f8df0417375b58be9004fcc3c47a108
---
_Built with Python, NumPy, SciPy, Matplotlib, and PySide6._
