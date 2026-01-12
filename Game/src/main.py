# main.py

import sys
from PyQt5.QtWidgets import QApplication
from ui.login_dialog import LoginDialog
from ui.main_menu import MainMenuWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Показываем окно входа
    login = LoginDialog()
    if login.exec_() == LoginDialog.Accepted:
        # Передаём имя пользователя и статистику в главное меню
        main_menu = MainMenuWindow(login.username, login.stats)
        main_menu.show()
        sys.exit(app.exec_())
    else:
        sys.exit(0)