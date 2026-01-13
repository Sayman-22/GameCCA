# ui/game_window.py

from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QPushButton, QMessageBox
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGroupBox, QGridLayout
from PyQt5.QtWidgets import QStackedWidget
from PyQt5.QtCore import Qt
from ui.game_view import GameView
from ui.mask_view import MaskView
from ui.style import COSMIC_STYLE
from ui.network_client import send_request
from ui.local_ai_advisor import get_hint
from ui.game_hero_info import setWindowLegend
from ui.game_hero_info import GameHeroInfo

class GameWindow(QMainWindow):
    ghi = GameHeroInfo()

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
        self.mask_view = None
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("Лабиринт — Игра")
        self.resize(1300, 800)

        # Главный вертикальный макет
        bottom_layout = QHBoxLayout()
        main_layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #0F1426;")
        central_widget.setLayout(bottom_layout)
        self.setCentralWidget(central_widget)

        # Верхняя часть: Кнопка + Стек с полем
        top_bar_layout = QHBoxLayout()
        
        # Кнопка переключения режима (в левом верхнем углу)
        self.btn_toggle_mask = QPushButton("❓ Маски")
        self.btn_toggle_mask.clicked.connect(self.toggle_mask_mode)
        top_bar_layout.addWidget(self.btn_toggle_mask)
        top_bar_layout.addStretch()  # кнопка прижата к левому краю
        
        main_layout.addLayout(top_bar_layout)

        # --- Стек для переключения между полями ---
        self.stack = QStackedWidget()

        # Основное поле (GameView)
        self.m_glWidget = GameView(None)
        self.stack.addWidget(self.m_glWidget)  # index 0

        # Поле ввода для масок
        self.mask_view = MaskView(None)
        self.stack.addWidget(self.mask_view)  # index 1

        main_layout.addWidget(self.stack)

        # --- Правая панель управления ---
        right_panel = QWidget()
        right_panel.setFixedWidth(300)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(10)

        # HUD в две колонки
        self.ghi.createInfo(right_layout, 1)
        right_layout.addStretch()

        # Легенда
        setWindowLegend(right_layout)
        right_layout.addStretch()

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

        # Кнопки действий
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(5)

        self.m_btnNext = QPushButton("⏭️")
        self.btn_freeze = QPushButton("❄️")
        self.btn_undo = QPushButton("↩️")
        self.btn_hint = QPushButton("🤔")

        grid_move.addWidget(self.m_btnNext, 2, 1) 
        grid_move.addWidget(self.btn_freeze, 2, 0)
        grid_move.addWidget(self.btn_undo, 2, 2)
        grid_move.addWidget(self.btn_hint, 3, 1)

        # Подключение сигналов
        self.m_btnUp.clicked.connect(lambda: self.onMove(-1, 0))
        self.m_btnDown.clicked.connect(lambda: self.onMove(1, 0))
        self.m_btnLeft.clicked.connect(lambda: self.onMove(0, -1))
        self.m_btnRight.clicked.connect(lambda: self.onMove(0, 1))
        self.m_btnNext.clicked.connect(self.onNextStep)
        self.btn_freeze.clicked.connect(self.onFreeze)
        self.btn_undo.clicked.connect(self.onUndo)
        self.btn_hint.clicked.connect(self.on_hint_clicked)

        bottom_layout.addLayout(main_layout)
        bottom_layout.addWidget(right_panel, 1)
        # main_layout.addLayout(bottom_layout)

        # Информационная строка (самая нижняя)
        info_bar = QWidget()
        info_bar.setObjectName("infoBar")
        info_layout = QHBoxLayout(info_bar)
        self.m_infoLabel = QLabel("Готов к ходу")
        self.m_infoLabel.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.m_infoLabel)
        main_layout.addWidget(info_bar)
        
####### ИНИЦИАЛИЗАЦИЯ ОКНА #######



