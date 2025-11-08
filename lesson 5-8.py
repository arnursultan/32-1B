# Что делает программа:
# - хранит список студентов в локальной SQLite-базе;
# - даёт добавить, посмотреть, обновить и удалить записи;
# - двойной клик по строке в таблице возвращает данные в форму для редактирования.

import sys            # нужен, чтобы создать QApplication и корректно выйти (sys.exit)
import sqlite3        # встроенная СУБД SQLite: подключение, запросы, commit

from PyQt6.QtWidgets import (
    QApplication,      # оболочка любого Qt-приложения (event loop)
    QMainWindow,       # готовое "главное окно" (рамка, меню, статус-бар)
    QWidget,           # базовый контейнер
    QVBoxLayout,       # вертикальная раскладка (складывает элементы столбиком)
    QHBoxLayout,       # горизонтальная раскладка (в линию)
    QFormLayout,       # форма "метка : поле" — удобно для анкет/форм
    QLineEdit,         # однострочное текстовое поле (Имя)
    QSpinBox,          # числовое поле со стрелками (Возраст)
    QComboBox,         # выпадающий список (Роль)
    QCheckBox,         # галочка (Активен)
    QRadioButton,      # переключатели (Пол: М/Ж)
    QDateEdit,         # поле даты с календарём (Дата рождения)
    QTextEdit,         # многострочный текст (Заметки)
    QPushButton,       # кнопки действий (Добавить/Обновить/Удалить/Очистить)
    QTableWidget,      # таблица для отображения записей
    QTableWidgetItem,  # ячейка таблицы
    QMessageBox,       # простые диалоги (предупреждения/ошибки)
    QStatusBar         # строка состояния внизу окна (показываем короткие подсказки)
)

from PyQt6.QtCore import QDate  # класс для работы с датами (в форме и при сохранении)


# Настройки Базы Данных
DB = "student.sqlite3"  # имя файла с БД; появится рядом со скриптом


