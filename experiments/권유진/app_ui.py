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
from PySide6.QtWidgets import (QApplication, QCommandLinkButton, QMainWindow, QMenu,
    QMenuBar, QPushButton, QSizePolicy, QStatusBar,
    QTextEdit, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(701, 600)
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
        self.action_6 = QAction(MainWindow)
        self.action_6.setObjectName(u"action_6")
        self.action_8 = QAction(MainWindow)
        self.action_8.setObjectName(u"action_8")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.textEdit = QTextEdit(self.centralwidget)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setGeometry(QRect(10, 10, 591, 551))
        self.commandLinkButton = QCommandLinkButton(self.centralwidget)
        self.commandLinkButton.setObjectName(u"commandLinkButton")
        self.commandLinkButton.setGeometry(QRect(210, 10, 186, 41))
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(10)
        font.setBold(False)
        font.setUnderline(True)
        self.commandLinkButton.setFont(font)
        self.commandLinkButton.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.InputGaming))
        self.commandLinkButton.setIcon(icon)
        self.pushButton = QPushButton(self.centralwidget)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(610, 530, 75, 24))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 701, 22))
        self.menu_F = QMenu(self.menubar)
        self.menu_F.setObjectName(u"menu_F")
        self.menu_E = QMenu(self.menubar)
        self.menu_E.setObjectName(u"menu_E")
        self.menu_O = QMenu(self.menubar)
        self.menu_O.setObjectName(u"menu_O")
        self.menu_V = QMenu(self.menubar)
        self.menu_V.setObjectName(u"menu_V")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menu_F.menuAction())
        self.menubar.addAction(self.menu_E.menuAction())
        self.menubar.addAction(self.menu_O.menuAction())
        self.menubar.addAction(self.menu_V.menuAction())
        self.menu_F.addAction(self.action_open)
        self.menu_F.addAction(self.action_save)
        self.menu_E.addAction(self.action_copy)
        self.menu_E.addSeparator()
        self.menu_E.addAction(self.action_find)
        self.menu_O.addAction(self.action_1)
        self.menu_O.addAction(self.action_2)
        self.menu_O.addAction(self.action_3)
        self.menu_O.addSeparator()
        self.menu_O.addAction(self.action_5)
        self.menu_V.addAction(self.action_6)
        self.menu_V.addSeparator()
        self.menu_V.addAction(self.action_8)

        self.retranslateUi(MainWindow)

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
        self.action_find.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+S", None))
#endif // QT_CONFIG(shortcut)
        self.action_save.setText(QCoreApplication.translate("MainWindow", u"\uc800\uc7a5(S)", None))
#if QT_CONFIG(shortcut)
        self.action_save.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+S", None))
#endif // QT_CONFIG(shortcut)
        self.action_1.setText(QCoreApplication.translate("MainWindow", u"\uc0ac\uc6a9\uc790 \uc11c\uc2dd 1", None))
        self.action_2.setText(QCoreApplication.translate("MainWindow", u"\uc0ac\uc6a9\uc790 \uc11c\uc2dd 2", None))
        self.action_3.setText(QCoreApplication.translate("MainWindow", u"\uc0ac\uc6a9\uc790 \uc11c\uc2dd 3", None))
        self.action_5.setText(QCoreApplication.translate("MainWindow", u"\uc0ac\uc6a9\uc790 \uc11c\uc2dd \ucd94\uac00...", None))
        self.action_6.setText(QCoreApplication.translate("MainWindow", u"\ud655\ub300\ud558\uae30/\ucd95\uc18c\ud558\uae30", None))
        self.action_8.setText(QCoreApplication.translate("MainWindow", u"\ubc1d\uac8c/\uc5b4\ub461\uac8c", None))
        self.textEdit.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'\ub9d1\uc740 \uace0\ub515'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt;\">\ud14d\uc2a4\ud2b8\ub97c \uc785\ub825\ud574\uc8fc\uc138\uc694. \ud639\uc740 </span></p></body></html>", None))
        self.commandLinkButton.setText(QCoreApplication.translate("MainWindow", u"\ud30c\uc77c \ubd88\ub7ec\uc624\uae30", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"\ubcc0\ud658", None))
        self.menu_F.setTitle(QCoreApplication.translate("MainWindow", u"\ud30c\uc77c(F)", None))
        self.menu_E.setTitle(QCoreApplication.translate("MainWindow", u"\ud3b8\uc9d1(E)", None))
        self.menu_O.setTitle(QCoreApplication.translate("MainWindow", u"\uc11c\uc2dd(O)", None))
        self.menu_V.setTitle(QCoreApplication.translate("MainWindow", u"\ubcf4\uae30(V)", None))
    # retranslateUi
