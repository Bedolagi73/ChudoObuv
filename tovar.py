from pathlib import Path

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

BASE_DIR = Path(__file__).resolve().parent


class Tovar(QWidget):
    def __init__(self, tovar, main_window, parent=None):
        super().__init__(parent)
        # загружаем UI
        loader = QUiLoader()
        self.ui = loader.load(str(BASE_DIR / "tovar.ui"), self)
        # компоновщик: форма растягивается вместе со строкой списка
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        # запоминаем ссылку на родительское окно
        self.main_window = main_window
        # сохраняем переданный товар
        self.tovar = tovar

        # заполняем поля формы
        self.ui.label_2.setText(f'{tovar.manufacturer.title} | {tovar.name}')
        # категория — через подкатегорию (новая связь в БД)
        self.ui.label_3.setText(f'Категория: {tovar.subcathegory.cathegory.title} / {tovar.subcathegory.title}')
        # количество — сумма остатков по всем размерам
        amount = sum(s.amount or 0 for s in tovar.stock)
        self.ui.label_4.setText(f'Количество на складе: {amount}')
        self.ui.label_5.setText(f'Состав: {tovar.composition}')
        self.ui.label_6.setText(f'{tovar.price} ₽')

        # в БД хранится имя файла; фотографии лежат в import/images
        photo = QPixmap(str(BASE_DIR / "import" / "images" / (tovar.image or "")))
        if photo.isNull():
            # поддерживаем и прежнее расположение файлов прямо в import
            photo = QPixmap(str(BASE_DIR / "import" / (tovar.image or "")))
        if photo.isNull():
            self.ui.label.setText("Нет фото")
        else:
            self.ui.label.setPixmap(photo.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio,
                                                 Qt.TransformationMode.SmoothTransformation))
