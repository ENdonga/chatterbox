from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_200_OK

from app import utils, models
from app.database import get_db
from app.schemas import BaseResponse, UserLogin

router = APIRouter(tags=["Authentication"])


@router.post("/login")
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
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
