from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_200_OK

from app.database import models
from app.database.database import get_db
from app.schemas.base_response import BaseResponse
from app.schemas.user import UserLogin
from app.utils import utils


class AuthService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def authenticate(self, user_credentials: UserLogin):
        user = self.db.query(models.User).filter(models.User.email == user_credentials.email).first()
        if not user:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid credentials", )
        if not utils.verify_password(user_credentials.password, user.password):
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail=BaseResponse.error(
                    message="Login Failed",
                    reason="Invalid credentials",
                    status_code=HTTP_401_UNAUTHORIZED
                )
            )
        return BaseResponse.success("Login Success", f"Login Success", status_code=HTTP_200_OK)
