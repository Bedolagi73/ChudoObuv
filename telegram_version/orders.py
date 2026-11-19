from dataclasses import dataclass
from datetime import date

from sqlalchemy import func, select, text, tuple_
from sqlalchemy.orm import Session, lazyload

from models import Order, Product_tovar, Stock


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


def save_order(engine, user_id, lines):
    lines = tuple(lines)
    if not lines or any(line.quantity < 1 for line in lines):
        raise ValueError("Заказ должен содержать позиции с положительным количеством.")

    keys = {(line.product_id, line.size_id) for line in lines}
    if len(keys) != len(lines):
        raise ValueError("Повторяющиеся позиции необходимо объединить до сохранения заказа.")

    with Session(engine) as db, db.begin():
        if db.get_bind().dialect.name == "postgresql":
            # Сериализует выдачу номеров заказов, включая вставки из других сессий.
            db.execute(text("LOCK TABLE orders IN SHARE ROW EXCLUSIVE MODE"))

        stock_query = (
            select(Stock)
            .options(lazyload(Stock.size))
            .where(tuple_(Stock.product_id, Stock.size_id).in_(keys))
            .with_for_update(of=Stock)
        )
        stock = {(row.product_id, row.size_id): row for row in db.scalars(stock_query)}
        for line in lines:
            row = stock.get((line.product_id, line.size_id))
            available = (row.amount or 0) if row is not None else 0
            if available < line.quantity:
                raise StockUnavailableError(
                    f"«{line.product_name}», размер {line.size_title}. "
                    f"Запрошено {line.quantity}, в наличии {max(available, 0)}."
                )

        code = db.scalar(select(func.coalesce(func.max(Order.code), 0))) + 1
        order_date = date.today()
        order = Order(code=code, order_date=order_date, user_id=user_id)
        for line in lines:
            stock[line.product_id, line.size_id].amount -= line.quantity
            order.items.append(
                Product_tovar(
                    product_id=line.product_id,
                    size_id=line.size_id,
                    count=line.quantity,
                    price=line.unit_price,
                )
            )
        db.add(order)

    return code, order_date
