import sys
from pathlib import Path

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models import engine, User

BASE_DIR = Path(__file__).resolve().parent


class Login(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Чудо Обувь — вход')
        self.ui = QUiLoader().load(str(BASE_DIR / 'login.ui'), self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        self.resize(420, 340)
        self.catalog = None
        self.ui.loginButton.clicked.connect(self.sign_in)
        self.ui.guestButton.clicked.connect(self.enter_as_guest)
        self.ui.loginEdit.returnPressed.connect(self.sign_in)
        self.ui.passwordEdit.returnPressed.connect(self.sign_in)
        self.ui.loginEdit.setFocus()

    def sign_in(self):
        self.ui.errorLabel.clear()
        username = self.ui.loginEdit.text().strip()
        password = self.ui.passwordEdit.text()
        if not username or not password:
            self.ui.errorLabel.setText('Введите логин и пароль.')
            (self.ui.loginEdit if not username else self.ui.passwordEdit).setFocus()
            return
        try:
            with Session(engine) as db:
                user = db.query(User).filter(User.user_login == username).one_or_none()
                if user is None or not user.check_password(password):
                    self.ui.errorLabel.setText('Неверный логин или пароль.')
                    self.ui.passwordEdit.clear()
                    self.ui.passwordEdit.setFocus()
                    return
        except SQLAlchemyError:
            self.ui.errorLabel.setText('Не удалось выполнить вход. Проверьте подключение к базе данных.')
            return
        self._open_catalog(user)

    def enter_as_guest(self):
        self.ui.errorLabel.clear()
        self._open_catalog(None)

    def _open_catalog(self, user):
        from widget import Widget

        try:
            catalog = Widget(user=user)
        except SQLAlchemyError:
            self.ui.errorLabel.setText('Не удалось загрузить каталог. Проверьте подключение к базе данных.')
            return
        self.catalog = catalog
        self.ui.passwordEdit.clear()
        self.catalog.show()
        self.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login = Login()
    login.show()
    sys.exit(app.exec())
