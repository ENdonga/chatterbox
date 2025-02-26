from datetime import datetime
from http import HTTPStatus
from typing import TypeVar, Generic, Optional
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from pydantic_core.core_schema import FieldValidationInfo
from starlette.responses import JSONResponse

TIMEZONE = ZoneInfo('Etc/GMT-3')


class Post(BaseModel):
    title: str = Field(..., min_length=3, strip_whitespace=True)
    content: str = Field(..., min_length=3, strip_whitespace=True)
    published: bool = True

    @field_validator("title", "content")
    @classmethod
    def validate_not_blank(cls, value: str, info: FieldValidationInfo) -> str:
        """Ensure title and content are not blank or just spaces"""
        if not value.strip():
            raise ValueError(f"{info.field_name} field cannot be blank or contain only spaces")
        return value


class UserCreate(BaseModel):
    email: EmailStr = Field(..., strip_whitespace=True)
    password: str = Field(..., min_length=3, strip_whitespace=True)

    @field_validator("password")
    def validate_password(cls, value):
        """Custom validator to check if password is blank or just spaces"""
        if not value.strip():
            raise ValueError("Password cannot be blank or contain only spaces")
        return value


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    # created_at: datetime

    class Config:
        from_attributes = True


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

    # Exclude None fields globally
    model_config = ConfigDict(extra="forbid", populate_by_name=True, exclude_none=True)

    def model_dump(self, *args, **kwargs):
        return super().model_dump(*args, exclude_none=True)

    @classmethod
    def success(cls, data: Optional[T] = None, message: str = "Success", status_code: int = 200):
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
    def error(cls, message: str, reason: Optional[str] = None, status_code: int = 404):
        response = cls(
            timestamp=datetime.now(TIMEZONE).isoformat(),
            status_code=status_code,
            status=HTTPStatus(status_code).phrase.replace(" ", "_").upper(),
            message=message,
            reason=reason
        ).model_dump(exclude_none=True)

        return JSONResponse(content=response, status_code=status_code)
