import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox, QInputDialog, QLabel, QFrame
)

from auth import verify_master_password, set_master_password, is_setup


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Secure Password Manager 🔐")
        self.setMinimumSize(400, 300)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: Segoe UI, Arial, sans-serif;
                font-size: 13px;
            }
            QFrame#card {
                background-color: #313244;
                border-radius: 12px;
            }
            QLabel#title {
                color: #cdd6f4;
                font-size: 20px;
                font-weight: bold;
            }
            QLabel#subtitle {
                color: #a6adc8;
                font-size: 12px;
            }
            QLineEdit {
                background-color: #1e1e2e;
                border: 1px solid #45475a;
                border-radius: 8px;
                padding: 10px 14px;
                color: #cdd6f4;
                font-size: 14px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 1px solid #89b4fa;
            }
            QPushButton#loginBtn {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                border-radius: 8px;
                padding: 11px;
                font-size: 14px;
                font-weight: bold;
                min-height: 20px;
            }
            QPushButton#loginBtn:hover { background-color: #b4befe; }
            QPushButton#loginBtn:pressed { background-color: #74c7ec; }
        """)

        # Outer layout — centres the card
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignCenter)

        # Card frame with fixed width
        card = QFrame()
        card.setObjectName("card")
        card.setFixedWidth(360)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(16)

        # Title
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

        # Password field
        self.password = QLineEdit()
        self.password.setPlaceholderText("Master Password")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.returnPressed.connect(self.login)
        card_layout.addWidget(self.password)

        # Login button
        btn = QPushButton("Login")
        btn.setObjectName("loginBtn")
        btn.clicked.connect(self.login)
        card_layout.addWidget(btn)

        outer.addWidget(card)

    def login(self):
        if not is_setup():
            new_pass, ok = QInputDialog.getText(
                self,
                "First Time Setup",
                "Create a Master Password:",
                QLineEdit.Password
            )

            if ok and new_pass:
                set_master_password(new_pass)
                self._open_vault(new_pass)

            return

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
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())