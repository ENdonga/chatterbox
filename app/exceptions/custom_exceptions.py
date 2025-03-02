from http import HTTPStatus

from pydantic import EmailStr
from starlette import status


class ChatterBoxException(Exception):
    """This is the base clas for all the ChatterBox application errors"""

    def __init__(self, message: str, reason: str = None, status_code: int = 400):
        self.message = message
        self.reason = reason
        self.status_code = status_code
        super().__init__(message)

    @staticmethod
    def status_code_to_phrase(status_code: int) -> str:
        """Converts HTTP status codes to uppercase phrases (e.g., 409 → CONFLICT)"""
        return HTTPStatus(status_code).phrase.replace(" ", "_").upper()


class InvalidTokenException(ChatterBoxException):
    """The user has provided an invalid or expired token"""

    def __init__(self, reason: str = "Invalid or expired token"):
        super().__init__(message="Invalid Token", reason=reason, status_code=status.HTTP_401_UNAUTHORIZED)


class EntityNotFoundException(ChatterBoxException):
    """The entity the user is trying to access is not found"""

    def __init__(self, entity_name: str, identifier: int):
        super().__init__(message=f"{entity_name} not found", reason=f"{entity_name} with id: {identifier} not found",
                         status_code=status.HTTP_404_NOT_FOUND)


class UserAlreadyExistsException(ChatterBoxException):
    """The user has provided an email address that already exists"""

    def __init__(self, email: EmailStr):
        super().__init__(message="User already exists", reason=f"User with email: {email} already exists",
                         status_code=status.HTTP_409_CONFLICT)


class InvalidCredentialsException(ChatterBoxException):
    """The user has provided invalid credentials during login"""

    def __init__(self, reason: str = "Invalid credentials provided. Please try again."):
        super().__init__(message="Login failed", reason=reason, status_code=status.HTTP_401_UNAUTHORIZED)


class UnknownHashException(ChatterBoxException):
    """The provided password does not match the user's hashed pasword"""

    def __init__(self, reason: str = "Invalid credentials provided. Please try again."):
        super().__init__(message="Login failed", reason=reason, status_code=status.HTTP_401_UNAUTHORIZED)


class InsufficientPermissionsException(ChatterBoxException):
    """The user does not have enough permissions to access this resource"""

    def __init__(self, reason: str = "Insufficient permissions to access this resource"):
        super().__init__(message="Insufficient permissions", reason=reason, status_code=status.HTTP_403_FORBIDDEN)


# Database errors
class DatabaseException(ChatterBoxException):
    """Base exception for all database-related errors."""

    def __init__(self, message: str, reason: str = "A database error occurred. Please try again."):
        super().__init__(message=message, reason=reason, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DatabaseIntegrityException(DatabaseException):
    """Raised when a database constraint (e.g., unique key) is violated."""

    def __init__(self, reason: str = "Database integrity constraint violated."):
        super().__init__(message="Database Integrity error", reason=reason)


class DatabaseConnectionException(DatabaseException):
    """Raised when the application fails to connect to the database."""

    def __init__(self, reason: str = "Database connection failed."):
        super().__init__(message="Database Connection error", reason=reason)


class DatabaseTimeoutException(DatabaseException):
    """Raised when a database query takes too long to execute."""

    def __init__(self, reason: str = "Database operation timed out."):
        super().__init__(message="Database Timeout error", reason=reason)


class RequestValidationException(ChatterBoxException):
    """Raised when a request body validation fails."""

    def __init__(self, message: str = "Invalid request body", reason: str = "One or more request fields are invalid"):
        super().__init__(message=message, reason=reason, status_code=status.HTTP_400_BAD_REQUEST)


class InternalServerError(ChatterBoxException):
    """Generic internal server error."""

    def __init__(self, reason: str = "An unexpected error occurred on the server"):
        super().__init__(message="Internal Server Error", reason=reason,
                         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

# def create_exception_handler(status_code: int, details: dict) -> Callable[[Request, Exception], JSONResponse]:
#     def exception_handler(request: Request, exception: ChatterBoxException) -> JSONResponse:
#         return JSONResponse(
#             content=details,
#             status_code=status_code,
#         )
#
#     return exception_handler
