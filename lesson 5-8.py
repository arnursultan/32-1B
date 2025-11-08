import sys, sqlite3
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QSpinBox, QComboBox, QCheckBox, QRadioButton,
    QDateEdit, QTextEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QStatusBar
)
from PyQt6.QtCore import Qt, QDate

DB = "student.sqlite3"

class StudentApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CRUD App + PyQt6 + SQLite")
        self.conn = sqlite3.connect(DB)
        self.conn.execute("""CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, age INT, role TEXT,
            active INT, gender TEXT, dob TEXT, notes TEXT
        )""")

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self._ui()
        self.load_data()

    def _ui(self):
        c = QWidget()
        self.setCentralWidget(c)
        root, form = QVBoxLayout(c), QFormLayout()

        self.name, self.age = QLineEdit(), QSpinBox()
        self.age.setRange(0, 120)
        self.role = QComboBox(); self.role.addItems(["Dev", "QA", "PM"])
        self.active = QCheckBox("Активен"); self.active.setChecked(True)
        self.genderM, self.genderF = QRadioButton("М"), QRadioButton("Ж")
        self.genderM.setChecked(True)
        gbox = QHBoxLayout(); [gbox.addWidget(i) for i in (self.genderM, self.genderF)]
        g = QWidget(); g.setLayout(gbox)
        self.dob = QDateEdit(); self.dob.setCalendarPopup(True)
        self.dob.setDate(QDate.currentDate().addYears(-20))
        self.notes = QTextEdit()

        for k, v in {
            "Имя:": self.name, "Возраст:": self.age, "Роль:": self.role,
            "": self.active, "Пол:": g, "Дата:": self.dob, "Заметки:": self.notes
        }.items():
            form.addRow(k, v)

        btns = QHBoxLayout()
        for text, fn in {
            "Добавить": self.create, "Обновить": self.update,
            "Удалить": self.delete, "Очистить": self.clear
        }.items():
            b = QPushButton(text)
            b.clicked.connect(fn)
            btns.addWidget(b)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["ID", "Имя", "Возраст", "Роль", "Активен", "Пол", "Дата", "Заметки"])
        self.table.cellDoubleClicked.connect(self.load_to_form)
        self.table.setColumnHidden(0, True)

        root.addLayout(form)
        root.addLayout(btns)
        root.addWidget(self.table)

    def create(self):
        name = self.name.text().strip()
        if not name:
            return QMessageBox.warning(self, "Ошибка", "Введите имя")

        data = (name, self.age.value(), self.role.currentText(),
                int(self.active.isChecked()),
                "М" if self.genderM.isChecked() else "Ж",
                self.dob.date().toString("yyyy-MM-dd"),
                self.notes.toPlainText())

        self.conn.execute("INSERT INTO students(name, age, role, active, gender, dob, notes) VALUES(?,?,?,?,?,?,?)", data)
        self.conn.commit()
        self.load_data()
        self.clear()
        self.status.showMessage("Добавлено", 1500)

    def load_data(self):
        self.table.setRowCount(0)
        for r in self.conn.execute("SELECT * FROM students ORDER BY id"):
            row = self.table.rowCount()
            self.table.insertRow(row)
            vals = list(map(str, r))
            for c, v in enumerate(vals):
                self.table.setItem(row, c, QTableWidgetItem(v))

    def load_to_form(self, row, _):
        self.cur_id = int(self.table.item(row, 0).text())
        self.name.setText(self.table.item(row, 1).text())
        self.age.setValue(int(self.table.item(row, 2).text()))
        self.role.setCurrentText(self.table.item(row, 3).text())
        self.active.setChecked(self.table.item(row, 4).text() in ["1", "Да"])
        (self.genderM if self.table.item(row, 5).text() == "М" else self.genderF).setChecked(True)
        self.dob.setDate(QDate.fromString(self.table.item(row, 6).text(), "yyyy-MM-dd"))
        self.notes.setPlainText(self.table.item(row, 7).text())

    def update(self):
        if not hasattr(self, "cur_id"):
            return QMessageBox.warning(self, "Выбор", "Выберите запись")

        data = (self.name.text(), self.age.value(), self.role.currentText(),
                int(self.active.isChecked()),
                "М" if self.genderM.isChecked() else "Ж",
                self.dob.date().toString("yyyy-MM-dd"),
                self.notes.toPlainText(), self.cur_id)
        self.conn.execute(
            "UPDATE students SET name=?, age=?, role=?, active=?, gender=?, dob=?, notes=? WHERE id=?", data)
        self.conn.commit()
        self.load_data()
        self.status.showMessage("Обновлено", 1500)

    def delete(self):
        if not hasattr(self, "cur_id"):
            return QMessageBox.warning(self, "Выбор", "Выберите запись")
        self.conn.execute("DELETE FROM students WHERE id=?", (self.cur_id,))
        self.conn.commit()
        self.load_data()
        self.clear()
        self.status.showMessage("Удалено", 1500)

    def clear(self):
        for w in [self.name, self.notes]:
            w.clear()
        self.age.setValue(25)
        self.role.setCurrentIndex(0)
        self.active.setChecked(True)
        self.genderM.setChecked(True)
        self.dob.setDate(QDate.currentDate().addYears(-20))
        if hasattr(self, "cur_id"):
            del self.cur_id


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = StudentApp()
    w.show()
    sys.exit(app.exec())
