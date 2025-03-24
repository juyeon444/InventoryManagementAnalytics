import sys
from PyQt5.QtWidgets import QApplication
from config import load_stylesheet
from database import db
from main_window import MainWindow  # The file that contains the MainWindow class with a QStackedWidget

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet())

    main_win = MainWindow()
    main_win.show()

    exit_code = app.exec_()
    db.close_connection() 
    sys.exit(exit_code)
