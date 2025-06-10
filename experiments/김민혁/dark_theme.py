dark_stylesheet = """

QMainWindow {
    background-color: #2b2b2b;
}
QLabel {
    color: #e0e0e0;
    font-size: 14px;
    font-weight: 600;
}

#label {
    color: #cccccc;
    font-weight: 600;
}
QPushButton {
    background-color: #424242;
    border-radius: 6px;
    color: white;
    padding: 10px 18px;
    font-weight: bold;
    font-size: 13px;    
    border: none;
}
QPushButton:hover {
    background-color: #008ee6;
}
QPushButton:pressed {
    background-color: #005f99;
}

QTextEdit, ZoomableTextEdit {
    background-color: #313335;
    border: 1.5px solid #555555;
    border-radius: 6px; 
    padding: 8px;
    font-size: 13px;
    color: #f0f0f0;
}

QTabWidget::pane {
    border: 1px solid #5c5f61;
    border-radius: 6px;
    background: #2b2b2b;
}
QTabBar::tab {
    background: #3c3f41;
    border: 1px solid #5c5f61;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 4px;
    color: #dddddd;
}
QTabBar::tab:selected {
    background: #2b2b2b;
    color: #ffffff;
    font-weight: bold;
    border-bottom: none;
}

QStatusBar {
    background-color: #2b2b2b;
    color: #aaaaaa;
}

QMenuBar {
    background-color: #3c3f41;
    color: #ffffff;
}
QMenuBar::item {
    background-color: transparent;
    padding: 4px 10px;
}
QMenuBar::item:selected {
    background-color: #505354;
}

QMenu {
    background-color: #2b2b2b;
    color: #ffffff;
    border: 1px solid #5c5f61;
}
QMenu::item:selected {
    background-color: #2a82da;
    color: white;
}

QDialog {
    background-color: #2b2b2b;
    color: white;
}

QLineEdit {
    background-color: #3c3f41;
    color: white;
    border: 1px solid #5c5f61;
    border-radius: 4px;
    padding: 4px 6px;
}

QGroupBox {
    border: 1px solid #5c5f61;
    border-radius: 6px;
    margin-top: 6px;
    color: white;
}

QCheckBox, QRadioButton {
    color: white;
}

/* 스크롤 영역 전체 배경색 */
QScrollArea {
    background-color: #2b2b2b;  /* 바깥 배경 */
    border: none;
}

/* 스크롤 영역 안의 실제 콘텐츠 위젯 */
QScrollArea QWidget {
    background-color: #2b2b2b;  /* 내부 흰 배경 제거 */
    color: #e0e0e0;
}
/* 다크모드 템플릿 버튼 색 지정*/
#btn_edit, #btn_delete {
    background-color: #424242;
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: bold;
    padding: 6px 12px;
}
#btn_edit:hover, #btn_delete:hover {
    background-color: #008ee6;
}
#btn_edit:pressed, #btn_delete:pressed {
    background-color: #005f99;
}


"""
