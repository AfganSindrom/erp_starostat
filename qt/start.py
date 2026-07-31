import sys

from datetime import date

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import Qt

from qt.timetable import Timetable
from qt.table import Tabel
from qt.semester import Semesters
from qt.students import StudentsTable
from qt.med import Med
from qt.info_app import InfoWindow

import query.connect as connect
import query.constants as constants
from query.select import get_week_info

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('ИС "Старостат"')
        self.resize(550, 350)

        menu_bar = self.menuBar()

        edit_bar = menu_bar.addMenu("Действия")
        info_bar = menu_bar.addMenu("Информация")

        semester_action = QAction("Выбор семестра", self)
        semester_action.triggered.connect(self.semester_triggered)
        edit_bar.addAction(semester_action)

        info_action = QAction("О приложении", self)
        info_action.triggered.connect(self.info_triggered)
        info_bar.addAction(info_action)

        central = QWidget()
        Homelayout = QVBoxLayout()

        hello = QLabel("Добрый день, " + connect.config['user']['first_name'])
        font = hello.font()
        font.setPointSize(16)
        hello.setFont(font)
        hello.setAlignment(Qt.AlignmentFlag.AlignCenter)
        Homelayout.addWidget(hello)
        Homelayout.setContentsMargins(0, 0, 0, 0)

        today = date.today()
        today_str = today.strftime("%d.%m.%Y")
        week_type = get_week_info(today)

        time = QLabel("Сегодня " + today_str + ", " + constants.DAY_NAMES_MAL[today.weekday()] + " | " + constants.WEEK_TYPES[week_type['week_type']] + " неделя")

        font = time.font()
        font.setPointSize(16)
        time.setFont(font)
        time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        Homelayout.addWidget(time)

        self.tabelsBtn = QPushButton(text="Табеля (F1)")
        self.timetableBtn = QPushButton(text="Расписание (F2)")
        self.helpBtn = QPushButton(text="Справочники (F3)")
        self.medBtn = QPushButton(text="Справки (F4)")

        self.tabelsBtn.setShortcut(QKeySequence("F1"))
        self.timetableBtn.setShortcut(QKeySequence("F2"))
        self.helpBtn.setShortcut(QKeySequence("F3"))
        self.medBtn.setShortcut(QKeySequence("F4"))

        SecondLayout = QHBoxLayout()
        buttonsAndTimetable = QWidget()
        Homelayout.addWidget(buttonsAndTimetable)
        buttonsAndTimetable.setLayout(SecondLayout)
        buttons = QWidget()
        SecondLayout.addWidget(buttons)
        ButLayout = QVBoxLayout()
        buttons.setLayout(ButLayout)

        ButLayout.addWidget(self.tabelsBtn)
        ButLayout.addWidget(self.timetableBtn)
        ButLayout.addWidget(self.helpBtn)
        ButLayout.addWidget(self.medBtn)
        
        central.setLayout(Homelayout)
        self.setCentralWidget(central)

        self.buttons_action()

    def open_med(self):
        self.med = Med()
        self.med.show()

    def open_tabel(self):
        self.tabel_window = Tabel()
        self.tabel_window.show()

    def open_timetable(self):
        self.timetable_window = Timetable()
        self.timetable_window.show()

    def open_students(self):
        self.students = StudentsTable()
        self.students.show()

    def buttons_action(self):
        self.tabelsBtn.clicked.connect(self.open_tabel)
        self.tabel_window = None

        self.timetableBtn.clicked.connect(self.open_timetable)
        self.timetable_window = None

        self.helpBtn.clicked.connect(self.open_students)
        self.students = None

        self.medBtn.clicked.connect(self.open_med)
        self.med = None
    
    def semester_triggered(self):
        self.semester = Semesters()
        self.semester.show()

    def info_triggered(self):
        self.info = InfoWindow()
        self.info.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())