class StudentApp(QMainWindow):
    # Главное окно: форма слева, таблица справа, кнопки снизу. Полный CRUD.

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CRUD App + PyQt6 + SQLite")

        # 1) Подключаемся к SQLite.
        self.conn = sqlite3.connect(DB)

        # 2) Готовим таблицу, если её ещё нет.
        #    id — автоинкремент, нужен для точной идентификации записи при UPDATE/DELETE
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS students(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name   TEXT,
                age    INT,
                role   TEXT,
                active INT,   -- 0/1 из чекбокса "Активен"
                gender TEXT,  -- 'М' или 'Ж' из радиокнопок
                dob    TEXT,  -- дата как строка 'YYYY-MM-DD' (удобно и стабильно)
                notes  TEXT
            )
        """)

        # 3) Статус-бар — просто чтобы показывать короткие сообщения пользователю.
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # 4) Собираем интерфейс и сразу подгружаем данные из БД в таблицу.
        self._build_ui()
        self.load_data()

    # Интерфейс
    def _build_ui(self):
        # Форма, кнопки, таблица — компонуем всё по местам.

        # Базовый контейнер окна.
        container = QWidget()
        self.setCentralWidget(container)

        # Корневой вертикальный лэйаут: сверху форма, ниже кнопки, ещё ниже таблица.
        root = QVBoxLayout(container)

        # Форма (слева)
        form = QFormLayout()

        # Поля формы
        self.name = QLineEdit()                 # Имя (обязательное поле)
        self.age = QSpinBox(); self.age.setRange(0, 120)
        self.role = QComboBox(); self.role.addItems(["Dev", "QA", "PM"])
        self.active = QCheckBox("Активен"); self.active.setChecked(True)

        # Пол: две радиокнопки. По умолчанию — 'М'.
        self.genderM, self.genderF = QRadioButton("М"), QRadioButton("Ж")
        self.genderM.setChecked(True)
        gbox = QHBoxLayout()
        gbox.addWidget(self.genderM)
        gbox.addWidget(self.genderF)
        gender_wrap = QWidget(); gender_wrap.setLayout(gbox)

        # Дата рождения — удобный виджет с календарём.
        self.dob = QDateEdit()
        self.dob.setCalendarPopup(True)
        self.dob.setDate(QDate.currentDate().addYears(-20))  # пусть по умолчанию будет -20 лет

        # Заметки — свободный текст.
        self.notes = QTextEdit()

        # Складываем всё в форму "метка : поле".
        for label, widget in {
            "Имя:": self.name,
            "Возраст:": self.age,
            "Роль:": self.role,
            "": self.active,            # пустая метка — чтобы чекбокс не имел подписи слева
            "Пол:": gender_wrap,
            "Дата:": self.dob,
            "Заметки:": self.notes,
        }.items():
            form.addRow(label, widget)

        # Кнопки (под формой)
        btns = QHBoxLayout()

        # К каждой кнопке сразу привязываем действие (метод).
        for title, slot in {
            "Добавить": self.create,  # INSERT
            "Обновить": self.update,  # UPDATE по выбранному ID
            "Удалить":  self.delete,  # DELETE по выбранному ID
            "Очистить": self.clear    # сброс формы в исходное состояние
        }.items():
            b = QPushButton(title)
            b.clicked.connect(slot)
            btns.addWidget(b)

        # Таблица (справа)
        # 8 колонок, точно соответствуют полям в таблице БД.
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Имя", "Возраст", "Роль", "Активен", "Пол", "Дата", "Заметки"]
        )
        self.table.setColumnHidden(0, True)  # ID скрываем — он служебный

        # Важный UX: двойной клик по строке — загружаем её в форму для правок.
        self.table.cellDoubleClicked.connect(self.load_to_form)

        # Итоговая сборка на экране
        root.addLayout(form)
        root.addLayout(btns)
        root.addWidget(self.table)

    # CRUD: CREATE/READ/UPDATE/DELETE

    def create(self):
        # Create / INSERT: берём данные из формы и добавляем новую запись в БД.
        # Мини-проверка: имя обязательно
        name = self.name.text().strip()
        if not name:
            return QMessageBox.warning(self, "Ошибка", "Введите имя")

        # Собираем данные в том порядке, как в таблице (кроме id).
        data = (
            name,
            self.age.value(),
            self.role.currentText(),
            int(self.active.isChecked()),               # чекбокс -> 0/1
            "М" if self.genderM.isChecked() else "Ж",  # радиокнопки -> 'М'/'Ж'
            self.dob.date().toString("yyyy-MM-dd"),    # удобный ISO-формат
            self.notes.toPlainText()
        )

        # Параметризованный запрос — безопасно и без танцев с кавычками
        self.conn.execute(
            "INSERT INTO students(name, age, role, active, gender, dob, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
            data
        )
        self.conn.commit()   # фиксируем изменения на диск
        self.load_data()     # перечитываем таблицу (Read) — чтобы сразу увидеть новую строку
        self.clear()         # очищаем форму под следующий ввод
        self.status.showMessage("Добавлено", 1500)

    def load_data(self):
        # Read / SELECT: читаем все записи и показываем их в таблице.
        self.table.setRowCount(0)  # сначала очищаем таблицу

        # Достаём все записи в стабильном порядке по id
        for row_tuple in self.conn.execute("SELECT * FROM students ORDER BY id"):
            row = self.table.rowCount()
            self.table.insertRow(row)

            # row_tuple = (id, name, age, role, active, gender, dob, notes)
            # В ячейку таблицы кладём строки.
            for col, value in enumerate(map(str, row_tuple)):
                self.table.setItem(row, col, QTableWidgetItem(value))

    def load_to_form(self, row: int, _col: int):
        # Двойной клик по строке в таблице -> переносим её данные в форму.
        # Параллельно запоминаем ID (self.cur_id), чтобы знать, что обновлять/удалять.

        # Берём ID из скрытой колонки [0] и запоминаем его в атрибуте объекта.
        self.cur_id = int(self.table.item(row, 0).text())

        # Остальные значения просто развозим по полям формы.
        self.name.setText(self.table.item(row, 1).text())
        self.age.setValue(int(self.table.item(row, 2).text()))
        self.role.setCurrentText(self.table.item(row, 3).text())
        self.active.setChecked(self.table.item(row, 4).text() in ("1", "Да"))
        (self.genderM if self.table.item(row, 5).text() == "М" else self.genderF).setChecked(True)
        self.dob.setDate(QDate.fromString(self.table.item(row, 6).text(), "yyyy-MM-dd"))
        self.notes.setPlainText(self.table.item(row, 7).text())

    def update(self):
        # Update / UPDATE: сохраняем изменения из формы в выбранную запись по ID.
        # Если пользователь ничего не выбрал — подскажем, что надо сделать.
        if not hasattr(self, "cur_id"):
            return QMessageBox.warning(self, "Выбор", "Выберите запись (двойной клик по строке таблицы)")

        # Собираем обновлённые значения и добавляем в конец ID (для WHERE).
        data = (
            self.name.text(),
            self.age.value(),
            self.role.currentText(),
            int(self.active.isChecked()),
            "М" if self.genderM.isChecked() else "Ж",
            self.dob.date().toString("yyyy-MM-dd"),
            self.notes.toPlainText(),
            self.cur_id  # важно: по этому ID и обновим строку
        )

        self.conn.execute(
            "UPDATE students SET name=?, age=?, role=?, active=?, gender=?, dob=?, notes=? WHERE id=?",
            data
        )
        self.conn.commit()
        self.load_data()  # сразу показать изменения в таблице
        self.status.showMessage("Обновлено", 1500)

    def delete(self):
        #Delete / DELETE: удаляем выбранную запись по её ID.
        if not hasattr(self, "cur_id"):
            return QMessageBox.warning(self, "Выбор", "Выберите запись (двойной клик по строке таблицы)")

        self.conn.execute("DELETE FROM students WHERE id=?", (self.cur_id,))
        self.conn.commit()
        self.load_data()  # обновим таблицу
        self.clear()      # сбросим форму и забудем cur_id
        self.status.showMessage("Удалено", 1500)

    def clear(self):
        # Сброс формы к значениям «по умолчанию» и снятие выделения записи.
        # Поля ввода — в ноль
        self.name.clear()
        self.notes.clear()

        # Стандартные значения — чтобы форма была в предсказуемом состоянии
        self.age.setValue(25)
        self.role.setCurrentIndex(0)
        self.active.setChecked(True)
        self.genderM.setChecked(True)
        self.dob.setDate(QDate.currentDate().addYears(-20))

        # Если ранее что-то было выбрано — убираем флажок выбора (ID).
        if hasattr(self, "cur_id"):
            del self.cur_id


#Точка Входа
if __name__ == "__main__":
    # Любое Qt-приложение начинается с QApplication.
    app = QApplication(sys.argv)

    # Создаём и показываем наше окно.
    w = StudentApp()
    w.show()

    # Запускаем цикл обработки событий (без него окно закроется сразу).
    sys.exit(app.exec())
