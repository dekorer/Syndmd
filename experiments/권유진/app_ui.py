# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'app.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QMainWindow,
    QMenu, QMenuBar, QPushButton, QSizePolicy,
    QStatusBar, QTabWidget, QTextEdit, QToolBar,
    QWidget)

from zoomabletextedit import ZoomableTextEdit

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(913, 647)
        self.action_open = QAction(MainWindow)
        self.action_open.setObjectName(u"action_open")
        self.action_copy = QAction(MainWindow)
        self.action_copy.setObjectName(u"action_copy")
        self.action_find = QAction(MainWindow)
        self.action_find.setObjectName(u"action_find")
        self.action_save = QAction(MainWindow)
        self.action_save.setObjectName(u"action_save")
        self.action_1 = QAction(MainWindow)
        self.action_1.setObjectName(u"action_1")
        self.action_2 = QAction(MainWindow)
        self.action_2.setObjectName(u"action_2")
        self.action_3 = QAction(MainWindow)
        self.action_3.setObjectName(u"action_3")
        self.action_5 = QAction(MainWindow)
        self.action_5.setObjectName(u"action_5")
        self.action_8 = QAction(MainWindow)
        self.action_8.setObjectName(u"action_8")
        self.action_close = QAction(MainWindow)
        self.action_close.setObjectName(u"action_close")
        self.action_zoom_in = QAction(MainWindow)
        self.action_zoom_in.setObjectName(u"action_zoom_in")
        self.action_zoom_out = QAction(MainWindow)
        self.action_zoom_out.setObjectName(u"action_zoom_out")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        self.label.setFont(font)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.gridLayout_2 = QGridLayout(self.tab)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.textEdit_2 = QTextEdit(self.tab)
        self.textEdit_2.setObjectName(u"textEdit_2")

        self.gridLayout_2.addWidget(self.textEdit_2, 1, 1, 1, 1)

        self.pushButton = QPushButton(self.tab)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.gridLayout_2.addWidget(self.pushButton, 2, 1, 1, 1)

        self.textEdit = ZoomableTextEdit(self.tab)
        self.textEdit.setObjectName(u"textEdit")

        self.gridLayout_2.addWidget(self.textEdit, 1, 0, 1, 1)

        self.pushButton_open = QPushButton(self.tab)
        self.pushButton_open.setObjectName(u"pushButton_open")
        self.pushButton_open.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.gridLayout_2.addWidget(self.pushButton_open, 2, 0, 1, 1)

        self.label_2 = QLabel(self.tab)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)

        self.label_3 = QLabel(self.tab)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 0, 1, 1, 1)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.textEdit_3 = QTextEdit(self.tab_2)
        self.textEdit_3.setObjectName(u"textEdit_3")
        self.textEdit_3.setGeometry(QRect(0, 0, 891, 441))
        self.tabWidget.addTab(self.tab_2, "")

        self.gridLayout.addWidget(self.tabWidget, 1, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 913, 22))
        self.menu_F = QMenu(self.menubar)
        self.menu_F.setObjectName(u"menu_F")
        self.menu_E = QMenu(self.menubar)
        self.menu_E.setObjectName(u"menu_E")
        self.menu_O = QMenu(self.menubar)
        self.menu_O.setObjectName(u"menu_O")
        self.menu_V = QMenu(self.menubar)
        self.menu_V.setObjectName(u"menu_V")
        self.menu = QMenu(self.menu_V)
        self.menu.setObjectName(u"menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        MainWindow.addToolBar(Qt.ToolBarArea.BottomToolBarArea, self.toolBar)

        self.menubar.addAction(self.menu_F.menuAction())
        self.menubar.addAction(self.menu_E.menuAction())
        self.menubar.addAction(self.menu_O.menuAction())
        self.menubar.addAction(self.menu_V.menuAction())
        self.menu_F.addAction(self.action_open)
        self.menu_F.addAction(self.action_save)
        self.menu_F.addAction(self.action_close)
        self.menu_E.addAction(self.action_copy)
        self.menu_E.addSeparator()
        self.menu_E.addAction(self.action_find)
        self.menu_O.addAction(self.action_1)
        self.menu_O.addAction(self.action_2)
        self.menu_O.addAction(self.action_3)
        self.menu_O.addSeparator()
        self.menu_O.addAction(self.action_5)
        self.menu_V.addAction(self.menu.menuAction())
        self.menu_V.addSeparator()
        self.menu_V.addAction(self.action_8)
        self.menu.addAction(self.action_zoom_in)
        self.menu.addAction(self.action_zoom_out)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.action_open.setText(QCoreApplication.translate("MainWindow", u"\uc5f4\uae30(O)", None))
#if QT_CONFIG(shortcut)
        self.action_open.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.action_copy.setText(QCoreApplication.translate("MainWindow", u"\ubcf5\uc0ac(C)", None))
#if QT_CONFIG(shortcut)
        self.action_copy.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+C", None))
#endif // QT_CONFIG(shortcut)
        self.action_find.setText(QCoreApplication.translate("MainWindow", u"\ucc3e\uae30(F)", None))
#if QT_CONFIG(shortcut)
        self.action_find.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+F", None))
#endif // QT_CONFIG(shortcut)
        self.action_save.setText(QCoreApplication.translate("MainWindow", u"\ud30c\uc77c \uc800\uc7a5(S)", None))
#if QT_CONFIG(shortcut)
        self.action_save.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+S", None))
#endif // QT_CONFIG(shortcut)
        self.action_1.setText(QCoreApplication.translate("MainWindow", u"\uc0ac\uc6a9\uc790 \uc11c\uc2dd 1", None))
        self.action_2.setText(QCoreApplication.translate("MainWindow", u"\uc0ac\uc6a9\uc790 \uc11c\uc2dd 2", None))
        self.action_3.setText(QCoreApplication.translate("MainWindow", u"\uc0ac\uc6a9\uc790 \uc11c\uc2dd 3", None))
        self.action_5.setText(QCoreApplication.translate("MainWindow", u"\uc0ac\uc6a9\uc790 \uc11c\uc2dd \ucd94\uac00...", None))
        self.action_8.setText(QCoreApplication.translate("MainWindow", u"\ubc1d\uac8c/\uc5b4\ub461\uac8c", None))
        self.action_close.setText(QCoreApplication.translate("MainWindow", u"\ub05d\ub0b4\uae30(X)", None))
#if QT_CONFIG(shortcut)
        self.action_close.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+X", None))
#endif // QT_CONFIG(shortcut)
        self.action_zoom_in.setText(QCoreApplication.translate("MainWindow", u"\ud655\ub300\ud558\uae30", None))
#if QT_CONFIG(shortcut)
        self.action_zoom_in.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+=", None))
#endif // QT_CONFIG(shortcut)
        self.action_zoom_out.setText(QCoreApplication.translate("MainWindow", u"\ucd95\uc18c\ud558\uae30", None))
#if QT_CONFIG(shortcut)
        self.action_zoom_out.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+-", None))
#endif // QT_CONFIG(shortcut)
        self.label.setText(QCoreApplication.translate("MainWindow", u"MDTOHWP", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"\ubcc0\ud658\ud558\uae30", None))
        self.pushButton_open.setText(QCoreApplication.translate("MainWindow", u"MD \ud30c\uc77c \uc5c5\ub85c\ub4dc", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Markdown \uc785\ub825", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"HWP \ubbf8\ub9ac\ubcf4\uae30", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"\ubcc0\ud658", None))
        self.textEdit_3.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'\ub9d1\uc740 \uace0\ub515'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\uc0ac\uc6a9\uc790\uc9c0\uc815\uc11c\uc2dd\ubcf4\uae30</p></body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"\ud15c\ud50c\ub9bf \uc124\uc815", None))
        self.menu_F.setTitle(QCoreApplication.translate("MainWindow", u"\ud30c\uc77c(F)", None))
        self.menu_E.setTitle(QCoreApplication.translate("MainWindow", u"\ud3b8\uc9d1(E)", None))
        self.menu_O.setTitle(QCoreApplication.translate("MainWindow", u"\uc11c\uc2dd(O)", None))
        self.menu_V.setTitle(QCoreApplication.translate("MainWindow", u"\ubcf4\uae30(V)", None))
        self.menu.setTitle(QCoreApplication.translate("MainWindow", u"\ud655\ub300\ud558\uae30/\ucd95\uc18c\ud558\uae30", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

