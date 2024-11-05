from PyQt5.QtWidgets import (QMainWindow, QGraphicsLineItem, QLineEdit, QWidget,
                            QLabel, QComboBox, QGridLayout, QToolTip,
                            QGraphicsScene, QGraphicsView, QPushButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen
from modules.grid import GridItem
import time
import math

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.state = 0
        self.lines = [] 

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.layout = QGridLayout()
        
        self.setup_canvas()
        self.setup_algorithm_dropdown()
        self.setup_coords_chooser()
        self.setup_time_label()

        central_widget.setLayout(self.layout)

        self.max_coord = (self.grid_size // self.grid_spacing) - 1

    def setup_canvas(self):
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)

        self.grid_size = 2500
        self.grid_spacing = 25

        self.grid_item = GridItem(self.grid_size, self.grid_spacing)
        self.scene.addItem(self.grid_item)

        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setMouseTracking(True)
        self.view.viewport().setMouseTracking(True)
        self.view.setRenderHint(QPainter.Antialiasing, True)
        self.view.scale(1, 1)

        self.set_view_events()
        self.layout.addWidget(self.view, 0, 0, 1, 6)

    def set_view_events(self):
        def mouseMoveEvent(event):
            pos = event.pos()
            scene_pos = self.view.mapToScene(pos)
            tooltip_text = f"x: {int(scene_pos.x() // self.grid_spacing)}, y: {int(scene_pos.y() // self.grid_spacing)}"
            pos = self.mapToGlobal(pos)
            QToolTip.showText(pos, tooltip_text, self)

        def wheel_event(event):
            factor = 1.1
            if event.angleDelta().y() < 0:
                factor = 1.0 / factor
            self.view.scale(factor, factor)

        self.view.mouseMoveEvent = mouseMoveEvent
        self.view.wheelEvent = wheel_event

    def setup_coords_chooser(self):
        x0_label = QLabel('x0:')
        y0_label = QLabel('y0:')
        x1_label = QLabel('x1:')
        y1_label = QLabel('y1:')

        self.x0_edit = QLineEdit()
        self.y0_edit = QLineEdit()
        self.x1_edit = QLineEdit()
        self.y1_edit = QLineEdit()

        self.draw_button = QPushButton('Draw')
        self.draw_button.clicked.connect(self.draw_button_toggled)

        self.layout.addWidget(x0_label, 1, 1)
        self.layout.addWidget(y0_label, 2, 1)
        self.layout.addWidget(x1_label, 1, 3)
        self.layout.addWidget(y1_label, 2, 3)

        self.layout.addWidget(self.x0_edit, 1, 2)
        self.layout.addWidget(self.y0_edit, 2, 2)
        self.layout.addWidget(self.x1_edit, 1, 4)
        self.layout.addWidget(self.y1_edit, 2, 4)

        self.layout.addWidget(self.draw_button, 1, 5, 1, 1)
        self.clear_button = QPushButton('Clear')
        self.clear_button.clicked.connect(self.clear_scene)
        self.layout.addWidget(self.clear_button, 2, 5, 1, 1)
    
    def setup_time_label(self):
        self.time_label = QLabel('Time: ')
        self.layout.addWidget(self.time_label, 3, 0)

    def setup_algorithm_dropdown(self):
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems([
            'Пошаговый алгоритм',
            'Алгоритм ЦДА',
            'Алгоритм Брезенхема',
            'Алгоритм Брезенхема (окружность)'
        ])
        self.algorithm_combo.currentIndexChanged.connect(self.set_algorithm_state)
        self.layout.addWidget(self.algorithm_combo, 1, 0)

    def clear_scene(self):
        for line in self.lines:
            self.scene.removeItem(line)
        self.lines.clear()
        self.grid_item.clear_cells()
        self.time_label.setText('Time: ')

    def draw_line(self, x0, y0, x1, y1):
        line_item = QGraphicsLineItem(self.convert_x_center(x0), self.convert_y_center(y0), 
                                      self.convert_x_center(x1), self.convert_y_center(y1))
        pen = QPen(Qt.blue)
        line_item.setPen(pen)
        self.scene.addItem(line_item)
        self.lines.append(line_item)

    def draw_button_toggled(self):
        x0 = int(self.x0_edit.text())
        y0 = int(self.y0_edit.text())
        x1 = int(self.x1_edit.text())
        y1 = int(self.y1_edit.text())

        x0 = max(0, min(x0, self.max_coord))
        y0 = max(0, min(y0, self.max_coord))
        x1 = max(0, min(x1, self.max_coord))
        y1 = max(0, min(y1, self.max_coord))

        self.x0_edit.setText(str(x0))
        self.y0_edit.setText(str(y0))
        self.x1_edit.setText(str(x1))
        self.y1_edit.setText(str(y1))

        self.draw_line(x0, y0, x1, y1)
        
        start_time = time.perf_counter()
        if self.state == 0:
            self.step_algorithm(x0, y0, x1, y1)
        elif self.state == 1:
            self.dda_algorithm(x0, y0, x1, y1)
        elif self.state == 2:
            self.brezenhem_algorithm(x0, y0, x1, y1)
        elif self.state == 3:
            radius = int(math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2))
            self.brezenhem_circle(x0, y0, radius)
        end_time = time.perf_counter()

        delta_time = (end_time - start_time) * 1e6
        self.time_label.setText('Time: ' + str(round(delta_time, 2)) + ' microseconds')

    def step_algorithm(self, x0, y0, x1, y1):
        if x1 == x0:  
            step_y = 1 if y1 > y0 else -1
            y = y0
            for _ in range(abs(y1 - y0) + 1):
                self.brush_cell(x0, y)
                y += step_y
        else:
            k = (y1 - y0) / (x1 - x0)  
            b = y0 - k * x0

            steps = max(abs(x1 - x0), abs(y1 - y0))
            step_x = (x1 - x0) / steps
            step_y = (y1 - y0) / steps
            
            x = x0
            for _ in range(steps + 1):
                y = round(k * x + b)
                self.brush_cell(x, y)
                x += step_x

    def dda_algorithm(self, x0, y0, x1, y1):
        steps = max(abs(x1 - x0), abs(y1 - y0))
        dx, dy = (x1 - x0) / steps, (y1 - y0) / steps
        x, y = x0, y0
        for _ in range(steps + 1):
            self.brush_cell(round(x), round(y))
            x += dx
            y += dy

    def brezenhem_algorithm(self, x0, y0, x1, y1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        lx = 1 if x0 < x1 else -1
        ly = 1 if y0 < y1 else -1
        error = dx - dy

        while True:
            self.brush_cell(x0, y0)
            if x0 == x1 and y0 == y1:
                break
            e2 = error * 2
            if e2 > -dy:
                error -= dy
                x0 += lx
            if e2 < dx:
                error += dx
                y0 += ly

    def brezenhem_circle(self, xc, yc, r):
        def plot_circle_points(xc, yc, x, y):
            for dx, dy in [(x, y), (-x, y), (x, -y), (-x, -y), (y, x), (-y, x), (y, -x), (-y, -x)]:
                self.brush_cell(xc + dx, yc + dy)

        x, y = 0, r
        d = 3 - 2 * r
        while y >= x:
            plot_circle_points(xc, yc, x, y)
            x += 1  
            if d > 0:
                y -= 1
                d += 4 * (x - y) + 10
            else:
                d += 4 * x + 6
     
    def convert_x(self, x):
        return x * self.grid_spacing

    def convert_y(self, y):
        return y * self.grid_spacing 
    
    def convert_x_center(self, x):
        return x * self.grid_spacing + self.grid_spacing // 2

    def convert_y_center(self, y):
        return y * self.grid_spacing + self.grid_spacing // 2

    def brush_cell(self, x, y):
        x = self.convert_x_center(x)
        y = self.convert_y_center(y)
        self.grid_item.add_cell(x // self.grid_item.spacing * self.grid_item.spacing,
                               y // self.grid_item.spacing * self.grid_item.spacing)

    def set_algorithm_state(self, index):
        self.state = index