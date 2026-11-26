from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session

from models import Order, Product, Product_tovar, Stock, User


class OrderError(ValueError):
    pass


class PricesChanged(OrderError):
    def __init__(self, prices):
        super().__init__('Цены изменились. Проверьте новую сумму и подтвердите заказ ещё раз.')
        self.prices = prices


@dataclass
class CartItem:
    product_id: int
    size_id: int
    product_name: str
    size: str
    unit_price: Decimal
    quantity: int

    @property
    def total(self):
        return self.unit_price * self.quantity


def add_to_cart(cart, product, size, quantity, price):
    key = product.id, size.id
    if key in cart:
        quantity += cart[key].quantity
    cart[key] = CartItem(product.id, size.id, product.name, size.title, price, quantity)


def get_prices(db, base_prices, today):
    if not base_prices:
        return {}
    month_start = today.replace(day=1)
    previous_month_start = (month_start - timedelta(days=1)).replace(day=1)
    rows = db.query(Product_tovar.product_id).join(Order, Product_tovar.order_id == Order.id)
    rows = rows.filter(Product_tovar.product_id.in_(base_prices),
                       Order.order_date >= previous_month_start,
                       Order.order_date < month_start).distinct()
    ordered = {row.product_id for row in rows}
    prices = {}
    for product_id, price in base_prices.items():
        amount = Decimal(str(price))
        if product_id not in ordered:
            amount *= Decimal('0.75')
        prices[product_id] = amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return prices


def format_price(amount):
    return f'{amount:,.2f} ₽'.replace(',', ' ').replace('.', ',')


def take_pairs(db, item):
    rows = db.query(Stock.id, Stock.amount).filter(
        Stock.product_id == item.product_id, Stock.size_id == item.size_id, Stock.amount > 0
    ).order_by(Stock.id).with_for_update().all()
    available = sum(row.amount for row in rows)
    if available < item.quantity:
        raise OrderError(
            f'«{item.product_name}», размер {item.size}: доступно пар — {available}. '
            'Удалите позицию или добавьте её снова с меньшим количеством.'
        )
    remaining = item.quantity
    for row in rows:
        taken = min(remaining, row.amount)
        result = db.execute(
            update(Stock)
            .where(Stock.id == row.id, Stock.amount >= taken)
            .values(amount=Stock.amount - taken)
        )
        if result.rowcount != 1:
            raise OrderError('Остатки изменились. Проверьте количество и повторите заказ.')
        remaining -= taken
        if remaining == 0:
            break


def save_order(database, user_id, cart):
    if not cart or any(line.quantity < 1 for line in cart.values()):
        raise OrderError('Добавьте хотя бы одну пару в заказ.')
    today = date.today()
    with Session(database) as db:
        if db.get(User, user_id) is None:
            raise OrderError('Пользователь больше недоступен. Войдите снова.')
        product_ids = {item.product_id for item in cart.values()}
        rows = db.query(Product.id, Product.price).filter(Product.id.in_(product_ids)).all()
        base_prices = {row.id: row.price for row in rows}
        if len(product_ids) != len(base_prices):
            raise OrderError('Один из товаров больше недоступен. Удалите его из заказа.')
        prices = get_prices(db, base_prices, today)
        for item in cart.values():
            if prices[item.product_id] != item.unit_price:
                raise PricesChanged(prices)

        # Блокируем остатки в одном порядке, даже если покупатели добавили их в разном порядке.
        for key in sorted(cart):
            take_pairs(db, cart[key])
        order = Order(order_date=today, user_id=user_id)
        db.add(order)
        for item in cart.values():
            # Одна строка order_items соответствует одной паре.
            for _ in range(item.quantity):
                order.items.append(Product_tovar(
                    product_id=item.product_id, size_id=item.size_id, price=float(item.unit_price)
                ))
        db.flush()
        order_id = order.id
        db.commit()
    return order_id, today


def delete_order(database, order_id):
    with Session(database) as db, db.begin():
        if db.scalar(select(Order.id).where(Order.id == order_id).with_for_update()) is None:
            raise OrderError('Заказ уже удалён.')

        pair = (Product_tovar.product_id, Product_tovar.size_id)
        lines = db.execute(select(*pair, func.count()).where(Product_tovar.order_id == order_id)
                           .group_by(*pair).order_by(*pair)).all()
        for product_id, size_id, quantity in lines:
            stock_id = db.scalar(select(Stock.id).where(
                Stock.product_id == product_id, Stock.size_id == size_id, Stock.amount >= 0,
            ).order_by(Stock.id).limit(1).with_for_update())
            if stock_id is None:
                db.add(Stock(product_id=product_id, size_id=size_id, amount=quantity))
            else:
                db.execute(update(Stock).where(Stock.id == stock_id).values(amount=Stock.amount + quantity))

        db.execute(delete(Product_tovar).where(Product_tovar.order_id == order_id))
        result = db.execute(delete(Order).where(Order.id == order_id))
        if result.rowcount != 1:
            raise OrderError('Заказ уже удалён.')
