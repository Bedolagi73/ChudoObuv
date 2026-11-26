from sqlalchemy import func, select, text
from sqlalchemy.orm import lazyload

from models import Order, Stock


def next_order_code(db):
    if db.get_bind().dialect.name == "postgresql":
        # Другой заказ получит номер после завершения этой транзакции.
        db.execute(text("LOCK TABLE orders IN SHARE ROW EXCLUSIVE MODE"))
    return db.scalar(select(func.coalesce(func.max(Order.code), 0))) + 1


def take_stock(db, tovar, size, count):
    stock = db.get(
        Stock,
        (tovar.id, size.id),
        options=[lazyload(Stock.size)],
        with_for_update={"of": Stock},
    )
    available = (stock.amount or 0) if stock is not None else 0
    if available < count:
        return (
            f"«{tovar.name}», размер {size.title}. "
            f"Запрошено {count}, в наличии {max(available, 0)}."
        )
    stock.amount -= count
    return None
