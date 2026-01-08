# ui/arena_settings_dialog.py

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QSpinBox, QDialogButtonBox, QLabel
from core.game_state import GameOptions

class ArenaSettingsDialog(QDialog):
    def __init__(self, parent=None, default_stats=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки арены")
        self.setModal(True)
        self.resize(300, 200)

        default_stats = default_stats or {}
        lives = default_stats.get("lives", 3)
        skips = default_stats.get("max_skips", 2)
        pressure = default_stats.get("pressure_tolerance", 200)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Настройте начальные параметры арены"))

        form = QFormLayout()

        self.lives_spin = QSpinBox()
        self.lives_spin.setRange(1, 10)
        self.lives_spin.setValue(lives)
        form.addRow("Начальные жизни:", self.lives_spin)

        self.skips_spin = QSpinBox()
        self.skips_spin.setRange(0, 10)
        self.skips_spin.setValue(skips)
        form.addRow("Начальные пропуски:", self.skips_spin)

        self.pressure_spin = QSpinBox()
        self.pressure_spin.setRange(50, 1000)
        self.pressure_spin.setSingleStep(10)
        self.pressure_spin.setValue(pressure)
        form.addRow("Допустимое давление:", self.pressure_spin)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_options(self) -> GameOptions:
        """Возвращает GameOptions в режиме арены."""
        return GameOptions(
            mode="arena",
            # arena_start_lives=self.lives_spin.value(),
            # arena_start_skips=self.skips_spin.value(),
            # arena_start_pressure=self.pressure_spin.value(),
        )