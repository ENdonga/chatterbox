from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from starlette import status

from app import utils, models
from app.database import get_db
from app.schemas import BaseResponse, UserResponse, UserCreate

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=BaseResponse[UserResponse])
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Hash the password
        hashed_password = utils.hash_password(user.password)
        user.password = hashed_password
        new_user = models.User(**user.model_dump())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return BaseResponse.success(data=UserResponse.model_validate(new_user), message="User created successfully",
                                    status_code=status.HTTP_201_CREATED)
    except Exception as e:
        db.rollback()
        return BaseResponse.error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to create user",
            reason=str(e)
        )


@router.get("/{user_id}", response_model=BaseResponse[UserResponse])
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return BaseResponse.error("Request Failed", f"User with id: {user_id} not found")
    return BaseResponse.success(data=UserResponse.model_validate(user), message="User retrieved successfully")
