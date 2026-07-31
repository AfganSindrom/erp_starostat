import sys
from datetime import date
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QScrollArea, QApplication, QDialog, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QFrame, QLabel, QPushButton, QLineEdit, QComboBox, QGridLayout, QMessageBox

import yaml
from pathlib import Path

import query.connect as connect
import query.constants as constants
import query.insert as insert
import query.select as select

class SemesterItem(QFrame):
    clicked = pyqtSignal()
    doubleClicked = pyqtSignal(str)

    def __init__(self, title: str, hours: str, disciplines: str, folder_path: str):
        super().__init__()
        self.folder_path = folder_path
        self.setObjectName('semesterItem')
        self.selected = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)

        self.titleLabel = QLabel(title)
        title_font = self.titleLabel.font()
        title_font.setBold(True)
        title_font.setPointSize(title_font.pointSize() + 4)
        self.titleLabel.setFont(title_font)

        self.hoursLabel = QLabel(hours)
        self.disciplinesLabel = QLabel(disciplines)

        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.Shape.HLine)
        self.separator.setFrameShadow(QFrame.Shadow.Sunken)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(4)
        layout.addWidget(self.titleLabel)
        layout.addWidget(self.hoursLabel)
        layout.addWidget(self.disciplinesLabel)
        layout.addWidget(self.separator)

        self.setStyleSheet(
            "QFrame#semesterItem {"
            "  border: 1px solid palette(mid);"
            "  border-radius: 6px;"
            "  background: palette(base);"
            "}"
            "QFrame#semesterItem:hover {"
            "  background: palette(alternate-base);"
            "}"
            "QFrame#semesterItem[selected=\"true\"] {"
            "  background: palette(highlight);"
            "  color: palette(highlighted-text);"
            "}"
        )
        self.updateStyle()

    def mousePressEvent(self, event):
        self.selected = True
        self.updateStyle()
        self.clicked.emit()
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit(self.folder_path)
        super().mouseDoubleClickEvent(event)

    def updateStyle(self):
        self.setProperty('selected', 'true' if self.selected else 'false')
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

class Choise(QFrame):
    def __init__(self, open_editor_callback):
        super().__init__()

        self.open_editor_callback = open_editor_callback
        self.selected_item: SemesterItem | None = None

        layout = QHBoxLayout()
        scroll = QScrollArea()
        contents = QWidget()
        self.contentLayout = QVBoxLayout()

        self.setLayout(layout)
        layout.addWidget(scroll)
        scroll.setWidgetResizable(True)
        contents.setLayout(self.contentLayout)
        scroll.setWidget(contents)

        self.load_semesters()

    def load_semesters(self):
        while self.contentLayout.count() > 0:
            item = self.contentLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        names = connect.get_names(constants.FOLDER)
        for name in names:
            title = constants.SEMESTER_TYPES[name['season']] + " семестр 20" + name['year_start'] + '/' + name['year_end']
            _, _, calendar, plan, timetable = connect.get_semester_data(name['folder_path'])
            total_hours = sum(int(item.get('hours', 0) or 0) for item in (plan or []))
            discipline_count = len(plan or [])

            item = SemesterItem(
                title,
                f'Суммарное количество часов: {total_hours}',
                f'Количество дисциплин: {discipline_count}',
                name['folder_path']
            )
            # ensure only one item is selected at a time
            item.clicked.connect(lambda _=None, it=item: self.on_item_clicked(it))
            item.doubleClicked.connect(lambda fp=name['folder_path'], it=item: self.on_item_double_clicked(it, fp))
            self.contentLayout.addWidget(item)

        self.contentLayout.addStretch()

    def on_item_clicked(self, item: SemesterItem):
        if self.selected_item is item:
            return
        if self.selected_item:
            self.selected_item.selected = False
            self.selected_item.updateStyle()
        item.selected = True
        item.updateStyle()
        self.selected_item = item

    def on_item_double_clicked(self, item: SemesterItem, folder_path: str):
        # select the item and open editor (which writes config.yml)
        self.on_item_clicked(item)
        self.open_editor_callback(folder_path)

class Semesters(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('ИС "Старостат" - выбор семестра')
        self.resize(600, 400)

        layout = QVBoxLayout()
        self.choise = Choise(self.open_semester_editor)

        self.setLayout(layout)
        layout.addWidget(self.choise)

    def open_semester_editor(self, folder_path: str | None = None):
        """If called with a folder_path (from double-click), write it as the current
        semester into the project's config.yml. If called without arguments (Add
        button), show a simple info message for now.
        """
        if not folder_path:
            QMessageBox.information(self, 'Добавить семестр', 'Добавление семестра не реализовано в этом диалоге.')
            return

        try:
            cfg_path = Path(__file__).parent.parent.parent / 'config.yml'
            with open(cfg_path, 'r', encoding='utf-8') as f:
                cfg = yaml.safe_load(f) or {}
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось прочитать config.yml:\n{e}')
            return

        folder_name = Path(folder_path).name
        if 'config' not in cfg or not isinstance(cfg.get('config'), dict):
            cfg['config'] = {}
        cfg['config']['current'] = folder_name

        try:
            with open(cfg_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(cfg, f, allow_unicode=True)
            # Try to update the in-memory config in query.connect if present
            try:
                connect.config = cfg
            except Exception:
                pass
            QMessageBox.information(self, 'Готово', f'Текущий семестр установлен: {folder_name}. Пожалуйста, перезагрузите приложение.')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось записать config.yml:\n{e}')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Semesters()
    window.show()
    sys.exit(app.exec())