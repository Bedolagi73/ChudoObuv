from sqlalchemy.orm import Session

from models import User


def role_name(user):
    return user.role.title.strip().casefold() if user is not None and user.role is not None else ''


def is_customer(user):
    return role_name(user) == 'авторизованный пользователь'


def can_manage_orders(user):
    return role_name(user) in {'администратор', 'менеджер'}


def find_user(database, login):
    with Session(database) as db:
        users = db.query(User).filter(User.user_login == login).limit(2).all()
        if len(users) == 1:
            return users[0]
    return None
