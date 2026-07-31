from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtSvgWidgets import QSvgWidget

class InfoWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("О приложении")
        self.resize(600, 200)

        central = QWidget()
        def_layout = QVBoxLayout()
        label0 = QLabel()
        svg = QSvgWidget("assets/otto.svg")
        svg.renderer().setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
        svg.setFixedSize(200, 200)
        label1 = QLabel('Информационная система "Старостат"')
        label2 = QLabel('<center>Версия 1.0 MVP</center>')
        label3 = QLabel('<center>Распространяется по лицензии GNU GPL v 3.0</center>')
        label4 = QLabel('<center><a href="https://github.com/afgansindrom/erp_starostat">Исходный код на GitHub</a></center>')
        label5 = QLabel("<center>By Afgansindrom. 2026</center>")

        label1_font = label1.font()
        label1_font.setPointSize(16)
        label1_font.setBold(True)
        label1.setFont(label1_font)

        self.setCentralWidget(central)
        central.setLayout(def_layout)

        def_layout.addWidget(svg, alignment=Qt.AlignmentFlag.AlignCenter)
        def_layout.addWidget(label1, alignment=Qt.AlignmentFlag.AlignCenter)
        def_layout.addWidget(label2)
        def_layout.addWidget(label3)
        def_layout.addWidget(label4)
        def_layout.addWidget(label5)