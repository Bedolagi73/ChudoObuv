from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence, QStandardItem, QStandardItemModel
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QDialog, QHeaderView, QMenu, QMessageBox, QVBoxLayout
from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload, lazyload

from models import Order, Product, Product_tovar, Stock, User
from order_info import OrderInfo


class OrderError(ValueError):
    pass


class PricesChanged(OrderError):
    def __init__(self, prices):
        super().__init__('Цены изменились. Проверьте новую сумму и подтвердите заказ ещё раз.')
        self.prices = prices


@dataclass
class CartItem:
    product_id: int
    size_id: int
    product_name: str
    size: str
    unit_price: Decimal
    quantity: int

    @property
    def total(self):
        return self.unit_price * self.quantity


def add_to_cart(cart, product, size, quantity, price):
    key = product.id, size.id
    if key in cart:
        quantity += cart[key].quantity
    cart[key] = CartItem(product.id, size.id, product.name, size.title, price, quantity)


def get_prices(db, base_prices, today):
    if not base_prices:
        return {}
    month_start = today.replace(day=1)
    previous_month_start = (month_start - timedelta(days=1)).replace(day=1)
    rows = db.query(Product_tovar.product_id).join(Order, Product_tovar.order_id == Order.id)
    rows = rows.filter(Product_tovar.product_id.in_(base_prices),
                       Order.order_date >= previous_month_start,
                       Order.order_date < month_start).distinct()
    ordered = {row.product_id for row in rows}
    prices = {}
    for product_id, price in base_prices.items():
        amount = Decimal(str(price))
        if product_id not in ordered:
            amount *= Decimal('0.75')
        prices[product_id] = amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return prices


def format_price(amount):
    return f'{amount:,.2f} ₽'.replace(',', ' ').replace('.', ',')


def take_pairs(db, item):
    rows = db.query(Stock.id, Stock.amount).filter(
        Stock.product_id == item.product_id, Stock.size_id == item.size_id, Stock.amount > 0
    ).order_by(Stock.id).with_for_update().all()
    available = sum(row.amount for row in rows)
    if available < item.quantity:
        raise OrderError(
            f'«{item.product_name}», размер {item.size}: доступно пар — {available}. '
            'Удалите позицию или добавьте её снова с меньшим количеством.'
        )
    remaining = item.quantity
    for row in rows:
        taken = min(remaining, row.amount)
        result = db.execute(
            update(Stock)
            .where(Stock.id == row.id, Stock.amount >= taken)
            .values(amount=Stock.amount - taken)
        )
        if result.rowcount != 1:
            raise OrderError('Остатки изменились. Проверьте количество и повторите заказ.')
        remaining -= taken
        if remaining == 0:
            break


def save_order(database, user_id, cart):
    if not cart or any(line.quantity < 1 for line in cart.values()):
        raise OrderError('Добавьте хотя бы одну пару в заказ.')
    today = date.today()
    with Session(database) as db:
        if db.get(User, user_id) is None:
            raise OrderError('Пользователь больше недоступен. Войдите снова.')
        product_ids = {item.product_id for item in cart.values()}
        rows = db.query(Product.id, Product.price).filter(Product.id.in_(product_ids)).all()
        base_prices = {row.id: row.price for row in rows}
        if len(product_ids) != len(base_prices):
            raise OrderError('Один из товаров больше недоступен. Удалите его из заказа.')
        prices = get_prices(db, base_prices, today)
        for item in cart.values():
            if prices[item.product_id] != item.unit_price:
                raise PricesChanged(prices)

        # Блокируем остатки в одном порядке, даже если покупатели добавили их в разном порядке.
        for key in sorted(cart):
            take_pairs(db, cart[key])
        order = Order(order_date=today, user_id=user_id)
        db.add(order)
        for item in cart.values():
            # Одна строка order_items соответствует одной паре.
            for _ in range(item.quantity):
                order.items.append(Product_tovar(
                    product_id=item.product_id, size_id=item.size_id, price=float(item.unit_price)
                ))
        db.flush()
        order_id = order.id
        db.commit()
    return order_id, today


