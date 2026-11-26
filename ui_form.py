# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.12.0
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
    QGridLayout, QLabel, QLineEdit, QListView,
    QListWidget, QListWidgetItem, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_Widget(object):
    def setupUi(self, Widget):
        if not Widget.objectName():
            Widget.setObjectName(u"Widget")
        Widget.resize(1000, 700)
        self.gridLayout = QGridLayout(Widget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 0, 0, 1, 1)

        self.label = QLabel(Widget)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)

        self.controlsFrame = QFrame(Widget)
        self.controlsFrame.setObjectName(u"controlsFrame")
        self.controlsFrame.setEnabled(False)
        self.controlsLayout = QVBoxLayout(self.controlsFrame)
        self.controlsLayout.setObjectName(u"controlsLayout")
        self.controlsLayout.setContentsMargins(0, 0, 0, 0)
        self.sortLabel = QLabel(self.controlsFrame)
        self.sortLabel.setObjectName(u"sortLabel")

        self.controlsLayout.addWidget(self.sortLabel)

        self.comboBox = QComboBox(self.controlsFrame)
        self.comboBox.setObjectName(u"comboBox")

        self.controlsLayout.addWidget(self.comboBox)

        self.filterLabel = QLabel(self.controlsFrame)
        self.filterLabel.setObjectName(u"filterLabel")

        self.controlsLayout.addWidget(self.filterLabel)

        self.categoryComboBox = QComboBox(self.controlsFrame)
        self.categoryComboBox.setObjectName(u"categoryComboBox")

        self.controlsLayout.addWidget(self.categoryComboBox)

        self.searchLabel = QLabel(self.controlsFrame)
        self.searchLabel.setObjectName(u"searchLabel")

        self.controlsLayout.addWidget(self.searchLabel)

        self.lineEdit = QLineEdit(self.controlsFrame)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setClearButtonEnabled(True)

        self.controlsLayout.addWidget(self.lineEdit)

        self.orderLabel = QLabel(self.controlsFrame)
        self.orderLabel.setObjectName(u"orderLabel")

        self.controlsLayout.addWidget(self.orderLabel)

        self.listOrder = QListView(self.controlsFrame)
        self.listOrder.setObjectName(u"listOrder")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listOrder.sizePolicy().hasHeightForWidth())
        self.listOrder.setSizePolicy(sizePolicy)
        self.listOrder.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.listOrder.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.listOrder.setWordWrap(True)
        self.listOrder.setResizeMode(QListView.ResizeMode.Adjust)

        self.controlsLayout.addWidget(self.listOrder)

        self.cartButton = QPushButton(self.controlsFrame)
        self.cartButton.setObjectName(u"cartButton")

        self.controlsLayout.addWidget(self.cartButton)

        self.ordersButton = QPushButton(self.controlsFrame)
        self.ordersButton.setObjectName(u"ordersButton")

        self.controlsLayout.addWidget(self.ordersButton)


        self.gridLayout.addWidget(self.controlsFrame, 1, 0, 1, 1)

        self.listWidget = QListWidget(Widget)
        self.listWidget.setObjectName(u"listWidget")

        self.gridLayout.addWidget(self.listWidget, 1, 1, 1, 1)

        self.gridLayout.setRowStretch(1, 1)
        self.gridLayout.setColumnStretch(1, 1)
#if QT_CONFIG(shortcut)
        self.sortLabel.setBuddy(self.comboBox)
        self.filterLabel.setBuddy(self.categoryComboBox)
        self.searchLabel.setBuddy(self.lineEdit)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.comboBox, self.categoryComboBox)
        QWidget.setTabOrder(self.categoryComboBox, self.lineEdit)
        QWidget.setTabOrder(self.lineEdit, self.listOrder)
        QWidget.setTabOrder(self.listOrder, self.cartButton)
        QWidget.setTabOrder(self.cartButton, self.ordersButton)
        QWidget.setTabOrder(self.ordersButton, self.listWidget)

        self.retranslateUi(Widget)

        QMetaObject.connectSlotsByName(Widget)
    # setupUi

    def retranslateUi(self, Widget):
        Widget.setWindowTitle(QCoreApplication.translate("Widget", u"\u0427\u0443\u0434\u043e \u041e\u0431\u0443\u0432\u044c", None))
        self.label.setText(QCoreApplication.translate("Widget", u"\u041a\u0430\u0442\u0430\u043b\u043e\u0433 \u0442\u043e\u0432\u0430\u0440\u043e\u0432", None))
        self.sortLabel.setText(QCoreApplication.translate("Widget", u"\u0421\u043e\u0440\u0442\u0438\u0440\u043e\u0432\u043a\u0430", None))
        self.filterLabel.setText(QCoreApplication.translate("Widget", u"\u0424\u0438\u043b\u044c\u0442\u0440\u0430\u0446\u0438\u044f", None))
#if QT_CONFIG(accessibility)
        self.categoryComboBox.setAccessibleName(QCoreApplication.translate("Widget", u"\u0424\u0438\u043b\u044c\u0442\u0440 \u043f\u043e \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0438 \u0442\u043e\u0432\u0430\u0440\u0430", None))
#endif // QT_CONFIG(accessibility)
        self.searchLabel.setText(QCoreApplication.translate("Widget", u"\u041f\u043e\u0438\u0441\u043a", None))
#if QT_CONFIG(accessibility)
        self.lineEdit.setAccessibleName(QCoreApplication.translate("Widget", u"\u041f\u043e\u0438\u0441\u043a \u0442\u043e\u0432\u0430\u0440\u043e\u0432", None))
#endif // QT_CONFIG(accessibility)
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("Widget", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0438\u043b\u0438 \u043e\u043f\u0438\u0441\u0430\u043d\u0438\u0435", None))
        self.orderLabel.setText(QCoreApplication.translate("Widget", u"\u041a\u043e\u0440\u0437\u0438\u043d\u0430", None))
#if QT_CONFIG(accessibility)
        self.listOrder.setAccessibleName(QCoreApplication.translate("Widget", u"\u041f\u043e\u0437\u0438\u0446\u0438\u0438 \u0437\u0430\u043a\u0430\u0437\u0430", None))
#endif // QT_CONFIG(accessibility)
        self.cartButton.setText(QCoreApplication.translate("Widget", u"\u041e\u0444\u043e\u0440\u043c\u0438\u0442\u044c \u0437\u0430\u043a\u0430\u0437", None))
        self.ordersButton.setText(QCoreApplication.translate("Widget", u"\u0417\u0430\u043a\u0430\u0437\u044b", None))
    # retranslateUi

