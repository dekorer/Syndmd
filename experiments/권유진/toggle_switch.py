from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QCheckBox
from PySide6.QtGui import QCursor

class ToggleSwitch(QCheckBox):
    """
    QCheckBox를 스타일링하여 만든 커스텀 토글 스위치 위젯입니다.
    """
    def __init__(
        self,
        parent=None,
        width=50,
        height=24,
        track_color="#ccc",
        handle_color="#fff",
        checked_color="#2a82da"
    ):
        super().__init__(parent)
        self._width = width
        self._height = height
        
        # 커서 모양을 손가락 모양으로 변경하여 클릭 가능함을 표시
        self.setCursor(QCursor(Qt.PointingHandCursor))

        # 핸들(동그라미)의 크기와 위치 계산
        handle_size = height - 6  # 위아래 여백 3px씩
        handle_unchecked_pos = 3  # 왼쪽 여백
        handle_checked_pos = width - handle_size - 3 # 오른쪽 여백
        
        # QSS (CSS와 유사)를 사용하여 스타일 정의
        style_sheet = f"""
            QCheckBox {{
                background-color: {track_color};
                border: none;
                border-radius: {height // 2}px;
                width: {width}px;
                height: {height}px;
            }}
            QCheckBox:checked {{
                background-color: {checked_color};
            }}
            QCheckBox::indicator {{
                subcontrol-position: left;
                width: {handle_size}px;
                height: {handle_size}px;
                border-radius: {handle_size // 2}px;
                background-color: {handle_color};
                left: {handle_unchecked_pos}px;
            }}
            QCheckBox::indicator:checked {{
                left: {handle_checked_pos}px;
            }}
        """
        self.setStyleSheet(style_sheet)

    def sizeHint(self):
        # 레이아웃에 배치될 때 적절한 크기를 반환하도록 함
        return QSize(self._width, self._height)