from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal, Qt

class OverlayWidget(QWidget):
    """
    QStackedWidget에 표시될 커스텀 위젯.
    '뒤로 가기' 버튼을 누르면 back_requested 시그널을 발생시킨다.
    """
    # 사용자 정의 시그널 생성. 이 시그널은 메인 윈도우에서 감지하여 처리합니다.
    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # UI 구성
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)

        self.label = QLabel("여기는 별도 파일에서 로드된 오버레이 위젯입니다.")
        self.label.setStyleSheet("font-size: 18px; color: #333;")

        self.back_button = QPushButton("메인 화면으로 돌아가기")
        self.back_button.setFixedSize(200, 40)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.back_button)

        # '뒤로 가기' 버튼 클릭 시 back_requested 시그널을 발생(emit)시킴
        self.back_button.clicked.connect(self.back_requested.emit)