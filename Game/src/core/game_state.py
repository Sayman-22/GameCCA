from dataclasses import dataclass
from typing import List
import random
from ui.network_client import send_request
from PyQt5.QtWidgets import QMessageBox

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
    generate_empty: bool = False
    generate_empty_count = 1

    # Игровые свойства
    hardcore: bool = False
    disable_regen_at_1: bool = False
    max_skips: int = 2  # количество пропусков хода
    pressure_tolerance: int = 200  # допустимое давление

    # Туман войны
    fog_of_war: bool = False
    visibility_radius = 1
    remember_visibility = False

    def __init__(self,
                 mode="maze",
                 lives=2,
                 rows=5,
                 cols=5,
                 randomize_at_4=False,
                 four_steals_neighbors=True,
                 max_skips=2):
        self.mode = mode
        self.lives = lives
        self.rows = rows
        self.cols = cols
        self.randomize_at_4 = randomize_at_4
        self.four_steals_neighbors = four_steals_neighbors
        self.max_skips = max_skips

class GameState:
####### ИНИЦИАЛИЗАЦИЯ КЛАССА ОБРАБОТЧИКА #######
    START_FIN_CELL = -1
    EMPTY = -2
    CRAFT = -3
    CRYSTAL = -4

    def __init__(self,
                 username,
                 rows, 
                 cols, 
                 options: GameOptions = GameOptions()):
        self.rows = rows
        self.cols = cols
        self.username = username
        self.options = options
        self.crystals = 0
        self.craftedCells = 0
            
        # Режим
        if self.options.mode == "arena":
            self.lives = self.options.lives
            self.rows = 10
            self.cols = 15
            self.generate_arena_grid()
            self.player_pos = (int(self.rows-2), int(self.cols/2-1))  # центр нижней трети
            self.start_pos = self.player_pos
            self.end_pos = None  # нет финиша
            self.move_count = 0
            self.rows_removed = 0
            self.level = 0
        else:
            self.lives = 1 if self.options.hardcore else self.options.lives
            self.player_pos = (0, 0)  # (row, col)
            self.start_pos = (0, 0)  # (row, col)
            self.end_pos = (self.rows - 1, self.cols - 1)  # (row, col)

        self.grid: List[List[int]] = [[0] * self.cols for _ in range(self.rows)]
        self.frozen: List[List[int]] = [[0] * self.cols for _ in range(self.rows)]
        self.damage: List[List[int]] = [[0] * self.cols for _ in range(self.rows)]
        if self.options.fog_of_war == False:
            self.visibility = [[True for _ in range(self.cols)] for _ in range(self.rows)]
        else:
            self.visibility = [[False for _ in range(self.cols)] for _ in range(self.rows)]

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
        if not self.options.mode == "arena":
            self.grid[self.end_pos[0]][self.end_pos[1]] = self.START_FIN_CELL

        # --- Генерация пустоты ---
        if self.options.generate_empty:
            # Получаем список всех ячеек, кроме старта и финиша
            all_cells = [(r, c) for r in range(self.rows) for c in range(self.cols)]
            # Удаляем старт и финиш
            start_pos = self.start_pos
            end_pos = self.end_pos
            valid_cells = [pos for pos in all_cells if pos != start_pos and pos != end_pos]

            # Выбираем 3 случайные ячейки
            void_positions = random.sample(valid_cells, min(self.options.generate_empty_count, len(valid_cells)))

            for r, c in void_positions:
                if random.random() < 0.5:  # 50% шанс
                    self.grid[r][c] = GameState.EMPTY

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

    def generate_arena_grid(self):
        self.grid = [
            [random.randint(10, 30) for _ in range(self.cols)]
            for _ in range(self.rows)
        ]

    def get_player_pos(self):
        """Возвращает текущую позицию игрока как кортеж (row, col)."""
        return self.player_pos
    
    def update_visibility(self):
        """Обновляет видимость вокруг игрока. Если remember_visibility=False, сбрасывает всё."""
        if self.options.fog_of_war == False:
            return
        if not self.options.remember_visibility:
            # Сбрасываем всё — видим только текущую окрестность
            self.visibility = [[False for _ in range(self.cols)] for _ in range(self.rows)]

        pr, pc = self.player_pos
        for dr in range(-self.options.visibility_radius, self.options.visibility_radius + 1):
            for dc in range(-self.options.visibility_radius, self.options.visibility_radius + 1):
                r, c = pr + dr, pc + dc
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    self.visibility[r][c] = True

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
        self.action_randomize_at_4()
        # Обновление ячеек
        self.update_all_cell(new_grid, new_frozen)
        # Обновление заморозки
        self.update_frozen_cell(new_grid, new_frozen)
        # Обновление урона
        self.update_damage_cell(new_grid, new_damage)

        # Новое поле
        self.frozen = new_frozen
        self.grid = new_grid
        self.damage = new_damage

    def arena_next_move(self):
        """Вызывается после каждого хода в режиме арены."""
        if not self.options.mode == "arena":
            return

        self.move_count += 1
        if self.move_count == 2:
            # Удаляем нижнюю строку
            self.grid.pop()
            self.rows_removed += 1
            self.level = self.rows_removed // 50
            # Новая верхняя строка
            max_val = 30 + 20 * self.level
            self.grid.insert(0, [random.randint(10, max_val) for _ in range(self.cols)])
            # Смещаем игрока
            r, c = self.player_pos
            self.player_pos = (r + 1, c)
            if r - 1 < 0:
                self.lives = 0
            self.move_count = 0

    def move_player(self, dr: int, dc: int) -> int:
        r, c = self.player_pos
        nr, nc = r + dr, c + dc
        if not (0 <= nr < self.rows and 0 <= nc < self.cols):
            return -2
        
        state_live = True
        self.player_pos = (nr, nc)
        cell = self.grid[nr][nc]
        damage = self.damage[nr][nc]

        if cell == self.CRYSTAL:
            self.update_crystals(nr, nc)
        elif cell == self.CRAFT:
            # Логика крафта (временно просто фиксируем)
            
            # request = {
            #     "action": "update_stats",
            #     "username": self.parent.username,
            #     "stat_type": "craft_cells"
            # }
            # response = send_request(request, self)
            pass
        elif cell <= 0 and cell != self.START_FIN_CELL:
            self.lives = -1
            state_live = False
        elif cell in (1, 2, 4):  # Цикл
            self.lives = 0
            state_live = False
            return -3
        elif cell % 2 == 1 and cell != self.START_FIN_CELL:  # Нечётное
            self.lives -= 1
            state_live = False
        elif cell > self.options.pressure_tolerance: # превышение допустимого давления
            self.lives -= 1
            state_live = False

        self.update_visibility()

        # Если в ячейке наносится урон
        if damage > 0 and state_live == True:
            self.lives -= 1
            state_live = False
        # Проверка смерти
        if self.lives <= 0:
            return -1
        # Если потеряна жизнь
        if state_live == False:
            return 2
        # Нет изменений
        return 1
    
