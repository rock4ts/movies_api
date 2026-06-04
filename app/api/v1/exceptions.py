from fastapi import HTTPException
from fastapi import status


class CredentialsHttpException(HTTPException):
    def __init__(self, detail: str = "Incorrect email or password"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
