# ANOVA Calculator

A **One-Way ANOVA (Analysis of Variance)** calculator built with Python. It includes a core computation engine, a desktop GUI built with PySide6, and unit tests validated against SciPy.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [GUI Application](#gui-application)
  - [Programmatic Usage](#programmatic-usage)
- [Running Tests](#running-tests)
- [ANOVA Theory](#anova-theory)
- [API Reference](#api-reference)

---

## Overview

This project performs **One-Way ANOVA** — a statistical test used to determine whether there are statistically significant differences between the means of three or more independent groups. It computes:

- **Sum of Squares** (Between, Within, Total)
- **Degrees of Freedom**
- **Mean Squares**
- **F-statistic**
- **p-value**

## Features

- 🖥️ **Desktop GUI** — Spreadsheet-style data entry with PySide6
- 🧮 **Core Logic** — Clean, reusable `ANOVA` class for programmatic use
- ✅ **Tested** — Unit tests validated against SciPy's `f_oneway`
- 📊 **Flexible Input** — Accepts lists, dictionaries, numpy arrays, and unbalanced group sizes
- 📋 **Formatted Output** — ANOVA summary table printed in a human-readable format

## Project Structure

```
Projects_python/
├── anova_logic.py         # Core ANOVA computation class
├── anova_gui.py           # PySide6 desktop GUI application
├── test_anova_logic.py    # Unit tests (unittest + scipy validation)
├── anova.ipynb            # Exploratory Jupyter notebook (prototyping)
└── README.md              # This file
```

| File                  | Description                                                                                 |
| --------------------- | ------------------------------------------------------------------------------------------- |
| `anova_logic.py`      | Contains the `ANOVA` class with `calculate()` method and summary formatting                 |
| `anova_gui.py`        | PySide6-based GUI with spreadsheet input, dynamic group/row management, and results display |
| `test_anova_logic.py` | Tests for balanced designs, unbalanced designs, and multiple input formats                  |
| `anova.ipynb`         | Initial exploratory notebook used during prototyping                                        |

## Requirements

- **Python** 3.8+
- **NumPy**
- **SciPy**
- **PySide6** (for the GUI only)

## Installation

1. **Clone or download** this project.

2. **Install dependencies:**

   ```bash
   pip install numpy scipy PySide6
   ```

## Usage

### GUI Application

Launch the desktop calculator:

```bash
python anova_gui.py
```

**How to use the GUI:**

1. Enter numeric data in the spreadsheet — each **column** represents a group.
2. Use **"Add Group (Column)"** / **"Remove Group"** to adjust the number of groups.
3. Use **"Add Row"** to add more data points.
4. Click **"Calculate ANOVA"** to see the results in the panel below.

### Programmatic Usage

Use the `ANOVA` class directly in your Python code:

```python
from anova_logic import ANOVA

# Option 1: List of lists
data = [
    [12.5, 13.1, 11.8, 12.9, 12.2, 13.5, 12.0],
    [15.2, 16.0, 14.8, 15.5, 16.2, 15.9, 14.5],
    [18.1, 17.9, 19.2, 18.5, 17.6, 18.8, 19.0]
]

anova = ANOVA(data)
results = anova.calculate()
print(results['summary'])
```

```python
# Option 2: Dictionary of groups
data = {
    "Control": [10, 12, 11, 13],
    "Treatment A": [15, 16, 14],
    "Treatment B": [20, 21, 19, 22, 20]
}

anova = ANOVA(data)
results = anova.calculate()
print(results['F'])       # F-statistic
print(results['p_value']) # p-value
```

**Sample output:**

```
Source          | SS         | df    | MS         | F        | p-value
----------------------------------------------------------------------
Between Groups | 151.87     | 2     | 75.94      | 218.29   | 0.0000
Within Groups  | 6.26       | 18    | 0.35       | -        | -
Total          | 158.13     | 20    | -          | -        | -
```

## Running Tests

```bash
python -m unittest test_anova_logic.py -v
```

The tests validate that the custom ANOVA implementation produces results matching SciPy's `scipy.stats.f_oneway` for:

- **Balanced designs** — equal group sizes
- **Unbalanced designs** — different group sizes
- **Multiple input formats** — dictionary input

## ANOVA Theory

One-Way ANOVA tests the null hypothesis:

> **H₀:** μ₁ = μ₂ = ... = μₖ (all group means are equal)

Against the alternative:

> **H₁:** At least one group mean is different

### Key Formulas

| Statistic   | Formula                 |
| ----------- | ----------------------- |
| SS Between  | Σ nᵢ(x̄ᵢ − x̄)²           |
| SS Within   | ΣΣ (xᵢⱼ − x̄ᵢ)²          |
| SS Total    | ΣΣ (xᵢⱼ − x̄)²           |
| df Between  | k − 1                   |
| df Within   | N − k                   |
| MS Between  | SS Between / df Between |
| MS Within   | SS Within / df Within   |
| F-statistic | MS Between / MS Within  |

Where _k_ = number of groups, _N_ = total observations, _x̄_ = grand mean.

A **small p-value** (typically < 0.05) indicates statistically significant differences between group means.

## API Reference

### `ANOVA(data)`

**Constructor.**

| Parameter | Type                               | Description                                                                                   |
| --------- | ---------------------------------- | --------------------------------------------------------------------------------------------- |
| `data`    | `list[list]`, `dict`, `np.ndarray` | Groups of samples. Lists/arrays are treated as separate groups; dict keys become group names. |

### `ANOVA.calculate() → dict`

Performs the one-way ANOVA and returns a dictionary:

| Key       | Type    | Description                                       |
| --------- | ------- | ------------------------------------------------- |
| `SS`      | `dict`  | Sum of Squares — `between`, `within`, `total`     |
| `df`      | `dict`  | Degrees of Freedom — `between`, `within`, `total` |
| `MS`      | `dict`  | Mean Squares — `between`, `within`                |
| `F`       | `float` | F-statistic                                       |
| `p_value` | `float` | p-value from the F-distribution                   |
| `summary` | `str`   | Formatted ANOVA table as a string                 |

---

_Built with Python, NumPy, SciPy, and PySide6._
