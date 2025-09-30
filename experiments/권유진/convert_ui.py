import sys ,tempfile, os, fitz, pythoncom, subprocess
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QWidget, QFrame, QLineEdit, QSizePolicy, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QPushButton, QDialog, QMessageBox, QScrollArea
from PySide6.QtCore import QUrl, Qt, QFile, QRegularExpression, Signal , QObject, QSize, QTimer, QThread
from PySide6.QtGui import QFont, QWheelEvent, QTextCursor, QPixmap, QImage

from loading_preview import Ui_Form
from dark_theme import dark_stylesheet
from app_ui import Ui_MainWindow
from find import Ui_Dialog
from template import AddressManagerWidget

from pathlib import Path


class Worker(QObject):
    # 진행률을 int(퍼센트)로 전달하는 신호 추가
    progress = Signal(int)
    # 최종 결과 신호는 동일
    finished = Signal(QPixmap, Exception)

    def __init__(self, main_window, hwp_path):
        super().__init__()
        self.main_window = main_window 
        self.hwp_path = hwp_path

    def run(self):
        """이 함수가 백그라운드 스레드에서 실행됩니다."""
        try:
            # 1. 작업 시작 (50%)
            #    HWP 생성은 이미 끝났으므로, 전체 작업의 50% 지점에서 시작합니다.
            self.progress.emit(50)
            
            # MainWindow의 generate_preview_pixmap 함수를 호출합니다.
            pixmap = self.main_window.generate_preview_pixmap(self.hwp_path)
            
            # 2. 작업 완료 (100%)
            self.progress.emit(100)
            
            self.finished.emit(pixmap, None)
        except Exception as e:
            self.finished.emit(QPixmap(), e)


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
   

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.tmp_md_path = None

        self.dark_mode = False #다크 모드

        # 메뉴·버튼 연결
        self.ui.action_open.triggered.connect(self.openFunction)
        self.ui.action_save.triggered.connect(self.saveFunction)
        self.ui.action_find.triggered.connect(self.findFunction)
        self.ui.action_close.triggered.connect(self.close)
        self.ui.pushButton.clicked.connect(self.on_conversion)
        self.ui.pushButton_preview.clicked.connect(self.on_preview)
        self.ui.pushButton_open.clicked.connect(self.open_click)
        self.ui.action_zoom_in.triggered.connect(self.zoom_in)
        self.ui.action_zoom_out.triggered.connect(self.zoom_out)
        self.ui.action_8.triggered.connect(self.toggle_theme)

               # --- 로딩 위젯 초기화 ---
        self.loading_widget = QWidget() 
        self.loading_ui = Ui_Form()
        self.loading_ui.setupUi(self.loading_widget)
        # QWidget을 창처럼 보이게 하고, 항상 위에 있도록 설정
        self.loading_widget.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowStaysOnTopHint)
        self.loading_widget.setWindowTitle("실행 중... (약간의 시간이 소요됩니다.)")
        # ---------------------------
        self.thread = None
        self.worker = None




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
                 if not (path.endswith(".md") or path.endswith(".txt")):
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





