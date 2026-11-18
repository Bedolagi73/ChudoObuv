from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select, tuple_, update
from sqlalchemy.orm import Session

from models import Order, Product, Product_tovar, Stock, User


class OrderError(ValueError):
    pass


class PricesChanged(OrderError):
    def __init__(self, prices):
        super().__init__('Цены изменились. Проверьте новую сумму и подтвердите заказ ещё раз.')
        self.prices = prices


@dataclass(frozen=True)
class CartLine:
    product_id: int
    size_id: int
    product_name: str
    size: str
    unit_price: Decimal
    quantity: int

    @property
    def total(self):
        return self.unit_price * self.quantity


def sale_prices(db, base_prices, today):
    if not base_prices:
        return {}
    month_start = today.replace(day=1)
    previous_month_start = (month_start - timedelta(days=1)).replace(day=1)
    ordered = set(db.scalars(
        select(Product_tovar.product_id)
        .join(Order, Product_tovar.order_id == Order.id)
        .where(Product_tovar.product_id.in_(base_prices),
               Order.order_date >= previous_month_start, Order.order_date < month_start)
        .distinct()
    ))
    return {
        product_id: (Decimal(str(price)) * (1 if product_id in ordered else Decimal('0.75')))
        .quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        for product_id, price in base_prices.items()
    }


def format_price(amount):
    return f'{amount:,.2f} ₽'.replace(',', ' ').replace('.', ',')


def place_order(database, user_id, cart):
    if not cart or any(line.quantity < 1 for line in cart.values()):
        raise OrderError('Добавьте хотя бы одну пару в заказ.')
    today = date.today()
    with Session(database) as db, db.begin():
        if db.scalar(select(User.id).where(User.id == user_id)) is None:
            raise OrderError('Пользователь больше недоступен. Войдите снова.')
        product_ids = {product_id for product_id, _ in cart}
        base_prices = dict(db.execute(
            select(Product.id, Product.price).where(Product.id.in_(product_ids))
        ).all())
        if product_ids != base_prices.keys():
            raise OrderError('Один из товаров больше недоступен. Удалите его из заказа.')
        prices = sale_prices(db, base_prices, today)
        if any(prices[line.product_id] != line.unit_price for line in cart.values()):
            raise PricesChanged(prices)

        # Несколько строк склада могут описывать один размер. Блокируем их в одном порядке.
        stock_rows = db.execute(
            select(Stock.id, Stock.product_id, Stock.size_id, Stock.amount)
            .where(tuple_(Stock.product_id, Stock.size_id).in_(list(cart)), Stock.amount > 0)
            .order_by(Stock.id)
            .with_for_update()
        )
        stock_by_size = defaultdict(list)
        for stock_id, product_id, size_id, amount in stock_rows:
            stock_by_size[product_id, size_id].append((stock_id, amount))

        order = Order(order_date=today, user_id=user_id)
        db.add(order)
        for key, line in cart.items():
            rows = stock_by_size[key]
            available = sum(amount for _, amount in rows)
            if available < line.quantity:
                raise OrderError(
                    f'«{line.product_name}», размер {line.size}: доступно пар — {available}. '
                    'Удалите позицию или добавьте её снова с меньшим количеством.'
                )
            remaining = line.quantity
            for stock_id, amount in rows:
                taken = min(remaining, amount)
                changed = db.execute(
                    update(Stock)
                    .where(Stock.id == stock_id, Stock.amount >= taken)
                    .values(amount=Stock.amount - taken)
                )
                if changed.rowcount != 1:
                    raise OrderError('Остатки изменились. Проверьте количество и повторите заказ.')
                remaining -= taken
                if remaining == 0:
                    break
            # В текущей схеме одна строка order_items соответствует одной паре.
            order.items.extend(
                Product_tovar(product_id=line.product_id, size_id=line.size_id,
                              price=float(prices[line.product_id]))
                for _ in range(line.quantity)
            )
        db.flush()
        order_id = order.id
    return order_id, today
