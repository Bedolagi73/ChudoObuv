# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.10.3
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QFrame,
    QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QListView, QListWidget, QListWidgetItem, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_Widget(object):
    def setupUi(self, Widget):
        if not Widget.objectName():
            Widget.setObjectName(u"Widget")
        Widget.resize(1100, 660)
        Widget.setStyleSheet(u"#Widget {\n"
"    background-color: #ffffff;\n"
"}\n"
"#frame {\n"
"    background-color: #ffffff;\n"
"    border: none;\n"
"}\n"
"#frame_2 {\n"
"    background-color: #d2f6e7;\n"
"    border: none;\n"
"}\n"
"#frame_3 {\n"
"    background-color: #ffffff;\n"
"    border: none;\n"
"}\n"
"QListWidget {\n"
"    background-color: #ffffff;\n"
"    border: none;\n"
"    outline: none;\n"
"}\n"
"#listOrder {\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #70b2af;\n"
"}\n"
"QComboBox {\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #70b2af;\n"
"    border-radius: 3px;\n"
"    padding: 2px 6px;\n"
"}\n"
"QComboBox:focus {\n"
"    border: 2px solid #70b2af;\n"
"}\n"
"QComboBox QAbstractItemView {\n"
"    background-color: #ffffff;\n"
"    selection-background-color: #70b2af;\n"
"}")
        self.gridLayout = QGridLayout(Widget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.frame = QFrame(Widget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")
        self.label.setTextFormat(Qt.TextFormat.PlainText)

        self.horizontalLayout.addWidget(self.label)

        self.btnLogin = QPushButton(self.frame)
        self.btnLogin.setObjectName(u"btnLogin")

        self.horizontalLayout.addWidget(self.btnLogin)


        self.gridLayout.addWidget(self.frame, 0, 0, 1, 2)

        self.frame_2 = QFrame(Widget)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frame_2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(12, 12, 12, 12)
        self.labelCats = QLabel(self.frame_2)
        self.labelCats.setObjectName(u"labelCats")

        self.verticalLayout.addWidget(self.labelCats)

        self.cmbxCats = QComboBox(self.frame_2)
        self.cmbxCats.addItem("")
        self.cmbxCats.setObjectName(u"cmbxCats")
        self.cmbxCats.setEnabled(False)

        self.verticalLayout.addWidget(self.cmbxCats)

        self.labelSort = QLabel(self.frame_2)
        self.labelSort.setObjectName(u"labelSort")

        self.verticalLayout.addWidget(self.labelSort)

        self.cmbxSort = QComboBox(self.frame_2)
        self.cmbxSort.addItem("")
        self.cmbxSort.addItem("")
        self.cmbxSort.setObjectName(u"cmbxSort")
        self.cmbxSort.setEnabled(False)

        self.verticalLayout.addWidget(self.cmbxSort)

        self.labelSearch = QLabel(self.frame_2)
        self.labelSearch.setObjectName(u"labelSearch")

        self.verticalLayout.addWidget(self.labelSearch)

        self.edtSearch = QLineEdit(self.frame_2)
        self.edtSearch.setObjectName(u"edtSearch")
        self.edtSearch.setEnabled(False)
        self.edtSearch.setClearButtonEnabled(True)

        self.verticalLayout.addWidget(self.edtSearch)

        self.labelOrder = QLabel(self.frame_2)
        self.labelOrder.setObjectName(u"labelOrder")

        self.verticalLayout.addWidget(self.labelOrder)

        self.listOrder = QListView(self.frame_2)
        self.listOrder.setObjectName(u"listOrder")
        self.listOrder.setMinimumSize(QSize(0, 160))
        self.listOrder.setMaximumSize(QSize(16777215, 192))
        self.listOrder.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.listOrder.setWordWrap(True)
        self.listOrder.setSpacing(3)

        self.verticalLayout.addWidget(self.listOrder)

        self.btnOrder = QPushButton(self.frame_2)
        self.btnOrder.setObjectName(u"btnOrder")
        self.btnOrder.setEnabled(False)

        self.verticalLayout.addWidget(self.btnOrder)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.gridLayout.addWidget(self.frame_2, 1, 0, 1, 1)

        self.frame_3 = QFrame(Widget)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_2 = QGridLayout(self.frame_3)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.listWidget = QListWidget(self.frame_3)
        self.listWidget.setObjectName(u"listWidget")

        self.gridLayout_2.addWidget(self.listWidget, 0, 0, 1, 1)


        self.gridLayout.addWidget(self.frame_3, 1, 1, 1, 1)

        self.gridLayout.setRowStretch(0, 1)
        self.gridLayout.setRowStretch(1, 8)
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 4)
#if QT_CONFIG(shortcut)
        self.labelCats.setBuddy(self.cmbxCats)
        self.labelSort.setBuddy(self.cmbxSort)
        self.labelSearch.setBuddy(self.edtSearch)
        self.labelOrder.setBuddy(self.listOrder)
#endif // QT_CONFIG(shortcut)

        self.retranslateUi(Widget)

        QMetaObject.connectSlotsByName(Widget)
    # setupUi

    def retranslateUi(self, Widget):
        Widget.setWindowTitle(QCoreApplication.translate("Widget", u"\u0427\u0443\u0434\u043e \u043e\u0431\u0443\u0432\u044c", None))
        self.label.setText(QCoreApplication.translate("Widget", u"\u041d\u0435\u0430\u0432\u0442\u043e\u0440\u0438\u0437\u043e\u0432\u0430\u043d\u043d\u044b\u0439 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c", None))
        self.btnLogin.setText(QCoreApplication.translate("Widget", u"\u0412\u043e\u0439\u0442\u0438", None))
        self.labelCats.setText(QCoreApplication.translate("Widget", u"\u0424\u0438\u043b\u044c\u0442\u0440\u0430\u0446\u0438\u044f", None))
        self.cmbxCats.setItemText(0, QCoreApplication.translate("Widget", u"\u0412\u0441\u0435 \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0438", None))

        self.labelSort.setText(QCoreApplication.translate("Widget", u"\u0421\u043e\u0440\u0442\u0438\u0440\u043e\u0432\u043a\u0430", None))
        self.cmbxSort.setItemText(0, QCoreApplication.translate("Widget", u"\u041f\u043e \u0432\u043e\u0437\u0440\u0430\u0441\u0442\u0430\u043d\u0438\u044e \u0446\u0435\u043d\u044b", None))
        self.cmbxSort.setItemText(1, QCoreApplication.translate("Widget", u"\u041f\u043e \u0443\u0431\u044b\u0432\u0430\u043d\u0438\u044e \u0446\u0435\u043d\u044b", None))

        self.labelSearch.setText(QCoreApplication.translate("Widget", u"\u041f\u043e\u0438\u0441\u043a", None))
        self.labelOrder.setText(QCoreApplication.translate("Widget", u"\u041a\u043e\u0440\u0437\u0438\u043d\u0430", None))
#if QT_CONFIG(accessibility)
        self.listOrder.setAccessibleName(QCoreApplication.translate("Widget", u"\u041a\u043e\u0440\u0437\u0438\u043d\u0430", None))
#endif // QT_CONFIG(accessibility)
        self.btnOrder.setText(QCoreApplication.translate("Widget", u"\u041e\u0444\u043e\u0440\u043c\u0438\u0442\u044c \u0437\u0430\u043a\u0430\u0437", None))
    # retranslateUi
