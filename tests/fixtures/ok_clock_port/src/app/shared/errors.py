class DomainError(Exception):
    code = 'domain_error'


class NotFound(DomainError):
    code = 'not_found'
