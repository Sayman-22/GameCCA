# ui/main_menu.py
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTextEdit
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import Qt
from ui.style import COSMIC_STYLE
from ui.main_menu_view import MainMenuView
from ui.game_window import GameWindow

class MainMenuWindow(QMainWindow):
    def __init__(self, username, stats):
        super().__init__()
        self.username = username
        self.stats = stats
        self.setWindowTitle("Лабиринт — Главное меню")
        self.resize(800, 700)
        self.setStyleSheet(COSMIC_STYLE)
        self.init_ui()
        self.game_window = None
        self.statistics_window = None
        self.campaign_window = None

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Игровое поле ---
        self.menu_view = MainMenuView(parent=self)
        main_layout.addWidget(self.menu_view)

        # --- Поле описания ---
        self.desc_label = QTextEdit()
        self.desc_label.setReadOnly(True)
        self.desc_label.setMaximumHeight(80)
        self.desc_label.setStyleSheet("background-color: #1A1A1A; color: #C0D0FF; padding: 5px;")
        main_layout.addWidget(self.desc_label)

        # Подключение сигналов
        self.menu_view.scene.mousePressEvent = self.on_mouse_click

    def on_mouse_click(self, event):
        """Обрабатывает клик по полю."""
        pos = event.pos()
        col = pos.x() // self.menu_view.cell_size
        row = pos.y() // self.menu_view.cell_size
        pos_key = (row, col)

        if event.button() == Qt.LeftButton:
            action = self.menu_view.get_action_at(pos_key)
            if action:
                self.handle_action(action["action"])
        elif event.button() == Qt.RightButton:
            action = self.menu_view.get_action_at(pos_key)
            if action:
                self.desc_label.setText(action["desc"])
            else:
                self.desc_label.setText("Это пустота. Здесь ничего нет.")

    def handle_action(self, action_name):
        """Выполняет действие по имени."""
        from ui.game_window import GameWindow
        from ui.campaign_map_window import CampaignMapWindow
        from ui.statistics_window import StatisticsWindow
        from ui.settings_dialog_random_lab import SettingsDialoRandomLab

        if action_name == "campaign":
            self.campaign_window = CampaignMapWindow(parent=self, username=self.username)
            self.campaign_window.show()
            self.hide()
        elif action_name == "arena":
            from ui.arena_settings_dialog import ArenaSettingsDialog
            dialog = ArenaSettingsDialog(self, default_stats=self.stats)
            self.hide()
            if dialog.exec_() == QDialog.Accepted:
                options = dialog.get_options()
                self.start_game_with_options(options)
            else:
                self.show()
        elif action_name == "random":
            from ui.settings_dialog_random_lab import SettingsDialoRandomLab
            dialog = SettingsDialoRandomLab(self)
            self.hide()
            if dialog.exec_() == QDialog.Accepted:
                options = dialog.get_options()
                self.start_game_with_options(options)
            else:
                self.show()
        elif action_name == "statistics":
            self.statistics_window = StatisticsWindow(username=self.username, stats=self.stats, parent=self)
            self.statistics_window.show()
            self.hide()
        elif action_name == "settings":
            dialog = SettingsDialoRandomLab(self)
            if dialog.exec_() == QDialog.Accepted:
                pass  # настройки сохранены
        elif action_name == "exit":
            self.close()
        elif action_name == "finish":
            QMessageBox.information(self, "Победа!", "Вы достигли финиша главного меню!")
            # Можно добавить анимацию или переход в другое состояние

    def start_game_with_options(self, options):
        if self.game_window:
            self.game_window.close()
        self.game_window = GameWindow(username=self.username, parent=self, game_options=options, campaign=False, level_id=0)
        self.game_window.startGame()
        self.game_window.show()
        self.hide()

    def show_main_menu(self):
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