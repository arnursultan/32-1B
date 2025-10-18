# import sys
# from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
#
# app = QApplication(sys.argv)
#
# window = QWidget()
# window.setWindowTitle("Простое окно")
#
# label = QLabel("Привет, PyQt6!")
# button = QPushButton("Нажми меня")
#
# layout = QVBoxLayout()
# layout.addWidget(label)
# layout.addWidget(button)
# window.setLayout(layout)
#
# window.show()
# sys.exit(app.exec())
#
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Окно с декомпозицией")
        self.init_ui()

    def init_ui(self):
        self.label = QLabel("Привет, Группа 32-1B")
        self.button = QPushButton("Нажми меня")
        self.button.clicked.connect(self.on_click)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def on_click(self):
        self.label.setText("Кнопка нажата!")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()