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

    def go_back(self):
        """Возврат в главное меню"""
        if self.parent_window:
            self.parent_window.show()
        self.close()
