# ui/achievements_window.py

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWidgets import QLabel, QPushButton
from ui.style import COSMIC_STYLE

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
        defense = self.stats.get("defense", 1)
        skips = self.stats.get("max_skips", 2)
        freeze = self.stats.get("freeze", 0)
        max_undo = self.stats.get("max_undo", 0)
        pressure = self.stats.get("pressure_tolerance", 200)
        deaths = self.stats.get("deaths", 0)
        fog_radius = self.stats.get("fog_radius", 1)
        fog_remember = "Да" if self.stats.get("fog_remember", False) else "Нет"
        
        layout.addWidget(QLabel(f"❤️ Текущее количество жизней: {lives}"))
        layout.addWidget(QLabel(f"🛡️ Защита: {defense}"))
        layout.addWidget(QLabel(f"⏭️ Допустимых пропусков хода: {skips}"))
        layout.addWidget(QLabel(f"❄️ Заряды заморозки: {freeze}"))
        layout.addWidget(QLabel(f"↩️ Макс. откатов: {max_undo}"))
        layout.addWidget(QLabel(f"⏲️ Допустимое давление: {pressure}"))
        layout.addWidget(QLabel(f"💀 Всего смертей: {deaths}"))
        layout.addWidget(QLabel(f"👁️ Радиус видимости: {fog_radius}"))
        layout.addWidget(QLabel(f"🧠 Запоминать пройденное: {fog_remember}"))
        layout.addSpacing(20)

        crystals = self.stats.get("total_crystals_collected", 0)
        crafts = self.stats.get("total_craft_cells_used", 0)
        layout.addWidget(QLabel(f"💎 Всего кристаллов собрано: {crystals}"))
        layout.addWidget(QLabel(f"🛠️ Всего крафтовых ячеек использовано: {crafts}"))
        layout.addSpacing(20)

        # --- Прогресс ---
        max_difficulty = self.stats.get("max_difficulty", 0)
        random_wins = self.stats.get("random_wins", 0)
        campaign_wins = self.stats.get("last_completed_level", 0)
        black_hole_deaths = self.stats.get("deaths_from_black_hole", 0)

        layout.addWidget(QLabel(f"🏆 Макс. сложность: {max_difficulty}"))
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
