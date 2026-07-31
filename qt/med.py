import sys
from datetime import datetime

from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QToolBar,
    QLabel,
    QComboBox,
    QMainWindow,
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
    )

from query.select import get_med, get_med_item
from query.insert import insert_med

class addDialog(QDialog):
    def __init__(self, students, edit, med_data: dict | None, med_table):
        super().__init__()
        self.students = students
        self.edit = edit
        self.table = med_table
        self.med_data = med_data
        self.setWindowTitle("Сведение о заболевшем")
        self._add_widgets()

    def _add_widgets(self):
        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)

        full_name_label = QLabel("ФИО обучающегося: ")
        self.full_name = QComboBox()
        for id_, full_name_data in self.students.items():
            self.full_name.addItem(full_name_data, id_)

        date_start_label = QLabel("Дата начала: ")
        self.date_start = QDateEdit()

        date_end_label = QLabel("Дата окончания: ")
        self.date_end = QDateEdit()

        url_label = QLabel("Ссылка на справку: ")
        self.url = QLineEdit()

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        self.buttons.accepted.connect(self.addMed)
        self.buttons.destroyed.connect(self.hide_show)

        if self.edit:
            self.full_name.setCurrentIndex(self.med_data['student_id']-1)
            start_date_data = datetime.strptime(self.med_data['start_date'], "%Y-%m-%d")
            start_date = QDate()
            start_date.setDate(start_date_data.year, start_date_data.month, start_date_data.day)
            end_date_data = datetime.strptime(self.med_data['end_date'], "%Y-%m-%d")
            end_date = QDate()
            end_date.setDate(end_date_data.year, end_date_data.month, end_date_data.day)
            self.date_start.setDate(start_date)
            self.date_end.setDate(end_date)
            self.url.setText(self.med_data['url'])

        self.main_layout.addWidget(full_name_label, 0, 0)
        self.main_layout.addWidget(self.full_name, 0, 1)
        self.main_layout.addWidget(date_start_label, 1, 0)
        self.main_layout.addWidget(self.date_start, 1, 1)
        self.main_layout.addWidget(date_end_label, 2, 0)
        self.main_layout.addWidget(self.date_end, 2, 1)
        self.main_layout.addWidget(url_label, 3, 0)
        self.main_layout.addWidget(self.url, 3, 1)
        self.main_layout.addWidget(self.buttons, 4, 1)

    def addMed(self):
        self.id = self.full_name.currentData()
        self.date_start_data = self.date_start.date().toPyDate()
        self.date_end_data = self.date_end.date().toPyDate()
        self.url_data = self.url.text()

        # преобразование в текст для БД
        self.date_start_data = self.date_start_data.strftime("%Y-%m-%d")
        self.date_end_data = self.date_end_data.strftime("%Y-%m-%d")

        self.data = [
            self.id,
            self.date_start_data,
            self.date_end_data,
            self.url_data
        ]

        insert_med(self.data)
        self.table._add_med_data()
        self.hide()

    def hide_show(self):
        self.hide()

class Table(QTableWidget):
    def __init__(self):
        super().__init__()

        self._add_labels()
        self._add_med_data()
        self._set_edit()

    def _add_labels(self):
        hor_labels = ['ID', 'ФИО', 'Дата начала', 'Дата конца', 'Ссылка на справку']

        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(item for item in hor_labels)
        headers = self.horizontalHeader()
        for i in range(len(hor_labels)):
            headers.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    def _add_med_data(self):
        self.med_data, self.students = get_med()
        self.setRowCount(len(self.med_data))

        for r, data_item in enumerate(self.med_data):
            id = QTableWidgetItem(str(data_item[0]))
            student = QTableWidgetItem(self.students[data_item[1]])
            data_start = QTableWidgetItem(data_item[2])
            data_end = QTableWidgetItem(data_item[3])
            url = QTableWidgetItem(data_item[4])

            self.setItem(r, 0, id)
            self.setItem(r, 1, student)
            self.setItem(r, 2, data_start)
            self.setItem(r, 3, data_end)
            self.setItem(r, 4, url)

    def _set_edit(self):
        self.itemDoubleClicked.connect(self._open_dialog_edit)
        self.dialog = None

    def _open_dialog_edit(self):
        data = get_med_item(self._get_id().text())
        data_dialog = {
            "student_id": data[0][0],
            "start_date": data[0][1],
            "end_date": data[0][2],
            "url": data[0][3]
        }
        self.dialog = addDialog(self.students, True, data_dialog, self)
        self.dialog.show()

    def _get_id(self):
        current_row = self.currentRow()
        if current_row == -1: return None

        return self.item(current_row, 0)


class Toolbar(QToolBar):
    def __init__(self):
        super().__init__()
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self._add_actions()

    def _add_actions(self):
        self.add = QAction(QIcon.fromTheme("document-new"), "Добавить справку", self)
        self.add.triggered.connect(self._show_dialog)
        self.dialog = None

        self.addAction(self.add)

    def _show_dialog(self):
        self.dialog = addDialog(self.parent().table.students, False, None, self.parent().table)
        self.dialog.show()

class Med(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('ИС "Старостат" - информация об отсутствующих')
        self.resize(600, 400)

        central = QWidget()
        layout = QVBoxLayout()

        toolbar = Toolbar()

        self.table = Table()

        self.setCentralWidget(central)
        central.setLayout(layout)
        self.addToolBar(toolbar)
        layout.addWidget(self.table)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = Med()
    main_window.show()
    sys.exit(app.exec())