####### СОСТОЯНИЯ #######
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

            # Отправляем запрос на обновление сложности
            difficulty = self.m_gameState.calculate_difficulty()
            difficulty_request = {
                "action": "update_max_difficulty",
                "username": self.parent.username,
                "difficulty": difficulty
            }
            difficulty_response = send_request(difficulty_request, self)
            if difficulty_response and difficulty_response["status"] == "success":
                self.parent.stats = difficulty_response["stats"]

            QMessageBox.information(self, "Победа!", "Вы достигли финиша!\nСтатистика обновлена!")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось обновить статистику на сервере.")
        self.m_gameState.state_history.clear()

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
        self.m_gameState.state_history.clear()

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
        self.m_gameState.state_history.clear()
        
        QMessageBox.information(self, "Чёрная дыра", msg)
        self.return_to_main_menu()

    def handle_arena_defeat(self):
        score = self.m_gameState.rows_removed
        QMessageBox.information(self, "Арена завершена", f"Пройдено строк: {score}")
        self.m_gameState.state_history.clear()
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
            self.moveStep(0, 0)
            self.ghi.update_hud(self.m_gameState)
            self.m_infoLabel.setText("Ячейка заморожена на один ход!")
        else:
            self.m_infoLabel.setText("Нет зарядов заморозки!")

    def onUndo(self):
        if self.m_gameState.undo_move():
            self.m_glWidget.update_view()
            self.ghi.update_hud(self.m_gameState)
            self.m_infoLabel.setText("Ход отменён.")
        else:
            self.m_infoLabel.setText("Нет ходов для отмены.")
            
    def toggle_mask_mode(self):
        if self.stack.currentIndex() == 0:
            self.mask_view.game_state = self.m_gameState
            self.mask_view.parent_window = self
            self.mask_view.update_view()
            self.stack.setCurrentIndex(1)
            self.btn_toggle_mask.setText("← Назад к лабиринту")
        else:
            if hasattr(self.mask_view, 'active_line_edit') and self.mask_view.active_line_edit:
                self.mask_view.active_line_edit.deleteLater()
                self.mask_view.active_line_edit = None
            self.stack.setCurrentIndex(0)
            self.btn_toggle_mask.setText("❓ Маски")

    def on_mask_guess(self, line_edit, r, c):
        try:
            guess = int(line_edit.text())
        except ValueError:
            return

        result = self.m_gameState.check_mask_guess(r, c, guess)
        if result == "correct":
            line_edit.setStyleSheet("background-color: #2E7D32; color: white;")
            self.ghi.update_hud(self.m_gameState)
            QMessageBox.information(self, "Успех!", "Вы угадали число!\n+3 кристалла!")
        elif result == "wrong":
            line_edit.setStyleSheet("background-color: #C62828; color: white;")
            self.m_infoLabel.setText(f"Ошибка! Осталось попыток: {3 - self.m_gameState.mask_attempts}")
            self.ghi.update_hud(self.m_gameState)
        elif result == "game_over":
            self.handle_defeat()

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
        
        # Записываем историю
        self.m_gameState.write_history()
        # Выполняем шаг
        self.m_gameState.advance_step()
        # Производим ход в логике игры
        state = self.m_gameState.move_player(dy, dx)
        # Обновляем интерфейс
        self.m_glWidget.update_view()
        # Обновляем HUD
        self.ghi.update_hud(self.m_gameState)

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
            self.m_gameState.max_undo = stats.get("max_undo", 0)
            self.m_gameState.pressure_tolerance = stats.get("pressure_tolerance", 200)
            self.m_gameState.options.visibility_radius = stats.get("fog_radius", 1)
            self.m_gameState.options.remember_visibility = stats.get("fog_remember", False)
            self.m_gameState.defense = stats.get("defense", 1)
            self.m_gameState.freeze_cell = stats.get("freeze_cell", 0)

        self.m_gameState.state_history.clear()
        self.m_glWidget.game_state = self.m_gameState
        self.m_gameState.update_visibility()
        self.m_glWidget.update_view()
        self.ghi.update_hud(self.m_gameState)

        self.mask_view.game_state = self.m_gameState
        self.mask_view.update_view()

    def return_to_main_menu(self):
        """Возвращает в главное меню"""
        if self.parent is not None:
            self.parent.show_main_menu()
        self.close()

####### СОБЫТИЯ #######