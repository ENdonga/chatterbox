from fastapi import Depends, APIRouter
from starlette import status

from app.schemas.base_response import BaseResponse
from app.schemas.user_model import UserResponseModel, UserCreateModel
from app.service.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=BaseResponse[UserResponseModel])
async def create_user(user: UserCreateModel, user_service: UserService = Depends()):
    new_user = user_service.create_user(user)
    return BaseResponse.success(data=new_user, message="User created successfully", status_code=status.HTTP_201_CREATED)


@router.get("/{user_id}", response_model=BaseResponse[UserResponseModel])
async def get_user(user_id: int, user_service: UserService = Depends()):
    user = user_service.get_user_by_id(user_id)
    return BaseResponse.success(data=user, message="User retrieved successfully")
