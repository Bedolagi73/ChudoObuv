from sqlalchemy.orm import Session

from models import User


def find_user(database, login):
    with Session(database) as db:
        users = db.query(User).filter(User.user_login == login).limit(2).all()
        if len(users) == 1:
            return users[0]
    return None
