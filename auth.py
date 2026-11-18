import argparse
from getpass import getpass
from hashlib import pbkdf2_hmac
from hmac import compare_digest
from secrets import token_bytes

from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models import User, UserCredential, config_error, engine

ROUNDS = 600_000


class AuthError(ValueError):
    pass


def hash_password(password, salt):
    return pbkdf2_hmac('sha256', password.encode('utf-8'), salt, ROUNDS)


def find_user(db, login):
    users = db.query(User).filter(User.user_login == login).limit(2).all()
    if len(users) == 1:
        return users[0]
    return None


def check_login(database, login, password):
    with Session(database) as db:
        if not inspect(db.connection()).has_table(UserCredential.__tablename__):
            raise AuthError('Вход ещё не настроен. Попросите администратора назначить пароль.')
        user = find_user(db, login)
        if user is None:
            return None
        entry = db.get(UserCredential, user.id)
        if entry is None:
            return None

    try:
        salt, digest = entry.password_hash.split('$', 1)
        salt = bytes.fromhex(salt)
        digest = bytes.fromhex(digest)
    except ValueError:
        return None
    if len(salt) != 16 or len(digest) != 32:
        return None
    if compare_digest(hash_password(password, salt), digest):
        return user
    return None


def set_password(database, login, password):
    if not 8 <= len(password) <= 256:
        raise AuthError('Пароль должен содержать от 8 до 256 символов.')
    with Session(database) as db:
        user = find_user(db, login)
        if user is None:
            raise AuthError('Укажите логин, который принадлежит ровно одному пользователю.')
        UserCredential.__table__.create(db.connection(), checkfirst=True)
        entry = db.get(UserCredential, user.id)
        if entry is None:
            entry = UserCredential(user_id=user.id)
            db.add(entry)
        salt = token_bytes(16)
        digest = hash_password(password, salt)
        entry.password_hash = f'{salt.hex()}${digest.hex()}'
        db.commit()


def main():
    parser = argparse.ArgumentParser(description='Назначить пароль существующему пользователю каталога.')
    parser.add_argument('login', help='Логин из таблицы пользователей')
    login = parser.parse_args().login.strip()
    if engine is None:
        parser.exit(1, f'{config_error}\n')
    password = getpass('Новый пароль: ')
    if password != getpass('Повторите пароль: '):
        parser.exit(1, 'Пароли не совпадают.\n')
    try:
        set_password(engine, login, password)
    except AuthError as error:
        parser.exit(1, f'{error}\n')
    except SQLAlchemyError:
        parser.exit(1, 'Не удалось сохранить пароль. Проверьте подключение и права в базе.\n')
    print('Пароль назначен.')


if __name__ == '__main__':
    main()
