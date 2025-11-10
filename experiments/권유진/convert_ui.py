import sys ,tempfile, os, fitz, subprocess, time, pyperclip
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDialog, QMessageBox,  QSystemTrayIcon, QMenu
from PySide6.QtCore import Qt, QRegularExpression, Signal , QObject, QTimer, QThread, QEvent, QSettings
from PySide6.QtGui import QTextCursor, QPixmap, QImage, QIcon, QAction

from loading_preview import Ui_Form
from app_ui import Ui_MainWindow
from find import Ui_Dialog
from template import AddressManagerWidget
from pathlib import Path
from toggle_switch import ToggleSwitch


## 로딩창
class Worker(QObject):
    # --- [수정 1] 신호(Signal)가 정수(int)와 문자열(str)을 함께 보내도록 변경
    progress = Signal(int, str)
    # --- [수정 2] 완료 신호도 작업 결과(경로, 오류)를 모두 포함하도록 통일
    finished = Signal(str, Exception) # final_path, error
    preview_ready = Signal(list, str, Exception)

    def __init__(self, main_window, text_content, mode='convert', save_path=''):
        super().__init__()
        self.main_window = main_window
        self.text_content = text_content
        self.mode = mode  # 'convert' 또는 'preview'
        self.save_path = save_path
        self.temp_hwp_path = ""

    def run(self):
        final_path = self.save_path
        try:
            # --- 1. HWP 파일 생성 (공통 과정) ---
            self.progress.emit(0, "작업을 준비합니다...")
            
            # 미리보기 모드일 경우 임시 파일 경로를 사용
            if self.mode == 'preview':
                self.temp_hwp_path = os.path.join(tempfile.gettempdir(), f"preview_{int(time.time())}.hwp")
                final_path = self.temp_hwp_path
            
            if self.mode == 'preview':
                self.progress.emit(10, "HWP로 변환 중입니다...")
            else :
                self.progress.emit(50, "HWP로 변환 중입니다...")
            # run_blank_hwp_generator가 모든 변환 과정을 포함
            self.main_window.run_blank_hwp_generator(
                self.text_content,
                final_path,
                self.main_window.selected_template_path,
                self.main_window.selected_template_page
            )
            if self.mode == 'preview':
                self.progress.emit(50, "HWP가 생성되었습니다.")
            else :
                self.progress.emit(100, "HWP가 생성되었습니다.")

            # --- 2. 모드에 따른 후속 작업 ---
            if self.mode == 'preview':
                self.progress.emit(75, "미리보기용 PDF를 생성 중입니다...")
                pixmap = self.main_window.generate_preview_pixmap(final_path)
                self.progress.emit(95, "미리보기 이미지를 불러오고 있습니다...")
                self.progress.emit(100, "완료")
                self.preview_ready.emit(pixmap, final_path, None)
            else: # 'convert' 모드
                self.progress.emit(100, "완료")
                self.finished.emit(final_path, None)

        except Exception as e:
            if self.mode == 'preview':
                self.preview_ready.emit(QPixmap(), self.temp_hwp_path, e)
            else:
                self.finished.emit(final_path, e)

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

        self.template_selec = AddressManagerWidget()
        self.template_overlay_widget = QWidget(self)
        self.template_overlay_widget.setObjectName("templateOverlay")
        overlay_layout = QVBoxLayout(self.template_overlay_widget)
        overlay_layout.setContentsMargins(8, 8, 8, 8)
        overlay_layout.addWidget(self.template_selec)
        self.template_overlay_widget.hide()

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("icon4.png"))  # 기존 아이콘 사용
        self.tray_icon.setToolTip("MDTOHWP 실행 중")
        self.tray_icon.show()
        
        # 트레이 메뉴
        tray_menu = QMenu()
        open_action = QAction("열기", self)
        quit_action = QAction("종료", self)

        tray_menu.addAction(open_action)
        tray_menu.addAction(quit_action)

        open_action.triggered.connect(self.showNormal)
        quit_action.triggered.connect(QApplication.quit)

        self.tray_icon.setContextMenu(tray_menu)

        # 더블클릭하면 창 복원
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

        self.ui.centralwidget.setAcceptDrops(True)
        self.ui.centralwidget.installEventFilter(self)
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
        self.ui.action_8.setVisible(False)
        self.ui.hwpruncheck.setChecked(True)

     # === [수정] 상태표시줄 레이아웃 재구성 ===
        status_bar_widget = QWidget()
        status_bar_layout = QHBoxLayout(status_bar_widget)
        status_bar_layout.setContentsMargins(10, 0, 10, 0)

        # 1. 테마 설정 위젯 (왼쪽)
        theme_widget = QWidget()
        theme_layout = QHBoxLayout(theme_widget)
        theme_layout.setContentsMargins(0, 0, 0, 0)
        theme_layout.setSpacing(8)

        self.dark_mode_label = QLabel("다크 모드")
        self.dark_mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.theme_switch = ToggleSwitch(checked_color="#3c75aa")
        self.theme_switch.toggled.connect(self.toggle_theme)
        # [수정] 라이트 모드 라벨 추가 코드 삭제
        theme_layout.addWidget(self.theme_switch)
        theme_layout.addWidget(self.dark_mode_label)

        # 2. 클립보드 감시 설정 위젯 (오른쪽)
        clipboard_widget = QWidget()
        clipboard_layout = QHBoxLayout(clipboard_widget)
        clipboard_layout.setContentsMargins(0, 0, 0, 0)
        clipboard_layout.setSpacing(8)

        self.clipboard_label = QLabel("클립보드 감시 활성화")
        self.clipboard_switch = ToggleSwitch()
        self.clipboard_switch.toggled.connect(self.toggle_clipboard_monitoring)

        clipboard_layout.addWidget(self.clipboard_label)
        clipboard_layout.addWidget(self.clipboard_switch)

        # 3. 상태표시줄에 위젯들 배치
        status_bar_layout.addWidget(clipboard_widget) # <- 클립보드가 왼쪽으로
        status_bar_layout.addStretch(1)
        status_bar_layout.addWidget(theme_widget)     # <- 테마가 오른쪽으로

        self.ui.statusbar.addWidget(status_bar_widget, 1)
        # ===============================================

        settings = QSettings("MyCompany", "HWPConverter")
        is_dark_mode = settings.value("darkMode", False, type=bool)
        self.theme_switch.setChecked(is_dark_mode)
        self.toggle_theme(is_dark_mode)

        self.last_clipboard_text = ""
        self.clipboard_timer = QTimer(self)
        self.clipboard_timer.setInterval(1000)
        self.clipboard_timer.timeout.connect(self.monitor_clipboard)

        is_clipboard_monitoring = settings.value("clipboardMonitoring", False, type=bool)
        self.clipboard_switch.setChecked(is_clipboard_monitoring)

        self.selected_template_path = ""
        self.selected_template_page = 0
        
        self.loading_widget = QWidget() 
        self.loading_ui = Ui_Form()
        self.loading_ui.setupUi(self.loading_widget)
        self.loading_widget.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowStaysOnTopHint)
        self.loading_widget.setWindowTitle("실행 중... (약간의 시간이 소요됩니다.)")
        self.thread = None
        self.worker = None
        
        self.template_selec.status_changed.connect(self.update_template_label)
        self.template_selec.template_selected.connect(self.on_template_selected)
        
        self.ui.template_label.setText("템플릿이 적용되지 않았습니다.")
        self.ui.template_button.clicked.connect(self.toggle_template_widget)
       

    def toggle_clipboard_monitoring(self, checked):
        settings = QSettings("MyCompany", "HWPConverter")
        settings.setValue("clipboardMonitoring", checked)

        if checked:
            self.last_clipboard_text = pyperclip.paste()
            self.clipboard_timer.start()
        else:
            self.clipboard_timer.stop()

    def monitor_clipboard(self):
        """타이머에 의해 주기적으로 호출되어 클립보드를 확인하는 메서드."""
        try:
            current_text = pyperclip.paste()

            # 클립보드 내용이 비어있지 않고, 이전과 다르며, 마크다운 기호를 포함할 때
            if current_text and current_text != self.last_clipboard_text and "#" in current_text:
                self.last_clipboard_text = current_text
                self.ui.textEdit.setPlainText(current_text)
                self.ui.statusbar.showMessage("클립보드에서 마크다운 텍스트를 붙여넣었습니다.", 3000)
            elif current_text != self.last_clipboard_text:
                # 마크다운이 아니더라도, 변경된 내용은 기억해둬야 중복 체크를 안 함
                self.last_clipboard_text = current_text

        except pyperclip.PyperclipException:
            # 클립보드를 사용할 수 없는 경우 (예: 복사된 내용이 텍스트가 아닐 때)
            self.last_clipboard_text = ""

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.showNormal()
            self.activateWindow()

    def update_progress(self, value, text):
        """Worker가 보낸 진행률(value)과 메시지(text)로 UI를 업데이트하는 슬롯"""
        self.loading_ui.preview_progressBar.setValue(value)
        self.loading_ui.label.setText(text) # 라벨의 텍스트를 업데이트
        QApplication.processEvents()

    def load_file_to_textedit(self, file_path):
        """파일 경로를 받아 textEdit에 내용을 로드하는 헬퍼 함수"""
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.ui.textEdit.setPlainText(f.read())
                print(f"파일 로드 성공: {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "오류", f"파일을 여는 데 실패했습니다:\n{e}")

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
        # [수정] hasattr를 사용하여 self.template_overlay_widget이 존재하는지 먼저 확인
        if hasattr(self, 'template_overlay_widget') and self.template_overlay_widget.isVisible():
            self.update_overlay_geometry()

    def changeEvent(self, event):
        super().changeEvent(event)
        if hasattr(self, 'template_overlay_widget') and event.type() == QEvent.WindowStateChange and self.template_overlay_widget.isVisible():
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
        if self.thread is not None and self.thread.isRunning():
            print("창을 닫기 전, 실행 중인 스레드를 안전하게 종료합니다...")
            self.thread.quit() # 스레드에 종료 요청
            if not self.thread.wait(5000): # 5초간 대기
                print("경고: 스레드가 시간 내에 종료되지 않았습니다.")
                
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("프로그램 종료")
        msg.setText("종료하시겠습니까? 프로그램을 종료하거나 트레이로 보낼 수 있습니다.")
        quit_button = msg.addButton("종료", QMessageBox.YesRole)
        tray_button = msg.addButton("트레이로 최소화", QMessageBox.NoRole)
        cancel_button = msg.addButton("취소", QMessageBox.RejectRole)
        msg.exec()

        clicked = msg.clickedButton()
        if clicked == quit_button:
            event.accept()
            # --- ▼▼▼ [수정] 애플리케이션을 명시적으로 종료하는 코드 추가 ▼▼▼ ---
            QApplication.instance().quit() 
        elif clicked == tray_button:
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "MDTOHWP",
                "프로그램이 트레이에서 계속 실행됩니다.",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            event.ignore()


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



    ## 미리보기 파트

    def on_preview(self):
        """'미리보기': 현재 편집 중인 텍스트를 기반으로 HWP를 임시 생성하여 미리보기를 보여줍니다."""
        if self.thread and self.thread.isRunning():
            QMessageBox.information(self, "알림", "현재 다른 작업이 실행 중입니다. 잠시 후 다시 시도해주세요.")
            return

        text_content = self.ui.textEdit.toPlainText()
        if not text_content.strip():
            QMessageBox.warning(self, "내용 없음", "미리보기할 내용을 먼저 입력해주세요.")
            return

        if not self.selected_template_path or not os.path.exists(self.selected_template_path):
            QMessageBox.warning(self, "템플릿 없음", "미리보기를 생성하려면 먼저 유효한 템플릿을 선택해주세요.")
            return
        
        self.loading_ui.label.setText("미리보기를 생성 중입니다...")
        self.loading_ui.preview_progressBar.setRange(0, 100)
        self.loading_ui.preview_progressBar.setValue(0)
        self.loading_widget.show()

        # --- ▼▼▼ [수정] 중복된 스레드 생성 로직을 하나로 정리 ▼▼▼ ---
        self.thread = QThread()
        self.worker = Worker(self, text_content, mode='preview')
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.preview_ready.connect(self.on_preview_finished) 
        self.worker.progress.connect(self.update_progress)
        
        self.worker.preview_ready.connect(self.thread.quit)
        self.worker.preview_ready.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.thread.start()

    # [수정] 중복된 메서드 정의 중 하나를 삭제함
    def cleanup_temp_files(self, hwp_path):
        """임시 HWP, PDF, TXT 파일을 삭제합니다."""
        try:
            # 임시 HWP 삭제
            if hwp_path and os.path.exists(hwp_path):
                os.remove(hwp_path)
                print(f"임시 파일 삭제: {hwp_path}")
            
            # 임시 PDF 삭제 (HWP와 이름이 같고 확장자만 다름)
            pdf_path = os.path.splitext(hwp_path)[0] + ".pdf"
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
                print(f"임시 파일 삭제: {pdf_path}")
            
            # 텍스트 전달용 임시 TXT 파일도 삭제
            temp_text_path = os.path.join(tempfile.gettempdir(), "content_to_convert.txt")
            if os.path.exists(temp_text_path):
                os.remove(temp_text_path)
                print(f"임시 파일 삭제: {temp_text_path}")

        except (OSError, TypeError) as e:
            print(f"임시 파일 삭제 중 오류 발생: {e}")

    def _cleanup_thread(self):
        """스레드와 워커 변수를 안전하게 정리합니다."""
        print("스레드 정리 작업 수행.")
        self.thread = None
        self.worker = None


    def on_preview_finished(self, pixmaps, temp_hwp_path, error):
        self.loading_widget.close()
        try:
            if error:
                QMessageBox.critical(self, "미리보기 생성 실패", f"오류가 발생했습니다:\n{error}")
                self.display_preview_image([]) # 빈 리스트로 미리보기 영역 초기화
                return

            # 리스트가 비어 있는지 확인
            if not pixmaps:
                 QMessageBox.warning(self, "미리보기 실패", "이미지를 생성할 수 없습니다.")
                 self.display_preview_image([])
                 return

            self.display_preview_image(pixmaps)

        finally:
            if temp_hwp_path:
                self.cleanup_temp_files(temp_hwp_path)
            QTimer.singleShot(10, self._cleanup_thread)



    def on_conversion(self):
        """'HWP로 변환': Worker 스레드를 사용하여 백그라운드에서 변환을 실행합니다."""
        if self.thread and self.thread.isRunning():
            QMessageBox.information(self, "알림", "다른 작업이 실행 중입니다. 잠시 후 다시 시도해주세요.")
            return

        text_content = self.ui.textEdit.toPlainText()
        if not text_content.strip():
            QMessageBox.warning(self, "내용 없음", "변환할 내용을 먼저 입력해주세요.")
            return
        
        if not self.selected_template_path or not os.path.exists(self.selected_template_path):
            QMessageBox.warning(self, "템플릿 없음", "파일을 변환하려면 먼저 유효한 템플릿을 선택해주세요.")
            return
        
        save_path_hwp, _ = QFileDialog.getSaveFileName(self, "HWP로 저장", "", "한글 파일 (*.hwp)")
        if not save_path_hwp:
            return
       
        self.loading_ui.label.setText("HWP 파일로 변환 중입니다...")
        self.loading_ui.preview_progressBar.setRange(0, 100) # 범위를 0-100으로 설정
        self.loading_ui.preview_progressBar.setValue(0)
        self.loading_widget.show()

        self.thread = QThread()
        # --- [핵심] 'convert' 모드와 저장 경로를 지정하여 Worker 생성 ---
        self.worker = Worker(self, text_content, mode='convert', save_path=save_path_hwp)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_conversion_finished)
        self.worker.progress.connect(self.update_progress)
        
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()


    def on_conversion_finished(self, final_path, error):
        self.loading_widget.close()

        if error:
            QMessageBox.critical(self, "변환 오류", f"HWP 파일을 저장하는 중 오류가 발생했습니다:\n{error}")
            QTimer.singleShot(10, self._cleanup_thread)
            return

        QMessageBox.information(self, "변환 완료", f"HWP 파일이 성공적으로 저장되었습니다:\n{final_path}")
        
        if self.ui.hwpruncheck.isChecked():
            file_ready = False
            for _ in range(50):
                if os.path.exists(final_path) and os.path.getsize(final_path) > 0:
                    file_ready = True
                    break
                time.sleep(0.1)
            
            if file_ready:
                try:
                    if sys.platform == "win32":
                        subprocess.Popen(['start', '', final_path], shell=True)
                    elif sys.platform == "darwin": # macOS
                        subprocess.Popen(['open', final_path])
                    else: # linux
                        subprocess.Popen(['xdg-open', final_path])
                    # --- ▲▲▲ [핵심 수정] 여기까지 ▲▲▲ ---
                except Exception as e:
                    QMessageBox.warning(self, "파일 실행 실패", f"파일을 자동으로 여는 데 실패했습니다:\n{e}")
            else:
                QMessageBox.warning(self, "파일 실행 대기 실패", "파일이 시간 내에 생성되지 않아 열 수 없습니다.")

        QTimer.singleShot(10, self._cleanup_thread)

    def run_blank_hwp_generator(self, text_content, output_hwp_path, template_path, template_page):
        ## converter_test에게 인자를 전달
        script_path = os.path.join(os.path.dirname(__file__), 'new0910.py')
        #script_path = os.path.join(os.path.dirname(__file__), 'new0910.py')
        temp_dir = tempfile.gettempdir()
        # 텍스트 내용을 임시 파일에 저장하여 경로를 인자로 전달
        temp_text_path = os.path.join(temp_dir, "content_to_convert.txt")
        with open(temp_text_path, "w", encoding="utf-8") as f:
            f.write(text_content)

        command = [
            sys.executable, 
            script_path, 
            temp_text_path,         # 인자 1: 텍스트 파일 경로
            output_hwp_path,        # 인자 2: 출력 파일 경로
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
            


    def generate_preview_pixmap(self, hwp_path):
        converter_script = os.path.join(os.path.dirname(__file__), 'hwp_converter_ui.py')
        subprocess.run([sys.executable, converter_script, hwp_path], check=True)
        pdf_path = str(Path(hwp_path).with_suffix('.pdf'))
        if not os.path.exists(pdf_path): 
            raise Exception("PDF 파일이 생성되지 않았습니다.")
        
        doc = fitz.open(pdf_path)
        if doc.page_count == 0:
            doc.close()
            raise Exception("PDF 파일에 페이지가 없습니다.")
        
        pixmaps = []
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            qimage = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            pixmaps.append(QPixmap.fromImage(qimage))
        
        doc.close()
        return pixmaps

    # === [수정] QPixmap 리스트를 받아 모든 페이지를 표시하도록 재작성 ===
    def display_preview_image(self, pixmaps):
        # 기존 위젯이 있다면 삭제하여 미리보기 영역 초기화
        if self.ui.pdfViewerArea.widget():
            self.ui.pdfViewerArea.widget().deleteLater()
            self.ui.pdfViewerArea.setWidget(None)

        if not pixmaps:
            return

        # 모든 페이지 라벨을 담을 컨테이너와 레이아웃 생성
        container_widget = QWidget()
        layout = QVBoxLayout(container_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)  # 페이지 사이 간격

        # 리스트의 각 pixmap에 대해 QLabel을 생성하고 레이아웃에 추가
        for pixmap in pixmaps:
            if pixmap.isNull():
                continue
            
            label = QLabel()
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
        
        # 스크롤 영역에 컨테이너 위젯 설정
        self.ui.pdfViewerArea.setWidget(container_widget)





## 다크모드

    def toggle_theme(self, is_checked):
        """
        토글 스위치의 상태에 따라 테마와 라벨의 활성화 상태를 변경하고,
        새로운 상태를 QSettings에 저장합니다.
        """
        app = QApplication.instance()
        self.dark_mode = is_checked

        # --- ▼▼▼ [수정] 현재 테마 상태를 저장하는 코드 추가 ▼▼▼ ---
        settings = QSettings("MyCompany", "HWPConverter")
        settings.setValue("darkMode", self.dark_mode)
        # --- ▲▲▲ [수정] 여기까지 추가 ▲▲▲ ---

        if self.dark_mode:
            app.setStyleSheet(dark_stylesheet)
            self.dark_mode_label.setEnabled(True)
        else:
            app.setStyleSheet(light_stylesheet)
            self.dark_mode_label.setEnabled(False)

    
if __name__ == "__main__":
    
    light_stylesheet = """
        QMainWindow { background-color: #f5f7fa; }
        
        /* === [수정] 텍스트 색상을 #2b2b2b로 변경 === */
        QLabel { font-size: 14px; font-weight: 600; color: #2b2b2b; }
        
        /* === [수정] 버튼 및 메뉴 바 배경색을 #2b2b2b로 변경 === */
        QPushButton {
            background-color: #2b2b2b; /* <-- 색상 변경 */
            border-radius: 8px; 
            color: white;
            padding: 10px 18px; 
            font-weight: bold; 
            font-size: 13px; 
            border: none;
        }
        QPushButton:hover { background-color: #2980b9; }
        
        QTextEdit {
            background-color: white; 
            border: 1.5px solid #bdc3c7; 
            border-radius: 6px;
            padding: 8px; 
            font-size: 13px; 
            color: #2c3e50;
        }
        
        /* === [수정] 메뉴 바 배경색을 #2b2b2b로 변경 === */
        QMenuBar { 
            background-color: #2b2b2b; /* <-- 색상 변경 */
            color: white; 
        }
        QMenuBar::item { background-color: transparent; padding: 4px 10px; }
        QMenuBar::item:selected { background-color: #2a82da; } 
        
        QMenu { background-color: white; border: 1px solid #dcdcdc; color: #2c3e50; }
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

        QWidget#LoadingWidget {
            background-color: #f0f0f0;
        }
        QLabel#loadingLabel {
            color: #2b2b2b;
        }
        QProgressBar#loadingProgressBar {
            border: none;
            background-color: #e0e0e0;
            height: 2px;
        }
        QProgressBar#loadingProgressBar::chunk {
            background-color: #2b2b2b;
        }
        """
    
    dark_stylesheet = """
        QMainWindow, QDialog { 
            background-color: #121212; 
            color: #E0E0E0;
        }
        QLabel { font-size: 14px; font-weight: 600; color: #E0E0E0; }
        
        QPushButton {
            background-color: #3c75aa;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 18px;
            font-weight: bold;
            font-size: 13px;
        }
        QPushButton:hover { 
            background-color: #32618f;
        }

        QTextEdit {
            background-color: #E0E0E0;
            border: 1.5px solid #5c5f61;
            border-radius: 6px; 
            padding: 8px; 
            font-size: 13px; 
            color: #121212;
        }
        QTextEdit QAbstractScrollArea QWidget#qt_scrollarea_viewport {
            background-color: #4a4e51;
        }

        QCheckBox {
            color: #E0E0E0;
        }
        /* === [수정] 메뉴바 배경색을 두 번째 어두운 색(#2b2b2b)으로 설정 === */
        QMenuBar {
            background-color: #2b2b2b;
            color: #E0E0E0;
        }
        QMenuBar::item {
            background-color: transparent;
            padding: 4px 10px;
        }
        QMenuBar::item:selected { background-color: #3c75aa; } 
        QMenu {
            background-color: #121212;
            color: #E0E0E0;
            border: 1px solid #5c5f61;
        }
        QMenu::item:selected {
            background-color: #3c75aa;
            color: white;
        }
        /* === [수정] 상태표시줄 배경색을 두 번째 어두운 색(#2b2b2b)으로 설정 === */
        QStatusBar {
            background-color: #2b2b2b;
            color: #E0E0E0;
        }

        QWidget#templateOverlay { 
            background-color: #121212; 
            border: 1px solid #555555; 
            border-radius: 8px; 
        }

        QScrollArea#templateScrollArea {
            background: #adadad; /* <-- 새로운 배경색 지정 */
            border: none;
        }
        QWidget#scrollAreaWidgetContents {
            background-color: #adadad; /* <-- 새로운 배경색 지정 */
        }

        /* ... (템플릿 위젯 스타일) ... */
        QLabel#mainTemplateStatusLabel { font-weight: bold; color: #E0E0E0; }
        QWidget#templateOverlay { background-color: #121212; border: 1px solid #555555; border-radius: 8px; }
        QLabel#statusLabel { color: #E0E0E0; font-weight: bold; }
        QScrollArea#templateScrollArea, QScrollArea#templateScrollArea > QWidget > QWidget {
            background: transparent; border: none;
        }
        QFrame#AddressItem { border: 1px solid #555555; border-radius: 5px; background-color: #2b2b2b; }
        QFrame#AddressItem:hover { background-color: #4a4e51; }
        QFrame#AddressItem[selected="true"] { border: 2px solid #63b3ed; background-color: #4a5568; }
        QFrame#AddressItem QLabel { background: transparent; color: #E0E0E0; }
        QFrame#AddressItem QLabel#templateNameLabel { font-size: 14px; font-weight: bold; }
        QFrame#AddressItem QLabel#pageLabel { font-size: 11px; color: #bbbbbb; }
        
        QFrame#AddressItem QPushButton#menuButton {
            background-color: transparent; border: none; padding: 0px;
            padding-bottom: 4px; color: #E0E0E0; font-size: 18px; font-weight: bold;
        }
        QFrame#AddressItem QPushButton#menuButton:hover { 
            background-color: #4a4e51; border-radius: 5px; 
        }

        /* ... (다이얼로그 스타일) ... */
        QInputDialog { background-color: #121212; }
        QInputDialog QLabel { color: #E0E0E0; }
        QInputDialog QLineEdit, QInputDialog QSpinBox, QInputDialog QPushButton {
            background-color: #2b2b2b; 
            border: 1px solid #5c5f61;
            color: #E0E0E0; 
            border-radius: 4px; 
            padding: 5px;
        }
        QInputDialog QPushButton {
             padding: 5px 15px;
             min-width: 60px;
        }
        /* === [수정] 다이얼로그 버튼 호버 색상을 #3c75aa로 변경 === */
        QInputDialog QPushButton:hover { background-color: #3c75aa; }

        QWidget#LoadingWidget {
            background-color: #121212;
        }
        QLabel#loadingLabel {
            color: #E0E0E0;
        }
        QProgressBar#loadingProgressBar {
            border: none;
            background-color: #555555;
            height: 2px;
        }
        QProgressBar#loadingProgressBar::chunk {
            background-color: #3c75aa;
        }
        """


    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setStyleSheet(light_stylesheet)
    win = WindowClass()
    win.ui.template_label.setObjectName("mainTemplateStatusLabel")
    win.show()
    sys.exit(app.exec())