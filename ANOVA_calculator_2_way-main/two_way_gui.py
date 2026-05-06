import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, QTextEdit,
    QMessageBox, QSpinBox, QLineEdit, QFileDialog, QGroupBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from two_way_logic import TwoWayANOVA


class TwoWayAnovaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Two-Way ANOVA Calculator")
        self.resize(900, 700)
        self._last_results = None  # store results for saving

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # ── Title ──
        title = QLabel("Two-Way ANOVA Calculator")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 8px;")
        main_layout.addWidget(title)

        # ── Factor Configuration Panel ──
        config_box = QGroupBox("Configuration")
        config_layout = QGridLayout(config_box)

        # Factor names
        config_layout.addWidget(QLabel("Factor A Name:"), 0, 0)
        self.factor_a_name = QLineEdit("Factor A")
        config_layout.addWidget(self.factor_a_name, 0, 1)

        config_layout.addWidget(QLabel("Factor B Name:"), 0, 2)
        self.factor_b_name = QLineEdit("Factor B")
        config_layout.addWidget(self.factor_b_name, 0, 3)

        # Spinboxes
        config_layout.addWidget(QLabel("Levels of A (rows):"), 1, 0)
        self.spin_a = QSpinBox()
        self.spin_a.setRange(2, 20)
        self.spin_a.setValue(2)
        config_layout.addWidget(self.spin_a, 1, 1)

        config_layout.addWidget(QLabel("Levels of B (cols):"), 1, 2)
        self.spin_b = QSpinBox()
        self.spin_b.setRange(2, 20)
        self.spin_b.setValue(3)
        config_layout.addWidget(self.spin_b, 1, 3)

        config_layout.addWidget(QLabel("Replicates per cell:"), 1, 4)
        self.spin_r = QSpinBox()
        self.spin_r.setRange(2, 50)
        self.spin_r.setValue(3)
        config_layout.addWidget(self.spin_r, 1, 5)

        # Generate Table button
        self.gen_btn = QPushButton("Generate Table")
        self.gen_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 6px;")
        self.gen_btn.clicked.connect(self.generate_table)
        config_layout.addWidget(self.gen_btn, 0, 4, 1, 2)

        main_layout.addWidget(config_box)

        # ── Spreadsheet ──
        self.table = QTableWidget()
        self.table.setStyleSheet("font-size: 13px;")
        main_layout.addWidget(self.table)

        # ── Action Buttons ──
        btn_layout = QHBoxLayout()

        self.calc_btn = QPushButton("Calculate ANOVA")
        self.calc_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; font-weight: bold; padding: 8px 16px;"
        )
        self.calc_btn.clicked.connect(self.calculate_anova)
        btn_layout.addWidget(self.calc_btn)

        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setStyleSheet("padding: 8px 16px;")
        self.reset_btn.clicked.connect(self.reset_all)
        btn_layout.addWidget(self.reset_btn)

        self.save_btn = QPushButton("Save Results")
        self.save_btn.setStyleSheet("padding: 8px 16px;")
        self.save_btn.clicked.connect(self.save_results)
        self.save_btn.setEnabled(False)
        btn_layout.addWidget(self.save_btn)

        main_layout.addLayout(btn_layout)

        # ── Results Panel ──
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setPlaceholderText("Results will appear here after calculation...")
        self.results_text.setFont(QFont("Consolas", 10))
        self.results_text.setMinimumHeight(140)
        main_layout.addWidget(self.results_text)

        # Build initial table
        self.generate_table()

    def generate_table(self):
        """Build the spreadsheet grid based on current configuration."""
        a = self.spin_a.value()
        b = self.spin_b.value()
        r = self.spin_r.value()
        fa_name = self.factor_a_name.text().strip() or "Factor A"
        fb_name = self.factor_b_name.text().strip() or "Factor B"

        total_rows = a * r
        total_cols = b

        self.table.clear()
        self.table.setRowCount(total_rows)
        self.table.setColumnCount(total_cols)

        # Column headers: Factor B levels
        col_headers = [f"{fb_name} {j+1}" for j in range(b)]
        self.table.setHorizontalHeaderLabels(col_headers)

        # Row headers: Factor A levels × replicates
        row_headers = []
        for i in range(a):
            for k in range(r):
                row_headers.append(f"{fa_name} {i+1} - Rep {k+1}")
        self.table.setVerticalHeaderLabels(row_headers)

        # Clear results
        self.results_text.clear()
        self._last_results = None
        self.save_btn.setEnabled(False)

    def _extract_data(self):
        """Extract data from the table into the 3D structure needed by TwoWayANOVA."""
        a = self.spin_a.value()
        b = self.spin_b.value()
        r = self.spin_r.value()

        data = []
        for i in range(a):
            row_data = []
            for j in range(b):
                replicates = []
                for k in range(r):
                    table_row = i * r + k
                    item = self.table.item(table_row, j)
                    if item is None or item.text().strip() == "":
                        raise ValueError(
                            f"Empty cell at {self.factor_a_name.text()} {i+1}, "
                            f"{self.factor_b_name.text()} {j+1}, Replicate {k+1}. "
                            "All cells must be filled."
                        )
                    try:
                        val = float(item.text())
                    except ValueError:
                        raise ValueError(
                            f"Invalid number '{item.text()}' at "
                            f"{self.factor_a_name.text()} {i+1}, "
                            f"{self.factor_b_name.text()} {j+1}, Replicate {k+1}."
                        )
                    replicates.append(val)
                row_data.append(replicates)
            data.append(row_data)
        return data

    def calculate_anova(self):
        """Run the two-way ANOVA calculation and display results."""
        try:
            data = self._extract_data()
            fa_name = self.factor_a_name.text().strip() or "Factor A"
            fb_name = self.factor_b_name.text().strip() or "Factor B"

            anova = TwoWayANOVA(data, factor_a_name=fa_name, factor_b_name=fb_name)
            results = anova.calculate()

            self.results_text.setText(results["summary"])
            self._last_results = anova  # save for CSV export
            self.save_btn.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def reset_all(self):
        """Clear all data and results."""
        # Clear table cells
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                self.table.setItem(row, col, QTableWidgetItem(""))

        # Clear results
        self.results_text.clear()
        self._last_results = None
        self.save_btn.setEnabled(False)

    def save_results(self):
        """Save the ANOVA results to a CSV file at a user-chosen location."""
        if self._last_results is None:
            QMessageBox.warning(self, "No Results", "Please calculate ANOVA first.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save ANOVA Results", os.path.expanduser("~/anova_results.csv"),
            "CSV Files (*.csv);;All Files (*)"
        )

        if file_path:
            try:
                csv_content = self._last_results.to_csv_string()
                with open(file_path, "w", newline="") as f:
                    f.write(csv_content)
                QMessageBox.information(self, "Saved", f"Results saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TwoWayAnovaApp()
    window.show()
    sys.exit(app.exec())
