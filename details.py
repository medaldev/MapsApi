import requests
import sys
from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QLCDNumber,
                             QLineEdit,
                             QApplication, QCheckBox, QPlainTextEdit)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class Form(QWidget):

    def __init__(self):
        super().__init__()
        self.setGeometry(800, 300, 600, 450)
        self.setWindowTitle("API")

        self.map = QLabel(self)
        self.picture = QPixmap("map.png")
        self.map.setPixmap(self.picture)

    def keyPressEvent(self, key):
        if key.key() == Qt.Key_PageDown:
            pass
        elif key.key() == Qt.Key_PageUp:
            pass
        elif key.key() == Qt.Key_Up:
            pass
        elif key.key() == Qt.Key_Down:
            pass
        elif key.key() == Qt.Key_Left:
            pass
        elif key.key() == Qt.Key_Right:
            pass
