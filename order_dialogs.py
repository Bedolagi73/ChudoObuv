from datetime import date

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QListWidget, QListWidgetItem, QMessageBox, QPushButton, QScrollArea,
    QSpinBox, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from auth import find_user, is_customer
from models import Order, Product, Size, Stock, User
from orders import OrderError, PricesChanged, add_to_cart, delete_order, format_price, get_prices, save_order
from tovar import load_photo


def make_label(value=''):
    label = QLabel(value)
    label.setTextFormat(Qt.TextFormat.PlainText)
    label.setWordWrap(True)
    return label


class LoginDialog(QDialog):
    def __init__(self, database, parent=None):
        super().__init__(parent)
        self.database = database
        self.user = None
        self.setWindowTitle('Вход в каталог')
        self.setMinimumWidth(350)
        form = QFormLayout(self)
        self.login = QLineEdit()
        form.addRow('&Логин', self.login)
        self.message = make_label()
        form.addRow(self.message)
        actions = QDialogButtonBox()
        submit = actions.addButton('Войти', QDialogButtonBox.ButtonRole.AcceptRole)
        submit.setProperty('primary', True)
        submit.setDefault(True)
        actions.addButton('Отмена', QDialogButtonBox.ButtonRole.RejectRole)
        actions.accepted.connect(self.sign_in)
        actions.rejected.connect(self.reject)
        form.addRow(actions)
        self.login.setFocus()

    def sign_in(self):
        login = self.login.text().strip()
        if not login:
            self.message.setText('Введите логин.')
            self.login.setFocus()
            return
        try:
            user = find_user(self.database, login)
        except SQLAlchemyError:
            self.message.setText('Не удалось выполнить вход. Проверьте подключение к базе.')
            return
        if user is None:
            self.message.setText('Не удалось найти пользователя по этому логину.')
            self.login.setFocus()
            return
        self.user = user
        self.accept()


def size_order(title):
    try:
        return 0, float(title.replace(',', '.'))
    except ValueError:
        return 1, title.casefold()