def delete_order(database, order_id):
    with Session(database) as db, db.begin():
        if db.scalar(select(Order.id).where(Order.id == order_id).with_for_update()) is None:
            raise OrderError('Заказ уже удалён.')

        pair = (Product_tovar.product_id, Product_tovar.size_id)
        lines = db.execute(select(*pair, func.count()).where(Product_tovar.order_id == order_id)
                           .group_by(*pair).order_by(*pair)).all()
        for product_id, size_id, quantity in lines:
            stock_id = db.scalar(select(Stock.id).where(
                Stock.product_id == product_id, Stock.size_id == size_id, Stock.amount >= 0,
            ).order_by(Stock.id).limit(1).with_for_update())
            if stock_id is None:
                db.add(Stock(product_id=product_id, size_id=size_id, amount=quantity))
            else:
                db.execute(update(Stock).where(Stock.id == stock_id).values(amount=Stock.amount + quantity))

        db.execute(delete(Product_tovar).where(Product_tovar.order_id == order_id))
        result = db.execute(delete(Order).where(Order.id == order_id))
        if result.rowcount != 1:
            raise OrderError('Заказ уже удалён.')


class Orders(QDialog):
    def __init__(self, database, user, parent=None):
        super().__init__(parent)
        self.database = database
        self.user = user
        self.changed = False
        self.order_window = None

        self.ui = QUiLoader().load(str(Path(__file__).with_name('orders.ui')), self)
        self.setWindowTitle(self.ui.windowTitle())
        self.resize(self.ui.size())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        self.ui.btnBack.clicked.connect(self.reject)
        self.ui.btnAddOrder.setProperty('primary', True)
        self.ui.btnAddOrder.clicked.connect(self.add_order)

        self.model = QStandardItemModel(self)
        self.model.setHorizontalHeaderLabels(['ID', 'Дата', 'ФИО клиента'])
        self.table = self.ui.tblOrders
        self.table.setModel(self.model)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.clicked.connect(self.order_clicked)

        self.remove_action = QAction('Удалить заказ', self.table)
        self.remove_action.setShortcut(QKeySequence('Delete'))
        self.remove_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.remove_action.triggered.connect(self.remove_order)
        self.table.addAction(self.remove_action)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_order_menu)
        self.load_orders()

    def load_orders(self):
        try:
            with Session(self.database) as db:
                orders = (db.query(Order).options(lazyload('*'), joinedload(Order.user))
                          .order_by(Order.order_date.desc(), Order.id.desc()).all())
        except SQLAlchemyError:
            QMessageBox.warning(self, 'Заказы', 'Не удалось загрузить список заказов.')
            return

        self.model.removeRows(0, self.model.rowCount())
        for order in orders:
            id_item = QStandardItem(str(order.id))
            id_item.setData(order, 256)
            self.model.appendRow([
                id_item, QStandardItem(order.order_date.strftime('%d.%m.%Y')), QStandardItem(str(order.user)),
            ])

    def order_clicked(self, index):
        order = index.siblingAtColumn(0).data(256)
        if order is None:
            return
        if self.order_window is None:
            self.order_window = OrderInfo(self)
        self.order_window.show_window(order)

    def add_order(self):
        from order_dialogs import NewOrderDialog

        try:
            dialog = NewOrderDialog(self.database, self.user, self)
        except SQLAlchemyError:
            QMessageBox.warning(self, 'Заказы', 'Не удалось загрузить клиентов и товары.')
            return
        accepted = dialog.exec() == QDialog.DialogCode.Accepted
        dialog.deleteLater()
        if accepted:
            self.changed = True
            self.load_orders()

    def show_order_menu(self, point):
        index = self.table.indexAt(point)
        if index.isValid():
            self.table.selectRow(index.row())
            menu = QMenu()
            menu.addAction(self.remove_action)
            menu.exec(self.table.viewport().mapToGlobal(point))

    def remove_order(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        order_id = rows[0].data(256).id
        answer = QMessageBox.question(self, 'Удаление заказа', f'Удалить заказ №{order_id} и вернуть пары на склад?',
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                      QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            delete_order(self.database, order_id)
        except OrderError as error:
            self.load_orders()
            QMessageBox.warning(self, 'Заказы', str(error))
        except SQLAlchemyError:
            QMessageBox.warning(self, 'Заказы', 'Не удалось удалить заказ.')
        else:
            self.changed = True
            self.load_orders()
