from PyQt5.QtWidgets import  QGraphicsItem
from PyQt5.QtCore import Qt, QRectF, QPoint
from PyQt5.QtGui import QBrush, QFont

class GridItem(QGraphicsItem):
    def __init__(self, size, spacing):
        super(GridItem, self).__init__()

        self.size = size
        self.spacing = spacing
        self.cell_size = spacing
        self.cells = []
        self.pixels = []

    def setup_grid(self, painter):
        pen = painter.pen()
        pen.setColor(Qt.lightGray)
        painter.setPen(pen)

        # вертикальные линии сетки
        for i in range(0, self.size, self.spacing):
            painter.drawLine(i, 0, i, self.size)

        # горизонтальные линии сетки
        for i in range(0, self.size, self.spacing):
            painter.drawLine(0, i, self.size, i)

        pen_axis = painter.pen()
        pen_axis.setColor(Qt.black)
        painter.setPen(pen_axis)

        # система координат
        painter.drawLine(0, 0, 0, self.size)
        painter.drawLine(0, 0, self.size, 0)
        number_size = self.spacing // 5
        painter.setFont(QFont('Arial', number_size))

        x_delta = self.spacing // 4
        y_delta = self.spacing // 2

        # числовые метки по оси х
        for i in range(0, self.size, self.spacing):
            temp = i // self.spacing
            painter.drawText(QPoint(i + x_delta, y_delta), str(temp))
            painter.drawLine(0, i, 3, i)

        # числовые метки по оси у
        for i in range(0, self.size, self.spacing):
            temp = i // self.spacing
            if (temp > 0):
                painter.drawText(QPoint(x_delta, i + 2 + y_delta), str(temp))
            painter.drawLine(i, 0, i, 3)

        painter.setFont(QFont('Arial', 12))
        painter.drawText(QPoint(self.size, 30), 'x')
        painter.drawText(QPoint(-30, self.size), 'y')

    def boundingRect(self):
        return QRectF(0, 0, self.size, self.size)

    # сетка + закрашивание клеток
    def paint(self, painter, option, widget):
        self.setup_grid(painter)

        pen = painter.pen()
        pen.setColor(Qt.lightGray)
        painter.setPen(pen)

        brush = QBrush(Qt.gray, Qt.SolidPattern)
        painter.setBrush(brush)

        for cell in self.cells:
            painter.drawRect(cell)

    def add_cell(self, x, y):
        cell_rect = QRectF(x, y, self.cell_size, self.cell_size)
        self.cells.append(cell_rect)
        self.update()

    def clear_cells(self):
        self.cells = []
        self.update()