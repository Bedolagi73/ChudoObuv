import sys
from PySide6.QtWidgets import QApplication, QWidget, QListWidgetItem, QMessageBox
from ui_form import Ui_Widget
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, QTimer
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import engine, Product, DatabaseConfigError, ENV_FILE, config_error
from tovar import Tovar


class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)
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
        # загружаем логотип фирмы
        self.setWindowIcon(QIcon('import/Чудо Обувь.ico'))
        if engine is None:
            raise DatabaseConfigError(config_error)

        self.load_tovars()

    # загружаем список товаров
    def load_tovars(self):
        self.search_timer.stop()
        # очистка списка
        self.ui.listWidget.clear()

        # получаем список товаров
        with Session(engine) as db:
            query = db.query(Product)
            search = self.ui.lineEdit.text().strip()
            if search:
                query = query.filter(or_(
                    Product.name.icontains(search, autoescape=True),
                    Product.description.icontains(search, autoescape=True),
                ))
            sort = self.ui.comboBox.currentData()
            if sort == 'asc':
                query = query.order_by(Product.price.asc().nulls_last(), Product.id)
            elif sort == 'desc':
                query = query.order_by(Product.price.desc().nulls_last(), Product.id)
            else:
                query = query.order_by(Product.id)
            tovary = query.all()
            for t in tovary:
                tovar = Tovar(t, self)
                # создаем стандартный контейнер-строку для списка
                item = QListWidgetItem(self.ui.listWidget)
                item.setSizeHint(QSize(0, 125))
                self.ui.listWidget.setItemWidget(item, tovar)


if __name__ == "__main__":
    app = QApplication(sys.argv)
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
