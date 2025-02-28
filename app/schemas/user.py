from pydantic import BaseModel, Field, field_validator, EmailStr


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


class UserLogin(BaseModel):
    email: EmailStr
    password: str