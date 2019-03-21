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
from PyQt5.QtCore import Qt


def convert_to_png(name):
    im = Image.open(f'{name}.jpg')
    im.save(f'{name}.png')


def get_map_on_coords(coords, z):
    payload = {'apikey': 'fe93f537-0f16-4412-a99a-090347b6cc4f',
               'l': GameData.map_views[GameData.map_view],
               'll': coords,
               'z': z,

               }
    name = "newobject"
    r = get("https://static-maps.yandex.ru/1.x", params=payload)
    with open(f"{name}.jpg", "wb") as file:
        file.write(r.content)
    convert_to_png(name)


class Application(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.check()

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

    def check(self, coord_set=False):
        if not coord_set:
            get_map_on_coords(self.address.text().replace(" ", ""), GameData.z)
            point = self.address.text().split(",")
            GameData.longitude = float(point[0])
            GameData.latitude = float(point[1])
        else:
            get_map_on_coords(f"{GameData.longitude},{GameData.latitude}",
                              GameData.z)
        pixmap = QPixmap("newobject.png")
        self.img.setPixmap(pixmap)

    def keyPressEvent(self, key):
        if key.key() == Qt.Key_PageDown:
            GameData.z = max(GameData.z - 1, 0)
            self.check()
        elif key.key() == Qt.Key_PageUp:
            GameData.z = min(GameData.z + 1, 17)
            self.check()
        elif key.key() == Qt.Key_Up:
            delta = 360 / 2 ** GameData.z
            GameData.latitude = max(GameData.latitude + delta, 90)
            self.check(coord_set=True)
        elif key.key() == Qt.Key_Down:
            delta = 360 / 2 ** GameData.z
            GameData.latitude = min(GameData.latitude - delta, -90)
            self.check(coord_set=True)
        elif key.key() == Qt.Key_Left:
            delta = 180 / 2 ** GameData.z
            GameData.longitude = min(GameData.longitude - delta, -180)
            print(GameData.longitude)
            self.check(coord_set=True)
        elif key.key() == Qt.Key_Right:
            delta = 180 / 2 ** GameData.z
            GameData.longitude = max(GameData.longitude + delta, 180)
            print(GameData.longitude)
            self.check(coord_set=True)
        elif key.key() == Qt.Key_Z:
            GameData.map_view = (GameData.map_view + 1) % \
                                len(GameData.map_views)
            self.check()


class GameData:
    valid = None
    map_views = ["sat,skl", "map", "sat"]
    map_view = 0
    pixmap_height = 450
    width = 600
    height = 600
    longitude = str(45.01)
    latitude = str(53.16)
    images = []
    z = 7


def lonlat_distance(a, b):
    degree_to_meters_factor = 111 * 1000
    a_lon, a_lat = a
    b_lon, b_lat = b
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor
    distance = math.sqrt(dx * dx + dy * dy)

    return distance


def select_zoom(a, b):

    a_lon, a_lat = a
    b_lon, b_lat = b

    delta_lon = abs(a_lon - b_lon)
    delta_lat = abs(a_lat - b_lat)

    z_x = math.log(180 / delta_lon, 2)
    z_y = math.log(360 / delta_lat, 2)

    z = min(int(z_x), int(z_y))

    return z


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Application()
    ex.show()
    sys.exit(app.exec())
