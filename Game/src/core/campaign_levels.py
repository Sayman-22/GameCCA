# core/campaign_levels.py

from core.game_state import GameOptions, GameState
import random

def get_level_1(username) -> GameState:
    """
    Уровень 1 кампании: Введение в чётные и нечётные числа.
    Размер: 5x5, нет кристаллов, базовые числа.
    """
    options = GameOptions(
        rows=5,
        cols=5,
        randomize_at_4=False,  # отключим, чтобы игрок увидел 4
        four_steals_neighbors=True,
        max_skips=3  # даём больше пропусков для обучения
    )
    
    game_state = GameState(username=username, rows=options.rows, cols=options.cols, options=options)
    
    # Фиксированная сетка для обучения
    fixed_grid = [
        [17, 18, 19, 20, 21],
        [22, -1, 23, 24, -4],  # -1 = старт, -4 = кристалл
        [25, 26, 27, 28, 29],
        [30, 31, 32, 33, 34],
        [35, 36, 37, 38, -1]   # -1 = финиш
    ]
    
    game_state.grid = [row[:] for row in fixed_grid]
    game_state.start_pos = (1, 1)
    game_state.end_pos = (4, 4)
    game_state.player_pos = game_state.start_pos
    
    return game_state