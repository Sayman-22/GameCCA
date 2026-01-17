from dataclasses import dataclass
from typing import List
import random
from core.network_client import RequestForServer
from PyQt5.QtWidgets import QMessageBox
from core.update_cell import CellStyle
from core.state_cell import StateCell

@dataclass
class GameOptions:
    border_void = False

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
    spawn_enemies_easy_static = False

    # Игровые свойства
    hardcore: bool = False
    disable_regen_at_1: bool = False
    max_skips: int = 2  # количество пропусков хода
    pressure_tolerance: int = 200  # допустимое давление

    # Туман войны
    fog_of_war: bool = False
    visibility_radius = 1
    remember_visibility = False

    # ячейки - маски
    mask_grid = None          # [[bool]] — True = закрыта
    original_values = None    # [[int]] — исходные числа
    mask_attempts = 0         # ошибки (макс. 3)
    use_masks = False         # флаг активности режима

    # параметры ячеек
    start_pos = None
    end_pos = None

    def __init__(self,
                 mode="maze",
                 lives=2,
                 defense=1,
                 freeze_cell=0,
                 max_undo=0,
                 rows=5,
                 cols=5,
                 randomize_at_4=False,
                 four_steals_neighbors=True,
                 max_skips=2):
        self.mode = mode
        self.lives = lives
        self.defense = defense
        self.freeze_cell = freeze_cell
        self.rows = rows
        self.cols = cols
        self.randomize_at_4 = randomize_at_4
        self.four_steals_neighbors = four_steals_neighbors
        self.max_skips = max_skips
        self.max_undo = max_undo

    def getNewGridValue(self):
        return random.randint(
            self.min_initial_value,
            self.max_initial_value
        )

class GameState:
####### ИНИЦИАЛИЗАЦИЯ КЛАССА ОБРАБОТЧИКА #######
    rfs = RequestForServer()

    def __init__(self, username, rows, cols, 
                 options: GameOptions = GameOptions()):
        
        self.cellStyle = CellStyle()
        self.options = options
        self.username = username

        self.options.rows = rows
        self.options.cols = cols

        self.state_history = []  # список: [(grid_copy, player_pos), ...]
        self.crystals = 0
        self.craftedCells = 0
        self.freeze_active = False   # активна ли заморозка в этом ходу
        self.freeze_pos = None       # позиция замороженной ячейки
        self.mask_attempts = 0
        self.just_damaged = False
        self.enemies_easy_static = []
            
        # Режим
        if self.options.mode == "arena":
            self.lives = self.options.lives
            self.options.rows = 10
            self.options.cols = 15
            self.generate_arena_grid()
            self.player_pos = (int(self.options.rows-2), int(self.options.cols/2-1))  # центр нижней трети
            self.options.start_pos = self.player_pos
            self.options.end_pos = None  # нет финиша
            self.move_count = 0
            self.rows_removed = 0
            self.level = 0
        else:
            self.lives = 1 if self.options.hardcore else self.options.lives
            self.player_pos = (0, 0)  # (row, col)
            self.options.start_pos = (0, 0)  # (row, col)
            self.options.end_pos = (self.options.rows - 1, self.options.cols - 1)  # (row, col)

        c = self.options.cols
        r = self.options.rows
        self.grid: List[List[int]] = [[0] * c for _ in range(r)]
        self.frozen: List[List[int]] = [[0] * c for _ in range(r)]
        self.damage: List[List[int]] = [[0] * c for _ in range(r)]
        self.planet: List[List[str]] = [[""] * c for _ in range(r)]
        if self.options.fog_of_war == False:
            self.visibility = [[True for _ in range(c)] for _ in range(r)]
        else:
            self.visibility = [[False for _ in range(c)] for _ in range(r)]

####### ИНИЦИАЛИЗАЦИЯ КЛАССА ОБРАБОТЧИКА #######



