import sys
import requests
from PyQt6.QtGui import QPixmap, QKeySequence, QShortcut
from MainWindow import Ui_MainWindow as main_window_ui
from PyQt6.QtWidgets import QApplication, QMainWindow
import os


class MainWindow(QMainWindow, main_window_ui):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Maps API')
        self.setFixedSize(800, 645)

        self.searchButton.clicked.connect(self.search)

        self.zoom_plus_shortcut = QShortcut(QKeySequence('PgUp'), self)
        self.zoom_plus_shortcut.activated.connect(lambda: self.zoom(True))

        self.zoom_minus_shortcut = QShortcut(QKeySequence('PgDown'), self)
        self.zoom_minus_shortcut.activated.connect(lambda: self.zoom(False))

    def search(self):
        lon = self.lonEdit.text()
        lat = self.latEdit.text()
        delta = self.deltaEdit.text()
        if delta.strip() and lon.strip() and lat.strip() and 0.01 <= float(delta) <= 3:
            self.statusbar.clearMessage()
            self.get_image(lon, lat, delta)
            self.pixmap = QPixmap(self.map_file)
            self.MapLabel.setPixmap(self.pixmap)
        else:
            self.statusbar.showMessage('Введены некорректные данные')

    def get_image(self, lon, lat, delta):
        params = {
            'apikey': STATIC_API_KEY,
            'll': f'{lon},{lat}',
            'spn': f'{delta},{delta}'
        }

        response = requests.get(STATIC_API_SERVER, params)

        if response.status_code == 200:
            self.map_file = 'map.png'
            with open(self.map_file, 'wb') as file:
                file.write(response.content)
        else:
            print(f'Ошибка: {response.status_code}')
            sys.exit(1)

    def zoom(self, fg):
        cur_delta = float(self.deltaEdit.text())
        step = 0.5
        if fg:
            if cur_delta - step >= 0.01:
                self.deltaEdit.setText(f'{round(cur_delta - step, 2)}')
        else:
            if cur_delta + step <= 3:
                self.deltaEdit.setText(f'{round(cur_delta + step, 2)}')
        self.search()

    def closeEvent(self, event):
        os.remove(self.map_file)


def main():
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())


def get_api_key():
    with open('api_data.csv', mode='r',
              encoding='utf-8') as file:  # необходимо создать файл api_data.csv с 1-ой строкой: geocode_api_key;static_api_key
        data = file.readlines()[1].split(';')

    return data


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    GEOCODE_API_KEY, STATIC_API_KEY = get_api_key()
    GEOCODE_API_SERVER = 'http://geocode-maps.yandex.ru/1.x/?'
    STATIC_API_SERVER = 'https://static-maps.yandex.ru/v1?'
    main()
