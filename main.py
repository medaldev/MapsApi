import math
import sys
import re
from requests import get
from random import randint, choice
from PIL import Image
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow
from PyQt5.QtWidgets import QLCDNumber, QLabel, QLineEdit, QMessageBox, \
    QCheckBox
from PyQt5.QtGui import QPixmap
from itertools import cycle
from json import dumps, loads
from pprint import pprint
from PyQt5.QtCore import Qt


def convert_to_png(name):
    im = Image.open(f'{name}.jpg')
    im.save(f'{name}.png')


def get_coords(address):
    payload = {'apikey': 'fe93f537-0f16-4412-a99a-090347b6cc4f',
               'geocode': address,
               'format': 'json'}

    response = get("https://geocode-maps.yandex.ru/1.x", params=payload)
    data = response.json()
    geo_object = data["response"]["GeoObjectCollection"]["featureMember"][0][
        "GeoObject"]
    GameData.address = geo_object["metaDataProperty"]["GeocoderMetaData"][
        "Address"]["formatted"]
    wtf_Envelope = geo_object["boundedBy"]["Envelope"]
    corner1, corner2 = wtf_Envelope["lowerCorner"], wtf_Envelope["upperCorner"]
    corner1 = list(map(float, corner1.split()))
    corner2 = list(map(float, corner2.split()))
    GameData.z = select_zoom(corner1, corner2)
    try:
        GameData.postal_index = geo_object["metaDataProperty"][
            "GeocoderMetaData"]["Address"]["postal_code"]
    except KeyError:
        GameData.postal_index = "нет индекса"
    return geo_object["Point"]["pos"]


def get_organization(address):
    lon, lat = list(map(float, address.split(",")))
    radians_lattitude = math.radians(lat)
    lat_lon_factor = math.cos(radians_lattitude)
    lon_r, lat_r = 50 / (111 * 1000) * lat_lon_factor, 50 / (111 * 1000)
    args = {"apikey": "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3",
            "lang": "ru_RU",
            "bbox": f"{lon + lon_r},{lat + lat_r}~{lon - lon_r},{lat - lat_r}",
            "rspn": 1,
            "type": "biz"}
    response = get("https://search-maps.yandex.ru/v1/", params=args)
    json_response = response.json()
    try:
        organization = json_response["features"][0]
        GameData.address = organization["properties"]["CompanyMetaData"]["name"]
        GameData.points = [",".join(
            list(map(str, organization["geometry"]["coordinates"])))]
        return organization["geometry"]["coordinates"]
    except IndexError:
        GameData.address = "Организаций нет"
        return False


def get_address(address):
    payload = {'apikey': 'fe93f537-0f16-4412-a99a-090347b6cc4f',
               'geocode': address,
               'format': 'json'}

    response = get("https://geocode-maps.yandex.ru/1.x", params=payload)
    data = response.json()
    geo_object = data["response"]["GeoObjectCollection"]["featureMember"][0][
        "GeoObject"]
    GameData.address = geo_object["metaDataProperty"]["GeocoderMetaData"][
        "Address"]["formatted"]
    try:
        GameData.postal_index = geo_object["metaDataProperty"][
            "GeocoderMetaData"]["Address"]["postal_code"]
    except KeyError:
        GameData.postal_index = "нет индекса"
    return GameData.address


def get_map_on_coords(coords, z, points=[]):
    payload = {'apikey': 'fe93f537-0f16-4412-a99a-090347b6cc4f',
               'l': GameData.map_views[GameData.map_view],
               'll': coords,
               'z': z,
               'pt': "",

               }
    if points:
        for i, point in enumerate(points):
            payload["pt"] += f"{point[0]},{point[1]},pm2blm{i + 1}"
            payload["pt"] += "~"
        payload["pt"] = payload["pt"][:-1]
    name = "newobject"
    r = get("https://static-maps.yandex.ru/1.x", params=payload)
    with open(f"{name}.jpg", "wb") as file:
        file.write(r.content)
    convert_to_png(name)


