import math
import sys
from requests import get
from random import randint, choice
from PIL import Image
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtWidgets import QLCDNumber, QLabel, QLineEdit, QMessageBox
from PyQt5.QtGui import QPixmap
from itertools import cycle
from json import dumps, loads
from pprint import pprint


def convert_to_png(name):
    im = Image.open(f'{name}.jpg')
    im.save(f'{name}.png')


def get_map_on_coords(coords, z):
    payload = {'apikey': 'fe93f537-0f16-4412-a99a-090347b6cc4f',
               'l': choice(['map']),
               'z': z,
               'll': ','.join(list(map(str, coords))),
               }
    name = "newobject"
    r = get("https://static-maps.yandex.ru/1.x", params=payload)
    with open(f"{name}.jpg", "wb") as file:
        file.write(r.content)
    convert_to_png(name)
    return name


class Application(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, GameData.width, GameData.height)
        self.setFixedSize(GameData.width, GameData.pixmap_height + 150)
        self.setWindowTitle('')

        self.address = QLineEdit(self)
        self.address.setPlaceholderText("ответ...")
        self.address.resize(GameData.width - 150, 28)
        self.address.setStyleSheet("border: 1px solid grey;")

        self.address.move(1, 1)

        self.search_button = QPushButton('Найти', self)
        self.search_button.resize(149, 30)
        self.search_button.move(self.address.width(), 0)
        self.search_button.clicked.connect(self.check)

        self.header = QLabel(self)
        self.header.setText("")
        self.header.setStyleSheet("font-family: Arial; font-size: 20pt;")
        self.header.move(70, GameData.height + 20)

        self.img = QLabel(self)
        self.img.move(0, self.address.height() + 2)
        self.img.resize(GameData.width, GameData.pixmap_height)

    def check(self):
        get_map_on_coords(self.address.text().split(), GameData.z)
        pixmap = QPixmap("newobject.png")
        self.img.setPixmap(pixmap)


class GameData:
    valid = None
    pixmap_height = 450
    width = 600
    height = 600
    images = []
    z = 14


def lonlat_distance(a, b):
    degree_to_meters_factor = 111 * 1000  # 111 километров в метрах
    a_lon, a_lat = a
    b_lon, b_lat = b

    # Берем среднюю по широте точку и считаем коэффициент для нее.
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)

    # Вычисляем смещения в метрах по вертикали и горизонтали.
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    # Вычисляем расстояние между точками.
    distance = math.sqrt(dx * dx + dy * dy)

    return distance


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Application()
    ex.show()
    sys.exit(app.exec())
