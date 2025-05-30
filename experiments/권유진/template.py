from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QScrollArea, QMessageBox, QFrame, QSizePolicy, QFileDialog
)
from PySide6.QtCore import Signal, Qt
import shutil
import sys
import os
import json

class AddressItem(QFrame):
    clicked = Signal(str)
    edited = Signal(str, str)
    removed = Signal(str)

    def __init__(self, text: str, value: str):
        super().__init__()
        self._text = text
        self._selected = False
        self.setFixedHeight(80)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.display_text = os.path.splitext(text)[0]
        self.value = value
        self.editing = False

        self.setObjectName("AddressItem")
        self.setMouseTracking(True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.label = QLabel(self.display_text)
        layout.addWidget(self.label)

        self.btn_edit = QPushButton("이름 수정")
        self.btn_delete = QPushButton("삭제")
        layout.addWidget(self.btn_edit)
        layout.addWidget(self.btn_delete)

        self.btn_edit.clicked.connect(self.start_edit)
        self.btn_delete.clicked.connect(self.confirm_delete)

        self.setStyleSheet("""
        QFrame#AddressItem {
            border: 2px solid black;
            border-radius: 5px;
            background-color: white;
        }
        QFrame#AddressItem:hover {
            background-color: #f0f0f0;
        }
        """)

    def mousePressEvent(self, event):
        self.clicked.emit(self._text)

    def set_selected(self, selected: bool):
        self._selected = selected
        self.update_style()

    def update_style(self):
        if self._selected:
            self.setStyleSheet("""
            QFrame#AddressItem {
                border: 3px solid blue;
                border-radius: 5px;
                background-color: #eef;
            }
            QFrame#AddressItem:hover {
                background-color: #e0f0ff;
            }
            """)
        else:
            self.setStyleSheet("""
            QFrame#AddressItem {
                border: 2px solid black;
                border-radius: 5px;
                background-color: white;
            }
            QFrame#AddressItem:hover {
                background-color: #f0f0f0;
            }
            """)

    def start_edit(self):
        if self.editing:
            return
        self.editing = True

        self.edit = QLineEdit(self._text, self)
        base_text = self._text[:-4] if self._text.endswith('.hwp') else self._text
        self.edit.setText(base_text)

        self.layout().insertWidget(0, self.edit)
        self.label.hide()
        self.edit.setFocus()

        self.edit.returnPressed.connect(self.save_edit)
        self.edit.editingFinished.connect(self.save_edit)

    def save_edit(self):
        if not self.editing:
            return

        new_text = self.edit.text().strip()
        if new_text and new_text != self._text:
            old_text = self._text
            old_value = self.value

            folder, old_filename = os.path.split(old_value)
            _, ext = os.path.splitext(old_filename)
            new_filename = new_text + ext
            new_value = os.path.join(folder, new_filename)

            if os.path.exists(new_value):
                QMessageBox.warning(
                self,
                "파일 이름 중복",
                f"'{new_filename}'이라는 이름의 파일이 이미 존재합니다.\n"
                "다른 이름을 입력해 주세요.")
                self.edit.setFocus()
                return

            try:
                os.rename(old_value, new_value)
                self.value = new_value
            except Exception as e:
                QMessageBox.warning(self, "파일 이름 변경 오류", f"파일 이름을 변경할 수 없습니다.\n\n"
                f"오류 내용: {str(e)}")
                self.edit.deleteLater()
                self.label.show()
                self.editing = False
                return

            self._text = new_text
            self.label.setText(new_text)
            self.edited.emit(old_text, new_text)

        self.edit.deleteLater()
        self.label.show()
        self.editing = False

    def confirm_delete(self):
        result = QMessageBox.question(self, "삭제 확인", f"'{self._text}' 을 삭제하시겠습니까?",
                                      QMessageBox.Yes | QMessageBox.No)
        if result == QMessageBox.Yes:
            if os.path.exists(self.value):
                os.remove(self.value)
            self.removed.emit(self._text)
            self.removed.emit(self.value)


class AddressManagerWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.address_content = QWidget()
        self.address_layout = QVBoxLayout(self.address_content)
        self.address_layout.setContentsMargins(10, 10, 10, 10)
        self.address_layout.setSpacing(10)
        self.address_content.setLayout(self.address_layout)

        self.scroll_area.setWidget(self.address_content)
        self.layout.addWidget(self.scroll_area)

        self.btn_add = QPushButton("새 템플릿 추가하기")
        self.label_status = QLabel("현재 선택된 템플릿이 없습니다.")
        self.label_status.setStyleSheet("color: blue;")

        self.layout.addWidget(self.btn_add)
        self.layout.addWidget(self.label_status)

        self.btn_add.clicked.connect(self.add_address)
        self.address_items = []
        self.selected_item = None

        # JSON 저장 파일 경로
        self.json_path = os.path.join(os.getcwd(), "addresses.json")

        #저장된 주소 정보 불러오기
        self.load_addresses()

    def add_address(self):
        source_file, _ = QFileDialog.getOpenFileName(self, "파일 열기", "", "Text Files (*.hwp);;All Files (*)")
        if not source_file:
            return

        if not source_file.endswith(".hwp"):
            QMessageBox.warning(self, "잘못된 파일", ".hwp 파일만 템플릿으로 지정할 수 있습니다.")
            return

        target_folder = os.path.join(os.getcwd(), "template")
        os.makedirs(target_folder, exist_ok=True)

        new_file_name = f"템플릿{len(self.address_items) + 1}.hwp"
        destination_path = os.path.join(target_folder, new_file_name)

        try:
            shutil.copy(source_file, destination_path)
            QMessageBox.information(self, "성공", f"{new_file_name}로 저장되었습니다:\n{destination_path}")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"파일 복사 중 오류 발생:\n{str(e)}")
            return

        self.add_address_item(new_file_name, destination_path)
        self.save_addresses()  # JSON 저장

    def add_address_item(self, text, value):
        item = AddressItem(text, value)
        item.clicked.connect(self.select_address)
        item.edited.connect(self.update_address)
        item.removed.connect(self.remove_address)

        self.address_items.append(item)
        self.address_layout.addWidget(item)

    def select_address(self, text):
        for item in self.address_items:
            is_selected = item._text == text
            item.set_selected(is_selected)
            if is_selected:
                self.selected_item = item
                display_text = item._text[:-4] if item._text.endswith('.hwp') else item._text
                self.label_status.setText(f"현재 선택된 템플릿은 {display_text}입니다.")
                print(self.selected_item.value)

    def update_address(self, old_text, new_text):
        for item in self.address_items:
            if item._text == new_text:
                if self.selected_item and self.selected_item._text == old_text:
                    self.selected_item = item
                    self.label_status.setText(f"현재 선택된 템플릿은 {new_text}입니다.")
                break
        self.save_addresses()  # JSON 저장

    def remove_address(self, text_or_path):
        for item in self.address_items:
            if item._text == text_or_path or item.value == text_or_path:
                self.address_layout.removeWidget(item)
                item.deleteLater()
                self.address_items.remove(item)
                break

        if self.selected_item and (self.selected_item._text == text_or_path or self.selected_item.value == text_or_path):
            self.label_status.setText("현재 선택된 템플릿은 없습니다.")
            self.selected_item = None

        self.save_addresses()  # JSON 저장

    def save_addresses(self):
        #JSON 저장
        data = [{"text": item._text, "value": item.value} for item in self.address_items]
        try:
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "저장 오류", f"주소 정보를 저장할 수 없습니다:\n{str(e)}")

    def load_addresses(self):
        #JSON 로드
        if not os.path.exists(self.json_path):
            return

        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for entry in data:
                    self.add_address_item(entry["text"], entry["value"])
        except Exception as e:
            QMessageBox.warning(self, "불러오기 오류", f"주소 정보를 불러올 수 없습니다:\n{str(e)}")