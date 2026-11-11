import sys
import datetime
from PySide6.QtWidgets import QApplication, QWidget, QListWidgetItem, QMessageBox
from ui_form import Ui_Widget
from PySide6.QtGui import QIcon, QPixmap, QFont
from PySide6.QtCore import QSize, Qt
from sqlalchemy.orm import Session
from models import create, engine, Product, Order, Product_tovar
from tovar import Tovar


# id товаров, которые заказывали в предыдущем календарном месяце
def ordered_last_month(db, today=None):
    today = today or datetime.date.today()
    month_start = today.replace(day=1)
    prev_start = (month_start - datetime.timedelta(days=1)).replace(day=1)
    rows = (db.query(Product_tovar.product_id).join(Order, Order.id == Product_tovar.order_id)
            .filter(Order.order_date >= prev_start, Order.order_date < month_start).distinct())
    return {product_id for (product_id,) in rows}


class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)
        # иконка приложения
        self.setWindowIcon(QIcon('import/images/Чудо Обувь.ico'))
        # логотип: только уменьшаем по высоте, пропорции и цвет не меняются
        logo = QPixmap('import/images/Чудо Обувь.png')
        if not logo.isNull():
            self.ui.logo.setPixmap(logo.scaledToHeight(50, Qt.TransformationMode.SmoothTransformation))
        try:
            # создаем таблицы (если их ещё нет)
            create()
            # загружаем товары
            self.load_tovars()
        except Exception as e:
            # нет связи с БД — сообщение вместо аварийного завершения
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить товары:\n{e}")

    # загружаем список товаров
    def load_tovars(self, today=None):
        # очистка списка
        self.ui.listWidget.clear()

        # получаем список товаров
        with Session(engine) as db:
            ordered = ordered_last_month(db, today)
            tovary = db.query(Product).order_by(Product.id).all()
            for t in tovary:
                tovar = Tovar(t, self, t.id not in ordered)
                # создаем стандартный контейнер-строку для списка
                item = QListWidgetItem(self.ui.listWidget)
                item.setSizeHint(QSize(0, 150))
                self.ui.listWidget.setItemWidget(item, tovar)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # шрифт Calibri для всех окон приложения
    app.setFont(QFont("Calibri", 11))
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
