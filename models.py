# This Python file uses the following encoding: utf-8
import os
import hashlib
import hmac

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import declarative_base, relationship

engine = create_engine(
    os.environ.get("DATABASE_URL", "postgresql+psycopg://localhost/TufliBatinkoKrosovki"),
    connect_args={"connect_timeout": 5},
)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    patronymic = Column(String)
    user_login = Column(String, nullable=False)
    user_pas = Column(String)  # хеш пароля; в Users_import паролей нет
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    role = relationship("Role", back_populates="users", lazy="joined")

    def __str__(self):
        return f'{self.surname} {self.name} {self.patronymic}'

    def set_password(self, password):
        if not password:
            raise ValueError('Пароль не должен быть пустым')
        salt = os.urandom(16)
        digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 600000)
        self.user_pas = f'pbkdf2_sha256$600000${salt.hex()}${digest.hex()}'

    def check_password(self, password):
        if not password or not self.user_pas:
            return False
        if not self.user_pas.startswith('pbkdf2_sha256$'):
            # совместимость с существующими учебными данными
            return hmac.compare_digest(password.encode('utf-8'), self.user_pas.encode('utf-8'))
        try:
            _, rounds, salt, expected = self.user_pas.split('$')
            rounds = int(rounds)
            salt, expected = bytes.fromhex(salt), bytes.fromhex(expected)
            if not 1 <= rounds <= 2000000 or len(salt) != 16 or len(expected) != 32:
                return False
            actual = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, rounds)
            return hmac.compare_digest(actual, expected)
        except (ValueError, TypeError):
            return False

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    users = relationship("User", back_populates="role", lazy="joined")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    cathegory_id = Column(Integer, ForeignKey("cathegories.id"), nullable=False)
    subcathegory_id = Column(Integer, ForeignKey("subcathegories.id"), nullable=False)
    manufacturer_id = Column(Integer, ForeignKey("manufacturers.id"), nullable=False)
    description = Column(String)
    composition = Column(String)
    price = Column(Integer)
    image = Column(String)
    cathegory = relationship("Cathegory", lazy="joined")
    subcathegory = relationship("Subcathegory", lazy="joined")
    manufacturer = relationship("Manufacturer", lazy="joined")
    # остатки по размерам: строки stock (размер + количество)
    stock = relationship("Stock", lazy="selectin")

class Cathegory(Base):
    __tablename__ = "cathegories"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    subcathegories = relationship("Subcathegory", back_populates="cathegory")

class Subcathegory(Base):
    __tablename__ = "subcathegories"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    # подкатегория принадлежит категории: «Кроссовки» детские и женские — разные строки
    cathegory_id = Column(Integer, ForeignKey("cathegories.id"), nullable=False)
    cathegory = relationship("Cathegory", back_populates="subcathegories", lazy="joined")

class Manufacturer(Base):
    __tablename__ = "manufacturers"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)

class Size(Base):
    __tablename__ = "sizes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)

class Stock(Base):
    __tablename__ = "stock"
    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True, nullable=False)
    size_id = Column(Integer, ForeignKey("sizes.id"), primary_key=True, nullable=False)
    amount = Column(Integer)
    size = relationship("Size", lazy="joined")

class Product_tovar(Base):
    __tablename__ = "product_tovar"
    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True, nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), primary_key=True, nullable=False)
    size_id = Column(Integer, ForeignKey("sizes.id"), primary_key=True, nullable=False)
    count = Column(Integer)
    price = Column(Integer)
    product = relationship("Product", lazy="joined")
    size = relationship("Size", lazy="joined")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(Integer, nullable=False)
    order_date = Column(Date, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", lazy="joined")
    # состав заказа: строки product_tovar (товар + размер + количество)
    items = relationship("Product_tovar", lazy="selectin")

def create():
    Base.metadata.create_all(bind=engine)
