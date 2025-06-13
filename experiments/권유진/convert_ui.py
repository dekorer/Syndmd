import sys ,tempfile
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QWidget, QFrame, QLineEdit, QSizePolicy, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QPushButton, QDialog, QMessageBox
from PySide6.QtCore import QUrl, Qt, QFile, QRegularExpression, Signal , QObject, QSize
from PySide6.QtGui import QFont, QWheelEvent, QTextCursor, QPixmap

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
        self.ui.lineEdit.textChanged.connect(self.update_button_state) 

        self.main_window = parent  # 찾기 박스 다크모드 적용
        if hasattr(parent, 'dark_mode') and parent.dark_mode:
            from dark_theme import dark_stylesheet
            self.setStyleSheet(dark_stylesheet)

        self.show()

        self.ui.pushButton_findnext.setObjectName("FindButton")
        self.ui.pushButton_cancel.setObjectName("FindButton")

        self.pe = parent.ui.textEdit
        self.cursor = self.pe.textCursor()
        self.last_pos = self.cursor.position()  # 초기값을 커서 위치로 설정

        # 현재 하이라이트 범위 저장용
        self.highlight_start = None
        self.highlight_end = None

        self.ui.pushButton_findnext.clicked.connect(self.findnext)
        self.ui.pushButton_cancel.clicked.connect(self.close)

        #방향 전환 시 현재 last_pos 갱신
        self.ui.radioButton_Up.toggled.connect(self.update_search_position)
        self.ui.radioButton_Down.toggled.connect(self.update_search_position)

        self.update_button_state()  # 초기 버튼 상태 업데이트


    def update_button_state(self):
        # 찾기 버튼 활성화/비활성화
        has_text = bool(self.ui.lineEdit.text().strip())
        self.ui.pushButton_findnext.setEnabled(has_text)

    def update_search_position(self):
        # 방향 변경 시 현재 last_pos 갱신
        if self.highlight_start is not None and self.highlight_end is not None:
            if self.ui.radioButton_Up.isChecked():
                self.last_pos = self.highlight_start
            else:
                self.last_pos = self.highlight_end
        else:
            self.cursor = self.pe.textCursor()
            self.last_pos = self.cursor.position()

        print(f"[update_search_position] Direction toggled → last_pos updated to: {self.last_pos}")

    def findnext(self):
       
        pattern = self.ui.lineEdit.text()
        

        regex = QRegularExpression(pattern)
        if self.ui.checkBox_CaseSenesitive.isChecked():
            regex.setPatternOptions(QRegularExpression.NoPatternOption)
        else:
            regex.setPatternOptions(QRegularExpression.CaseInsensitiveOption)

        text = self.pe.toPlainText()

        # 순환 기능: checkBox_UpDown이 체크되어있으면 "순환" 적용
        if self.ui.checkBox_UpDown.isChecked():
            if self.ui.radioButton_Down.isChecked():
                # 아래로 찾기 순환
                print(f"[findnext] Searching DOWN from position {self.last_pos}")
                match = regex.match(text, self.last_pos)
                if match.hasMatch():
                    start = match.capturedStart()
                    length = match.capturedLength()
                    self.highlightText(start, start + length)
                    self.last_pos = start + length
                    return
                else:
                    # 순환 시도
                    print("[findnext] No match DOWN, wrapping to top")
                    match = regex.match(text, 0)
                    if match.hasMatch():
                        start = match.capturedStart()
                        length = match.capturedLength()
                        self.highlightText(start, start + length)
                        self.last_pos = start + length
                        return
                    else:
                        self.show_not_found_message(pattern)

            elif self.ui.radioButton_Up.isChecked():
                # 위로 찾기 순환
                print(f"[findnext] Searching UP from position {self.last_pos}")
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
                else:
                    # 순환 시도 (맨 끝에서부터 찾기)
                    print("[findnext] No match UP, wrapping to bottom")
                    it = regex.globalMatch(text)
                    last_match = None
                    while it.hasNext():
                        m = it.next()
                        last_match = m
                    if last_match:
                        start = last_match.capturedStart()
                        length = last_match.capturedLength()
                        self.highlightText(start, start + length)
                        self.last_pos = start
                        return
                    else:
                        self.show_not_found_message(pattern)

        else:
            # 순환 OFF → 기존처럼 방향만 처리
            if self.ui.radioButton_Down.isChecked():
                print(f"[findnext] Searching DOWN (no wrap) from position {self.last_pos}")
                match = regex.match(text, self.last_pos)
                if match.hasMatch():
                    start = match.capturedStart()
                    length = match.capturedLength()
                    self.highlightText(start, start + length)
                    self.last_pos = start + length
                    return
                else:
                    self.show_not_found_message(pattern)

            elif self.ui.radioButton_Up.isChecked():
                print(f"[findnext] Searching UP (no wrap) from position {self.last_pos}")
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
                else:
                    self.show_not_found_message(pattern)

    def show_not_found_message(self, pattern):
        QMessageBox.warning(self, "찾기", f"'{pattern}'을(를) 찾을 수 없습니다.")

    def highlightText(self, start, end):
        # 지정 범위를 강조 표시 + 현재 위치 저장
        self.cursor = self.pe.textCursor()
        self.cursor.setPosition(start)
        self.cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, end - start)
        self.pe.setTextCursor(self.cursor)

        # 현재 하이라이트 위치 저장
        self.highlight_start = start
        self.highlight_end = end

        print(f"[highlightText] Highlight updated: start={start}, end={end}")

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if not self.ui.lineEdit.text().strip():
                QMessageBox.warning(self, "찾기", "찾을 내용을 입력하세요.")
                event.accept()
                return
            self.findnext()
            event.accept()
        else:
            super().keyPressEvent(event)





