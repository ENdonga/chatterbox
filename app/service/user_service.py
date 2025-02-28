from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status

from app import utils, models
from app.database import get_db
from app.models import User
from app.schemas import UserResponse, BaseResponse, UserCreate


class UserService():
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_user_by_id(self, user_id: int) -> UserResponse:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=BaseResponse.error(
                    message="User not found",
                    reason=f"User with id: {user_id} not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )
            )
        return UserResponse.model_validate(user)

    def create_user(self, user: UserCreate) -> UserResponse:
        try:
            # Hash the password
            hashed_password = utils.hash_password(user.password)
            user.password = hashed_password
            new_user = models.User(**user.model_dump())
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            return UserResponse.model_validate(new_user)
        except IntegrityError as e:
            self.db.rollback()
            raise e
        except Exception as e:
            self.db.rollback()
            raise e
