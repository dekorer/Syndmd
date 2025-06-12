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
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QLabel,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QSizePolicy, QStatusBar, QTabWidget, QToolBar,
    QWidget)

from zoomabletextedit import ZoomableTextEdit
import resource_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(913, 647)
        icon = QIcon()
        icon.addFile(u":/icon/icon.jpg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
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
        self.action_H = QAction(MainWindow)
        self.action_H.setObjectName(u"action_H")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.logo = QLabel(self.centralwidget)
        self.logo.setObjectName(u"logo")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.logo.sizePolicy().hasHeightForWidth())
        self.logo.setSizePolicy(sizePolicy)
        self.logo.setMinimumSize(QSize(100, 100))
        self.logo.setMaximumSize(QSize(16777215, 16777215))
        self.logo.setScaledContents(False)
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.logo, 0, 1, 1, 1)

        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.gridLayout_2 = QGridLayout(self.tab)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.textEdit = ZoomableTextEdit(self.tab)
        self.textEdit.setObjectName(u"textEdit")

        self.gridLayout_2.addWidget(self.textEdit, 2, 0, 1, 2)

        self.template_label = QLabel(self.tab)
        self.template_label.setObjectName(u"template_label")

        self.gridLayout_2.addWidget(self.template_label, 5, 0, 1, 1)

        self.hwpruncheck = QCheckBox(self.tab)
        self.hwpruncheck.setObjectName(u"hwpruncheck")
        self.hwpruncheck.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.gridLayout_2.addWidget(self.hwpruncheck, 5, 1, 1, 1)

        self.pushButton_open = QPushButton(self.tab)
        self.pushButton_open.setObjectName(u"pushButton_open")
        self.pushButton_open.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.gridLayout_2.addWidget(self.pushButton_open, 3, 0, 1, 1)

        self.pushButton = QPushButton(self.tab)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.gridLayout_2.addWidget(self.pushButton, 3, 1, 1, 1)

        self.tabWidget.addTab(self.tab, "")
        self.tab_template = QWidget()
        self.tab_template.setObjectName(u"tab_template")
        self.tabWidget.addTab(self.tab_template, "")

        self.gridLayout.addWidget(self.tabWidget, 1, 1, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 913, 22))
        self.menu_F = QMenu(self.menubar)
        self.menu_F.setObjectName(u"menu_F")
        self.menu_E = QMenu(self.menubar)
        self.menu_E.setObjectName(u"menu_E")
        self.menu_V = QMenu(self.menubar)
        self.menu_V.setObjectName(u"menu_V")
        self.menu = QMenu(self.menu_V)
        self.menu.setObjectName(u"menu")
        self.menu_H = QMenu(self.menubar)
        self.menu_H.setObjectName(u"menu_H")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        MainWindow.addToolBar(Qt.ToolBarArea.BottomToolBarArea, self.toolBar)

        self.menubar.addAction(self.menu_F.menuAction())
        self.menubar.addAction(self.menu_E.menuAction())
        self.menubar.addAction(self.menu_V.menuAction())
        self.menubar.addAction(self.menu_H.menuAction())
        self.menu_F.addAction(self.action_open)
        self.menu_F.addAction(self.action_save)
        self.menu_F.addAction(self.action_close)
        self.menu_E.addAction(self.action_copy)
        self.menu_E.addSeparator()
        self.menu_E.addAction(self.action_find)
        self.menu_V.addAction(self.menu.menuAction())
        self.menu_V.addSeparator()
        self.menu_V.addAction(self.action_8)
        self.menu.addAction(self.action_zoom_in)
        self.menu.addAction(self.action_zoom_out)
        self.menu_H.addAction(self.action_H)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MDTOHWP", None))
        self.action_open.setText(QCoreApplication.translate("MainWindow", u"\uc5f4\uae30(&O)", None))
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
        self.action_save.setText(QCoreApplication.translate("MainWindow", u"\ud30c\uc77c \uc800\uc7a5(&S)", None))
#if QT_CONFIG(shortcut)
        self.action_save.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+S", None))
#endif // QT_CONFIG(shortcut)
        self.action_1.setText(QCoreApplication.translate("MainWindow", u"\uc0ac\uc6a9\uc790 \uc11c\uc2dd 1", None))
        self.action_2.setText(QCoreApplication.translate("MainWindow", u"\uc0ac\uc6a9\uc790 \uc11c\uc2dd 2", None))
        self.action_3.setText(QCoreApplication.translate("MainWindow", u"\uc0ac\uc6a9\uc790 \uc11c\uc2dd 3", None))
        self.action_5.setText(QCoreApplication.translate("MainWindow", u"\uc0ac\uc6a9\uc790 \uc11c\uc2dd \ucd94\uac00...", None))
        self.action_8.setText(QCoreApplication.translate("MainWindow", u"\ubc1d\uac8c/\uc5b4\ub461\uac8c", None))
        self.action_close.setText(QCoreApplication.translate("MainWindow", u"\ub05d\ub0b4\uae30(&X)", None))
#if QT_CONFIG(shortcut)
        self.action_close.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+X", None))
#endif // QT_CONFIG(shortcut)
        self.action_zoom_in.setText(QCoreApplication.translate("MainWindow", u"\ud655\ub300\ud558\uae30(&i)", None))
#if QT_CONFIG(shortcut)
        self.action_zoom_in.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+=", None))
#endif // QT_CONFIG(shortcut)
        self.action_zoom_out.setText(QCoreApplication.translate("MainWindow", u"\ucd95\uc18c\ud558\uae30(&O)", None))
#if QT_CONFIG(shortcut)
        self.action_zoom_out.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+-", None))
#endif // QT_CONFIG(shortcut)
        self.action_H.setText(QCoreApplication.translate("MainWindow", u"\ub3c4\uc6c0\ub9d0 \ubcf4\uae30(&H)", None))
        self.template_label.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.hwpruncheck.setText(QCoreApplication.translate("MainWindow", u"\ubcc0\ud658\ub41c \ud55c\uae00\ud30c\uc77c \uc2e4\ud589\ud558\uae30(&R)", None))
        self.pushButton_open.setText(QCoreApplication.translate("MainWindow", u"MD \ud30c\uc77c \uc5c5\ub85c\ub4dc", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"\ubcc0\ud658\ud558\uae30", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"\ubcc0\ud658", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_template), QCoreApplication.translate("MainWindow", u"\ud15c\ud50c\ub9bf \uc124\uc815", None))
        self.menu_F.setTitle(QCoreApplication.translate("MainWindow", u"\ud30c\uc77c(&F)", None))
        self.menu_E.setTitle(QCoreApplication.translate("MainWindow", u"\ud3b8\uc9d1(&E)", None))
        self.menu_V.setTitle(QCoreApplication.translate("MainWindow", u"\ubcf4\uae30(&V)", None))
        self.menu.setTitle(QCoreApplication.translate("MainWindow", u"\ud655\ub300\ud558\uae30/\ucd95\uc18c\ud558\uae30", None))
        self.menu_H.setTitle(QCoreApplication.translate("MainWindow", u"\ub3c4\uc6c0\ub9d0(&H)", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

