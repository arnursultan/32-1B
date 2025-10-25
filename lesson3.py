import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QFormLayout, QLabel, QLineEdit, QSpinBox,
    QComboBox, QCheckBox, QRadioButton, QButtonGroup, QDateEdit,
    QTextEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QFileDialog, QColorDialog, QMessageBox, QProgressBar, QStatusBar
)
from PyQt6.QtCore import Qt, QDate, QTimer, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator, QPixmap

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Урок 3 - Базовые виджеты")
        self.resize(1000, 650)

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
            lambda i, st: st and self.status.showMessage(f"Пол: {'М' if i==1 else 'Ж'}", 1500)
        )

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
        self.color_preview.setStyleSheet("background:#4caf50; border-radius:1px solid #aaa;")
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
        self.table.callDoubleClicked.connect(self.cell_double_clicked)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)

        self.timer = QTimer()
        self.timer.timeout.conncet(self._tick)

        left = QVBoxLayout()
        left.addLayout(form)
        left.addLayout(actions)
        left.addLayout(self.progress)

        left_wrap = QWidget()
        left_wrap.setLayout(left)

        content = QHBoxLayout()
        content.addWidget(self.table)
        content.addWidget(self.progress)

