# ui/local_ai_advisor.py

from core.game_state import GameState
from typing import List, Tuple

DIRECTIONS = {
    "вверх": (-1, 0),
    "вниз": (1, 0),
    "влево": (0, -1),
    "вправо": (0, 1),
}

def _is_valid_pos(game_state, r: int, c: int) -> bool:
    return 0 <= r < game_state.rows and 0 <= c < game_state.cols

def _is_passable(game_state, r: int, c: int) -> bool:
    if not _is_valid_pos(game_state, r, c):
        return False
    cell = game_state.grid[r][c]
    return cell != GameState.EMPTY

def _cell_risk(game_state, r: int, c: int) -> int:
    """0 = безопасно, 1 = −1 жизнь, 2 = нельзя туда идти"""
    if not _is_passable(game_state, r, c):
        return 2
    cell = game_state.grid[r][c]
    if cell <= 0:
        return 0
    if cell in (1, 2, 4):
        return 1
    if cell > game_state.pressure_tolerance:
        return 1
    if cell % 2 == 1:
        return 1
    return 0

def _manhattan_dist(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def get_hint(game_state) -> str:
    pr, pc = game_state.player_pos
    end_pos = game_state.end_pos
    lives = game_state.lives
    skips = game_state.skips_remaining

    current_dist = _manhattan_dist((pr, pc), end_pos)
    candidates = []

    # Анализ 1-го хода
    for name, (dr, dc) in DIRECTIONS.items():
        r1, c1 = pr + dr, pc + dc
        risk1 = _cell_risk(game_state, r1, c1)
        if risk1 == 2:
            continue  # непроходимо

        new_dist = _manhattan_dist((r1, c1), end_pos)
        progress = current_dist - new_dist  # >0 = ближе к финишу

        # Оценка: приоритет — безопасность, затем прогресс
        score = 0
        if risk1 == 0:
            score = 100 + progress  # безопасные ходы в приоритете
        elif risk1 == 1 and lives > 1:
            score = 50 + progress  # рискованные — только если есть жизни

        if score > 0:
            candidates.append((score, name, risk1, r1, c1))

    # Сортируем по убыванию оценки
    candidates.sort(key=lambda x: x[0], reverse=True)

    if candidates:
        _, best_move, risk, r1, c1 = candidates[0]
        # Анализ 2-го хода для уточнения
        if risk == 0:
            # Ищем, есть ли безопасный второй ход к цели
            next_dist = _manhattan_dist((r1, c1), end_pos)
            for name2, (dr2, dc2) in DIRECTIONS.items():
                r2, c2 = r1 + dr2, c1 + dc2
                risk2 = _cell_risk(game_state, r2, c2)
                if risk2 == 0:
                    new_next_dist = _manhattan_dist((r2, c2), end_pos)
                    if new_next_dist < next_dist:
                        return f"Иди {best_move}, затем {name2} — путь безопасен и ведёт к финишу."
            return f"Иди {best_move} — безопасно и ближе к финишу."
        else:
            return f"Рискни: иди {best_move}. Это приблизит тебя к цели."

    # Если нет безопасных/прогрессивных ходов — проверим просто безопасные
    safe_moves = []
    for name, (dr, dc) in DIRECTIONS.items():
        r1, c1 = pr + dr, pc + dc
        if _cell_risk(game_state, r1, c1) == 0:
            safe_moves.append(name)
    if safe_moves:
        return f"Иди {safe_moves[0]} — путь безопасен."

    # Если всё плохо — предложим пропуск или сдачу
    if skips > 0:
        return "Используй пропуск хода: число уменьшится и путь откроется."
    return "Все ходы опасны. Перезапусти уровень."