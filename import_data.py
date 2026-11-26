# This Python file uses the following encoding: utf-8
# Загрузка табличек из import\ в БД: python import_data.py
import datetime
from pathlib import Path

from openpyxl import load_workbook
from sqlalchemy.orm import Session

from models import (create, engine, Role, User, Cathegory, Subcathegory, Manufacturer,
                    Size, Product, Stock, Order, Product_tovar)

IMPORT_DIR = Path(__file__).resolve().parent / "import"


def rows(name):
    """Строки листа без заголовка."""
    ws = load_workbook(IMPORT_DIR / f"{name}_import.xlsx", data_only=True).active
    return [r for r in ws.iter_rows(min_row=2, values_only=True) if any(r)]


def clean(text):
    # в табличках встречаются неразрывные пробелы и двойные пробелы
    return " ".join(str(text).replace("\xa0", " ").split())


def size_title(value):
    # 20, 20.0, "20" → "20";  36.5 → "36.5"
    return f"{float(str(value).replace(',', '.')):g}"


def to_date(value):
    # дата приходит датой или числом Excel (46114 = 02.04.2026)
    if isinstance(value, datetime.datetime):
        return value.date()
    return datetime.date(1899, 12, 30) + datetime.timedelta(days=int(value))


def main():
    create()
    with Session(engine) as db:
        if db.query(Role).first() is not None:
            print("В базе уже есть данные, загрузка пропущена.")
            return

        refs = {}

        def ref(cls, title):
            # один объект справочника на одно название
            title = clean(title)
            if (cls, title) not in refs:
                refs[(cls, title)] = cls(title=title)
                db.add(refs[(cls, title)])
            return refs[(cls, title)]

        users = {}
        for surname, name, patronymic, login, role in rows("Users"):
            u = User(surname=clean(surname), name=clean(name), patronymic=clean(patronymic),
                     user_login=clean(login), role=ref(Role, role))
            db.add(u)
            users[clean(f"{surname} {name} {patronymic}")] = u

        for (value,) in rows("Sizes"):
            ref(Size, size_title(value))

        subcathegories = {}

        def subcathegory(cat, title):
            # подкатегория своя у каждой категории
            key = (clean(cat), clean(title))
            if key not in subcathegories:
                subcathegories[key] = Subcathegory(title=key[1], cathegory=ref(Cathegory, cat))
                db.add(subcathegories[key])
            return subcathegories[key]

        products = {}
        for cat, subcat, image, name, manuf, description, composition, price in rows("Products"):
            p = Product(name=clean(name),
                        subcathegory=subcathegory(cat, subcat),
                        manufacturer=ref(Manufacturer, manuf), description=description or '',
                        composition=composition or '', price=float(price), image=image or '')
            db.add(p)
            products[(clean(name), clean(manuf))] = p

        def find_product(name, manuf):
            key = (clean(name), clean(manuf))
            if key in products:
                return products[key]
            # в Stock/Orders название бывает короче, чем в Products:
            # «Черные туфли в классическом стиле» и «… — база для деловых образов»
            same = [p for (n, m), p in products.items() if m == key[1] and n.startswith(key[0])]
            if len(same) == 1:
                print(f"  сопоставлено по началу названия: «{key[0]}» → «{same[0].name}»")
                return same[0]
            raise ValueError(f"Товар не найден: {key[0]} ({key[1]})")

        for name, manuf, size, amount in rows("Stock_Items"):
            p = find_product(name, manuf)
            p.stock.append(Stock(size=ref(Size, size_title(size)), amount=int(amount)))

        orders = {}
        for code, date, fio, cat, name, manuf, size, count, price in rows("Orders"):
            code = int(code)
            if code not in orders:
                user = users.get(clean(fio))
                if user is None:
                    raise ValueError(f"Заказ {code}: пользователь не найден: {fio}")
                orders[code] = Order(order_date=to_date(date), user=user)
                db.add(orders[code])
            # в order_items нет колонки количества: одна строка на каждую пару
            for _ in range(int(count)):
                orders[code].items.append(Product_tovar(product=find_product(name, manuf),
                                                        size=ref(Size, size_title(size)),
                                                        price=float(price)))

        db.commit()

        for cls in (Role, User, Cathegory, Subcathegory, Manufacturer, Size,
                    Product, Stock, Order, Product_tovar):
            print(f"{cls.__tablename__}: {db.query(cls).count()}")


if __name__ == "__main__":
    main()
