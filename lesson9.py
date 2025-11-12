import sys, json, urllib.request, urllib.parse, ssl
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QDoubleSpinBox, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt

#  Отключаем проверку SSL
#  Это полезно при тестировании, чтобы избежать ошибок SSL-соединения
ssl._create_default_https_context = ssl._create_unverified_context

#  Список Валют
#  Можно добавить любые другие коды ISO (например, PLN, CAD, JPY)
CURRENCIES = ["USD", "EUR", "KGS", "KZT", "UZS", "CNY", "RUB"]

# API-адреса
# 1. exchangerate.host — основной источник (актуальные курсы в реальном времени)
# 2. open.er-api.com — резервный источник (на случай, если первый не работает)
API_MAIN = "https://api.exchangerate.host/convert"
API_BACKUP = "https://open.er-api.com/v6/latest/"

# Класс основного окна
class Converter(QWidget):
    # Главное окно приложения — онлайн-конвертер валют.

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Онлайн-конвертер валют")
        self.resize(400, 200)

        # Поле для ввода суммы
        # Позволяет ввести число с плавающей точкой (0.00)
        self.amount = QDoubleSpinBox()
        self.amount.setRange(0.0, 1e9)    # допустимый диапазон
        self.amount.setDecimals(2)        # количество знаков после запятой
        self.amount.setValue(100.0)       # значение по умолчанию

        # Выпадающие списки для выбора валют
        self.from_cb, self.to_cb = QComboBox(), QComboBox()
        for cb in (self.from_cb, self.to_cb):
            cb.addItems(CURRENCIES)
        self.from_cb.setCurrentText("USD")  # изначально доллар
        self.to_cb.setCurrentText("KGS")    # по умолчанию сом

        # Mетка для отображения результата
        self.result = QLabel("—")
        self.result.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result.setStyleSheet("font-size:16px; font-weight:bold; margin-top:8px;")

        # Кнопка "Конвертировать"
        btn = QPushButton("Конвертировать")
        btn.setMinimumHeight(32)
        btn.clicked.connect(self.convert)  # при нажатии запускаем метод convert()

        # омпоновка интерфейса
        # QVBoxLayout — вертикальное расположение элементов
        layout = QVBoxLayout(self)

        # Создаём несколько горизонтальных рядов (метка + виджет)
        for text, widget in [("Сумма:", self.amount), ("Из:", self.from_cb), ("В:", self.to_cb)]:
            row = QHBoxLayout()
            row.addWidget(QLabel(text))
            row.addWidget(widget)
            layout.addLayout(row)

        # Добавляем кнопку и метку результата в основной вертикальный макет
        layout.addWidget(btn)
        layout.addWidget(self.result)

    # Вспомогательный элемент
    def fetch_json(self, url):
        # Отправляет GET-запрос по указанному URL и возвращает результат в виде словаря (распарсенный JSON).
        # Если соединение не удалось — вызовет исключение.
        with urllib.request.urlopen(url, timeout=8) as r:
            return json.loads(r.read().decode("utf-8"))

    # Основная логика конвертации
    def convert(self):
        # Метод вызывается при нажатии на кнопку.
        # Получает выбранные валюты, сумму, делает запрос к API
        # и отображает результат пользователю.

        amount = self.amount.value()
        src, dst = self.from_cb.currentText(), self.to_cb.currentText()

        # Если выбраны одинаковые валюты — пересчёт не нужен
        if src == dst:
            self.result.setText(f"{amount:.2f} {dst}")
            return

        try:
            # Отправляем запрос к основному API
            params = urllib.parse.urlencode({"from": src, "to": dst, "amount": amount})
            url = f"{API_MAIN}?{params}"
            data = self.fetch_json(url)
            result = data.get("result")

            # Если основной API не вернул результат — используем запасной
            if result is None:
                data2 = self.fetch_json(API_BACKUP + src)
                rate = data2["rates"].get(dst)
                if rate:
                    result = rate * amount

            # Если даже запасной источник не дал данных — выводим ошибку
            if result is None:
                raise ValueError("Курс не найден.")

            # Отображаем итог пользователю
            self.result.setText(f"{amount:.2f} {src} = {result:.2f} {dst}")

        except Exception as e:
            # В случае любых сетевых или логических ошибок
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить курс валют.\n\n{e}")

# Точка Входа
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Converter()
    w.show()
    sys.exit(app.exec())
