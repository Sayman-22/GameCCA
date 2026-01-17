# ui/network_client.py

import socket, json
from PyQt5.QtWidgets import QMessageBox

class RequestForServer:
    def prepare_update_stats(self, username, parametr, action, value):
        request = {
            "action": "update_stats",
            "username": username,
            "stat_type": parametr,
            "operation": action,
            "value": value
        }
        return request
    
    def prepare_update_campaign_level(self, username, level_id):
        request = {
            "action": "update_campaign_level",
            "username": username,
            "level_id": str(level_id)
        }
        return request
    
    def prepare_update_max_difficulty(self, username, difficulty):
        request = {
            "action": "update_max_difficulty",
            "username": username,
            "difficulty": difficulty
        }
        return request
    
    def prepare_get_stats(self, username):
        request = {
            "action": "get_stats",
            "username": username
        }
        return request
        
    def send_request(self, request_data, parent_widget=None):
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