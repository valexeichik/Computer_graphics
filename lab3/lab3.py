import sys
from PyQt5.QtWidgets import QApplication
from modules.mainwindow import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle('lab 3')
    window.showMaximized()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()