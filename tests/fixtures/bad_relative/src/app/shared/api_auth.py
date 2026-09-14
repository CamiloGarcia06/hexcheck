from fastapi import HTTPException, Request


def require_token(request: Request) -> None:
    if request.headers.get('authorization') != 'Bearer x':
        raise HTTPException(status_code=401)