###미리보기 파트


    def on_preview(self):
        """'미리보기' 버튼: Worker를 사용하여 비동기로 미리보기를 생성합니다."""
        if self.thread and self.thread.isRunning():
            QMessageBox.warning(self, "처리 중", "이미 다른 작업이 진행 중입니다.")
            return

        text_content = self.ui.textEdit.toPlainText()
        if not text_content.strip(): return

        # --- 1. 로딩 창 설정 및 표시 (수정) ---
        # 프로그레스 바를 0~100 범위로 설정하고, 텍스트를 보이게 합니다.
        self.loading_ui.preview_progressBar.setRange(0, 100)
        self.loading_ui.preview_progressBar.setValue(0)
        # self.loading_ui.preview_progressBar.setTextVisible(True) # 필요하다면 주석 해제

        # HWP 생성을 시작하기 전에 10%를 채웁니다.
        self.update_progress(10)
        self.loading_widget.show()
        QApplication.processEvents()
        
        try:
            # 2. 임시 HWP 생성 (이 작업이 끝나면 50%를 채웁니다)
            temp_dir = tempfile.gettempdir()
            temp_hwp_path = os.path.join(temp_dir, "preview_temp.hwp")
            self.run_make_hwp(text_content, temp_hwp_path)
            self.update_progress(50) # HWP 생성 완료

            # 3. QThread와 Worker 설정 (수정)
            self.thread = QThread()
            self.worker = Worker(self, temp_hwp_path) 
            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.on_preview_finished)
            
            # --- 핵심 추가: progress 신호를 update_progress 슬롯에 연결 ---
            self.worker.progress.connect(self.update_progress)
            
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.finished.connect(self.worker.deleteLater)
            
            self.thread.start()

        except Exception as e:
            QMessageBox.critical(self, "미리보기 오류", f"미리보기 준비 중 오류가 발생했습니다:\n{e}")
            self.loading_widget.close()

    def update_progress(self, value):
        ##Worker가 보낸 진행률(value)로 프로그레스 바를 업데이트하는 슬롯
        self.loading_ui.preview_progressBar.setValue(value)
        QApplication.processEvents() # 프로그레스 바 업데이트를 즉시 화면에 반영

    def on_preview_finished(self, pixmap, error):
        ##Worker 스레드가 작업을 마쳤을 때 호출
        self.loading_widget.close() # 로딩 창 닫기
        
        if error:
            QMessageBox.critical(self, "미리보기 생성 실패", f"{error}")
            return
        
        # Worker가 성공적으로 만들어준 QPixmap을 화면에 표시
        self.display_preview_image(pixmap)

    # on_conversion과 run_make_hwp는 당신의 "정상 작동 코드"와 100% 동일합니다.
    # 수정할 필요가 없습니다.

    def on_conversion(self):
        """'변환' 버튼: 로딩 창을 띄우고 사용자가 지정한 이름의 HWP 파일을 저장합니다."""
        text_content = self.ui.textEdit.toPlainText()
        if not text_content.strip():
            QMessageBox.warning(self, "내용 없음", "변환할 내용을 먼저 입력해주세요.")
            return

        save_path_hwp, _ = QFileDialog.getSaveFileName(self, "HWP로 저장", "", "한글 파일 (*.hwp)")
        if not save_path_hwp:
            return

        # --- 1. 작업의 성공/실패 상태와 메시지를 저장할 변수 초기화 ---
        success = False
        error_message = ""

        # --- 2. 로딩 창 재활용 및 내용 변경 ---
        self.loading_ui.label.setText("HWP 파일로 변환 중입니다...")
        self.loading_ui.preview_progressBar.setRange(0, 0)
        self.loading_widget.show()
        QApplication.processEvents()

        try:
            # --- 3. HWP 저장 작업 수행 ---
            self.run_make_hwp(text_content, save_path_hwp)
            # 성공했다면, 상태 변수를 True로 변경
            success = True
        except Exception as e:
            # 실패했다면, 에러 메시지를 변수에 저장
            error_message = str(e)
            print(f"[변환 오류] {e}") # 터미널에도 로그 남기기
        finally:
            # --- 4. 작업이 끝나면 (성공/실패 무관) 로딩 창을 먼저 닫습니다 ---
            self.loading_widget.close()
            self.loading_ui.label.setText("미리보기를 생성 중입니다...") # 라벨 텍스트 복원
        
        # --- 5. 로딩 창이 완전히 닫힌 후, 결과에 따라 메시지 박스를 띄웁니다 ---
        if success:
            QMessageBox.information(self, "변환 완료", f"HWP 파일이 성공적으로 저장되었습니다:\n{save_path_hwp}")
        else:
            QMessageBox.critical(self, "변환 오류", f"HWP 파일을 저장하는 중 오류가 발생했습니다:\n{error_message}")



    def run_make_hwp(self, text_content, output_hwp_path):
        print(f"[메인 앱] HWP 생성 시작 -> {output_hwp_path}")
        make_hwp_script = os.path.join(os.path.dirname(__file__), 'make_hwp.py')
        temp_dir = tempfile.gettempdir()
        temp_text_path = os.path.join(temp_dir, "content_to_convert.txt")
        with open(temp_text_path, "w", encoding="utf-8") as f:
            f.write(text_content)
        command = [sys.executable, make_hwp_script, temp_text_path, output_hwp_path]
        subprocess.run(command, check=True)
        print(f"[메인 앱] HWP 생성 완료.")

    # --- 기존 generate_and_display_preview를 두 개의 함수로 분리 ---
    
    def generate_preview_pixmap(self, hwp_path):
        
        ## [백그라운드 스레드에서 실행됨]
        ## HWP -> PDF -> QPixmap 변환이라는 무거운 작업을 수행하고 결과물(pixmap)을 반환합니다.

        print(f"[Worker] PDF 변환 시작: {hwp_path}")
        converter_script = os.path.join(os.path.dirname(__file__), 'hwp_converter_ui.py')
        command = [sys.executable, converter_script, hwp_path]
        subprocess.run(command, check=True)

        pdf_path = str(Path(hwp_path).with_suffix('.pdf'))
        if not os.path.exists(pdf_path):
            raise Exception("PDF 파일이 생성되지 않았습니다.")
        
        print(f"[Worker] PDF 렌더링 시작: {pdf_path}")
        doc = fitz.open(pdf_path)
        if doc.page_count == 0:
            raise Exception("PDF 파일에 페이지가 없습니다.")
        page = doc.load_page(0)
        pix = page.get_pixmap()
        doc.close()

        qimage = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        return pixmap # 최종 결과물인 QPixmap 객체를 반환

    def display_preview_image(self, pixmap):
        
        ##[메인 GUI 스레드에서 실행됨]
        ##전달받은 QPixmap 객체를 ScrollArea에 표시합니다.
        if pixmap.isNull(): return
        label = QLabel()
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)
        self.ui.pdfViewerArea.setWidgetResizable(True)
        self.ui.pdfViewerArea.setWidget(label)
        print(f"[메인 앱] 미리보기 이미지 표시 성공.")




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
        QLabel { font-size: 14px; font-weight: 600; color: #000000; }
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
            background-color: #323232;
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
            border-color: #323232;
        }
        QStatusBar { background-color: #ecf0f1; color: #34495e; }
        QMenuBar { background-color: #323232; color: white; }
        QMenuBar::item { background-color: transparent; padding: 4px 10px; }
        QMenuBar::item:selected { background-color: #2980b9; }
        QMenu {
            background-color: white;
            border: 1px solid #dcdcdc;
            color: #2c3e50;
        }
        QMenu::item:selected {
            background-color: #323232;
            color: white;
        }
        """
    
    app = QApplication(sys.argv)
    app.setStyleSheet(light_stylesheet)  # 초기 라이트 테마 적용
    
    win = WindowClass()
    win.show()
    sys.exit(app.exec())
