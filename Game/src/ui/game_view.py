from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush, QFont, QPainter
from core.game_state import GameState
from ui.style import COSMIC_STYLE
from core.update_cell import CellStyle

class GameView(QGraphicsView):
####### ИНИЦИАЛИЗАЦИЯ ОКНА #######
    def __init__(self, game_state):
        super().__init__()
        self.game_state = game_state
        self.setStyleSheet(COSMIC_STYLE)
        self.scene = QGraphicsScene()
        self.cellStyle = CellStyle()
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
                        self.cellStyle.updateColorCell(self.scene, cell_size, c, r, "#4A4A4A")
                        self.cellStyle.updateObjectCell(self.scene, r, c, cell_size, "?")
                    else:
                        self.update_all_cell(cell_size, r, c)
                else:# Туман войны
                    self.cellStyle.updateColorCell(self.scene, cell_size, c, r, "#305050")

        # 2. Рисуем игрока
        self.cellStyle.updateObjectCell(self.scene, self.game_state.player_pos[0], self.game_state.player_pos[1], cell_size, "🛸")
        # 3. Текст с числом ячейки ПОД героем
        self.update_text_hero(cell_size)
        # 4. Отображаем "Старт"
        if not self.game_state.options.mode == "arena":
            self.update_start(cell_size)
        # 5. Отображаем "Финиш"
        if not self.game_state.options.mode == "arena":
            self.update_finish(cell_size)

        self.setSceneRect(0, 0, self.game_state.cols * cell_size, self.game_state.rows * cell_size)

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
        
        emoji = ""
        if value == GameState.CRYSTAL:
            self.cellStyle.updateObjectCell(self.scene, r, c, cell_size, "💎")
        elif value == GameState.CRAFT:
            self.cellStyle.updateObjectCell(self.scene, r, c, cell_size, "⚒")
        elif value == GameState.START_FIN_CELL:
            pass
        elif value == GameState.EMPTY:
            self.cellStyle.updateObjectCell(self.scene, r, c, cell_size, "⚫")
        elif value > self.game_state.pressure_tolerance and (r, c) != self.game_state.player_pos:   # не рисуем, если там герой
            self.cellStyle.updateObjectCell(self.scene, r, c, cell_size, "⏲️")
            # Число в правом верхнем углу
            self.cellStyle.updateDigitalCell(self.scene, r, c, cell_size, str(value))
        elif value > 0 and (r, c) != self.game_state.player_pos:  # не рисуем, если там герой
            emoji = self.update_point_cell(cell_size, value, r, c)

    def update_point_cell(self, cell_size, value, r, c):
        # Выбор эмодзи
        if value == 4:# черная дыра для 4
            self.cellStyle.updateObjectCell(self.scene, r, c, cell_size, "🕳️")
        elif value % 2 == 0:# Земля для чётных
            self.cellStyle.updateTextureCell(self.scene, r, c, cell_size, self.game_state.getNamePlanet(r, c))
        else:# Взрыв для нечётных
            self.cellStyle.updateObjectCell(self.scene, r, c, cell_size, "💥")

        # Число в правом верхнем углу
        self.cellStyle.updateDigitalCell(self.scene, r, c, cell_size, str(value))
        
    def update_text_hero(self, cell_size):
        pr, pc = self.game_state.player_pos
        hero_value = self.game_state.grid[pr][pc]
        if hero_value > 0:  # только для числовых ячеек
            self.cellStyle.updateDigitalCell(self.scene, pr, pc, cell_size, str(hero_value))

    def update_start(self, cell_size):
        r, c = self.game_state.start_pos
        self.cellStyle.updateLeftCell(self.scene, self.game_state.visibility, r, c, cell_size, "🚩")

    def update_finish(self, cell_size):
        r, c = self.game_state.end_pos
        self.cellStyle.updateLeftCell(self.scene, self.game_state.visibility, r, c, cell_size, "🏁")

####### ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ #######
