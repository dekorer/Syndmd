# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'find.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog, QGridLayout,
    QGroupBox, QLabel, QLineEdit, QPushButton,
    QRadioButton, QSizePolicy, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(495, 211)
        self.gridLayout_2 = QGridLayout(Dialog)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.groupBox = QGroupBox(Dialog)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_3 = QGridLayout(self.groupBox)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.radioButton = QRadioButton(self.groupBox)
        self.radioButton.setObjectName(u"radioButton")
        self.radioButton.setChecked(False)

        self.gridLayout_3.addWidget(self.radioButton, 0, 0, 1, 1)

        self.radioButton_2 = QRadioButton(self.groupBox)
        self.radioButton_2.setObjectName(u"radioButton_2")
        self.radioButton_2.setChecked(True)

        self.gridLayout_3.addWidget(self.radioButton_2, 0, 1, 1, 1)


        self.gridLayout_2.addWidget(self.groupBox, 1, 1, 1, 1)

        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.pushButton_cancel = QPushButton(Dialog)
        self.pushButton_cancel.setObjectName(u"pushButton_cancel")

        self.gridLayout_2.addWidget(self.pushButton_cancel, 1, 3, 1, 1, Qt.AlignmentFlag.AlignTop)

        self.pushButton_findnext = QPushButton(Dialog)
        self.pushButton_findnext.setObjectName(u"pushButton_findnext")
        self.pushButton_findnext.setEnabled(False)

        self.gridLayout_2.addWidget(self.pushButton_findnext, 0, 3, 1, 1)

        self.lineEdit = QLineEdit(Dialog)
        self.lineEdit.setObjectName(u"lineEdit")

        self.gridLayout_2.addWidget(self.lineEdit, 0, 1, 1, 1)

        self.checkBox_CaseSenesitive = QCheckBox(Dialog)
        self.checkBox_CaseSenesitive.setObjectName(u"checkBox_CaseSenesitive")

        self.gridLayout_2.addWidget(self.checkBox_CaseSenesitive, 2, 0, 1, 3)

        self.checkBox_2 = QCheckBox(Dialog)
        self.checkBox_2.setObjectName(u"checkBox_2")

        self.gridLayout_2.addWidget(self.checkBox_2, 3, 0, 1, 3)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"\ucc3e\uae30", None))
        self.groupBox.setTitle(QCoreApplication.translate("Dialog", u"\ubc29\ud5a5", None))
        self.radioButton.setText(QCoreApplication.translate("Dialog", u"\uc704\ub85c", None))
        self.radioButton_2.setText(QCoreApplication.translate("Dialog", u"\uc544\ub798\ub85c", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"\ucc3e\uc744 \ub0b4\uc6a9:", None))
        self.pushButton_cancel.setText(QCoreApplication.translate("Dialog", u"\ucde8\uc18c", None))
        self.pushButton_findnext.setText(QCoreApplication.translate("Dialog", u"\ub2e4\uc74c \ucc3e\uae30", None))
        self.checkBox_CaseSenesitive.setText(QCoreApplication.translate("Dialog", u"\ub300/\uc18c\ubb38\uc790 \uad6c\ubd84", None))
        self.checkBox_2.setText(QCoreApplication.translate("Dialog", u"\uc8fc\uc704\uc5d0 \ubc30\uce58", None))
    # retranslateUi

