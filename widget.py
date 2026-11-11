import sys
from PySide6.QtWidgets import QApplication, QWidget, QListWidgetItem, QMessageBox
from ui_form import Ui_Widget
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import create, engine, Product, DatabaseConfigError, ENV_FILE
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
        # загружаем логотип фирмы
        self.setWindowIcon(QIcon('import/Чудо Обувь.ico'))
        # создаем таблицы (если их ещё нет)
        create()

        self.load_tovars()

    # загружаем список товаров
    def load_tovars(self):
        # очистка списка
        self.ui.listWidget.clear()

        # получаем список товаров
        with Session(engine) as db:
            query = db.query(Product)
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
