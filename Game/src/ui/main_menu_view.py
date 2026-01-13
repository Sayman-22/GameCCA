# ui/main_menu_view.py
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush, QPainter
from core.game_state import GameState
from core.update_cell import CellStyle

class MainMenuView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setStyleSheet("background-color: #0B0F1F;")
        self.scene = QGraphicsScene()
        self.cellStyle = CellStyle()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor("#0B0F1F")))
        self.rows = 15
        self.cols = 20
        self.cell_size = 40
        self.player_pos = (7, 9)  # старт
        self.finish_pos = (10, 8) # финиш на стене
        self.actions = {}
        self.setup_scene()

    def setup_scene(self):
        """Инициализирует поле."""

        sf = GameState.START_FIN_CELL
        ee = GameState.EMPTY
        cc = GameState.CASTLE
        ww = GameState.WALL
        ca = GameState.CAMPAIGN_CELL
        ar = GameState.ARENA_CELL
        ra = GameState.RANDOM_CELL
        st = GameState.STATISTICS_CELL
        se = GameState.SETTINGS_CELL
        ec = GameState.END_CELL
        sc = GameState.START_CELL
        bh = GameState.BLACK_HOLE_CELL
        gs = GameState.GOOD_SYSTEM_CELL
        bs = GameState.BAD_SYSTEM_CELL
        mc = GameState.MASK_CELL
        fc = GameState.FOG_CELL
        # Фиксированная сетка для обучения
        fixed_grid = [
            [ee, ee, ee, ee, ee, ee, ee, ee, ee, ww, ee, ee, ee, ee, ee, ee, ee, ee, ee, ee],# 1
            [ee, gs, ee, mc, ee, ee, ee, ee, ww, ww, ww, ee, ee, ee, ee, ee, ee, ee, ee, gs],# 2
            [ee, ee, ee, ee, ee, ee, ee, ww, ww, ww, ww, ww, ee, ee, ee, ee, gs, ee, ee, ee],# 3
            [ee, ee, ee, ee, ee, bh, ww, ww, ww, ww, ww, ww, ww, bh, ee, ee, ee, ee, ee, ee],# 4
            [ee, ee, ee, ee, bh, ww, ww, ww, ww, ww, ww, ww, ww, ww, bh, ee, ee, ee, mc, ee],# 5
            [ee, ee, ee, ee, ww, ww, ca, cc, cc, cc, cc, cc, ra, ww, ww, ww, ww, ww, ee, ee],# 6
            [ee, ee, ee, ww, ww, ww, cc, cc, cc, cc, cc, cc, cc, ww, ww, ww, ww, ww, ee, ee],# 7
            [ee, ee, ww, ww, ww, ww, cc, cc, cc, sc, cc, cc, cc, ww, se, st, ww, ww, ee, ee],# 8
            [ee, ee, ee, ww, ww, ww, cc, cc, cc, cc, cc, cc, cc, ww, ww, ww, ww, ww, ee, ee],# 9
            [ee, ee, ee, ee, ww, ec, cc, cc, cc, cc, cc, cc, ar, ww, ww, ww, ww, ww, ee, ee],# 10
            [ee, ee, ee, ee, ee, ec, ec, ww, ww, ww, ww, ww, ww, ww, bh, ee, ee, ee, ee, ee],# 11
            [ee, ee, ee, ee, ee, ee, ww, ww, ww, ww, ww, ww, ww, bh, ee, ee, fc, fc, fc, fc],# 12
            [ee, bs, ee, ee, ee, ee, ee, ww, ww, ww, ww, ww, ee, ee, ee, fc, fc, fc, bs, fc],# 13
            [ee, ee, ee, ee, ee, ee, ee, ee, ww, ww, ww, ee, ee, ee, fc, gs, fc, fc, fc, ee],# 14
            [bs, ee, bs, ee, ee, ee, ee, ee, ee, ww, ee, ee, ee, ee, fc, fc, fc, fc, ee, ee]# 15
            # 1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20 
        ]

        # Заполняем пустотой
        par = {"name": "Пустота", "action": "void", "desc": "Здесь нет ничего интересного"}
        self.cellStyle.updateTexture(self.scene, fixed_grid, self.rows, self.cols, self.cell_size, self.actions, par,
                                     GameState.EMPTY, "void.png")
        
        # Рисуем иконку с финишем
        par = {"name": "Выход", "action": "exit", "desc": "🏁 Закройте игру"}
        self.cellStyle.updateTexture(self.scene, fixed_grid, self.rows, self.cols, self.cell_size, self.actions, par,
                                     GameState.END_CELL, "🏁")
        
        # Заполняем черные дыры
        par = {"name": "Черная дыра", "action": "black_hole", "desc": "Черная дыра - смерть, ждущая путников"}
        self.cellStyle.updateTexture(self.scene, fixed_grid, self.rows, self.cols, self.cell_size, self.actions, par,
                                     GameState.BLACK_HOLE_CELL, "🕳️")
        
        # Заполняем обитаемые системы
        par = {"name": "Обитаемые системы", "action": "good_system", "desc": "Обитаемые системы"}
        self.cellStyle.updateTexture(self.scene, fixed_grid, self.rows, self.cols, self.cell_size, self.actions, par,
                                     GameState.GOOD_SYSTEM_CELL, "🌍")
        
        # Заполняем ytобитаемые системы
        par = {"name": "Необитаемые системы", "action": "bad_system", "desc": "Необитаемые системы"}
        self.cellStyle.updateTexture(self.scene, fixed_grid, self.rows, self.cols, self.cell_size, self.actions, par,
                                     GameState.BAD_SYSTEM_CELL, "💥")

        # Ячейка - маска
        par = {"name": "Маска", "action": "mask_cell", "desc": "?   Ячейка - маска"}
        self.cellStyle.updateTexture(self.scene, fixed_grid, self.rows, self.cols, self.cell_size, self.actions, par,
                                     GameState.MASK_CELL, "?")
        
        # Туман войны
        for r in range(self.rows):
            for c in range(self.cols):
                if GameState.FOG_CELL == fixed_grid[r][c]:
                    self.cellStyle.updateColorCell(self.scene, self.cell_size, c, r, "#305050")

        # Рисуем замок
        par = {"name": "Замок", "action": "castle_cell", "desc": "Это пространство замка"}
        self.cellStyle.updateTexture(self.scene, fixed_grid, self.rows, self.cols, self.cell_size, self.actions, par,
                                     GameState.CASTLE, "wall_texture.png")

        # Рисуем стену
        par = {"name": "Стена", "action": "wall_cell", "desc": "Это стена"}
        self.cellStyle.updateTexture(self.scene, fixed_grid, self.rows, self.cols, self.cell_size, self.actions, par,
                                     GameState.WALL, "wall_texture_2.png")

        # Рисуем иконку кампании
        cc = self.cellStyle.updateObject(self.scene, fixed_grid, self.rows, self.cols, self.cell_size,
                                         GameState.CAMPAIGN_CELL, "📜")
        self.actions[(cc.row, cc.col)] = {"name": "Кампания", "action": "campaign", "desc": "📜 Пройдите уровни кампании"}

        # Рисуем иконку арены
        cc = self.cellStyle.updateObject(self.scene, fixed_grid, self.rows, self.cols, self.cell_size,
                                         GameState.ARENA_CELL, "⚔️")
        self.actions[(cc.row, cc.col)] = {"name": "Арена", "action": "arena", "desc": "⚔️ Испытайте себя в арене"}

        # Рисуем иконку случайного лабиринта
        cc = self.cellStyle.updateObject(self.scene, fixed_grid, self.rows, self.cols, self.cell_size,
                                         GameState.RANDOM_CELL, "🎲")
        self.actions[(cc.row, cc.col)] = {"name": "Случайный уровень", "action": "random", "desc": "🎲 Начните случайный лабиринт"}

        # Рисуем иконку окна со статистикой
        cc = self.cellStyle.updateObject(self.scene, fixed_grid, self.rows, self.cols, self.cell_size,
                                         GameState.STATISTICS_CELL, "📊")
        self.actions[(cc.row, cc.col)] = {"name": "Статистика", "action": "statistics", "desc": "📊 Посмотрите свою статистику"}

        # Рисуем иконку окна с настройками
        cc = self.cellStyle.updateObject(self.scene, fixed_grid, self.rows, self.cols, self.cell_size,
                                         GameState.SETTINGS_CELL, "⚙️")
        self.actions[(cc.row, cc.col)] = {"name": "Настройки", "action": "settings", "desc": "⚙️ Измените настройки игры"}

        # Рисуем персонажа
        cc = self.cellStyle.updateObject(self.scene, fixed_grid, self.rows, self.cols, self.cell_size,
                                         GameState.START_CELL, "🛸")

        # Устанавливаем размер сцены
        self.setSceneRect(0, 0, self.cols * self.cell_size, self.rows * self.cell_size)

    def get_action_at(self, pos):
        """Возвращает действие по позиции."""
        if pos in self.actions:
            return self.actions[pos]
        elif pos == self.finish_pos:
            return {"name": "Финиш", "action": "finish", "desc": "Победа!"}
        else:
            return None

    def mousePressEvent(self, event):
        """Обрабатывает клик по полю."""
        pos = event.pos()
        col = pos.x() // self.cell_size
        row = pos.y() // self.cell_size
        pos_key = (row, col)

        if event.button() == Qt.LeftButton:
            action = self.get_action_at(pos_key)
            if action:
                self.parent.handle_action(action["action"])
        elif event.button() == Qt.RightButton:
            action = self.get_action_at(pos_key)
            if action:
                self.parent.desc_label.setText(action["desc"])
            else:
                # Определяем тип ячейки
                if (row, col) in self.actions:
                    self.parent.desc_label.setText("Это действие. ЛКМ — выполнить.")
                elif (row, col) == self.finish_pos:
                    self.parent.desc