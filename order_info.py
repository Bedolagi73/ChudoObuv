from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QDialog, QVBoxLayout


class OrderInfo(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = QUiLoader().load(str(Path(__file__).with_name('order_info.ui')), self)
        self.setWindowTitle(self.ui.windowTitle())
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.resize(self.ui.size())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

    def show_window(self, order):
        self.ui.label.setText(f'Заказ № {order.id}')
        self.show()
