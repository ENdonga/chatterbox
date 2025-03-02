from pydantic import BaseModel, Field, field_validator, EmailStr
from pydantic_core.core_schema import FieldValidationInfo


class UserCreateModel(BaseModel):
    firstname: str = Field(..., max_length=15, min_length=3)
    lastname: str = Field(..., max_length=15, min_length=3)
    email: EmailStr = Field(..., strip_whitespace=True)
    password: str = Field(..., min_length=3, strip_whitespace=True)

    @field_validator("firstname", "lastname")
    @classmethod
    def validate_not_blank(cls, value: str, info: FieldValidationInfo) -> str:
        """Ensure firstname and lastname are not blank or just spaces"""
        if not value.strip():
            raise ValueError(f"{info.field_name} field cannot be blank or contain only spaces")
        return value

    @field_validator("password")
    def validate_password(cls, value):
        """Custom validator to check if password is blank or just spaces"""
        if not value.strip():
            raise ValueError("Password cannot be blank or contain only spaces")
        return value


class UserResponseModel(BaseModel):
    id: int
    firstname: str
    lastname: str
    is_verified: bool
    email: EmailStr

    # created_at: datetime

    class Config:
        from_attributes = True


class UserLoginModel(BaseModel):
    email: EmailStr
    password: str