class Application(QMainWindow):
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

        self.full_address = QLineEdit(self)
        self.full_address.setReadOnly(True)
        self.full_address.setPlaceholderText("Полный адрес...")
        self.full_address.resize(GameData.width * 0.8 - 5, 28)
        self.full_address.setStyleSheet(
            "border: 1px solid grey; background: rgba(255, 255, 255, 0.78);")
        self.full_address.move(1, 450)

        self.index = QLineEdit(self)
        self.index.setReadOnly(True)
        self.index.setPlaceholderText("индекс...")
        self.index.resize(GameData.width * 0.2, 28)
        self.index.setStyleSheet(
            "border: 1px solid grey; background: rgba(255, 255, 255, 0.78);")
        self.index.move(GameData.width * 0.8, 450)

        self.reset_but = QPushButton('Сброс', self)
        self.reset_but.resize(149, 30)
        self.reset_but.move(GameData.width - 151, GameData.height - 32)
        self.reset_but.setStyleSheet("border: 1px solid grey;")
        self.reset_but.clicked.connect(self.reset)

        self.need_index = QCheckBox("Индекс", self)
        self.need_index.move(10, GameData.height - 100)
        self.need_index.toggle()
        self.need_index.stateChanged.connect(self.change_index_field)

        self.exit = QPushButton('Выход', self)
        self.exit.resize(149, 30)
        self.exit.move(2, GameData.height - 32)
        self.exit.setStyleSheet("border: 1px solid grey;")
        self.exit.clicked.connect(self.close)

    def change_index_field(self):
        try:
            if self.need_index.isChecked():
                self.index.move(GameData.width * 0.8, 450)

            else:
                self.index.move(GameData.width * 0.8, 4500)

        except Exception as e:
            QMessageBox.about(self, "error", str(e))

    def reset(self):
        try:
            pixmap = QPixmap("newobject.png")
            self.img.setPixmap(pixmap)
            self.address.setText("")
            self.full_address.setText("")
            self.index.setText("")

            GameData.points = []
            GameData.address = ""
            GameData.postal_index = ""
            self.check(coord_set=True)

        except Exception as e:
            QMessageBox.about(self, "error", str(e))

    def check(self, coord_set=False):
        try:
            points = []
            query = self.address.text().replace(" ", "")
            if not coord_set:
                if GameData.address or query:
                    if not query:
                        query = GameData.address
                    if re.search(r"\d+(\.\d+)*,\d+(\.\d+)*", query) != query:
                        points.append(get_coords(query).split())
                        query = ",".join(get_coords(query).split())
                        GameData.points = points.copy()
                get_map_on_coords(query, GameData.z, points=points)
                point = query.split(",")
                GameData.longitude = float(point[0])
                GameData.latitude = float(point[1])
            else:
                get_map_on_coords(f"{GameData.longitude},{GameData.latitude}",
                                  GameData.z, points=GameData.points)
            pixmap = QPixmap("newobject.png")
            self.img.setPixmap(pixmap)
            self.full_address.setText(GameData.address)
            self.index.setText(GameData.postal_index)
        except Exception as e:
            QMessageBox.about(self, "error", str(e))

    def mousePressEvent(self, event):
        try:
            focused_widget = QApplication.focusWidget()
            if isinstance(focused_widget, QLineEdit):
                focused_widget.clearFocus()
            QMainWindow.mousePressEvent(self, event)
            point = get_click([event.pos().x(), event.pos().y()])
            if event.button() == 1:
                get_address(",".join(list(map(str, point))))
                self.index.setText(GameData.postal_index)
            elif event.button() == 2:
                point = get_organization(",".join(list(map(str, point))))
                if not point:
                    GameData.points = []
                    self.check(coord_set=True)
            if point:
                GameData.points = [point]
                self.check(coord_set=True)
        except Exception as e:
            QMessageBox.about(self, "error", str(e))

    def keyPressEvent(self, key):
        move_k = 2
        if key.key() == Qt.Key_PageDown:
            GameData.z = max(GameData.z - 1, 0)
            self.check(coord_set=True)
        elif key.key() == Qt.Key_PageUp:
            GameData.z = min(GameData.z + 1, 17)
            self.check(coord_set=True)
        elif key.key() == Qt.Key_Up:
            delta = 180 / 2 ** GameData.z * move_k
            GameData.latitude = min(float(GameData.latitude) + delta, 90)
            self.check(coord_set=True)
        elif key.key() == Qt.Key_Down:
            delta = 180 / 2 ** GameData.z * move_k
            GameData.latitude = max(float(GameData.latitude) - delta, -90)
            self.check(coord_set=True)
        elif key.key() == Qt.Key_Left:
            delta = 360 / 2 ** GameData.z * move_k
            GameData.longitude = max(float(GameData.longitude) - delta, -180)
            self.check(coord_set=True)
        elif key.key() == Qt.Key_Right:
            delta = 360 / 2 ** GameData.z * move_k
            GameData.longitude = min(float(GameData.longitude) + delta, 180)
            self.check(coord_set=True)
        elif key.key() == Qt.Key_Z:
            GameData.map_view = (GameData.map_view + 1) % \
                                len(GameData.map_views)
            self.check(coord_set=True)


class GameData:
    valid = None
    map_views = ["sat,skl", "map", "sat"]
    map_view = 0
    pixmap_height = 450
    width = 600
    height = 600
    longitude = str(44.972349)
    latitude = str(53.146328)
    images = []
    z = 7
    points = []
    address = ""
    postal_index = ""

    @staticmethod
    def get_coord():
        return GameData.longitude, GameData.latitude


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

    z_x = math.log(180.0 / delta_lon, 2)
    z_y = math.log(360.0 / delta_lat, 2)

    z = min(int(z_x), int(z_y))

    return z


def get_click(point):
    x, y = point
    map_center = [ex.img.rect().center().x(), ex.img.rect().center().y()]
    map_coords = GameData.get_coord()
    map_pos = [ex.img.rect().x(), ex.img.rect().y()]
    delta_x, delta_y = x - map_center[0], map_center[1] - y
    width, height = ex.img.rect().width(), ex.img.rect().height()
    if abs(delta_x) > width / 2 or abs(delta_y) > height / 2:
        return False
    lon_view, lat_view = 360.0 / 2 ** GameData.z, 180.0 / 2 ** GameData.z
    pix_ratio_x, pix_ratio_y = delta_x / (width / 2), (delta_y + 30) / (
                height / 2)
    k1, k2 = 1.2, 1.05
    delta_lon = pix_ratio_x * lon_view * k1
    delta_lat = pix_ratio_y * lat_view * k2
    lon = float(map_coords[0]) + delta_lon
    lat = float(map_coords[1]) + delta_lat
    return [lon, lat]


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Application()
    ex.show()
    ex.check(coord_set=True)
    sys.exit(app.exec())
