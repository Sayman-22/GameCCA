from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsScene, QGraphicsTextItem
from PyQt5.QtGui import QColor, QBrush, QFont, QPixmap, QPen
from PyQt5.QtCore import Qt
from core.state_cell import StateCell
import os, random

class CoorCell:
    row = -1
    col = -1

class CellStyle:
    def updateDigitalCell(self, scene, r, c, cell_size, name):
        item = QGraphicsTextItem(name)
        item.setFont(QFont("Arial", 7, QFont.Bold))
        item.setDefaultTextColor(Qt.white)
        item.setPos(
            c * cell_size + cell_size - item.boundingRect().width(),
            r * cell_size + 0
        )
        scene.addItem(item)

    def updateLeftCell(self, scene, visibility, r, c, cell_size, name):
        if not visibility[r][c]:
            return
        item = QGraphicsTextItem(name)
        item.setFont(QFont("Arial", 10, QFont.Bold))
        item.setDefaultTextColor(Qt.white)
        item.setPos(
            c * cell_size - 0.1*cell_size,
            r * cell_size - 0.1*cell_size
        )
        scene.addItem(item)

    def updateColorCell(self, scene, cell_size, r, c, color):
        cell = QGraphicsRectItem(r * cell_size, c * cell_size, cell_size, cell_size)
        cell.setBrush(QColor(color))
        scene.addItem(cell)

    def updateObjectCell(self,
                    scene,
                    r,
                    c,
                    cell_size,
                    name):
        item = QGraphicsTextItem(name)
        item.setFont(QFont("Arial", 14, QFont.Bold))
        item.setDefaultTextColor(Qt.white)
        item.setPos(
            c * cell_size + cell_size / 2 - item.boundingRect().width() / 2,
            r * cell_size + cell_size / 2 - item.boundingRect().height() / 2
        )
        scene.addItem(item)
    
    def updateObject(self, scene, fixed_grid, rows, cols, cell_size, state, name) -> CoorCell:
        cc = CoorCell()
        sta = False
        r1 = -1
        c1 = -1
        for r in range(rows):
            if sta:
                break
            for c in range(cols):
                if not fixed_grid[r][c] == state:
                    continue
                self.updateObjectCell(scene, r, c, cell_size, name)

                sta = True
                r1 = r
                c1 = c
                break

        cc.row = r1
        cc.col = c1
        return cc

    def updateTextureCell(self, scene, r, c, cell_size, name):
        item = QGraphicsRectItem(c * cell_size, r * cell_size, cell_size, cell_size)
    
        # Текстура 
        current_dir = os.path.dirname(__file__)
        texture_path = os.path.join(current_dir, "..\png", name)
        pixmap = QPixmap(texture_path)
        if pixmap.isNull():
            print(f"[ERROR] Файл не найден: {texture_path}")
            brush = QBrush(QColor("#000000"))
        else:
            brush = QBrush(pixmap.scaled(cell_size, cell_size))
        item.setBrush(brush)

        # Серая рамка
        pen = QPen(QColor("#888888"), 1)
        item.setPen(pen)
        scene.addItem(item)

    def updateTexture(self, scene, fixed_grid, rows, cols, cell_size, actions, parametr, state, name):
        # поиск по ячейкам поля
        for r in range(rows):
            for c in range(cols):
                if not fixed_grid[r][c] == state:
                    continue
                if "." in name:
                    self.updateTextureCell(scene, r, c, cell_size, name)
                else:
                    self.updateObjectCell(scene, r, c, cell_size, name)
                actions[(r, c)] = parametr

    def getNamePlanet(self):
        base_string = "planet"
        random_number = random.randint(1, 18)  # Генерирует номер планеты
        return f"{base_string}{random_number}.png"

    def updateRandomizeAt4(self, options, grid, planet):
        for y in range(options.rows):
            for x in range(options.cols):
                if grid[y][x] == 4:
                    grid[y][x] = options.getNewGridValue()
                    planet[y][x] = self.getNamePlanet()

    def updateNewGrid(self, options, grid):
        for r in range(options.rows):
            for c in range(options.cols):
                if grid[r][c] == StateCell.EMPTY or grid[r][c] == StateCell.START_FIN_CELL:
                    continue
                grid[r][c] = options.getNewGridValue()
        return grid

    def updatePlanetGrid(self, options, grid, planet):
        for r in range(options.rows):
            for c in range(options.cols):
                if grid[r][c] == StateCell.EMPTY or grid[r][c] == StateCell.START_FIN_CELL:
                    continue
                planet[r][c] = self.getNamePlanet()
        return planet
    
    def get_count_positive_cells(self, options, grid):
        # Собираем все ячейки с положительными значениями 
        positive_cells = [
            (r, c) for r in range(options.rows) for c in range(options.cols)
            if grid[r][c] >= 0 and (r, c) != options.start_pos and (r, c) != options.end_pos
        ]
        return positive_cells
            
    def add_crystal(self, options, grid):
        free_cells = self.get_count_positive_cells(options, grid)
        if free_cells:
            r, c = random.choice(free_cells)
            grid[r][c] = StateCell.CRYSTAL
            
    def add_craft(self, options, grid):
            free_cells = self.get_count_positive_cells(options, grid)
            if free_cells:
                r, c = random.choice(free_cells)
                grid[r][c] = StateCell.CRAFT
            
    def add_enemies_easy_static(self, options, grid):
        """Добавляет стационарных врагов."""        
        positive_cells = self.get_count_positive_cells(options, grid)
        if not positive_cells:
            return  # нет подходящих ячеек
        
        num_masks = max(1, int(len(positive_cells) * 0.10))# 10%
        num_enemies = min(num_masks, len(positive_cells))
        enemy_positions = random.sample(positive_cells, num_enemies)
        for r, c in enemy_positions:
            grid[r][c] = StateCell.ENEMY_EASY_STATIC
        return enemy_positions

    def generation_empty(self, options, grid):
        if options.generate_empty:
            valid_cells = self.get_count_positive_cells(options, grid)
            if not valid_cells:
                return  # нет подходящих ячеек
            
            count = max(1, int(len(valid_cells) * 0.15))
            void_positions = random.sample(valid_cells, min(count, len(valid_cells)))
            for r, c in void_positions:
                grid[r][c] = StateCell.EMPTY

    def add_masks(self, options, grid):
        """Добавляет маски на случайные ячейки."""
        options.use_masks = True
        rows, cols = options.rows, options.cols

        # Инициализация
        options.mask_grid = [[False] * cols for _ in range(rows)]
        options.original_values = [[0] * cols for _ in range(rows)]

        positive_cells = self.get_count_positive_cells(options, grid)
        if not positive_cells:
            return  # нет подходящих ячеек
    
        num_masks = max(1, int(len(positive_cells) * 0.15))# Выбираем N ячеек для масок (15%)
        mask_cells = random.sample(positive_cells, min(num_masks, len(positive_cells)))

        for r, c in mask_cells:
            options.mask_grid[r][c] = True
            options.original_values[r][c] = grid[r][c]
                        
    def update_all_cell(self, options, grid, new_grid, new_frozen):
        for r in range(options.rows):
            for c in range(options.cols):
                val = grid[r][c]
                if val <= 0:  # статические ячейки не обновляются
                    continue
                if new_frozen[r][c]:  # замороженные ячейки не обновляются
                    continue
                if options.use_masks:
                    if options.mask_grid[r][c]:# Не обновляем числа под масками
                        continue

                # Применяем базовое правило Коллатца
                if val % 2 == 0:
                    new_val = val // 2
                else:
                    new_val = 3 * val + 1
                new_grid[r][c] = new_val
                        
    def update_frozen_cell(self, options, new_grid, new_frozen):
        for r in range(options.rows):
            for c in range(options.cols):
                new_frozen[r][c] = 0
        for r in range(options.rows):
            for c in range(options.cols):
                # Опция: four_steals_neighbors
                if options.four_steals_neighbors and options.randomize_at_4 and new_grid[r][c] == 4:
                    # Заморозим соседей (запомним координаты)
                    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < options.rows and 0 <= nc < options.cols and new_grid[nr][nc] > 4:
                            new_frozen[nr][nc] = 1
                        
    def update_damage_cell(self, options, new_grid, new_damage, enemies_easy_static):
        for r in range(options.rows):
            for c in range(options.cols):
                new_damage[r][c] = 0
        for r in range(options.rows):
            for c in range(options.cols):
                # Опция: four_steals_neighbors
                if options.four_steals_neighbors and (new_grid[r][c] == 4 or new_grid[r][c] == 2 or new_grid[r][c] == 1):
                    # Урон
                    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < options.rows and 0 <= nc < options.cols:
                            new_damage[nr][nc] = 1
        
        # Проверка урона от врагов
        for er, ec in enemies_easy_static:
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1), (1,1), (-1,-1), (-1,1), (1,-1)]:
                nr, nc = er + dr, ec + dc
                if 0 <= nr < options.rows and 0 <= nc < options.cols:
                    new_damage[nr][nc] = 1

    def add_border_void(self, options, grid):
        """Добавляет пустоту по краю и размещает старт/финиш."""
        rows, cols = options.rows, options.cols

        # 1. Заполняем весь периметр EMPTY
        for r in range(rows):
            for c in range(cols):
                if r == 0 or r == rows - 1 or c == 0 or c == cols - 1:
                    grid[r][c] = StateCell.EMPTY

        # 2. Выбираем стартовую сторону
        sides = ["top", "bottom", "left", "right"]
        start_side = random.choice(sides)

        # 3. Определяем противоположную сторону
        opposite = {
            "top": "bottom",
            "bottom": "top",
            "left": "right",
            "right": "left"
        }
        end_side = opposite[start_side]

        # 4. Генерируем позиции (не в углах!)
        def get_random_pos(side):
            if side == "top":
                r = 0
                c = random.randint(1, cols - 2)  # не в углах
            elif side == "bottom":
                r = rows - 1
                c = random.randint(1, cols - 2)
            elif side == "left":
                r = random.randint(1, rows - 2)
                c = 0
            else:  # right
                r = random.randint(1, rows - 2)
                c = cols - 1
            return (r, c)

        start_pos = get_random_pos(start_side)
        end_pos = get_random_pos(end_side)

        # 5. Устанавливаем старт и финиш
        options.start_pos = start_pos
        options.end_pos = end_pos
        grid[start_pos[0]][start_pos[1]] = StateCell.START_FIN_CELL
        grid[end_pos[0]][end_pos[1]] = StateCell.START_FIN_CELL

        # 6. Обновляем позицию игрока
        return start_pos
                
                