import sys
import ctypes
import pyperclip

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QComboBox, QSpinBox,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView,
    QFrame, QSizePolicy
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
        self.is_dark_mode = True

        create_table()

        self.setWindowTitle("Secure Password Manager 🔐")
        self.setGeometry(250, 100, 860, 680)
        self._apply_style()

        self.ui()
        self.show_data()

    DARK_STYLE = """
        QWidget { background-color: #1e1e2e; color: #cdd6f4;
                  font-family: Segoe UI, Arial, sans-serif; font-size: 13px; }
        QLineEdit, QComboBox, QSpinBox { background-color: #313244; border: 1px solid #45475a;
            border-radius: 6px; padding: 6px 10px; color: #cdd6f4; }
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus { border: 1px solid #89b4fa; }
        QPushButton { background-color: #89b4fa; color: #1e1e2e; border: none;
            border-radius: 6px; padding: 7px 14px; font-weight: bold; }
        QPushButton:hover { background-color: #b4befe; }
        QPushButton:pressed { background-color: #74c7ec; }
        QPushButton:checked { background-color: #a6e3a1; color: #1e1e2e; }
        QTableWidget { background-color: #313244; gridline-color: #45475a;
            border: none; border-radius: 6px; }
        QHeaderView::section { background-color: #45475a; color: #cdd6f4;
            padding: 6px; border: none; font-weight: bold; }
        QTableWidget::item:selected { background-color: #89b4fa; color: #1e1e2e; }
        QLabel { color: #cdd6f4; }
    """

    LIGHT_STYLE = """
        QWidget { background-color: #eff1f5; color: #4c4f69;
                  font-family: Segoe UI, Arial, sans-serif; font-size: 13px; }
        QLineEdit, QComboBox, QSpinBox { background-color: #ffffff; border: 1px solid #bcc0cc;
            border-radius: 6px; padding: 6px 10px; color: #4c4f69; }
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus { border: 1px solid #1e66f5; }
        QPushButton { background-color: #1e66f5; color: #ffffff; border: none;
            border-radius: 6px; padding: 7px 14px; font-weight: bold; }
        QPushButton:hover { background-color: #209fb5; }
        QPushButton:pressed { background-color: #04a5e5; }
        QPushButton:checked { background-color: #40a02b; color: #ffffff; }
        QTableWidget { background-color: #ffffff; gridline-color: #bcc0cc;
            border: none; border-radius: 6px; }
        QHeaderView::section { background-color: #dce0e8; color: #4c4f69;
            padding: 6px; border: none; font-weight: bold; }
        QTableWidget::item:selected { background-color: #1e66f5; color: #ffffff; }
        QLabel { color: #4c4f69; }
    """

    def _apply_style(self):
        self.setStyleSheet(self.DARK_STYLE if self.is_dark_mode else self.LIGHT_STYLE)

    def ui(self):
        # Root layout
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)

        # ── Top bar ──────────────────────────────────────────
        top_bar = QHBoxLayout()
        title_lbl = QLabel("🔐  Secure Password Manager")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold;")
        top_bar.addWidget(title_lbl)

        local_badge = QLabel("🖥 Local Only — Never Synced")
        local_badge.setStyleSheet(
            "color: #a6e3a1; font-size: 11px; font-weight: bold; "
            "background-color: #1e3a2e; border-radius: 4px; padding: 3px 8px;"
        )
        top_bar.addWidget(local_badge)
        top_bar.addStretch()
        self.theme_btn = QPushButton("☀  Light Mode")
        self.theme_btn.setCheckable(True)
        self.theme_btn.setFixedWidth(140)
        self.theme_btn.toggled.connect(self._toggle_theme)
        top_bar.addWidget(self.theme_btn)
        root.addLayout(top_bar)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #45475a;")
        root.addWidget(line)

        # ── Two-column body ───────────────────────────────────
        body = QHBoxLayout()
        body.setSpacing(20)

        # ── LEFT PANEL: form ──────────────────────────────────
        left = QVBoxLayout()
        left.setSpacing(10)

        form_label = QLabel("Add New Password")
        form_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        left.addWidget(form_label)

        self.site = QLineEdit()
        self.site.setPlaceholderText("Site  (e.g. github.com)")
        left.addWidget(self.site)

        self.user = QLineEdit()
        self.user.setPlaceholderText("Username / Email")
        left.addWidget(self.user)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.textChanged.connect(self._update_strength_indicator)
        left.addWidget(self.password)

        self.strength_label = QLabel("Strength: —")
        self.strength_label.setStyleSheet("color: gray; font-weight: bold; font-size: 12px;")
        self.strength_label.setWordWrap(True)
        left.addWidget(self.strength_label)

        # Row: Strength + Length
        opts_row = QHBoxLayout()
        opts_row.addWidget(QLabel("Strength:"))
        self.strength = QComboBox()
        self.strength.addItems(["weak", "medium", "strong"])
        self.strength.setCurrentIndex(2)
        opts_row.addWidget(self.strength)
        opts_row.addSpacing(12)
        opts_row.addWidget(QLabel("Length:"))
        self.length = QSpinBox()
        self.length.setRange(6, 32)
        self.length.setValue(12)
        opts_row.addWidget(self.length)
        left.addLayout(opts_row)

        # Row: Category
        cat_row = QHBoxLayout()
        cat_row.addWidget(QLabel("Category:"))
        self.category = QComboBox()
        self.category.addItems(["Social", "Banking", "Work", "Other"])
        cat_row.addWidget(self.category)
        left.addLayout(cat_row)

        btn_gen = QPushButton("⚡  Generate Password")
        btn_gen.clicked.connect(self.generate)
        left.addWidget(btn_gen)

        btn_save = QPushButton("💾  Save Password")
        btn_save.clicked.connect(self.save)
        left.addWidget(btn_save)

        left.addStretch()

        # Wrap left panel in a fixed-width frame
        left_frame = QFrame()
        left_frame.setFixedWidth(300)
        left_frame.setLayout(left)
        body.addWidget(left_frame)

        # ── RIGHT PANEL: vault table ──────────────────────────
        right = QVBoxLayout()
        right.setSpacing(8)

        vault_label = QLabel("Password Vault")
        vault_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        right.addWidget(vault_label)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search by site or username...")
        self.search_box.textChanged.connect(self._filter_table)
        right.addWidget(self.search_box)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Site", "Username", "Password", "Category"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right.addWidget(self.table)

        # Vault action buttons
        vault_btns = QHBoxLayout()
        vault_btns.setSpacing(8)

        self.reveal_btn = QPushButton("👁  Show Passwords")
        self.reveal_btn.setCheckable(True)
        self.reveal_btn.toggled.connect(self._toggle_reveal)
        vault_btns.addWidget(self.reveal_btn)

        btn_copy = QPushButton("📋  Copy Password")
        btn_copy.clicked.connect(self.copy_selected_password)
        vault_btns.addWidget(btn_copy)

        btn_del = QPushButton("🗑  Delete Selected")
        btn_del.clicked.connect(self.delete_selected)
        vault_btns.addWidget(btn_del)

        btn_refresh = QPushButton("↻  Refresh")
        btn_refresh.clicked.connect(self.show_data)
        vault_btns.addWidget(btn_refresh)

        right.addLayout(vault_btns)
        body.addLayout(right)

        root.addLayout(body)

    # Toggle dark / light theme
    def _toggle_theme(self, checked):
        self.is_dark_mode = not checked
        self.theme_btn.setText("🌙  Dark Mode" if checked else "☀  Light Mode")
        self._apply_style()
        # Re-apply dynamic strength label color
        self._update_strength_indicator(self.password.text())

    # Live strength indicator
    def _update_strength_indicator(self, text):
        if not text:
            self.strength_label.setText("Strength: —")
            self.strength_label.setStyleSheet("color: gray; font-weight: bold;")
            return

        # Breach check takes priority
        if check_breach(text):
            self.strength_label.setText("⚠ BREACHED — This password was found in a data leak!")
            self.strength_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
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

    def _clear_clipboard(self):
        """
        Clear the current clipboard AND Windows Clipboard History.
        Uses Win32 EmptyClipboard for the active clipboard and the WinRT
        Clipboard.ClearHistory() API (via PowerShell) for the history.
        """
        # 1. Clear active clipboard
        try:
            if ctypes.windll.user32.OpenClipboard(None):
                ctypes.windll.user32.EmptyClipboard()
                ctypes.windll.user32.CloseClipboard()
        except Exception:
            QApplication.clipboard().setText("")

        # 2. Clear Windows Clipboard History (Win+V) via WinRT API
        try:
            import subprocess
            subprocess.Popen(
                [
                    "powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command",
                    "[Windows.ApplicationModel.DataTransfer.Clipboard,"
                    "Windows.ApplicationModel.DataTransfer,ContentType=WindowsRuntime]"
                    " | Out-Null; "
                    "[Windows.ApplicationModel.DataTransfer.Clipboard]::ClearHistory() | Out-Null"
                ],
                creationflags=0x08000000,  # CREATE_NO_WINDOW
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass

    # Generate password
    def generate(self):
        pwd = generate_password(
            self.length.value(),
            self.strength.currentText()
        )

        self.password.setText(pwd)

        QApplication.clipboard().setText(pwd)
        QTimer.singleShot(10000, self._clear_clipboard)

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

        QApplication.clipboard().setText(pwd)
        QTimer.singleShot(10000, self._clear_clipboard)
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

        self._filter_table(self.search_box.text() if hasattr(self, 'search_box') else "")

    # Live search / filter
    def _filter_table(self, query):
        query = query.strip().lower()
        for i in range(self.table.rowCount()):
            site = self.table.item(i, 0)
            user = self.table.item(i, 1)
            visible = (
                not query
                or (site and query in site.text().lower())
                or (user and query in user.text().lower())
            )
            self.table.setRowHidden(i, not visible)

    # Clear clipboard on close
    def closeEvent(self, event):
        self._clear_clipboard()
        event.accept()


if __name__ == "__main__":
    from login import LoginWindow
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    sys.exit(app.exec_())