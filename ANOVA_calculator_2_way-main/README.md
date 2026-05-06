# Two-Way ANOVA Calculator

A **Two-Way ANOVA (Analysis of Variance)** calculator for balanced factorial designs with replication. Includes a core computation engine, a PySide6 desktop GUI, and comprehensive unit tests.

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
- [Two-Way ANOVA Theory](#two-way-anova-theory)
- [API Reference](#api-reference)

---

## Overview

Two-Way ANOVA tests for statistically significant differences across **two factors** simultaneously, plus their **interaction effect**. Given a balanced factorial design with replication, it computes:

- **SS, df, MS, F, and p-value** for Factor A (row effect)
- **SS, df, MS, F, and p-value** for Factor B (column effect)
- **SS, df, MS, F, and p-value** for the A×B Interaction
- **SS and df** for Error and Total

## Features

- 🖥️ **Desktop GUI** — Configure factors, levels, and replicates; enter data in a spreadsheet; view formatted results
- 🧮 **Core Logic** — Clean `TwoWayANOVA` class for programmatic use
- ✅ **10 Unit Tests** — Covers balanced designs, SS/df decomposition, interaction effects, edge cases, and CSV export
- 📋 **Formatted Output** — ANOVA summary table with significance stars (`*`, `**`, `***`)
- 💾 **CSV Export** — Save results to CSV from the GUI or programmatically
- 🏷️ **Custom Factor Names** — Name your factors (e.g., "Fertilizer", "Watering") for readable output

## Project Structure

```
two_way_anova/
├── two_way_logic.py     # Core TwoWayANOVA computation class
├── two_way_gui.py       # PySide6 desktop GUI application
├── test_two_way.py      # Unit tests (10 test cases)
└── README.md            # This file
```

| File               | Description                                                                                                                    |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| `two_way_logic.py` | `TwoWayANOVA` class — computes SS, df, MS, F, p-values for Factor A, Factor B, Interaction, and Error                          |
| `two_way_gui.py`   | `TwoWayAnovaApp` GUI — configurable factor names/levels/replicates, spreadsheet input, results display, CSV save               |
| `test_two_way.py`  | Tests for 2×3 and 3×2 designs, no-interaction data, strong-interaction data, SS/df decomposition, input validation, CSV export |

## Requirements

- **Python** 3.8+
- **NumPy**
- **SciPy**
- **PySide6** (for the GUI only)

## Installation

```bash
pip install numpy scipy PySide6
```

## Usage

### GUI Application

```bash
cd two_way_anova
python two_way_gui.py
```

**How to use the GUI:**

1. **Configure** — Set Factor A name, Factor B name, number of levels for each, and replicates per cell.
2. **Generate Table** — Click "Generate Table" to create the spreadsheet grid.
3. **Enter Data** — Fill in all cells. Rows are grouped by Factor A levels, columns represent Factor B levels.
4. **Calculate** — Click "Calculate ANOVA" to see the full ANOVA table with significance stars.
5. **Save** — Click "Save Results" to export the ANOVA table as a CSV file.
6. **Reset** — Click "Reset" to clear all data and start over.

### Programmatic Usage

```python
from two_way_logic import TwoWayANOVA

# Data format: data[i][j] = list of replicates
# i = Factor A level, j = Factor B level
data = [
    [[12, 14, 13], [15, 16, 14], [18, 17, 19]],  # Factor A level 1
    [[10, 11, 12], [13, 14, 12], [16, 15, 17]],   # Factor A level 2
]

anova = TwoWayANOVA(data, factor_a_name="Fertilizer", factor_b_name="Watering")
results = anova.calculate()

# Print formatted table
print(results['summary'])

# Access individual values
print(f"F(A) = {results['F']['A']:.4f}, p = {results['p_value']['A']:.6f}")
print(f"F(B) = {results['F']['B']:.4f}, p = {results['p_value']['B']:.6f}")
print(f"F(AB) = {results['F']['AB']:.4f}, p = {results['p_value']['AB']:.6f}")

# Export to CSV
csv_string = anova.to_csv_string()
with open("results.csv", "w") as f:
    f.write(csv_string)
```

**Sample output:**

```
Source               | SS           | df    | MS           | F          | p-value
------------------------------------------------------------------------------------
Fertilizer           | 10.8889      | 1     | 10.8889      | 9.8000     | 0.008547 **
Watering             | 96.3333      | 2     | 48.1667      | 43.3500    | 0.000003 ***
Interaction          | 0.1111       | 2     | 0.0556       | 0.0500     | 0.951355
Error                | 13.3333      | 12    | 1.1111       | -          | -
Total                | 120.6667     | 17    | -            | -          | -

Significance: * p<0.05, ** p<0.01, *** p<0.001
```

## Running Tests

```bash
cd two_way_anova
python -m unittest test_two_way.py -v
```

**Test coverage:**

| Test                             | What it validates                                                         |
| -------------------------------- | ------------------------------------------------------------------------- |
| `test_balanced_2x3`              | Basic 2×3 design produces correct structure, positive F-values, p ∈ [0,1] |
| `test_balanced_3x2`              | 3×2 design with correct degrees of freedom                                |
| `test_no_interaction`            | Perfectly additive data → SS_AB = 0                                       |
| `test_strong_interaction`        | Crossed effects → SS_A ≈ 0, SS_B ≈ 0, SS_AB > 0                           |
| `test_single_replicate_rejected` | r=1 raises `ValueError`                                                   |
| `test_unbalanced_rejected`       | Unequal replicates per cell raises `ValueError`                           |
| `test_ss_decomposition`          | SS_A + SS_B + SS_AB + SS_Error = SS_Total                                 |
| `test_df_decomposition`          | df_A + df_B + df_AB + df_Error = df_Total                                 |
| `test_csv_export`                | CSV output has correct header and row structure                           |
| `test_custom_names_in_summary`   | Custom factor names appear in formatted summary                           |

## Two-Way ANOVA Theory

Two-Way ANOVA tests **three null hypotheses** simultaneously:

> **H₀₁:** All levels of Factor A have equal means
> **H₀₂:** All levels of Factor B have equal means
> **H₀₃:** There is no interaction between Factor A and Factor B

### Data Layout

For _a_ levels of Factor A, _b_ levels of Factor B, and _n_ replicates per cell:

|        | B₁                    | B₂              | ... | Bⱼ              |
| ------ | --------------------- | --------------- | --- | --------------- |
| **A₁** | x₁₁₁, x₁₁₂, ..., x₁₁ₙ | x₁₂₁, ..., x₁₂ₙ | ... | x₁ⱼ₁, ..., x₁ⱼₙ |
| **A₂** | x₂₁₁, ..., x₂₁ₙ       | x₂₂₁, ..., x₂₂ₙ | ... | ...             |
| **Aᵢ** | ...                   | ...             | ... | xᵢⱼ₁, ..., xᵢⱼₙ |

### Key Formulas

| Source      | SS                           | df         | MS            | F            |
| ----------- | ---------------------------- | ---------- | ------------- | ------------ |
| Factor A    | b·n · Σ(x̄ᵢ. − x̄)²            | a − 1      | SS_A / df_A   | MS_A / MS_E  |
| Factor B    | a·n · Σ(x̄.ⱼ − x̄)²            | b − 1      | SS_B / df_B   | MS_B / MS_E  |
| Interaction | n · ΣΣ(x̄ᵢⱼ − x̄ᵢ. − x̄.ⱼ + x̄)² | (a−1)(b−1) | SS_AB / df_AB | MS_AB / MS_E |
| Error       | ΣΣΣ(xᵢⱼₖ − x̄ᵢⱼ)²             | ab(n−1)    | SS_E / df_E   | —            |
| Total       | ΣΣΣ(xᵢⱼₖ − x̄)²               | N − 1      | —             | —            |

### Interpretation

- **Small p-value** (< 0.05) → reject the null hypothesis for that source
- **Significant Factor A** → row means differ
- **Significant Factor B** → column means differ
- **Significant Interaction** → the effect of one factor depends on the level of the other

## API Reference

### `TwoWayANOVA(data, factor_a_name, factor_b_name)`

**Constructor.**

| Parameter       | Type               | Default      | Description                                                                  |
| --------------- | ------------------ | ------------ | ---------------------------------------------------------------------------- |
| `data`          | `list[list[list]]` | _(required)_ | 3D structure: `data[i][j]` = list of replicates for A level _i_, B level _j_ |
| `factor_a_name` | `str`              | `"Factor A"` | Display name for Factor A                                                    |
| `factor_b_name` | `str`              | `"Factor B"` | Display name for Factor B                                                    |

**Raises:** `ValueError` if design is unbalanced or has fewer than 2 replicates per cell.

### `TwoWayANOVA.calculate() → dict`

Performs the two-way ANOVA and returns:

| Key       | Type   | Description                                                 |
| --------- | ------ | ----------------------------------------------------------- |
| `SS`      | `dict` | Sum of Squares — keys: `A`, `B`, `AB`, `error`, `total`     |
| `df`      | `dict` | Degrees of Freedom — keys: `A`, `B`, `AB`, `error`, `total` |
| `MS`      | `dict` | Mean Squares — keys: `A`, `B`, `AB`, `error`                |
| `F`       | `dict` | F-statistics — keys: `A`, `B`, `AB`                         |
| `p_value` | `dict` | p-values — keys: `A`, `B`, `AB`                             |
| `summary` | `str`  | Formatted ANOVA table with significance stars               |

### `TwoWayANOVA.to_csv_string() → str`

Returns the ANOVA table as a CSV-formatted string. Columns: `Source,SS,df,MS,F,p-value`.

---

_Built with Python, NumPy, SciPy, and PySide6._
