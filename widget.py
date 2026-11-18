import sys
from datetime import date

from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QHBoxLayout, QLabel,
                               QListWidgetItem, QMessageBox, QPushButton, QWidget)
from ui_form import Ui_Widget
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtCore import QSize, Qt, QTimer
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import engine, Product, Cathegory, Subcathegory, DatabaseConfigError, ENV_FILE, config_error
from order_dialogs import CartDialog, Info, LoginDialog
from orders import get_prices
from tovar import BASE_DIR, Tovar

IMPORT_DIR = BASE_DIR / 'import'


def set_style(app):
    app.setStyle('Fusion')
    app.styleHints().setColorScheme(Qt.ColorScheme.Light)
    app.setFont(QFont('Calibri', 11))
    app.setStyleSheet((BASE_DIR / 'style.qss').read_text(encoding='utf-8'))
    icon = IMPORT_DIR / 'Чудо Обувь.ico'
    if icon.is_file():
        app.setWindowIcon(QIcon(str(icon)))


class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)
        self.user = None
        self.cart = {}
        self.info_window = None
        self.make_buttons()
        self.ui.comboBox.addItem('Сортировка: по умолчанию', None)
        self.ui.comboBox.addItem('Цена: по возрастанию', 'asc')
        self.ui.comboBox.addItem('Цена: по убыванию', 'desc')
        self.ui.comboBox.setAccessibleName('Сортировка товаров по цене')
        self.ui.comboBox.setToolTip('Выберите порядок цены')
        self.ui.comboBox.currentIndexChanged.connect(self.load_tovars)
        # ищем после небольшой паузы, а не отправляем запрос на каждую букву
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(300)
        self.search_timer.timeout.connect(self.load_tovars)
        self.ui.lineEdit.textChanged.connect(lambda _text: self.search_timer.start())
        if engine is None:
            raise DatabaseConfigError(config_error)

        self.ui.categoryComboBox.addItem('Все категории', None)
        with Session(engine) as db:
            categories = db.query(Cathegory).order_by(Cathegory.title, Cathegory.id).all()
            for category in categories:
                self.ui.categoryComboBox.addItem(category.title, category.id)
        self.ui.categoryComboBox.currentIndexChanged.connect(self.load_tovars)
        self.load_tovars(startup=True)

    def make_buttons(self):
        self.ui.gridLayout.removeWidget(self.ui.label)
        self.ui.gridLayout.removeItem(self.ui.horizontalSpacer)
        bar = QFrame()
        bar.setObjectName('catalogHeader')
        header = QHBoxLayout(bar)
        logo = QPixmap(str(IMPORT_DIR / 'logo.png'))
        if not logo.isNull():
            logo_label = QLabel()
            logo_label.setAccessibleName('Логотип Чудо Обувь')
            logo_label.setPixmap(logo.scaled(128, 56, Qt.AspectRatioMode.KeepAspectRatio,
                                             Qt.TransformationMode.SmoothTransformation))
            header.addWidget(logo_label)
        self.ui.label.setObjectName('catalogTitle')
        header.addWidget(self.ui.label)
        header.addStretch()
        self.account = QLabel()
        self.account.setTextFormat(Qt.TextFormat.PlainText)
        header.addWidget(self.account)
        self.login_button = QPushButton()
        self.login_button.clicked.connect(self.change_user)
        header.addWidget(self.login_button)
        self.cart_button = QPushButton()
        self.cart_button.setProperty('primary', True)
        self.cart_button.clicked.connect(self.open_cart)
        header.addWidget(self.cart_button)
        self.ui.gridLayout.addWidget(bar, 0, 0, 1, 2)

        self.open_button = QPushButton('Открыть товар')
        self.open_button.clicked.connect(self.show_selected)
        self.ui.controlsLayout.insertWidget(self.ui.controlsLayout.count() - 1, self.open_button)
        self.ui.listWidget.itemClicked.connect(self.showInfo)
        self.ui.listWidget.currentItemChanged.connect(self.update_buttons)
        self.update_buttons()

    def update_buttons(self):
        logged_in = self.user is not None
        self.account.setText(str(self.user) if logged_in else 'Гость')
        self.login_button.setText('Выйти' if logged_in else 'Войти')
        self.cart_button.setText(f'Заказ ({sum(line.quantity for line in self.cart.values())})')
        self.cart_button.setEnabled(logged_in)
        self.open_button.setEnabled(logged_in and self.ui.listWidget.currentItem() is not None)
        self.open_button.setToolTip('' if logged_in else 'Войдите, чтобы открыть товар и оформить заказ')

    def change_user(self):
        if self.user is not None:
            if self.cart:
                answer = QMessageBox.question(
                    self, 'Выход', 'При выходе текущий заказ будет очищен. Выйти?',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if answer != QMessageBox.StandardButton.Yes:
                    return
            self.user = None
            self.cart.clear()
        else:
            dialog = LoginDialog(engine, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.user = dialog.user
            dialog.deleteLater()
        self.update_buttons()

    def show_selected(self):
        self.show_info(self.ui.listWidget.currentItem())

    def show_info(self, item):
        if self.user is None or item is None:
            return
        # Окно создаём при первом открытии карточки.
        if self.info_window is None:
            self.info_window = Info(engine, self.cart, self)
            self.info_window.added.connect(self.update_buttons)
            self.info_window.missing.connect(self.load_tovars)
        tovar = self.ui.listWidget.itemWidget(item)
        if tovar:
            self.info_window.show_info(tovar.tovar)

    showInfo = show_info

    def open_cart(self):
        if self.user is None:
            return
        dialog = CartDialog(engine, self.user.id, self.cart, self)
        accepted = dialog.exec() == QDialog.DialogCode.Accepted
        order = dialog.order
        dialog.deleteLater()
        if accepted:
            order_id, order_date = order
            self.cart.clear()
            self.load_tovars()
            QMessageBox.information(self, 'Заказ оформлен', f'Заказ №{order_id} от {order_date:%d.%m.%Y}')
        self.update_buttons()

    def load_tovars(self, *, startup=False):
        self.search_timer.stop()
        try:
            with Session(engine) as db:
                query = db.query(Product)
                category_id = self.ui.categoryComboBox.currentData()
                if category_id is not None:
                    query = query.join(Product.subcathegory).filter(
                        Subcathegory.cathegory_id == category_id
                    )
                search = self.ui.lineEdit.text().strip()
                if search:
                    query = query.filter(or_(
                        Product.name.icontains(search, autoescape=True),
                        Product.description.icontains(search, autoescape=True),
                    ))
                products = query.order_by(Product.id).all()
                base_prices = {product.id: product.price for product in products}
                prices = get_prices(db, base_prices, date.today())
        except SQLAlchemyError:
            if startup:
                raise
            QMessageBox.warning(self, 'Каталог', 'Не удалось обновить список товаров.')
            return
        sort = self.ui.comboBox.currentData()
        if sort:
            products.sort(key=lambda product: prices[product.id], reverse=sort == 'desc')
        self.ui.listWidget.clear()
        for product in products:
            item = QListWidgetItem(self.ui.listWidget)
            item.setSizeHint(QSize(0, 125))
            self.ui.listWidget.setItemWidget(item, Tovar(product, prices[product.id]))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    set_style(app)
    try:
        widget = Widget()
    except (DatabaseConfigError, SQLAlchemyError) as error:
        message = str(error) if isinstance(error, DatabaseConfigError) else (
            'Не удалось подключиться к PostgreSQL. Проверьте сервер, порт, имя базы, '
            'логин и пароль в DATABASE_URL. Убедитесь, что сервер доступен.'
        )
        QMessageBox.critical(None, 'Подключение к базе данных', f'{message}\n\nФайл настройки: {ENV_FILE}')
        sys.exit(1)
    widget.show()
    sys.exit(app.exec())
