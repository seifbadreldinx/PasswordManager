import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox,
    QInputDialog
)

from auth import get_master_password, set_master_password


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
        saved = get_master_password()

        if saved is None:
            new_pass, ok = QInputDialog.getText(
                self,
                "Setup",
                "Create Master Password:",
                QLineEdit.Password
            )

            if ok and new_pass:
                set_master_password(new_pass)
                saved = new_pass
            else:
                return

        if self.password.text() == saved:
            from gui import PasswordManagerUI

            self.win = PasswordManagerUI()
            self.win.show()
            self.close()

        else:
            QMessageBox.warning(self, "Error", "Wrong Password ❌")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())