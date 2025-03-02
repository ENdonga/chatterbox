from fastapi import Depends, APIRouter
from starlette.status import HTTP_200_OK

from app.schemas.base_response import BaseResponse
from app.schemas.user_model import UserLoginModel
from app.service.auth_service import AuthService

router = APIRouter(tags=["Authentication"])


@router.post("/login")
def login(user_credentials: UserLoginModel, auth_service: AuthService = Depends()):
    auth_service.authenticate(user_credentials)
    return BaseResponse.success("Login Success", f"Login Success", status_code=HTTP_200_OK)
