import argparse
from getpass import getpass
from hashlib import pbkdf2_hmac
from hmac import compare_digest
from secrets import token_bytes

from sqlalchemy import inspect, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models import User, UserCredential, config_error, engine

ROUNDS = 600_000


class AuthError(ValueError):
    pass


def password_digest(password, salt):
    return pbkdf2_hmac('sha256', password.encode('utf-8'), salt, ROUNDS)


def authenticate(database, login, password):
    with Session(database) as db:
        if not inspect(db.connection()).has_table(UserCredential.__tablename__):
            raise AuthError('Вход ещё не настроен. Попросите администратора назначить пароль.')
        matches = db.execute(
            select(User, UserCredential.password_hash)
            .outerjoin(UserCredential, UserCredential.user_id == User.id)
            .where(User.user_login == login)
            .limit(2)
        ).unique().all()
        if len(matches) != 1:
            return None
        user, encoded = matches[0]
        if encoded is None:
            return None
        try:
            salt, expected = (bytes.fromhex(part) for part in encoded.split('$'))
        except ValueError:
            return None
        if len(salt) == 16 and len(expected) == 32:
            if compare_digest(password_digest(password, salt), expected):
                return user
        return None


def set_password(database, login, password):
    if not 8 <= len(password) <= 256:
        raise AuthError('Пароль должен содержать от 8 до 256 символов.')
    with Session(database) as db, db.begin():
        ids = db.scalars(select(User.id).where(User.user_login == login).limit(2)).all()
        if len(ids) != 1:
            raise AuthError('Укажите логин, который принадлежит ровно одному пользователю.')
        UserCredential.__table__.create(db.connection(), checkfirst=True)
        salt = token_bytes(16)
        digest = password_digest(password, salt)
        db.merge(UserCredential(user_id=ids[0], password_hash=f'{salt.hex()}${digest.hex()}'))


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
