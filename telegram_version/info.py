from pathlib import Path

from PySide6.QtCore import QSignalBlocker, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QVBoxLayout, QWidget

from models import Product, Size
from tovar import Tovar, product_pixmap, unit_price


BASE_DIR = Path(__file__).resolve().parent
AVAILABLE_AMOUNT_ROLE = Qt.ItemDataRole.UserRole + 1


class Info(QWidget):
    add = Signal(Product, Size, int, float)

    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Window)
        self.tovar = None
        self.price = 0

        loader = QUiLoader()
        self.ui = loader.load(str(BASE_DIR / "info.ui"), self)
        if self.ui is None:
            raise RuntimeError(f"Не удалось загрузить info.ui: {loader.errorString()}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        self.resize(self.ui.size())

        self.setWindowTitle(self.ui.windowTitle())
        self.setWindowIcon(QIcon(str(BASE_DIR / "import" / "Чудо Обувь.ico")))
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.ui.btnBack.clicked.connect(self.close)
        self.ui.btnCancel.clicked.connect(self.close)
        self.ui.cmbxSizes.currentIndexChanged.connect(self.update_stock)
        self.ui.spinQuantity.valueChanged.connect(self.update_add_button)
        self.ui.btnAddToOrder.clicked.connect(self.add_tovar)
        self.ui.btnAddToOrder.setEnabled(False)
        self.ui.spinQuantity.setEnabled(False)

    def show_info(self, tovar: Product, discount=0, queued_sizes=None):
        self.tovar = tovar
        self.price = unit_price(tovar.price, discount)
        queued_sizes = queued_sizes or {}
        ui = self.ui

        ui.imagePreview.setPixmap(product_pixmap(tovar.image, ui.imagePreview.size()))
        ui.valueName.setText(tovar.name or "—")
        ui.valueManufacturer.setText(tovar.manufacturer.title if tovar.manufacturer else "—")
        ui.valueCategory.setText(tovar.cathegory.title if tovar.cathegory else "—")
        ui.valuePrice.setText(f"{Tovar.format_price(self.price)} ₽")
        ui.valuePrice.setToolTip(f"Скидка {discount}%" if discount else "")
        ui.valueComposition.setText(tovar.composition or "—")
        ui.valueDescription.setText(tovar.description or "—")

        stock = sorted(
            (item for item in tovar.stock if item.size is not None),
            key=lambda item: item.size.title,
        )
        ui.valueSizeRange.setText(", ".join(item.size.title for item in stock) or "—")
        combo = ui.cmbxSizes
        with QSignalBlocker(combo):
            combo.clear()
            for item in stock:
                size = item.size
                amount = (item.amount or 0) - queued_sizes.get(size.id, 0)
                if amount > 0:
                    combo.addItem(size.title, size)
                    combo.setItemData(combo.count() - 1, amount, AVAILABLE_AMOUNT_ROLE)
        combo.setEnabled(combo.count() > 0)
        self.update_stock()
        self.show()

    def update_stock(self):
        amount = self.ui.cmbxSizes.currentData(AVAILABLE_AMOUNT_ROLE) or 0
        self.ui.spinQuantity.setValue(0)
        self.ui.spinQuantity.setMaximum(amount)
        self.ui.spinQuantity.setEnabled(amount > 0)
        self.ui.labelStatus.setText(
            f"Можно добавить: {amount}" if amount else "Нет доступных для заказа размеров"
        )
        self.update_add_button(0)

    def update_add_button(self, quantity):
        self.ui.btnAddToOrder.setEnabled(quantity > 0)

    def add_tovar(self):
        size = self.ui.cmbxSizes.currentData()
        quantity = self.ui.spinQuantity.value()
        if self.tovar is not None and size is not None and quantity > 0:
            self.add.emit(self.tovar, size, quantity, self.price)
