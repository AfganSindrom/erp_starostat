from PyQt6.QtWidgets import QMainWindow, QWidget, QGridLayout, QVBoxLayout, QScrollArea, QLabel, QFrame, QHBoxLayout, QToolBar, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon

from query.constants import Lesson, Day, TIMES
from query.select import get_timetable_period, get_week_info
from datetime import date, timedelta

def week(today):
    week = get_week_info(today)
    week_type = "Нечётная" if week['week_type'] == 1 else "Чётная"
    return week, week_type

class lessonWidget(QFrame):
    def __init__(self,
            lesson: Lesson):
        super().__init__()

        self._create_widgets(lesson)
        self._create_layout()
        self._title_custom()
        
    def _create_widgets(self, lesson):
        self.timeLabel = QLabel(lesson.time)
        self.typeLabel = QLabel(lesson.lesson_type)
        self.titleLabel = QLabel(lesson.title)
        self.teacherLabel = QLabel(lesson.teacher)
        self.subgroupLabel = QLabel(lesson.subgroup)

    def _create_layout(self):
        layout = QGridLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(4)
        layout.addWidget(self.timeLabel, 0, 0)
        layout.addWidget(self.typeLabel, 0, 1)
        layout.addWidget(self.titleLabel, 1, 0, 1, 2)
        layout.addWidget(self.teacherLabel, 2, 0)
        layout.addWidget(self.subgroupLabel, 2, 1)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)

        layout.addWidget(line, 3, 0, 1, 2)

        layout.setColumnStretch(0, 1)

    def _title_custom(self):
        font = self.titleLabel.font()
        font.setBold(True)
        self.titleLabel.setFont(font)
        self.subgroupLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.typeLabel.setAlignment(Qt.AlignmentFlag.AlignRight)

# Перед началом отладки реализовать переключение недель, т.е. влево - today - timedelta(7), вправо - today + timedelta(7)
class weekToolbar(QToolBar):
    def __init__(self, today):
        super().__init__()
        self.today = today
        self.setMovable(False)
        self.create_widgets()
        self.custom_label()

    def create_widgets(self):
        weekLabels, self.weekType = week(self.today)
        self.start_date = weekLabels['start_week'].strftime("%d.%m.%Y")
        self.end_date = weekLabels['end_week'].strftime("%d.%m.%Y")
        left_spacer = QWidget()
        left_spacer.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )
        self.left_action = QAction(QIcon.fromTheme("pan-start"), "Назад", self)
        self.title = QLabel(self.weekType + " | " + self.start_date + " - " + self.end_date)
        self.right_action = QAction(QIcon.fromTheme("pan-end"), "Вперед", self)

        self.left_action.triggered.connect(self.week_before)
        self.right_action.triggered.connect(self.week_after)

        right_spacer = QWidget()
        right_spacer.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )

        self.addAction(self.left_action)
        self.addWidget(left_spacer)
        self.addWidget(self.title)
        self.addWidget(right_spacer)
        self.addAction(self.right_action)

    def custom_label(self):
        font = self.title.font()
        font.setPointSize(16)
        self.title.setFont(font)

    def set_week(self, date_edu):
        week1, week1_type = week(date_edu)
        self.start_date = week1['start_week'].strftime("%d.%m.%Y")
        self.end_date = week1['end_week'].strftime("%d.%m.%Y")
        self.title.setText(week1_type + " | " + self.start_date + " - " + self.end_date)
        timetable = get_timetable_period(week1['start_week'].strftime("%Y-%m-%d"), week1['end_week'].strftime("%Y-%m-%d"))
        self.clear_lessons()
        for item in timetable:
            lesson = Lesson(time=TIMES[item["time"]], title=item["title"], lesson_type=item["lesson_type"], teacher=item["teacher"], subgroup=item["subgroup"])
            match item["day"]:
                case 0:
                    self.parent().monday.addLesson(lesson)
                case 1:
                    self.parent().tuesday.addLesson(lesson)
                case 2:
                    self.parent().wednesday.addLesson(lesson)
                case 3:
                    self.parent().thursday.addLesson(lesson)
                case 4:
                    self.parent().friday.addLesson(lesson)
                case 5:
                    self.parent().saturday.addLesson(lesson)

    def week_before(self):
        self.today -= timedelta(7)
        self.set_week(self.today)

    def week_after(self):
        self.today += timedelta(7)
        self.set_week(self.today)

    def clear_lessons(self):
        self.parent().monday.clearLessons()
        self.parent().tuesday.clearLessons()
        self.parent().wednesday.clearLessons()
        self.parent().thursday.clearLessons()
        self.parent().friday.clearLessons()
        self.parent().saturday.clearLessons()

class dayWidget(QFrame):
    def __init__(self, title: str):
        super().__init__()
        self._create_layout(title)
        self._title_custom()
        
    def _create_layout(self, title):
        header = QFrame()
        headerLayout = QHBoxLayout(header)
        self.titleLabel = QLabel(title)
        headerLayout.addWidget(self.titleLabel)
        layout = QVBoxLayout()
        scroll = QScrollArea()
        contents = QWidget()
        self.contentLayout = QVBoxLayout()

        layout.addWidget(header)

        contents.setLayout(self.contentLayout)
        layout.setContentsMargins(0, 0, 0, 0)
        self.contentLayout.addStretch()
        scroll.setWidget(contents)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        self.setLayout(layout)


    def _title_custom(self):
        font = self.titleLabel.font()
        font.setPointSize(16)
        self.titleLabel.setFont(font)
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def addLesson(self, lesson):
        self.contentLayout.insertWidget(
            self.contentLayout.count() - 1,
            lessonWidget(lesson)
        )

    def clearLessons(self):
        for i in range(self.contentLayout.count() - 2, -1, -1):
            item = self.contentLayout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    self.contentLayout.removeWidget(widget)
                    widget.deleteLater()

class Timetable(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('ИС "Старостат" - расписание')
        self.resize(1400, 800)

        today = date.today()
        self.week1, self.week1_type = week(today)

        central = QWidget()
        layout = QGridLayout()
        toolbar = weekToolbar(today)

        self.monday = dayWidget("Понедельник")
        self.tuesday = dayWidget("Вторник")
        self.wednesday = dayWidget("Среда")
        self.thursday = dayWidget("Четверг")
        self.friday = dayWidget("Пятница")
        self.saturday = dayWidget("Суббота")

        layout.addWidget(self.monday, 0, 0)
        layout.addWidget(self.tuesday, 0, 1)
        layout.addWidget(self.wednesday, 0, 2)
        layout.addWidget(self.thursday, 1, 0)
        layout.addWidget(self.friday, 1, 1)
        layout.addWidget(self.saturday, 1, 2)
        self.addToolBar(toolbar)
        central.setLayout(layout)
        self.setCentralWidget(central)

    def set_timetable(self):
        timetable = get_timetable_period(self.week1['start_week'].strftime("%Y-%m-%d"), self.week1['end_week'].strftime("%Y-%m-%d"))
        for item in timetable:
            lesson = Lesson(time=TIMES[item["time"]], title=item["title"], lesson_type=item["lesson_type"], teacher=item["teacher"], subgroup=item["subgroup"])
            match item["day"]:
                case 0: self.monday.addLesson(lesson)
                case 1: self.tuesday.addLesson(lesson)
                case 2: self.wednesday.addLesson(lesson)
                case 3: self.thursday.addLesson(lesson)
                case 4: self.friday.addLesson(lesson)
                case 5: self.saturday.addLesson(lesson)