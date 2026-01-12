from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsScene, QGraphicsTextItem
from PyQt5.QtGui import QColor, QBrush, QFont, QPixmap, QPen
from PyQt5.QtCore import Qt
import os, random

class CoorCell:
    row = -1
    col = -1

class CellStyle:
    def updateDigitalCell(self,
                    scene,
                    r,
                    c,
                    cell_size,
                    name):
        item = QGraphicsTextItem(name)
        item.setFont(QFont("Arial", 7, QFont.Bold))
        item.setDefaultTextColor(Qt.white)
        item.setPos(
            c * cell_size + cell_size - item.boundingRect().width(),
            r * cell_size + 0
        )
        scene.addItem(item)

    def updateLeftCell(self,
                    scene,
                    visibility,
                    r,
                    c,
                    cell_size,
                    name):
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

    def updateColorCell(self,
                    scene,
                    cell_size,
                    r,
                    c,
                    color):
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
    
    def updateObject(self,
                    scene,
                    fixed_grid,
                    rows,
                    cols,
                    cell_size,
                    state,
                    name) -> CoorCell:
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

    def updateTextureCell(self,
                      scene,
                      r,
                      c,
                      cell_size,
                      name):
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

    def updateTexture(self,
                      scene,
                      fixed_grid,
                      rows,
                      cols,
                      cell_size,
                      actions,
                      parametr,
                      state,
                      name):
        
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