from datetime import datetime
from http import HTTPStatus

from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from .custom_exceptions import RequestValidationError, ResponseValidationError, DatabaseConnectionError, \
    AuthorizationError, AuthenticationError, EntityNotFound, DatabaseIntegrityError


def format_error_response(exception: Exception, status_code: int, message: str, reason: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "timestamp": datetime.now().isoformat(),
            "status_code": status_code,
            "status": HTTPStatus(status_code).phrase.replace(" ", "_").upper(),
            "message": message,
            "reason": reason,
        }
    )


def custom_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, RequestValidationError):
        return format_error_response(exc, status.HTTP_400_BAD_REQUEST, "Request validation failed", str(exc.detail))
    elif isinstance(exc, ResponseValidationError):
        return format_error_response(exc, status.HTTP_400_BAD_REQUEST, "Response validation failed", str(exc.detail))
    elif isinstance(exc, DatabaseConnectionError):
        return format_error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR, "Database connection failed",
                                     str(exc.detail))
    elif isinstance(exc, DatabaseIntegrityError):
        return format_error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR, "Unique constraint violation",
                                     str(exc.detail))
    elif isinstance(exc, AuthorizationError):
        return format_error_response(exc, status.HTTP_403_FORBIDDEN, "Authorization error", str(exc.detail))
    elif isinstance(exc, AuthenticationError):
        return format_error_response(exc, status.HTTP_401_UNAUTHORIZED, "Authentication error", str(exc.detail))
    elif isinstance(exc, EntityNotFound):
        return format_error_response(exc, status.HTTP_404_NOT_FOUND, "Request failed", str(exc.detail))

    return format_error_response(exc, status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error",
                                 "An unexpected error occurred")
