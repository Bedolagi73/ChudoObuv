from os import environ

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date, Float
from sqlalchemy.orm import declarative_base, relationship

engine = create_engine(environ["DATABASE_URL"])
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    patronymic = Column(String)
    user_login = Column(String, nullable=False)
    user_pas = Column(String)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    role = relationship("Role", back_populates="users")

    def __str__(self):
        return f"{self.surname} {self.name} {self.patronymic}"


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    users = relationship("User", back_populates="role")


class Cathegory(Base):
    __tablename__ = "cathegories"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)


class Subcathegory(Base):
    __tablename__ = "subcathegories"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)


class Manufacturer(Base):
    __tablename__ = "manufacturers"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)


class Size(Base):
    __tablename__ = "sizes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)


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
    stock = relationship("Stock", lazy="selectin")


class Stock(Base):
    __tablename__ = "stock"
    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    size_id = Column(Integer, ForeignKey("sizes.id"), primary_key=True)
    amount = Column(Integer)
    size = relationship("Size", lazy="joined")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(Integer, nullable=False)
    order_date = Column(Date, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", lazy="joined")
    items = relationship("Product_tovar", lazy="selectin")


class Product_tovar(Base):
    __tablename__ = "product_tovar"
    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), primary_key=True)
    size_id = Column(Integer, ForeignKey("sizes.id"), primary_key=True)
    count = Column(Integer)
    price = Column(Integer)
    product = relationship("Product", lazy="joined")
    size = relationship("Size", lazy="joined")


def create():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create()