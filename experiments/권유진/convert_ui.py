import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QWidget, QFrame, QLineEdit, QSizePolicy, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QPushButton, QDialog, QMessageBox
from PySide6.QtCore import QUrl, Qt, QFile, QRegularExpression, Signal
from PySide6.QtGui import QFont, QWheelEvent, QTextCursor

from dark_theme import dark_stylesheet
from app_ui import Ui_MainWindow
from find import Ui_Dialog
from template import AddressManagerWidget


class FindWindow(QDialog):  ## 찾기 기능
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.lineEdit.returnPressed.connect(self.findnext)

        self.main_window = parent # 찾기 박스 다크모드 적용
        if hasattr(parent, 'dark_mode') and parent.dark_mode:
            from dark_theme import dark_stylesheet
            self.setStyleSheet(dark_stylesheet)

        self.show()

        self.ui.pushButton_findnext.setObjectName("FindButton")
        self.ui.pushButton_cancel.setObjectName("FindButton")

        self.pe = parent.ui.textEdit
        self.cursor = self.pe.textCursor()
        self.last_pos = 0

        self.ui.pushButton_findnext.clicked.connect(self.findnext)
        self.ui.pushButton_cancel.clicked.connect(self.close)

    def findnext(self):
        print("findnext called")
        pattern = self.ui.lineEdit.text()
        if not pattern:
            return

        regex = QRegularExpression(pattern)
        if self.ui.checkBox_CaseSenesitive.isChecked():
            regex.setPatternOptions(QRegularExpression.NoPatternOption)
        else:
            regex.setPatternOptions(QRegularExpression.CaseInsensitiveOption)

        text = self.pe.toPlainText()
        self.cursor = self.pe.textCursor()  # 최신 커서

        if self.ui.checkBox_UpDown.isChecked():
            if self.ui.radioButton_Up.isChecked():
                if self.last_pos >= len(text):
                    self.last_pos = 0
                match = regex.match(text, self.last_pos)
                if match.hasMatch():
                    start = match.capturedStart()
                    length = match.capturedLength()
                    self.highlightText(start, start + length)
                    self.last_pos = start + length
                    return

            elif self.ui.radioButton_Down.isChecked():
                if self.last_pos == 0:
                    self.last_pos = len(text)
                it = regex.globalMatch(text)
                prev_match = None
                while it.hasNext():
                    m = it.next()
                    pos = m.capturedStart()
                    if pos < self.last_pos:
                        prev_match = m
                    else:
                        break
                if prev_match:
                    start = prev_match.capturedStart()
                    length = prev_match.capturedLength()
                    self.highlightText(start, start + length)
                    self.last_pos = start
                    return

            self.show_not_found_message(pattern)

        else:
            match = regex.match(text, self.last_pos)
            if match.hasMatch():
                start = match.capturedStart()
                length = match.capturedLength()
                self.highlightText(start, start + length)
                self.last_pos = start + length
            else:
                self.show_not_found_message(pattern)

    def show_not_found_message(self, pattern):
        QMessageBox.warning(self, "찾기", f"'{pattern}'을(를) 찾을 수 없습니다.")

    def highlightText(self, start, end):
        self.cursor = self.pe.textCursor()
        self.cursor.setPosition(start)  # 앞에 커서를 찍음
        self.cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, end - start)  # 뒤로 커서를 움직임
        self.pe.setTextCursor(self.cursor)


    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.findnext()
            event.accept()
        else:
            super().keyPressEvent(event)





