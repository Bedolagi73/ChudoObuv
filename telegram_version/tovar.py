from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget

from ui_tovar import Ui_Form

BASE_DIR = Path(__file__).resolve().parent
IMAGES_DIR = BASE_DIR / "import" / "Images"
PLACEHOLDER_IMAGE = BASE_DIR / "import" / "picture.png"
LOW_STOCK_LIMIT = 3


def unit_price(price, discount):
    # В существующей базе цена позиции заказа хранится в целых рублях.
    return ((price or 0) * (100 - discount) + 50) // 100


def product_pixmap(image_name, size):
    pixmap = QPixmap(str(IMAGES_DIR / image_name)) if image_name else QPixmap()
    if pixmap.isNull():
        pixmap = QPixmap(str(PLACEHOLDER_IMAGE))
    if pixmap.isNull():
        return pixmap
    return pixmap.scaled(
        size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
    )


class Tovar(QWidget):

    def __init__(self, tovar, discount=0, parent=None):
        super().__init__(parent)
        self.tovar = tovar
        self.discount = discount
        self.title_text = ""

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.fill()

    def fill(self):
        product = self.tovar
        total_amount = sum((item.amount or 0) for item in product.stock)

        self.load_image(product.image)

        manufacturer = product.manufacturer.title if product.manufacturer else "—"
        self.title_text = f"{manufacturer} | {product.name}"
        self.ui.label_2.setToolTip(self.title_text)
        self.update_title()

        cathegory = product.cathegory.title if product.cathegory else "—"
        self.ui.label_4.setText(cathegory)

        self.ui.label_6.setText(str(total_amount))
        self.ui.label_6.setToolTip(f"Всего на складе: {total_amount} пар")

        composition = product.composition or "—"
        self.ui.label_8.setText(composition)
        self.ui.label_8.setToolTip(composition)
        self.ui.label_8.setMaximumHeight(
            self.ui.label_8.fontMetrics().lineSpacing() * 4
        )

        price = product.price or 0
        final_price = unit_price(price, self.discount)
        self.ui.label_9.setText(f"{self.format_price(final_price)} ₽")
        if self.discount:
            self.ui.label_9.setToolTip(
                f"Скидка {self.discount}%: нет заказов за предыдущий месяц "
                f"(обычная цена {self.format_price(price)} ₽)"
            )
        else:
            self.ui.label_9.setToolTip(f"Обычная цена {self.format_price(price)} ₽")

        if total_amount <= LOW_STOCK_LIMIT:
            self.setStyleSheet(
                self.styleSheet() + " #Form { background-color: #ff8080; }"
            )
            self.ui.label_6.setToolTip(
                f"Доступно для заказа: {total_amount} пар (не больше {LOW_STOCK_LIMIT})"
            )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_title()

    def update_title(self):
        if not hasattr(self, "ui") or not self.title_text:
            return
        metrics = self.ui.label_2.fontMetrics()
        width = max(self.ui.label_2.width() - 4, 0)
        self.ui.label_2.setText(
            metrics.elidedText(self.title_text, Qt.TextElideMode.ElideRight, width)
        )

    def load_image(self, image_name):
        self.ui.label.setPixmap(product_pixmap(image_name, self.ui.label.size()))

    @staticmethod
    def format_price(value):
        return f"{value:,.2f}".replace(",", " ").replace(".", ",")
