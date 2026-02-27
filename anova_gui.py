"""
Unified ANOVA Calculator — PySide6 GUI

Tab 1: One-Way ANOVA
Tab 2: Two-Way ANOVA

Both tabs include: Calculate, Post-Hoc, Visualize, Reset, Save CSV.
"""

import sys
import os
import numpy as np

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QTabWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QTextEdit, QMessageBox, QSpinBox,
    QLineEdit, QFileDialog, QGroupBox, QScrollArea, QSplitter,
    QSizePolicy,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from one_way_logic import OneWayANOVA
from two_way_logic import TwoWayANOVA
from post_hoc import tukey_hsd, bonferroni, scheffe
from visualizations import box_plot, bar_chart_with_error, interaction_plot, residual_plots


# ======================================================================
# Shared styles
# ======================================================================
BTN_GREEN = "background-color: #4CAF50; color: white; font-weight: bold; padding: 6px 14px;"
BTN_BLUE = "background-color: #2196F3; color: white; font-weight: bold; padding: 6px 14px;"
BTN_ORANGE = "background-color: #FF9800; color: white; font-weight: bold; padding: 6px 14px;"
BTN_RED = "background-color: #f44336; color: white; font-weight: bold; padding: 6px 14px;"
BTN_GRAY = "background-color: #607D8B; color: white; font-weight: bold; padding: 6px 14px;"
MONO_FONT = "font-family: Consolas, 'Courier New', monospace; font-size: 12px;"


