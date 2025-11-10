from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QScrollArea, QMessageBox, QFrame, QSizePolicy, QFileDialog,
    QGridLayout, QInputDialog, QSpacerItem, QMenu
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Signal, Qt, QPoint
import shutil
import sys
import os
import json

class AddressItem(QFrame):
    clicked = Signal(str)
    edited = Signal(str, str)
    removed = Signal(str)
    page_changed = Signal()

    def __init__(self, text: str, value: str, page: int = 0):
        super().__init__()
        self._text = text
        self._value = value
        self._page = page
        self._selected = False
        self.setMinimumHeight(60)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.display_text = os.path.splitext(text)[0]
        self.setObjectName("AddressItem")
        self.setMouseTracking(True)
        self.setProperty("selected", self._selected)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 10, 10, 10)
        main_layout.setSpacing(10)

        self.info_layout = QVBoxLayout()
        self.info_layout.setSpacing(2)
        
        self.label = QLabel(self.display_text)
        self.label.setObjectName("templateNameLabel")
        
        self.page_label = QLabel(f"템플릿 시작 페이지: {self._page}")
        self.page_label.setObjectName("pageLabel")

        self.info_layout.addWidget(self.label)
        self.info_layout.addWidget(self.page_label)
        self.info_layout.addStretch()

        main_layout.addLayout(self.info_layout)
        main_layout.addStretch()

        self.menu_button = QPushButton("⋮")
        self.menu_button.setFixedSize(25, 25)
        self.menu_button.setObjectName("menuButton")
        self.menu_button.clicked.connect(self.show_menu)
        main_layout.addWidget(self.menu_button)
        
        self.menu = QMenu(self)
        edit_action = QAction("이름 수정", self)
        edit_action.triggered.connect(self.start_edit)
        page_action = QAction("페이지 지정", self)
        page_action.triggered.connect(self.set_page)
        self.menu.addSeparator()
        delete_action = QAction("삭제", self)
        delete_action.triggered.connect(self.confirm_delete)
        self.menu.addAction(edit_action)
        self.menu.addAction(page_action)
        self.menu.addAction(delete_action)

    def show_menu(self):
        point = self.menu_button.mapToGlobal(QPoint(0, self.menu_button.height()))
        self.menu.exec(point)

    @property
    def value(self): return self._value
    @value.setter
    def value(self, new_value): self._value = new_value
        
    def set_page(self):
        page_num, ok = QInputDialog.getInt(self, "페이지 지정", "페이지를 입력하세요:", self._page, 0)
        if ok and page_num != self._page:
            self._page = page_num
            self.page_label.setText(f"템플릿 시작 페이지: {self._page}")
            self.page_changed.emit()

    def mousePressEvent(self, event):
        if not self.menu_button.geometry().contains(event.pos()):
            self.clicked.emit(self._text)

    def set_selected(self, selected: bool):
        self._selected = selected
        self.update_style()

    def update_style(self):
        self.setProperty("selected", self._selected)
        self.style().unpolish(self)
        self.style().polish(self)

    def start_edit(self):
        current_base_name = self.display_text
        new_base_name, ok = QInputDialog.getText(
            self, "이름 수정", "새 템플릿 이름을 입력하세요:", QLineEdit.Normal, current_base_name
        )
        if ok and new_base_name and new_base_name != current_base_name:
            old_text = self._text
            old_value = self.value
            _, ext = os.path.splitext(self._text)
            new_text = new_base_name.strip() + ext
            folder = os.path.dirname(old_value)
            new_value = os.path.join(folder, new_text)
            if os.path.exists(new_value):
                QMessageBox.warning(self, "파일 이름 중복", f"'{new_base_name}'이라는 이름의 파일이 이미 존재합니다.")
                return
            try:
                os.rename(old_value, new_value)
            except Exception as e:
                QMessageBox.warning(self, "파일 이름 변경 오류", f"파일 이름을 변경할 수 없습니다:\n{e}")
                return
            self._text = new_text
            self.value = new_value
            self.display_text = new_base_name.strip()
            self.label.setText(self.display_text)
            self.edited.emit(old_text, self._text)

    def confirm_delete(self):
        msgBox = QMessageBox(self)
        msgBox.setWindowTitle('삭제 확인')
        msgBox.setText(f"'{self.display_text}' 템플릿을 정말 삭제하시겠습니까?")
        msgBox.setIcon(QMessageBox.Question)
        yes_button = msgBox.addButton("예(&Y)", QMessageBox.YesRole)
        no_button = msgBox.addButton("아니오(&N)", QMessageBox.NoRole)
        msgBox.setDefaultButton(no_button)
        msgBox.exec()

        if msgBox.clickedButton() == yes_button:
            if os.path.exists(self.value):
                try: os.remove(self.value)
                except OSError as e: QMessageBox.warning(self, "파일 삭제 오류", f"파일을 삭제할 수 없습니다:\n{e}")
            self.removed.emit(self._text)


