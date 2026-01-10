# ui/settings_dialog_random_lab.py

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QHBoxLayout
from PyQt5.QtWidgets import QSpinBox, QCheckBox, QPushButton, QLabel
from core.game_state import GameOptions
from ui.style import COSMIC_STYLE

class SettingsDialoRandomLab(QDialog):
####### ИНИЦИАЛИЗАЦИЯ ОКНА #######
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки случайного уровня")
        self.setStyleSheet(COSMIC_STYLE)
        self.resize(500, 600)
        self.options = GameOptions()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Информация
        info_label = QLabel(f"ℹ️ Количество пропусков хода («Следующий шаг»): {self.options.max_skips}")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Размер поля
        size_layout = QHBoxLayout()
        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(5, 20)
        self.rows_spin.setValue(self.options.rows)
        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(5, 30)
        self.cols_spin.setValue(self.options.cols)
        size_layout.addWidget(QLabel("Строки:"))
        size_layout.addWidget(self.rows_spin)
        size_layout.addWidget(QLabel("Столбцы:"))
        size_layout.addWidget(self.cols_spin)
        layout.addLayout(size_layout)

        # Диапазон начальных чисел
        range_layout = QHBoxLayout()
        self.min_val_spin = QSpinBox()
        self.min_val_spin.setRange(1, 100)
        self.min_val_spin.setValue(17)
        self.max_val_spin = QSpinBox()
        self.max_val_spin.setRange(1, 1000)
        self.max_val_spin.setValue(30)
        range_layout.addWidget(QLabel("Мин. число:"))
        range_layout.addWidget(self.min_val_spin)
        range_layout.addWidget(QLabel("Макс. число:"))
        range_layout.addWidget(self.max_val_spin)
        self.min_val_spin.valueChanged.connect(self.validate_range)
        self.max_val_spin.valueChanged.connect(self.validate_range)
        layout.addLayout(range_layout)

        # Опции CCA
        layout.addWidget(QLabel("Опции клеточного автомата:"))

        self.checkboxes = {}
        checkbox_config = [
            ("Число 4 замораживает соседей", "four_steals_neighbors"),
            # ("Ускорение рядом с магистралью", "neighbors_affect_speed"),
            # ("Чётные замораживаются, если окружены нечётными", "even_steal_energy"),
            # ("Нечётные делают 2 шага, если окружены чётными", "odd_jump_if_surrounded_by_even"),
            # ("Использовать 8 соседей", "use_8_neighbors"),
            # ("Только чётные обновляются, если есть r%6==0", "only_even_update_if_r6"),
            # ("Только нечётные обновляются, если есть r%6==3", "only_odd_update_if_r3"),
            # ("Чётные +2, если есть подпространство 6", "even_numbers_add_2_if_sub6"),
        ]

        form = QFormLayout()
        for label, attr in checkbox_config:
            cb = QCheckBox(label)
            cb.setChecked(getattr(self.options, attr))
            form.addRow(cb)
            self.checkboxes[attr] = cb
        layout.addLayout(form)

        # Пустота
        self.randomize_at_4_checkbox = QCheckBox("Обновлять при достижении числа 4")
        self.randomize_at_4_checkbox.setChecked(True)
        layout.addWidget(self.randomize_at_4_checkbox)

        # === Игровые свойства ===
        layout.addWidget(QLabel("Свойства игры:"))
        self.cb_hardcore = QCheckBox("Хардкор (1 жизнь)")
        # self.cb_noregen = QCheckBox("Не перегенерировать при 1")
        layout.addWidget(self.cb_hardcore)
        # layout.addWidget(self.cb_noregen)

        # Пустота
        empty_layout = QHBoxLayout()
        self.empty_checkbox = QCheckBox("Пустота")
        self.empty_spin = QSpinBox()
        self.empty_spin.setRange(1, 4)
        self.empty_spin.setValue(1)
        layout.addWidget(self.empty_checkbox)
        empty_layout.addWidget(QLabel("Количество случайых пустот:"))
        empty_layout.addWidget(self.empty_spin)
        layout.addLayout(empty_layout)

        # Туман войны
        fog_layout = QHBoxLayout()
        self.fog_checkbox = QCheckBox("Туман войны")
        self.fog_spin = QSpinBox()
        self.fog_spin.setRange(1, 20)
        self.fog_spin.setValue(1)
        layout.addWidget(self.fog_checkbox)
        fog_layout.addWidget(QLabel("Радиус видимости в тумане войны:"))
        fog_layout.addWidget(self.fog_spin)
        layout.addLayout(fog_layout)

        self.masks_checkbox = QCheckBox("Режим масок")
        layout.addWidget(self.masks_checkbox)

        # === Кнопки ===
        btn_ok = QPushButton("Начать игру")
        btn_cancel = QPushButton("Отмена")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
####### ИНИЦИАЛИЗАЦИЯ ОКНА #######



####### ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ #######
    def validate_range(self):
        if self.min_val_spin.value() > self.max_val_spin.value():
            self.max_val_spin.setValue(self.min_val_spin.value())

    def get_options(self) -> GameOptions:
        """Возвращает настроенные опции."""
        opts = GameOptions()
        opts.rows = self.rows_spin.value()
        opts.cols = self.cols_spin.value()
        for attr, cb in self.checkboxes.items():
            setattr(opts, attr, cb.isChecked())
        opts.hardcore = self.cb_hardcore.isChecked()
        opts.min_initial_value = self.min_val_spin.value()
        opts.max_initial_value = self.max_val_spin.value()

        opts.randomize_at_4 = self.randomize_at_4_checkbox.isChecked()
        opts.generate_empty = self.empty_checkbox.isChecked()
        opts.visibility_radius = self.empty_spin.value()
        opts.fog_of_war = self.fog_checkbox.isChecked()
        opts.visibility_radius = self.fog_spin.value()
        self.options.use_masks = self.masks_checkbox.isChecked()
        opts.border_void = True
        # opts.disable_regen_at_1 = self.cb_noregen.isChecked()
        return opts
####### ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ #######