# ui/main_menu.py

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtWidgets import QLabel, QDialog
from PyQt5.QtCore import Qt
from ui.style import COSMIC_STYLE

class MainMenuWindow(QMainWindow):
####### ИНИЦИАЛИЗАЦИЯ ОКНА #######
    def __init__(self, username, stats):
        super().__init__()
        self.username = username
        self.stats = stats

        self.setWindowTitle("Лабиринт — Главное меню")
        self.resize(400, 300)
        self.setStyleSheet(COSMIC_STYLE)
        self.init_ui()

        self.game_window = None  # ссылка на игровое окно
        self.statistics_window = None  # ссылка на окно достижений
        self.campaign_window = None # ссылка на окно кампании

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Титл
        title = QLabel(f"🎮 Привет, {self.username}!")
        title.setObjectName("MainMenuTitle")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Объяляем кнопки
        btn_random = QPushButton("🎲 Случайный уровень")
        btn_campaign = QPushButton("📜 Кампания")
        btn_achievements = QPushButton("🏆 Статистика")
        btn_settings = QPushButton("⚙️ Настройки")
        btn_exit = QPushButton("🚪 Выход")

        # Кнопки на компоновщик
        layout.addWidget(btn_random)
        layout.addWidget(btn_campaign)
        layout.addWidget(btn_achievements)
        layout.addWidget(btn_settings)
        layout.addWidget(btn_exit)

        # Подключаем сигналы
        btn_random.clicked.connect(self.start_random_level)
        btn_campaign.clicked.connect(self.show_campaign_map)
        btn_achievements.clicked.connect(self.show_statistics)
        btn_exit.clicked.connect(self.close)

####### ИНИЦИАЛИЗАЦИЯ ОКНА #######



####### СОБЫТИЯ #######
    def show_statistics(self):
        from ui.statistics_window import StatisticsWindow
        self.statistics_window = StatisticsWindow(
            username=self.username,
            stats=self.stats,
            parent=self
        )
        self.statistics_window.show()
        self.hide()

    def show_campaign_map(self):
        from ui.campaign_map_window import CampaignMapWindow
        self.campaign_window = CampaignMapWindow(parent=self, username=self.username)
        self.campaign_window.show()
        # self.hide()

    def start_random_level(self):
        from ui.settings_dialog_random_lab import SettingsDialoRandomLab
        dialog = SettingsDialoRandomLab(self)
        if dialog.exec_() == QDialog.Accepted:
            options = dialog.get_options()
            self.start_game_with_options(options)

    def start_game_with_options(self, options):
        from ui.game_window import GameWindow
        if self.game_window:
            self.game_window.close()
        self.game_window = GameWindow(username=self.username, parent=self, game_options=options, campaign=False, level_id=0)
        self.game_window.startGame()
        self.game_window.show()
        self.hide()

    def show_main_menu(self):
        """Метод для возврата в главное меню"""
        if self.game_window is not None:
            self.game_window.close()
            self.game_window = None
        if self.statistics_window is not None:
            self.statistics_window.close()
            self.statistics_window = None
        if self.campaign_window is not None:
            self.campaign_window.close()
            self.campaign_window = None
        self.show()

####### СОБЫТИЯ #######
