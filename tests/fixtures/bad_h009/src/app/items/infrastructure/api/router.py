import sqlalchemy
from fastapi import APIRouter, Depends

from app.items.application.create_item import CreateItem
from app.shared.api_auth import require_token

from .deps import get_create_item
from .schemas import ItemIn

router = APIRouter(prefix='/items')


@router.post('', dependencies=[Depends(require_token)])
def create(body: ItemIn, use_case: CreateItem = Depends(get_create_item)) -> dict[str, int]:
    return {'id': use_case(body.name).id}
