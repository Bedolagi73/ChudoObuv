from dataclasses import dataclass

from sqlalchemy import func, select, text
from sqlalchemy.orm import lazyload

from models import Order, Stock


@dataclass(frozen=True)
class OrderLine:
    product_id: int
    size_id: int
    product_name: str
    size_title: str
    quantity: int
    unit_price: int

    @property
    def total(self):
        return self.quantity * self.unit_price


class StockUnavailableError(Exception):
    pass


def next_order_code(db):
    if db.get_bind().dialect.name == "postgresql":
        # Другой заказ получит номер после завершения этой транзакции.
        db.execute(text("LOCK TABLE orders IN SHARE ROW EXCLUSIVE MODE"))
    return db.scalar(select(func.coalesce(func.max(Order.code), 0))) + 1


def take_stock(db, line):
    stock = db.get(
        Stock,
        (line.product_id, line.size_id),
        options=[lazyload(Stock.size)],
        with_for_update={"of": Stock},
    )
    available = (stock.amount or 0) if stock is not None else 0
    if available < line.quantity:
        raise StockUnavailableError(
            f"«{line.product_name}», размер {line.size_title}. "
            f"Запрошено {line.quantity}, в наличии {max(available, 0)}."
        )
    stock.amount -= line.quantity
