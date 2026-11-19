import sys
from datetime import date, timedelta

from PySide6.QtCore import QSignalBlocker, QSize, Qt
from PySide6.QtGui import QFont, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QApplication, QDialog, QListWidgetItem, QMessageBox, QWidget
from sqlalchemy import func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from info import Info
from login_dialog import LoginDialog
from models import Cathegory, Order, Product, Product_tovar, Size, engine
from orders import next_order_code, take_stock
from tovar import Tovar
from ui_form import Ui_Widget

# Скидка на товары, по которым не было заказов в предыдущем календарном месяце.
DISCOUNT_PERCENT = 25


class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)
        self.setWindowTitle("Чудо обувь")
        self.info_window = None

        self.user_id = None
        self.user_name = None
        self.model = QStandardItemModel(self)
        self.ui.listOrder.setModel(self.model)
        self.model.rowsInserted.connect(self.update_order_button)
        self.model.rowsRemoved.connect(self.update_order_button)
        self.model.modelReset.connect(self.update_order_button)
        self.ui.listWidget.setSpacing(4)
        self.ui.listWidget.itemClicked.connect(self.show_info)
        self.ui.listWidget.itemActivated.connect(self.show_info)

        self.ui.btnLogin.clicked.connect(self.toggle_login)
        self.ui.btnOrder.clicked.connect(self.create_order)
        self.ui.cmbxSort.setToolTip("Сортировка по цене до скидки")
        self.ui.cmbxSort.currentIndexChanged.connect(self.load_tovars)
        self.ui.cmbxCats.currentIndexChanged.connect(self.load_tovars)
        self.ui.edtSearch.textChanged.connect(self.load_tovars)
        self.load_tovars()

    def toggle_login(self):
        if self.user_id is None:
            dialog = LoginDialog(self)
            result = dialog.exec()
            user_id = dialog.user_id
            user_name = dialog.user_name
            dialog.deleteLater()
            if result != QDialog.DialogCode.Accepted:
                return
            self.user_id = user_id
            self.user_name = user_name
            self.load_cats()
        else:
            self.user_id = None
            self.user_name = None
            self.model.clear()
            with QSignalBlocker(self.ui.cmbxSort), QSignalBlocker(self.ui.cmbxCats):
                self.ui.cmbxSort.setCurrentIndex(0)
                self.ui.cmbxCats.setCurrentIndex(0)
            with QSignalBlocker(self.ui.edtSearch):
                self.ui.edtSearch.clear()

        logged_in = self.user_id is not None
        self.ui.label.setText(self.user_name or "Неавторизованный пользователь")
        self.ui.btnLogin.setText("Выйти" if logged_in else "Войти")
        self.ui.cmbxSort.setEnabled(logged_in)
        self.ui.cmbxCats.setEnabled(logged_in)
        self.ui.edtSearch.setEnabled(logged_in)
        self.update_order_button()
        self.load_tovars()

    def load_cats(self):
        query = select(Cathegory.title, Cathegory.id).order_by(Cathegory.title, Cathegory.id)
        try:
            with Session(engine) as db:
                categories = db.execute(query).all()
        except SQLAlchemyError:
            QMessageBox.warning(
                self, "Каталог", "Не удалось загрузить категории из базы данных."
            )
            return

        combo = self.ui.cmbxCats
        with QSignalBlocker(combo):
            while combo.count() > 1:
                combo.removeItem(combo.count() - 1)
            for title, category_id in categories:
                combo.addItem(title, category_id)

    def load_tovars(self):
        self.ui.listWidget.clear()

        logged_in = self.user_id is not None
        price = func.coalesce(Product.price, 0)
        descending = logged_in and self.ui.cmbxSort.currentIndex() == 1
        price_order = price.desc() if descending else price.asc()
        query = select(Product).order_by(price_order, Product.id)
        category_id = self.ui.cmbxCats.currentData()
        if logged_in and category_id is not None:
            query = query.where(Product.cathegory_id == category_id)

        search_text = self.ui.edtSearch.text().strip()
        if logged_in and search_text:
            query = query.where(
                or_(
                    Product.name.icontains(search_text, autoescape=True),
                    Product.description.icontains(search_text, autoescape=True),
                )
            )

        try:
            with Session(engine) as db:
                products = db.scalars(query).all()
                ordered_ids = self.ordered_last_month(db)
        except SQLAlchemyError:
            QMessageBox.warning(self, "Каталог", "Не удалось загрузить товары из базы данных.")
            return

        for product in products:
            discount = 0 if product.id in ordered_ids else DISCOUNT_PERCENT
            tovar = Tovar(product, discount)
            item = QListWidgetItem(self.ui.listWidget)
            item.setSizeHint(QSize(0, 160))
            self.ui.listWidget.setItemWidget(item, tovar)

    @staticmethod
    def ordered_last_month(db):
        """id товаров, на которые были заказы в предыдущем календарном месяце."""
        first_day_this_month = date.today().replace(day=1)
        first_day_last_month = (first_day_this_month - timedelta(days=1)).replace(day=1)

        rows = (
            db.query(Product_tovar.product_id)
            .join(Order, Product_tovar.order_id == Order.id)
            .filter(
                Order.order_date >= first_day_last_month,
                Order.order_date < first_day_this_month,
            )
            .distinct()
        )
        return {row[0] for row in rows}

    def show_info(self, item):
        if self.user_id is None:
            return
        tovar = self.ui.listWidget.itemWidget(item)
        if tovar is None:
            return
        if self.info_window is None:
            self.info_window = Info(self)
            self.info_window.add.connect(self.add_tovar)
        if self.info_window.isVisible():
            return

        queued_sizes = {
            line["size"].id: line["amount"]
            for line in self.order_lines()
            if line["tovar"].id == tovar.tovar.id
        }
        self.info_window.show_info(tovar.tovar, tovar.discount, queued_sizes)

    def order_lines(self):
        return [self.model.item(row).data() for row in range(self.model.rowCount())]

    def add_tovar(self, tovar: Product, size: Size, amount: int, price: float):
        info = self.info_window
        if self.user_id is None or info is None or amount < 1:
            return

        existing_row = None
        for row, line in enumerate(self.order_lines()):
            if line["tovar"].id == tovar.id and line["size"].id == size.id:
                existing_row = row
                amount += line["amount"]
                break

        text = f"{tovar.name}\nРазмер {size.title} · {amount} шт."
        item = QStandardItem(text)
        item.setToolTip(text)
        item.setEditable(False)
        item.setData({"tovar": tovar, "size": size, "amount": amount, "price": price})
        if existing_row is None:
            self.model.appendRow(item)
        else:
            self.model.setItem(existing_row, item)
        info.close()

    def update_order_button(self):
        self.ui.btnOrder.setEnabled(self.user_id is not None and self.model.rowCount() > 0)

    def create_order(self):
        if self.user_id is None or self.model.rowCount() == 0:
            return

        with Session(engine) as db:
            # Создаём новый заказ.
            new_order = Order(
                code=next_order_code(db),
                order_date=date.today(),
                user_id=self.user_id,
            )
            db.add(new_order)
            db.flush()  # Получаем ID нового заказа.

            # Перебираем позиции в корзине.
            for row in range(self.model.rowCount()):
                item = self.model.item(row)
                data = item.data()
                tovar = data["tovar"]
                size = data["size"]
                count = data["amount"]
                cost = data["price"]

                message = take_stock(db, tovar, size, count)
                if message:
                    db.rollback()
                    QMessageBox.warning(self, "Недостаточно товара", message)
                    self.load_tovars()
                    return

                # Добавляем позицию к заказу.
                order_item = Product_tovar(
                    order_id=new_order.id,
                    product_id=tovar.id,
                    size_id=size.id,
                    count=count,
                    price=int(cost),
                )
                db.add(order_item)

            db.commit()

        QMessageBox.information(self, "Успех", "Заказ успешно оформлен!")
        self.model.clear()
        self.load_tovars()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Calibri", 10))
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
