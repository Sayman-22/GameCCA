# ui/game_window.py

from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QPushButton, QMessageBox
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGroupBox, QGridLayout
from PyQt5.QtCore import Qt
from ui.game_view import GameView
from ui.style import COSMIC_STYLE
from ui.network_client import send_request
from ui.local_ai_advisor import get_hint

class GameWindow(QMainWindow):
####### ИНИЦИАЛИЗАЦИЯ ОКНА #######
    def __init__(self, username, parent=None, game_options=None, campaign=False, level_id=0):
        super().__init__(parent)
        self.username = username
        self.parent = parent
        self.setStyleSheet(COSMIC_STYLE)
        self.game_options = game_options
        self.campaign = campaign
        self.level_id = level_id
        self.m_gameState = None
        self.m_glWidget = None
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("Лабиринт — Игра")
        self.resize(1300, 800)  # немного выше, чтобы уместить всё

        # Главный вертикальный макет
        main_layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #0F1426;")
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # === Верхняя часть: Игровое поле + Правая панель ===
        top_layout = QHBoxLayout()

        # --- Игровое поле (слева) ---
        self.m_glWidget = GameView(None)
        top_layout.addWidget(self.m_glWidget, 3)

        # --- Правая панель управления (справа) ---
        right_panel = QWidget()
        right_panel.setFixedWidth(200)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(10)

        # HUD: Жизни, кристаллы, крафт (без m_infoLabel)
        self.m_lifeLabel = QLabel("❤️ Жизни: 2")
        self.m_defenseLabel = QLabel("🛡️ Защита: 1")
        self.m_skipLabel = QLabel("⏭️ Пропуски: 2")
        self.m_freezeLabel = QLabel(f"❄️ Заморозка: 0")
        self.m_pressureLabel = QLabel("⏲️ Давление: 200")
        self.m_crystalLabel = QLabel("💎 Кристаллы: 0")
        self.m_craftLabel = QLabel("🛠️ Крафт: 0")

        right_layout.addWidget(self.m_lifeLabel)
        right_layout.addWidget(self.m_defenseLabel)
        right_layout.addWidget(self.m_skipLabel)
        right_layout.addWidget(self.m_freezeLabel)
        right_layout.addWidget(self.m_pressureLabel)
        right_layout.addWidget(self.m_crystalLabel)
        right_layout.addWidget(self.m_craftLabel)
        right_layout.addStretch()

        # === Легенда цветов ===
        legend_group = QGroupBox("Легенда")
        legend_layout = QVBoxLayout(legend_group)

        # Создаём строки легенды
        legend_items = [
            ("#1A2332", "🌍 Чётное число"),
            ("#8B2E3C", "💥 Нечётное число"),
            ("#C07B3B", "🕳️ Цикл (1, 2, 4)"),
            ("#2A4B8C", "🔵 Старт / Финиш"),
            ("#FF4444", "⏲️ Давление"),
            ("#6A4C93", "💎 Кристалл"),
            ("#B5651D", "🛠️ Крафт"),
            ("#000000", "⬛ Пустота")
        ]

        for color_hex, text in legend_items:
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(5)

            # Квадратик цвета
            color_square = QLabel()
            color_square.setFixedSize(16, 16)
            color_square.setStyleSheet(f"background-color: {color_hex}; border: 1px solid #888;")

            # Текст
            label_text = QLabel(text)
            label_text.setStyleSheet("padding-left: 5px; color: #C0D0FF;")

            row_layout.addWidget(color_square)
            row_layout.addWidget(label_text)
            row_layout.addStretch()

            legend_layout.addWidget(row_widget)

        right_layout.addWidget(legend_group)

        # Управление
        move_group = QGroupBox("Управление")
        move_layout = QVBoxLayout(move_group)
        grid_move = QGridLayout()
        self.m_btnUp = QPushButton("↑")
        self.m_btnDown = QPushButton("↓")
        self.m_btnLeft = QPushButton("←")
        self.m_btnRight = QPushButton("→")
        grid_move.addWidget(self.m_btnUp, 0, 1)
        grid_move.addWidget(self.m_btnLeft, 1, 0)
        grid_move.addWidget(self.m_btnDown, 1, 1)
        grid_move.addWidget(self.m_btnRight, 1, 2)
        move_layout.addLayout(grid_move)
        right_layout.addWidget(move_group)
        
        # Следующий шаг
        self.m_btnNext = QPushButton("Следующий шаг")
        right_layout.addWidget(self.m_btnNext)

        # Заморозить
        self.btn_freeze = QPushButton("❄️ Заморозить")
        right_layout.addWidget(self.btn_freeze)

        # Помощь
        self.btn_hint = QPushButton("🤔 Помощь")
        right_layout.addWidget(self.btn_hint)

        # ---- Сигналы ----
        self.m_btnUp.clicked.connect(lambda: self.onMove(-1, 0))
        self.m_btnDown.clicked.connect(lambda: self.onMove(1, 0))
        self.m_btnLeft.clicked.connect(lambda: self.onMove(0, -1))
        self.m_btnRight.clicked.connect(lambda: self.onMove(0, 1))
        self.m_btnNext.clicked.connect(self.onNextStep)
        self.btn_freeze.clicked.connect(self.onFreeze)
        self.btn_hint.clicked.connect(self.on_hint_clicked)

        top_layout.addWidget(right_panel, 1)
        main_layout.addLayout(top_layout)

        # === Нижняя панель: Информационная строка (во всю ширину) ===
        info_bar = QWidget()
        info_bar.setObjectName("infoBar")
        info_layout = QHBoxLayout(info_bar)
        info_layout.setContentsMargins(0, 0, 0, 0)

        self.m_infoLabel = QLabel("Готов к ходу")
        self.m_infoLabel.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.m_infoLabel)
        main_layout.addWidget(info_bar)  # Добавляем в основной макет
        
