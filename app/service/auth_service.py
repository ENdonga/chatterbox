from fastapi import Depends
from passlib.exc import UnknownHashError
from sqlalchemy.orm import Session
from starlette.status import HTTP_200_OK

from app.database import models
from app.database.database import get_db
from app.exceptions.custom_exceptions import InvalidCredentialsException, UnknownHashException
from app.schemas.base_response import BaseResponse
from app.schemas.user_model import UserLoginModel
from app.utils import password_util


class AuthService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def authenticate(self, user_credentials: UserLoginModel):
        user = self.db.query(models.User).filter(models.User.email == user_credentials.email).first()
        if not user:
            raise InvalidCredentialsException()
        try:
            if not password_util.verify_password(user_credentials.password, user.password):
                raise InvalidCredentialsException(reason="Invalid credentials provided!!!!")
            return BaseResponse.success("Login Success", f"Login Success", status_code=HTTP_200_OK)
        except UnknownHashError:
            raise UnknownHashException()
        except Exception:
            raise InvalidCredentialsException()
