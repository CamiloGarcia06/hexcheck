"""Router de __FEATURE__: traduce HTTP ↔ casos de uso. Sin lógica de negocio."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from __APP__.shared.api_auth import require_token

from .deps import __Entity__UseCases, get___FEATURE__
from .schemas import __Entity__In, __Entity__Out

router = APIRouter(prefix="/api/__FEATURE__", tags=["__FEATURE__"])


@router.get(
    "",
    response_model=list[__Entity__Out],
)
def list___FEATURE__(
    use_cases: __Entity__UseCases = Depends(get___FEATURE__),
) -> list[__Entity__Out]:
    return [__Entity__Out.from_entity(e) for e in use_cases.list_all()]


@router.post(
    "",
    response_model=__Entity__Out,
    status_code=201,
    dependencies=[Depends(require_token)],
)
def create___entity__(
    body: __Entity__In,
    use_cases: __Entity__UseCases = Depends(get___FEATURE__),
) -> __Entity__Out:
    return __Entity__Out.from_entity(use_cases.create(body.name))