class Info(QDialog):
    add = Signal(Product, Size, int)
    missing = Signal()

    def __init__(self, database, cart, parent=None):
        super().__init__(parent)
        self.database = database
        self.cart = cart
        self.user = None
        self.can_order = False
        self.setWindowTitle('Карточка товара')
        self.resize(640, 485)
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        panel = QWidget()
        panel.setObjectName('infoPanel')
        overview = QHBoxLayout(panel)
        overview.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.photo = make_label()
        self.photo.setObjectName('productPhoto')
        self.photo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo.setFixedSize(144, 144)
        overview.addWidget(self.photo, alignment=Qt.AlignmentFlag.AlignTop)

        fields = QFormLayout()
        fields.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        self.fields = {}
        for title in ('Наименование', 'Производство', 'Категория', 'Цена со скидкой',
                      'Состав', 'Описание', 'Размерный ряд'):
            label = make_label()
            fields.addRow(title, label)
            self.fields[title] = label
        overview.addLayout(fields, 1)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(panel)
        layout.addWidget(scroll, 1)

        selection = QFormLayout()
        self.size = QComboBox()
        selection.addRow('Доступные &размеры', self.size)
        self.quantity = QSpinBox()
        selection.addRow('&Количество пар', self.quantity)
        layout.addLayout(selection)
        self.notice = make_label()
        layout.addWidget(self.notice)

        actions = QDialogButtonBox()
        self.add_button = actions.addButton('Добавить в заказ', QDialogButtonBox.ButtonRole.AcceptRole)
        self.add_button.setProperty('primary', True)
        self.add_button.setDefault(True)
        actions.addButton('Закрыть', QDialogButtonBox.ButtonRole.RejectRole)
        self.add_button.clicked.connect(self.add_tovar)
        actions.rejected.connect(self.reject)
        layout.addWidget(actions)
        self.size.currentIndexChanged.connect(self.change_amount)

    def show_info(self, product_id, user, *, allow_order=True):
        try:
            with Session(self.database) as db:
                current = db.get(Product, product_id)
                if current is not None:
                    prices = get_prices(db, {current.id: current.price}, date.today())
        except SQLAlchemyError:
            QMessageBox.warning(self.parentWidget(), 'Карточка товара', 'Не удалось загрузить товар.')
            return
        if current is None:
            QMessageBox.information(self.parentWidget(), 'Карточка товара', 'Товар больше недоступен.')
            self.missing.emit()
            return
        self.tovar = current
        self.user = user
        self.can_order = user is not None and allow_order
        self.price = prices[current.id]
        self.fill()
        self.exec()

    def fill(self):
        tovar = self.tovar
        self.photo.setAccessibleName(f'Изображение товара: {tovar.name}')
        photo = load_photo(tovar, 144)
        if photo.isNull():
            self.photo.setText('Нет фото')
        else:
            self.photo.setPixmap(photo)

        category = tovar.subcathegory
        self.fields['Наименование'].setText(tovar.name)
        self.fields['Производство'].setText(tovar.manufacturer.title)
        self.fields['Категория'].setText(f'{category.cathegory.title} / {category.title}')
        self.fields['Цена со скидкой'].setText(format_price(self.price))
        self.fields['Состав'].setText(tovar.composition or '—')
        self.fields['Описание'].setText(tovar.description or '—')
        self.fill_sizes()

    def fill_sizes(self):
        sizes = {}
        stock = {}
        for row in self.tovar.stock:
            sizes[row.size_id] = row.size
            stock[row.size_id] = stock.get(row.size_id, 0) + max(row.amount, 0)

        sizes = sorted(sizes.values(), key=lambda size: size_order(size.title))
        titles = [size.title for size in sizes]
        self.fields['Размерный ряд'].setText(', '.join(titles) or '—')

        self.size.clear()
        self.size.addItem('Выберите размер')
        self.available = {}
        for size in sizes:
            amount = stock[size.id]
            added = self.cart.get((self.tovar.id, size.id))
            if added is not None:
                amount -= added.quantity
            if amount > 0:
                self.available[size.id] = amount
                self.size.addItem(size.title, size)

        has_sizes = self.size.count() > 1
        can_order = self.can_order and has_sizes
        self.size.setEnabled(can_order)
        self.quantity.setValue(1)
        self.change_amount()
        self.notice.setVisible(not can_order)
        if self.user is None:
            self.notice.setText('Войдите, чтобы добавить товар в заказ.')
        elif not self.can_order:
            self.notice.setText('Для оформления откройте «Заказы».')
        elif any(stock.values()):
            self.notice.setText('Доступные пары уже добавлены в заказ.')
        else:
            self.notice.setText('Нет размеров в наличии.')
        if can_order:
            self.size.setFocus()

    def change_amount(self):
        size = self.size.currentData()
        chosen = self.can_order and size is not None
        self.quantity.setRange(0, self.available[size.id] if chosen else 1)
        self.quantity.setEnabled(chosen)
        self.add_button.setEnabled(chosen)

    def add_tovar(self):
        size = self.size.currentData()
        if not self.can_order or size is None:
            return
        amount = self.quantity.value()
        if amount <= 0:
            QMessageBox.warning(self, 'Количество товара', 'Введите количество товара!')
            return

        try:
            with Session(self.database) as db:
                stock = db.scalar(select(func.sum(Stock.amount)).where(
                    Stock.product_id == self.tovar.id, Stock.size_id == size.id, Stock.amount > 0,
                )) or 0
        except SQLAlchemyError:
            QMessageBox.warning(self, 'Количество товара', 'Не удалось проверить остаток на складе.')
            return

        added = self.cart.get((self.tovar.id, size.id))
        available = max(stock - (added.quantity if added is not None else 0), 0)
        if amount > available:
            QMessageBox.warning(self, 'Количество товара', f'Максимально доступно для заказа: {available}')
            return

        self.add.emit(self.tovar, size, amount)
        self.accept()


