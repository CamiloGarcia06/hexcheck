from __future__ import annotations

from __APP__.shared.errors import Invalid, NotFound


class __Entity__NotFound(NotFound):
    code = "__entity___not_found"


class Empty__Entity__Name(Invalid):
    code = "empty___entity___name"
