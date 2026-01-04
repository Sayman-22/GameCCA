# ui/login_dialog.py

import socket
import json
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from ui.style import COSMIC_STYLE
from ui.network_client import send_request_log

class LoginDialog(QDialog):
####### ИНИЦИАЛИЗАЦИЯ ОКНА #######
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Авторизация")
        self.resize(300, 200)
        self.setStyleSheet(COSMIC_STYLE)
        self.username = None
        self.stats = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.label = QLabel("Войдите или зарегистрируйтесь")

        # Логин
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Логин")
        self.login_input.setText("User")

        # Пароль
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Пароль")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setText("123")

        # Управление
        self.btn_login = QPushButton("Войти")
        self.btn_register = QPushButton("Регистрация")

        # Добавляем виджеты на компановщик
        layout.addWidget(self.label)
        layout.addWidget(self.login_input)
        layout.addWidget(self.pass_input)
        layout.addWidget(self.btn_login)
        layout.addWidget(self.btn_register)

        self.btn_login.clicked.connect(self.login)
        self.btn_register.clicked.connect(self.register)
####### ИНИЦИАЛИЗАЦИЯ ОКНА #######


    def login(self):
        username = self.login_input.text().strip()
        password = self.pass_input.text()
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        response = send_request_log(self, "login", username, password)
        if response and response["status"] == "success":
            self.username = username
            self.stats = response["stats"]
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", response["message"] if response else "Неизвестная ошибка")

    def register(self):
        username = self.login_input.text().strip()
        password = self.pass_input.text()
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        response = send_request_log(self, "register", username, password)
        if response and response["status"] == "success":
            self.username = username
            self.stats = response["stats"]
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", response["message"] if response else "Неизвестная ошибка")