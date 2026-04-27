import sys
import pyperclip

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QComboBox, QSpinBox,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView
)

from generator import generate_password
from database import create_table, insert_password, get_passwords, delete_password, check_password_reuse
from security import check_strength, calculate_entropy, entropy_level
from breach import check_breach


class PasswordManagerUI(QWidget):
    def __init__(self, master_password):
        super().__init__()

        self.master_password = master_password
        self.current_data = []
        self.passwords_visible = False

        create_table()

        self.setWindowTitle("Secure Password Manager 🔐")
        self.setGeometry(250, 100, 800, 600)

        self.ui()
        self.show_data()

    def ui(self):
        layout = QVBoxLayout()

        self.site = QLineEdit()
        self.site.setPlaceholderText("Site")
        layout.addWidget(self.site)

        self.user = QLineEdit()
        self.user.setPlaceholderText("Username")
        layout.addWidget(self.user)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.textChanged.connect(self._update_strength_indicator)
        layout.addWidget(self.password)

        self.strength_label = QLabel("Strength: —")
        self.strength_label.setStyleSheet("color: gray; font-weight: bold;")
        layout.addWidget(self.strength_label)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Strength:"))

        self.strength = QComboBox()
        self.strength.addItems(["weak", "medium", "strong"])
        row1.addWidget(self.strength)

        layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Length:"))

        self.length = QSpinBox()
        self.length.setRange(6, 32)
        self.length.setValue(12)
        row2.addWidget(self.length)

        layout.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Category:"))

        self.category = QComboBox()
        self.category.addItems(["Social", "Banking", "Work", "Other"])
        row3.addWidget(self.category)

        layout.addLayout(row3)

        btn1 = QPushButton("Generate Password")
        btn1.clicked.connect(self.generate)
        layout.addWidget(btn1)

        btn2 = QPushButton("Save Password")
        btn2.clicked.connect(self.save)
        layout.addWidget(btn2)

        btn3 = QPushButton("Refresh Vault")
        btn3.clicked.connect(self.show_data)
        layout.addWidget(btn3)

        btn_row = QHBoxLayout()

        btn4 = QPushButton("Delete Selected")
        btn4.clicked.connect(self.delete_selected)
        btn_row.addWidget(btn4)

        btn5 = QPushButton("Copy Password")
        btn5.clicked.connect(self.copy_selected_password)
        btn_row.addWidget(btn5)

        self.reveal_btn = QPushButton("Show Passwords")
        self.reveal_btn.setCheckable(True)
        self.reveal_btn.toggled.connect(self._toggle_reveal)
        btn_row.addWidget(self.reveal_btn)

        layout.addLayout(btn_row)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["Site", "Username", "Password", "Category"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.table)

        self.setLayout(layout)

    # Live strength indicator
    def _update_strength_indicator(self, text):
        if not text:
            self.strength_label.setText("Strength: —")
            self.strength_label.setStyleSheet("color: gray; font-weight: bold;")
            return

        strength, _ = check_strength(text)
        entropy = calculate_entropy(text)
        level = entropy_level(entropy)

        colors = {"Weak": "#e74c3c", "Medium": "#e67e22", "Strong": "#27ae60"}
        color = colors.get(level, "gray")

        self.strength_label.setText(
            f"Strength: {strength}  |  Entropy: {entropy} bits  |  Level: {level}"
        )
        self.strength_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    # Generate password
    def generate(self):
        pwd = generate_password(
            self.length.value(),
            self.strength.currentText()
        )

        self.password.setText(pwd)

        clipboard = QApplication.clipboard()
        clipboard.setText(pwd)

        QTimer.singleShot(10000, lambda: clipboard.clear())

    # Save password
    def save(self):
        site = self.site.text().strip()
        user = self.user.text().strip()
        pwd = self.password.text().strip()
        cat = self.category.currentText()

        if not site or not user or not pwd:
            QMessageBox.warning(self, "Warning", "Fill all fields")
            return

        strength, msg = check_strength(pwd)
        entropy = calculate_entropy(pwd)
        level = entropy_level(entropy)

        if check_breach(pwd):
            QMessageBox.critical(self, "Breached", "Password leaked!")
            return

        reused, sites = check_password_reuse(pwd, self.master_password)
        if reused:
            QMessageBox.critical(
                self,
                "Reuse Blocked",
                "Used in:\n" + ", ".join(sites)
            )
            return

        insert_password(site, user, pwd, cat, self.master_password)

        QMessageBox.information(
            self,
            "Saved ✔",
            f"Strength: {strength}\n"
            f"Entropy: {entropy} bits\n"
            f"Security Level: {level}"
        )

        self.site.clear()
        self.user.clear()
        self.password.clear()

        self.show_data()

    # Copy selected password to clipboard
    def copy_selected_password(self):
        selected = self.table.currentRow()

        if selected < 0:
            QMessageBox.warning(self, "Warning", "Select a row to copy")
            return

        pwd = self.current_data[selected][3]
        if pwd is None:
            QMessageBox.warning(self, "Error", "Could not decrypt password")
            return

        clipboard = QApplication.clipboard()
        clipboard.setText(pwd)
        QTimer.singleShot(10000, lambda: clipboard.clear())
        QMessageBox.information(self, "Copied", "Password copied. Clipboard clears in 10 seconds.")

    # Toggle password visibility in table
    def _toggle_reveal(self, checked):
        self.passwords_visible = checked
        self.reveal_btn.setText("Hide Passwords" if checked else "Show Passwords")
        self.show_data()

    # Delete selected password
    def delete_selected(self):
        selected = self.table.currentRow()

        if selected < 0:
            QMessageBox.warning(self, "Warning", "Select a row to delete")
            return

        entry_id = self.current_data[selected][0]
        site = self.current_data[selected][1]

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete password for '{site}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            delete_password(entry_id)
            self.show_data()

    # Show passwords
    def show_data(self):
        self.current_data = get_passwords(self.master_password)
        self.table.setRowCount(len(self.current_data))

        for i, row in enumerate(self.current_data):
            pwd_display = row[3] if self.passwords_visible else "••••••••"
            self.table.setItem(i, 0, QTableWidgetItem(row[1]))
            self.table.setItem(i, 1, QTableWidgetItem(row[2]))
            self.table.setItem(i, 2, QTableWidgetItem(pwd_display))
            self.table.setItem(i, 3, QTableWidgetItem(row[4]))

    # Clear clipboard on close
    def closeEvent(self, event):
        pyperclip.copy("")
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PasswordManagerUI()
    win.show()
    sys.exit(app.exec_())