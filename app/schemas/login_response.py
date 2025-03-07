from dataclasses import dataclass

from pydantic import BaseModel


@dataclass
class TokenOwnerModel(BaseModel):
    id: int
    email: str


@dataclass
class LoginResponseModel(BaseModel):
    access_token: str
    refresh_token: str
    owner: TokenOwnerModel
    type: str = 'Bearer'


@dataclass
class TokenRefreshModel(BaseModel):
    refresh_token: str