####### ДВИЖЕНИЕ #######


####### ФУНКЦИИ #######
    def action_randomize_at_4(self):
        if self.options.randomize_at_4:
            for y in range(self.rows):
                for x in range(self.cols):
                    if self.grid[y][x] == 4:
                        self.grid[y][x] = random.randint(
                            self.options.min_initial_value,
                            self.options.max_initial_value
                        )
                        
    def update_all_cell(self, new_grid, new_frozen):
        for r in range(self.rows):
            for c in range(self.cols):
                val = self.grid[r][c]
                if val <= 0:  # статические ячейки не обновляются
                    continue
                if new_frozen[r][c]:  # замороженные ячейки не обновляются
                    continue

                # Применяем базовое правило Коллатца
                if val % 2 == 0:
                    new_val = val // 2
                else:
                    new_val = 3 * val + 1
                new_grid[r][c] = new_val
                        
    def update_frozen_cell(self, new_grid, new_frozen):
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
                        
    def update_damage_cell(self, new_grid, new_damage):
        for r in range(self.rows):
            for c in range(self.cols):
                new_damage[r][c] = 0
        for r in range(self.rows):
            for c in range(self.cols):
                # Опция: four_steals_neighbors
                if self.options.four_steals_neighbors and (new_grid[r][c] == 4 or new_grid[r][c] == 2 or new_grid[r][c] == 1):
                    # Заморозим соседей (запомним координаты)
                    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            new_damage[nr][nc] = 1
                        
    def update_crystals(self, nr, nc):
        self.crystals += 1
        self.grid[nr][nc] = random.randint(
            self.options.min_initial_value,
            self.options.max_initial_value
        )
        request = {
            "action": "update_stats",
            "username": self.username,
            "stat_type": "crystals",
            "operation": "increment",
            "value": 1
        }
        response = send_request(request, self)
        if response and response["status"] == "success":
            self.stats = response["stats"]
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось обновить статистику на сервере.")

    def get_grid_value(self, nr, nc) -> int:
        return self.grid[nr][nc]

####### ФУНКЦИИ #######
