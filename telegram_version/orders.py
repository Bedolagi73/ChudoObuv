from dataclasses import dataclass


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
