import re
from collections import Counter
from dataclasses import replace

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QPushButton, QScrollArea, QSpinBox, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)
from sqlalchemy.exc import SQLAlchemyError

from auth import AuthError, authenticate
from orders import CartLine, OrderError, PricesChanged, format_price, place_order
from tovar import product_photo


def text_label(value=''):
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
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setMaxLength(256)
        form.addRow('&Логин', self.login)
        form.addRow('&Пароль', self.password)
        self.message = text_label()
        form.addRow(self.message)
        actions = QDialogButtonBox()
        submit = actions.addButton('Войти', QDialogButtonBox.ButtonRole.AcceptRole)
        submit.setDefault(True)
        actions.addButton('Отмена', QDialogButtonBox.ButtonRole.RejectRole)
        actions.accepted.connect(self.sign_in)
        actions.rejected.connect(self.reject)
        form.addRow(actions)
        self.login.setFocus()

    def sign_in(self):
        login, password = self.login.text().strip(), self.password.text()
        if not login or not password:
            self.message.setText('Введите логин и пароль.')
            (self.password if login else self.login).setFocus()
            return
        try:
            user = authenticate(self.database, login, password)
        except AuthError as error:
            self.message.setText(str(error))
            return
        except SQLAlchemyError:
            self.message.setText('Не удалось выполнить вход. Проверьте подключение к базе.')
            return
        if user is None:
            self.message.setText('Неверный логин или пароль.')
            self.password.clear()
            self.password.setFocus()
            return
        self.user = user
        self.password.clear()
        self.accept()


def size_order(title):
    if re.fullmatch(r'[0-9]+(?:[,.][0-9]+)?', title):
        return (0, float(title.replace(',', '.')))
    return (1, title.casefold())


class ProductDialog(QDialog):
    def __init__(self, product, price, cart, parent=None):
        super().__init__(parent)
        self.product = product
        self.price = price
        self.line = None
        self.setWindowTitle('Карточка товара')
        self.resize(640, 485)
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        panel = QWidget()
        overview = QHBoxLayout(panel)
        overview.setAlignment(Qt.AlignmentFlag.AlignTop)
        photo = text_label('Нет фото')
        photo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        photo.setAccessibleName(f'Изображение товара: {product.name}')
        photo.setFixedSize(144, 144)
        photo.setStyleSheet('background: #D2F6E7; color: #172F2C;')
        pixmap = product_photo(product, 144)
        if not pixmap.isNull():
            photo.setPixmap(pixmap)
        overview.addWidget(photo, alignment=Qt.AlignmentFlag.AlignTop)

        fields = QFormLayout()
        fields.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        fields.addRow('Наименование', text_label(product.name))
        fields.addRow('Производство', text_label(product.manufacturer.title))
        category = product.subcathegory
        fields.addRow('Категория', text_label(f'{category.cathegory.title} / {category.title}'))
        fields.addRow('Цена со скидкой', text_label(format_price(price)))
        fields.addRow('Состав', text_label(product.composition or '—'))
        fields.addRow('Описание', text_label(product.description or '—'))
        overview.addLayout(fields, 1)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(panel)
        layout.addWidget(scroll, 1)

        titles = {}
        stock = Counter()
        for row in product.stock:
            titles[row.size_id] = row.size.title
            stock[row.size_id] += max(row.amount, 0)
        sizes = sorted(titles, key=lambda size_id: size_order(titles[size_id]))
        available = [f'{titles[size_id]} — {stock[size_id]}' for size_id in sizes if stock[size_id]]
        fields.addRow('Размерный ряд', text_label(', '.join(titles[i] for i in sizes) or '—'))
        fields.addRow('Доступно для заказа (пар)', text_label(', '.join(available) or 'Нет в наличии'))

        selection = QFormLayout()
        self.size = QComboBox()
        self.size.addItem('Выберите размер', None)
        for size_id in sizes:
            added = cart.get((product.id, size_id))
            remaining = stock[size_id] - (added.quantity if added else 0)
            if remaining > 0:
                self.size.addItem(f'{titles[size_id]} · доступно {remaining}', (size_id, titles[size_id], remaining))
        self.size.setEnabled(self.size.count() > 1)
        selection.addRow('&Размер', self.size)
        self.quantity = QSpinBox()
        selection.addRow('&Количество пар', self.quantity)
        layout.addLayout(selection)
        if self.size.count() == 1:
            message = 'Доступные пары уже добавлены в заказ.' if available else 'Добавить товар пока нельзя.'
            layout.addWidget(text_label(message))

        actions = QDialogButtonBox()
        self.add_button = actions.addButton('Добавить в заказ', QDialogButtonBox.ButtonRole.AcceptRole)
        self.add_button.setDefault(True)
        self.add_button.setStyleSheet(
            'QPushButton:enabled { background: #70B2AF; color: #172F2C; }'
            'QPushButton:focus { border: 2px solid #172F2C; }'
        )
        actions.addButton('Закрыть', QDialogButtonBox.ButtonRole.RejectRole)
        actions.accepted.connect(self.add_to_cart)
        actions.rejected.connect(self.reject)
        layout.addWidget(actions)
        self.size.currentIndexChanged.connect(self.update_quantity)
        self.update_quantity()

    def update_quantity(self):
        size = self.size.currentData()
        self.quantity.setRange(1, size[2] if size else 1)
        self.quantity.setEnabled(size is not None)
        self.add_button.setEnabled(size is not None)

    def add_to_cart(self):
        size = self.size.currentData()
        if size is not None:
            size_id, title, _ = size
            self.line = CartLine(self.product.id, size_id, self.product.name, title,
                                 self.price, self.quantity.value())
            self.accept()


class CartDialog(QDialog):
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
        self.remove.clicked.connect(self.remove_line)
        self.total = text_label()
        summary = QHBoxLayout()
        summary.addWidget(self.remove)
        summary.addStretch()
        summary.addWidget(self.total)
        layout.addLayout(summary)
        self.message = text_label()
        layout.addWidget(self.message)
        actions = QDialogButtonBox()
        self.confirm = actions.addButton('Подтвердить заказ', QDialogButtonBox.ButtonRole.AcceptRole)
        self.confirm.setAutoDefault(False)
        actions.addButton('Продолжить покупки', QDialogButtonBox.ButtonRole.RejectRole)
        actions.accepted.connect(self.submit)
        actions.rejected.connect(self.reject)
        layout.addWidget(actions)
        self.table.itemSelectionChanged.connect(self.update_selection)
        self.render_cart()

    def render_cart(self):
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
        self.update_selection()

    def update_selection(self):
        self.remove.setEnabled(bool(self.table.selectedItems()))

    def remove_line(self):
        selected = self.table.selectedIndexes()
        if selected:
            del self.cart[self.keys[selected[0].row()]]
            self.message.clear()
            self.render_cart()

    def submit(self):
        try:
            self.order = place_order(self.database, self.user_id, self.cart)
        except PricesChanged as error:
            for key, line in self.cart.items():
                self.cart[key] = replace(line, unit_price=error.prices[line.product_id])
            self.render_cart()
            self.message.setText(str(error))
        except OrderError as error:
            self.message.setText(str(error))
        except SQLAlchemyError:
            self.message.setText('Не удалось сохранить заказ. Проверьте подключение к базе.')
        else:
            self.accept()
