# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'app.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
    QLabel, QMainWindow, QMenu, QMenuBar,
    QPushButton, QScrollArea, QSizePolicy, QStatusBar,
    QTextEdit, QToolBar, QWidget)
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
        self.pdfViewerArea = QScrollArea(self.centralwidget)
        self.pdfViewerArea.setObjectName(u"pdfViewerArea")
        self.pdfViewerArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 442, 378))
        self.pdfViewerArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout.addWidget(self.pdfViewerArea, 5, 1, 1, 1)

        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.groupBox.setFlat(True)
        self.gridLayout_3 = QGridLayout(self.groupBox)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.pushButton_preview = QPushButton(self.groupBox)
        self.pushButton_preview.setObjectName(u"pushButton_preview")

        self.gridLayout_3.addWidget(self.pushButton_preview, 1, 1, 1, 1)

        self.template_label = QLabel(self.groupBox)
        self.template_label.setObjectName(u"template_label")

        self.gridLayout_3.addWidget(self.template_label, 2, 0, 1, 1)

        self.hwpruncheck = QCheckBox(self.groupBox)
        self.hwpruncheck.setObjectName(u"hwpruncheck")
        self.hwpruncheck.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.gridLayout_3.addWidget(self.hwpruncheck, 6, 0, 1, 2)

        self.pushButton = QPushButton(self.groupBox)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.gridLayout_3.addWidget(self.pushButton, 2, 1, 1, 1)

        self.pushButton_open = QPushButton(self.groupBox)
        self.pushButton_open.setObjectName(u"pushButton_open")
        self.pushButton_open.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.gridLayout_3.addWidget(self.pushButton_open, 1, 0, 1, 1)


        self.gridLayout.addWidget(self.groupBox, 6, 0, 1, 2)

        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 4, 0, 1, 1, Qt.AlignmentFlag.AlignHCenter)

        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 4, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter)

        self.textEdit = QTextEdit(self.centralwidget)
        self.textEdit.setObjectName(u"textEdit")

        self.gridLayout.addWidget(self.textEdit, 5, 0, 1, 1)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.label, 1, 0, 1, 2)

        self.template_button = QPushButton(self.centralwidget)
        self.template_button.setObjectName(u"template_button")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.template_button.sizePolicy().hasHeightForWidth())
        self.template_button.setSizePolicy(sizePolicy)
        font1 = QFont()
        font1.setPointSize(10)
        self.template_button.setFont(font1)
        self.template_button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.gridLayout.addWidget(self.template_button, 3, 1, 1, 1, Qt.AlignmentFlag.AlignRight)

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
        self.groupBox.setTitle("")
        self.pushButton_preview.setText(QCoreApplication.translate("MainWindow", u"\ubbf8\ub9ac\ubcf4\uae30 \uac31\uc2e0\ud558\uae30(&F5)", None))
#if QT_CONFIG(shortcut)
        self.pushButton_preview.setShortcut(QCoreApplication.translate("MainWindow", u"F5", None))
#endif // QT_CONFIG(shortcut)
        self.template_label.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.hwpruncheck.setText(QCoreApplication.translate("MainWindow", u"\ubcc0\ud658\ub41c \ud55c\uae00\ud30c\uc77c \uc2e4\ud589\ud558\uae30(&R)", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"\ubcc0\ud658\ud558\uae30", None))
        self.pushButton_open.setText(QCoreApplication.translate("MainWindow", u"MD \ud30c\uc77c \uc5c5\ub85c\ub4dc", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"\ub9c8\ud06c\ub2e4\uc6b4 \uc785\ub825\ub780", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\ud55c/\uae00 \ud30c\uc77c \ubbf8\ub9ac\ubcf4\uae30", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\ub9c8\ud06c\ub2e4\uc6b4 \ud55c/\uae00 \ubcc0\ud658\uae30", None))
        self.template_button.setText(QCoreApplication.translate("MainWindow", u"\ud15c\ud50c\ub9bf \uad00\ub9ac \u25bc", None))
        self.menu_F.setTitle(QCoreApplication.translate("MainWindow", u"\ud30c\uc77c(&F)", None))
        self.menu_E.setTitle(QCoreApplication.translate("MainWindow", u"\ud3b8\uc9d1(&E)", None))
        self.menu_V.setTitle(QCoreApplication.translate("MainWindow", u"\ubcf4\uae30(&V)", None))
        self.menu.setTitle(QCoreApplication.translate("MainWindow", u"\ud655\ub300\ud558\uae30/\ucd95\uc18c\ud558\uae30", None))
        self.menu_H.setTitle(QCoreApplication.translate("MainWindow", u"\ub3c4\uc6c0\ub9d0(&H)", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

