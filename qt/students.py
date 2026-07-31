import sys
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QToolBar,
    QLabel,
    QComboBox,
    QMainWindow,
    QTabWidget,
    QTableWidget,
    QGridLayout,
    QAbstractItemView,
    QHeaderView,
    QTableWidgetItem,
    QDialog,
    QVBoxLayout,
    QDialogButtonBox,
    QLineEdit,
    QDateEdit,
    QHBoxLayout, QPushButton,
)

from query.select import get_all_students, get_student, get_subgrps
from query.insert import insert_students, update_student, update_subgrps
import query.constants as constants

from datetime import date

class Dialog(QDialog):
    def __init__(self, edit: bool, student: dict | None, table):
        super().__init__()
        self.edit = edit
        self.student = student
        self.table = table

        self.setWindowTitle("Информация о студенте")
        self._add_widgets()

    def _add_widgets(self):
        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)

        full_name_label = QLabel("ФИО обучающегося: ")
        self.full_name = QLineEdit()

        birthday_label = QLabel("Дата рождения")
        self.birthday = QDateEdit()

        phone_label = QLabel("Номер телефона")
        self.phone = QLineEdit()

        if self.edit:
            self.full_name.setText(self.student['full_name'])
            birthday_data = date.strptime(self.student['birthday'], "%Y-%m-%d")
            birthday = QDate()
            birthday.setDate(birthday_data.year, birthday_data.month, birthday_data.day)
            self.birthday.setDate(birthday)
            self.phone.setText(self.student['phone'])
            status_label = QLabel("Статус:")
            self.status = QComboBox()
            self.status.setCurrentText(constants.STATUS_TYPE[self.student['status']])
            for id_, name in constants.STATUS_TYPE.items():
                self.status.addItem(name, id_)
            self.main_layout.addWidget(status_label, 3, 0)
            self.main_layout.addWidget(self.status, 3, 1)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        self.buttons.accepted.connect(self._add_student)

        self.main_layout.addWidget(full_name_label, 0, 0)
        self.main_layout.addWidget(self.full_name, 0, 1)
        self.main_layout.addWidget(birthday_label, 1, 0)
        self.main_layout.addWidget(self.birthday, 1, 1)
        self.main_layout.addWidget(phone_label, 2, 0)
        self.main_layout.addWidget(self.phone, 2, 1)
        if self.edit: self.main_layout.addWidget(self.buttons, 4, 1)
        else: self.main_layout.addWidget(self.buttons, 3, 1)

    def _add_student(self):
        self.full_name_data = self.full_name.text()
        self.birthday_data = self.birthday.date().toPyDate()
        self.phone_data = self.phone.text()
        if self.edit: self.status_data = self.status.currentData()
        else: self.status_data = 'edu'

        self.birthday_data = self.birthday_data.strftime("%Y-%m-%d")

        if self.edit: self.data = [
            self.full_name_data,
            self.phone_data,
            self.birthday_data,
            self.status_data,
            self.student['id']
        ]
        else: self.data = [
            self.full_name_data,
            self.phone_data,
            self.birthday_data,
            self.status_data
        ]
        if self.edit: update_student(self.data)
        else: insert_students(self.data)
        self.hide()
        self.table._add_data()

class Table(QTableWidget):
    def __init__(self):
        super().__init__()
        self._add_labels()
        self._add_data()
        self._set_edit()

    def _add_labels(self):
        hor_labels = ['ID', 'ФИО', 'Контакты', 'Дата рождения', 'Статус']

        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(item for item in hor_labels)
        headers = self.horizontalHeader()
        for i in range(len(hor_labels)):
            headers.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    def _add_data(self):
        self.students = get_all_students()
        self.setRowCount(len(self.students))

        for r, data_item in enumerate(self.students):
            id = QTableWidgetItem(str(data_item[0]))
            student = QTableWidgetItem(data_item[1])
            contacts = QTableWidgetItem(data_item[2])
            status = QTableWidgetItem(constants.STATUS_TYPE[data_item[4]])

            birthday = date.strptime(data_item[3], "%Y-%m-%d")
            birthday = QTableWidgetItem(birthday.strftime("%d.%m.%Y"))

            self.setItem(r, 0, id)
            self.setItem(r, 1, student)
            self.setItem(r, 2, contacts)
            self.setItem(r, 3, birthday)
            self.setItem(r, 4, status)

    def _set_edit(self):
        self.itemDoubleClicked.connect(self._open_dialog_edit)
        self.dialog = None

    def _open_dialog_edit(self):
        data = get_student(self._get_id().text())
        data_dialog = {
            "id": self._get_id().text(),
            "full_name": data[0][0],
            "phone": data[0][1],
            "birthday": data[0][2],
            "status": data[0][3]
        }
        self.dialog = Dialog(True, data_dialog, self)
        self.dialog.show()

    def _get_id(self):
        current_row = self.currentRow()
        if current_row == -1: return None

        return self.item(current_row, 0)

class SubgrpsTable(QTableWidget):
    def __init__(self):
        super().__init__()
        self.students, self.names, self.subgrps = get_subgrps()
        self._add_labels()
        self._add_subgrps_data()

    def _add_labels(self):
        hor_labels = [name[1] for name in self.names]
        self.setColumnCount(len(hor_labels))

        ver_labels = [name[1] for name in self.students]
        self.setRowCount(len(ver_labels))

        self.setHorizontalHeaderLabels(hor_labels)
        self.setVerticalHeaderLabels(ver_labels)

    def _add_subgrps_data(self):
        for r, student in enumerate(self.students):
            for c, subgrp_name in enumerate(self.names):
                mark_data = self.subgrps.get((r+1, c+1))
                mark = QTableWidgetItem(str(mark_data['mark']) if mark_data is not None else '')
                self.setItem(r, c, mark)

    def _save_data(self):
        rows = self.rowCount()
        columns = self.columnCount()

        data = []

        for row in range(rows):
            for col in range(columns):
                item = self.item(row, col)
                text = item.text() if item is not None else "1"
                data.append((row+1, col+1, text))

        update_subgrps(data)

class subgrpWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.button = QPushButton("Сохранить")
        self.subgrps = SubgrpsTable()
        layout.addWidget(self.subgrps)
        layout.addWidget(self.button)

        self.button.clicked.connect(self._save)

    def _save(self):
        self.subgrps._save_data()

class Tabs(QTabWidget):
    def __init__(self):
        super().__init__()
        self.table = Table()
        self.subgrps = subgrpWidget()
        self.addTab(self.table, "Список студентов")
        self.addTab(self.subgrps, "Подгруппы")

class StudentsToolbar(QToolBar):
    def __init__(self):
        super().__init__()
        self.setMovable(False)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        self.set_actions()

    def set_actions(self):
        addStudent = QAction(QIcon("document-new"), "Добавить студента", self)

        addStudent.triggered.connect(self._show_dialog)
        self.dialog = None

        self.addAction(addStudent)

    def _show_dialog(self):
        self.dialog = Dialog(False, None, self.parent().tabs.table)
        self.dialog.show()

class StudentsTable(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('ИС "Старостат" - справочник студентов')
        self.resize(600, 800)

        central = QWidget()
        layout = QVBoxLayout()

        toolbar = StudentsToolbar()

        self.tabs = Tabs()

        self.setCentralWidget(central)
        central.setLayout(layout)
        self.addToolBar(toolbar)
        layout.addWidget(self.tabs)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StudentsTable()
    window.show()
    sys.exit(app.exec())