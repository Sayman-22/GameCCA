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
        self.layout().insertWidget(0, self.m_glWidget)  # или как у вас layout устроен

    def update_view(self):
        if self.game_state is None:
            return  # ← выходим, если состояние ещё не задано

        self.scene.clear()
        cell_size = 40
        pr, pc = self.game_state.player_pos

        # 👾 🛰️ 👽 🌚 🌍☄️🌠 🛰︎ 🦑 🔸 💥

        # 1. Рисуем все ячейки
        for r in range(self.game_state.rows):
            for c in range(self.game_state.cols):
                value = self.game_state.grid[r][c]
                item = QGraphicsRectItem(c * cell_size, r * cell_size, cell_size, cell_size)
                item.setBrush(self._get_color(value))
                self.scene.addItem(item)

                # Текст для обычных числовых ячеек (не спец.)
                if pr == r and pc == c:
                    continue
                # --- Отображение эмодзи и числа для числовых ячеек ---
                if value > 0 and (r, c) != self.game_state.player_pos:  # не рисуем, если там герой
                    # Выбор эмодзи
                    if value == 4:
                        emoji = "🕳️"  # черная дыра для 4
                    elif value % 2 == 0:
                        emoji = "🌍"  # Земля для чётных
                    else:
                        emoji = "💥"  # Взрыв для нечётных

                    # Рисуем эмодзи в центре
                    emoji_text = QGraphicsTextItem(emoji)
                    emoji_text.setFont(QFont("Arial", 16, QFont.Bold))
                    emoji_text.setDefaultTextColor(Qt.white)
                    emoji_text.setPos(
                        c * cell_size + cell_size / 2 - emoji_text.boundingRect().width() / 2,
                        r * cell_size + cell_size / 2 - emoji_text.boundingRect().height() / 2
                    )
                    self.scene.addItem(emoji_text)

                    # Число в правом верхнем углу
                    number_text = QGraphicsTextItem(str(value))
                    number_text.setFont(QFont("Arial", 4, QFont.Bold))
                    number_text.setDefaultTextColor(Qt.white)
                    number_text.setPos(
                        c * cell_size + cell_size - number_text.boundingRect().width(),
                        r * cell_size + 0
                    )
                    self.scene.addItem(number_text)

        # 2. Рисуем игрока
        player_text = QGraphicsTextItem("🛸")
        player_text.setFont(QFont("Arial", 16, QFont.Bold))
        player_text.setPos(
            pc * cell_size + cell_size / 2 - player_text.boundingRect().width() / 2,
            pr * cell_size + cell_size / 2 - player_text.boundingRect().height() / 2
        )
        self.scene.addItem(player_text)

        # 3. ➕ ДОБАВИТЬ: Текст с числом ячейки ПОД героем
        hero_value = self.game_state.grid[pr][pc]
        if hero_value > 0:  # только для числовых ячеек
            hero_number = QGraphicsTextItem(str(hero_value))
            hero_number.setFont(QFont("Arial", 4, QFont.Bold))
            # Позиция: справа вверху ячейки
            hero_number.setPos(
                pc * cell_size + cell_size - hero_number.boundingRect().width(),
                pr * cell_size + 0
            )
            self.scene.addItem(hero_number)

        # 4. Отображаем "С" и "Ф" на старте и финише
        start_r, start_c = self.game_state.start_pos
        end_r, end_c = self.game_state.end_pos

        # Старт
        start_label = QGraphicsTextItem("🚩")
        start_label.setFont(QFont("Arial", 7, QFont.Bold))
        start_label.setDefaultTextColor(Qt.white)
        start_label.setPos(
            start_c * cell_size - start_label.boundingRect().width() / 2 + 5,
            start_r * cell_size - cell_size / 2 + 13
            # start_c * cell_size + cell_size / 2 - start_label.boundingRect().width() / 2,
            # start_r * cell_size + cell_size / 2 - start_label.boundingRect().height() / 2
        )
        self.scene.addItem(start_label)

        # Финиш
        end_label = QGraphicsTextItem("🏁")
        end_label.setFont(QFont("Arial", 7, QFont.Bold))
        end_label.setDefaultTextColor(Qt.white)
        end_label.setPos(
            end_c * cell_size - cell_size / 2 + 15,
            end_r * cell_size - cell_size / 2 + 13
            # end_c * cell_size + cell_size / 2 - end_label.boundingRect().width() / 2,
            # end_r * cell_size + cell_size / 2 - end_label.boundingRect().height() / 2
        )
        self.scene.addItem(end_label)

        self.setSceneRect(0, 0, self.game_state.cols * cell_size, self.game_state.rows * cell_size)
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

####### СОБЫТИЯ #######



####### ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ #######
    def _get_color(self, value):
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
        if value % 2 == 0:
            return QBrush(QColor("#1A2332"))  # почти фон (чётные)
        else:
            return QBrush(QColor("#8B2E3C"))  # броский, но тёмный (нечётные)
        
####### ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ #######
