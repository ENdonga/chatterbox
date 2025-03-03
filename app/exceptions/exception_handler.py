import logging

from fastapi.responses import JSONResponse, Response
from sqlalchemy.exc import IntegrityError, OperationalError
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request

from app.exceptions.custom_exceptions import ChatterBoxException, UnknownHashException
from app.utils.exception_util import create_error_response


def chatterbox_exception_handler(request: Request, exc: ChatterBoxException) -> Response:
    """Handles all ChatterBox custom exceptions."""
    logging.exception(f"Exception occurred at {request.url.path} - {exc.message}")
    return create_error_response(status_code=exc.status_code, message=exc.message, reason=exc.reason)


def unknown_hash_exception_handler(request: Request, exc: UnknownHashException) -> Response:
    """Handles UnknownHashException (invalid password hash)."""
    logging.exception(f"Unknown hash error at {request.url.path} - {exc.message}")
    return create_error_response(status_code=exc.status_code, message=exc.message, reason=exc.reason)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handles HTTP validation errors (e.g., missing fields, invalid JSON)."""
    logging.exception(f"Exception occurred at {request.url.path} - {exc.detail}")
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        reason = f"The requested resource '{request.url.path}' does not exist."
        return create_error_response(status_code=exc.status_code, message="Resource not found", reason=reason)
    return create_error_response(status_code=exc.status_code, message="Validation error", reason=exc.detail)


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """Handles database integrity errors (e.g., duplicate key violations)."""
    logging.exception(f"Database IntegrityError at {request.url.path} - {exc}")
    return create_error_response(status_code=status.HTTP_400_BAD_REQUEST, message="Database integrity error",
                                 reason="A database constraint was violated (e.g., duplicate entry).")


async def database_connection_error_handler(request: Request, exc: OperationalError) -> JSONResponse:
    """Handles database connection issues."""
    logging.exception(f"Database Connection Error at {request.url.path} - {exc}")
    return create_error_response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Database connection error",
                                 reason="Could not connect to the database. Please try again later.")


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catches unexpected errors not handled elsewhere."""
    logging.exception(f"Exception occurred at {request.url.path} - {exc}")
    return create_error_response(status_code=500, message="An unexpected error occurred", reason=str(exc))
