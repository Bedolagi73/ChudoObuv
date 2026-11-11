import sys
from PySide6.QtWidgets import QApplication, QWidget, QListWidgetItem
from ui_form import Ui_Widget
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, QSignalBlocker
from sqlalchemy.orm import Session
from models import create, engine, Product
from tovar import Tovar


class Widget(QWidget):
    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)
        self.user = None
        self.ui.comboBox.addItem('Сортировка: по умолчанию', None)
        self.ui.comboBox.addItem('Цена: по возрастанию', 'asc')
        self.ui.comboBox.addItem('Цена: по убыванию', 'desc')
        self.ui.comboBox.setAccessibleName('Сортировка товаров по цене')
        self.ui.comboBox.currentIndexChanged.connect(self.load_tovars)
        # загружаем логотип фирмы
        self.setWindowIcon(QIcon('import/Чудо Обувь.ico'))
        # создаем таблицы (если их ещё нет)
        create()

        self.set_user(user)

    # передаём пользователя после успешного входа; None означает гостя
    def set_user(self, user):
        self.user = user
        self.ui.label.setText(str(user) if user is not None else 'Неавторизованный пользователь')
        self.ui.comboBox.setEnabled(user is not None)
        self.ui.comboBox.setToolTip(
            'Выберите порядок цены' if user is not None else 'Для сортировки войдите в аккаунт'
        )
        # при смене пользователя сбрасываем сортировку и обновляем список один раз
        with QSignalBlocker(self.ui.comboBox):
            self.ui.comboBox.setCurrentIndex(0)
        self.load_tovars()

    # загружаем список товаров
    def load_tovars(self):
        # очистка списка
        self.ui.listWidget.clear()

        # получаем список товаров
        with Session(engine) as db:
            query = db.query(Product)
            # проверяем пользователя и здесь: одного отключения списка недостаточно
            sort = self.ui.comboBox.currentData() if self.user is not None else None
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
    from login import Login

    app = QApplication(sys.argv)
    login = Login()
    login.show()
    sys.exit(app.exec())
