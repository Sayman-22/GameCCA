# ui/campaign_map_window.py

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QScrollArea, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ui.network_client import send_request

class CampaignMapWindow(QMainWindow):
    def __init__(self, parent=None, username=None):
        super().__init__(parent)
        self.parent_window = parent
        self.username = username
        self.setWindowTitle("🌌 Карта кампании")
        self.resize(800, 600)
        self.setStyleSheet("background-color: #0B0F1F; color: #C0D0FF;")

        request = {"action": "get_stats", "username": self.username}
        response = send_request(request, self)
        if response and response["status"] == "success":
            self.stats = response["stats"]
        else:
            self.stats = {"campaign_levels": {}}

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        title = QLabel("🌌 Галактическая карта уровней")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Создаём "галактику" из уровней
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        level_container = QWidget()
        level_layout = QHBoxLayout(level_container)
        level_layout.setAlignment(Qt.AlignCenter)
        level_layout.setSpacing(40)

        scroll.setWidget(level_container)
        layout.addWidget(scroll)

        # Кнопка назад
        btn_back = QPushButton("← Назад в меню")
        btn_back.clicked.connect(self.go_back)
        layout.addWidget(btn_back)

        # Определяем статусы уровней
        last_completed = self.stats.get("last_completed_level", 0)
        levels_data = []

        for lvl_id in range(1, 6):  # Уровни 1-5
            if lvl_id <= last_completed:
                status = "completed"
            elif lvl_id == last_completed + 1:
                status = "available"
            else:
                status = "locked"

            levels_data.append({"id": lvl_id, "status": status, "difficulty": min(lvl_id, 3)})

        # Создаём кнопки
        for lvl in levels_data:
            btn = self.create_level_button(lvl)
            if lvl["status"] != "locked":
                btn.clicked.connect(lambda _, lid=lvl["id"]: self.start_level(lid))
            level_layout.addWidget(btn)





    def create_level_button(self, level):
        btn = QPushButton()
        btn.setFixedSize(100, 100)

        if level["status"] == "locked": #  заблокирован
            btn.setStyleSheet("background-color: #4A5B7C; border-radius: 50px; color: #8090B0;")
            btn.setText("🔒\nLVL " + str(level["id"]))
            btn.setEnabled(False)
        elif level["status"] == "completed": # выполнен
            btn.setStyleSheet("background-color: #FFD700; border-radius: 50px; color: #000000;")
            btn.setText("🏆\nLVL " + str(level["id"]))
        else:  # доступен
            btn.setStyleSheet("background-color: #2A4B8C; border: 2px solid #6ACAFE; border-radius: 50px; color: #FFFFFF;")
            btn.setText("🚀\nLVL " + str(level["id"]))

        return btn

    def go_back(self):
        if self.parent_window:
            self.parent_window.show()
        self.close()

    def start_level(self, level_idd):
        """Запускает указанный уровень."""
        from core.campaign_levels import get_level_1
        from ui.game_window import GameWindow

        if level_idd == 1:
            level_state = get_level_1()
        # elif level_id == 2:
        #     level_state = get_level_2()
        else:
            return

        # Создаём игровое окно
        self.game_window = GameWindow(parent=self.parent_window, campaign=True, level_id=level_idd)
        self.game_window.show()
        self.game_window.startGame(predefined_state=level_state)
        self.parent_window.hide() 
        self.hide()