# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'loading_preview.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QProgressBar, QSizePolicy,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(323, 61)
        self.preview_progressBar = QProgressBar(Form)
        self.preview_progressBar.setObjectName(u"preview_progressBar")
        self.preview_progressBar.setGeometry(QRect(10, 30, 301, 16))
        self.preview_progressBar.setCursor(QCursor(Qt.CursorShape.WaitCursor))
        self.preview_progressBar.setAutoFillBackground(False)
        self.preview_progressBar.setStyleSheet(u"QProgressBar {\n"
"        border: none;\n"
"        background-color: white;\n"
"		height: 2px;\n"
"    }\n"
"    QProgressBar::chunk {\n"
"        background-color: #323232;\n"
"    }\n"
"")
        self.preview_progressBar.setValue(24)
        self.preview_progressBar.setTextVisible(False)
        self.preview_progressBar.setInvertedAppearance(False)
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 10, 291, 16))
        font = QFont()
        font.setFamilies([u"\ub9d1\uc740 \uace0\ub515"])
        self.label.setFont(font)
        self.label.setCursor(QCursor(Qt.CursorShape.IBeamCursor))
        self.label.setMouseTracking(False)
        self.label.setTabletTracking(False)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"loading", None))
        self.label.setText(QCoreApplication.translate("Form", u"\ubbf8\ub9ac\ubcf4\uae30 \uac31\uc2e0 \uc911...", None))
    # retranslateUi

