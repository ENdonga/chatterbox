from fastapi import Depends
from passlib.exc import UnknownHashError
from sqlalchemy.orm import Session

from app.database import models
from app.database.database import get_db
from app.exceptions.custom_exceptions import (
    InvalidCredentialsException,
    UnknownHashException,
    InternalServerError,
    ExpiredTokenException,
    InvalidTokenException,
    TokenSignatureException
)
from app.schemas.login_response import LoginResponseModel, TokenOwnerModel
from app.schemas.user_model import UserLoginModel
from app.utils import password_util
from app.utils.token_util import create_access_token, create_refresh_token, decode_access_token


class AuthService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def authenticate(self, user_credentials: UserLoginModel) -> LoginResponseModel:
        """Authenticates a user and returns an access and refresh token."""
        user = self.db.query(models.User).filter(models.User.email == user_credentials.email).first()
        if not user:
            raise InvalidCredentialsException()
        # check whether the provided password matches the hashed password in the db
        if not password_util.verify_password(user_credentials.password, str(user.password)):
            raise InvalidCredentialsException(reason="Invalid credentials provided!")
        try:
            # Generate access and refresh tokens
            user_data = {"id": user.id, "email": user.email}
            access_token = create_access_token(user_data)
            refresh_token = create_refresh_token(user_data)
            owner_data = TokenOwnerModel.model_validate({"id": user.id, "email": user.email}).model_dump()
            return LoginResponseModel.model_validate({
                "access_token": access_token,
                "refresh_token": refresh_token,
                "owner": owner_data
            })
        except UnknownHashError:
            raise UnknownHashException()
        except Exception:
            raise InternalServerError(reason="An error occurred while processing your login request")

    def refresh_access_token(self, refresh_token: str) -> LoginResponseModel:
        """Uses a refresh token to generate a new access token."""
        try:
            token_data = decode_access_token(refresh_token)
            # Ensure it's actually a refresh token
            if not token_data.get("refresh"):
                raise InvalidTokenException(reason="Invalid refresh token!")
            user_data = token_data.get("user")
            new_access_token = create_access_token(user_data)
            owner_data = TokenOwnerModel(id=user_data["id"], email=user_data["email"]).model_dump()
            return LoginResponseModel.model_validate({
                "access_token": new_access_token,
                "refresh_token": refresh_token,
                "owner": owner_data
            })
        except ExpiredTokenException:
            raise ExpiredTokenException(reason="Refresh token has expired. Please log in again.")
        except InvalidTokenException:
            raise InvalidTokenException(reason="Invalid refresh token. Please log in again.")
        except TokenSignatureException:
            raise TokenSignatureException(reason="Invalid refresh token signature.")
        except Exception:
            raise InternalServerError(reason="An error occurred while processing your login request")
