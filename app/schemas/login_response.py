from pydantic import BaseModel


class TokenOwnerModel(BaseModel):
    id: int
    email: str


class LoginResponseModel(BaseModel):
    access_token: str
    refresh_token: str
    type: str = 'Bearer'
    owner: TokenOwnerModel


class TokenRefreshModel(BaseModel):
    refresh_token: str