####### ИНИЦИАЛИЗАЦИЯ ОКНА #######



####### СОСТОЯНИЯ #######
    def update_hud(self):
        """Обновляет все элементы HUD."""
        self.m_lifeLabel.setText(f"❤️ Жизни: {self.m_gameState.lives}")
        self.m_defenseLabel.setText(f"🛡️ Защита: {self.m_gameState.defense}")
        self.m_skipLabel.setText(f"⏭️ Пропуски: {self.m_gameState.max_skips}")
        self.m_freezeLabel.setText(f"❄️ Заморозка: {self.m_gameState.freeze_cell}")
        self.m_pressureLabel.setText(f"⏲️ Давление: {self.m_gameState.pressure_tolerance}")
        self.m_crystalLabel.setText(f"💎 Кристаллы: {self.m_gameState.crystals}")
        self.m_craftLabel.setText(f"🛠️ Крафт: {self.m_gameState.craftedCells}")

    def handle_victory(self):
        """Обработка победы."""
        if self.campaign:
            request = {
                "action": "update_campaign_level",
                "username": self.parent.username,
                "level_id": str(self.level_id)
            }
        else:
            request = {
                "action": "update_stats",
                "username": self.parent.username,
                "stat_type": "random_wins",
                "operation": "increment",
                "value": 1
            }
        response = send_request(request, self)
        if response and response["status"] == "success":
            self.parent.stats = response["stats"]
            QMessageBox.information(self, "Победа!", "Вы достигли финиша!\nСтатистика обновлена!")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось обновить статистику на сервере.")

    def handle_defeat(self):
        """Обработка проигрыша."""
        if hasattr(self.parent, 'username'):
            request = {"action": "record_death", "username": self.parent.username}
            response = send_request(request, self)
            if response and response["status"] == "success":
                self.parent.stats = response["stats"]
                msg = "Вы проиграли!\nСтатистика обновлена."
            else:
                msg = "Вы проиграли!\n(Не удалось обновить статистику)"
        else:
            msg = "Вы проиграли!"

        QMessageBox.information(self, "Проигрыш", msg)
        self.return_to_main_menu()

    def handle_black_hole_death(self):
        """Смерть от чёрной дыры."""
        if hasattr(self.parent, 'username'):
            request = {"action": "record_black_hole_death", "username": self.parent.username}
            response = send_request(request, self)
            if response and response["status"] == "success":
                self.parent.stats = response["stats"]
                msg = "Вы поглощены чёрной дырой!\nСтатистика обновлена."
            else:
                msg = "Вы поглощены чёрной дырой!"
        else:
            msg = "Вы поглощены чёрной дырой!"
        
        QMessageBox.information(self, "Чёрная дыра", msg)
        self.return_to_main_menu()

    def handle_arena_defeat(self):
        score = self.m_gameState.rows_removed
        QMessageBox.information(self, "Арена завершена", f"Пройдено строк: {score}")
        self.return_to_main_menu()

    def handle_message(self, state):
        if (state == 2):
            self.m_infoLabel.setText("💔 -1 жизнь.")
        elif (state == 1):
            self.m_infoLabel.setText("Повезло, играем дальше! 🔄 Поле обновлено")
        elif (state == -1):
            self.m_infoLabel.setText("Смерть!")
        
    def on_hint_clicked(self):
        if self.m_gameState:
            hint = get_hint(self.m_gameState)
            QMessageBox.information(self, "Совет помощника", hint)

    def onFreeze(self):
        if self.m_gameState.activate_freeze():
            self.update_hud()
            self.m_infoLabel.setText("Ячейка заморожена на один ход!")
            self.moveStep(0, 0)
        else:
            self.m_infoLabel.setText("Нет зарядов заморозки!")
            
