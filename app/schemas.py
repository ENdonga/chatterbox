from datetime import datetime
from http import HTTPStatus
from typing import TypeVar, Generic, Optional

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    published: bool

    class Config:
        from_attributes = True


# Generic Type Variable for data
T = TypeVar("T")


# This is a custom HTTP response that will be sent to all endpoints
class BaseResponse(BaseModel, Generic[T]):
    timestamp: str
    status_code: int
    status: str
    message: str
    reason: Optional[str] = None  # Only shown if there is an error
    data: Optional[T] = None  # Data is optional for cases like delete operations

    # 🔹 Exclude None fields globally
    model_config = ConfigDict(extra="forbid", populate_by_name=True, exclude_none=True)

    @classmethod
    def success(cls, data: Optional[T] = None, message: str = "Success", status_code: int = 200):
        response = cls(
            timestamp=datetime.utcnow().isoformat(),
            status_code=status_code,
            status=HTTPStatus(status_code).phrase.replace(" ", "_").upper(),
            message=message,
            data=data
        )
        return response

    @classmethod
    def error(cls, message: str, reason: Optional[str] = None, status_code: int = 404):
        response = cls(
            timestamp=datetime.utcnow().isoformat(),
            status_code=status_code,
            status=HTTPStatus(status_code).phrase.replace(" ", "_").upper(),
            message=message,
            reason=reason
        ).model_dump(exclude_none=True)
        raise HTTPException(
            status_code=status_code,
            detail=response  # Convert to dict before passing
        )
