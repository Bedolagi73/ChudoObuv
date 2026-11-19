from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLabel, QLineEdit
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models import User, engine


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Вход в аккаунт")
        self.setMinimumWidth(340)
        self.user_id = None
        self.user_name = None

        self.login = QLineEdit(self)
        self.error_label = QLabel(self)
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        self.login.textEdited.connect(self.error_label.hide)

        buttons = QDialogButtonBox(self)
        sign_in_button = buttons.addButton("Войти", QDialogButtonBox.ButtonRole.AcceptRole)
        sign_in_button.setDefault(True)
        buttons.addButton("Отмена", QDialogButtonBox.ButtonRole.RejectRole)
        buttons.accepted.connect(self.check_credentials)
        buttons.rejected.connect(self.reject)

        layout = QFormLayout(self)
        layout.addRow("Логин", self.login)
        layout.addRow(self.error_label)
        layout.addRow(buttons)
        self.login.setFocus()

    def check_credentials(self):
        login = self.login.text().strip()
        if not login:
            self.show_error("Введите логин.")
            self.login.setFocus()
            return

        query = (
            select(User.id, User.surname, User.name, User.patronymic)
            .where(User.user_login == login)
            .limit(1)
        )
        try:
            with Session(engine) as db:
                name_parts = db.execute(query).first()
        except SQLAlchemyError:
            self.show_error("Не удалось подключиться к базе данных. Попробуйте ещё раз.")
            return

        if name_parts is None:
            self.show_error("Пользователь с таким логином не найден.")
            self.login.setFocus()
            self.login.selectAll()
            return

        self.user_id, *name_parts = name_parts
        self.user_name = " ".join(part for part in name_parts if part) or login
        self.accept()

    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()