# ======================================================================
# One-Way Tab
# ======================================================================
class OneWayTab(QWidget):
    def __init__(self):
        super().__init__()
        self._last_results = None
        self._last_csv = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # ── Config row ──
        config_group = QGroupBox("Configuration")
        config_layout = QHBoxLayout(config_group)

        config_layout.addWidget(QLabel("Number of Groups:"))
        self.num_groups_spin = QSpinBox()
        self.num_groups_spin.setRange(2, 20)
        self.num_groups_spin.setValue(3)
        config_layout.addWidget(self.num_groups_spin)

        config_layout.addWidget(QLabel("Rows per Group:"))
        self.num_rows_spin = QSpinBox()
        self.num_rows_spin.setRange(2, 100)
        self.num_rows_spin.setValue(10)
        config_layout.addWidget(self.num_rows_spin)

        config_layout.addWidget(QLabel("Group Names (comma-separated):"))
        self.group_names_edit = QLineEdit()
        self.group_names_edit.setPlaceholderText("e.g. Control, Treatment A, Treatment B")
        config_layout.addWidget(self.group_names_edit)

        gen_btn = QPushButton("Generate Table")
        gen_btn.setStyleSheet(BTN_GRAY)
        gen_btn.clicked.connect(self.generate_table)
        config_layout.addWidget(gen_btn)

        layout.addWidget(config_group)

        # ── Data table ──
        self.table = QTableWidget(10, 3)
        self.table.setHorizontalHeaderLabels(["Group 1", "Group 2", "Group 3"])
        layout.addWidget(self.table)

        # ── Row buttons ──
        row_btn_layout = QHBoxLayout()
        add_row_btn = QPushButton("Add Row")
        add_row_btn.clicked.connect(lambda: self.table.insertRow(self.table.rowCount()))
        row_btn_layout.addWidget(add_row_btn)

        rem_row_btn = QPushButton("Remove Row")
        rem_row_btn.clicked.connect(
            lambda: self.table.removeRow(self.table.rowCount() - 1) if self.table.rowCount() > 1 else None
        )
        row_btn_layout.addWidget(rem_row_btn)
        layout.addLayout(row_btn_layout)

        # ── Action buttons ──
        action_layout = QHBoxLayout()

        calc_btn = QPushButton("Calculate ANOVA")
        calc_btn.setStyleSheet(BTN_GREEN)
        calc_btn.clicked.connect(self.calculate_anova)
        action_layout.addWidget(calc_btn)

        self.posthoc_btn = QPushButton("Run Post-Hoc")
        self.posthoc_btn.setStyleSheet(BTN_BLUE)
        self.posthoc_btn.setEnabled(False)
        self.posthoc_btn.clicked.connect(self.run_posthoc)
        action_layout.addWidget(self.posthoc_btn)

        self.viz_btn = QPushButton("Visualize")
        self.viz_btn.setStyleSheet(BTN_ORANGE)
        self.viz_btn.setEnabled(False)
        self.viz_btn.clicked.connect(self.visualize)
        action_layout.addWidget(self.viz_btn)

        save_btn = QPushButton("Save Results (CSV)")
        save_btn.setStyleSheet(BTN_GRAY)
        save_btn.clicked.connect(self.save_results)
        action_layout.addWidget(save_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.setStyleSheet(BTN_RED)
        reset_btn.clicked.connect(self.reset_all)
        action_layout.addWidget(reset_btn)

        layout.addLayout(action_layout)

        # ── Results area ──
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setPlaceholderText("Results will appear here ...")
        self.results_text.setStyleSheet(MONO_FONT)
        self.results_text.setMaximumHeight(200)
        layout.addWidget(self.results_text)

        # ── Visualization scroll area ──
        self.viz_scroll = QScrollArea()
        self.viz_scroll.setWidgetResizable(True)
        self.viz_container = QWidget()
        self.viz_layout = QVBoxLayout(self.viz_container)
        self.viz_scroll.setWidget(self.viz_container)
        self.viz_scroll.setMinimumHeight(100)
        layout.addWidget(self.viz_scroll, stretch=1)

    # ── Generate table ──
    def generate_table(self):
        n_groups = self.num_groups_spin.value()
        n_rows = self.num_rows_spin.value()
        names = self._parse_group_names(n_groups)

        self.table.setColumnCount(n_groups)
        self.table.setRowCount(n_rows)
        self.table.setHorizontalHeaderLabels(names)
        self.table.clearContents()

    # ── Extract data ──
    def _extract_data(self):
        data = []
        n_groups = self.table.columnCount()
        names = []
        for col in range(n_groups):
            group = []
            for row in range(self.table.rowCount()):
                item = self.table.item(row, col)
                if item and item.text().strip():
                    try:
                        group.append(float(item.text()))
                    except ValueError:
                        raise ValueError(
                            f"Invalid number at Row {row + 1}, "
                            f"Column {col + 1}: '{item.text()}'"
                        )
            if group:
                data.append(group)
                header = self.table.horizontalHeaderItem(col)
                names.append(header.text() if header else f"Group {col + 1}")
        return data, names

    # ── Calculate ──
    def calculate_anova(self):
        try:
            data, names = self._extract_data()
            if len(data) < 2:
                QMessageBox.warning(self, "Input Error",
                                    "Provide at least 2 groups with data.")
                return

            anova = OneWayANOVA(data, group_names=names)
            self._last_results = anova.calculate()
            self._last_csv = anova.to_csv_string()
            self.results_text.setText(self._last_results["summary"])
            self.posthoc_btn.setEnabled(True)
            self.viz_btn.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # ── Post-hoc ──
    def run_posthoc(self):
        if not self._last_results:
            return
        try:
            data, names = self._extract_data()
            groups = [np.array(g) for g in data]

            ms_w = self._last_results["MS"]["within"]
            df_w = self._last_results["df"]["within"]

            tukey = tukey_hsd(groups, names)
            bonf = bonferroni(groups, names)
            sch = scheffe(groups, names, ms_within=ms_w, df_within=df_w)

            combined = (
                self._last_results["summary"]
                + "\n\n" + tukey["summary"]
                + "\n\n" + bonf["summary"]
                + "\n\n" + sch["summary"]
            )
            self.results_text.setText(combined)
        except Exception as e:
            QMessageBox.critical(self, "Post-Hoc Error", str(e))

    # ── Visualize ──
    def visualize(self):
        if not self._last_results:
            return
        self._clear_viz()
        try:
            r = self._last_results
            data, _ = self._extract_data()
            groups = [np.array(g) for g in data]

            figs = [
                box_plot(groups, r["group_names"]),
                bar_chart_with_error(r["group_means"], r["group_se"],
                                     r["group_names"]),
                residual_plots(r["residuals"]),
            ]
            for fig in figs:
                canvas = FigureCanvas(fig)
                canvas.setMinimumHeight(350)
                self.viz_layout.addWidget(canvas)
        except Exception as e:
            QMessageBox.critical(self, "Visualization Error", str(e))

    # ── Save ──
    def save_results(self):
        if not self._last_csv:
            QMessageBox.information(self, "Nothing to Save",
                                    "Run a calculation first.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "anova_results.csv",
            "CSV Files (*.csv);;All Files (*)"
        )
        if path:
            with open(path, "w", newline="") as f:
                f.write(self._last_csv)
            QMessageBox.information(self, "Saved", f"Results saved to:\n{path}")

    # ── Reset ──
    def reset_all(self):
        self.table.clearContents()
        self.results_text.clear()
        self._last_results = None
        self._last_csv = None
        self.posthoc_btn.setEnabled(False)
        self.viz_btn.setEnabled(False)
        self._clear_viz()

    # ── Helpers ──
    def _clear_viz(self):
        while self.viz_layout.count():
            child = self.viz_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _parse_group_names(self, n):
        raw = self.group_names_edit.text().strip()
        if raw:
            parts = [s.strip() for s in raw.split(",") if s.strip()]
            if len(parts) >= n:
                return parts[:n]
        return [f"Group {i + 1}" for i in range(n)]


# ======================================================================
# Two-Way Tab
# ======================================================================
class TwoWayTab(QWidget):
    def __init__(self):
        super().__init__()
        self._last_results = None
        self._last_csv = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # ── Config ──
        config_group = QGroupBox("Configuration")
        cg = QGridLayout(config_group)

        cg.addWidget(QLabel("Factor A Name:"), 0, 0)
        self.factor_a_edit = QLineEdit("Factor A")
        cg.addWidget(self.factor_a_edit, 0, 1)

        cg.addWidget(QLabel("Factor B Name:"), 0, 2)
        self.factor_b_edit = QLineEdit("Factor B")
        cg.addWidget(self.factor_b_edit, 0, 3)

        cg.addWidget(QLabel("Levels of A:"), 1, 0)
        self.levels_a_spin = QSpinBox()
        self.levels_a_spin.setRange(2, 20)
        self.levels_a_spin.setValue(2)
        cg.addWidget(self.levels_a_spin, 1, 1)

        cg.addWidget(QLabel("Levels of B:"), 1, 2)
        self.levels_b_spin = QSpinBox()
        self.levels_b_spin.setRange(2, 20)
        self.levels_b_spin.setValue(3)
        cg.addWidget(self.levels_b_spin, 1, 3)

        cg.addWidget(QLabel("Replicates/cell:"), 2, 0)
        self.reps_spin = QSpinBox()
        self.reps_spin.setRange(2, 50)
        self.reps_spin.setValue(3)
        cg.addWidget(self.reps_spin, 2, 1)

        gen_btn = QPushButton("Generate Table")
        gen_btn.setStyleSheet(BTN_GRAY)
        gen_btn.clicked.connect(self.generate_table)
        cg.addWidget(gen_btn, 2, 2, 1, 2)

        layout.addWidget(config_group)

        # ── Data table ──
        self.table = QTableWidget()
        layout.addWidget(self.table)

        # ── Action buttons ──
        action_layout = QHBoxLayout()

        calc_btn = QPushButton("Calculate ANOVA")
        calc_btn.setStyleSheet(BTN_GREEN)
        calc_btn.clicked.connect(self.calculate_anova)
        action_layout.addWidget(calc_btn)

        self.posthoc_btn = QPushButton("Run Post-Hoc")
        self.posthoc_btn.setStyleSheet(BTN_BLUE)
        self.posthoc_btn.setEnabled(False)
        self.posthoc_btn.clicked.connect(self.run_posthoc)
        action_layout.addWidget(self.posthoc_btn)

        self.viz_btn = QPushButton("Visualize")
        self.viz_btn.setStyleSheet(BTN_ORANGE)
        self.viz_btn.setEnabled(False)
        self.viz_btn.clicked.connect(self.visualize)
        action_layout.addWidget(self.viz_btn)

        save_btn = QPushButton("Save Results (CSV)")
        save_btn.setStyleSheet(BTN_GRAY)
        save_btn.clicked.connect(self.save_results)
        action_layout.addWidget(save_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.setStyleSheet(BTN_RED)
        reset_btn.clicked.connect(self.reset_all)
        action_layout.addWidget(reset_btn)

        layout.addLayout(action_layout)

        # ── Results ──
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setPlaceholderText("Results will appear here ...")
        self.results_text.setStyleSheet(MONO_FONT)
        self.results_text.setMaximumHeight(220)
        layout.addWidget(self.results_text)

        # ── Viz scroll ──
        self.viz_scroll = QScrollArea()
        self.viz_scroll.setWidgetResizable(True)
        self.viz_container = QWidget()
        self.viz_layout = QVBoxLayout(self.viz_container)
        self.viz_scroll.setWidget(self.viz_container)
        self.viz_scroll.setMinimumHeight(100)
        layout.addWidget(self.viz_scroll, stretch=1)

        # Generate initial table
        self.generate_table()

    # ── Generate table ──
    def generate_table(self):
        a = self.levels_a_spin.value()
        b = self.levels_b_spin.value()
        r = self.reps_spin.value()
        fa = self.factor_a_edit.text().strip() or "Factor A"
        fb = self.factor_b_edit.text().strip() or "Factor B"

        total_rows = a * r
        total_cols = b

        self.table.setRowCount(total_rows)
        self.table.setColumnCount(total_cols)

        # Column headers: Factor B levels
        headers_col = [f"{fb} {j + 1}" for j in range(b)]
        self.table.setHorizontalHeaderLabels(headers_col)

        # Row headers: Factor A levels with replicate indices
        headers_row = []
        for i in range(a):
            for k in range(r):
                headers_row.append(f"{fa} {i + 1} [r{k + 1}]")
        self.table.setVerticalHeaderLabels(headers_row)
        self.table.clearContents()

    # ── Extract data ──
    def _extract_data(self):
        a = self.levels_a_spin.value()
        b = self.levels_b_spin.value()
        r = self.reps_spin.value()

        data = []
        for i in range(a):
            row_data = []
            for j in range(b):
                cell_reps = []
                for k in range(r):
                    table_row = i * r + k
                    item = self.table.item(table_row, j)
                    if item and item.text().strip():
                        try:
                            cell_reps.append(float(item.text()))
                        except ValueError:
                            raise ValueError(
                                f"Invalid number at row {table_row + 1}, "
                                f"column {j + 1}: '{item.text()}'"
                            )
                    else:
                        raise ValueError(
                            f"Empty cell at row {table_row + 1}, "
                            f"column {j + 1}. All cells must be filled."
                        )
                row_data.append(cell_reps)
            data.append(row_data)
        return data

    # ── Calculate ──
    def calculate_anova(self):
        try:
            data = self._extract_data()
            fa = self.factor_a_edit.text().strip() or "Factor A"
            fb = self.factor_b_edit.text().strip() or "Factor B"

            anova = TwoWayANOVA(data, factor_a_name=fa, factor_b_name=fb)
            self._last_results = anova.calculate()
            self._last_csv = anova.to_csv_string()
            self.results_text.setText(self._last_results["summary"])
            self.posthoc_btn.setEnabled(True)
            self.viz_btn.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # ── Post-hoc ──
    def run_posthoc(self):
        if not self._last_results:
            return
        try:
            r = self._last_results
            ms_e = r["MS"]["error"]
            df_e = r["df"]["error"]

            sections = [r["summary"]]

            # Post-hoc on Factor A if significant
            if r["p_value"]["A"] < 0.05:
                sections.append(
                    f"\n\n--- Post-Hoc for {r['a_names'][0].rsplit(' ', 1)[0]} "
                    f"(p={r['p_value']['A']:.6f}) ---"
                )
                t = tukey_hsd(r["groups_by_a"], r["a_names"])
                b = bonferroni(r["groups_by_a"], r["a_names"])
                s = scheffe(r["groups_by_a"], r["a_names"],
                            ms_within=ms_e, df_within=df_e)
                sections += [t["summary"], b["summary"], s["summary"]]
            else:
                sections.append(
                    f"\nFactor A not significant (p={r['p_value']['A']:.4f}), "
                    "post-hoc skipped."
                )

            # Post-hoc on Factor B if significant
            if r["p_value"]["B"] < 0.05:
                sections.append(
                    f"\n\n--- Post-Hoc for {r['b_names'][0].rsplit(' ', 1)[0]} "
                    f"(p={r['p_value']['B']:.6f}) ---"
                )
                t = tukey_hsd(r["groups_by_b"], r["b_names"])
                b = bonferroni(r["groups_by_b"], r["b_names"])
                s = scheffe(r["groups_by_b"], r["b_names"],
                            ms_within=ms_e, df_within=df_e)
                sections += [t["summary"], b["summary"], s["summary"]]
            else:
                sections.append(
                    f"\nFactor B not significant (p={r['p_value']['B']:.4f}), "
                    "post-hoc skipped."
                )

            self.results_text.setText("\n".join(sections))
        except Exception as e:
            QMessageBox.critical(self, "Post-Hoc Error", str(e))

    # ── Visualize ──
    def visualize(self):
        if not self._last_results:
            return
        self._clear_viz()
        try:
            r = self._last_results
            fa = self.factor_a_edit.text().strip() or "Factor A"
            fb = self.factor_b_edit.text().strip() or "Factor B"

            figs = [
                # Box plots per Factor A
                box_plot(r["groups_by_a"], r["a_names"],
                         title=f"Box Plot by {fa}"),
                # Bar chart per Factor A
                bar_chart_with_error(
                    r["row_means"], r["se_a"], r["a_names"],
                    title=f"{fa} Means ± SE"
                ),
                # Box plots per Factor B
                box_plot(r["groups_by_b"], r["b_names"],
                         title=f"Box Plot by {fb}"),
                # Bar chart per Factor B
                bar_chart_with_error(
                    r["col_means"], r["se_b"], r["b_names"],
                    title=f"{fb} Means ± SE"
                ),
                # Interaction plot
                interaction_plot(
                    r["cell_means"], r["a_names"], r["b_names"],
                    factor_a_label=fa, factor_b_label=fb
                ),
                # Residual diagnostics
                residual_plots(r["residuals"]),
            ]
            for fig in figs:
                canvas = FigureCanvas(fig)
                canvas.setMinimumHeight(350)
                self.viz_layout.addWidget(canvas)
        except Exception as e:
            QMessageBox.critical(self, "Visualization Error", str(e))

    # ── Save ──
    def save_results(self):
        if not self._last_csv:
            QMessageBox.information(self, "Nothing to Save",
                                    "Run a calculation first.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "two_way_anova_results.csv",
            "CSV Files (*.csv);;All Files (*)"
        )
        if path:
            with open(path, "w", newline="") as f:
                f.write(self._last_csv)
            QMessageBox.information(self, "Saved", f"Results saved to:\n{path}")

    # ── Reset ──
    def reset_all(self):
        self.table.clearContents()
        self.results_text.clear()
        self._last_results = None
        self._last_csv = None
        self.posthoc_btn.setEnabled(False)
        self.viz_btn.setEnabled(False)
        self._clear_viz()

    # ── Helpers ──
    def _clear_viz(self):
        while self.viz_layout.count():
            child = self.viz_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()


# ======================================================================
# Main Window
# ======================================================================
class ANOVACalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ANOVA Calculator — One-Way & Two-Way")
        self.resize(1050, 800)

        tabs = QTabWidget()
        tabs.setFont(QFont("Segoe UI", 11))

        self.one_way_tab = OneWayTab()
        self.two_way_tab = TwoWayTab()

        tabs.addTab(self.one_way_tab, "  One-Way ANOVA  ")
        tabs.addTab(self.two_way_tab, "  Two-Way ANOVA  ")

        self.setCentralWidget(tabs)


# ======================================================================
# Entry point
# ======================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ANOVACalculator()
    window.show()
    sys.exit(app.exec())