class CartDialog(QDialog):
    changed = Signal()

    def __init__(self, database, user_id, cart, parent=None):
        super().__init__(parent)
        self.database = database
        self.user_id = user_id
        self.cart = cart
        self.order = None
        self.setWindowTitle('Оформление заказа')
        self.resize(720, 420)
        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(['Товар', 'Размер', 'Пар', 'Цена', 'Сумма'])
        self.table.setAccessibleName('Позиции заказа')
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().hide()
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        self.remove = QPushButton('Удалить позицию')
        self.remove.clicked.connect(self.remove_item)
        self.total = make_label()
        summary = QHBoxLayout()
        summary.addWidget(self.remove)
        summary.addStretch()
        summary.addWidget(self.total)
        layout.addLayout(summary)
        self.message = make_label()
        layout.addWidget(self.message)
        actions = QDialogButtonBox()
        self.confirm = actions.addButton('Подтвердить заказ', QDialogButtonBox.ButtonRole.AcceptRole)
        self.confirm.setProperty('primary', True)
        self.confirm.setAutoDefault(False)
        self.cancel = actions.addButton('Продолжить покупки', QDialogButtonBox.ButtonRole.RejectRole)
        actions.accepted.connect(self.save)
        actions.rejected.connect(self.reject)
        layout.addWidget(actions)
        self.table.itemSelectionChanged.connect(self.update_remove)
        self.fill()

    def fill(self):
        self.keys = list(self.cart)
        self.table.clearContents()
        self.table.setRowCount(len(self.keys))
        for row, key in enumerate(self.keys):
            line = self.cart[key]
            cells = (line.product_name, line.size, str(line.quantity),
                     format_price(line.unit_price), format_price(line.total))
            for column, value in enumerate(cells):
                self.table.setItem(row, column, QTableWidgetItem(value))
        self.table.resizeRowsToContents()
        self.total.setText(f'Итого: {format_price(sum(line.total for line in self.cart.values()))}')
        self.confirm.setEnabled(bool(self.cart))
        self.update_remove()

    def update_remove(self):
        self.remove.setEnabled(bool(self.table.selectedItems()))

    def remove_item(self):
        selected = self.table.selectedIndexes()
        if selected:
            del self.cart[self.keys[selected[0].row()]]
            self.message.clear()
            self.fill()
            self.changed.emit()

    def save(self):
        try:
            self.order = save_order(self.database, self.user_id, self.cart)
        except PricesChanged as error:
            for item in self.cart.values():
                item.unit_price = error.prices[item.product_id]
            self.fill()
            self.message.setText(str(error))
        except OrderError as error:
            self.message.setText(str(error))
        except SQLAlchemyError:
            self.message.setText('Не удалось сохранить заказ. Проверьте подключение к базе.')
        else:
            self.accept()


class NewOrderDialog(CartDialog):
    def __init__(self, database, user, parent=None):
        super().__init__(database, None, {}, parent)
        self.user = user
        self.setWindowTitle('Новый заказ')
        self.resize(720, 620)
        self.cancel.setText('Отмена')

        self.customer = QComboBox()
        self.customer.addItem('Выберите клиента')
        self.search = QLineEdit()
        self.search.setClearButtonEnabled(True)
        fields = QFormLayout()
        fields.addRow('&Клиент', self.customer)
        fields.addRow('&Поиск по названию', self.search)
        self.layout().insertLayout(0, fields)
        self.catalog = QListWidget()
        self.catalog.setAccessibleName('Каталог товаров')
        self.layout().insertWidget(1, self.catalog)
        self.open_product = QPushButton('Открыть товар')
        self.open_product.setAutoDefault(False)
        self.layout().insertWidget(2, self.open_product)

        with Session(database) as db:
            for customer in db.query(User).order_by(User.surname, User.name, User.id):
                if is_customer(customer):
                    self.customer.addItem(str(customer), customer.id)
            self.products = db.execute(select(Product.id, Product.name).order_by(Product.name, Product.id)).all()

        self.info = Info(database, self.cart, self)
        self.info.add.connect(self.add_product)
        self.search.textChanged.connect(self.filter_catalog)
        self.catalog.currentItemChanged.connect(self.update_product_button)
        self.catalog.itemActivated.connect(self.show_product)
        self.open_product.clicked.connect(self.show_product)
        self.filter_catalog()

    def filter_catalog(self):
        search = self.search.text().strip().casefold()
        self.catalog.clear()
        for product_id, name in self.products:
            if search in name.casefold():
                item = QListWidgetItem(name, self.catalog)
                item.setData(Qt.ItemDataRole.UserRole, product_id)
        self.catalog.setCurrentRow(0)
        self.update_product_button()

    def update_product_button(self):
        self.open_product.setEnabled(self.catalog.currentItem() is not None)

    def show_product(self):
        item = self.catalog.currentItem()
        if item is not None:
            self.info.show_info(item.data(Qt.ItemDataRole.UserRole), self.user)

    def add_product(self, product, size, quantity):
        add_to_cart(self.cart, product, size, quantity, self.info.price)
        self.message.clear()
        self.fill()

    def save(self):
        self.user_id = self.customer.currentData()
        if self.user_id is None:
            self.message.setText('Выберите клиента.')
            self.customer.setFocus()
            return
        super().save()


