"""Assign a password to an existing account without putting it in shell history."""
import argparse
from getpass import getpass

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models import engine, User


def main():
    parser = argparse.ArgumentParser(description='Назначить пароль существующему пользователю')
    parser.add_argument('login', help='Логин из таблицы users')
    args = parser.parse_args()
    password = getpass('Новый пароль: ')
    confirmation = getpass('Повторите пароль: ')
    if not password:
        parser.error('Пароль не должен быть пустым.')
    if password != confirmation:
        parser.error('Пароли не совпадают.')
    try:
        with Session(engine) as db:
            user = db.query(User).filter(User.user_login == args.login.strip()).one_or_none()
            if user is None:
                parser.error('Пользователь не найден. Сначала импортируйте пользователей.')
            user.set_password(password)
            db.commit()
    except SQLAlchemyError:
        parser.exit(1, 'Не удалось сохранить пароль. Проверьте подключение к базе данных.\n')
    print('Пароль сохранён.')


if __name__ == '__main__':
    main()
