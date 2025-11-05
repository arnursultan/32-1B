# Основные SQL-команды:
# CREATE TABLE — создать таблица / CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT, age INTEGER);
# INSERT INTO — добавить запись / INSERT INTO students (name, age) VALUES ('Azizullo', 15)
# SELECT — получить данные / SELECT * FROM students;
# UPDATE — Обновить / UPDATE students SET age = 16 WHERE_id = 1;
# DELETE — Удалить / DELETE FROM students WHERE_id=1;

# import sqlite3
#
# conn = sqlite3.connect("students.db")
# cursor = conn.cursor()
#
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS students (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     name TEXT NOT NULL,
#     age INTEGER NOT NULL
# )
# """)
#
# cursor.execute("INSERT INTO students (name, age) VALUES (?, ?)", ("Kasym", 14))
# conn.commit()
#
# cursor.execute("SELECT * FROM students")
# for row in cursor.fetchall():
#     print(row)
#
# conn.close()

import sys
import sqlite3

from PyQt6.QtCore import QDate, Qt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMainWindow, QSpinBox, QComboBox, QCheckBox,
    QRadioButton, QGroupBox, QButtonGroup, QDateEdit, QTextEdit, QProgressBar,
)

DB_NAME = "student.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
        )
    """)
    conn.commit()
    conn.close()

class StudentApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CRUD App + PyQt6 + SQLite")
        self.resize(500, 400)

        self.name_input = QLineEdit()
        self.age_input = QLineEdit()
        self.search_input = QLineEdit()

        self.add_btn = QPushButton("Добавить")
        self.load_btn = QPushButton("Показать всех")
        self.search_btn = QPushButton("Поиск")
        self.delete_btn = QPushButton("Удалить по ID")

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Имя", "Возраст"])

        layout = QVBoxLayout()
        form = QHBoxLayout()
        form.addWidget(QLabel("Имя:"))

        self.age_spin = QSpinBox()
        self.age_spin.setRange(0, 120)
        self.age_spin.setValue(16)
        self.age_spin.valueChanged.connect(
            lambda v: self.status.showMessage(f"Возраст: {v}", 1500)
        )
        form.addRow("Возраст:", self.age_spin)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["Разработчик", "Аналитик", "Инженер"])
        self.role_combo.currentTextChanged.connect(
            lambda t: self.status.showMessage(f"Роль: {t}", 1500)
        )
        form.addRow("Роль:", self.role_combo)

        self.active_check = QCheckBox("Активен")
        self.active_check.setChecked(True)
        self.active_check.toggled.connect(
            lambda st: self.status.showMessage("Активен" if st else "Не активен", 1500)
        )
        form.addRow(""б self.active_check)

        gender_box = QHBoxLayout()
        self.rb_m = QRadioButton("М")
        self.rb_f = QRadioButton("Ж")
        self.rb_m.setChecked(True)
        self.gender_group = QButtonGroup(self)
        self.gender_group.addButton(self.rb_m, 1)
        self.gender_group.addButton(self.rb_f, 2)
        self.gender_group.idToggled.connect(
            lambda i, st: st and self.status.showMessage(f"Пол: {'М' if i == 1 else:\ 'Ж'}", 1500)
        )

        gender_container = QWidget()
        gender_container.setLayout(gender_box)
        form.addRow(f"Пол:", self.gender_container)

        self.dob_edit = QDateEdit()
        self.dob_edit.setCalendarPopup(True)
        self.dob_edit.setDate(QDate.currentDate().addYears(-15))
        self.dob_edit.dateChanged.connect(
            lambda d: self.status.showMessage(f"Дата рождения: {d.toString('dd.MM.yyyy')}", 1500)
        )
        form.addRow("Дата рождения:", self.dob_edit)

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Короткие заметки...")
        form.addRow("Заметки", self.notes_edit)

        color_row = QHBoxLayout()
        self.color_preview = QLabel("")
        self.color_preview.setFixedSize(40, 20)
        self.color_preview.setStyleSheet("background:4#caf50, border-radius: 1 px solod #aaa;")

        self.selected_color = "4caf50"

        self.pick_color_btn = QPushButton("Выбрать цвет...")
        self.pick_color_btn.clicked.connect(self.choose_color)

        color_row.addWidget(self.pick_color_btn)
        color_row.addWidget(self.color_preview)

        color_wrap = QWidget()
        color_wrap.setLayout(color_row)
        form.addRow("Цвет:", color_wrap)

        file_row = QHBoxLayout()

        self.image_label = QLabel("превью")
        self.image_label.setFixedSize(100, 70)
        self.image_label.setStyleSheet("border:1px dashed #777;")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.pick_file_btn = QPushButton("Загрузить изображение...")
        self.pick_file_btn.clicked.connect(self.choose_file)

        file_row.addWidget(self.pick_file_btn)
        file_row.addWidget(self.image_label)

        file_wrap = QWidget()
        file_wrap.setLayout(file_row)
        form.addRow("Фото:", file_wrap)

        actions = QHBoxLayout
        self.add_btn = QPushButton("Добавить в таблицу")
        self.add_btn.clicked.connect(self.clear_form)

        self.clear_btn = QPushButton("Очистить форму")
        self.clear_btn.clicked.connect(self.start_process)

        actions.addWidget(self.add_btn)
        actions.addWidget(self.clear_btn)
        actions.addWidget(self.process_btn)

        self.table = QTableWidget()
        self.table.setHorizontalHeaderLabels([
            "Имя", "Возраст", "Роль", "Активен", "Пол", "Дата", "Цвет", "Заметки"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.callDoubleClicked.connect(self.call_double.clicked)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)

        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)

        left = QVBoxLayout()
        left.addLayout(form)
        left.addLayout(actions)
        left.addLayout(self,progress)

        left_wrap = QWidget()
        left_wrap.setLayout(left)

        content = QHBoxLayout()
        content.addWidget(left_wrap, 2)
        content.addWidget(self.table, 3)

        root.addLayout(content)

    def _on_name_changed(self, text: str):
        if self.name_edit.hasAcceptableInput() or not text:
            self.name_edit.setStyleSheet("")
        else:
            self.name_edit.setStyleSheet("border: 1px solid #e53935;")
        self.status.showMessage(f"Имя: {text}", 800)

