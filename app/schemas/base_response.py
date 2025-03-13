from datetime import datetime
from http import HTTPStatus
from typing import Generic, TypeVar, Optional, Union, List, Dict
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict
from starlette.responses import JSONResponse

TIMEZONE = ZoneInfo('Etc/GMT-3')

# Generic Type Variable for data
T = TypeVar("T")


# This is a custom HTTP response that will be sent to all endpoints
class BaseResponse(BaseModel, Generic[T]):
    timestamp: str
    status_code: int
    status: str
    message: str
    reason: Optional[Union[str, List[Dict[str, str]]]]= None  # Only shown if there is an error
    data: Optional[T] = None  # Data is optional for cases like delete operations

    # Exclude None fields globally
    model_config = ConfigDict(extra="forbid", populate_by_name=True, exclude_none=True)

    def model_dump(self, *args, **kwargs):
        return super().model_dump(*args, exclude_none=True)

    @classmethod
    def success(cls, data: Optional[T] = None, message: str = "Success", status_code: int = 200):
        """Creates a successful API response"""
        response = cls(
            timestamp=datetime.now(TIMEZONE).isoformat(),
            status_code=status_code,
            status=HTTPStatus(status_code).phrase.replace(" ", "_").upper(),
            message=message,
            data=data if data is not None else None
        ).model_dump(exclude_none=True)
        # force the response to be returned as JSON to remove none values
        return JSONResponse(content=response, status_code=status_code)

    @classmethod
    def error(cls, message: str, reason: Optional[Union[str, List[Dict[str, str]]]] = None, status_code: int = 400):
        """Returns a dictionary instead of JSONResponse so exception handlers can use it"""
        return {
            "timestamp": datetime.now().isoformat(),
            "status_code": status_code,
            "status": HTTPStatus(status_code).phrase.replace(" ", "_").upper(),
            "message": message,
            "reason": reason
        }
