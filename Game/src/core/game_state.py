from dataclasses import dataclass
from typing import List
import random

@dataclass
class GameOptions:
    # Размер поля
    rows: int = 4
    cols: int = 4
    
    # Новые поля для диапазона чисел
    min_initial_value: int = 17
    max_initial_value: int = 30

    # Основные опции CCA
    randomize_at_4: bool = True
    neighbors_affect_speed: bool = True
    even_steal_energy: bool = True
    four_steals_neighbors: bool = True
    odd_jump_if_surrounded_by_even: bool = True
    use_8_neighbors: bool = False
    only_even_update_if_r6: bool = False
    only_odd_update_if_r3: bool = False
    even_numbers_add_2_if_sub6: bool = False

    # Игровые свойства
    hardcore: bool = False
    fog_of_war: bool = False
    disable_regen_at_1: bool = False
    max_skips: int = 200  # количество пропусков хода

class GameState:
####### ИНИЦИАЛИЗАЦИЯ КЛАССА ОБРАБОТЧИКА #######
    START_FIN_CELL = -1
    EMPTY = -3
    CRAFT = -5
    CRYSTAL = -4

    def __init__(self, rows: int = 10, cols: int = 14, options: GameOptions = None):
        self.rows = rows
        self.cols = cols
        self.options = options or GameOptions()
        self.grid: List[List[int]] = [[0] * cols for _ in range(rows)]
        self.frozen: List[List[int]] = [[0] * cols for _ in range(rows)]
        self.damage: List[List[int]] = [[0] * cols for _ in range(rows)]
        self.player_pos = (0, 0)  # (row, col)
        self.start_pos = (0, 0)
        self.end_pos = (rows - 1, cols - 1)
        self.lives = 1 if self.options.hardcore else 2
        self.crystals = 0
        self.craftedCells = 0
        self.skips_remaining = self.options.max_skips  # счетчик пропусков хода
####### ИНИЦИАЛИЗАЦИЯ КЛАССА ОБРАБОТЧИКА #######



####### ФУНКЦИИ #######
    def generate_initial_grid(self):
        # Заполняем случайными числами
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = random.randint(
                    self.options.min_initial_value,
                    self.options.max_initial_value
                )

        # Старт и финиш
        self.grid[self.start_pos[0]][self.start_pos[1]] = self.START_FIN_CELL
        self.grid[self.end_pos[0]][self.end_pos[1]] = self.START_FIN_CELL

        # Кристалл (75%)
        if random.random() < 0.75:
            free_cells = [(r, c) for r in range(self.rows) for c in range(self.cols)
                          if (r, c) not in [self.start_pos, self.end_pos] and self.grid[r][c] > 0]
            if free_cells:
                r, c = random.choice(free_cells)
                self.grid[r][c] = self.CRYSTAL

        # Крафт (75%)
        if random.random() < 0.75:
            free_cells = [(r, c) for r in range(self.rows) for c in range(self.cols)
                          if (r, c) not in [self.start_pos, self.end_pos] and self.grid[r][c] > 0]
            if free_cells:
                r, c = random.choice(free_cells)
                self.grid[r][c] = self.CRAFT

    def get_player_pos(self):
        """Возвращает текущую позицию игрока как кортеж (row, col)."""
        return self.player_pos

    def collatz_step(self, n):
        """Применяет один шаг правила Коллатца."""
        if n <= 0:
            return n  # Статические ячейки не меняются
        if n in (1, 2, 4):
            return n  # Цикл
        if n % 2 == 0:
            return n // 2
        return 3 * n + 1
####### ФУНКЦИИ #######




####### ДВИЖЕНИЕ #######
    def advance_step(self):        
        """Выполняет шаг автомата с учётом опций."""
        new_grid = [row[:] for row in self.grid]
        new_frozen = [row[:] for row in self.frozen]
        new_damage = [row[:] for row in self.damage]

        # Опция: randomize_at_4
        if self.options.randomize_at_4:
            for y in range(self.rows):
                for x in range(self.cols):
                    if self.grid[y][x] == 4:
                        self.grid[y][x] = random.randint(
                            self.options.min_initial_value,
                            self.options.max_initial_value
                        )

        # Обновление ячеек
        for r in range(self.rows):
            for c in range(self.cols):
                val = self.grid[r][c]
                if val <= 0:  # статические ячейки не обновляются
                    continue
                if new_frozen[r][c]:  # статические ячейки не обновляются
                    continue

                # Применяем базовое правило Коллатца
                if val % 2 == 0:
                    new_val = val // 2
                else:
                    new_val = 3 * val + 1
                new_grid[r][c] = new_val

        # Обновление заморозки
        for r in range(self.rows):
            for c in range(self.cols):
                new_frozen[r][c] = 0
        for r in range(self.rows):
            for c in range(self.cols):
                # Опция: four_steals_neighbors
                if self.options.four_steals_neighbors and self.options.randomize_at_4 and new_grid[r][c] == 4:
                    # Заморозим соседей (запомним координаты)
                    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols and new_grid[nr][nc] > 4:
                            new_frozen[nr][nc] = 1

        # Обновление заморозки
        for r in range(self.rows):
            for c in range(self.cols):
                new_damage[r][c] = 0
        for r in range(self.rows):
            for c in range(self.cols):
                # Опция: randomize_at_4
                if self.options.four_steals_neighbors and self.options.randomize_at_4 and new_grid[r][c] == 4:
                    # Заморозим соседей (запомним координаты)
                    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            new_damage[nr][nc] = 1

        # Новое поле
        self.frozen = new_frozen
        self.grid = new_grid
        self.damage = new_damage


    def move_player(self, dr: int, dc: int) -> int:
        r, c = self.player_pos
        nr, nc = r + dr, c + dc
        if not (0 <= nr < self.rows and 0 <= nc < self.cols):
            return -2
        
        state_live = True
        self.player_pos = (nr, nc)
        cell = self.grid[nr][nc]
        damage = 0
        # Опция: randomize_at_4
        if self.options.randomize_at_4:
            # Заморозим соседей (запомним координаты)
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nnr, nnc = r + dr, c + dc
                if 0 <= nnr < self.rows and 0 <= nnc < self.cols:
                    damage += 1

        if cell == self.CRYSTAL:
            self.crystals += 1
            self.grid[nr][nc] = random.randint(
                self.options.min_initial_value,
                self.options.max_initial_value
            )
        elif cell == self.CRAFT:
            # Логика крафта (временно просто фиксируем)
            pass
        elif cell <= 0 and cell != self.START_FIN_CELL:
            self.lives = -1  # Пустота или boost = смерть
            state_live = False
        elif cell % 2 == 1 and cell not in (1, 2, 4) and cell != self.START_FIN_CELL:  # Нечётное
            self.lives -= 1
            state_live = False
        elif cell in (1, 2, 4):  # Цикл
            self.lives = 0
            state_live = False
            return -3

        # Проверка смерти
        if self.lives <= 0:
            return -1
        # Если потеряна жизнь
        if state_live == False:
            return 2
        # Если в ячейке наносится урон
        # if damage > 0:
        #     self.lives -= 1
        #     return 2
        # Нет изменений
        return 1
    
####### ДВИЖЕНИЕ #######
