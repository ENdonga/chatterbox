import logging
from typing import List

from fastapi import Depends, APIRouter
from starlette import status

from app.schemas.base_response import BaseResponse
from app.schemas.user_model import UserResponseModel, UserCreateModel, UpdateIsVerifiedModel
from app.service.user_service import UserService
from app.utils.token_util import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=BaseResponse[UserResponseModel])
async def create_user(user: UserCreateModel, user_service: UserService = Depends()):
    """Creates and stores a new user to the database."""
    new_user = user_service.create_user(user)
    return BaseResponse.success(data=new_user, message="User created successfully", status_code=status.HTTP_201_CREATED)


@router.get("/{user_id}", response_model=BaseResponse[UserResponseModel])
async def get_user(user_id: int = None, user_service: UserService = Depends(),
                   current_user: dict = Depends(get_current_user)):
    """Returns a user who matches the given user id."""
    logging.info(f"Current user: {current_user}")
    user = user_service.get_user_by_id(user_id)
    return BaseResponse.success(data=user, message="User retrieved successfully")


@router.get("", response_model=List[BaseResponse[UserResponseModel]])
async def get_users(user_service: UserService = Depends()):
    """Returns a list of all users."""
    users = user_service.get_all_users()
    return BaseResponse.success(data=users, message="Users retrieved successfully")


@router.patch("/activate/{user_id}", response_model=BaseResponse[UserResponseModel])
async def activate_user(user_id: int, update_data: UpdateIsVerifiedModel, user_service: UserService = Depends()):
    """Activates a user."""
    user = user_service.get_user_by_id(user_id)
    updated_user = user_service.activate_user(user.id, update_data)
    action = "activated" if updated_user.is_verified else "deactivated"
    return BaseResponse.success(data=updated_user, message=f"User {action} successfully")