####### ФУНКЦИИ #######
    def getNamePlanet(self, r, c):
        return self.planet[r][c]
    
    def getRows(self):
        return self.options.rows
    
    def getCols(self):
        return self.options.cols
    
    def getParUseMasks(self):
        return self.options.use_masks
    
    def getStartPos(self):
        return self.options.start_pos
    
    def getEndPos(self):
        return self.options.end_pos
    
    def get_player_pos(self):
        return self.player_pos
    
    def getMaskGrid(self):
        return self.options.mask_grid
    
    def get_grid_value(self, nr, nc):
        return self.grid[nr][nc]

    def generate_initial_grid(self):
        # Бордеры и старт финиш
        if self.options.border_void:
            self.player_pos = self.cellStyle.add_border_void(self.options, self.grid)

        # Генерация пустоты
        self.cellStyle.generation_empty(self.options, self.grid)
        # Заполняем случайными числами
        self.cellStyle.updateNewGrid(self.options, self.grid)
        # Заполняем случайными планетами
        self.cellStyle.updatePlanetGrid(self.options, self.grid, self.planet)

        # Ячейки с масками
        if self.options.use_masks:
            self.cellStyle.add_masks(self.options, self.grid)
            self.mask_attempts = 0
        # Кристалл
        if random.random() < 0.75:
            self.cellStyle.add_crystal(self.options, self.grid)
        # Крафт
        if random.random() < 0.5:
            self.cellStyle.add_craft(self.options, self.grid)
        # Воины - Хасы
        if self.options.spawn_enemies_easy_static:
            self.enemies_easy_static = self.cellStyle.add_enemies_easy_static()

    def generate_arena_grid(self):
        self.grid = [
            [random.randint(10, 30) for _ in range(self.options.cols)]
            for _ in range(self.options.rows)
        ]
    
    def update_visibility(self):
        """Обновляет видимость вокруг игрока. Если remember_visibility=False, сбрасывает всё."""
        if self.options.fog_of_war == False:
            return
        if not self.options.remember_visibility:
            # Сбрасываем всё — видим только текущую окрестность
            self.visibility = [[False for _ in range(self.options.cols)] for _ in range(self.options.rows)]

        pr, pc = self.player_pos
        for dr in range(-self.options.visibility_radius, self.options.visibility_radius + 1):
            for dc in range(-self.options.visibility_radius, self.options.visibility_radius + 1):
                r, c = pr + dr, pc + dc
                if 0 <= r < self.options.rows and 0 <= c < self.options.cols:
                    self.visibility[r][c] = True

    # def collatz_step(self, n):
    #     """Применяет один шаг правила Коллатца."""
    #     if n <= 0:
    #         return n  # Статические ячейки не меняются
    #     if n in (1, 2, 4):
    #         return n  # Цикл
    #     if n % 2 == 0:
    #         return n // 2
    #     return 3 * n + 1
    
####### ФУНКЦИИ #######




