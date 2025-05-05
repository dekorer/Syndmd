from PySide6.QtWidgets import QApplication, QMainWindow
import sys
from app_ui import Ui_MainWindow 

class WindowClass(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # QAction 연결
        self.ui.action_open.triggered.connect(self.openFunction)
        ##self.ui.action_save.triggered.connect(self.saveFunction)

        # 버튼 클릭 시 함수 연결
        self.ui.pushButton.clicked.connect(self.on_click)

    def openFunction(self):
        print("Open function executed!")

   ## def saveFunction(self):
        ##print("Save function executed!")

    def on_click(self):
        print("버튼이 눌렸습니다.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainwindow = WindowClass()
    mainwindow.show()
    sys.exit(app.exec())
