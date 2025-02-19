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

        # создание горячих клавиш
        self.zoom_plus_shortcut = QShortcut(QKeySequence('PgUp'), self)
        self.zoom_plus_shortcut.activated.connect(lambda: self.zoom(True))

        self.zoom_minus_shortcut = QShortcut(QKeySequence('PgDown'), self)
        self.zoom_minus_shortcut.activated.connect(lambda: self.zoom(False))

        self.up = QShortcut(QKeySequence('Up'), self)
        self.up.activated.connect(lambda: self.movement('up'))

        self.down = QShortcut(QKeySequence('Down'), self)
        self.down.activated.connect(lambda: self.movement('down'))

        self.left = QShortcut(QKeySequence('Left'), self)
        self.left.activated.connect(lambda: self.movement('left'))

        self.right = QShortcut(QKeySequence('Right'), self)
        self.right.activated.connect(lambda: self.movement('right'))

    def search(self):
        '''Поиск и вывод объекта по введенным данным'''
        lon = self.lonEdit.text()
        lat = self.latEdit.text()
        delta = self.deltaEdit.text()
        if delta.strip() and lon.strip() and lat.strip() and 0.01 <= float(
                delta) <= 3 and -180 < float(lon) < 180 and -85 < float(lat) < 85:  # проверка введенных данных
            self.statusbar.clearMessage()
            self.get_image(lon, lat, delta)
            self.pixmap = QPixmap(self.map_file)
            self.MapLabel.setPixmap(self.pixmap)
        else:
            self.statusbar.showMessage('Введены некорректные данные')

    def get_image(self, lon, lat, delta):
        '''Создание и выполнение запроса для получения карты'''
        params = {
            'apikey': STATIC_API_KEY,
            'll': f'{lon},{lat}',
            'spn': f'{delta},{delta}'
        }
        # запрос на получение картинки по введенным данным
        response = requests.get(STATIC_API_SERVER, params)

        if response.status_code == 200:
            # сохранение карты на компьютер при успешном выполнении запроса
            self.map_file = 'map.png'
            with open(self.map_file, 'wb') as file:
                file.write(response.content)
        else:  # обработка ошибки при попытке выполнения запроса
            print(f'Ошибка: {response.status_code}')
            sys.exit(1)

    def zoom(self, fg):
        '''Изменение масштаба карты при использовании горячих клавиш'''
        cur_delta = float(self.deltaEdit.text())
        step = 0.5  # шаг изменения масштаба
        if fg:
            if cur_delta - step >= 0.01:
                self.deltaEdit.setText(f'{round(cur_delta - step, 2)}')
        else:
            if cur_delta + step <= 3:
                self.deltaEdit.setText(f'{round(cur_delta + step, 2)}')
        self.search()

    def movement(self, direction):
        '''Изменение положения карты при нажатии на клавиши стрелок'''
        lon = float(self.lonEdit.text())
        lat = float(self.latEdit.text())
        delta = float(self.deltaEdit.text())
        step = 0.25 * delta  # шаг равен 25% от текущего масштаба
        if direction == 'up':
            lat += step
        elif direction == 'down':
            lat -= step
        elif direction == 'right':
            if lon + step > 180:
                lon = -180 + (lon + step) % 180
            elif lon + step == 180:
                lon = -179
            else:
                lon += step
        elif direction == 'left':
            if lon - step < -180:
                lon = 180 - (lon + step) % 180
            elif lon - step == -180:
                lon = 179
            else:
                lon -= step
        self.latEdit.setText(str(lat))
        self.lonEdit.setText(str(lon))
        self.search()

    def closeEvent(self, event):
        os.remove(self.map_file)  # удаления сохранившейся карты с компьютера при завершении работы программы


def main():
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())


def get_api_key():
    '''Получение API ключей из файла api_data.csv'''
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
