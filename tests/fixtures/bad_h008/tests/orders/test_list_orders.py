from app.orders.application.list_orders import ListOrders


def test_list() -> None:
    assert ListOrders()() == []
