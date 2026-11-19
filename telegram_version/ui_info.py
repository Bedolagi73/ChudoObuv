# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'info.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
    QLabel, QPushButton, QSizePolicy, QSpinBox,
    QWidget)

class Ui_Info(object):
    def setupUi(self, Info):
        if not Info.objectName():
            Info.setObjectName(u"Info")
        Info.resize(840, 500)
        self.gridLayout = QGridLayout(Info)
        self.gridLayout.setObjectName(u"gridLayout")
        self.btnBack = QPushButton(Info)
        self.btnBack.setObjectName(u"btnBack")

        self.gridLayout.addWidget(self.btnBack, 0, 0, 1, 1)

        self.labelName = QLabel(Info)
        self.labelName.setObjectName(u"labelName")

        self.gridLayout.addWidget(self.labelName, 1, 0, 1, 1)

        self.valueName = QLabel(Info)
        self.valueName.setObjectName(u"valueName")
        self.valueName.setTextFormat(Qt.TextFormat.PlainText)
        self.valueName.setWordWrap(True)

        self.gridLayout.addWidget(self.valueName, 1, 1, 1, 1)

        self.labelManufacturer = QLabel(Info)
        self.labelManufacturer.setObjectName(u"labelManufacturer")

        self.gridLayout.addWidget(self.labelManufacturer, 2, 0, 1, 1)

        self.valueManufacturer = QLabel(Info)
        self.valueManufacturer.setObjectName(u"valueManufacturer")
        self.valueManufacturer.setTextFormat(Qt.TextFormat.PlainText)
        self.valueManufacturer.setWordWrap(True)

        self.gridLayout.addWidget(self.valueManufacturer, 2, 1, 1, 1)

        self.labelCategory = QLabel(Info)
        self.labelCategory.setObjectName(u"labelCategory")

        self.gridLayout.addWidget(self.labelCategory, 3, 0, 1, 1)

        self.valueCategory = QLabel(Info)
        self.valueCategory.setObjectName(u"valueCategory")
        self.valueCategory.setTextFormat(Qt.TextFormat.PlainText)
        self.valueCategory.setWordWrap(True)

        self.gridLayout.addWidget(self.valueCategory, 3, 1, 1, 1)

        self.labelPrice = QLabel(Info)
        self.labelPrice.setObjectName(u"labelPrice")

        self.gridLayout.addWidget(self.labelPrice, 4, 0, 1, 1)

        self.valuePrice = QLabel(Info)
        self.valuePrice.setObjectName(u"valuePrice")
        self.valuePrice.setTextFormat(Qt.TextFormat.PlainText)

        self.gridLayout.addWidget(self.valuePrice, 4, 1, 1, 1)

        self.labelComposition = QLabel(Info)
        self.labelComposition.setObjectName(u"labelComposition")

        self.gridLayout.addWidget(self.labelComposition, 5, 0, 1, 1)

        self.valueComposition = QLabel(Info)
        self.valueComposition.setObjectName(u"valueComposition")
        self.valueComposition.setTextFormat(Qt.TextFormat.PlainText)
        self.valueComposition.setWordWrap(True)

        self.gridLayout.addWidget(self.valueComposition, 5, 1, 1, 1)

        self.labelDescription = QLabel(Info)
        self.labelDescription.setObjectName(u"labelDescription")

        self.gridLayout.addWidget(self.labelDescription, 6, 0, 1, 1)

        self.valueDescription = QLabel(Info)
        self.valueDescription.setObjectName(u"valueDescription")
        self.valueDescription.setTextFormat(Qt.TextFormat.PlainText)
        self.valueDescription.setWordWrap(True)

        self.gridLayout.addWidget(self.valueDescription, 6, 1, 1, 1)

        self.labelSizeRange = QLabel(Info)
        self.labelSizeRange.setObjectName(u"labelSizeRange")

        self.gridLayout.addWidget(self.labelSizeRange, 7, 0, 1, 1)

        self.valueSizeRange = QLabel(Info)
        self.valueSizeRange.setObjectName(u"valueSizeRange")
        self.valueSizeRange.setTextFormat(Qt.TextFormat.PlainText)
        self.valueSizeRange.setWordWrap(True)

        self.gridLayout.addWidget(self.valueSizeRange, 7, 1, 1, 1)

        self.imagePreview = QLabel(Info)
        self.imagePreview.setObjectName(u"imagePreview")
        self.imagePreview.setMinimumSize(QSize(200, 180))
        self.imagePreview.setMaximumSize(QSize(200, 180))
        self.imagePreview.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.imagePreview, 1, 2, 7, 1)

        self.labelStatus = QLabel(Info)
        self.labelStatus.setObjectName(u"labelStatus")
        self.labelStatus.setTextFormat(Qt.TextFormat.PlainText)
        self.labelStatus.setWordWrap(True)

        self.gridLayout.addWidget(self.labelStatus, 8, 0, 1, 3)

        self.orderSeparator = QFrame(Info)
        self.orderSeparator.setObjectName(u"orderSeparator")
        self.orderSeparator.setFrameShape(QFrame.Shape.HLine)
        self.orderSeparator.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.orderSeparator, 9, 0, 1, 3)

        self.labelAvailableSizes = QLabel(Info)
        self.labelAvailableSizes.setObjectName(u"labelAvailableSizes")

        self.gridLayout.addWidget(self.labelAvailableSizes, 10, 0, 1, 1)

        self.cmbxSizes = QComboBox(Info)
        self.cmbxSizes.setObjectName(u"cmbxSizes")

        self.gridLayout.addWidget(self.cmbxSizes, 10, 1, 1, 2)

        self.labelQuantity = QLabel(Info)
        self.labelQuantity.setObjectName(u"labelQuantity")

        self.gridLayout.addWidget(self.labelQuantity, 11, 0, 1, 1)

        self.spinQuantity = QSpinBox(Info)
        self.spinQuantity.setObjectName(u"spinQuantity")

        self.gridLayout.addWidget(self.spinQuantity, 11, 1, 1, 2)

        self.btnCancel = QPushButton(Info)
        self.btnCancel.setObjectName(u"btnCancel")

        self.gridLayout.addWidget(self.btnCancel, 12, 0, 1, 1)

        self.btnAddToOrder = QPushButton(Info)
        self.btnAddToOrder.setObjectName(u"btnAddToOrder")

        self.gridLayout.addWidget(self.btnAddToOrder, 12, 1, 1, 2)

        self.gridLayout.setRowStretch(1, 1)
        self.gridLayout.setRowStretch(2, 1)
        self.gridLayout.setRowStretch(3, 1)
        self.gridLayout.setRowStretch(4, 1)
        self.gridLayout.setRowStretch(5, 1)
        self.gridLayout.setRowStretch(6, 1)
        self.gridLayout.setRowStretch(7, 1)
        self.gridLayout.setRowStretch(8, 1)
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 2)
#if QT_CONFIG(shortcut)
        self.labelAvailableSizes.setBuddy(self.cmbxSizes)
        self.labelQuantity.setBuddy(self.spinQuantity)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.btnBack, self.cmbxSizes)
        QWidget.setTabOrder(self.cmbxSizes, self.spinQuantity)
        QWidget.setTabOrder(self.spinQuantity, self.btnCancel)
        QWidget.setTabOrder(self.btnCancel, self.btnAddToOrder)

        self.retranslateUi(Info)

        QMetaObject.connectSlotsByName(Info)
    # setupUi

    def retranslateUi(self, Info):
        Info.setWindowTitle(QCoreApplication.translate("Info", u"\u041a\u0430\u0440\u0442\u043e\u0447\u043a\u0430 \u0442\u043e\u0432\u0430\u0440\u0430", None))
        self.btnBack.setText(QCoreApplication.translate("Info", u"\u041d\u0430\u0437\u0430\u0434", None))
        self.labelName.setText(QCoreApplication.translate("Info", u"\u041d\u0430\u0438\u043c\u0435\u043d\u043e\u0432\u0430\u043d\u0438\u0435", None))
        self.valueName.setText("")
        self.labelManufacturer.setText(QCoreApplication.translate("Info", u"\u041f\u0440\u043e\u0438\u0437\u0432\u043e\u0434\u0441\u0442\u0432\u043e", None))
        self.valueManufacturer.setText("")
        self.labelCategory.setText(QCoreApplication.translate("Info", u"\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f", None))
        self.valueCategory.setText("")
        self.labelPrice.setText(QCoreApplication.translate("Info", u"\u0426\u0435\u043d\u0430 \u0441\u043e \u0441\u043a\u0438\u0434\u043a\u043e\u0439", None))
        self.valuePrice.setText("")
        self.labelComposition.setText(QCoreApplication.translate("Info", u"\u0421\u043e\u0441\u0442\u0430\u0432", None))
        self.valueComposition.setText("")
        self.labelDescription.setText(QCoreApplication.translate("Info", u"\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435", None))
        self.valueDescription.setText("")
        self.labelSizeRange.setText(QCoreApplication.translate("Info", u"\u0420\u0430\u0437\u043c\u0435\u0440\u043d\u044b\u0439 \u0440\u044f\u0434", None))
        self.valueSizeRange.setText("")
#if QT_CONFIG(accessibility)
        self.imagePreview.setAccessibleName(QCoreApplication.translate("Info", u"\u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435 \u0442\u043e\u0432\u0430\u0440\u0430", None))
#endif // QT_CONFIG(accessibility)
        self.labelStatus.setText("")
        self.labelAvailableSizes.setText(QCoreApplication.translate("Info", u"\u0414\u043e\u0441\u0442\u0443\u043f\u043d\u044b\u0435 \u0440\u0430\u0437\u043c\u0435\u0440\u044b", None))
        self.labelQuantity.setText(QCoreApplication.translate("Info", u"\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e", None))
        self.btnCancel.setText(QCoreApplication.translate("Info", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
        self.btnAddToOrder.setText(QCoreApplication.translate("Info", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u0432 \u0437\u0430\u043a\u0430\u0437", None))
    # retranslateUi
