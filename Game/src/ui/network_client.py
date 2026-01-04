# ui/network_client.py

import socket
import json
from PyQt5.QtWidgets import QMessageBox

def send_request(request_data, parent_widget=None):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(("localhost", 9999))
            sock.send(json.dumps(request_data).encode("utf-8"))
            return json.loads(sock.recv(1024).decode("utf-8"))
    except Exception as e:
        if parent_widget:
            QMessageBox.critical(parent_widget, "Ошибка сервера", f"Не удалось подключиться:\n{e}")
        return None
    

def send_request_log(self, action, username, password):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(("localhost", 9999))
            request = {"action": action, "username": username, "password": password}
            sock.send(json.dumps(request).encode("utf-8"))
            response = json.loads(sock.recv(1024).decode("utf-8"))
            return response
    except Exception as e:
        QMessageBox.critical(self, "Ошибка", f"Не удаётся подключиться к серверу:\n{e}")
        return None