####### СОСТОЯНИЯ #######




####### ПЕРЕМЕЩЕНИЕ ПО ПОЛЮ #######
    def onMove(self, dy, dx):
        self.moveStep(dy, dx)

    def onNextStep(self):
        if not self.m_gameState:
            self.m_infoLabel.setText("❌ Игра не запущена.")
            return

        if self.m_gameState.max_skips <= 0:
            self.m_infoLabel.setText("⚠️ Пропуски хода закончились!")
            self.m_btnNext.setEnabled(False)
            return

        self.m_gameState.max_skips -= 1
        self.moveStep(0, 0)

    def moveStep(self, dy, dx):
        r, c = self.m_gameState.player_pos
        nr, nc = r + dy, c + dx
        
        # Проверка валидности хода
        state_check = self.m_gameState.check_step(nr, nc)
        if not state_check:
            return
        
        # Выполняем шаг
        self.m_gameState.advance_step()
        # Производим ход в логике игры
        state = self.m_gameState.move_player(dy, dx)
        # Обновляем интерфейс
        self.m_glWidget.update_view()
        # Обновляем HUD
        self.update_hud()

        # Проверяем режим
        if self.m_gameState.options.mode == "arena":
            if self.m_gameState.lives <= 0:
                self.handle_arena_defeat()
        else:
            # Обычный режим
            if self.m_gameState and state > 0:
                # Проверяем победу
                if self.m_gameState.player_pos == self.m_gameState.end_pos:
                    self.handle_victory()
                    # Возврат в главное меню ПОСЛЕ закрытия сообщения
                    self.return_to_main_menu()
            else:
                # Если ход неудачный — проигрыш
                if state == -3:
                    self.handle_black_hole_death()
                else:
                    self.handle_defeat()
                # Возврат в главное меню ПОСЛЕ закрытия сообщения
                self.return_to_main_menu()
            self.handle_message(state)

####### ПЕРЕМЕЩЕНИЕ ПО ПОЛЮ #######





####### СОБЫТИЯ #######
    def startGame(self, predefined_state=None):
        """
        Запускает игру.
        Если передан predefined_state — использует его.
        Иначе — создаёт случайный уровень из game_options.
        """
        if predefined_state is not None:
            self.m_gameState = predefined_state
        else:
            from core.game_state import GameState
            self.m_gameState = GameState(
                username=self.username,
                rows=self.game_options.rows,
                cols=self.game_options.cols,
                options=self.game_options
            )
            self.m_gameState.generate_initial_grid()
        
        if hasattr(self.parent, 'stats'):
            stats = self.parent.stats

            if not self.m_gameState.options.hardcore:
                self.m_gameState.lives = stats.get("lives", 2)

            self.m_gameState.max_skips = stats.get("max_skips", 2)
            self.m_gameState.pressure_tolerance = stats.get("pressure_tolerance", 200)
            self.m_gameState.options.visibility_radius = stats.get("fog_radius", 1)
            self.m_gameState.options.remember_visibility = stats.get("fog_remember", False)
            self.m_gameState.defense = stats.get("defense", 1)
            self.m_gameState.freeze_cell = stats.get("freeze_cell", 0)

        self.m_glWidget.game_state = self.m_gameState
        self.m_gameState.update_visibility()
        self.m_glWidget.update_view()
        self.update_hud()

    def return_to_main_menu(self):
        """Возвращает в главное меню"""
        if self.parent is not None:
            self.parent.show_main_menu()
        self.close()

####### СОБЫТИЯ #######