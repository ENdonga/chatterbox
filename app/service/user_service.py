import logging
from typing import List

from fastapi.params import Depends
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.database import models
from app.database.database import get_db
from app.database.models import User
from app.exceptions.custom_exceptions import (
    UserAlreadyExistsException,
    EntityNotFoundException,
    DatabaseIntegrityException,
    DatabaseConnectionException,
    DatabaseTimeoutException,
    InternalServerError
)
from app.schemas.user_model import UserResponseModel, UserCreateModel, UpdateIsVerifiedModel
from app.utils import password_util


class UserService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_all_users(self) -> List[UserResponseModel]:
        users = self.db.query(models.User).all()
        return [UserResponseModel.model_validate(user) for user in users]

    def get_user_by_id(self, user_id: int) -> UserResponseModel:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise EntityNotFoundException(entity_name="User", identifier=user_id)
        return UserResponseModel.model_validate(user)

    def get_user_by_email(self, email: EmailStr) -> User | None:
        """Fetch a user by email. Returns None if not found"""
        return self.db.query(User).filter(User.email == email).first()

    def get_orm_user_by_id(self, user_id: int) -> User | None:
        """Fetch a user by email. Returns None if not found"""
        return self.db.query(User).filter(User.id == user_id).first()

    def user_exists(self, email: EmailStr) -> bool:
        """Check if a user with the given email exists."""
        user = self.get_user_by_email(email)
        return True if user is not None else False

    def create_user(self, user: UserCreateModel) -> UserResponseModel:
        # check if user already exists
        if self.user_exists(user.email):
            raise UserAlreadyExistsException(email=user.email)
        try:
            # Hash the password
            updated_data = user.model_dump()
            hashed_password = password_util.hash_password(updated_data['password'])
            updated_data['password'] = hashed_password
            # converts this Pydantic user object into a dictionary.
            new_user = models.User(**updated_data)
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            return UserResponseModel.model_validate(new_user)

        except IntegrityError:
            self.db.rollback()
            raise DatabaseIntegrityException(reason=f"User with email {user.email} already exists.")

        except OperationalError:
            self.db.rollback()
            raise DatabaseConnectionException(reason="Failed to connect to the database. Please try again later.")

        except TimeoutError:
            self.db.rollback()
            raise DatabaseTimeoutException(reason="Database operation timed out. Please try again later.")

        except Exception as e:
            self.db.rollback()
            raise InternalServerError(reason=str(e))

    def activate_user(self, user_id: int, update_data: UpdateIsVerifiedModel) -> UserResponseModel:
        user = self.get_orm_user_by_id(user_id)
        if not user:
            raise EntityNotFoundException(entity_name="User", identifier=user_id)
        try:
            # update user's is_verified flag
            user.is_verified = update_data.is_verified
            self.db.commit()
            self.db.refresh(user)
            return UserResponseModel.model_validate(user)
        except OperationalError:
            self.db.rollback()
            raise DatabaseConnectionException(reason="Failed to connect to the database. Please try again later.")
        except TimeoutError:
            self.db.rollback()
            raise DatabaseTimeoutException(reason="Database operation timed out. Please try again later.")
        except Exception as e:
            logging.exception(e)
            self.db.rollback()
            raise InternalServerError(reason=str(e))
