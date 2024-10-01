import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFrame, QLabel, QPushButton, QColorDialog, QGridLayout, QWidget, QLineEdit, QSlider
from PyQt5.QtCore import Qt
from color_converter import ColorConverter

class ColorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.r, self.g, self.b, self.c, self.m, self.yy, self.k, self.h, self.s, self.v = [0] * 10

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.layout = QGridLayout()
        central_widget.setLayout(self.layout)

        self.create_labels()
        self.create_sliders_and_line_edits()
        self.set_widgets_position()
        self.create_color_rectangle()
        self.create_palette_button()

    def create_color_rectangle(self):
        self.rectangle = QFrame()
        self.rectangle.setFrameShape(QFrame.Box)
        self.rectangle.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.layout.addWidget(self.rectangle, 0, 6, 9, 5)

    def create_palette_button(self):
        self.color_button = QPushButton('Choose color')
        self.color_button.clicked.connect(self.show_color_dialog)
        self.layout.addWidget(self.color_button, 9, 6, 1, 5)

    def show_color_dialog(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.r, self.g, self.b = color.red(), color.green(), color.blue()
            self.update_from_rgb()

    def create_labels(self):
        names = ['C:', 'M:', 'Y:', 'K:', 'R:', 'G:', 'B:', 'H:', 'S:', 'V:']
        self.labels = [QLabel(name) for name in names]

    def create_slider(self, min_val, max_val, handler):
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_val, max_val)
        slider.valueChanged.connect(handler)
        return slider
    
    def create_line_edit(self, handler):
        linedit = QLineEdit()
        linedit.setFixedWidth(35)
        linedit.editingFinished.connect(handler)
        return linedit

    def create_sliders_and_line_edits(self):
        self.cmyk_sliders = [self.create_slider(0, 100, self.update_from_cmyk_slider) for _ in range(4)]
        self.rgb_sliders = [self.create_slider(0, 255, self.update_from_rgb_slider) for _ in range(3)]
        self.hsv_sliders = [self.create_slider(0, 360, self.update_from_hsv_slider),  
                            self.create_slider(0, 100, self.update_from_hsv_slider),   
                            self.create_slider(0, 100, self.update_from_hsv_slider)]  

        self.cmyk_linedits = [self.create_line_edit(self.update_from_cmyk_linedit) for _ in range(4)]
        self.rgb_linedits = [self.create_line_edit(self.update_from_rgb_linedit) for _ in range(3)]
        self.hsv_linedits = [self.create_line_edit(self.update_from_hsv_linedit) for _ in range(3)]

    def set_widgets_position(self):
        for i, label in enumerate(self.labels):
            self.layout.addWidget(label, i, 0)

        for i, slider in enumerate(self.cmyk_sliders + self.rgb_sliders + self.hsv_sliders):
            self.layout.addWidget(slider, i, 2, 1, 4)

        for i, linedit in enumerate(self.cmyk_linedits + self.rgb_linedits + self.hsv_linedits):
            self.layout.addWidget(linedit, i, 1)

    def update_sliders_and_linedits(self):
        self.block_signals(True)

        sliders = self.cmyk_sliders + self.rgb_sliders + self.hsv_sliders
        values = [self.c, self.m, self.yy, self.k, self.r, self.g, self.b, self.h, self.s, self.v]
        for slider, value in zip(sliders, values):
            slider.setValue(int(value))

        linedits = self.cmyk_linedits + self.rgb_linedits + self.hsv_linedits
        for linedit, value in zip(linedits, values):
            linedit.setText(str(int(value)))

        self.rectangle.setStyleSheet(f"background-color: rgb({self.r}, {self.g}, {self.b});")

        self.block_signals(False)

    def block_signals(self, is_block):
        for slider in self.cmyk_sliders + self.rgb_sliders + self.hsv_sliders:
            slider.blockSignals(is_block)
        for linedit in self.cmyk_linedits + self.rgb_linedits + self.hsv_linedits:
            linedit.blockSignals(is_block)

    def update_from_cmyk(self):
        self.r, self.g, self.b = ColorConverter.cmyk_to_rgb(self.c, self.m, self.yy, self.k)
        self.h, self.s, self.v = ColorConverter.rgb_to_hsv(self.r, self.g, self.b)
        self.update_sliders_and_linedits()

    def update_from_rgb(self):
        self.c, self.m, self.yy, self.k = ColorConverter.rgb_to_cmyk(self.r, self.g, self.b)
        self.h, self.s, self.v = ColorConverter.rgb_to_hsv(self.r, self.g, self.b)
        self.update_sliders_and_linedits()

    def update_from_hsv(self):
        self.r, self.g, self.b = ColorConverter.hsv_to_rgb(self.h, self.s, self.v)
        self.c, self.m, self.yy, self.k = ColorConverter.rgb_to_cmyk(self.r, self.g, self.b)
        self.update_sliders_and_linedits()

    # handlers
    def update_from_cmyk_slider(self):
        self.c, self.m, self.yy, self.k = [s.value() for s in self.cmyk_sliders]
        self.update_from_cmyk()

    def update_from_rgb_slider(self):
        self.r, self.g, self.b = [s.value() for s in self.rgb_sliders]
        self.update_from_rgb()

    def update_from_hsv_slider(self):
        self.h, self.s, self.v = [s.value() for s in self.hsv_sliders]
        self.update_from_hsv()

    def update_from_cmyk_linedit(self):
        self.c, self.m, self.yy, self.k = [self.validate(l.text(), 0, 100) for l in self.cmyk_linedits]
        self.update_from_cmyk()

    def update_from_rgb_linedit(self):
        self.r, self.g, self.b = [self.validate(l.text(), 0, 255) for l in self.rgb_linedits]
        self.update_from_rgb()

    def update_from_hsv_linedit(self):
        self.h = self.validate(self.hsv_linedits[0].text(), 0, 360)
        self.s = self.validate(self.hsv_linedits[1].text(), 0, 100)
        self.v = self.validate(self.hsv_linedits[2].text(), 0, 100)
        self.update_from_hsv()

    def validate(self, value, min_val, max_val):
        try:
            val = int(float(value))
            val = max(min_val, min(val, max_val))
        except ValueError:
            val = min_val
        return val

def main():
    app = QApplication(sys.argv)
    window = ColorApp()
    window.setWindowTitle("Color Picker")
    window.setGeometry(100, 100, 400, 200)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
