from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from starlette import status


class RequestValidationError(HTTPException):
    def __init__(self, detail="Invalid request data"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class ResponseValidationError(HTTPException):
    def __init__(self, detail="Invalid response data"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class DatabaseConnectionError(HTTPException):
    def __init__(self, detail="Database connection failed"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class DatabaseIntegrityError(HTTPException):
    def __init__(self, detail="Database constraint violation"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


# Authentication & Authorization
class AuthenticationError(HTTPException):
    def __init__(self, detail="Invalid authentication credentials"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class AuthorizationError(HTTPException):
    def __init__(self, detail="Insufficient permissions"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


# Custom Business Logic Errors
class EntityNotFound(HTTPException):
    def __init__(self, entity_name: str, user_id: int):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"{entity_name} with ID {user_id} not found")

# class TimeoutError(HTTPException):
#     def __init__(self, detail="Request timed out"):
#         super().__init__(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=detail)