class AddressManagerWidget(QWidget):
    status_changed = Signal(str)
    # [추가] 파일 경로(str)와 페이지 번호(int)를 전달할 새 시그널 정의
    template_selected = Signal(str, int)

    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.grid_columns = 2
        self.layout = QVBoxLayout(self)
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("templateScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.address_content = QWidget()
        self.address_layout = QGridLayout(self.address_content)
        self.address_layout.setContentsMargins(10, 10, 10, 10)
        self.address_layout.setSpacing(10)
        self.address_content.setLayout(self.address_layout)
        self.btn_clear_selection = QPushButton("선택 취소")
        self.btn_clear_selection.setFixedSize(100, 35)
        self.btn_clear_selection.clicked.connect(self.clear_selection)
        top_button_layout = QHBoxLayout()
        top_button_layout.addStretch()
        top_button_layout.addWidget(self.btn_clear_selection)
        self.layout.addLayout(top_button_layout)
        self.scroll_area.setWidget(self.address_content)
        self.layout.addWidget(self.scroll_area)
        self.btn_add = QPushButton("새 템플릿 추가하기")
        self.label_status = QLabel("현재 선택된 템플릿이 없습니다.")
        self.label_status.setObjectName("statusLabel")

        self.layout.addWidget(self.btn_add)
        self.layout.addWidget(self.label_status)
        self.btn_add.clicked.connect(self.add_address)
        self.address_items = []
        self.selected_item = None
        self.json_path = os.path.join(os.getcwd(), "addresses.json")
        self.load_addresses()

    def add_address(self):
        source_file, _ = QFileDialog.getOpenFileName(self, "파일 열기", "", "Hangul Word Processor Files (*.hwp);;All Files (*)")
        if not source_file: return
        if not source_file.lower().endswith(".hwp"):
            QMessageBox.warning(self, "잘못된 파일", ".hwp 파일만 템플릿으로 지정할 수 있습니다.")
            return
        target_folder = os.path.join(os.getcwd(), "template")
        os.makedirs(target_folder, exist_ok=True)
        base_name = os.path.basename(source_file)
        new_file_name = base_name
        count = 1
        while os.path.exists(os.path.join(target_folder, new_file_name)):
            name, ext = os.path.splitext(base_name)
            new_file_name = f"{name}_{count}{ext}"
            count += 1
        destination_path = os.path.join(target_folder, new_file_name)
        try:
            shutil.copy(source_file, destination_path)
            display_name = os.path.splitext(new_file_name)[0]
            QMessageBox.information(self, "저장 성공", f"'{display_name}'(으)로 저장되었습니다.")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"파일 복사 중 오류 발생:\n{e}")
            return
        self.add_address_item(new_file_name, destination_path, page=0)
        self.save_addresses()


    def add_address_item(self, text, value, page=0):
        item = AddressItem(text, value, page)
        item.clicked.connect(self.select_address)
        item.edited.connect(self.update_address)
        item.removed.connect(self.remove_address)
        item.page_changed.connect(self.save_addresses)
        self.address_items.append(item)
        self._redraw_grid()


    def _redraw_grid(self):
        while self.address_layout.count():
            child = self.address_layout.takeAt(0)
            if child.widget(): child.widget().setParent(None)
        for i, item in enumerate(self.address_items):
            row = i // self.grid_columns
            col = i % self.grid_columns
            self.address_layout.addWidget(item, row, col)
        last_row = (len(self.address_items) - 1) // self.grid_columns
        self.address_layout.setRowStretch(last_row + 1, 1)


    def select_address(self, text):
        for item in self.address_items:
            is_selected = item._text == text
            item.set_selected(is_selected)
            
            if is_selected:
                self.selected_item = item
                self.label_status.setText(f"현재 선택된 템플릿은 '{item.display_text}' 입니다.")
                self.status_changed.emit(item.display_text)

                # [수정] 파일 존재 여부 확인 후 데이터 전송
                if os.path.exists(self.selected_item.value):
                    # 파일이 존재할 때만 경로와 페이지 정보를 담아 시그널을 보냄
                    self.template_selected.emit(self.selected_item.value, self.selected_item._page)
                else:
                    QMessageBox.warning(self, "존재하지 않는 파일", "선택한 템플릿 파일이 존재하지 않습니다.")
                    msgBox = QMessageBox(self)
                    msgBox.setWindowTitle("존재하지 않는 파일")
                    msgBox.setText("목록에서 이 템플릿을 삭제하시겠습니까?")
                    msgBox.setIcon(QMessageBox.Question)
                    yes_button = msgBox.addButton("예(&Y)", QMessageBox.YesRole)
                    no_button = msgBox.addButton("아니오(&N)", QMessageBox.NoRole)
                    msgBox.setDefaultButton(no_button)
                    msgBox.exec()
                    if msgBox.clickedButton() == yes_button:
                        self.remove_address(self.selected_item._text)
                    self.clear_selection()

                

    def clear_selection(self):
        if self.selected_item: self.selected_item.set_selected(False)
        self.selected_item = None
        self.label_status.setText("현재 선택된 템플릿이 없습니다.")
        self.status_changed.emit("")
        # [수정] 선택 해제 시 빈 데이터를 담아 시그널을 보냄
        self.template_selected.emit("", 0)


    def update_address(self, old_text, new_text):
        found_item = next((item for item in self.address_items if item._text == new_text), None)
        if found_item and self.selected_item and self.selected_item._text == new_text:
            self.label_status.setText(f"현재 선택된 템플릿은 '{found_item.display_text}' 입니다.")
            self.status_changed.emit(found_item.display_text)
        self.save_addresses()


    def remove_address(self, text_or_path):
        item_to_remove = next((item for item in self.address_items if item._text == text_or_path or item.value == text_or_path), None)
        if not item_to_remove: return
        if self.selected_item == item_to_remove: self.clear_selection()
        self.address_items.remove(item_to_remove)
        item_to_remove.deleteLater()
        self._redraw_grid()
        self.save_addresses()


    def save_addresses(self):
        data = [{"text": item._text, "value": item.value, "page": item._page} for item in self.address_items]
        try:
            with open(self.json_path, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "저장 오류", f"주소 정보를 저장할 수 없습니다:\n{e}")


    def load_addresses(self):
        if not os.path.exists(self.json_path): return
        try:
            with open(self.json_path, "r", encoding="utf-8") as f: data = json.load(f)
            for item in self.address_items: item.deleteLater()
            self.address_items.clear()
            for entry in data:
                page = entry.get("page", 0)
                self.add_address_item(entry["text"], entry["value"], page)
        except Exception as e:
            QMessageBox.warning(self, "불러오기 오류", f"주소 정보를 불러올 수 없습니다:\n{e}")