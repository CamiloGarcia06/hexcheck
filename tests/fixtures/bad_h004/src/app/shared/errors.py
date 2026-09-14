from app.items.domain.entities import Item
class DomainError(Exception):
    code = 'domain_error'


class NotFound(DomainError):
    code = 'not_found'
