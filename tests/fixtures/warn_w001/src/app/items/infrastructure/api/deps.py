from fastapi import Request

from app.items.application.create_item import CreateItem


def get_create_item(request: Request) -> CreateItem:
    return request.app.state.items
