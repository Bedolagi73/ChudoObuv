# This Python file uses the following encoding: utf-8
import os
from pathlib import Path

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date, Float, Text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import declarative_base, relationship
from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().with_name('.env')
load_dotenv(ENV_FILE, override=False, interpolate=False, encoding='utf-8-sig')


class DatabaseConfigError(ValueError):
    pass


engine = None
config_error = 'Не задана DATABASE_URL. Скопируйте .env.example в .env рядом с models.py и укажите свою базу данных.'
database_url = os.environ.get('DATABASE_URL', '').strip()
if database_url:
    try:
        url = make_url(database_url)
        if url.drivername == 'postgresql':
            url = url.set(drivername='postgresql+psycopg')
        options = {'connect_timeout': 5} if url.get_backend_name() == 'postgresql' else {}
        engine = create_engine(url, connect_args=options)
    except (ArgumentError, ValueError):
        config_error = 'Некорректная DATABASE_URL. Проверьте формат подключения по образцу .env.example.'

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    patronymic = Column(String)
    user_login = Column('login', String, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    role = relationship("Role", back_populates="users", lazy="joined")

    def __str__(self):
        return f'{self.surname} {self.name} {self.patronymic}'

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    title = Column('name', String, nullable=False)
    users = relationship("User", back_populates="role", lazy="joined")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    subcathegory_id = Column('sub_cat_id', Integer, ForeignKey("sub_categories.id"), nullable=False)
    manufacturer_id = Column(Integer, ForeignKey("manufacturers.id"), nullable=False)
    description = Column(Text, nullable=False)
    composition = Column('content', Text, nullable=False)
    price = Column(Float, nullable=False)
    image = Column('image_path', String, nullable=False)
    subcathegory = relationship("Subcathegory", lazy="joined")
    manufacturer = relationship("Manufacturer", lazy="joined")
    # остатки по размерам: строки product_items (размер + количество)
    stock = relationship("Stock", lazy="selectin")

class Cathegory(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    title = Column('name', String, nullable=False)
    subcathegories = relationship("Subcathegory", back_populates="cathegory")

class Subcathegory(Base):
    __tablename__ = "sub_categories"
    id = Column(Integer, primary_key=True, index=True)
    title = Column('name', String, nullable=False)
    # подкатегория принадлежит категории: «Кроссовки» детские и женские — разные строки
    cathegory_id = Column('category_id', Integer, ForeignKey("categories.id"), nullable=False)
    cathegory = relationship("Cathegory", back_populates="subcathegories", lazy="joined")

class Manufacturer(Base):
    __tablename__ = "manufacturers"
    id = Column(Integer, primary_key=True, index=True)
    title = Column('name', String, nullable=False)

class Size(Base):
    __tablename__ = "sizes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column('name', String, nullable=False)

class Stock(Base):
    __tablename__ = "product_items"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    size_id = Column(Integer, ForeignKey("sizes.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    size = relationship("Size", lazy="joined")

class Product_tovar(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    size_id = Column(Integer, ForeignKey("sizes.id"), nullable=False)
    price = Column(Float, nullable=False)
    product = relationship("Product", lazy="joined")
    size = relationship("Size", lazy="joined")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    order_date = Column('date', Date, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", lazy="joined")
    # состав заказа: строки order_items; каждая строка соответствует одной паре
    items = relationship("Product_tovar", lazy="selectin")

def create():
    if engine is None:
        raise DatabaseConfigError(config_error)
    Base.metadata.create_all(bind=engine)
