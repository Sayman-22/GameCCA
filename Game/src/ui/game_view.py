from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush, QFont, QPainter
from core.game_state import GameState
from ui.style import COSMIC_STYLE

class GameView(QGraphicsView):
####### ИНИЦИАЛИЗАЦИЯ ОКНА #######
    def __init__(self, game_state):
        super().__init__()
        self.game_state = game_state
        self.setStyleSheet(COSMIC_STYLE)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor("#0B0F1F")))
        
####### ИНИЦИАЛИЗАЦИЯ ОКНА #######



####### СОБЫТИЯ #######
    def startGame(self):
        self.game_state.generateInitialGrid()
        
        # Удаляем старый виджет (если есть) и создаём новый
        if hasattr(self, 'm_glWidget'):
            self.m_glWidget.setParent(None)  # отсоединяем от layout

        self.m_glWidget = GameView(self.game_state)
        self.layout().insertWidget(0, self.m_glWidget)

    def update_view(self):
        if self.game_state is None:
            return  # выходим, если состояние ещё не задано

        self.scene.clear()
        cell_size = 60

        # 👾 🛰️ 👽 🌚 🌍☄️🌠 🛰︎ 🦑 🔸 💥

        self.game_state.arena_next_move()

        # 1. Рисуем все ячейки
        for r in range(self.game_state.rows):
            for c in range(self.game_state.cols):
                if self.game_state.visibility[r][c]:
                    if self.game_state.use_masks and self.game_state.mask_grid[r][c]:
                        emoji = QGraphicsTextItem("?")
                        emoji.setBrush(QColor("#4A4A4A"))  # серый туман
                        emoji.setDefaultTextColor(Qt.white)
                        self.scene.addItem(emoji)
                    else:
                        self.update_all_cell(cell_size, r, c)
                else:
                    # Туман войны
                    fog = QGraphicsRectItem(c * cell_size, r * cell_size, cell_size, cell_size)
                    fog.setBrush(QColor("#305050"))  # чёрный туман
                    self.scene.addItem(fog)

            
        # 2. Рисуем игрока
        self.update_hero(cell_size)
        # 3. Текст с числом ячейки ПОД героем
        self.update_text_hero(cell_size)
        # 4. Отображаем "Старт"
        if not self.game_state.options.mode == "arena":
            self.update_start(cell_size)
        # 5. Отображаем "Финиш"
        if not self.game_state.options.mode == "arena":
            self.update_finish(cell_size)

        self.setSceneRect(0, 0, self.game_state.cols * cell_size, self.game_state.rows * cell_size)
        # self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

####### СОБЫТИЯ #######



####### ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ #######
    def get_color(self, value, pressure_tolerance):
        if value == GameState.START_FIN_CELL:
            return QBrush(QColor("#2A4B8C"))  # тёмно-синий (старт/финиш)
        if value == GameState.CRYSTAL:
            return QBrush(QColor("#6A4C93"))  # пурпурный (кристалл)
        if value == GameState.CRAFT:
            return QBrush(QColor("#B5651D"))  # медный (крафт)
        if value == GameState.EMPTY:
            return QBrush(QColor("#000000"))  # чёрная пустота
        if value in (1, 2, 4):
            return QBrush(QColor("#C07B3B"))  # тусклый оранжевый (цикл)
        if value > pressure_tolerance:
            return QBrush(QColor("#FF4444"))  # превышение допустимого давления
        if value % 2 == 0:
            return QBrush(QColor("#1A2332"))  # почти фон (чётные)
        else:
            return QBrush(QColor("#8B2E3C"))  # броский, но тёмный (нечётные)
        
    def update_all_cell(self, cell_size, r, c):
        pr, pc = self.game_state.player_pos
        value = self.game_state.grid[r][c]
        item = QGraphicsRectItem(c * cell_size, r * cell_size, cell_size, cell_size)
        item.setBrush(self.get_color(value, self.game_state.pressure_tolerance))
        self.scene.addItem(item)

        # Текст для обычных числовых ячеек (не спец.)
        if pr == r and pc == c:
            return
        
        if value == GameState.CRYSTAL:
            self.update_crystals_cell(cell_size, r, c)
        elif value == GameState.CRAFT:
            self.update_craft_cell(cell_size, r, c)
        elif value == GameState.START_FIN_CELL:
            # Старт/Финиш — уже отрисовываются отдельно, можно пропустить
            pass
        elif value == GameState.EMPTY:
            void_emoji = QGraphicsTextItem("⚫")
            void_emoji.setFont(QFont("Arial", 14, QFont.Bold))
            void_emoji.setDefaultTextColor(Qt.white)
            void_emoji.setPos(
                c * cell_size + cell_size / 2 - void_emoji.boundingRect().width() / 2,
                r * cell_size + cell_size / 2 - void_emoji.boundingRect().height() / 2
            )
            self.scene.addItem(void_emoji)
        elif value > self.game_state.pressure_tolerance and (r, c) != self.game_state.player_pos:   # не рисуем, если там герой
            self.update_pressure_tolerance(cell_size, value, r, c)
        elif value > 0 and (r, c) != self.game_state.player_pos:  # не рисуем, если там герой
            self.update_point_cell(cell_size, value, r, c)

    def update_pressure_tolerance(self, cell_size, value, r, c):
        emoji_text = QGraphicsTextItem("⏲️")
        emoji_text.setFont(QFont("Arial", 14, QFont.Bold))
        emoji_text.setDefaultTextColor(Qt.white)
        emoji_text.setPos(
            c * cell_size + cell_size / 2 - emoji_text.boundingRect().width() / 2,
            r * cell_size + cell_size / 2 - emoji_text.boundingRect().height() / 2
        )
        self.scene.addItem(emoji_text)

        # Число в правом верхнем углу
        num_item = QGraphicsTextItem(str(value))
        num_item.setFont(QFont("Arial", 7, QFont.Bold))
        num_item.setDefaultTextColor(Qt.white)
        num_item.setPos(
            c * cell_size + cell_size - num_item.boundingRect().width(),
            r * cell_size + 0
        )
        self.scene.addItem(num_item)

    def update_crystals_cell(self, cell_size, r, c):
        emoji = QGraphicsTextItem("💎")
        emoji.setFont(QFont("Arial", 14, QFont.Bold))
        emoji.setDefaultTextColor(Qt.white)
        emoji.setPos(
            c * cell_size + cell_size / 2 - emoji.boundingRect().width() / 2,
            r * cell_size + cell_size / 2 - emoji.boundingRect().height() / 2
        )
        self.scene.addItem(emoji)

    def update_craft_cell(self, cell_size, r, c):
        emoji = QGraphicsTextItem("⚒")
        emoji.setFont(QFont("Arial", 14, QFont.Bold))
        emoji.setDefaultTextColor(Qt.white)
        emoji.setPos(
            c * cell_size + cell_size / 2 - emoji.boundingRect().width() / 2,
            r * cell_size + cell_size / 2 - emoji.boundingRect().height() / 2
        )
        self.scene.addItem(emoji)

    def update_point_cell(self, cell_size, value, r, c):
        # Выбор эмодзи
        if value == 4:
            emoji = "🕳️"  # черная дыра для 4
        elif value % 2 == 0:
            emoji = "🌍"  # Земля для чётных
        else:
            emoji = "💥"  # Взрыв для нечётных

        # Рисуем эмодзи в центре
        emoji_text = QGraphicsTextItem(emoji)
        emoji_text.setFont(QFont("Arial", 14, QFont.Bold))
        emoji_text.setDefaultTextColor(Qt.white)
        emoji_text.setPos(
            c * cell_size + cell_size / 2 - emoji_text.boundingRect().width() / 2,
            r * cell_size + cell_size / 2 - emoji_text.boundingRect().height() / 2
        )
        self.scene.addItem(emoji_text)

        # Число в правом верхнем углу
        number_text = QGraphicsTextItem(str(value))
        number_text.setFont(QFont("Arial", 7, QFont.Bold))
        number_text.setDefaultTextColor(Qt.white)
        number_text.setPos(
            c * cell_size + cell_size - number_text.boundingRect().width(),
            r * cell_size + 0
        )
        self.scene.addItem(number_text)

    def update_hero(self, cell_size):
        pr, pc = self.game_state.player_pos
        player_text = QGraphicsTextItem("🛸")
        player_text.setFont(QFont("Arial", 14, QFont.Bold))
        player_text.setDefaultTextColor(Qt.white)
        player_text.setPos(
            pc * cell_size + cell_size / 2 - player_text.boundingRect().width() / 2,
            pr * cell_size + cell_size / 2 - player_text.boundingRect().height() / 2
        )
        self.scene.addItem(player_text)
        
    def update_text_hero(self, cell_size):
        pr, pc = self.game_state.player_pos
        hero_value = self.game_state.grid[pr][pc]
        if hero_value > 0:  # только для числовых ячеек
            hero_number = QGraphicsTextItem(str(hero_value))
            hero_number.setFont(QFont("Arial", 7, QFont.Bold))
            hero_number.setDefaultTextColor(Qt.white)
            # Позиция: справа вверху ячейки
            hero_number.setPos(
                pc * cell_size + cell_size - hero_number.boundingRect().width(),
                pr * cell_size + 0
            )
            self.scene.addItem(hero_number)

    def update_start(self, cell_size):
        start_r, start_c = self.game_state.start_pos
        if not self.game_state.visibility[start_r][start_c]:
            return
        start_r, start_c = self.game_state.start_pos
        start_label = QGraphicsTextItem("🚩")
        start_label.setFont(QFont("Arial", 10, QFont.Bold))
        start_label.setDefaultTextColor(Qt.white)
        start_label.setPos(
            start_c * cell_size - 0.1*cell_size,
            start_r * cell_size - 0.1*cell_size
        )
        self.scene.addItem(start_label)

    def update_finish(self, cell_size):
        end_r, end_c = self.game_state.end_pos
        if not self.game_state.visibility[end_r][end_c]:
            return
        end_label = QGraphicsTextItem("🏁")
        end_label.setFont(QFont("Arial", 10, QFont.Bold))
        end_label.setDefaultTextColor(Qt.white)
        end_label.setPos(
            end_c * cell_size - 0.1*cell_size,
            end_r * cell_size - 0.1*cell_size
        )
        self.scene.addItem(end_label)
####### ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ #######
