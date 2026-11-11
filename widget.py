import sys
from PySide6.QtWidgets import QApplication, QWidget, QListWidgetItem
from ui_form import Ui_Widget
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
from sqlalchemy.orm import Session
from models import create, engine, Product
from tovar import Tovar


class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)
        # загружаем логотип фирмы
        self.setWindowIcon(QIcon('import/Чудо Обувь.ico'))
        # создаем таблицы (если их ещё нет)
        create()

        # загружаем товары
        self.load_tovars()

    # загружаем список товаров
    def load_tovars(self):
        # очистка списка
        self.ui.listWidget.clear()

        # получаем список товаров
        with Session(engine) as db:
            tovary = db.query(Product).order_by(Product.id).all()
            for t in tovary:
                tovar = Tovar(t, self)
                # создаем стандартный контейнер-строку для списка
                item = QListWidgetItem(self.ui.listWidget)
                item.setSizeHint(QSize(0, 125))
                self.ui.listWidget.setItemWidget(item, tovar)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
