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
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMainWindow,
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


