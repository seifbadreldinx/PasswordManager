import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog
from login import LoginWindow, SetupDialog, DARK
from auth import is_setup, set_master_password


def main():
    app = QApplication(sys.argv)

    if not is_setup():
        dlg = SetupDialog(DARK)
        if dlg.exec_() == QDialog.Accepted and dlg.result_password:
            set_master_password(dlg.result_password)
            from gui import PasswordManagerUI
            win = PasswordManagerUI(dlg.result_password)
            win.show()
            sys.exit(app.exec_())
        sys.exit(0)
    else:
        window = LoginWindow()
        window.show()
        sys.exit(app.exec_())


if __name__ == "__main__":
    main()
