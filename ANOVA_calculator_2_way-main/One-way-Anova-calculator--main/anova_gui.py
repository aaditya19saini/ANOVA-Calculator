import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QTableWidget, QTableWidgetItem, 
                               QPushButton, QLabel, QTextEdit, QMessageBox, QHeaderView)
from PySide6.QtCore import Qt
from anova_logic import ANOVA

class AnovaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ANOVA Calculator")
        self.resize(800, 600)

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Title
        title_label = QLabel("One-Way ANOVA Calculator")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)

        # Instructions
        instr_label = QLabel("Enter data in columns. Each column represents a group.")
        layout.addWidget(instr_label)

        # Spreadsheet (QTableWidget)
        self.table = QTableWidget(10, 3) # Initial size: 10 rows, 3 columns
        self.table.setHorizontalHeaderLabels(["Group 1", "Group 2", "Group 3"])
        layout.addWidget(self.table)

        # Buttons Layout
        btn_layout = QHBoxLayout()
        
        self.add_col_btn = QPushButton("Add Group (Column)")
        self.add_col_btn.clicked.connect(self.add_column)
        btn_layout.addWidget(self.add_col_btn)

        self.remove_col_btn = QPushButton("Remove Group")
        self.remove_col_btn.clicked.connect(self.remove_column)
        btn_layout.addWidget(self.remove_col_btn)

        self.add_row_btn = QPushButton("Add Row")
        self.add_row_btn.clicked.connect(self.add_row)
        btn_layout.addWidget(self.add_row_btn)
        
        self.calc_btn = QPushButton("Calculate ANOVA")
        self.calc_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.calc_btn.clicked.connect(self.calculate_anova)
        btn_layout.addWidget(self.calc_btn)

        layout.addLayout(btn_layout)

        # Results Display
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setPlaceholderText("Results will appear here...")
        self.results_text.setStyleSheet("font-family: Consolas, monospace;")
        layout.addWidget(self.results_text)

    def add_column(self):
        col_count = self.table.columnCount()
        self.table.insertColumn(col_count)
        self.table.setHorizontalHeaderItem(col_count, QTableWidgetItem(f"Group {col_count + 1}"))

    def remove_column(self):
        col_count = self.table.columnCount()
        if col_count > 0:
            self.table.removeColumn(col_count - 1)

    def add_row(self):
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)

    def calculate_anova(self):
        data = []
        try:
            # Iterate over columns (groups)
            for col in range(self.table.columnCount()):
                group_data = []
                for row in range(self.table.rowCount()):
                    item = self.table.item(row, col)
                    if item and item.text().strip():
                        try:
                            val = float(item.text())
                            group_data.append(val)
                        except ValueError:
                            raise ValueError(f"Invalid number at Row {row+1}, Column {col+1}")
                
                if group_data:
                    data.append(group_data)
            
            if len(data) < 2:
                QMessageBox.warning(self, "Input Error", "Please provide at least two groups with data.")
                return

            # Perform Calculation
            anova = ANOVA(data)
            results = anova.calculate()
            
            # Display Results
            self.results_text.setText(results['summary'])
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnovaApp()
    window.show()
    sys.exit(app.exec())
