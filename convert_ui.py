import sys ,tempfile, os, fitz, pythoncom, subprocess
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QWidget, QFrame, QLineEdit, QSizePolicy, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QPushButton, QDialog, QMessageBox, QScrollArea
from PySide6.QtCore import QUrl, Qt, QFile, QRegularExpression, Signal , QObject, QSize, QTimer, QThread, QEvent
from PySide6.QtGui import QFont, QWheelEvent, QTextCursor, QPixmap, QImage

from loading_preview import Ui_Form
from app_ui import Ui_MainWindow
from find import Ui_Dialog
from template import AddressManagerWidget
from pathlib import Path


## 로딩창
class Worker(QObject):
    progress = Signal(int)
    finished = Signal(QPixmap, Exception)

    # [수정] __init__에서 HWP 파일 경로를 직접 받도록 변경
    def __init__(self, main_window, hwp_file_path):
        super().__init__()
        self.main_window = main_window 
        self.hwp_file_path = hwp_file_path

    def run(self):
        try:
            # --- 1단계: HWP -> PDF -> QPixmap 변환 ---
            self.progress.emit(20)
            pixmap = self.main_window.generate_preview_pixmap(self.hwp_file_path)
            self.progress.emit(100) # 모든 작업 완료
            self.finished.emit(pixmap, None)

        except Exception as e:
            # 오류가 발생하면 에러를 전달
            self.finished.emit(QPixmap(), e)


## 찾기
class FindWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.lineEdit.returnPressed.connect(self.findnext)
        self.ui.lineEdit.textChanged.connect(self.update_button_state) 
        self.main_window = parent
        if hasattr(parent, 'dark_mode') and parent.dark_mode:
            self.setStyleSheet(dark_stylesheet)
        self.show()
        self.ui.pushButton_findnext.setObjectName("FindButton")
        self.ui.pushButton_cancel.setObjectName("FindButton")
        self.pe = parent.ui.textEdit
        self.cursor = self.pe.textCursor()
        self.last_pos = self.cursor.position()
        self.highlight_start = None
        self.highlight_end = None
        self.ui.pushButton_findnext.clicked.connect(self.findnext)
        self.ui.pushButton_cancel.clicked.connect(self.close)
        self.ui.radioButton_Up.toggled.connect(self.update_search_position)
        self.ui.radioButton_Down.toggled.connect(self.update_search_position)
        self.update_button_state()
    def update_button_state(self):
        has_text = bool(self.ui.lineEdit.text().strip())
        self.ui.pushButton_findnext.setEnabled(has_text)
    def update_search_position(self):
        if self.highlight_start is not None and self.highlight_end is not None:
            if self.ui.radioButton_Up.isChecked(): self.last_pos = self.highlight_start
            else: self.last_pos = self.highlight_end
        else:
            self.cursor = self.pe.textCursor()
            self.last_pos = self.cursor.position()


    def findnext(self):
        pattern = self.ui.lineEdit.text()
        regex = QRegularExpression(pattern)
        if self.ui.checkBox_CaseSenesitive.isChecked(): regex.setPatternOptions(QRegularExpression.NoPatternOption)
        else: regex.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
        text = self.pe.toPlainText()
        if self.ui.checkBox_UpDown.isChecked():
            if self.ui.radioButton_Down.isChecked():
                match = regex.match(text, self.last_pos)
                if not match.hasMatch(): match = regex.match(text, 0)
                if match.hasMatch():
                    start, length = match.capturedStart(), match.capturedLength()
                    self.highlightText(start, start + length)
                    self.last_pos = start + length
                    return
                self.show_not_found_message(pattern)
            elif self.ui.radioButton_Up.isChecked():
                it = regex.globalMatch(text)
                prev_match = None
                while it.hasNext():
                    m = it.next()
                    if m.capturedStart() < self.last_pos: prev_match = m
                    else: break
                if not prev_match:
                    it = regex.globalMatch(text)
                    last_match = None
                    while it.hasNext(): last_match = it.next()
                    prev_match = last_match
                if prev_match:
                    start, length = prev_match.capturedStart(), prev_match.capturedLength()
                    self.highlightText(start, start + length)
                    self.last_pos = start
                    return
                self.show_not_found_message(pattern)
        else:
            if self.ui.radioButton_Down.isChecked():
                match = regex.match(text, self.last_pos)
                if match.hasMatch():
                    start, length = match.capturedStart(), match.capturedLength()
                    self.highlightText(start, start + length)
                    self.last_pos = start + length
                    return
            elif self.ui.radioButton_Up.isChecked():
                it = regex.globalMatch(text)
                prev_match = None
                while it.hasNext():
                    m = it.next()
                    if m.capturedStart() < self.last_pos: prev_match = m
                    else: break
                if prev_match:
                    start, length = prev_match.capturedStart(), prev_match.capturedLength()
                    self.highlightText(start, start + length)
                    self.last_pos = start
                    return
            self.show_not_found_message(pattern)


    def show_not_found_message(self, pattern): QMessageBox.warning(self, "찾기", f"'{pattern}'을(를) 찾을 수 없습니다.")


    def highlightText(self, start, end):
        self.cursor = self.pe.textCursor()
        self.cursor.setPosition(start)
        self.cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, end - start)
        self.pe.setTextCursor(self.cursor)
        self.highlight_start, self.highlight_end = start, end


    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if not self.ui.lineEdit.text().strip(): return
            self.findnext()
            event.accept()
        else: super().keyPressEvent(event)




