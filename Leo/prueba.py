from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QLabel, QProgressBar, QLineEdit, QFileDialog
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QCursor
import sys
class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.title = "your_title"

        self.screen_dim = (1600, 900)

        self.width = 650
        self.height = 400

        self.left = int(self.screen_dim[0]/2 - self.width/2)
        self.top = int(self.screen_dim[1]/2 - self.height/2)

        self.init_window()

    def init_window(self):
        self.setWindowIcon(QtGui.QIcon('path_to_icon.png'))
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setStyleSheet('background-color: rgb(52, 50, 51);')

        self.create_layout()

        self.show()

    def create_layout(self):
        self.button = QPushButton('Click Me', self)
        self.button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

if __name__ == '__main__':

    App = QApplication(sys.argv)
    window = Window()
    sys.exit(App.exec())