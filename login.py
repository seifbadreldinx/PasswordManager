import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox, QLabel, QFrame, QDialog
)

from auth import verify_master_password, set_master_password, is_setup


DARK = """
    QWidget { background-color: #1e1e2e; color: #cdd6f4;
              font-family: Segoe UI, Arial, sans-serif; font-size: 13px; }
    QFrame#card { background-color: #313244; border-radius: 12px; }
    QLabel#title { color: #cdd6f4; font-size: 20px; font-weight: bold; }
    QLabel#subtitle { color: #a6adc8; font-size: 12px; }
    QLineEdit { background-color: #1e1e2e; border: 1px solid #45475a;
                border-radius: 8px; padding: 10px 14px; color: #cdd6f4;
                font-size: 14px; min-height: 20px; }
    QLineEdit:focus { border: 1px solid #89b4fa; }
    QPushButton#loginBtn { background-color: #89b4fa; color: #1e1e2e; border: none;
                           border-radius: 8px; padding: 11px; font-size: 14px;
                           font-weight: bold; min-height: 20px; }
    QPushButton#loginBtn:hover { background-color: #b4befe; }
    QPushButton#loginBtn:pressed { background-color: #74c7ec; }
    QPushButton#themeBtn { background-color: #313244; color: #cdd6f4; border: 1px solid #45475a;
                           border-radius: 6px; padding: 5px 10px; font-size: 12px; }
    QPushButton#themeBtn:hover { background-color: #45475a; }
"""

LIGHT = """
    QWidget { background-color: #eff1f5; color: #4c4f69;
              font-family: Segoe UI, Arial, sans-serif; font-size: 13px; }
    QFrame#card { background-color: #ffffff; border-radius: 12px; }
    QLabel#title { color: #4c4f69; font-size: 20px; font-weight: bold; }
    QLabel#subtitle { color: #7c7f93; font-size: 12px; }
    QLineEdit { background-color: #eff1f5; border: 1px solid #bcc0cc;
                border-radius: 8px; padding: 10px 14px; color: #4c4f69;
                font-size: 14px; min-height: 20px; }
    QLineEdit:focus { border: 1px solid #1e66f5; }
    QPushButton#loginBtn { background-color: #1e66f5; color: #ffffff; border: none;
                           border-radius: 8px; padding: 11px; font-size: 14px;
                           font-weight: bold; min-height: 20px; }
    QPushButton#loginBtn:hover { background-color: #209fb5; }
    QPushButton#loginBtn:pressed { background-color: #04a5e5; }
    QPushButton#themeBtn { background-color: #dce0e8; color: #4c4f69; border: 1px solid #bcc0cc;
                           border-radius: 6px; padding: 5px 10px; font-size: 12px; }
    QPushButton#themeBtn:hover { background-color: #bcc0cc; }
"""


class SetupDialog(QDialog):
    """Styled first-run dialog that inherits the app theme."""

    def __init__(self, stylesheet, parent=None):
        super().__init__(parent)
        self.setWindowTitle("First Time Setup")
        self.setFixedWidth(360)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setStyleSheet(stylesheet)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(14)

        title = QLabel("🔑  Create Master Password")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        sub = QLabel("This password encrypts your entire vault.\nIt cannot be recovered if forgotten.")
        sub.setObjectName("subtitle")
        sub.setAlignment(Qt.AlignCenter)
        sub.setWordWrap(True)
        layout.addWidget(sub)

        layout.addSpacing(4)

        self.field = QLineEdit()
        self.field.setPlaceholderText("New Master Password")
        self.field.setEchoMode(QLineEdit.Password)
        self.field.returnPressed.connect(self._confirm)
        layout.addWidget(self.field)

        self.confirm = QLineEdit()
        self.confirm.setPlaceholderText("Confirm Master Password")
        self.confirm.setEchoMode(QLineEdit.Password)
        self.confirm.returnPressed.connect(self._confirm)
        layout.addWidget(self.confirm)

        self.error_lbl = QLabel("")
        self.error_lbl.setStyleSheet("color: #f38ba8; font-size: 12px;")
        self.error_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_lbl)

        btn = QPushButton("Create Vault")
        btn.setObjectName("loginBtn")
        btn.clicked.connect(self._confirm)
        layout.addWidget(btn)

        self.result_password = None

    def _confirm(self):
        p1 = self.field.text()
        p2 = self.confirm.text()
        if not p1:
            self.error_lbl.setText("Password cannot be empty.")
            return
        if p1 != p2:
            self.error_lbl.setText("Passwords do not match.")
            self.confirm.clear()
            return
        self.result_password = p1
        self.accept()


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.is_dark = True

        self.setWindowTitle("Secure Password Manager 🔐")
        self.setMinimumSize(400, 300)
        self.setStyleSheet(DARK)

        # Outer layout — centres the card vertically and horizontally
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        # Theme button pinned top-right
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        self.theme_btn = QPushButton("☀  Light Mode")
        self.theme_btn.setObjectName("themeBtn")
        self.theme_btn.setFixedWidth(120)
        self.theme_btn.clicked.connect(self._toggle_theme)
        top_bar.addWidget(self.theme_btn)
        top_bar.setContentsMargins(0, 8, 12, 0)
        outer.addLayout(top_bar)

        outer.addStretch()

        # Card frame with fixed width, centred
        card_row = QHBoxLayout()
        card_row.addStretch()

        card = QFrame()
        card.setObjectName("card")
        card.setFixedWidth(360)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(16)

        title = QLabel("🔐  Password Manager")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)

        subtitle = QLabel("Enter your master password to unlock the vault")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        card_layout.addWidget(subtitle)

        card_layout.addSpacing(8)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Master Password")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.returnPressed.connect(self.login)
        card_layout.addWidget(self.password)

        btn = QPushButton("Login")
        btn.setObjectName("loginBtn")
        btn.clicked.connect(self.login)
        card_layout.addWidget(btn)

        card_row.addWidget(card)
        card_row.addStretch()
        outer.addLayout(card_row)

        outer.addStretch()


    def _toggle_theme(self):
        self.is_dark = not self.is_dark
        self.setStyleSheet(DARK if self.is_dark else LIGHT)
        self.theme_btn.setText("☀  Light Mode" if self.is_dark else "🌙  Dark Mode")

    def login(self):
        entered = self.password.text()

        if verify_master_password(entered):
            self._open_vault(entered)
        else:
            self.password.clear()
            self.password.setStyleSheet("border: 1px solid #f38ba8;")
            QMessageBox.warning(self, "Error", "Wrong Password ❌")
            self.password.setStyleSheet("")

    def _open_vault(self, master_password):
        from gui import PasswordManagerUI

        self.win = PasswordManagerUI(master_password)
        self.win.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    if not is_setup():
        # First run — show only the setup dialog, then show login
        dlg = SetupDialog(DARK)
        if dlg.exec_() == QDialog.Accepted and dlg.result_password:
            set_master_password(dlg.result_password)
        else:
            sys.exit(0)

    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())