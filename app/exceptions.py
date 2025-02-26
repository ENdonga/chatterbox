import logging
from sqlite3 import IntegrityError

from fastapi import HTTPException, Request
from psycopg2.errors import UniqueViolation
from starlette.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from app.schemas import BaseResponse

logger = logging.getLogger("uvicorn.error")


# Handle standard HTTP exceptions
def handle_http_exception(request: Request, exception: HTTPException):
    status_code = exception.status_code
    if status_code not in {400, 401, 403, 404}:
        status_code = HTTP_400_BAD_REQUEST

    # If exception.detail is already a dictionary (structured response), use it directly
    if isinstance(exception.detail, dict):
        return JSONResponse(content=exception.detail, status_code=status_code)

    response = BaseResponse.error(message="Request failed", reason=exception.detail, status_code=status_code)
    return JSONResponse(content=response, status_code=exception.status_code)


# Handle database errors
def handle_db_integrity_exception(request: Request, exception: IntegrityError):
    logger.error(f"IntegrityError: {exception}")
    if isinstance(exception.orig, UniqueViolation):
        response = BaseResponse.error(
            message="Conflict error",
            reason="A user with this email already exists.",
            status_code=HTTP_400_BAD_REQUEST
        )
        return JSONResponse(content=response, status_code=HTTP_400_BAD_REQUEST)
    response = BaseResponse.error(
        message="Invalid request",
        reason="A database integrity error occurred.",
        status_code=HTTP_400_BAD_REQUEST
    )
    return JSONResponse(content=response, status_code=HTTP_400_BAD_REQUEST)


# Handle unexpected errors
def handle_general_exception(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {exc}")

    response = BaseResponse.error(
        message="Request failed",
        reason="An unexpected error occurred. Please try again later.",
        status_code=HTTP_500_INTERNAL_SERVER_ERROR
    )

    return JSONResponse(content=response, status_code=HTTP_500_INTERNAL_SERVER_ERROR)
