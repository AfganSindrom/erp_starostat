import sys
from pathlib import Path
from dataclasses import dataclass, field

if "__compiled__" in globals():
    APP_DIR = Path(sys.argv[0]).resolve().parent
else:
    APP_DIR = Path(__file__).resolve().parent

PATH_DATA = APP_DIR / "data"

TYPES = ['lection', 'practice', 'lab']

CONTROL_TYPES = ['za', 'zao', 'exam']

FOLDER = Path(PATH_DATA)

LESSON_TYPE_FULL = {
    'lection': "Лекция",
    'practice': "Практическое занятие",
    'lab': "Лабораторная работа",
}

LESSON_TYPE_SMALL = {
    'lection': "лек.",
    'practice': "прак.",
    'lab': "лаб."
}

CONTROL_TYPES_FULL = {
    'za': "Зачёт",
    'zao': "Зачёт с оценкой",
    'exam': "Экзамен"
}

STATUS_TYPE = {
    'edu': "Учится",
    'exp': "Отчислен",
    'academ': "Академический отпуск"
}

TIMES = {
    1: "8:30-10:00",
    2: "10:10-11:40",
    3: "12:20-13:50",
    4: "14:00-15:30",
    5: "15:40-17:10",
    6: "17:20-19:50",
    7: "20:00-21:30"
}

DAY_NAMES = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
DAY_NAMES_MAL = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']
WEEK_TYPES = {1: 'Нечётная', 2: 'Чётная'}
SEMESTER_TYPES = {'spring': "Весенний", "autumn": "Осенний"}

@dataclass
class Lesson:
    time: str
    title: str
    lesson_type: str
    teacher: str
    subgroup: str
    

@dataclass
class Day:
    title: str
    lessons: list[Lesson] = field(default_factory=True)