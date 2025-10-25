from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QSpinBox, QComboBox, QCheckBox, QRadioButton, QButtonGroup,
    QDateEdit, QTextEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QFileDialog, QColorDialog, QMessageBox, QProgressBar, QStatusBar
)
from PyQt6.QtCore import Qt, QDate, QTimer, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator, QPixmap
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Урок 3 — Базовые виджеты")
        self.resize(980, 640)

        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        form = QFormLayout()

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Старшак Даткайым")
        reg = QRegularExpression(r"^[\p{L}\s\-]{2,40}$")
        self.name_edit.setValidator(QRegularExpressionValidator(reg))
        self.name_edit.textChanged.connect(self._on_name_changed)
        form.addRow("Имя:", self.name_edit)

        # Возраст: QSpinBox
        self.age_spin = QSpinBox()
        self.age_spin.setRange(0, 120)
        self.age_spin.setValue(25)
        self.age_spin.valueChanged.connect(
            lambda v: self.status.showMessage(f"Возраст: {v}", 1500)
        )
        form.addRow("Возраст:", self.age_spin)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["Разработчик", "Тестер", "Аналитик", "Менеджер"])
        self.role_combo.currentTextChanged.connect(
            lambda t: self.status.showMessage(f"Роль: {t}", 1500)
        )
        form.addRow("Роль:", self.role_combo)

        self.active_check = QCheckBox("Активен")
        self.active_check.setChecked(True)
        self.active_check.toggled.connect(
            lambda st: self.status.showMessage("Активен" if st else "Не активен", 1500)
        )
        form.addRow("", self.active_check)

        gender_box = QHBoxLayout()
        self.rb_m = QRadioButton("М")
        self.rb_f = QRadioButton("Ж")
        self.rb_m.setChecked(True)

        self.gender_group = QButtonGroup(self)
        self.gender_group.addButton(self.rb_m, 1)
        self.gender_group.addButton(self.rb_f, 2)

        self.gender_group.idToggled.connect(
            lambda i, st: st and self.status.showMessage(f"Пол: {'М' if i == 1 else 'Ж'}", 1500)
        )

        gender_box.addWidget(self.rb_m)
        gender_box.addWidget(self.rb_f)

        gender_container = QWidget()
        gender_container.setLayout(gender_box)
        form.addRow("Пол:", gender_container)

        self.dob_edit = QDateEdit()
        self.dob_edit.setCalendarPopup(True)
        self.dob_edit.setDate(QDate.currentDate().addYears(-20))
        self.dob_edit.dateChanged.connect(
            lambda d: self.status.showMessage(f"Дата рождения: {d.toString('dd.MM.yyyy')}", 1500)
        )
        form.addRow("Дата рождения:", self.dob_edit)

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Короткие заметки...")
        form.addRow("Заметки:", self.notes_edit)

        color_row = QHBoxLayout()
        self.color_preview = QLabel("  ")
        self.color_preview.setFixedSize(40, 20)
        self.color_preview.setStyleSheet("background:#4caf50; border:1px solid #aaa;")
        self.selected_color = "#4caf50"

        self.pick_color_btn = QPushButton("Выбрать цвет…")
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

        self.pick_file_btn = QPushButton("Загрузить изображение…")
        self.pick_file_btn.clicked.connect(self.choose_file)

        file_row.addWidget(self.pick_file_btn)
        file_row.addWidget(self.image_label)

        file_wrap = QWidget()
        file_wrap.setLayout(file_row)
        form.addRow("Фото:", file_wrap)

        actions = QHBoxLayout()
        self.add_btn = QPushButton("Добавить в таблицу")
        self.add_btn.clicked.connect(self.add_to_table)

        self.clear_btn = QPushButton("Очистить форму")
        self.clear_btn.clicked.connect(self.clear_form)

        self.process_btn = QPushButton("Смоделировать процесс")
        self.process_btn.clicked.connect(self.start_process)

        actions.addWidget(self.add_btn)
        actions.addWidget(self.clear_btn)
        actions.addWidget(self.process_btn)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "Имя", "Возраст", "Роль", "Активен", "Пол", "Дата", "Цвет", "Заметки"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.cellDoubleClicked.connect(self.cell_double_clicked)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)

        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)

        left = QVBoxLayout()
        left.addLayout(form)
        left.addLayout(actions)
        left.addWidget(self.progress)

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

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = color.name()
            self.color_preview.setStyleSheet(
                f"background:{self.selected_color}; border:1px solid #aaa;"
            )
            self.status.showMessage(f"Выбран цвет: {self.selected_color}", 1500)

    def choose_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение",
            "",
            "Изображения (*.png *.jpg *.jpeg *.bmp)"
        )
        if path:
            pix = QPixmap(path)
            if not pix.isNull():
                self.image_label.setPixmap(pix.scaled(
                    self.image_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))
                self.status.showMessage(f"Загружено: {path}", 1500)
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить изображение.")

    def clear_form(self):
        self.name_edit.clear()
        self.age_spin.setValue(25)
        self.role_combo.setCurrentIndex(0)
        self.active_check.setChecked(True)
        self.rb_m.setChecked(True)
        self.dob_edit.setDate(QDate.currentDate().addYears(-20))
        self.notes_edit.clear()
        self.image_label.setPixmap(QPixmap())
        self.status.showMessage("Форма очищена", 1200)

    def add_to_table(self):
        if not self.name_edit.hasAcceptableInput():
            QMessageBox.warning(
                self,
                "Проверка",
                "Введите корректное имя (2–40 символов, только буквы/пробел/дефис)."
            )
            self.name_edit.setFocus()
            return

        name = self.name_edit.text().strip()
        age_val = self.age_spin.value()
        age = str(age_val)
        role = self.role_combo.currentText()
        active = "Да" if self.active_check.isChecked() else "Нет"
        gender = "М" if self.gender_group.checkedId() == 1 else "Ж"
        dob = self.dob_edit.date().toString("dd.MM.yyyy")
        color = self.selected_color
        notes = self.notes_edit.toPlainText().strip()

        row = self.table.rowCount()
        self.table.insertRow(row)

        values = [name, age, role, active, gender, dob, color, notes]
        for col, val in enumerate(values):
            item = QTableWidgetItem(val)
            if col == 1:
                item.setData(Qt.ItemDataRole.EditRole, int(age_val))
            self.table.setItem(row, col, item)

        self.status.showMessage(f"Добавлено: {name}", 1500)

    def cell_double_clicked(self, row, col):
        name_item = self.table.item(row, 0)
        val = name_item.text() if name_item else ""
        QMessageBox.information(
            self,
            "Двойной клик",
            f"Строка {row + 1}, колонка {col + 1}\nИмя: {val}"
        )

    def start_process(self):
        self.progress.setValue(0)
        self.timer.start(30)
        self.status.showMessage("Идёт процесс…", 1000)

    def _tick(self):
        v = self.progress.value() + 1
        self.progress.setValue(v)
        if v >= 100:
            self.timer.stop()
            self.status.showMessage("Готово!", 1500)


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
