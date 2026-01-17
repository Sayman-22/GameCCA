from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QBrush, QPainter
from ui.game_hero_info import GameHeroInfo
from ui.style import COSMIC_STYLE
from core.update_cell import CellStyle
from core.state_cell import StateCell

class GameView(QGraphicsView):
    ghi = GameHeroInfo()

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
        mask_grid = self.game_state.getMaskGrid()
        for r in range(self.game_state.getRows()):
            for c in range(self.game_state.getCols()):
                if self.game_state.visibility[r][c]:
                    if self.game_state.getParUseMasks() and mask_grid[r][c]:
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

        # Если герой получил урон — мерцаем красным
        if getattr(self.game_state, 'just_damaged', True):
            overlay = QGraphicsRectItem(self.game_state.player_pos[1] * cell_size, self.game_state.player_pos[0] * cell_size, cell_size, cell_size)
            overlay.setBrush(QColor(255, 0, 0, 255))  # полупрозрачный красный
            self.scene.addItem(overlay)
            QTimer.singleShot(100, lambda: setattr(self.game_state, 'just_damaged', False))
            QTimer.singleShot(200, lambda: self.update_view())

        self.setSceneRect(0, 0, self.game_state.getCols() * cell_size, self.game_state.getRows() * cell_size)

####### СОБЫТИЯ #######



####### ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ #######
    def update_all_cell(self, cell_size, r, c):
        pr, pc = self.game_state.player_pos
        value = self.game_state.grid[r][c]
        item = QGraphicsRectItem(c * cell_size, r * cell_size, cell_size, cell_size)
        item.setBrush(self.ghi.get_color_cell(value, self.game_state.pressure_tolerance))
        self.scene.addItem(item)

        # Текст для обычных числовых ячеек (не спец.)
        if pr == r and pc == c:
            return
        
        if value == StateCell.CRYSTAL:
            self.cellStyle.updateObjectCell(self.scene, r, c, cell_size, "💎")
        elif value == StateCell.CRAFT:
            self.cellStyle.updateObjectCell(self.scene, r, c, cell_size, "⚒")
        elif value == StateCell.ENEMY_EASY_STATIC:
            self.cellStyle.updateTextureCell(self.scene, r, c, cell_size, "ALIEN1.png")
        elif value == StateCell.START_FIN_CELL:
            pass
        elif value == StateCell.EMPTY:
            self.cellStyle.updateObjectCell(self.scene, r, c, cell_size, "⚫")
        elif value > self.game_state.pressure_tolerance and (r, c) != self.game_state.player_pos:   # не рисуем, если там герой
            self.cellStyle.updateObjectCell(self.scene, r, c, cell_size, "⏲️")
            # Число в правом верхнем углу
            self.cellStyle.updateDigitalCell(self.scene, r, c, cell_size, str(value))
        elif value > 0 and (r, c) != self.game_state.player_pos:  # не рисуем, если там герой
            self.update_point_cell(cell_size, value, r, c)

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
        r, c = self.game_state.getStartPos()
        self.cellStyle.updateLeftCell(self.scene, self.game_state.visibility, r, c, cell_size, "🚩")

    def update_finish(self, cell_size):
        r, c = self.game_state.getEndPos()
        self.cellStyle.updateLeftCell(self.scene, self.game_state.visibility, r, c, cell_size, "🏁")

####### ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ #######
