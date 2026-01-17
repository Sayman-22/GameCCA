# ui/mask_view.py
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem
from PyQt5.QtWidgets import QMessageBox, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush, QPainter
from ui.style import COSMIC_STYLE
from core.update_cell import CellStyle

class MaskView(QGraphicsView):
    def __init__(self, game_state):
        super().__init__()
        self.game_state = game_state
        self.setStyleSheet(COSMIC_STYLE)
        self.scene = QGraphicsScene()
        self.cellStyle = CellStyle()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor("#0B0F1F")))
        self.cell_size = 60
        self.parent_window = None
        self.active_line_edit = None

    def update_view(self):
        if self.game_state is None:
            return

        self.scene.clear()
        rows, cols = self.game_state.getRows(), self.game_state.getCols()
        mask_grid = self.game_state.getMaskGrid()

        for r in range(rows):
            for c in range(cols):
                value = self.game_state.grid[r][c]
                item = QGraphicsRectItem(c * self.cell_size, r * self.cell_size, self.cell_size, self.cell_size)

                # Ячейки с отрицательными значениями — не могут быть масками
                if value <= 0:
                    item.setBrush(QColor("#2A2A2A"))
                    item.setPen(QColor("#888"))
                elif self.game_state.getParUseMasks() and mask_grid[r][c]:
                    self.cellStyle.updateColorCell(self.scene, self.cell_size, c, r, "#4A4A4A")
                    self.cellStyle.updateObjectCell(self.scene, r, c, self.cell_size, "?")
                else:
                    item.setBrush(QColor("#2A2A2A"))
                    item.setPen(QColor("#888"))

                self.scene.addItem(item)

        # Устанавливаем размер сцены
        self.setSceneRect(0, 0, cols * self.cell_size, rows * self.cell_size)

    def mousePressEvent(self, event):
        pos = self.mapToScene(event.pos())
        c = int(pos.x() // self.cell_size)
        r = int(pos.y() // self.cell_size)

        if (0 <= r < self.game_state.getRows() and 0 <= c < self.game_state.getCols()):
            if self.game_state.getParUseMasks() and self.game_state.mask_grid[r][c]:
                # Если уже есть активное поле ввода — закрываем его
                if self.active_line_edit:
                    self.active_line_edit.deleteLater()
                    self.active_line_edit = None

                # Создаём QLineEdit
                line_edit = QLineEdit(self.parent_window)
                line_edit.setFixedSize(self.cell_size, self.cell_size)
                line_edit.setAlignment(Qt.AlignCenter)
                line_edit.setFocus()

                # Позиционируем относительно сцены
                scene_pos = self.mapFromScene(c * self.cell_size, r * self.cell_size)
                line_edit.move(scene_pos.x(), scene_pos.y())

                line_edit.returnPressed.connect(lambda: self.on_mask_guess(line_edit, r, c))
                line_edit.show()
                self.active_line_edit = line_edit  # сохраняем ссылку

    def on_mask_guess(self, line_edit, r, c):
        try:
            guess = int(line_edit.text())
        except ValueError:
            line_edit.deleteLater()
            self.active_line_edit = None
            return

        result = self.game_state.check_mask_guess(r, c, guess)
        if result == "correct":
            line_edit.setStyleSheet("background-color: #2E7D32; color: white;")
            self.update_view()
            self.parent_window.update_hud()
            self.parent_window.m_glWidget.update_view()
            QMessageBox.information(self.parent_window, "Успех!", "Вы угадали число!\n+3 кристалла!")
        elif result == "wrong":
            line_edit.setStyleSheet("background-color: #C62828; color: white;")
            self.parent_window.m_infoLabel.setText(f"Ошибка! Осталось попыток: {3 - self.game_state.mask_attempts}")
            self.parent_window.update_hud()
        elif result == "game_over":
            self.parent_window.handle_defeat()

        line_edit.deleteLater()
        self.active_line_edit = None