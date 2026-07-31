import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from PyQt6.QtWidgets import (QApplication, QWidget, QToolBar, QLabel, QComboBox, QMainWindow, QTableWidget,
                             QGridLayout, QAbstractItemView, QHeaderView, QTableWidgetItem, QMenu, QDialog,
                             QRadioButton,
                             QVBoxLayout, QDialogButtonBox, QLineEdit, QDateEdit, QHBoxLayout, QPushButton, QMessageBox,
                             QFileDialog)

from datetime import date

from query.select import get_students_att, get_timetable_names, get_week_info
from query.insert import insert_att, update_status, insert_lesson

from export.tables import tables_generate

class exportDialog(QDialog):
    def __init__(self, table):
        super().__init__()
        self.table = table
        self.setWindowTitle("Экспорт в отчёт")
        self.def_layout = QVBoxLayout()
        self.setLayout(self.def_layout)
        self._add_widgets()

    def _add_widgets(self):
        self.widget1 = QWidget()
        self.widget2 = QWidget()
        self.widget3 = QWidget()
        self.widget5 = QWidget()

        self.def_layout.addWidget(self.widget1)
        self.def_layout.addWidget(self.widget2)
        self.def_layout.addWidget(self.widget3)
        self.def_layout.addWidget(self.widget5)

        self.title_label = QLabel("Выберите диапазон:")
        self.radio1 = QRadioButton("За семестр")
        self.radio2 = QRadioButton("За занятие")

        self.radio1.clicked.connect(self._add_date)
        self.radio2.clicked.connect(self._add_diapazone)

        self.button = QPushButton("Экспорт")

        self.button.clicked.connect(self.export)

        self.layout1 = QHBoxLayout()
        self.layout2 = QHBoxLayout()
        self.layout3 = QHBoxLayout()
        self.layout5 = QHBoxLayout()

        self.widget1.setLayout(self.layout1)
        self.widget2.setLayout(self.layout2)
        self.widget3.setLayout(self.layout3)
        self.widget5.setLayout(self.layout5)

        self.cur1 = QWidget()

        self.layout1.addWidget(self.title_label)

        self.layout2.addWidget(self.radio1)
        self.layout2.addWidget(self.radio2)

        self.layout3.addWidget(self.cur1)

        self.layout5.addWidget(self.button)

    def _add_date(self):
        old_wid1 = self.cur1

        self.none = QWidget()

        item1 = self.layout3.replaceWidget(old_wid1, self.none)

        if item1 is not None:
            old_wid1.hide()
            old_wid1.deleteLater()
            del item1

            self.cur1 = self.none

    def _add_diapazone(self):
        old_widget = self.cur1

        self.lesson_box = QComboBox()

        for lesson in self.table.dates:
            lesson_id = lesson["id"]
            lesson_date = lesson["date"]

            # lesson_id хранится внутри элемента списка
            self.lesson_box.addItem(
                f"{lesson_date:%d.%m.%Y} — занятие №{lesson_id}",
                userData=lesson_id,
            )

        item = self.layout3.replaceWidget(
            old_widget,
            self.lesson_box,
        )

        if item is not None:
            old_widget.hide()
            old_widget.deleteLater()
            del item

        self.cur1 = self.lesson_box

    def export(self):
        info = self.table.info

        students = list(zip(
            self.table.student_ids,
            self.table.students_names,
        ))

        if self.radio1.isChecked():
            # За семестр
            dates = self.table.dates
            marks = self.table.marks

        elif self.radio2.isChecked():
            # Получаем lesson_id выбранного элемента
            selected_lesson_id = self.lesson_box.currentData()

            if selected_lesson_id is None:
                QMessageBox.warning(
                    self,
                    "Экспорт",
                    "Выберите занятие.",
                )
                return

            # Оставляем ровно одно занятие
            dates = [
                lesson
                for lesson in self.table.dates
                if lesson["id"] == selected_lesson_id
            ]

            # Оставляем отметки только этого занятия
            marks = {
                (student_id, lesson_id): mark_info
                for (student_id, lesson_id), mark_info
                in self.table.marks.items()
                if lesson_id == selected_lesson_id
            }

            if not dates:
                QMessageBox.warning(
                    self,
                    "Экспорт",
                    "Выбранное занятие не найдено.",
                )
                return

        else:
            QMessageBox.warning(
                self,
                "Экспорт",
                "Выберите период экспорта.",
            )
            return

        save_dir, _ = QFileDialog.getSaveFileName(self, "Сохранить ведомость", "Ведомость.xlsx", "Excel (.xlsx)")

        tables_generate(
            students,
            dates,
            marks,
            info,
            save_dir,
        )
        self.hide()

