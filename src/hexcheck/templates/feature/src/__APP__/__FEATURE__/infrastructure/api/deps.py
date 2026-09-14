"""Los casos de uso de __FEATURE__ ya cableados por main.py, leídos de app.state."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Request

from __APP__.__FEATURE__.application.create___entity__ import Create__Entity__
from __APP__.__FEATURE__.application.list___FEATURE__ import List__Feature__


@dataclass(frozen=True)
class __Entity__UseCases:
    create: Create__Entity__
    list_all: List__Feature__


def get___FEATURE__(request: Request) -> __Entity__UseCases:
    return request.app.state.__FEATURE__
