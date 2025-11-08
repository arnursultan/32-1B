# Основные SQL-команды:
# CREATE TABLE — создать таблица / CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT, age INTEGER);
# INSERT INTO — добавить запись / INSERT INTO students (name, age) VALUES ('Azizullo', 15)
# SELECT — получить данные / SELECT * FROM students;
# UPDATE — Обновить / UPDATE students SET age = 16 WHERE_id = 1;
# DELETE — Удалить / DELETE FROM students WHERE_id=1;

import sqlite3

conn = sqlite3.connect("students.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER NOT NULL
)
""")

cursor.execute("INSERT INTO students (name, age) VALUES (?, ?)", ("Kasym", 14))
conn.commit()

cursor.execute("SELECT * FROM students")
for row in cursor.fetchall():
    print(row)

conn.close()

i