class WindowClass(QMainWindow):
    FIXED_SIZE = QSize(200, 80)
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.tmp_md_path = None

        self.dark_mode = False #다크 모드

        self.original_pixmap = QPixmap('final_logo.png')####로고사진경로(상대경로로)
        self.ui.logo.setAlignment(Qt.AlignCenter)
        self.update_logo_pixmap()####
        self.show()

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

        self.template_selec = AddressManagerWidget() 

        target_tab = self.ui.tab_template
        if target_tab.layout() is None:
            from PySide6.QtWidgets import QVBoxLayout
            target_tab.setLayout(QVBoxLayout())

        target_tab.layout().addWidget(self.template_selec)  

        self.template_selec.status_changed.connect(self.update_template_label)
        self.ui.template_label.setText("템플릿이 적용되지 않았습니다.")

    def update_template_label(self, display_text):
        if display_text == "":
            self.ui.template_label.setText("템플릿이 적용되지 않았습니다.")
        else :
            self.ui.template_label.setText(f"[{display_text}] 템플릿 적용 중입니다.")

    
    def update_logo_pixmap(self):####
        if self.original_pixmap.isNull():
            return

        scaled_pixmap = self.original_pixmap.scaled(
            self.FIXED_SIZE,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.ui.logo.setPixmap(scaled_pixmap)
        

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
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("프로그램 종료")
        msg.setText("종료하시겠습니까? 저장되지 않거나 변환되지 않은 파일은 전부 삭제됩니다.")

        yes_button = msg.addButton("예(&Y)", QMessageBox.YesRole)  # Alt+Y
        no_button = msg.addButton("아니오(&N)", QMessageBox.NoRole)  # Alt+N

        msg.exec()
        if msg.clickedButton() == yes_button:
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
        #여기에 템플릿 파일 존재하는지 체크 해야함
        text = self.ui.textEdit.toPlainText()
       #import tempfile 해야 됨
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".md", mode="w", encoding="utf-8")
        tmp_file.write(text)
        tmp_file.close()

        # 경로 저장 
        tmp_md_path = tmp_file.name
        print(f"tmp.md 파일 저장됨 → {tmp_md_path}")####연결부분(md파일부분)

        # md파일 읽어보기(없어도 됨 테스트용)
        with open(tmp_md_path, "r", encoding="utf-8") as f:
            content = f.read()
            print("tmp.md 내용:\n", content)

        if content == "":
            QMessageBox.warning(self, "변환용 파일 감지 실패", "변환할 파일을 작성해주세요.")
            return

        ####여기 변환 코드 연동해야됨
        
        if self.ui.hwpruncheck.isChecked():
            ### 여기에 한글파일 실행 코드 작성
            self.show_message_box("변환 되었습니다.")
        else:
            self.show_message_box("변환 되었습니다.")


# 다크모드 수정
    def toggle_theme(self):
        app = QApplication.instance()
        if self.dark_mode:
            app.setStyleSheet(light_stylesheet)  # 라이트 스타일 재적용
        else:
            from dark_theme import dark_stylesheet
            app.setStyleSheet(dark_stylesheet)   # 다크 스타일 적용

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



# 다크모드 해제시 스타일 시트 해제 수정
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    light_stylesheet = """
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
        """
    
    app = QApplication(sys.argv)
    app.setStyleSheet(light_stylesheet)  # 초기 라이트 테마 적용
    
    win = WindowClass()
    win.show()
    sys.exit(app.exec())
