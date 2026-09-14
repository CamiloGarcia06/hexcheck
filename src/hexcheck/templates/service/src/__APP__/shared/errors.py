"""Jerarquía base de errores de dominio. Cada funcionalidad hereda en domain/errors.py.

Vive en shared/ para que un solo traductor (api_errors.py) capture toda la jerarquía.
"""

from __future__ import annotations


class DomainError(Exception):
    code = "domain_error"

    def __init__(self, message: str = "") -> None:
        super().__init__(message or self.code)
        self.message = message or self.code


class NotFound(DomainError):
    code = "not_found"


class Conflict(DomainError):
    code = "conflict"


class Invalid(DomainError):
    code = "invalid"
