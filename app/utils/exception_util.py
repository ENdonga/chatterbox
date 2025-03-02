from datetime import datetime
from http import HTTPStatus
from zoneinfo import ZoneInfo

from fastapi.responses import JSONResponse

TIMEZONE = ZoneInfo('Etc/GMT-3')


def create_error_response(status_code: int, message: str, reason: str) -> JSONResponse:
    """Generates a consistent JSON error response."""
    return JSONResponse(
        status_code=status_code,
        content={
            "timestamp": datetime.now(TIMEZONE).isoformat(),
            "status_code": status_code,
            "status": status_code_to_phrase(status_code),
            "message": message,
            "reason": reason,
        },
    )


def status_code_to_phrase(status_code: int) -> str:
    """Converts HTTP status codes to uppercase phrases (e.g., 409 → CONFLICT)"""
    return HTTPStatus(status_code).phrase.replace(" ", "_").upper()