####### ДВИЖЕНИЕ #######
    def advance_step(self):        
        """Выполняет шаг автомата с учётом опций."""
        new_grid = [row[:] for row in self.grid]
        new_frozen = [row[:] for row in self.frozen]
        new_damage = [row[:] for row in self.damage]

        # Опция: randomize_at_4
        self.action_randomize_at_4()
        
        # Заморозка ячейки героем
        if self.freeze_active:
            s, e = self.freeze_pos
            new_frozen[s][e] = 1
            self.freeze_active = False
            self.freeze_pos = None

        # Обновление ячеек
        self.cellStyle.update_all_cell(self.options, self.grid, new_grid, new_frozen)
        # Обновление заморозки
        self.cellStyle.update_frozen_cell(self.options, new_grid, new_frozen)
        # Обновление урона
        self.cellStyle.update_damage_cell(self.options, new_grid, new_damage, self.enemies_easy_static)

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
            self.grid.insert(0, [random.randint(10, max_val) for _ in range(self.options.cols)])
            # Смещаем игрока
            r, c = self.player_pos
            self.player_pos = (r + 1, c)
            if r - 1 < 0:
                self.lives = 0
            self.move_count = 0

    def check_step(self, nr: int, nc: int) -> bool:
        # за пределы границ
        if not (0 <= nr < self.options.rows and 0 <= nc < self.options.cols):
            return False

        # пустота
        cell = self.get_grid_value(nr, nc)
        if cell == StateCell.EMPTY:
            return False
        
        return True

    def undo_move(self):
        """Возвращает героя на предыдущую позицию."""
        if self.state_history:
            grid_prev, pos_prev = self.state_history.pop()
            for r in range(self.options.rows):
                for c in range(self.options.cols):
                    self.grid[r][c] = grid_prev[r][c]
            self.player_pos = pos_prev
            self.options.max_undo -= 1
            return True
        return False

    def write_history(self):
        if self.options.max_undo > 0:
            grid_copy = [row[:] for row in self.grid]  # глубокая копия
            state = (grid_copy, self.player_pos)
            self.state_history.append(state)
            # Ограничиваем длину
            if len(self.state_history) > self.options.max_undo:
                self.state_history.pop(0)

    def move_player(self, dr: int, dc: int) -> int:
        r, c = self.player_pos
        nr, nc = r + dr, c + dc

        # Автоматическое открытие маски при входе
        if self.options.use_masks:
            if self.options.mask_grid[nr][nc]:
                self.options.mask_grid[nr][nc] = False  # снимаем маску

        state_live = True # Отслеживает изменение жизни
        self.player_pos = (nr, nc)
        cell = self.grid[nr][nc]
        damage = self.damage[nr][nc]

        if cell == StateCell.CRYSTAL:
            self.update_crystals(nr, nc)
        elif cell == StateCell.CRAFT:
            # Логика крафта (временно просто фиксируем)
            
            # request = {
            #     "action": "update_stats",
            #     "username": self.parent.username,
            #     "stat_type": "craft_cells"
            # }
            # response = send_request(request, self)
            pass
        elif cell <= 0 and cell != StateCell.START_FIN_CELL:
            self.lives -= 1
            state_live = False
        elif cell in (1, 2, 4):  # Цикл
            self.lives = 0
            state_live = False
            return -3
        elif cell % 2 == 1 and cell != StateCell.START_FIN_CELL:  # Нечётное
            self.lives -= 1
            state_live = False
        elif cell > self.options.pressure_tolerance: # превышение допустимого давления
            self.lives -= 1
            state_live = False

        self.update_visibility()

        # Если в ячейке наносится урон
        if damage > 0 and state_live == True:
            self.apply_damage(1)
            state_live = False
        # Проверка смерти
        if self.lives <= 0:
            self.just_damaged = True 
            return -1
        # Если потеряна жизнь
        if state_live == False:
            self.just_damaged = True 
            return 2
        # Нет изменений
        return 1
    
####### ДВИЖЕНИЕ #######


####### ФУНКЦИИ #######
    def action_randomize_at_4(self):
        if self.options.randomize_at_4:
            self.cellStyle.updateRandomizeAt4(self.options, self.grid, self.planet)
      
    def update_crystals(self, nr, nc):
        self.crystals += 1
        self.grid[nr][nc] = self.options.getNewGridValue()
        request = self.rfs.prepare_update_stats(self.username, "crystals", "increment", 1)
        response = self.rfs.send_request(request, self)
        if response and response["status"] == "success":
            self.stats = response["stats"]
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось обновить статистику на сервере.")
    
    def activate_freeze(self):
        """Активирует заморозку на текущей позиции."""
        if self.options.freeze_cell > 0:
            self.options.freeze_cell -= 1
            self.freeze_active = True
            self.freeze_pos = self.player_pos
            return True
        return False

    def apply_damage(self, amount=1):
        """Наносит урон с учётом защиты."""
        self.options.defense = self.options.defense - amount
        if (self.options.defense < 0):
            self.lives -= amount
            self.options.defense = 0
        return
    
    def calculate_difficulty(self):
        """Рассчитывает уровень сложности лабиринта."""
        base = 0
        min_side = min(self.options.rows, self.options.cols)
        if min_side >= 8:
            base = (min_side - 8 + 3) // 3  # +2 для округления вверх

        # бонусы за опции
        bonus = 0
        if self.options.fog_of_war:
            bonus += 3
        if self.options.hardcore:
            bonus += 2
        if self.options.use_masks:
            bonus += 1
        if self.options.spawn_enemies_easy_static:
            bonus += 1
        if self.options.generate_empty:
            bonus += 1

        # Бонус за минимальное число
        min_val_bonus = self.options.min_initial_value // 50
        bonus += min_val_bonus
        return base + bonus

    def check_mask_guess(self, r, c, guess):
        """Проверяет число под маской."""
        if not self.options.mask_grid[r][c]:
            return False  # уже открыта

        original = self.original_values[r][c]
        if guess == original:
            self.options.mask_grid[r][c] = False  # открываем
            self.crystals += 3
            return "correct"
        else:
            self.mask_attempts += 1
            if self.mask_attempts >= 3:
                return "game_over"
            return "wrong"
    
####### ФУНКЦИИ #######