class WindowClass(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.tmp_md_path = None
        self.dark_mode = False
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

        # [추가 1] 선택된 템플릿 정보를 저장할 변수 초기화
        self.selected_template_path = ""
        self.selected_template_page = 0
        
        self.loading_widget = QWidget() 
        self.loading_ui = Ui_Form()
        self.loading_ui.setupUi(self.loading_widget)
        self.loading_widget.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowStaysOnTopHint)
        self.loading_widget.setWindowTitle("실행 중... (약간의 시간이 소요됩니다.)")
        self.thread, self.worker = None, None
        self.template_selec = AddressManagerWidget()
        self.template_overlay_widget = QWidget(self)
        self.template_overlay_widget.setObjectName("templateOverlay")
        overlay_layout = QVBoxLayout(self.template_overlay_widget)
        overlay_layout.setContentsMargins(8, 8, 8, 8)
        overlay_layout.addWidget(self.template_selec)
        self.template_overlay_widget.hide()
        
        self.template_selec.status_changed.connect(self.update_template_label)
        # [추가 2] 새 시그널과 새 슬롯 연결
        self.template_selec.template_selected.connect(self.on_template_selected)
        
        self.ui.template_label.setText("템플릿이 적용되지 않았습니다.")
        self.ui.template_button.clicked.connect(self.toggle_template_widget)

       # [추가 3] 데이터를 받을 새 슬롯(메서드) 정의
    def on_template_selected(self, path, page):
        """AddressManagerWidget에서 보낸 템플릿 정보를 받는 슬롯"""
        self.selected_template_path = path
        self.selected_template_page = page
        
        # 데이터가 잘 들어왔는지 터미널에 출력하여 확인
        print(f"템플릿 경로: {self.selected_template_path}, 페이지: {self.selected_template_page}")

    def update_template_label(self, display_text):
        if not display_text: self.ui.template_label.setText("템플릿이 적용되지 않았습니다.")
        else: self.ui.template_label.setText(f"[{display_text}] 템플릿 적용 중입니다.")

    def toggle_template_widget(self):
        if self.template_overlay_widget.isVisible():
            self.template_overlay_widget.hide()
            self.ui.template_button.setText("템플릿 관리 ▼")
        else:
            self.update_overlay_geometry()
            self.template_overlay_widget.raise_()
            self.template_overlay_widget.show()
            self.ui.template_button.setText("템플릿 관리 ▲")

    def update_overlay_geometry(self):
        main_size = self.size()
        w, h = int(main_size.width() * 0.9), int(main_size.height() * 0.8)
        x, y = int(main_size.width() * 0.05), int(main_size.height() * 0.15)
        self.template_overlay_widget.setGeometry(x, y, w, h)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.template_overlay_widget.isVisible(): self.update_overlay_geometry()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.WindowStateChange and self.template_overlay_widget.isVisible():
            self.update_overlay_geometry()

    def zoom_in(self):
        font = self.ui.textEdit.font()
        font.setPointSize(font.pointSize() + 1)
        self.ui.textEdit.setFont(font)

    def zoom_out(self):
        font = self.ui.textEdit.font()
        font.setPointSize(max(1, font.pointSize() - 1))
        self.ui.textEdit.setFont(font)

    def closeEvent(self, event):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("프로그램 종료")
        msg.setText("종료하시겠습니까? 저장되지 않거나 변환되지 않은 파일은 전부 삭제됩니다.")
        yes_button, no_button = msg.addButton("예(&Y)", QMessageBox.YesRole), msg.addButton("아니오(&N)", QMessageBox.NoRole)
        msg.exec()
        if msg.clickedButton() == yes_button: event.accept()
        else: event.ignore()

    def openFunction(self):
        path, _ = QFileDialog.getOpenFileName(self, "파일 열기", "", "Text Files (*.txt *.md);;All Files (*)")
        if path:
            with open(path, encoding="utf-8") as f: self.ui.textEdit.setPlainText(f.read())

    def saveFunction(self):
        path, _ = QFileDialog.getSaveFileName(self, "파일 저장", "", "Text Files (*.txt *.md);;All Files (*)")
        if path:
            with open(path, "w", encoding="utf-8") as f: f.write(self.ui.textEdit.toPlainText())

    def findFunction(self): FindWindow(self)
    def open_click(self): self.openFunction()

    def update_progress(self, value):
        """Worker가 보낸 진행률(value)로 프로그레스 바를 업데이트하는 슬롯"""
        self.loading_ui.preview_progressBar.setValue(value)
        QApplication.processEvents() # UI를 즉시 갱신


    ## 미리보기 파트

    def on_preview(self):
        """'미리보기': 모든 작업을 처리하는 Worker 스레드를 시작시킵니다."""
        if self.thread and self.thread.isRunning():
            return
            
        text_content = self.ui.textEdit.toPlainText()
        
        # [복구된 부분] 내용이 없으면 경고 메시지를 표시하고 함수를 종료합니다.
        if not text_content.strip():
            QMessageBox.warning(self, "내용 없음", "미리보기를 생성할 내용을 먼저 입력해주세요.")
            return

        self.loading_ui.preview_progressBar.setRange(0, 100)
        self.loading_ui.preview_progressBar.setValue(0)
        self.loading_widget.show()
        
        self.thread = QThread()
        self.worker = Worker(
            self, 
            text_content, 
            self.selected_template_path, 
            self.selected_template_page
        ) 
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_preview_finished)
        self.worker.progress.connect(self.update_progress)
        
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.finished.connect(self.worker.deleteLater)
        
        self.thread.start()
        
    def on_preview_finished(self, pixmap, error):
        self.loading_widget.close()
        if error:
            QMessageBox.critical(self, "미리보기 생성 실패", f"오류가 발생했습니다:\n{error}")
            return
        self.display_preview_image(pixmap)


    def on_conversion(self):
        ## 변환

        text_content = self.ui.textEdit.toPlainText()

        if not text_content.strip():
            QMessageBox.warning(self, "내용 없음", "변환할 내용을 먼저 입력해주세요.")
            return
        
        save_path_hwp, _ = QFileDialog.getSaveFileName(self, "HWP로 저장", "", "한글 파일 (*.hwp)")
        if not save_path_hwp:
            return
       
        success, error_message = False, ""
        self.loading_ui.label.setText("HWP 파일로 변환 중입니다...")
        self.loading_ui.preview_progressBar.setRange(0, 0)
        self.loading_widget.show()
        QApplication.processEvents()

        try:
            self.run_blank_hwp_generator(
                text_content,
                save_path_hwp,
                self.selected_template_path,
                self.selected_template_page
            )
            success = True
        except Exception as e:
            error_message = str(e)
        finally:
            self.loading_widget.close()
            self.loading_ui.label.setText("미리보기를 생성 중입니다...")
        
        if success:
            QMessageBox.information(self, "변환 완료", f"HWP 파일이 성공적으로 저장되었습니다:\n{save_path_hwp}")
        else:
            QMessageBox.critical(self, "변환 오류", f"HWP 파일을 저장하는 중 오류가 발생했습니다:\n{error_message}")


    def run_blank_hwp_generator(self, text_content, output_hwp_path, template_path, template_page):
        ## converter_test에게 인자를 전달
        script_path = os.path.join(os.path.dirname(__file__), 'new0910.py')
        temp_dir = tempfile.gettempdir()
        # 텍스트 내용을 임시 파일에 저장하여 경로를 인자로 전달
        temp_text_path = os.path.join(temp_dir, "content_to_convert.txt")
        with open(temp_text_path, "w", encoding="utf-8") as f:
            f.write(text_content)

        command = [
            sys.executable, 
            script_path, 
            temp_text_path,         # 인자 1: 텍스트 파일 경로
            output_hwp_path,        # 인자 2: 출력 파일 경로 (실제 사용됨)
            template_path,          # 인자 3: 템플릿 경로
            str(template_page)      # 인자 4: 페이지 번호
        ]

            # --- ▼▼▼ 디버깅 코드 추가 ▼▼▼ ---
        print("--- [convert_ui.py] new0910.py 실행 ---")
        print(f"1. 텍스트 파일 경로: {temp_text_path}")
        print(f"2. 최종 HWP 경로: {output_hwp_path}")
        print(f"3. 템플릿 경로: {template_path}")
        print(f"4. 시작 페이지: {template_page}")
        print("-----------------------------------------")
        # --- ▲▲▲ 디버깅 코드 추가 ▲▲▲ ---

        subprocess.run(command, check=True)
            
    def cleanup_temp_files(self, hwp_path):
        """임시 HWP, PDF, TXT 파일을 삭제합니다."""
        try:
            if hwp_path and os.path.exists(hwp_path):
                os.remove(hwp_path)
                print(f"임시 파일 삭제: {hwp_path}")
            
            pdf_path = os.path.splitext(hwp_path)[0] + ".pdf"
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
                print(f"임시 파일 삭제: {pdf_path}")
            
            # 텍스트 임시 파일도 삭제
            temp_text_path = os.path.join(tempfile.gettempdir(), "content_to_convert.txt")
            if os.path.exists(temp_text_path):
                os.remove(temp_text_path)
                print(f"임시 파일 삭제: {temp_text_path}")

        except OSError as e:
            print(f"임시 파일 삭제 오류: {e}")







    def generate_preview_pixmap(self, hwp_path):
        converter_script = os.path.join(os.path.dirname(__file__), 'hwp_converter_ui.py')
        subprocess.run([sys.executable, converter_script, hwp_path], check=True)
        pdf_path = str(Path(hwp_path).with_suffix('.pdf'))
        if not os.path.exists(pdf_path): raise Exception("PDF 파일이 생성되지 않았습니다.")
        doc = fitz.open(pdf_path)
        if doc.page_count == 0: raise Exception("PDF 파일에 페이지가 없습니다.")
        pix = doc.load_page(0).get_pixmap()
        doc.close()
        return QPixmap.fromImage(QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888))

    def display_preview_image(self, pixmap):
        if pixmap.isNull(): return
        label = QLabel()
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)
        self.ui.pdfViewerArea.setWidgetResizable(True)
        self.ui.pdfViewerArea.setWidget(label)