class OrdersDialog(QDialog):
    def __init__(self, database, user, parent=None):
        super().__init__(parent)
        self.database = database
        self.user = user
        self.changed = False
        self.setWindowTitle('Заказы')
        self.resize(660, 420)
        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(['№', 'Дата заказа', 'ФИО клиента'])
        self.table.setAccessibleName('Список заказов')
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().hide()
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(True)
        layout.addWidget(self.table)
        self.message = make_label()
        layout.addWidget(self.message)

        actions = QDialogButtonBox()
        self.add_button = actions.addButton('Добавить заказ', QDialogButtonBox.ButtonRole.ActionRole)
        self.add_button.setProperty('primary', True)
        self.remove_button = actions.addButton('Удалить заказ', QDialogButtonBox.ButtonRole.ActionRole)
        self.remove_button.setEnabled(False)
        actions.addButton('Закрыть', QDialogButtonBox.ButtonRole.RejectRole)
        actions.rejected.connect(self.reject)
        self.add_button.clicked.connect(self.add_order)
        self.remove_button.clicked.connect(self.remove_order)
        self.table.itemSelectionChanged.connect(self.update_remove)
        layout.addWidget(actions)
        self.load_orders()

    def load_orders(self):
        try:
            with Session(self.database) as db:
                orders = db.execute(
                    select(Order.id, Order.order_date, User.surname, User.name, User.patronymic)
                    .join(User, Order.user_id == User.id).order_by(Order.order_date.desc(), Order.id.desc())
                ).all()
        except SQLAlchemyError:
            self.message.setText('Не удалось загрузить список заказов.')
            return False

        self.table.clearContents()
        self.table.setRowCount(len(orders))
        for row, (order_id, order_date, *name) in enumerate(orders):
            for column, value in enumerate((str(order_id), order_date.strftime('%d.%m.%Y'), ' '.join(filter(None, name)))):
                self.table.setItem(row, column, QTableWidgetItem(value))
        self.message.setText('' if orders else 'Заказов пока нет.')
        self.update_remove()
        return True

    def update_remove(self):
        self.remove_button.setEnabled(bool(self.table.selectedItems()))

    def add_order(self):
        try:
            dialog = NewOrderDialog(self.database, self.user, self)
        except SQLAlchemyError:
            self.message.setText('Не удалось загрузить клиентов и товары.')
            return
        accepted = dialog.exec() == QDialog.DialogCode.Accepted
        order = dialog.order
        dialog.deleteLater()
        if accepted:
            self.changed = True
            if self.load_orders():
                self.message.setText(f'Заказ №{order[0]} оформлен.')

    def remove_order(self):
        item = self.table.item(self.table.currentRow(), 0)
        if item is None:
            return
        order_id = int(item.text())
        answer = QMessageBox.question(self, 'Удаление заказа', f'Удалить заказ №{order_id} и вернуть пары на склад?',
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                      QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            delete_order(self.database, order_id)
        except OrderError as error:
            self.load_orders()
            self.message.setText(str(error))
        except SQLAlchemyError:
            self.message.setText('Не удалось удалить заказ.')
        else:
            self.changed = True
            if self.load_orders():
                self.message.setText(f'Заказ №{order_id} удалён.')
