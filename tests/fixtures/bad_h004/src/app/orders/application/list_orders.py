from app.orders.domain.entities import Order


class ListOrders:
    def __call__(self) -> list[Order]:
        return []