## 다크모드

    def toggle_theme(self):
        app = QApplication.instance()
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            app.setStyleSheet(dark_stylesheet)
        else:
            app.setStyleSheet(light_stylesheet)

    
if __name__ == "__main__":
    
    light_stylesheet = """
        QMainWindow { background-color: #f5f7fa; }
        QLabel { font-size: 14px; font-weight: 600; color: #000000; }
        QPushButton {
            background-color: #323232; border-radius: 8px; color: white;
            padding: 10px 18px; font-weight: bold; font-size: 13px; border: none;
        }
        QPushButton:hover { background-color: #2980b9; }
        QTextEdit {
            background-color: white; border: 1.5px solid #bdc3c7; border-radius: 6px;
            padding: 8px; font-size: 13px; color: #2c3e50;
        }
        QMenuBar { background-color: #323232; color: white; }
        QMenuBar::item { background-color: transparent; padding: 4px 10px; }
        /* [수정] 메뉴바 호버 색상 변경 */
        QMenuBar::item:selected { background-color: #2a82da; } 
        QMenu { background-color: white; border: 1px solid #dcdcdc; color: #2c3e50; }
        /* [수정] 메뉴 아이템 호버 색상 변경 */
        QMenu::item:selected { background-color: #2a82da; color: white; } 
        QStatusBar { background-color: #ecf0f1; color: #34495e; }

        /* --- 템플릿 위젯 스타일 (라이트 모드) --- */
        QLabel#mainTemplateStatusLabel { font-weight: bold; color: #333; }
        QWidget#templateOverlay { background-color: #f0f0f0; border: 1px solid #BDBDBD; border-radius: 8px; }
        QLabel#statusLabel { color: #333333; font-weight: bold; }
        QScrollArea#templateScrollArea, QScrollArea#templateScrollArea > QWidget > QWidget {
            background: transparent; border: none;
        }
        QFrame#AddressItem { border: 1px solid #cccccc; border-radius: 5px; background-color: white; }
        QFrame#AddressItem:hover { background-color: #f5f5f5; }
        QFrame#AddressItem[selected="true"] { border: 2px solid #0078d7; background-color: #e8f3ff; }
        QFrame#AddressItem QLabel { background: transparent; }
        QFrame#AddressItem QLabel#templateNameLabel { font-size: 14px; font-weight: bold; color: #2c3e50; }
        QFrame#AddressItem QLabel#pageLabel { font-size: 11px; color: #888888; }
        QFrame#AddressItem QPushButton#menuButton {
            color: #555555; border: none; background-color: transparent;
            font-size: 18px; font-weight: bold; padding: 0px; padding-bottom: 4px;
        }
        QFrame#AddressItem QPushButton#menuButton:hover { background-color: #e9e9e9; border-radius: 5px; }
        """
    
    dark_stylesheet = """
        QMainWindow, QDialog { 
            background-color: #2b2b2b; 
            color: #f0f0f0; 
        }
        QLabel { font-size: 14px; font-weight: 600; color: #f0f0f0; }
        QPushButton {
            background-color: #3c3f41;
            color: #f0f0f0;
            border: 1px solid #5c5f61;
            border-radius: 8px;
            padding: 10px 18px;
            font-weight: bold;
            font-size: 13px;
        }
        QPushButton:hover { background-color: #2a82da; }
        QTextEdit {
            background-color: #3c3f41; border: 1.5px solid #5c5f61;
            border-radius: 6px; padding: 8px; font-size: 13px; color: #f0f0f0;
        }
        QCheckBox {
            color: #f0f0f0;
        }
        QMenuBar {
            background-color: #3c3f41;
            color: #f0f0f0;
        }
        /* [추가] 메뉴바 기본 아이템 스타일 (파싱 오류 방지) */
        QMenuBar::item {
            background-color: transparent;
            padding: 4px 10px;
        }
        QMenuBar::item:selected { background-color: #2a82da; }
        QMenu {
            background-color: #2b2b2b;
            color: #f0f0f0;
            border: 1px solid #5c5f61;
        }
        QMenu::item:selected {
            background-color: #2a82da;
            color: #f0f0f0;
        }
        QStatusBar {
            background-color: #3c3f41;
            color: #f0f0f0;
        }

        /* --- 템플릿 위젯 스타일 (다크 모드) --- */
        QLabel#mainTemplateStatusLabel { font-weight: bold; color: #f0f0f0; }
        QWidget#templateOverlay { background-color: #2b2b2b; border: 1px solid #555555; border-radius: 8px; }
        QLabel#statusLabel { color: #f0f0f0; font-weight: bold; }
        QScrollArea#templateScrollArea, QScrollArea#templateScrollArea > QWidget > QWidget {
            background: transparent; border: none;
        }
        QFrame#AddressItem { border: 1px solid #555555; border-radius: 5px; background-color: #3c3f41; }
        QFrame#AddressItem:hover { background-color: #4a4e51; }
        QFrame#AddressItem[selected="true"] { border: 2px solid #63b3ed; background-color: #4a5568; }
        QFrame#AddressItem QLabel { background: transparent; color: #f0f0f0; }
        QFrame#AddressItem QLabel#templateNameLabel { font-size: 14px; font-weight: bold; }
        QFrame#AddressItem QLabel#pageLabel { font-size: 11px; color: #bbbbbb; }
        
        QFrame#AddressItem QPushButton#menuButton {
            background-color: transparent;
            border: none;
            padding: 0px;
            padding-bottom: 4px;
            color: #f0f0f0;
            font-size: 18px;
            font-weight: bold;
        }
        QFrame#AddressItem QPushButton#menuButton:hover { 
            background-color: #4a4e51; 
            border-radius: 5px; 
        }

        /* --- 다이얼로그 및 입력창 스타일 (다크 모드) --- */
        QInputDialog { background-color: #2b2b2b; }
        QInputDialog QLabel { color: #f0f0f0; }
        QInputDialog QLineEdit {
            background-color: #3c3f41; border: 1px solid #5c5f61;
            color: #f0f0f0; border-radius: 4px; padding: 5px;
        }
        QInputDialog QSpinBox {
            background-color: #3c3f41; border: 1px solid #5c5f61;
            color: #f0f0f0; border-radius: 4px; padding: 5px;
        }
        QInputDialog QPushButton {
            background-color: #3c3f41; border: 1px solid #5c5f61;
            color: #f0f0f0; padding: 5px 15px;
            border-radius: 4px; min-width: 60px;
        }
        QInputDialog QPushButton:hover { background-color: #2a82da; }
        """

    app = QApplication(sys.argv)
    app.setStyleSheet(light_stylesheet)
    win = WindowClass()
    win.ui.template_label.setObjectName("mainTemplateStatusLabel")
    win.show()
    sys.exit(app.exec())