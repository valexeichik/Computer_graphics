import sys
import cv2
import numpy as np
import skimage
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                             QFileDialog, QVBoxLayout, QWidget, QHBoxLayout, QRadioButton, QButtonGroup)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt


class ImageFilterApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Filter image")
        self.resize(1200, 600)

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        self.original_image_label = QLabel(self)
        self.filtered_image_label = QLabel(self)

        self.original_image_label.setAlignment(Qt.AlignCenter)
        self.filtered_image_label.setAlignment(Qt.AlignCenter)

        self.load_button = QPushButton("Load image", self)
        self.load_button.clicked.connect(self.load_image)

        self.niblack_radio = QRadioButton("Niblack", self)
        self.niblack_radio.setChecked(True)
        self.bernsen_radio = QRadioButton("Bernsen", self)
        self.segmentation_radio = QRadioButton("Segmentation", self)

        self.filter_group = QButtonGroup(self)
        self.filter_group.addButton(self.niblack_radio)
        self.filter_group.addButton(self.bernsen_radio)
        self.filter_group.addButton(self.segmentation_radio)

        self.apply_button = QPushButton("Apply filter", self)
        self.apply_button.clicked.connect(self.apply_filter)

        self.save_button = QPushButton("Save filtered image", self)
        self.save_button.clicked.connect(self.save_image)
        self.save_button.setEnabled(False)  

        image_layout = QHBoxLayout()
        image_layout.addWidget(self.original_image_label)
        image_layout.addWidget(self.filtered_image_label)

        control_layout = QVBoxLayout()
        control_layout.addWidget(self.load_button)

        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.niblack_radio)
        radio_layout.addWidget(self.bernsen_radio)
        radio_layout.addWidget(self.segmentation_radio)

        control_layout.addLayout(radio_layout)
        control_layout.addWidget(self.apply_button)
        control_layout.addWidget(self.save_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(image_layout)
        main_layout.addLayout(control_layout)

        self.main_widget.setLayout(main_layout)

        self.original_image = None
        self.filtered_image = None

    def load_image(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "Open image", os.getcwd(), "Image files (*.png *.jpg *.bmp)")
        if image_path:
            self.original_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            self.display_image(self.original_image, self.original_image_label)

    def display_image(self, image, label):
        height, width = image.shape
        bytes_per_line = width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)

        pixmap = QPixmap.fromImage(q_image).scaled(label.width(), label.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(pixmap)

    def save_image(self):
        if self.filtered_image is not None:
            save_path, _ = QFileDialog.getSaveFileName(self, "Save image", os.getcwd(), "PNG files (*.png);;JPEG Files (*.jpg);;BMP Files (*.bmp)")
            if save_path:
                cv2.imwrite(save_path, self.filtered_image)

    def apply_filter(self):
        if self.original_image is None:
            return

        if self.niblack_radio.isChecked():
            self.apply_niblack()
        elif self.bernsen_radio.isChecked():
            self.apply_bernsen()
        elif self.segmentation_radio.isChecked():
            self.apply_segmentation()

        self.display_image(self.filtered_image, self.filtered_image_label)
        self.save_button.setEnabled(True)

    def apply_niblack(self):
        thresh_niblack = skimage.filters.threshold_niblack(self.original_image, window_size=15, k=-0.2)
        binary_niblack = self.original_image > thresh_niblack
        self.filtered_image = (binary_niblack * 255).astype(np.uint8) 

    def apply_bernsen(self):
        window_size = 10
        half_window = window_size // 2
        self.filtered_image = np.zeros_like(self.original_image)

        float_image = self.original_image.astype(np.float32)

        for i in range(half_window, self.original_image.shape[0] - half_window):
            for j in range(half_window, self.original_image.shape[1] - half_window):
                local_region = float_image[i-half_window:i+half_window+1, j-half_window:j+half_window+1]

                local_min = np.min(local_region)
                local_max = np.max(local_region)

                threshold = (local_min + local_max) / 2

                self.filtered_image[i, j] = 255 if float_image[i, j] > threshold else 0

    def apply_segmentation(self):
        self.filtered_image = np.copy(self.original_image)
        edges = cv2.Canny(self.original_image, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(self.filtered_image, contours, -1, (255, 255, 255), 2)

        gray = np.float32(self.original_image)
        dst = cv2.cornerHarris(gray, blockSize=2, ksize=3, k=0.04)
        dst = cv2.dilate(dst, None)
        self.filtered_image[dst > 0.01 * dst.max()] = 255

        grad_x = cv2.Sobel(self.original_image, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(self.original_image, cv2.CV_64F, 0, 1, ksize=3)
        grad = cv2.magnitude(grad_x, grad_y)
        self.filtered_image = cv2.normalize(grad, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageFilterApp()
    window.show()
    sys.exit(app.exec_())