# Добавление записи
class AddLesson(QDialog):
    def __init__(self, item, index, table):
        super().__init__()
        self.setWindowTitle("Добавление пары")
        self.resize(370, 80)
        self.def_layout = QVBoxLayout()

        self.item = item
        self.index = index
        self.table = table
        
        self.widget1 = QWidget()
        self.hlayout_1 = QHBoxLayout()
        self.date_label = QLabel("Дата: ")
        self.date = QDateEdit()
        self.date.setDate(date.today())

        self.widget2 = QWidget()
        self.hlayout_2 = QHBoxLayout()
        self.time_label = QLabel("Пара: ")
        self.time = QComboBox()
        self.time.addItems(['1', '2', '3', '4', '5', '6', '7'])

        self.widget3 = QWidget()
        self.hlayout_3 = QHBoxLayout()
        self.teacher_label = QLabel("Преподаватель: ")
        self.teacher = QLineEdit()
        self.teacher.setText(item['teacher'])

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        self.setLayout(self.def_layout)

        self.def_layout.addWidget(self.widget1)
        self.def_layout.addWidget(self.widget2)
        self.def_layout.addWidget(self.widget3)
        self.def_layout.addWidget(self.buttons)

        self.widget1.setLayout(self.hlayout_1)
        self.widget2.setLayout(self.hlayout_2)
        self.widget3.setLayout(self.hlayout_3)

        self.hlayout_1.addWidget(self.date_label)
        self.hlayout_1.addWidget(self.date)
        self.hlayout_2.addWidget(self.time_label)
        self.hlayout_2.addWidget(self.time)
        self.hlayout_3.addWidget(self.teacher_label)
        self.hlayout_3.addWidget(self.teacher)

        self.buttons.accepted.connect(self.add_lesson)

    def add_lesson(self):
        teacher = self.teacher.text()
        date_lesson = self.date.date().toString("yyyy-MM-dd")
        date_lesson_type = date.strptime(date_lesson,"%Y-%m-%d")
        time = self.time.currentText()
        discipline = self.item['name']
        subgrp_type = self.item['subgrp_type']
        subgroup = self.item['subgroup']
        type_lesson = self.item['type']
        week_type = get_week_info(date_lesson_type)
        status = 2
        add = [date_lesson, time, discipline, type_lesson, teacher, subgrp_type, subgroup, week_type['week_type'], status]
        insert_lesson(add)
        self.table.load_data(self.index, self.item["name"],
            self.item['teacher'],
            self.item['hours'],
            self.item['subgrp_type'],
            self.item["subgroup"],
            self.item["type"]
        )
        self.hide()

# Состояние пары
class LessonDialog(QDialog):
    def __init__(self, lesson_id, students_len, disc_id, table):
        super().__init__()
        self.setWindowTitle("Состояние пары")
        names, self.items = get_timetable_names()
        self.def_layout = QVBoxLayout()
        self.setLayout(self.def_layout)
        self.modified = {}
        self.lesson_id = lesson_id
        self.students_len = students_len
        self.disc_id = disc_id
        self.table = table

        self.title = QLabel("Состояние пары:")
        self.true = QRadioButton("Состоялась")
        self.false = QRadioButton("Отменена")

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        self.def_layout.addWidget(self.title)
        self.def_layout.addWidget(self.true)
        self.def_layout.addWidget(self.false)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.false.clicked.connect(self.add_desc)

        self.def_layout.addWidget(self.buttons)

    def add_desc(self):
        self.desc_label = QLabel("Причина")
        self.desc = QLineEdit()
        self.desc.setPlaceholderText("Причина отмены")

        self.def_layout.removeWidget(self.buttons)
        self.def_layout.addWidget(self.desc_label)
        self.def_layout.addWidget(self.desc)
        self.def_layout.addWidget(self.buttons)

    def accept(self):
        # если установлена "Состоялась" - просто ставим 1 в расписание и не блокируем присутствие
        if self.true.isChecked():
            update_status(1, self.lesson_id)
            for student_id in range(self.students_len):
                self.change_mark(student_id+1, self.lesson_id, "", "")
                lesson_block = False
        # если установлена "Отменена" - ОБЯЗАТЕЛЬНО ставим 0, ПИШЕМ ПРИЧИНУ!! и блокируем присутствие, устанавливая всем "н"
        elif self.false.isChecked():
            update_status(0, self.lesson_id)
            absence_text = self.desc.text()
            for student_id in range(self.students_len):
                self.change_mark(student_id+1, self.lesson_id, "н", "Отмена пары. Причина: " + absence_text)
            lesson_block = True
        modified = [
            (lesson_id, student_id, mark, comment, lesson_block)
            for (lesson_id, student_id), (mark, comment) in self.modified.items()
        ]
        insert_att(modified)
        self.modified.clear()
        self.hide()
        self.set_discipline(self.disc_id)

    def reject(self):
        self.hide()

    def change_mark(self, row, column, value, comment):
        self.modified[(column, row)] = value, comment

    def set_discipline(self, index):
        item = self.items[index]

        self.table.load_data(
            index,
            item["name"],
            item["subgroup"],
            item["type"],
        )


class TableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.modified = {}
        self.blocked = {}

    # способ добавления отметки - через клавиатуру. space - присутствовал (+), n - отсутствовал (н), o (англ.) - опоздал <= 15 мин (оп)
    def keyPressEvent(self, event):
        item = self.currentItem()

        if not item:
            return

        if (event.key() == Qt.Key.Key_Space) and (self.is_cell_editable(item.column(), item.row())):
            item.setText("+")
            self.change_mark(item.row(), item.column(), "+", "")
            self.setCurrentCell(item.row() + 1, item.column())

        elif (event.key() == Qt.Key.Key_N) and (self.is_cell_editable(item.column(), item.row())):

            item.setText("н")
            self.change_mark(item.row(), item.column(), "н", "Неуважительная причина или грубейшее опоздание")
            self.setCurrentCell(item.row() + 1, item.column())

        elif (event.key() == Qt.Key.Key_O) and (self.is_cell_editable(item.column(), item.row())):
            item.setText("оп")
            self.change_mark(item.row(), item.column(), "оп", "Опоздание")
            self.setCurrentCell(item.row() + 1, item.column())

        elif (event.key() == Qt.Key.Key_Delete) and (self.is_cell_editable(item.column(), item.row())):
            item.setText("")
        
        elif event.key() == Qt.Key.Key_Down:
            self.setCurrentCell(item.row() + 1, item.column())

        elif event.key() == Qt.Key.Key_Up:
            self.setCurrentCell(item.row() - 1, item.column())

        elif event.key() == Qt.Key.Key_Left:
            self.setCurrentCell(item.row(), item.column() - 1)

        elif event.key() == Qt.Key.Key_Right:
            self.setCurrentCell(item.row(), item.column() + 1)

    # способ добавления отметки - через меню
    def show_menu(self, pos):
        item = self.currentItem()
        row = item.row()
        column = item.column()

        if not self.is_cell_editable(row, column):
            return
        item = self.currentItem()
        menu = QMenu(self)

        present_action = menu.addAction("Присутствовал (+)")
        absent_action = menu.addAction("Отсутствовал (н)")
        excused_action = menu.addAction("Опоздал (оп)")
        menu.addSeparator()
        clear_action = menu.addAction("Очистить")

        action = menu.exec(self.viewport().mapToGlobal(pos))

        if action == present_action: self.change_mark(item.row(), item.column(), "+", "")
        if action == absent_action: self.change_mark(item.row(), item.column(), "н", "Неуважительная причина или грубейшее опоздание")
        if action == excused_action: self.change_mark(item.row(), item.column(), "оп", "Опоздание")
        if action == clear_action: self.set_attendance(item.row(), item.column(), "")

    def set_attendance(self, row, column, value):
        item = self.item(row, column)

        if item is None:
            item = QTableWidgetItem()
            self.setItem(row, column, item)

        item.setText(value)

    def load_data(self, index, name_dis, teacher, hours, subgrp_type, subgroup, type_):
        self.index = index
        self.marks = {}
        self.info = {
            "name": name_dis,
            "type": type_,
            "teacher": teacher,
            "hours": hours
        }
        self.students, self.subgrp_types, timetable, self.attendance = get_students_att(name_dis, subgrp_type, subgroup, type_)

        self.student_ids = []
        self.students_names = []
        self.lesson_ids = [lesson['lesson_id'] for lesson in self.attendance]

        for attendance_item in self.attendance:
            self.marks.update(attendance_item.get("marks", {}))

        student_name = []

        self.setColumnCount(len(self.attendance))
        self.setRowCount(len(self.subgrp_types))

        for ids in self.subgrp_types:
            for student_id in self.students:
                if ids[0] == student_id[0]:
                    self.student_ids.append(student_id[0])
                    self.students_names.append(student_id[1])
                    student_name.append(str(student_id[0]) + ". " + student_id[1])

        dates = [date.strptime(att_item['date'], "%Y-%m-%d") for att_item in self.attendance]
        self.dates = [{"id": att_item['lesson_id'], "date": date.strptime(att_item['date'], "%Y-%m-%d")} for att_item in self.attendance]
        self.dates_month = [date_item.strftime("%d.%m") for date_item in dates]

        self.setHorizontalHeaderLabels(self.dates_month)
        self.setVerticalHeaderLabels(student_name)

        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        header = self.horizontalHeader()
        for index, att_item in enumerate(self.attendance):
            header.setSectionResizeMode(index, QHeaderView.ResizeMode.ResizeToContents)

        for r, student in enumerate(self.student_ids):
            student_id = student

            for c, lesson in enumerate(timetable):
                lesson_id = lesson[0]

                info = self.attendance[c]['marks'].get((student_id, lesson_id))

                if info:
                    mark = info["mark"]
                    blocked = info["blocked"]
                else:
                    mark = ""
                    blocked = False

                table_item = QTableWidgetItem(mark)
                self.blocked[(r, c)] = blocked
                if blocked:
                    table_item.setBackground(Qt.GlobalColor.lightGray)
                    table_item.setFlags(table_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.setItem(r, c, table_item)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)

        self.itemDoubleClicked.connect(self.lesson_dialog_show)
        self.lesson_dialog = None

    def change_mark(self, row, column, value, comment):
        if not self.is_cell_editable(row, column):
            return
        self.set_attendance(row, column, value)
        self.modified[(self.lesson_ids[column], self.student_ids[row])] = value, comment

    def lesson_dialog_show(self):
        item = self.currentItem()
        self.lesson_dialog = LessonDialog(self.lesson_ids[item.column()], len(self.students), self.index, self)
        self.lesson_dialog.setModal(True)
        self.lesson_dialog.show()

    def is_cell_editable(self, row, column):
        return not self.blocked.get((row, column), False)

class TabelToolbar(QToolBar):
    def __init__(self):
        super().__init__()
        self.setMovable(False)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.create_actions()

    def create_actions(self):
        addDate = QAction(QIcon.fromTheme("document-new"), "Добавить запись", self)
        addDate.triggered.connect(self.open_addDate)
        self.addDate_show = None
        self.export = QAction(QIcon.fromTheme("document-save"), "Экпорт в ведомость", self)
        self.save_action = QAction(
            QIcon.fromTheme("document-save"),
            "Сохранить",
            self
        )
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.setShortcutVisibleInContextMenu(True)

        self.export.triggered.connect(self.save_export)
        self.export_dialog = None

        discipline_text = QLabel("Дисциплина: ")
        discipline_text.setFixedWidth(90)
        discipline = QComboBox()
        names, self.items = get_timetable_names()
        discipline.addItems(names)
        discipline.currentIndexChanged.connect(self.set_discipline)

        self.addAction(addDate)
        self.addSeparator()
        self.addWidget(discipline_text)
        self.addWidget(discipline)
        self.addSeparator()
        self.addAction(self.export)
        self.addAction(self.save_action)

    def set_discipline(self, index):
        self.item = self.items[index]
        self.index = index

        self.parent().table.load_data(
            index,
            self.item["name"],
            self.item['teacher'],
            self.item['hours'],
            self.item['subgrp_type'],
            self.item["subgroup"],
            self.item["type"],
        )

    def open_addDate(self):
        self.addDate_show = AddLesson(self.item, self.index, self.parent().table)
        self.addDate_show.show()

    def save_export(self):
        self.export_dialog = exportDialog(table=self.parent().table)
        self.export_dialog.show()

class Tabel(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('ИС "Старостат" - посещаемость')
        self.resize(1600, 900)

        self.name_dis = ""
        self.subgroup = 0
        self.type = ""

        central = QWidget()
        layout = QGridLayout()

        self.toolbar = TabelToolbar()
        self.toolbar.save_action.triggered.connect(self.save_attendance)
        self.table = TableWidget(self)

        layout.addWidget(self.table)
        self.addToolBar(self.toolbar)
        central.setLayout(layout)
        self.setCentralWidget(central)

    def save_attendance(self):
        modified = [
            (lesson_id, student_id, mark, comment, False)
            for (lesson_id, student_id), (mark, comment) in self.table.modified.items()
        ]
        insert_att(modified)
        self.update_lessons()
        self.table.modified.clear()

    def update_lessons(self):
        lessons = {
            lesson_id
            for (lesson_id, student_id) in self.table.modified.keys()
        }

        for lesson_id in lessons:
            update_status(1, lesson_id)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Tabel()
    window.show()
    sys.exit(app.exec())