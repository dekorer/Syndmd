from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
import sys
from app_ui import Ui_MainWindow
from PySide6.QtWidgets import QTextEdit
from PySide6.QtCore import QUrl
from PySide6.QtCore import Qt
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QDialog
from find import Ui_Dialog
from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QTextCursor
from PySide6.QtCore import QRegularExpression, QRegularExpressionMatch
from PySide6.QtGui import QFont
from PySide6.QtGui import QWheelEvent



class FindWindow(QDialog): ## 찾기 기능
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.show()

        self.pe=parent.ui.textEdit
        self.cursor = self.pe.textCursor()
        self.last_pos = 0

        self.ui.pushButton_findnext.clicked.connect(self.findnext)
        self.ui.pushButton_cancel.clicked.connect(self.close)

    def findnext(self):

        self.cursor = self.pe.textCursor()  # 최신 커서 받아오기

        pattern = self.ui.lineEdit.text()
        regex = QRegularExpression(pattern)
        text = self.pe.toPlainText()

        if self.ui.checkBox_CaseSenesitive.isChecked():
            regex.setPatternOptions(QRegularExpression.NoPatternOption) 
        else: 
            regex.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
        
        text = self.pe.toPlainText()
        match = regex.match(text, self.last_pos)


    
        if match.hasMatch():
            # match.capturedStart()로 일치한 부분의 시작 위치를 찾음
            start = match.capturedStart()  # 일치 시작 위치
            length = match.capturedLength()  # 일치한 텍스트의 길이
            self.setCursor(start, start+length)# 일치한 텍스트 출력
            self.last_pos = start+length # 끝 위치 저장
        else:
            print("No match found.")
            msgBox = QMessageBox()
            msgBox.setText(f"'{pattern}'을(를) 찾을 수 없습니다.")
            msgBox.exec()


    def keyReleaseEvent(self, event):
        print(self.ui.lineEdit.text())
        if self.ui.lineEdit.text():
            self.ui.pushButton_findnext.setEnabled(True)
        else:
            self.ui.pushButton_findnext.setEnabled(False)

    def setCursor(self, start, end):
        #print(self.cursor.selectionStart(), self.cursor.selectionEnd())
        self.cursor = self.pe.textCursor()
        self.cursor.setPosition(start) #앞에 커서를 찍음
        self.cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, end-start) #뒤로 커서를 움직임
        # 커서 설정 후 텍스트 편집기에 커서를 적용
        self.pe.setTextCursor(self.cursor)


class WindowClass(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 2) 메뉴·버튼 연결
        self.ui.action_open.triggered.connect(self.openFunction)
        self.ui.action_save.triggered.connect(self.saveFunction)
        self.ui.action_find.triggered.connect(self.findFunction)
        self.ui.action_close.triggered.connect(self.close)
        self.ui.pushButton.clicked.connect(self.on_conversion)
        self.ui.pushButton_open.clicked.connect(self.open_click)
        self.ui.action_zoom_in.triggered.connect(self.zoom_in)
        self.ui.action_zoom_out.triggered.connect(self.zoom_out)

    def zoom_in(self): ##키보드/메뉴바 사용
        font = self.ui.textEdit.font()
        size = font.pointSize()
        font.setPointSize(size + 1)
        self.ui.textEdit.setFont(font)

    def zoom_out(self): ##키보드/메뉴바 사용
        font = self.ui.textEdit.font()
        size = font.pointSize()
        font.setPointSize(max(1, size - 1))
        self.ui.textEdit.setFont(font)


    def closeEvent(self, event):
        msgBox = QMessageBox()
        msgBox.setText("종료하시겠습니까?")
        msgBox.addButton("예", QMessageBox.YesRole)
        msgBox.addButton("아니요", QMessageBox.RejectRole)
        ret = msgBox.exec()
        print(ret)
        if ret == 3:
            event.ignore()
            print("exit ignore")

    def openFunction(self):
        path, _ = QFileDialog.getOpenFileName(self, "파일 열기", "", "Text Files (*.txt *.md);;All Files (*)")
        if path:
            with open(path, encoding="utf-8") as f:
                text = f.read()
            self.ui.textEdit.setPlainText(text)
            print(f"{path} 파일을 열었습니다.")

    def saveFunction(self):
        path, _ = QFileDialog.getSaveFileName(self, "파일 저장", "", "Text Files (*.txt *.md);;All Files (*)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.ui.textEdit.toPlainText())
            print(f"{path} 파일이 저장되었습니다.")

        
    def findFunction(self):
        FindWindow(self)
    

    def open_click(self):
        path, _ = QFileDialog.getOpenFileName(self, "파일 열기", "", "Text Files (*.txt *.md);;All Files (*)")
        if path:
            with open(path, encoding="utf-8") as f:
                text = f.read()
            self.ui.textEdit.setPlainText(text)
            print(f"{path} 파일을 열었습니다.")


    def on_conversion(self):
        msgBox = QMessageBox()
        msgBox.setText("변환 되었습니다.     ")
        print("press conversion.")
        msgBox.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = WindowClass()
    win.show()
    sys.exit(app.exec())