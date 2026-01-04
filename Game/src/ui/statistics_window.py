# ui/achievements_window.py

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWidgets import QLabel, QPushButton, QMessageBox
from ui.style import COSMIC_STYLE
from ui.network_client import send_request

import socket
import json

class StatisticsWindow(QMainWindow):
    def __init__(self, username, stats, parent=None):
        super().__init__(parent)
        self.username = username
        self.stats = stats
        self.parent_window = parent
        self.setStyleSheet(COSMIC_STYLE)
        self.setWindowTitle("🏆 Статистика")
        self.resize(400, 300)
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        title = QLabel(f"🏆 Ваша статистика: {self.username}")
        title.setObjectName("MainMenuTitle")
        layout.addWidget(title)

        

        # --- Текущие ресурсы ---
        lives = self.stats.get("lives", 2)
        skips = self.stats.get("max_skips", 2)
        deaths = self.stats.get("deaths", 0)
        layout.addWidget(QLabel(f"❤️ Текущее количество жизней: {lives}"))
        layout.addWidget(QLabel(f"⏭️ Допустимых пропусков хода: {skips}"))
        layout.addWidget(QLabel(f"💀 Всего смертей: {deaths}"))
        layout.addSpacing(20)

        crystals = self.stats.get("total_crystals_collected", 0)
        crafts = self.stats.get("total_craft_cells_used", 0)
        layout.addWidget(QLabel(f"💎 Всего кристаллов собрано: {crystals}"))
        layout.addWidget(QLabel(f"🛠️ Всего крафтовых ячеек использовано: {crafts}"))
        layout.addSpacing(20)

        # --- Прогресс ---
        random_wins = self.stats.get("random_wins", 0)
        campaign_wins = self.stats.get("last_completed_level", 0)
        black_hole_deaths = self.stats.get("deaths_from_black_hole", 0)

        layout.addWidget(QLabel(f"🎲 Пройдено случайных лабиринтов: {random_wins}"))
        layout.addWidget(QLabel(f"📜 Пройдено уровней в кампании: {campaign_wins}"))
        layout.addWidget(QLabel(f"🕳️ Смертей от черных дыр: {black_hole_deaths}"))
        layout.addSpacing(20)
        layout.addStretch()

        btn_back = QPushButton("← Назад в меню")
        btn_back.clicked.connect(self.go_back)
        layout.addWidget(btn_back)





        # # Отображение статистики
        # player_label = QLabel(f"Игрок: {self.username}")

        # # Инициализация состояний
        # random_wins = self.stats.get("random_wins", 0)
        # last_completed = self.stats.get("last_completed_level", 0)
        # deaths = self.stats.get("deaths", 0)
        # black_hole_deaths = self.stats.get("deaths_from_black_hole", 0)
        # crystals = self.stats.get("crystals", 0)
        # crafts = self.stats.get("craft_cells", 0)

        # # Создание лейблов
        # wins_label = QLabel(f"Пройдено случайных лабиринтов: {random_wins}")
        # campaign_label = QLabel(f"Пройдено уровней в кампании: {last_completed}")
        # deaths_label = QLabel(f"Смертей: {deaths}")
        # bh_label = QLabel(f"Поглощено чёрными дырами: {black_hole_deaths}")
        # crystals_label = QLabel(f"Всего кристаллов собрано: {crystals}")
        # crafts_label = QLabel(f"Всего крафтовых ячеек использовано: {crafts}")
        
        # # Запрашиваем актуальную статистику с сервера
        # response = send_request({"action": "get_stats", "username": self.username}, self)
        # if response and response["status"] == "success":
        #     self.stats = response["stats"]

        #     random_wins = self.stats.get("random_wins", 0)
        #     wins_label.setText(f"Пройдено случайных лабиринтов: {random_wins}")

        #     last_completed = self.stats.get("last_completed_level", 0)
        #     campaign_label.setText(f"Пройдено уровней в кампании: {last_completed}")
            
        #     deaths = self.stats.get("deaths", 0)
        #     deaths_label.setText(f"Смертей: {deaths}")
            
        #     black_hole_deaths = self.stats.get("deaths_from_black_hole", 0)
        #     bh_label.setText(f"Поглощено чёрными дырами: {black_hole_deaths}")
            
        #     crystals = self.stats.get("crystals", 0)
        #     crystals_label.setText(f"Всего кристаллов собрано: {crystals}")

        #     crafts = self.stats.get("craft_cells", 0)
        #     crafts_label.setText(f"Всего крафтовых ячеек использовано: {crafts}")

        # # Добавление лейблов на компоновщик
        # layout.addWidget(player_label)
        # layout.addWidget(wins_label)
        # layout.addWidget(campaign_label)
        # layout.addWidget(deaths_label)
        # layout.addWidget(bh_label)
        # layout.addWidget(crystals_label)
        # layout.addWidget(crafts_label)
        # layout.addStretch()

        # # Кнопка "Назад"
        # btn_back = QPushButton("← Назад в меню")
        # btn_back.clicked.connect(self.go_back)
        # layout.addWidget(btn_back)

    def go_back(self):
        """Возврат в главное меню"""
        if self.parent_window:
            self.parent_window.show()
        self.close()
