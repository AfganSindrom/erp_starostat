import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from qt.start import MainWindow
import query.constants as constants

app = QApplication(sys.argv)

icon_path =  "assets/otto.ico"
app.setWindowIcon(QIcon(str(icon_path)))

main_window = MainWindow()
main_window.show()
app.exec()