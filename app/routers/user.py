from fastapi import Depends, APIRouter
from starlette import status

from app.schemas import BaseResponse, UserResponse, UserCreate
from app.service.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=BaseResponse[UserResponse])
async def create_user(user: UserCreate, user_service: UserService = Depends()):
    new_user = user_service.create_user(user)
    return BaseResponse.success(data=new_user, message="User created successfully", status_code=status.HTTP_201_CREATED)


@router.get("/{user_id}", response_model=BaseResponse[UserResponse])
async def get_user(user_id: int, user_service: UserService = Depends()):
    user = user_service.get_user_by_id(user_id)
    return BaseResponse.success(data=user, message="User retrieved successfully")
