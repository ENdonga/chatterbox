from fastapi import Depends, APIRouter
from starlette.status import HTTP_200_OK

from app.schemas.base_response import BaseResponse
from app.schemas.login_response import TokenRefreshModel, LoginResponseModel
from app.schemas.user_model import UserLoginModel
from app.service.auth_service import AuthService

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=BaseResponse[LoginResponseModel])
def login(user_credentials: UserLoginModel, auth_service: AuthService = Depends()):
    login_response = auth_service.authenticate(user_credentials)
    return BaseResponse.success(data=login_response, message=f"Login Success", status_code=HTTP_200_OK)


@router.post("/refresh-token", response_model=BaseResponse[LoginResponseModel])
def refresh_token(refresh_data: TokenRefreshModel, auth_service: AuthService = Depends()):
    """Generates a new access token using a refresh token."""
    token_response = auth_service.refresh_access_token(refresh_data.refresh_token)
    return BaseResponse.success(
        message="Token refreshed successfully",
        status_code=200,
        data=token_response
    )
