
from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QWheelEvent
from PySide6.QtCore import Qt
##마우스휠로 텍스트 확대/축소
class ZoomableTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.zoom_step = 1
        self.min_size = 6
        self.max_size = 40

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() == Qt.ControlModifier:
            delta = event.angleDelta().y()
            font = self.font()
            size = font.pointSize()
            if delta > 0:
                size = min(self.max_size, size + self.zoom_step)
            else:
                size = max(self.min_size, size - self.zoom_step)
            font.setPointSize(size)
            self.setFont(font)
            event.accept()
        else:
            super().wheelEvent(event)