class WindowClass(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


        self.dark_mode = False #다크 모드 관련
        

        # 메뉴·버튼 연결
        self.ui.action_open.triggered.connect(self.openFunction)
        self.ui.action_save.triggered.connect(self.saveFunction)
        self.ui.action_find.triggered.connect(self.findFunction)
        self.ui.action_close.triggered.connect(self.close)
        self.ui.pushButton.clicked.connect(self.on_conversion)
        self.ui.pushButton_open.clicked.connect(self.open_click)
        self.ui.action_zoom_in.triggered.connect(self.zoom_in)
        self.ui.action_zoom_out.triggered.connect(self.zoom_out)
        self.ui.action_8.triggered.connect(self.toggle_theme)


        target_tab = self.ui.tab_template
        if target_tab.layout() is None:
            from PySide6.QtWidgets import QVBoxLayout
            target_tab.setLayout(QVBoxLayout())

        target_tab.layout().addWidget(AddressManagerWidget())


    def zoom_in(self):
        font = self.ui.textEdit.font()
        size = font.pointSize()
        font.setPointSize(size + 1)
        self.ui.textEdit.setFont(font)

    def zoom_out(self):
        font = self.ui.textEdit.font()
        size = font.pointSize()
        font.setPointSize(max(1, size - 1))
        self.ui.textEdit.setFont(font)

    def closeEvent(self, event):
        ret = self.show_message_box("종료하시겠습니까? 저장되지 않거나 변환되지 않은 파일은 전부 삭제됩니다. ", QMessageBox.Question, QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            self.save_addresses()
            event.accept()
        else:
            event.ignore()


    def openFunction(self):
        msgBox = QMessageBox()
        path, _ = QFileDialog.getOpenFileName(self, "파일 열기", "", "Text Files (*.txt *.md);;All Files (*)")
        if path:
            with open(path, encoding="utf-8") as f:
                 if not (path.endswith(".md ") or path.endswith(".txt")):
                    QMessageBox.warning(self, "잘못된 파일", ".md 혹은 .txt 형식의 파일만 불러올 수 있습니다.")
                    return
                 text = f.read()
                 self.ui.textEdit.setPlainText(text)
                 
                 print(f"{path} 파일을 열었습니다.")
                 self.ui.textEdit.setPlainText(text)


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
                if not (path.endswith(".md ") or path.endswith(".txt")):
                    QMessageBox.warning(self, "잘못된 파일", ".md 혹은 .txt 형식의 파일만 불러올 수 있습니다.")
                    return
                text = f.read()
            self.ui.textEdit.setPlainText(text)
            print(f"{path} 파일을 열었습니다.")

    def on_conversion(self):
        self.show_message_box("변환 되었습니다.")


    def toggle_theme(self):
        if self.dark_mode:
            self.setStyleSheet("")  # 라이트 모드
        else:
            self.setStyleSheet(dark_stylesheet)  # 다크 모드 적용
        self.dark_mode = not self.dark_mode
    
    def show_message_box(self, text, icon=QMessageBox.Information, buttons=QMessageBox.Ok):
        msgBox = QMessageBox(self)
        msgBox.setText(text)
        msgBox.setIcon(icon)
        msgBox.setStandardButtons(buttons)

        if self.dark_mode:
            msgBox.setStyleSheet("""
                QMessageBox {
                    background-color: #2b2b2b;
                    color: white;
                }
                QLabel {
                    color: white;
                    font-size: 10pt;
                }
                QPushButton {
                    background-color: #3c3f41;
                    color: white;
                    border: 1px solid #5c5f61;
                    border-radius: 4px;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background-color: #2a82da;
                }
            """)

        return msgBox.exec()



if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # 스타일시트 한 번만 적용
    app.setStyleSheet("""
    QMainWindow { background-color: #f5f7fa; }
    QLabel { font-size: 14px; font-weight: 600; color: #2c3e50; }
    
    /* 메시지박스 전용 텍스트 */
    QMessageBox QLabel {
        font-size: 10pt;
        font-weight: normal;
        color: black;
}

    /* 메시지박스 전용 버튼 */
    QMessageBox QPushButton {
        font-size: 10pt;
        font-weight: normal;
        padding: 4px 10px;
        min-width: 80px;
        background-color: #e0e0e0;
        color: #000;
        border: 1px solid #aaa;
        border-radius: 4px;
}
                      
    QPushButton {
        background-color: #3498db;
        border-radius: 8px;
        color: white;
        padding: 10px 18px;
        font-weight: bold;
        font-size: 13px;
        border: none;
        transition: background-color 0.3s ease;
    }
    QPushButton:hover { background-color: #2980b9; }
    QPushButton:pressed { background-color: #1c5980; }
    QTextEdit, ZoomableTextEdit {
        background-color: white;
        border: 1.5px solid #bdc3c7;
        border-radius: 6px;
        padding: 8px;
        font-size: 13px;
        color: #2c3e50;
    }
    QTabWidget::pane {
        border: 1px solid #dcdcdc;
        border-radius: 6px;
        background: white;
    }
    QTabBar::tab {
        background: #ecf0f1;
        border: 1px solid #dcdcdc;
        border-bottom: none;
        padding: 8px 16px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        margin-right: 4px;
        font-weight: 600;
        color: #34495e;
    }
    QTabBar::tab:selected {
        background: white;
        font-weight: 700;
        color: #2c3e50;
        border-color: #3498db;
    }
    QStatusBar { background-color: #ecf0f1; color: #34495e; }
    QMenuBar { background-color: #3498db; color: white; }
    QMenuBar::item { background-color: transparent; padding: 4px 10px; }
    QMenuBar::item:selected { background-color: #2980b9; }
    QMenu {
        background-color: white;
        border: 1px solid #dcdcdc;
        color: #2c3e50;
    }
    QMenu::item:selected {
        background-color: #3498db;
        color: white;
    }
    """)

    win = WindowClass()
    win.show()
    sys.exit(app.exec())
