# ui/main_menu_view.py
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush, QPainter
from core.update_cell import CellStyle
from core.state_cell import StateCell

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

        sf = StateCell.START_FIN_CELL
        ee = StateCell.EMPTY
        cc = StateCell.CASTLE
        ww = StateCell.WALL
        ca = StateCell.CAMPAIGN_CELL
        ar = StateCell.ARENA_CELL
        ra = StateCell.RANDOM_CELL
        st = StateCell.STATISTICS_CELL
        se = StateCell.SETTINGS_CELL
        ec = StateCell.END_CELL
        sc = StateCell.START_CELL
        bh = StateCell.BLACK_HOLE_CELL
        gs = StateCell.GOOD_SYSTEM_CELL
        bs = StateCell.BAD_SYSTEM_CELL
        mc = StateCell.MASK_CELL
        fc = StateCell.FOG_CELL
        es = StateCell.ENEMY_EASY_STATIC
        # Фиксированная сетка для обучения
        fixed_grid = [
            [ee, ee, ee, ee, ee, ee, ee, ee, ee, ww, ee, ee, ee, ee, ee, ee, ee, ee, ee, ee],# 1
            [ee, gs, ee, mc, ee, ee, ee, ee, ww, ww, ww, ee, ee, ee, ee, ee, ee, ee, ee, gs],# 2
            [ee, ee, ee, ee, ee, ee, ee, ww, ww, es, ww, ww, ee, ee, ee, ee, gs, ee, ee, ee],# 3
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
                                     StateCell.EMPTY, "void.png")
        
        # Рисуем иконку с финишем
        par = {"name": "Выход", "action": "exit", "desc": "🏁 Закройте игру"}
        self.cellStyle.updateTexture(self.scene, fixed_grid, self.rows, self.cols, self.cell_size, self.actions, par,
                                     StateCell.END_CELL, "🏁")
        
        # Заполняем черные дыры
        par = {"name": "Черная дыра", "action": "black_hole", "desc": "Черная дыра - смерть, ждущая путников"}
        self.cellStyle.updateTexture(self.scene, fixed_grid, self.rows, self.cols, self.cell_size, self.actions, par,
                                     StateCell.BLACK_HOLE_CELL, "🕳️")
        
        # Заполняем обитаемые системы
        par = {"name": "Обитаемые системы", "action": "good_system", "desc": "Обитаемые системы"}
        self.cellStyle.updateTexture(self.scene, fixed_grid, self.rows, self.cols, self.cell_size, self.actions, par,
                                     StateCell.GOOD_SYSTEM_CELL, "🌍")
        
        # Заполняем необитаемые системы
        par = {"name": "Необитаемые системы", "action": "bad_system", "desc": "Необитаемые системы"}
        self.cellStyle.updateTexture(self.scene, fixed_grid, self.rows, self.cols, self.cell_size, self.actions, par,
                                     StateCell.BAD_SYSTEM_CELL, "💥")

        # Ячейка - маска
        par = {"name": "Маска", "action": "mask_cell", "desc": "?   Ячейка - маска"}
        self.cellStyle.updateTexture(self.scene, fixed_grid, self.rows, self.cols, self.cell_size, self.actions, par,
                                     StateCell.MASK_CELL, "?")
        
        # Туман войны
        for r in range(self.rows):
            for c in range(self.cols):
                if StateCell.FOG_CELL == fixed_grid[r][c]:
                    self.cellStyle.updateColorCell(self.scene, self.cell_size, c, r, "#305050")
                    self.actions[(r, c)] = {"name": "Туман войны", "action": "fog", "desc": "Туман войны"}

        # Рисуем замок
        par = {"name": "Замок", "action": "castle_cell", "desc": "Это пространство замка"}
        self.cellStyle.updateTexture(self.scene, fixed_grid, self.rows, self.cols, self.cell_size, self.actions, par,
                                     StateCell.CASTLE, "wall_texture.png")

        # Рисуем стену
        par = {"name": "Стена", "action": "wall_cell", "desc": "Это стена"}
        self.cellStyle.updateTexture(self.scene, fixed_grid, self.rows, self.cols, self.cell_size, self.actions, par,
                                     StateCell.WALL, "wall_texture_2.png")

        # Рисуем врага (простого статического)
        par = {"name": "Хасы", "action": "wall_cell", "desc": "Это  враг - Хасы, не перемещается по ячейкам, атакует в радиусе 1 ячейки"}
        self.cellStyle.updateTexture(self.scene, fixed_grid, self.rows, self.cols, self.cell_size, self.actions, par,
                                     StateCell.ENEMY_EASY_STATIC, "ALIEN1.png")

        # Рисуем иконку кампании
        cc = self.cellStyle.updateObject(self.scene, fixed_grid, self.rows, self.cols, self.cell_size,
                                         StateCell.CAMPAIGN_CELL, "📜")
        self.actions[(cc.row, cc.col)] = {"name": "Кампания", "action": "campaign", "desc": "📜 Пройдите уровни кампании"}

        # Рисуем иконку арены
        cc = self.cellStyle.updateObject(self.scene, fixed_grid, self.rows, self.cols, self.cell_size,
                                         StateCell.ARENA_CELL, "⚔️")
        self.actions[(cc.row, cc.col)] = {"name": "Арена", "action": "arena", "desc": "⚔️ Испытайте себя в арене"}

        # Рисуем иконку случайного лабиринта
        cc = self.cellStyle.updateObject(self.scene, fixed_grid, self.rows, self.cols, self.cell_size,
                                         StateCell.RANDOM_CELL, "🎲")
        self.actions[(cc.row, cc.col)] = {"name": "Случайный уровень", "action": "random", "desc": "🎲 Начните случайный лабиринт"}

        # Рисуем иконку окна со статистикой
        cc = self.cellStyle.updateObject(self.scene, fixed_grid, self.rows, self.cols, self.cell_size,
                                         StateCell.STATISTICS_CELL, "📊")
        self.actions[(cc.row, cc.col)] = {"name": "Статистика", "action": "statistics", "desc": "📊 Посмотрите свою статистику"}

        # Рисуем иконку окна с настройками
        cc = self.cellStyle.updateObject(self.scene, fixed_grid, self.rows, self.cols, self.cell_size,
                                         StateCell.SETTINGS_CELL, "⚙️")
        self.actions[(cc.row, cc.col)] = {"name": "Настройки", "action": "settings", "desc": "⚙️ Измените настройки игры"}

        # Рисуем персонажа
        cc = self.cellStyle.updateObject(self.scene, fixed_grid, self.rows, self.cols, self.cell_size,
                                         StateCell.START_CELL, "🛸")

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