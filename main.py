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


class Toponim:
    def __init__(self, toponym_to_find, name="newobject"):
        self.toponim = None
        self.name = name
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        geocoder_params = {"geocode": toponym_to_find, "format": "json"}
        response = get(geocoder_api_server, params=geocoder_params)
        if not response:
            # обработка ошибочной ситуации
            pass
        # Преобразуем ответ в json-объект
        self.toponim = response.json()
        self.toponim = self.toponim["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]

    def set(self, response):
        self.toponim = response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]

    def get(self):
        return self.toponim

    def get_coords(self):
        coords = self.toponim["Point"]["pos"]
        print(coords)
        return list(map(float, coords.split(" ")))

    def get_address(self):
        return self.toponim["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"][
            "GeocoderMetaData"]["Address"]["formatted"]

    def get_size(self):
        coords = self.toponim["boundedBy"]["Envelope"]
        a = list(map(float, coords["lowerCorner"].split(" ")))
        c = list(map(float, coords["upperCorner"].split(" ")))
        b = a[0], c[1]
        width = lonlat_distance(a, b)
        height = lonlat_distance(b, c)
        return width, height

    def __get_z(self, height):
        return

    def get_map(self):
        x, y = self.get_size()
        square = math.sqrt(math.sqrt(math.sqrt(x * y)))
        z = int(max(14, min(17, square)))
        print(z, square)
        payload = {'apikey': 'fe93f537-0f16-4412-a99a-090347b6cc4f',
                   'l': choice(['map']),
                   'z': z,
                   'll': ','.join(list(map(str, self.get_coords()))),
                   }
        name = self.name
        r = get("https://static-maps.yandex.ru/1.x", params=payload)
        with open(f"{name}.jpg", "wb") as file:
            file.write(r.content)
        convert_to_png(name)
        return name

    def get_near_objects(self, keyword):
        objects = search(keyword)
        for obj in objects:
            obj.append(lonlat_distance(obj[-1], self.get_coords()))
        objects.sort(key=lambda organization: float(organization[-1]))
        return objects


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
        query = Toponim(self.address.text())
        query.get_map()
        pixmap = QPixmap("newobject.png")
        self.img.setPixmap(pixmap)


class GameData:
    valid = None
    pixmap_height = 450
    width = 600
    height = 600
    images = []


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
