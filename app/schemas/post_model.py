from pydantic import BaseModel, Field, field_validator
from pydantic_core.core_schema import FieldValidationInfo


class PostModel(BaseModel):
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

    @field_validator("title", "content")
    @classmethod
    def trim_whitespace(cls, value: str) -> str:
        """Ensure title and content have no extra white spaces before and after"""
        return value.strip()


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    published: bool

    class Config:
        from_attributes = True
