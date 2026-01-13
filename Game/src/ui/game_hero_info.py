from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGroupBox

def setWindowLegend(right_layout):
    legend_group = QGroupBox("Легенда")
    legend_layout = QVBoxLayout(legend_group)
    legend_items = [
        ("#1A2332", "🌍 Чётное число"),
        ("#8B2E3C", "💥 Нечётное число"),
        ("#C07B3B", "🕳️ Цикл (1, 2, 4)"),
        ("#2A4B8C", "🔵 Старт / Финиш"),
        ("#FF4444", "⏲️ Давление"),
        ("#6A4C93", "💎 Кристалл"),
        ("#B5651D", "🛠️ Крафт"),
        ("#000000", "⬛ Пустота")
    ]
    for color_hex, text in legend_items:
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(5)
        color_square = QLabel()
        color_square.setFixedSize(16, 16)
        color_square.setStyleSheet(f"background-color: {color_hex}; border: 1px solid #888;")
        label_text = QLabel(text)
        label_text.setStyleSheet("padding-left: 5px; color: #C0D0FF;")
        row_layout.addWidget(color_square)
        row_layout.addWidget(label_text)
        row_layout.addStretch()
        legend_layout.addWidget(row_widget)
    right_layout.addWidget(legend_group)


class GameHeroInfo:
    def createInfo(self, right_layout, state):
        hud_grid = QGridLayout()
        hud_grid.setSpacing(5)

        # Левая колонка
        self.m_lifeLabel = QLabel("❤️ Жизни: 2")
        self.m_defenseLabel = QLabel("🛡️ Защита: 1")
        self.m_skipLabel = QLabel("⏭️ Пропуски: 2")
        self.m_freezeLabel = QLabel(f"❄️ Заморозка: 0")
        self.m_pressureLabel = QLabel("⏲️ Давление: 200")
        self.m_undoLabel = QLabel(f"↩️ Откаты: 0")
        self.m_difficultyLabel = QLabel("🧩 Сложность: 0")

        # Добавляем в сетку
        hud_grid.addWidget(self.m_lifeLabel, 0, 0)
        hud_grid.addWidget(self.m_defenseLabel, 1, 0)
        hud_grid.addWidget(self.m_skipLabel, 2, 0)
        hud_grid.addWidget(self.m_freezeLabel, 3, 0)
        hud_grid.addWidget(self.m_pressureLabel, 4, 0)
        hud_grid.addWidget(self.m_undoLabel, 5, 0)
        hud_grid.addWidget(self.m_difficultyLabel, 6, 0)

        # Правая колонка
        self.m_crystalLabel = QLabel("💎 Кристаллы: 0")
        self.m_craftLabel = QLabel("🛠️ Крафт: 0")
        self.m_mask_attempts = QLabel("👀 Ясновидение: 3")

        hud_grid.addWidget(self.m_crystalLabel, 0, 1)
        hud_grid.addWidget(self.m_craftLabel, 1, 1)
        hud_grid.addWidget(self.m_mask_attempts, 2, 1)

        if (state == 2):
            self.m_crystalLabel.hide()
            self.m_craftLabel.hide()
            self.m_mask_attempts.hide()

        right_layout.addLayout(hud_grid)

    def update_hud(self, gameState):
        """Обновляет все элементы HUD."""
        self.m_lifeLabel.setText(f"❤️ Жизни: {gameState.lives}")
        self.m_defenseLabel.setText(f"🛡️ Защита: {gameState.defense}")
        self.m_skipLabel.setText(f"⏭️ Пропуски: {gameState.max_skips}")
        self.m_freezeLabel.setText(f"❄️ Заморозка: {gameState.freeze_cell}")
        available = min(len(gameState.state_history), gameState.max_undo)
        self.m_undoLabel.setText(f"↩️ Откаты: {available}/{gameState.max_undo}")
        self.m_pressureLabel.setText(f"⏲️ Давление: {gameState.pressure_tolerance}")
        self.m_crystalLabel.setText(f"💎 Кристаллы: {gameState.crystals}")
        self.m_craftLabel.setText(f"🛠️ Крафт: {gameState.craftedCells}")
        self.m_mask_attempts.setText(f"👀 Ясновидение: {3 - gameState.mask_attempts}/3")
        self.m_difficultyLabel.setText(f"🧩 Сложность: {gameState.calculate_difficulty()}")

