import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox,
    QInputDialog
)

from auth import verify_master_password, set_master_password, is_setup


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Login 🔐")
        self.setGeometry(300, 300, 300, 150)

        layout = QVBoxLayout()

        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter Master Password")
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password)

        btn = QPushButton("Login")
        btn.clicked.connect(self.login)
        layout.addWidget(btn)

        self.setLayout(layout)

    def login(self):
        if not is_setup():
            # First run — prompt to create master password
            new_pass, ok = QInputDialog.getText(
                self,
                "Setup",
                "Create Master Password:",
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
            QMessageBox.warning(self, "Error", "Wrong Password ❌")

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