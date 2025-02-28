from fastapi import Depends, APIRouter
from starlette.status import HTTP_200_OK

from app.schemas import BaseResponse, UserLogin
from app.service.auth_service import AuthService

router = APIRouter(tags=["Authentication"])


@router.post("/login")
def login(user_credentials: UserLogin, auth_service: AuthService = Depends()):
    user = auth_service.authenticate(user_credentials)
    return BaseResponse.success("Login Success", f"Login Success", status_code=HTTP_200_OK)
