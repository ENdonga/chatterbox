from datetime import datetime

from fastapi import HTTPException
from fastapi.params import Depends
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status

from app.database import models
from app.database.database import get_db
from app.database.models import User
from app.schemas.base_response import BaseResponse
from app.schemas.user import UserResponse, UserCreate
from app.utils import utils


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

    def get_user_by_email(self, email: EmailStr) -> User | None:
        """Fetch a user by email. Returns None if not found"""
        return self.db.query(User).filter(User.email == email).first()

    def user_exists(self, email: EmailStr) -> bool:
        """Check if a user with the given email exists."""
        user = self.get_user_by_email(email)
        return True if user is not None else False

    def create_user(self, user: UserCreate) -> UserResponse:
        try:
            # check if user already exists
            if self.user_exists(user.email):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=BaseResponse.error(
                        message="User already exists",
                        status_code=status.HTTP_409_CONFLICT,
                        reason=f"User with email: {user.email} already exists"
                    )
                )

            updated_data = user.model_dump()
            updated_data['created_at'] = datetime.now()
            # Hash the password
            hashed_password = utils.hash_password(user.password)
            user.password = hashed_password
            # converts this Pydantic user object into a dictionary.
            new_user = models.User(**updated_data)
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
